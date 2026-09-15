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

This supports feasibility only. Actual A6 device behavior is determined by the physical test unit.

### 6.2 Zello Android PTT behavior

Current Zello support documentation states that Android device PTT buttons may be assigned, but its general device-button guidance says device PTT buttons operate with the screen on and talk screen in the foreground.

Reference:

https://support.zello.com/zc/using-volume/screen-button-for-ptt-android

Zello also documents screen-off transmission for Android when an external PTT or wired/Bluetooth headset button is connected, with the active contact already selected.

Reference:

https://support.zello.com/zc/using-zello-while-screen-is-off-android

The F400 vendor separately advertises dedicated real PTT + Zello support. Because the built-in F400 PTT implementation may present differently from a generic Android device button, A6 does not assume screen-off behavior from either source. It measures it empirically unless prior laboratory evidence already establishes the specific behavior with adequate detail.

### 6.3 ElevenLabs latency

ElevenLabs distinguishes model inference latency from user-perceived time-to-first-audio (TTFA). Network, recognition, LLM, TTS and playback buffering all contribute to end-to-end voice-agent latency.

References:

https://elevenlabs.io/docs/eleven-api/concepts/latency
https://elevenlabs.io/docs/eleven-api/guides/how-to/best-practices/latency-optimization

A6 therefore measures the real user-perceived path rather than treating a provider model benchmark as the result.

## 7. Verdict and evidence model

Per newly executed A6 scenario:

```text
PASS
FAIL
NOT_RUN
NOT_AVAILABLE
UNVERIFIABLE
```

Historical laboratory observations that predate A6 and were not versioned with exact run metadata use the separate evidence label:

```text
HISTORICAL_PHYSICAL_EVIDENCE
```

Rules:

- historical evidence may prevent unnecessary repetition of a basic capability already demonstrated;
- historical evidence must not be upgraded into an exact A6 run count, latency figure, clipping result or environmental robustness result that was not recorded at the time;
- one prohibited/safety behavior is FAIL;
- `NOT_AVAILABLE` is not silently converted to PASS;
- provider `DRIFT` is not silently converted to expected-config PASS;
- qualitative claims must be backed by repeated observation;
- latency is recorded before defining any future product SLA.

## 8. Preflight

### A6-PRE-01 — Exact repository state

Observed before physical A6 execution:

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

Record without secrets:

```text
F400 Android version
Zello app version on F400
Zello app version on phone
network type: private Wi-Fi or public/mobile LTE
screen state
speaker volume setting as a relative percentage if visible
headset/external PTT: yes/no
existing direct phone path available: yes/no
```

Do not use the corporate network.

## 9. Prior physical evidence carried into A6

Before A6 was opened, the laboratory had already exercised the real Zello path using the phone and the UNIWA F400.

The previously observed minimum evidence is:

```text
mobile with Zello ↔ UNIWA F400 with Zello: communication OK in both directions
F400 dedicated physical PTT: operational
basic communication: repeated successfully
```

Evidence classification:

```text
HISTORICAL_PHYSICAL_EVIDENCE
```

Limitations of this historical evidence:

- exact run count was not versioned;
- exact test phrases were not versioned;
- no exact clipping score was recorded;
- no latency distribution was recorded;
- no controlled-noise/overlap result was recorded;
- no exact A6 branch/head SHA can be attached because the observations predate A6.

Therefore A6 does **not** repeat basic proof that Zello can pass audio between the phone and F400 or that the F400 physical PTT can transmit under the previously tested normal condition. It still executes the narrower measurements that were not previously captured.

## 10. A6-B — Zello phone ↔ F400 matrix

Use the same dummy phrase set in both directions for newly executed clipping/reliability measurements.

Default repetition rule for new A6 execution:

```text
functional scenario: 5 repetitions
critical clipping/reliability scenario: 10 repetitions
```

Any single prohibited behavior still fails the relevant safety scenario.

| ID | Direction/state | What to verify | PASS condition | Runs | Status |
|---|---|---|---|---:|---|
| `ZEL-01` | phone → F400, screen on | basic receive audio | basic bidirectional Zello communication was previously observed | historical | HISTORICAL_PHYSICAL_EVIDENCE |
| `ZEL-02` | F400 → phone, screen on | basic physical PTT + transmit | physical F400 PTT and transmission were previously observed | historical | HISTORICAL_PHYSICAL_EVIDENCE |
| `ZEL-03` | F400, Zello background, screen on | physical PTT behavior | actual behavior recorded; PASS only if transmission works without unintended UI dependency | 5 | NOT_RUN |
| `ZEL-04` | F400, screen off | physical PTT behavior | actual behavior recorded; PASS only if intended transmission works reliably | 5 | NOT_RUN |
| `ZEL-05` | phone → F400 | first-token clipping | critical first token preserved 10/10 | 10 | NOT_RUN |
| `ZEL-06` | F400 → phone | first-token clipping | critical first token preserved 10/10 | 10 | NOT_RUN |
| `ZEL-07` | both directions | last-token clipping | critical final token preserved 10/10 each direction | 10 | NOT_RUN |
| `ZEL-08` | both directions | repeated transmission robustness | no dropped/empty transmission in run set | 10 | NOT_RUN |
| `ZEL-09` | F400 receive | speaker intelligibility | dummy phrase understood without visual/text aid | 5 | NOT_RUN |
| `ZEL-10` | F400 transmit | microphone intelligibility | dummy phrase understood without repetition | 5 | NOT_RUN |

`ZEL-01` and `ZEL-02` are not requested again merely to recreate evidence that already exists. They are not equivalent to the exact-run clipping/reliability scenarios below.

### Clipping phrase set

Use clearly synthetic tokens:

```text
ALFA uno dos tres
BRAVO modelo X línea uno
CHARLIE OP100 robot R1
uno dos tres OMEGA
modelo X línea uno SIGMA
```

The critical first/last token must be heard completely; guessing from context is not PASS.

## 11. A6-C — controlled noise and overlap

No real workshop recording is required.

Use controlled local background audio at a stable level and synthetic phrases.

| ID | Condition | PASS condition | Runs | Status |
|---|---|---|---:|---|
| `ENV-01` | moderate controlled background noise | critical tokens remain intelligible | 5 | NOT_RUN |
| `ENV-02` | competing nearby speech | receiver can identify whether test phrase is intelligible; no fabricated transcription claim | 5 | NOT_RUN |
| `ENV-03` | speaker overlap / interruption | recovery behavior is observable and recorded | 5 | NOT_RUN |
| `ENV-04` | repeat after unclear audio | second transmission recovers without stale/mixed phrase | 5 | NOT_RUN |

If a condition cannot be produced consistently, use `UNVERIFIABLE` rather than inventing a result.

## 12. A6-A — existing direct phone / AI Control path

Execute only if an already existing isolated phone path is available.

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

### Phone scenarios

| ID | What to measure | Evidence | Runs | Status |
|---|---|---|---:|---|
| `PHN-01` | successful existing-path connection | real isolated call/session | 5 | NOT_RUN |
| `PHN-02` | first user utterance intelligibility | critical dummy tokens retained | 5 | NOT_RUN |
| `PHN-03` | agent response intelligibility | human listener result | 5 | NOT_RUN |
| `PHN-04` | user-end → first-agent-audio latency | milliseconds per turn | 10 | NOT_RUN |
| `PHN-05` | overlap/interruption behavior | observed recovery | 5 | NOT_RUN |
| `PHN-06` | unclear/clipped utterance recovery | no silent guessing; observed response recorded | 5 | NOT_RUN |

For `PHN-04`, report at minimum:

```text
sample count
minimum
median
maximum
```

No PASS/FAIL latency SLA is invented in V1. The measurement becomes evidence for a later threshold decision.

## 13. Result record

For each newly executed scenario record:

```text
Scenario ID
Date/time
A6 branch/head SHA
Provider baseline classification where applicable
Device direction
Network type
Screen/background state
Run count
PASS / FAIL / NOT_RUN / NOT_AVAILABLE / UNVERIFIABLE
Observed clipping or dropped token
Latency samples if applicable
Concise sanitized notes
```

For carried historical observations, record `HISTORICAL_PHYSICAL_EVIDENCE` and its limitations instead of inventing missing metadata.

Do not commit secrets, raw provider responses, real identities or protected audio.

## 14. A6 completion rules

A6 is not complete merely because basic Zello connectivity was already demonstrated.

Required for final audit:

- historical Zello/F400 basic-connectivity evidence explicitly separated from new A6 exact-run evidence;
- ZEL-03/ZEL-04 executed if those background/screen-off states were not previously evidenced with sufficient detail, otherwise the prior evidence must be described precisely;
- controlled first/last-token clipping and repeated-transmission scenarios executed;
- F400 speaker/microphone intelligibility measured under the A6 phrase set;
- A6-C robustness evidence recorded;
- A6-A executed if an existing direct phone path is available, otherwise explicitly `NOT_AVAILABLE`;
- current provider baseline tied to provider-dependent tests;
- transport/device conclusions separated from provider-semantic conclusions;
- no unauthorized configuration/integration changes;
- complete diff reviewed;
- exact head/status evidence recorded;
- PR remains Draft until Albert authorizes Ready.

## 15. Current stop point

```text
A6: ACTIVE
ISSUE: #18
BASIC_ZELLO_F400_CONNECTIVITY: HISTORICAL_PHYSICAL_EVIDENCE
ZEL-01/ZEL-02_REPEAT: NOT_REQUIRED
NEW_EXACT_RUN_AUDIO_EVIDENCE: NOT_STARTED
PROVIDER_WRITE: NOT_AUTHORIZED
A7: NOT_AUTHORIZED
```

Next action: execute only the A6 measurements not already established by prior physical testing, beginning with the missing F400 background/screen-off behavior or clipping/reliability evidence as applicable.

No canonical-state update required.
