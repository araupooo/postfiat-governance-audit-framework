#!/usr/bin/env python3
"""Amendment governance checks.

Rules transcribed from the pinned postfiatd tree:
  - include/xrpl/protocol/SystemParameters.h:81-88
      preFixAmendmentMajorityCalcThreshold  = 204/256
      postFixAmendmentMajorityCalcThreshold = 67/100 (pinned)
      defaultAmendmentMajorityTime          = 2 weeks
  - src/xrpld/app/misc/detail/AmendmentTable.cpp:326-377
      computeThreshold: threshold = max(1, floor(N * num / den))
      passes: pre-fix (or N == 1): votes >= threshold
              post-fix:            votes >  threshold
  - AmendmentTable.cpp:847-935 (doVoting): majority recorded, then enable
    only when (majorityTime + majorityTime_) <= closeTime and local vote up
    (action 0); otherwise hold. Vetoed (vote down) never enables.
  - AmendmentTable.cpp:153-263 (recordVotes): vote record expires 24h after
    the validator's last validation (expiresAfter = 24h, line 172);
    validations from untrusted validators are ignored (lines 214-220).
  - AmendmentTable.cpp:817-840 (doValidation): only supported, up-voted,
    not-yet-enabled amendments are voted; unknown amendments are never voted.

Read-only: reads fixtures/amendments.json, prints PASS/FAIL per case.
Exit 0 iff every case passes. No network, no writes outside stdout.
"""
import json
import os
import sys

PACK = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(PACK, "fixtures", "amendments.json")

with open(FIX) as f:
    data = json.load(f)

meta = data["meta"]
PIN_NUM, PIN_DEN = meta["pinned_postfix_num"], meta["pinned_postfix_den"]
PRE_NUM, PRE_DEN = meta["prefix_num"], meta["prefix_den"]
UP_NUM, UP_DEN = meta["upstream_postfix_num"], meta["upstream_postfix_den"]
HOLD = meta["majority_time_seconds"]
EXPIRY = meta["vote_expiry_seconds"]

passed = failed = 0


def check(case_id, rule, actual, expected):
    global passed, failed
    ok = actual == expected
    print("%s [%s] %s (got %r, expected %r)" % (
        "PASS" if ok else "FAIL", case_id, rule, actual, expected))
    if ok:
        passed += 1
    else:
        failed += 1


def threshold(n, num, den):
    return max(1, (n * num) // den)


def passes_pinned(votes, n, fix_on):
    if not fix_on:
        return votes >= threshold(n, PRE_NUM, PRE_DEN)
    if n == 1:
        return votes >= threshold(n, PIN_NUM, PIN_DEN)
    return votes > threshold(n, PIN_NUM, PIN_DEN)


def passes_upstream(votes, n):
    if n == 1:
        return votes >= threshold(n, UP_NUM, UP_DEN)
    return votes > threshold(n, UP_NUM, UP_DEN)


for c in data["threshold_cases"]:
    check(c["id"], c["rule"],
          passes_pinned(c["votes"], c["n"], c["fix_on"]), c["expected"])

for c in data["upstream_comparison_cases"]:
    check(c["id"], c["rule"],
          passes_upstream(c["votes"], c["n"]), c["expected"])

for c in data["hold_cases"]:
    actual = "enable" if (c["majority_time"] + HOLD) <= c["close_time"] else "hold"
    check(c["id"], c["rule"], actual, c["expected"])

for c in data["expiry_cases"]:
    actual = "expired" if c["close_time"] > c["last_seen"] + EXPIRY else "live"
    check(c["id"], c["rule"], actual, c["expected"])

for c in data["veto_cases"]:
    # A vetoed amendment can never gain majority or enable, regardless of
    # validator support or elapsed hold time (doVoting requires vote == up).
    actual = "never_enable" if c["vote"] == "down" else "enable"
    check(c["id"], c["rule"], actual, c["expected"])

for c in data["unknown_cases"]:
    actual = "not_voted" if not c["known"] else "voted"
    check(c["id"], c["rule"], actual, c["expected"])

print("AMENDMENT-THRESHOLD: %d passed, %d failed" % (passed, failed))
sys.exit(1 if failed else 0)
