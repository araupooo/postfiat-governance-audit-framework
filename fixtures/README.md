# Fixtures

All files in this directory are **synthetic**: invented amendment names,
validator and publisher keys, accounts, sequences, and fees, built from the
real schema shapes so the harness can exercise the rules as transcribed
from the pinned postfiatd source. No fixture contains real network data,
real keys, or real signatures.

- `amendments.json` — threshold, hold-time, vote-expiry, veto, and
  unknown-amendment cases.
- `validator_lists.json` — publisher list thresholds, quorum math,
  trusted-set inclusion, publisher signatures, and list sequences.
- `ledger_fees.json` — account reserves, fee sufficiency, fee-load
  scaling, account sequences, and fee-escalation constants.
- `tampered.json` — tampered inputs the harness must detect and reject.

Publisher-list "signatures" are synthetic `sha256(publisher_key + "|" +
blob)` stand-ins. They exercise the verify-then-apply rule; they are not
real ed25519 signatures and no real key material is involved.
