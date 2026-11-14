#!/usr/bin/env python3
"""Validator-set change checks.

Rules transcribed from the pinned postfiatd tree:
  - src/xrpld/app/misc/detail/ValidatorList.cpp:210-212
      listThreshold_ = 1 when fewer than 3 publishers,
      else publisherLists_.size() / 2 + 1.
  - ValidatorList.cpp:1898-1900 and 1934 (calculateQuorum)
      pinned:   quorum = max(ceil(effectiveUnlSize * 0.67),
                             ceil(unlSize * 0.6))
      upstream rippled 2.5.0: max(ceil(effectiveUnlSize * 0.8),
                                  ceil(unlSize * 0.6))
  - ValidatorList.cpp:2042-2066 (updateTrusted)
      a validator is trusted iff listed on >= listThreshold_ publisher
      lists AND its manifest is not revoked.
  - ValidatorList.cpp:1158-1183 (applyList) and 1413-1443 (verify)
      a publisher list is applied only after its signature verifies
      against the publisher key; a list whose sequence is below the
      current sequence is stale, equal is already known, above is new.
  - ValidatorList.cpp:178-181 (load): a revoked publisher manifest is
    rejected at load time.

Signatures in the fixtures are SYNTHETIC stand-ins:
sha256(publisher_key + "|" + blob). They exercise the verify-then-apply
rule; they are not real ed25519 signatures and no real key material is
involved.

Read-only: reads fixtures/validator_lists.json, prints PASS/FAIL per case.
Exit 0 iff every case passes. No network, no writes outside stdout.
"""
import hashlib
import json
import math
import os
import sys

PACK = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(PACK, "fixtures", "validator_lists.json")

with open(FIX) as f:
    data = json.load(f)

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


def list_threshold(publishers):
    return 1 if publishers < 3 else publishers // 2 + 1


def quorum(unl, effective, factor):
    return max(math.ceil(effective * factor), math.ceil(unl * 0.6))


def signature_valid(pubkey, blob, signature):
    return hashlib.sha256((pubkey + "|" + blob).encode()).hexdigest() == signature


for c in data["list_threshold_cases"]:
    check(c["id"], c["rule"], list_threshold(c["publishers"]), c["expected"])

for c in data["quorum_cases"]:
    check(c["id"], c["rule"] + " [pinned 67%]",
          quorum(c["unl_size"], c["effective_unl_size"], 0.67),
          c["expected_pinned"])
    check(c["id"], c["rule"] + " [upstream 80%]",
          quorum(c["unl_size"], c["effective_unl_size"], 0.8),
          c["expected_upstream"])

for c in data["trusted_inclusion_cases"]:
    actual = (c["listings"] >= c["list_threshold"]) and not c["revoked"]
    check(c["id"], c["rule"], actual, c["expected"])

for c in data["signature_cases"]:
    actual = "accepted" if signature_valid(
        c["publisher_key"], c["blob"], c["signature"]) else "rejected"
    check(c["id"], c["rule"], actual, c["expected"])

for c in data["sequence_cases"]:
    if c["incoming_sequence"] < c["current_sequence"]:
        actual = "stale"
    elif c["incoming_sequence"] == c["current_sequence"]:
        actual = "same_sequence"
    else:
        actual = "new"
    check(c["id"], c["rule"], actual, c["expected"])

print("VALIDATOR-LIST: %d passed, %d failed" % (passed, failed))
sys.exit(1 if failed else 0)
