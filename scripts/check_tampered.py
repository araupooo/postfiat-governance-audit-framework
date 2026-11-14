#!/usr/bin/env python3
"""Tampered-input negative tests.

Each fixture is an input a correct harness must DETECT and reject. A check
PASSES when the tamper is detected; the tampered input itself is expected
to fail validation. Detection rules are the same rules the other checks
implement, transcribed from the pinned postfiatd tree:
  - pinned post-fix threshold 67/100:
    include/xrpl/protocol/SystemParameters.h:85
  - publisher signature verification before applying a list:
    src/xrpld/app/misc/detail/ValidatorList.cpp:1158-1183, 1413-1443
  - fee sufficiency: src/xrpld/app/tx/detail/Transactor.cpp:379-413
  - sequence enforcement: Transactor.cpp:480-550
  - list sequence disposition: ValidatorList.cpp:1427-1443
  - vote counts cannot exceed the trusted validator set:
    src/xrpld/app/misc/detail/AmendmentTable.cpp:326-377
    (threshold math is over trustedValidations_)
  - digest integrity: SHA-256 over the recorded fixture bytes.

The digest-tamper case (TAMP-08) copies fixtures/amendments.json to a
temporary directory, flips one byte, and runs `sha256sum --check` against
a manifest generated from the original bytes; the check passes only if
the tampered copy is reported as FAILED. All temp files live under the
system temp directory, never inside the pack.

Read-only with respect to the pack and the pinned tree. Prints PASS/FAIL
per case. Exit 0 iff every tamper is detected.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile

PACK = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(PACK, "fixtures", "tampered.json")

with open(FIX) as f:
    data = json.load(f)

passed = failed = 0


def check(case_id, rule, detected, expected):
    global passed, failed
    ok = detected == expected
    print("%s [%s] %s (detected=%r, expected=%r)" % (
        "PASS" if ok else "FAIL", case_id, rule, detected, expected))
    if ok:
        passed += 1
    else:
        failed += 1


# TAMP-01: threshold constant tamper
c = data["threshold_tamper"]
claimed = (c["claimed_postfix_num"], c["claimed_postfix_den"])
pinned = (c["pinned_postfix_num"], c["pinned_postfix_den"])
check(c["id"], c["rule"],
      "detected" if claimed != pinned else "not_detected", c["expected"])

# TAMP-02: forged validator-list signature
c = data["forged_signature"]
digest = hashlib.sha256(
    (c["publisher_key"] + "|" + c["blob"]).encode()).hexdigest()
check(c["id"], c["rule"],
      "rejected" if digest != c["signature"] else "accepted", c["expected"])

# TAMP-03: fee below minimum
c = data["fee_below_minimum"]
result = ("telINSUF_FEE_P" if c["ledger_open"]
          and c["fee_paid_drops"] < c["fee_due_drops"] else "ok")
check(c["id"], c["rule"], result, c["expected"])

# TAMP-04: sequence gap
c = data["sequence_gap"]
if not c["account_exists"]:
    result = "terNO_ACCOUNT"
elif c["tx_seq"] > c["account_seq"]:
    result = "terPRE_SEQ"
elif c["tx_seq"] < c["account_seq"]:
    result = "tefPAST_SEQ"
else:
    result = "ok"
check(c["id"], c["rule"], result, c["expected"])

# TAMP-05: sequence replay
c = data["sequence_replay"]
if not c["account_exists"]:
    result = "terNO_ACCOUNT"
elif c["tx_seq"] > c["account_seq"]:
    result = "terPRE_SEQ"
elif c["tx_seq"] < c["account_seq"]:
    result = "tefPAST_SEQ"
else:
    result = "ok"
check(c["id"], c["rule"], result, c["expected"])

# TAMP-06: validator-list sequence regression
c = data["list_sequence_regression"]
if c["incoming_sequence"] < c["current_sequence"]:
    result = "stale"
elif c["incoming_sequence"] == c["current_sequence"]:
    result = "same_sequence"
else:
    result = "new"
check(c["id"], c["rule"], result, c["expected"])

# TAMP-07: vote count exceeding the trusted validator set
c = data["vote_overflow"]
result = "invalid" if c["votes"] > c["trusted_validators"] else "valid"
check(c["id"], c["rule"], result, c["expected"])

# TAMP-08: digest tamper -- flip one byte in a copy and verify --check fails
c = data["digest_tamper"]
src = os.path.join(PACK, "fixtures", "amendments.json")
with open(src, "rb") as f:
    original = f.read()
tampered_bytes = bytearray(original)
# Flip one byte in the middle of the file (a '0' digit in a fixture value).
tampered_bytes[len(tampered_bytes) // 2] ^= 0x01
manifest_digest = hashlib.sha256(original).hexdigest()
tampered_digest = hashlib.sha256(bytes(tampered_bytes)).hexdigest()
detected = "detected" if tampered_digest != manifest_digest else "not_detected"
# Also confirm through the real tool, not just hashlib: write the tampered
# copy to a temp dir with a manifest of the ORIGINAL digest and run
# sha256sum --check; it must report FAILED.
with tempfile.TemporaryDirectory() as tmp:
    copy_path = os.path.join(tmp, "amendments.json")
    manifest_path = os.path.join(tmp, "SHA256SUMS")
    with open(copy_path, "wb") as f:
        f.write(bytes(tampered_bytes))
    with open(manifest_path, "w") as f:
        f.write("%s  amendments.json\n" % manifest_digest)
    proc = subprocess.run(
        ["sha256sum", "--check", "SHA256SUMS"],
        cwd=tmp, capture_output=True, text=True)
    tool_detected = "FAILED" in proc.stdout or proc.returncode != 0
    if not tool_detected:
        detected = "not_detected"
check(c["id"], c["rule"], detected, c["expected"])

print("TAMPERED-INPUT: %d passed, %d failed" % (passed, failed))
sys.exit(1 if failed else 0)
