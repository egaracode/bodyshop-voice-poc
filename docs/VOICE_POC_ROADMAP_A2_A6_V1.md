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
    PLANNED / NOT AUTHORIZED

A7  Future BODYSHOP Integration Evaluation
    only if preceding evidence is acceptable
    GATED
```

## 3. A2 and A3

A2 and A3 remain the merged semantic and verification authority for the Voice PoC.

A2 defines the conversational/domain semantics. A3 defines the verification contract and ownership boundaries.

Neither block is reopened by this roadmap reconciliation.

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

A6 is the later laboratory block for real audio/channel validation through the relevant paths and devices:

```text
phone
+
UNIWA F400
+
walkie / Zello
```

A6 owns acoustic/transport concerns such as clipping, overlap, PTT timing, radio compression and repeated real-audio robustness.

A6 is PLANNED and is not authorized by the completion or merge of A5.

## 7. A7 — Future BODYSHOP Integration Evaluation

A7 is a gated future evaluation only.

It may evaluate a future integration path with BODYSHOP PRO only after the isolated Voice PoC has accumulated acceptable semantic, provider-control and audio evidence.

A7 does not authorize Supabase, `AI-Control-Workshop`, production, corporate-network or lifecycle changes.

## 8. Sequencing rule

```text
A2 MERGED
→ A3 MERGED
→ A4 CLOSED / SUPERSEDED / NOT_PASS
→ A5 PROVIDER CONTROL HARNESS MERGED / PHASE 1 COMPLETE
→ A6 REAL VOICE/AUDIO VALIDATION PLANNED / NOT AUTHORIZED
→ A7 FUTURE INTEGRATION EVALUATION GATED
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
Zello API use
phone/SIP integration
F400 runtime changes
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
NEXT_LATER_BLOCK: A6
A6_STATUS: PLANNED / NOT_AUTHORIZED
FUTURE_GATED_BLOCK: A7
```
