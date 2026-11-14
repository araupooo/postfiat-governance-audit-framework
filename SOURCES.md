# Sources — file:line citation map

Pinned postfiatd tree: commit `0085a1ff885d6a446369cf73a4430f75af22be55`.
Upstream comparison: rippled 2.5.0, commit
`1e01cd34f7a216092ed779f291b43324c167167a`.

All paths are relative to the repository root of the respective tree.
Line numbers were read from the pinned tree (and from the upstream tree
via `git show` where the sparse checkout lacks the file).

## (a) Amendment governance

| Rule | Pinned citation | Upstream note |
|------|-----------------|---------------|
| Post-fix majority threshold constant 67/100 | `include/xrpl/protocol/SystemParameters.h:85` | `SystemParameters.h:83` is 80/100 |
| Pre-fix majority threshold constant 204/256 | `include/xrpl/protocol/SystemParameters.h:83` | identical line/value |
| Default majority hold time, 2 weeks | `include/xrpl/protocol/SystemParameters.h:88` | `SystemParameters.h:86`, same value, `weeks{2}` spelling |
| `computeThreshold` / `passes` (strict `>` post-fix, `>=` pre-fix, single-validator exception) | `src/xrpld/app/misc/detail/AmendmentTable.cpp:326-377` | file byte-identical to upstream 2.5.0 (`diff` empty) |
| `doVoting` action logic (tfGotMajority / tfLostMajority / enable action 0 / hold) | `src/xrpld/app/misc/detail/AmendmentTable.cpp:847-935`, enable condition at 918 | byte-identical |
| `recordVotes`: 24h vote expiry, untrusted validations ignored | `src/xrpld/app/misc/detail/AmendmentTable.cpp:153-263`; `expiresAfter = 24h` at 172; untrusted ignored at 214-220; expiry cleared at 240-250 | byte-identical |
| `doValidation`: only supported, up-voted, not-yet-enabled amendments, sorted | `src/xrpld/app/misc/detail/AmendmentTable.cpp:817-840` | byte-identical |
| `fixAmendmentMajorityCalc` feature flag | `include/xrpl/protocol/detail/features.macro:104` | same feature exists upstream |
| Amendment ledger fields (`sfAmendments` on validations) | `src/xrpld/app/misc/detail/AmendmentTable.cpp:153-263` (votes read from `sfAmendments`) | byte-identical |

Divergence summary: the only amendment-governance divergence from
upstream 2.5.0 is the threshold constant (67/100 pinned vs 80/100
upstream). Consequence, verified by the harness: minimum majority 11/16
pinned vs 13/16 upstream; 8/10 pinned vs 9/10 upstream.

## (b) Validator-set changes

| Rule | Pinned citation | Upstream note |
|------|-----------------|---------------|
| Publisher list threshold (1 if < 3 publishers, else size/2 + 1) | `src/xrpld/app/misc/detail/ValidatorList.cpp:197-215` | same rule upstream |
| Validator quorum 67%: `max(ceil(effectiveUnlSize * 0.67), ceil(unlSize * 0.6))` | `src/xrpld/app/misc/detail/ValidatorList.cpp:1898-1900` (comment) and `:1934` (formula) | upstream uses 80%: `ValidatorList.cpp:1872` and return formula with `0.8f`; pinned comment states 67% is for devnet/testnet and mainnet should revert to 80% |
| Trusted-set inclusion (listings >= listThreshold_, manifest not revoked) | `src/xrpld/app/misc/detail/ValidatorList.cpp:2036-2066` | same structure upstream |
| Publisher list signature verification before apply; revoked publisher rejected at load | `src/xrpld/app/misc/detail/ValidatorList.cpp:1158-1183` (applyList), `:1413-1443` (verify), `:178-181` (revoked rejected) | pinned `applyList` takes a deserialized `Manifest` and uses an uncapped manifest rate-limit policy; upstream deserializes inside `verify` |
| List sequence disposition (stale / same_sequence / new) | `src/xrpld/app/misc/detail/ValidatorList.cpp:1427-1443` | same dispositions upstream |
| Trusted list population (config keys + signed publisher lists) and quorum reporting | `src/xrpld/app/misc/ValidatorList.h:131-170` (incl. the 125% trusted-list-size note at 168-170); `src/xrpld/app/misc/detail/ValidatorList.cpp:2109-2124` | header not diffed against upstream; no upstream claim made for the header text |
| Genesis quorum default 1 | `src/xrpld/app/misc/detail/ValidatorList.cpp:132` | identical upstream (region not in the 69-line diff) |

Divergence summary: `ValidatorList.cpp` differs from upstream 2.5.0 in
69 diff lines — manifest promotion to trusted on listing, the
deserialized-manifest `applyList` path, and the 67% quorum. The
list-threshold and trusted-inclusion rules are unchanged.

## (c) Ledger fee and sequence enforcement

| Rule | Pinned citation | Upstream note |
|------|-----------------|---------------|
| Default fee schedule: reference fee 10 drops, account reserve 10 XRP, owner reserve 2 XRP | `src/xrpld/core/Config.h:66-77` (`struct FeeSetup`) | not compared (upstream sparse checkout lacks this path in the copy used; no upstream claim made) |
| Fee settings per ledger; `accountReserve(ownerCount) = reserve + ownerCount * increment` | `include/xrpl/protocol/Fees.h:32-57` | not compared |
| Preflight malformed fee -> `temBAD_FEE` | `src/xrpld/app/tx/detail/Transactor.cpp:214-218` | not compared (see above) |
| `checkFee`: sufficiency checked only on open ledger; below due -> `telINSUF_FEE_P` | `src/xrpld/app/tx/detail/Transactor.cpp:379-413` | not compared |
| `minimumFee` / `scaleFeeLoad` wiring | `src/xrpld/app/tx/detail/Transactor.cpp:370-376` | not compared |
| `scaleFeeLoad`: `fee * feeFactor / loadBase`, integer division | `src/xrpld/app/misc/detail/LoadFeeTrack.cpp:84-110` | not compared |
| Normal load base 256; max fee 256 * 1,000,000 | `src/xrpld/app/misc/LoadFeeTrack.h:141-147` | not compared |
| `checkSeqProxy`: `terNO_ACCOUNT` / `terPRE_SEQ` / `tefPAST_SEQ` | `src/xrpld/app/tx/detail/Transactor.cpp:480-550` | not compared |
| Fee escalation constants: min multiplier `baseLevel * 500`, min 32 txns/ledger (1000 standalone), target 256, replacement +25% | `src/xrpld/app/misc/TxQ.h:98-113` | not compared |

## Comparison method

- `diff src/xrpld/app/misc/detail/AmendmentTable.cpp <upstream same path>`:
  empty (byte-identical).
- `diff src/xrpld/app/misc/detail/ValidatorList.cpp <upstream same path>`:
  69 changed lines (see table above).
- `diff include/xrpl/protocol/SystemParameters.h <upstream via git show>`:
  network name, `INITIAL_XRP` asserts, `XRP_LEDGER_EARLIEST_SEQ` 1 vs
  32570, threshold 67/100 vs 80/100, `weeks{2}` spelling.
- The upstream sparse checkout used for comparison contains
  `src/xrpld/app/misc`, `src/xrpld/app/tx` is absent, and the `xrpl`
  include tree is absent; upstream files outside `src/xrpld/app/misc`
  were read via `git show HEAD:<path>` where possible
  (`SystemParameters.h`), and are otherwise marked "not compared" above
  rather than asserted.
