# Claim-to-evidence index

Pinned postfiatd commit: `0085a1ff885d6a446369cf73a4430f75af22be55`

Upstream comparison: rippled 2.5.0, commit `1e01cd34f7a216092ed779f291b43324c167167a`.

MEASURED claims are backed by a runnable check and raw output in `results/run_log.txt`. SOURCE-DERIVED claims are backed by an exact file:line citation in the pinned tree (or the upstream tree where stated).

## Measured claims

| ID | Claim | Evidence |
|----|-------|----------|
| M-01 | Under the pinned post-fix 67% rule, the minimum yes-vote count for an amendment majority with 16 trusted validators is 11 (threshold 10, strict >). | check_amendment_threshold.py, cases AMEND-T-01..T-05 (16 validators, 10 votes no majority, 11 votes majority). Raw output: results/run_log.txt. |
| M-02 | Under the pinned post-fix 67% rule, the minimum majority is 7 of 10 and 8 of 11 trusted validators. | check_amendment_threshold.py, cases AMEND-T-06..T-10. Raw output: results/run_log.txt. |
| M-03 | Under the pre-fix 204/256 rule, the minimum majority is 12 of 16 and 7 of 10 (votes >= threshold). | check_amendment_threshold.py, cases AMEND-T-14..T-17. Raw output: results/run_log.txt. |
| M-04 | Under upstream rippled 2.5.0 80/100, 11 of 16 and 12 of 16 are NOT majorities; the minimum is 13 of 16. The pinned 67% rule therefore enables an amendment at 11/16 where upstream requires 13/16. | check_amendment_threshold.py, cases AMEND-U-01..U-05. Raw output: results/run_log.txt. |
| M-05 | An amendment enables only once majority_time + 2 weeks <= close_time; one second earlier it only holds. | check_amendment_threshold.py, cases AMEND-H-01..H-05. Raw output: results/run_log.txt. |
| M-06 | A validator's recorded amendment vote expires 24 hours after its last validation; at exactly 24h it is still live, one second later it is cleared. | check_amendment_threshold.py, cases AMEND-E-01..E-05. Raw output: results/run_log.txt. |
| M-07 | A vetoed amendment never enables, even with unanimous validator support and the hold time elapsed. | check_amendment_threshold.py, cases AMEND-V-01..V-02. Raw output: results/run_log.txt. |
| M-08 | An unknown amendment (not in the known set) is never voted. | check_amendment_threshold.py, case AMEND-K-01. Raw output: results/run_log.txt. |
| M-09 | Publisher list threshold is 1 for fewer than 3 publishers, otherwise publishers/2 + 1 (3->2, 4->3, 5->3, 10->6). | check_validator_list.py, cases VAL-L-01..L-08. Raw output: results/run_log.txt. |
| M-10 | Validator quorum under the pinned 67% rule is 11 of 16, 7 of 10, 24 of 35, 67 of 100; upstream 80% gives 13, 8, 28, 80. The 60% floor dominates when the effective UNL is much smaller than the UNL (20/15 -> 12 both). | check_validator_list.py, cases VAL-Q-01..Q-05 (pinned and upstream evaluated side by side). Raw output: results/run_log.txt. |
| M-11 | A validator is trusted only when listed on at least listThreshold_ publisher lists and its manifest is not revoked. | check_validator_list.py, cases VAL-T-01..T-05. Raw output: results/run_log.txt. |
| M-12 | A publisher list whose signature does not match its blob is rejected; a matching signature is accepted. | check_validator_list.py, cases VAL-S-01..S-03 (synthetic sha256 stand-in signature). Raw output: results/run_log.txt. |
| M-13 | A publisher list with a regressed sequence is stale, an equal sequence is already known, and a higher sequence is new and applied. | check_validator_list.py, cases VAL-QQ-01..QQ-03. Raw output: results/run_log.txt. |
| M-14 | The default account reserve is 10 XRP with 0 owned items, 16 XRP with 3, 20 XRP with 5 (10 XRP base + 2 XRP per owned item). | check_fee_sequence.py, cases FEE-R-01..R-03. Raw output: results/run_log.txt. |
| M-15 | On an open ledger, a fee below the fee due is rejected with telINSUF_FEE_P; a fee equal to or above the due fee is accepted; fee sufficiency is not checked on a closed ledger. | check_fee_sequence.py, cases FEE-C-01..C-06. Raw output: results/run_log.txt. |
| M-16 | A malformed fee (negative, or non-native currency) is rejected with temBAD_FEE. | check_fee_sequence.py, cases FEE-C-07..C-08. Raw output: results/run_log.txt. |
| M-17 | Fee-load scaling is fee * factor / 256 with integer division: 10 drops at factor 256 stays 10, at 512 becomes 20, at 320 becomes 12. | check_fee_sequence.py, cases FEE-S-01..S-06. Raw output: results/run_log.txt. |
| M-18 | A transaction sequence equal to the account sequence is accepted; a future sequence returns terPRE_SEQ; a past sequence returns tefPAST_SEQ; a missing source account returns terNO_ACCOUNT. | check_fee_sequence.py, cases SEQ-01..SEQ-06. Raw output: results/run_log.txt. |
| M-19 | Fee escalation constants: minimum escalation multiplier is baseLevel * 500 (256 -> 128000); minimum 32 transactions per ledger before escalation (1000 standalone); target 256; a replacement transaction for the same sequence must pay at least 1.25x (512 -> 640). | check_fee_sequence.py, cases FEE-E-01..E-06. Raw output: results/run_log.txt. |
| M-20 | Tampered inputs are detected: a fixture claiming the pinned threshold is 80/100 is flagged; a forged validator-list signature is rejected; a 5-drop fee against a 10-drop due fee is rejected; a sequence gap is held and a replay fails; a regressed list sequence is stale; a vote count above the trusted validator set is invalid. | check_tampered.py, cases TAMP-01..TAMP-07. Raw output: results/run_log.txt. |
| M-21 | A fixture file with one byte changed fails sha256sum --check against the recorded digest (tamper detected by the digest check itself). | check_tampered.py, case TAMP-08 (real sha256sum --check run on a tampered copy in a temp directory). Raw output: results/run_log.txt. |
| M-22 | The full harness reproduces from a fresh copy with exit status 0 and all digest checks passing. | results/reproduction_log.txt (fresh-copy run of bash run_all.sh). |

## Source-derived claims

| ID | Claim | Evidence |
|----|-------|----------|
| S-01 | The pinned post-fix amendment majority threshold constant is 67/100. | include/xrpl/protocol/SystemParameters.h:85 (constexpr std::ratio<67, 100> postFixAmendmentMajorityCalcThreshold). |
| S-02 | Upstream rippled 2.5.0 uses 80/100 for the same constant. | Upstream commit 1e01cd34f7a216092ed779f291b43324c167167a, include/xrpl/protocol/SystemParameters.h:83 (constexpr std::ratio<80, 100> postFixAmendmentMajorityCalcThreshold), read via git show. |
| S-03 | The pinned AmendmentTable implementation is byte-identical to upstream rippled 2.5.0; the threshold divergence lives only in the SystemParameters.h constant. | diff of src/xrpld/app/misc/detail/AmendmentTable.cpp against upstream 2.5.0: empty (identical). |
| S-04 | doVoting records tfGotMajority when validators have a majority and the ledger does not, tfLostMajority when the ledger has one and validators do not, and enables (action 0) only when the ledger majority has held for majorityTime_ and the local vote is up; otherwise it holds. | src/xrpld/app/misc/detail/AmendmentTable.cpp:847-935 (doVoting), lines 902-923. |
| S-05 | recordVotes ignores validations from untrusted validators and clears a validator's recorded votes 24 hours after its last validation. | src/xrpld/app/misc/detail/AmendmentTable.cpp:153-263, expiresAfter = 24h at line 172, untrusted ignored at lines 214-220, expiry cleared at lines 240-250. |
| S-06 | doValidation returns only supported, up-voted, not-yet-enabled amendments, sorted by amendment ID. | src/xrpld/app/misc/detail/AmendmentTable.cpp:817-840. |
| S-07 | The fixAmendmentMajorityCalc feature gates the post-fix (strict >) threshold comparison. | include/xrpl/protocol/detail/features.macro:104; src/xrpld/app/misc/detail/AmendmentTable.cpp:326-377. |
| S-08 | The pinned validator quorum is 67% (max of ceil(effectiveUnlSize * 0.67) and ceil(unlSize * 0.6)); upstream rippled 2.5.0 uses 80%. The pinned source comments that 67% is for devnet/testnet and mainnet should revert to 80%. | src/xrpld/app/misc/detail/ValidatorList.cpp:1898-1900 (comment) and 1934 (formula); upstream ValidatorList.cpp:1872 and return formula with 0.8f. |
| S-09 | The publisher list threshold defaults to 1 for fewer than 3 publishers, otherwise publishers/2 + 1, unless overridden in configuration. | src/xrpld/app/misc/detail/ValidatorList.cpp:197-215. |
| S-10 | updateTrusted adds a validator to the trusted set only when it is listed on at least listThreshold_ publisher lists and its manifest is not revoked, and removes it otherwise. | src/xrpld/app/misc/detail/ValidatorList.cpp:2036-2066. |
| S-11 | A publisher list is applied only after its manifest deserializes and its signature verifies against the publisher key; a revoked publisher manifest is rejected at load time. | src/xrpld/app/misc/detail/ValidatorList.cpp:1158-1183 (applyList), 1413-1443 (verify), 178-181 (revoked publisher rejected at load). |
| S-12 | A publisher list whose sequence is below the current sequence is stale, equal is already known, and above the maximum is new. | src/xrpld/app/misc/detail/ValidatorList.cpp:1427-1443. |
| S-13 | The default fee schedule is a 10-drop reference fee, a 10 XRP account reserve, and a 2 XRP per-owned-item reserve increment. | src/xrpld/core/Config.h:66-77 (struct FeeSetup, default-constructed values). |
| S-14 | A malformed transaction fee (non-native, negative, or illegal amount) is rejected in preflight with temBAD_FEE. | src/xrpld/app/tx/detail/Transactor.cpp:214-218. |
| S-15 | checkFee compares the fee paid against the load-scaled minimum fee only when the ledger is open, and returns telINSUF_FEE_P when the fee paid is below the fee due. | src/xrpld/app/tx/detail/Transactor.cpp:379-413. |
| S-16 | checkSeqProxy returns terNO_ACCOUNT for a missing source account, terPRE_SEQ for a future sequence, tefPAST_SEQ for a past sequence, and success when the sequences match. | src/xrpld/app/tx/detail/Transactor.cpp:480-550. |
| S-17 | scaleFeeLoad computes fee * feeFactor / loadBase with integer division; the normal load base is 256 and the maximum fee is 256 * 1,000,000. | src/xrpld/app/misc/detail/LoadFeeTrack.cpp:84-110; src/xrpld/app/misc/LoadFeeTrack.h:141-147. |
| S-18 | Fee escalation parameters: minimum escalation multiplier baseLevel * 500, minimum 32 transactions per ledger before escalation (1000 standalone), target 256 transactions per ledger, replacement transactions pay at least 25% more for the same sequence. | src/xrpld/app/misc/TxQ.h:98-113. |
| S-19 | The pinned ValidatorList implementation differs from upstream rippled 2.5.0 (69 diff lines): manifest promotion to trusted on listing, uncapped manifest rate-limit policy, deserialized-manifest applyList path, and the 67% quorum. | diff of src/xrpld/app/misc/detail/ValidatorList.cpp against upstream 2.5.0. |
| S-20 | Ledger fee settings are per-ledger values (base reference cost, reserve base, reserve increment); the account reserve for a given owner count is reserve + ownerCount * increment. | include/xrpl/protocol/Fees.h:32-57 (struct Fees, accountReserve). |
