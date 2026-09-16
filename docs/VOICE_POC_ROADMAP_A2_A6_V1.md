# BODYSHOP Voice PoC Roadmap — A2 to A7 V2

## 1. Purpose

This document records the current authorized functional sequence for the isolated `egaracode/bodyshop-voice-poc` laboratory.

It supersedes the previous A2→A6 sequence while preserving the same repository and safety boundaries. It is a sequencing contract only; later blocks still require their own Issue, branch, validation and Albert authorization.

## 2. Current sequence

```text
A2  Conversational Foundation
    MERGED

A3  Conversational Verification
    + ElevenLabs Test Contract
    MERGED

A4  ElevenLabs Sandbox Agent
    CLOSED / SUPERSEDED / NOT_PASS
    PR #13 CLOSED UNMERGED

A5  ChatGPT ↔ ElevenLabs Provider Control Harness
    MERGED
    Phase 1 READ_ONLY COMPLETE / PASS
    Provider result: DRIFT

A6  Voice / Audio Validation
    phone + F400 + walkie/Zello
    MERGED / EVIDENCE_COMPLETE_WITH_RETAINED_LIMITATIONS
    Issue #18 CLOSED / completed
    PR #19 MERGED
    provider-dependent expected-config PASS remains gated by A5 DRIFT

A7  Future BODYSHOP Integration Evaluation
    only if preceding evidence is acceptable
    GATED / NOT AUTHORIZED
```

## 3. A2 and A3

A2 and A3 remain the merged semantic and verification authority for the Voice PoC.

A2 defines the conversational/domain semantics. A3 defines the verification contract and ownership boundaries.

Neither block is reopened by this roadmap reconciliation.

A3 uses the historical owner label `A5_REAL_AUDIO_REQUIRED` for real-device/audio cases. Because the roadmap was later resequenced, that historical ownership maps to current A6 without changing A3 semantics.

## 4. A4 closure

A4 attempted to establish an isolated ElevenLabs sandbox agent and provider-native verification.

Final classification:

```text
A4_RESULT: SUPERSEDED_BY_PROVIDER_CONTROL_REQUIREMENT
A4_OVERALL: NOT_PASS
READY: NO
MERGE: NO
PR_13: CLOSED_UNMERGED
```

A4 produced useful historical provider/configuration evidence, but manual Dashboard synchronization was not sufficiently reproducible. Its unmerged branch/head is evidence only and is not configuration authority for A5.

## 5. A5 — Provider Control Harness

Status:

```text
MERGED
PR: #15
MERGE_COMMIT: 0f55db18b20446d1f69d4cc5a7860238debc747d
PHASE_1: READ_ONLY COMPLETE / PASS
PROVIDER_RESULT: DRIFT
```

A5 establishes a safe, authenticated, read-only path to inspect the effective ElevenLabs `AI Control` sandbox configuration, normalize it and compare it reproducibly with a GitHub-owned expected configuration.

A5 introduces:

```text
A5_EXPECTED_PROVIDER_CONFIGURATION_V1
```

as the configuration authority for the sandbox.

Authority rules:

```text
A2/A3
→ semantic authority

A5_EXPECTED_PROVIDER_CONFIGURATION_V1
→ provider configuration authority

PR #13 / head 1de7cf9cda806af7b355e3228585cb115347c049
→ historical evidence only
```

No A4 value is inherited automatically when it conflicts with the explicit A5 decision.

Phase 1 completed strictly read-only. No provider write, Publish, provider branch/version mutation or runtime integration occurred. The final provider verdict remained `DRIFT`; that is valid Phase-1 evidence because A5 proves reproducible drift detection rather than provider correction.

Any future controlled provider write requires a separate authorization path.

## 6. A6 — Voice / Audio Validation

Status:

```text
MERGED / EVIDENCE_COMPLETE_WITH_RETAINED_LIMITATIONS
AUTHORIZED: 2026-09-14
ISSUE: #18 CLOSED / completed
PR: #19 MERGED
FINAL_HEAD: 4021f49674e270f408bd15a701992331d7058e06
MERGE_COMMIT: d4b696ef2d32c8e76171f5e8bb2ecf5838e73674
PHYSICAL_EXECUTION_ANCHOR: 5705ee53adad83561b6517baf51ca7efc0841675
TARGETED_MEASUREMENTS: COMPLETE
FINAL_AUDIT: COMPLETE
PROVIDER_WRITE: NOT_AUTHORIZED / NOT_PERFORMED
A7: NOT_AUTHORIZED
```

A6 owns real audio/channel evidence for the available isolated F400/Zello laboratory path.

Canonical historical smoke-test evidence establishes PASS for:

```text
phone ↔ F400 bidirectional Zello audio
physical F400 PTT
background operation
screen-off operation
```

A6 then executed only the previously unresolved targeted measurements:

```text
noise robustness → PASS (10/10 transmissions)
approximate bidirectional latency → observed < 0.5 s
objective latency distribution → UNVERIFIABLE (exact samples not retained)
prolonged-session stability → PASS (30 min checkpoints)
```

The detailed result record is:

`docs/A6_TARGETED_MEASUREMENT_RESULTS_V1.md`

A6 execution contract:

`docs/A6_REAL_VOICE_AUDIO_VALIDATION_V1.md`

Repository inspection found no existing isolated direct phone/AI Control telephony path and no AI Control → Zello/F400 bridge. A6 did not provision either path:

```text
A6_A_DIRECT_PHONE_AI_PATH: NOT_AVAILABLE
FULL_AI_CONTROL_TO_F400_PATH: NOT_AVAILABLE
```

Because A5 ended with provider `DRIFT`, A6 does not claim expected-provider semantic/configuration PASS.

A6 is merged with its exact-latency distribution limitation explicitly retained rather than guessed.

## 7. A7 — Future BODYSHOP Integration Evaluation

A7 is a gated future evaluation only.

It may evaluate a future integration path with BODYSHOP PRO only after the isolated Voice PoC has accumulated acceptable semantic, provider-control and audio evidence and after Albert explicitly authorizes A7.

A7 does not authorize Supabase, `AI-Control-Workshop`, production, corporate-network or lifecycle changes.

## 8. Sequencing rule

```text
A2 MERGED
→ A3 MERGED
→ A4 CLOSED / SUPERSEDED / NOT_PASS
→ A5 PROVIDER CONTROL HARNESS MERGED / PHASE 1 COMPLETE
→ A6 REAL VOICE/AUDIO MERGED / EVIDENCE_COMPLETE_WITH_RETAINED_LIMITATIONS
→ A7 FUTURE INTEGRATION EVALUATION GATED / NOT AUTHORIZED
```

Each block remains governed by:

```text
one objective
→ one Issue
→ one branch
→ one PR
→ validation
→ Albert Ready decision
→ manual merge
```

## 9. Safety boundary

This roadmap does not authorize:

```text
ElevenLabs writes or Publish
provider versioning activation
provider branch creation or deployment
Zello API use or automation
new phone/SIP provisioning or integration
AI Control → Zello/F400 bridge implementation
F400 software/runtime modification beyond ordinary lab configuration needed to execute authorized tests
Supabase
AI-Control-Workshop changes
production use
corporate-network use
dependencies
CI/workflow changes
secrets in chat or public repository
automation with real operational impact
```

Any expansion requires separate explicit authorization.

## 10. Canonical relationship

`egaracode/bodyshop-voice-poc` remains an isolated parallel laboratory.

`egaracode/AI-Control-Workshop` remains the canonical BODYSHOP PRO repository and is untouched by this roadmap.

No canonical-state update required.

## 11. Current stop model

```text
ACTIVE_BLOCK: NONE
A5: MERGED / PHASE_1_COMPLETE / PASS
A5_PROVIDER_RESULT: DRIFT
A6_STATUS: MERGED / EVIDENCE_COMPLETE_WITH_RETAINED_LIMITATIONS
A6_ISSUE: #18 CLOSED / completed
A6_PR: #19 MERGED
A6_MERGE_COMMIT: d4b696ef2d32c8e76171f5e8bb2ecf5838e73674
A6_TARGETED_MEASUREMENTS: COMPLETE
A6_NOISE: PASS
A6_APPROX_LATENCY: PASS / observed < 0.5 s bidirectionally
A6_OBJECTIVE_LATENCY_DISTRIBUTION: UNVERIFIABLE
A6_PROLONGED_SESSION: PASS
A6_DIRECT_PHONE_AI_PATH: NOT_AVAILABLE
A6_PROVIDER_WRITE: NOT_AUTHORIZED / NOT_PERFORMED
NEXT_GATED_BLOCK: A7
A7_STATUS: NOT_AUTHORIZED
```
