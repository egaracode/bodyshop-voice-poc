# BODYSHOP Voice PoC Roadmap — A2 to A6 V1

## 1. Purpose

This document records the agreed functional sequence for the isolated `egaracode/bodyshop-voice-poc` laboratory after completion of the A2 conversational foundation and merge of the A3 conversational verification/test contract.

It is a roadmap and sequencing contract only. It does not by itself authorize implementation of A4, A5 or A6.

## 2. Agreed sequence

```text
A2  Conversational Foundation
     ✅ MERGED

A3  Conversational Verification
    + ElevenLabs Test Contract
     ✅ MERGED

A4  ElevenLabs Sandbox Agent
     ← NEXT

A5  Voice / audio validation
    phone + F400 + walkie/Zello
    PLANNED

A6  Future integration evaluation
    with BODYSHOP PRO
    only if the previous blocks pass
    GATED
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
MERGED
```

A3 converted the A2 conversational behavior into an explicit PASS/FAIL verification contract and mapped each verification concern to the appropriate owning layer, including ElevenLabs-native testing, adapter-required checks, hybrid verification, BODYSHOP domain assertions and A5 real-audio validation.

A3 was merged through PR #9.

`A3 MERGED` means the verification/test contract is versioned in `main`. It does **not** mean ElevenLabs runtime tests have already been executed.

The A3 contract explicitly preserves:

```text
RUNTIME_TEST_EXECUTION: NOT_STARTED
ELEVENLABS_AGENT: NOT_CREATED_BY_A3
```

### A4 — ElevenLabs Sandbox Agent

Status:

```text
NEXT
```

A4 is the next functional block.

A4 is the first block intended to create/configure a real ElevenLabs agent in a sandbox context and to execute the provider-compatible verification path defined by A3 where authorized.

It must remain isolated from BODYSHOP PRO production/runtime and from any real operational action.

A4 requires its own Issue, branch, validation and PR. This roadmap synchronization does not authorize A4 implementation by itself.

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
→ A3 CONTRACT MERGED
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

No canonical-state update is required by this documentation-only roadmap synchronization.

## 7. Current roadmap position

```text
COMPLETED: A2 Conversational Foundation
COMPLETED: A3 Conversational Verification + ElevenLabs Test Contract
NEXT:      A4 ElevenLabs Sandbox Agent
LATER:     A5 → A6
```

## 8. Stop point

```text
ROADMAP_SYNCED_AFTER_A3
A4_IMPLEMENTATION_NOT_STARTED
```
