# PFTL Governance Audit Framework

A read-only audit harness and rendered results page for PFTL governance
rules, covering three areas in the pinned postfiatd tree:

- **Amendment governance** — majority thresholds, voting/enablement flow,
  vote expiry, vetoes.
- **Validator-set changes** — publisher list integrity, trusted-set
  inclusion, quorum rules.
- **Ledger fee and sequence enforcement** — reference fee, fee-load
  scaling, fee escalation, account sequence rules.

Vote replay and reordered validations are out of scope for this pack.

## Pinned sources

- postfiatd commit `0085a1ff885d6a446369cf73a4430f75af22be55`
- Upstream comparison: rippled 2.5.0, commit
  `1e01cd34f7a216092ed779f291b43324c167167a`

Exact file:line citations for every rule are in `SOURCES.md`. The
claim-to-evidence index (`claim-evidence-index.md`) separates MEASURED
claims (backed by a runnable check and raw output) from SOURCE-DERIVED
claims (backed by an exact citation).

## Running the harness

```sh
bash run_all.sh
```

Exit status is 0 only when every check passes, the digest check is clean,
and the derived files are stable across a rebuild. No network calls. The
harness never reads or writes the pinned postfiatd tree; it checks local
synthetic fixtures against rules transcribed from the cited source lines.

## Layout

- `run_all.sh` — runs all checks, assembles `results/run_log.txt`,
  regenerates digests and derived files.
- `scripts/` — the four check scripts and `build_derived.py`.
- `fixtures/` — synthetic JSON fixtures (all invented data, labelled in
  `fixtures/README.md`).
- `results/` — unedited run log, environment details, digest manifest and
  digest-check output, fresh-copy reproduction log.
- `docs/index.html` — rendered results page (served from `/docs`).
- `claims.json` — claim list; single source of truth for the rendered page
  and the claim-to-evidence index.
- `claim-evidence-index.md` — claim-to-evidence index.
- `SOURCES.md` — file:line citation map and upstream comparison notes.

## Reproduction

From a fresh copy of this pack, run `bash run_all.sh` and confirm exit
status 0. The exact commands, exit status, and any limitations of the
fresh-copy run are recorded in `results/reproduction_log.txt`.

## Limitations

- Fixtures are synthetic JSON built from the real schema shapes. The
  harness checks the rules as transcribed from the cited source lines; it
  does not compile or execute postfiatd (a full build is not feasible on
  this machine: the build needs Conan-managed dependencies and far more
  memory than is available here).
- Publisher-list signatures in the fixtures are synthetic sha256
  stand-ins that exercise the verify-then-apply rule, not real ed25519
  signatures.
- Upstream comparison covers `AmendmentTable.cpp`, `ValidatorList.cpp`,
  and `SystemParameters.h`. The upstream sparse checkout used here does
  not contain `src/xrpld/app/tx` or the `xrpl` include tree, so no upstream
  diff is claimed for the fee/sequence code.
