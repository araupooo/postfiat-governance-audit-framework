#!/usr/bin/env python3
"""Ledger fee and sequence enforcement checks.

Rules transcribed from the pinned postfiatd tree:
  - src/xrpld/core/Config.h:66-77 (FeeSetup, default-constructed)
      reference_fee    = 10 drops
      account_reserve  = 10 XRP  (10,000,000 drops)
      owner_reserve    = 2 XRP   (2,000,000 drops)
  - include/xrpl/protocol/Fees.h:32-57 (struct Fees)
      accountReserve(ownerCount) = reserve + ownerCount * increment
  - src/xrpld/app/tx/detail/Transactor.cpp:214-218 (preflight1)
      malformed fee (non-native, negative, illegal amount) -> temBAD_FEE
  - Transactor.cpp:379-413 (checkFee)
      fee sufficiency is checked only when the ledger is open;
      feePaid < feeDue -> telINSUF_FEE_P; feePaid == 0 on an open ledger
      with a fee due also fails; otherwise tesSUCCESS.
  - src/xrpld/app/misc/detail/LoadFeeTrack.cpp:84-110 (scaleFeeLoad)
      feeDue = fee * feeFactor / loadBase, integer division;
      loadBase = lftNormalFee = 256 (LoadFeeTrack.h:141)
  - Transactor.cpp:480-550 (checkSeqProxy)
      account missing -> terNO_ACCOUNT
      tx seq > account seq -> terPRE_SEQ (gap, retryable)
      tx seq < account seq -> tefPAST_SEQ (replay, fee claimed)
      tx seq == account seq -> ok
  - src/xrpld/app/misc/TxQ.h:98-113
      minimumEscalationMultiplier = baseLevel * 500
      minimumTxnInLedger = 32, minimumTxnInLedgerSA = 1000,
      targetTxnInLedger = 256, retrySequencePercent = 25
      (replacement for the same sequence must pay >= 1.25x)

Read-only: reads fixtures/ledger_fees.json, prints PASS/FAIL per case.
Exit 0 iff every case passes. No network, no writes outside stdout.
"""
import json
import os
import sys

PACK = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(PACK, "fixtures", "ledger_fees.json")

with open(FIX) as f:
    data = json.load(f)

meta = data["meta"]
LOAD_BASE = meta["load_base"]

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


def account_reserve(owner_count):
    return meta["account_reserve_drops"] + owner_count * meta["owner_reserve_drops"]


def check_fee(fee_paid, fee_due, ledger_open, non_native=False):
    if non_native or fee_paid < 0:
        return "temBAD_FEE"
    if ledger_open and fee_paid < fee_due:
        return "telINSUF_FEE_P"
    return "ok"


def scale_fee_load(fee, factor):
    if fee == 0:
        return 0
    return (fee * factor) // LOAD_BASE


def check_seq(account_seq, tx_seq, account_exists):
    if not account_exists:
        return "terNO_ACCOUNT"
    if tx_seq > account_seq:
        return "terPRE_SEQ"
    if tx_seq < account_seq:
        return "tefPAST_SEQ"
    return "ok"


for c in data["reserve_cases"]:
    check(c["id"], c["rule"], account_reserve(c["owner_count"]),
          c["expected_drops"])

for c in data["check_fee_cases"]:
    check(c["id"], c["rule"],
          check_fee(c["fee_paid_drops"], c["fee_due_drops"],
                    c["ledger_open"], c.get("non_native", False)),
          c["expected"])

for c in data["scale_fee_load_cases"]:
    check(c["id"], c["rule"],
          scale_fee_load(c["fee_drops"], c["fee_factor"]),
          c["expected_drops"])

for c in data["sequence_cases"]:
    check(c["id"], c["rule"],
          check_seq(c["account_seq"], c["tx_seq"], c["account_exists"]),
          c["expected"])

for c in data["escalation_constants"]:
    if "base_level" in c:
        check(c["id"], c["rule"], c["base_level"] * 500,
              c["expected_multiplier"])
    elif "queued_fee_level" in c:
        # replacement must pay at least 1.25x: 512 * 125 // 100 = 640
        check(c["id"], c["rule"],
              c["queued_fee_level"] * 125 // 100, c["expected_replacement"])
    else:
        expected = {"minimumTxnInLedger": 32,
                    "targetTxnInLedger": 256,
                    "minimumTxnInLedgerSA": 1000,
                    "retrySequencePercent": 25}[c["constant"]]
        check(c["id"], c["rule"], expected, c["expected"])

print("FEE-SEQUENCE: %d passed, %d failed" % (passed, failed))
sys.exit(1 if failed else 0)
