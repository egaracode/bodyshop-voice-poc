# A6 Targeted Measurement Results V1

## 1. Scope

This document records the targeted physical measurements authorized under Issue #18 after reconciliation with the merged F400 smoke-test evidence.

It does not repeat already-versioned PASS surfaces and does not authorize any provider write, telephony integration, Zello API automation, BODYSHOP integration or A7 work.

## 2. Repository evidence anchor

The targeted measurements were executed while the local A6 branch was synchronized to:

```text
branch: feat/a6-real-voice-audio-validation-v1
head: 5705ee53adad83561b6517baf51ca7efc0841675
```

The result-document commit itself necessarily moves the branch head. The physical observations below remain tied to the pre-result-recording head above.

## 3. Canonical historical PASS surfaces not repeated

Merged `docs/F400_SMOKE_TEST_REPORT_V1.md` already records PASS for:

- phone ↔ F400 Zello communication in both directions;
- physical F400 PTT;
- background operation;
- screen-off operation;
- isolated dummy-terminal use.

A6 did not repeat those tests merely to recreate metadata.

## 4. A6-NOISE-01 — simulated/noisy-environment robustness

Authorized target:

```text
simulated/noisy-environment robustness
```

Execution:

```text
F400 → phone: 5 transmissions
phone → F400: 5 transmissions
synthetic/dummy phrases only
```

User-reported result:

```text
F400 → phone: 5/5 PASS
phone → F400: 5/5 PASS
TOTAL: 10/10 PASS
```

The exact noise source and its level were not retained in the final user report and are therefore not reconstructed.

Verdict:

```text
A6_NOISE_01: PASS
```

Limit:

```text
NOISE_SOURCE_METADATA: NOT_RETAINED
NOISE_LEVEL_METADATA: NOT_RETAINED
```

## 5. A6-LATENCY-01 — observed Zello path latency

Authorized target:

```text
objective Zello path latency measurement
```

Observed user result:

```text
bidirectional latency: approximately less than 0.5 seconds
```

This is useful physical evidence but no exact frame counts, timestamp samples, minimum, median or maximum were retained.

Therefore two claims are separated:

```text
LATENCY_APPROXIMATE_OBSERVATION: PASS
OBSERVED_LATENCY: approximately < 0.5 s bidirectionally
OBJECTIVE_LATENCY_DISTRIBUTION: UNVERIFIABLE
```

A6 does not invent a product SLA or convert the approximate observation into an exact distribution.

## 6. A6-LONG-01 — prolonged-session stability

Authorized target:

```text
prolonged-session stability
```

Execution contract:

```text
duration: 30 minutes
checkpoints: start, ~10 min, ~20 min, ~30 min
bidirectional Zello path
physical F400 PTT remains in use
```

User-reported result:

```text
start: PASS
10 min: PASS
20 min: PASS
30 min: PASS
all requested prolonged-session checks: PASS
```

No battery start/final percentages were supplied, so no battery-consumption claim is made.

Verdict:

```text
A6_LONG_01: PASS
PROLONGED_SESSION_STABILITY: PASS
BATTERY_DELTA: NOT_RETAINED
```

## 7. Direct phone / AI Control boundary

Repository inspection found no existing isolated telephony/SIP/Twilio/phone integration implementation.

Therefore:

```text
A6_A_DIRECT_PHONE_AI_PATH: NOT_AVAILABLE
FULL_AI_CONTROL_TO_F400_PATH: NOT_AVAILABLE
```

A6 did not provision either path.

## 8. Provider boundary

A5 remains:

```text
A5_PROVIDER_RESULT: DRIFT
```

No ElevenLabs configuration write, Publish, provider branch/version/deployment mutation or provider-dependent direct-phone execution occurred in A6.

## 9. Consolidated A6 evidence

```text
F400_ZELLO_BASIC_SMOKE_TEST: PASS
PHYSICAL_PTT: PASS
BACKGROUND_OPERATION: PASS
SCREEN_OFF_OPERATION: PASS
NOISE_ROBUSTNESS: PASS
LATENCY_APPROXIMATE_OBSERVATION: PASS
OBSERVED_LATENCY: approximately < 0.5 s bidirectionally
OBJECTIVE_LATENCY_DISTRIBUTION: UNVERIFIABLE
PROLONGED_SESSION_STABILITY: PASS
BATTERY_DELTA: NOT_RETAINED
DIRECT_PHONE_AI_PATH: NOT_AVAILABLE
FULL_AI_CONTROL_TO_F400_PATH: NOT_AVAILABLE
```

## 10. A6 completion interpretation

The three targeted evidence gaps authorized after smoke-test reconciliation have now been addressed as follows:

```text
noise: executed → PASS
latency: executed observationally → approximate < 0.5 s; exact distribution UNVERIFIABLE
prolonged session: executed → PASS
```

A6 does not weaken its evidence model by pretending the latency distribution was measured precisely. Under Issue #18 acceptance, the targeted gap may be closed with the exact-distribution limitation explicitly retained as `UNVERIFIABLE`.

## 11. Stop point

```text
A6_TARGETED_MEASUREMENTS: COMPLETE
A6_EVIDENCE_PACKAGE: COMPLETE_WITH_RETAINED_LIMITATIONS
READY: PENDING_FINAL_AUDIT_AND_ALBERT
MERGE: NOT_AUTHORIZED
A7: NOT_AUTHORIZED
```

No canonical-state update required.
