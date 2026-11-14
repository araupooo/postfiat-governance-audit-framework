#!/usr/bin/env bash
# PFTL governance audit harness runner.
#
# Read-only: runs local Python checks against synthetic fixtures. No network
# calls, no mutation of the pinned postfiatd tree (the harness never reads
# it at run time; the rules it checks were transcribed from cited source
# lines at build time). All intermediate output is captured in a temp
# directory outside the pack and only copied into results/ once complete.
#
# Exit status: 0 iff every check passed, the digest check is clean, and
# the derived files (docs/index.html, claim-evidence-index.md) are stable
# across a rebuild (fixed point). Non-zero otherwise.
#
# Invoke scripts with `bash` / `python3` explicitly; never rely on the
# executable bit (a fresh clone may carry mode 644).
set -u

PACK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RESULTS_DIR="$PACK_DIR/results"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

PINNED_COMMIT="$(cat "$PACK_DIR/PINNED_COMMIT")"
UPSTREAM_COMMIT="1e01cd34f7a216092ed779f291b43324c167167a"

CHECKS="check_amendment_threshold check_validator_list check_fee_sequence check_tampered"

total_pass=0
total_fail=0
check_status=0

for name in $CHECKS; do
    out="$TMP_DIR/$name.out"
    if python3 "$PACK_DIR/scripts/$name.py" "$PACK_DIR" > "$out" 2>&1; then
        echo "$name: ok"
    else
        echo "$name: FAILED (see results/run_log.txt)"
        check_status=1
    fi
done

# Assemble the unedited run log from the captured outputs (deterministic:
# no timestamps anywhere in the log).
{
    echo "PFTL governance audit harness — run log"
    echo "pinned_postfiatd_commit: $PINNED_COMMIT"
    echo "upstream_rippled_2.5.0_commit: $UPSTREAM_COMMIT"
    echo "---"
    for name in $CHECKS; do
        echo "=== $name ==="
        cat "$TMP_DIR/$name.out"
        echo ""
    done
} > "$TMP_DIR/run_log.txt"

# Count PASS/FAIL lines per group and overall.
for name in $CHECKS; do
    p="$(grep -c '^PASS' "$TMP_DIR/$name.out" || true)"
    f="$(grep -c '^FAIL' "$TMP_DIR/$name.out" || true)"
    total_pass=$((total_pass + p))
    total_fail=$((total_fail + f))
done
echo "OVERALL RESULT: $total_pass passed, $total_fail failed" >> "$TMP_DIR/run_log.txt"
cp "$TMP_DIR/run_log.txt" "$RESULTS_DIR/run_log.txt"

# Environment details (versions only; deterministic on one machine).
{
    echo "os: $(uname -srm)"
    echo "python3: $(python3 --version 2>&1)"
    echo "bash: $(bash --version | head -1)"
    echo "sha256sum: $(sha256sum --version | head -1)"
    echo "pinned_postfiatd_commit: $PINNED_COMMIT"
    echo "upstream_rippled_2.5.0_commit: $UPSTREAM_COMMIT"
} > "$RESULTS_DIR/env.txt"

# Digest manifest: every pack file except the manifest itself, the digest
# check output, and the reproduction log (the last two are outputs of
# checking the manifest / of the fresh-copy run, not inputs to it).
write_manifest() {
    ( cd "$PACK_DIR" && find . -type f \
        ! -path './.git/*' \
        ! -path './results/SHA256SUMS' \
        ! -path './results/digest_check_output.txt' \
        ! -path './results/reproduction_log.txt' \
        | LC_ALL=C sort | xargs sha256sum > "$RESULTS_DIR/SHA256SUMS" )
}
check_digests() {
    ( cd "$PACK_DIR" && sha256sum --check results/SHA256SUMS \
        > "$RESULTS_DIR/digest_check_output.txt" 2>&1 )
}

write_manifest
check_digests

# Derived files embed the run log tail and the digest output, and the
# manifest covers the derived files, so converge by iterating the
# (manifest -> digest check -> rebuild derived files) cycle until the
# derived files stop changing. On a first run the derived files do not
# exist yet, so the first pass adds them to the manifest and the digest
# output grows; the cycle settles at the fixed point within a few passes.
fixed_point=0
prev_index_hash="none"
prev_index_md_hash="none"
for _ in 1 2 3 4; do
    write_manifest
    check_digests
    python3 "$PACK_DIR/scripts/build_derived.py" "$PACK_DIR"
    index_hash="$(sha256sum "$PACK_DIR/docs/index.html" | cut -d' ' -f1)"
    index_md_hash="$(sha256sum "$PACK_DIR/claim-evidence-index.md" | cut -d' ' -f1)"
    if [ "$index_hash" = "$prev_index_hash" ] \
       && [ "$index_md_hash" = "$prev_index_md_hash" ]; then
        fixed_point=1
        break
    fi
    prev_index_hash="$index_hash"
    prev_index_md_hash="$index_md_hash"
done
if [ "$fixed_point" != 1 ]; then
    echo "ERROR: derived files not stable across rebuild (fixed point not reached)"
    fixed_point=0
fi

# Final manifest + digest check over the settled file set.
write_manifest
check_digests
if ! grep -q ': FAILED' "$RESULTS_DIR/digest_check_output.txt" \
   && grep -c ': OK' "$RESULTS_DIR/digest_check_output.txt" >/dev/null; then
    digest_status=0
else
    digest_status=1
fi
digest_ok_count="$(grep -c ': OK' "$RESULTS_DIR/digest_check_output.txt" || true)"

echo "checks: $total_pass passed, $total_fail failed"
echo "digests: $digest_ok_count files OK"
echo "fixed point: $([ "$fixed_point" = 1 ] && echo stable || echo UNSTABLE)"

if [ "$total_fail" != 0 ] || [ "$check_status" != 0 ] \
   || [ "$digest_status" != 0 ] || [ "$fixed_point" != 1 ]; then
    exit 1
fi
exit 0
