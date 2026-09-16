# A6 Real Voice / Audio Validation V1

## 1. Status

```text
ISSUE: #18
BLOCK: A6
STATUS: ACTIVE / EVIDENCE_COMPLETE_WITH_RETAINED_LIMITATIONS
BASE_MAIN: 7f6150b69f007aeea0e38cd5159eb2e244ff3e32
PROVIDER_WRITES: FORBIDDEN
PRODUCTION: FORBIDDEN
A7: NOT_AUTHORIZED
```

A6 validates real laboratory audio/device/PTT/transport behavior for the isolated Voice PoC.

It does not build production integration and does not correct ElevenLabs configuration.

## 2. Authority and historical numbering

Authority order:

```text
GitHub LIVE / merged repository evidence
→ A2 conversational/domain semantics
→ A3 verification principles
→ A5 provider-configuration authority + read-only harness
→ A6 real audio/device/transport evidence
→ chat/memory only as supporting context
```

A3 was written before roadmap resequencing and uses the historical label `A5_REAL_AUDIO_REQUIRED`. That historical owner maps to current A6; A3 semantics are not rewritten.

## 3. A5 provider-drift gate

A5 Phase 1 completed with:

```text
A5_PHASE_1_REPOSITORY: PASS
A5_PROVIDER_RESULT: DRIFT
```

Therefore:

```text
hardware / transport result
!=
expected-provider semantic/configuration result
```

Before any provider-dependent phone/AI test, rerun the A5 GET-only harness. A drifted provider baseline may be observed but must not be represented as PASS for `A5_EXPECTED_PROVIDER_CONFIGURATION_V1`.

Changing provider configuration is outside A6 and requires separate authorization.

## 4. Test topology

```text
A6-A
existing direct phone path
↔ AI Control

A6-B
lab phone with Zello
↔ Zello transport
↔ UNIWA F400

A6-C
acoustic / robustness evidence
```

A6 does not assume an AI Control → Zello/F400 bridge exists and does not create one.

## 5. Public-laboratory data boundary

Use only synthetic identities and dummy operational values. Do not commit real worker names, protected operational audio/data, production identifiers, credentials, corporate-network information or unnecessary raw provider IDs.

## 6. Current official technical evidence

Revalidated for A6 on 2026-09-14.

### 6.1 UNIWA F400

Vendor material supports Android 15, dedicated PTT, 2.5 W front speaker, Wi-Fi/4G/Bluetooth and PoC/Zello suitability. Vendor claims support feasibility only; repository physical evidence controls the A6 verdict for the tested unit.

Reference:

https://www.cwelltech.com/product/uniwa-f400-octa-core-ip65-android-15-walkie-talkie/

### 6.2 Zello

Generic Android guidance documents device-button and screen-off behavior, but the tested F400-specific behavior is established by the merged physical smoke-test report rather than inferred from generic documentation.

References:

https://support.zello.com/zc/using-volume/screen-button-for-ptt-android
https://support.zello.com/zc/using-zello-while-screen-is-off-android

### 6.3 ElevenLabs latency

ElevenLabs distinguishes model inference from user-perceived time-to-first-audio / end-to-end latency. A6 does not invent a latency value that was never measured and retained.

References:

https://elevenlabs.io/docs/eleven-api/concepts/latency
https://elevenlabs.io/docs/eleven-api/guides/how-to/best-practices/latency-optimization

## 7. Verdict and evidence model

```text
PASS
FAIL
NOT_RUN
NOT_AVAILABLE
UNVERIFIABLE
HISTORICAL_PHYSICAL_EVIDENCE
```

Rules:

- merged/versioned repository evidence outranks chat/memory;
- historical evidence may prevent unnecessary repetition of a capability already demonstrated;
- missing metrics are `UNVERIFIABLE`, not fabricated PASS;
- one prohibited/safety behavior is FAIL;
- provider `DRIFT` is not silently converted to expected-config PASS.

## 8. Exact repository preflight

Initial A6 synchronization was observed at:

```text
main: 7f6150b69f007aeea0e38cd5159eb2e244ff3e32
A6 initial synchronized head: 38058ec5da1efd6cbf8afc958a26e388bbfade8f
working tree: clean
```

The targeted physical measurements were later executed while the local A6 branch was synchronized to:

```text
5705ee53adad83561b6517baf51ca7efc0841675
```

Later result-documentation commits necessarily move the branch head. The physical observations remain tied to the exact pre-result-recording head above.

## 9. Canonical historical F400/Zello evidence

The merged `docs/F400_SMOKE_TEST_REPORT_V1.md` is the authoritative historical physical record.

It records PASS for:

```text
F400 powered/operational
Google Play confirmed
Zello operational on F400
F400 and phone connected to Zello
voice F400 → phone
voice phone → F400
physical PTT button
background operation
screen-off operation
use as dummy technical terminal
```

The report identifies Albert as executor and records the manual smoke test date as `2026-09-01`.

Canonical historical verdict:

```text
VOICE_POC_F400_MANUAL_SMOKE_TEST_V1: PASS
EVIDENCE_CLASS: HISTORICAL_PHYSICAL_EVIDENCE
```

A6 does not repeat those already versioned smoke-test capabilities merely to recreate evidence.

## 10. Canonical historical gaps

The same merged smoke-test report explicitly listed these as pending before broader use:

```text
behavior in real or simulated noisy environment
more objective latency measurement
stability during long sessions
Android/Zello update-policy confirmation
permissions review
```

Albert later authorized targeted A6 measurements only for the first three physical evidence gaps. Update-policy and permissions review were not added to the A6 physical-measurement objective.

Historical classification before the targeted measurements was:

| Surface | Historical status | Reason |
|---|---|---|
| basic phone↔F400 Zello audio | HISTORICAL_PHYSICAL_EVIDENCE | merged smoke test PASS |
| F400 physical PTT | HISTORICAL_PHYSICAL_EVIDENCE | merged smoke test PASS |
| Zello background behavior | HISTORICAL_PHYSICAL_EVIDENCE | merged smoke test PASS |
| screen-off behavior | HISTORICAL_PHYSICAL_EVIDENCE | merged smoke test PASS |
| noise robustness | UNVERIFIABLE | merged smoke test left it pending |
| objective latency | UNVERIFIABLE | merged smoke test left it pending |
| prolonged-session stability | UNVERIFIABLE | merged smoke test left it pending |
| exact first/last-token clipping score | UNVERIFIABLE | no retained canonical measurement |
| competing-speech / overlap behavior | UNVERIFIABLE | no retained canonical measurement |

## 11. A6-A — direct phone / AI Control path

Repository tree inspection found documentation, the A5 read-only provider harness/tests and expected provider JSON, but no telephony/SIP/Twilio/phone integration implementation.

Repository search for telephony/SIP/Twilio/phone-integration code also returned no implementation evidence.

Therefore, under the current A6 rule that no new telephony may be provisioned:

```text
A6-A_DIRECT_PHONE_AI_PATH: NOT_AVAILABLE
FULL_AI_CONTROL_TO_F400_PATH: NOT_AVAILABLE
```

This does not say a future direct-phone integration is impossible. It says it does not currently exist as an isolated executable path in this repository and A6 is not authorized to create it.

## 12. Targeted measurement results

Detailed results are versioned in:

`docs/A6_TARGETED_MEASUREMENT_RESULTS_V1.md`

Observed results:

```text
A6-NOISE-01: PASS
F400 → phone: 5/5 PASS
phone → F400: 5/5 PASS
TOTAL: 10/10 PASS

A6-LATENCY-01:
approximate bidirectional Zello latency: < 0.5 s
LATENCY_APPROXIMATE_OBSERVATION: PASS
OBJECTIVE_LATENCY_DISTRIBUTION: UNVERIFIABLE

A6-LONG-01: PASS
duration: 30 minutes
start: PASS
~10 min: PASS
~20 min: PASS
~30 min: PASS
PROLONGED_SESSION_STABILITY: PASS
BATTERY_DELTA: NOT_RETAINED
```

No product latency SLA is inferred. Exact battery percentages were not supplied and are not reconstructed.

## 13. A6 evidence conclusion

Current defensible result:

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

A6 retains the exact-latency limitation instead of weakening the evidence model.

## 14. Completion boundary

Albert authorized the targeted-measurement path after the historical evidence contradiction was identified.

The three authorized physical gaps were handled as:

```text
noise → executed → PASS
latency → executed observationally → approximate < 0.5 s; exact distribution UNVERIFIABLE
prolonged session → executed → PASS
```

Under Issue #18 acceptance, the A6 evidence package is complete with the exact-latency limitation explicitly retained.

No ElevenLabs write, Publish, provider branch/version/deployment mutation, telephony provisioning, Zello API automation, Supabase, `AI-Control-Workshop`, production/corporate-network or A7 work occurred.

## 15. Current stop point

```text
A6: EVIDENCE_COMPLETE_WITH_RETAINED_LIMITATIONS
ISSUE: #18
F400_ZELLO_SMOKE_TEST: PASS
BACKGROUND: PASS
SCREEN_OFF: PASS
NOISE: PASS
APPROX_LATENCY: PASS / observed < 0.5 s bidirectionally
OBJECTIVE_LATENCY_DISTRIBUTION: UNVERIFIABLE
PROLONGED_SESSION: PASS
DIRECT_PHONE_AI_PATH: NOT_AVAILABLE
PROVIDER_WRITE: NOT_AUTHORIZED
A7: NOT_AUTHORIZED
READY: PENDING_FINAL_AUDIT_AND_ALBERT
MERGE: NOT_AUTHORIZED
```

STOP in Draft pending final audit and Albert's explicit Ready decision.

No canonical-state update required.
