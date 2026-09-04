# BODYSHOP Voice PoC Roadmap — A2 to A6 V1

## 1. Purpose

This document records the agreed functional sequence for the isolated `egaracode/bodyshop-voice-poc` laboratory after completion of A2.

It is a roadmap and sequencing contract only. It does not by itself authorize implementation of A3, A4, A5 or A6.

## 2. Agreed sequence

```text
A2  Conversational Foundation
     ✅ MERGED

A3  Conversational Verification
    + ElevenLabs Test Contract
     ← NEXT

A4  ElevenLabs Sandbox Agent
    real configuration, still isolated

A5  Voice / audio validation
    phone + F400 + walkie/Zello

A6  Future integration evaluation
    with BODYSHOP PRO
    only if the previous blocks pass
```

## 3. Block status and intent

### A2 — Conversational Foundation

Status:

```text
MERGED
```

A2 established the minimum conversational foundation for the PoC, including guided conversation, phone vs shared-walkie activation, non-intervention behavior, contextual intent interpretation, technician pre-close semantics, ambiguity handling, selective confirmation, bounded recovery and the ElevenLabs provider boundary.

A2 is complete and is not reopened by this roadmap.

### A3 — Conversational Verification + ElevenLabs Test Contract

Status:

```text
NEXT
```

A3 is the next functional block.

Its purpose is to define how the A2 conversational behavior will be verified through explicit PASS/FAIL scenarios and how those scenarios map to ElevenLabs testing capabilities where appropriate.

A3 remains a separate block and requires its own Issue, branch, validation and PR.

### A4 — ElevenLabs Sandbox Agent

Status:

```text
PLANNED
```

A4 is the first block intended to create/configure a real ElevenLabs agent in a sandbox context.

It must remain isolated from BODYSHOP PRO production/runtime and from any real operational action.

A4 does not begin through this roadmap document.

### A5 — Voice / Audio Validation

Status:

```text
PLANNED
```

A5 is intended to validate the voice/audio behavior through the relevant laboratory channels and devices:

```text
phone
+
F400
+
walkie / Zello
```

This block is where real audio/channel behavior can be evaluated separately from purely semantic or textual conversational verification.

A5 does not begin through this roadmap document.

### A6 — Future Integration Evaluation with BODYSHOP PRO

Status:

```text
GATED FUTURE EVALUATION
```

A6 is not an implementation authorization.

Its purpose is to evaluate whether the isolated Voice PoC has produced enough verified evidence to consider a future integration path with BODYSHOP PRO.

A6 may only be considered if the preceding blocks have produced acceptable evidence and passed their own acceptance criteria.

## 4. Sequencing rule

The intended progression is:

```text
A2 MERGED
→ A3 VERIFIED
→ A4 SANDBOX
→ A5 REAL VOICE/AUDIO VALIDATION
→ A6 INTEGRATION EVALUATION
```

Each block remains independently governed by the repository working method:

```text
one objective
→ one Issue
→ one branch
→ one PR
→ validation
→ Albert Ready decision
→ manual merge
```

No later block is implicitly authorized merely because it appears in this roadmap.

## 5. Repository and safety boundary

This roadmap does not authorize:

```text
ElevenLabs API/runtime use
Zello API use
phone integration
F400 runtime changes
Supabase
AI-Control-Workshop changes
production use
corporate-network use
dependencies
CI/workflow changes
automation with real operational impact
```

Any such work requires a separately authorized functional block.

## 6. Canonical relationship

`egaracode/bodyshop-voice-poc` remains an isolated parallel laboratory.

`egaracode/AI-Control-Workshop` remains the canonical BODYSHOP PRO repository and is not modified by this roadmap.

No canonical-state update is required by this documentation-only roadmap.

## 7. Current roadmap position

```text
CURRENT: A2 MERGED
NEXT:    A3 Conversational Verification + ElevenLabs Test Contract
LATER:   A4 → A5 → A6
```

## 8. Stop point

```text
ROADMAP_DOCUMENTED
A3_IMPLEMENTATION_NOT_STARTED
```
