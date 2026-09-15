# A6 Real Voice / Audio Validation V1

## 1. Status

```text
ISSUE: #18
BLOCK: A6
STATUS: ACTIVE
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
A2 conversational/domain semantics
→ A3 verification principles
→ A5 provider-configuration authority + read-only harness
→ A6 real audio/device/transport evidence
```

A3 was written before the roadmap resequencing and uses the historical label:

```text
A5_REAL_AUDIO_REQUIRED
```

That historical owner maps to current A6. The A3 semantics are not rewritten.

## 3. A5 provider-drift gate

A5 Phase 1 completed with:

```text
A5_PHASE_1_REPOSITORY: PASS
A5_PROVIDER_RESULT: DRIFT
```

Therefore A6 separates two claims:

```text
hardware / transport result
!=
expected-provider semantic/configuration result
```

Before any provider-dependent phone/AI test, rerun the A5 GET-only harness and record only the sanitized field verdicts.

If the provider remains different from `A5_EXPECTED_PROVIDER_CONFIGURATION_V1`, AI audio/conversation results are labeled:

```text
CURRENT_PROVIDER_DRIFT_BASELINE
```

They may describe the observed current provider, but they must not be reported as PASS for the expected GitHub configuration.

Changing provider configuration is outside A6 and requires separate authorization.

## 4. Test topology

A6 validates available laboratory legs independently.

```text
A6-A
existing direct phone path
↔ AI Control

A6-B
lab phone with Zello
↔ Zello transport
↔ UNIWA F400

A6-C
controlled acoustic/noise conditions
applied to the available legs
```

A6 does not assume an AI Control → Zello/F400 bridge exists.

If such a bridge is absent:

```text
FULL_COMBINED_PATH: NOT_AVAILABLE
```

Do not create one inside A6.

## 5. Public-laboratory data boundary

Use only synthetic identities and dummy operational values.

Example test vocabulary:

```text
Persona Alfa
Modelo X
Línea Uno
OP100
Robot R1
problema de prueba
```

Never commit:

- real worker names;
- real protected operational audio;
- production identifiers;
- credentials or API keys;
- corporate-network information;
- raw provider resource IDs when a sanitized fingerprint is sufficient.

Raw audio may be used locally for inspection but is not committed by default.

## 6. Current official technical evidence

Revalidated for A6 on 2026-09-14.

### 6.1 UNIWA F400

Current vendor specification states the F400 provides:

- Android 15;
- dedicated PTT button;
- front 2.5 W speaker;
- IP65 protection;
- Wi-Fi / 4G / Bluetooth;
- PoC support including Zello.

Reference:

https://www.cwelltech.com/product/uniwa-f400-octa-core-ip65-android-15-walkie-talkie/

This supports feasibility only. Actual device behavior is determined by physical evidence.

### 6.2 Zello Android PTT behavior

Current Zello support documentation states that Android device PTT buttons may be assigned, while its generic device-button guidance distinguishes screen-on and screen-off cases.

References:

https://support.zello.com/zc/using-volume/screen-button-for-ptt-android
https://support.zello.com/zc/using-zello-while-screen-is-off-android

The F400 vendor separately advertises dedicated real PTT + Zello support. A6 therefore treats the already completed physical F400 test as stronger evidence for this specific device than generic Android behavior.

### 6.3 ElevenLabs latency

ElevenLabs distinguishes model inference latency from user-perceived time-to-first-audio (TTFA). Network, recognition, LLM, TTS and playback buffering all contribute to end-to-end voice-agent latency.

References:

https://elevenlabs.io/docs/eleven-api/concepts/latency
https://elevenlabs.io/docs/eleven-api/guides/how-to/best-practices/latency-optimization

A6 does not invent a historical latency figure that was never recorded.

## 7. Verdict and evidence model

Per newly executed A6 scenario:

```text
PASS
FAIL
NOT_RUN
NOT_AVAILABLE
UNVERIFIABLE
```

Historical laboratory observations that predate A6 and were not versioned with exact per-scenario metadata use:

```text
HISTORICAL_PHYSICAL_EVIDENCE
```

Rules:

- historical evidence may prevent unnecessary repetition of a capability already demonstrated;
- historical evidence must not be upgraded into an exact run count, latency figure, clipping score or other metric that was not retained;
- a missing historical metric is `UNVERIFIABLE` from retained evidence, not `FAIL` and not a fabricated PASS;
- one prohibited/safety behavior is FAIL;
- provider `DRIFT` is not silently converted to expected-config PASS.

## 8. Preflight

### A6-PRE-01 — Exact repository state

Observed before A6 consolidation:

```text
main SHA: 7f6150b69f007aeea0e38cd5159eb2e244ff3e32
A6 branch/head initially synchronized: 38058ec5da1efd6cbf8afc958a26e388bbfade8f
working tree: clean at synchronization
```

Any later head change requires recording the new exact head for evidence generated after that change.

### A6-PRE-02 — Provider baseline

Before A6-A provider-dependent testing:

1. execute the A5 harness GET-only;
2. record `OVERALL` and field-level statuses only;
3. clear the API key from the local environment;
4. do not commit generated provider output unless manually sanitized.

### A6-PRE-03 — Device/channel inventory

Historical physical testing covered the available F400/Zello laboratory device path. Do not reconstruct missing app-version/volume metadata from memory.

## 9. Prior physical audit carried into A6

Before A6 was opened, the laboratory had already completed the physical F400/Zello audit with an overall PASS.

Previously exercised surfaces included:

```text
mobile with Zello ↔ UNIWA F400 with Zello
bidirectional communication
F400 dedicated physical PTT
PTT with Zello in background
PTT / receive behavior with screen locked or off
real audio under noise
reception with device locked
long-session / battery behavior
private Wi-Fi path
SIM / mobile-data path
```

Recorded historical result:

```text
PHYSICAL_F400_ZELLO_AUDIT: PASS
EVIDENCE_CLASS: HISTORICAL_PHYSICAL_EVIDENCE
```

The historical audit did not retain a per-scenario table with exact run counts, phrase-by-phrase clipping results, latency distribution or every device/app setting. Those missing details are not invented now.

Therefore A6 does **not** repeat the completed physical audit merely to recreate richer metadata after the fact.

## 10. A6-B — Zello phone ↔ F400 evidence map

| ID | Surface | A6 treatment | Status |
|---|---|---|---|
| `ZEL-01` | phone → F400 basic receive | covered by prior physical audit | HISTORICAL_PHYSICAL_EVIDENCE |
| `ZEL-02` | F400 → phone physical PTT/transmit | covered by prior physical audit | HISTORICAL_PHYSICAL_EVIDENCE |
| `ZEL-03` | F400 PTT with Zello background | covered by prior physical audit | HISTORICAL_PHYSICAL_EVIDENCE |
| `ZEL-04` | F400 screen locked/off behavior | covered by prior physical audit | HISTORICAL_PHYSICAL_EVIDENCE |
| `ZEL-05` | exact first-token clipping score phone → F400 | exact score not retained | UNVERIFIABLE |
| `ZEL-06` | exact first-token clipping score F400 → phone | exact score not retained | UNVERIFIABLE |
| `ZEL-07` | exact last-token clipping score | exact score not retained | UNVERIFIABLE |
| `ZEL-08` | repeated-transmission robustness | repeated basic success observed; exact run count not retained | HISTORICAL_PHYSICAL_EVIDENCE |
| `ZEL-09` | F400 speaker intelligibility | successful real communication observed | HISTORICAL_PHYSICAL_EVIDENCE |
| `ZEL-10` | F400 microphone intelligibility | successful real communication observed | HISTORICAL_PHYSICAL_EVIDENCE |

The `UNVERIFIABLE` clipping metrics above are evidence-granularity gaps. They are not a request to redo the complete historical audit inside A6.

## 11. A6-C — environment/device robustness evidence map

| ID | Condition | A6 treatment | Status |
|---|---|---|---|
| `ENV-01` | controlled/background noise | audio-with-noise physical test previously passed globally | HISTORICAL_PHYSICAL_EVIDENCE |
| `ENV-02` | competing nearby speech | no retained isolated result | UNVERIFIABLE |
| `ENV-03` | explicit speaker overlap/interruption | no retained isolated result | UNVERIFIABLE |
| `ENV-04` | repeat after unclear audio | no retained isolated result | UNVERIFIABLE |
| `DEV-01` | long-session / battery behavior | previously exercised with global PASS | HISTORICAL_PHYSICAL_EVIDENCE |
| `NET-01` | private Wi-Fi | previously exercised with global PASS | HISTORICAL_PHYSICAL_EVIDENCE |
| `NET-02` | SIM / mobile data | previously exercised with global PASS | HISTORICAL_PHYSICAL_EVIDENCE |

No new physical rerun is required merely to fill historical metadata gaps. If a later product decision requires quantified clipping, overlap or latency thresholds, that should be a targeted measurement objective with explicit acceptance criteria rather than a retroactive reconstruction.

## 12. A6-A — existing direct phone / AI Control path

This surface is separate from the completed F400/Zello physical audit.

Execute only if an already existing isolated phone/AI Control path is available.

If it is not already available:

```text
A6-A: NOT_AVAILABLE
```

Do not provision SIP/telephony inside A6.

Before execution, A6-PRE-02 is mandatory.

Provider-dependent results must include one of:

```text
EXPECTED_PROVIDER_ALIGNED
CURRENT_PROVIDER_DRIFT_BASELINE
```

Potential phone evidence, only if the path already exists:

```text
connection/session works
first user utterance is intelligible
agent response is intelligible
user-end → first-agent-audio latency can be measured
interruption/unclear-audio behavior can be observed
```

No PASS/FAIL latency SLA is invented in A6 V1.

## 13. Result record

For newly executed provider-dependent evidence record:

```text
Date/time
A6 branch/head SHA
Provider baseline classification
Available phone path
Observed result
Latency samples if measured
Concise sanitized notes
```

For carried historical observations, use `HISTORICAL_PHYSICAL_EVIDENCE` and preserve their limitations instead of inventing missing metadata.

Do not commit secrets, raw provider responses, real identities or protected audio.

## 14. A6 completion rules

A6 must preserve two distinct conclusions:

```text
F400/ZELLO PHYSICAL AUDIT
→ historical overall PASS
→ granular metrics partially unavailable

PHONE/AI CONTROL PROVIDER-DEPENDENT PATH
→ separate evidence surface
→ gated by current A5 GET-only provider baseline
```

A6 is ready for final audit when:

- the historical F400/Zello audit is accurately recorded without fabricated per-run detail;
- granular gaps are explicitly `UNVERIFIABLE` rather than silently upgraded to PASS;
- A6-A is executed if an existing isolated phone path is already available, otherwise recorded as `NOT_AVAILABLE`;
- any provider-dependent evidence is tied to a current GET-only provider baseline;
- no unauthorized configuration/integration change occurs;
- complete diff and exact-head evidence are reviewed;
- PR remains Draft until Albert authorizes Ready.

## 15. Current stop point

```text
A6: ACTIVE
ISSUE: #18
F400_ZELLO_PHYSICAL_AUDIT: HISTORICAL_PASS
F400_ZELLO_REPEAT_AUDIT: NOT_REQUIRED
GRANULAR_HISTORICAL_METRICS: PARTIALLY_UNVERIFIABLE
A6_A_PHONE_AI_PATH: PENDING_AVAILABILITY_CHECK
PROVIDER_WRITE: NOT_AUTHORIZED
A7: NOT_AUTHORIZED
```

Next action: determine only whether the already-existing isolated direct phone/AI Control path is available; if yes, rerun the A5 GET-only baseline before that provider-dependent test. Do not repeat the completed F400/Zello physical audit.

No canonical-state update required.
