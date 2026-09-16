# A7 — BODYSHOP Voice Shadow Integration Decision V1

> Status: VOICE-LAB INTEGRATION DECISION / SHADOW-ONLY / NO RUNTIME INTEGRATION

## 1. Purpose and authority

Define the minimum boundary that `bodyshop-voice-poc` must respect in any future connection to canonical BODYSHOP PRO.

This document is authoritative only for the Voice PoC side. It does **not** create or modify a canonical BODYSHOP architecture decision. Any future change in `egaracode/AI-Control-Workshop` requires that repository's own bootstrap, Issue, authorization, branch, tests, CI and Albert decision.

Canonical BODYSHOP domain and lifecycle authority remains in `egaracode/AI-Control-Workshop`.

A7 implements nothing. No provider, telephony, Zello, BODYSHOP, Supabase or Production runtime is changed.

## 2. Current source basis

Consulted on 2026-09-16.

Voice repository at decision time:

```text
egaracode/bodyshop-voice-poc
main = 30283d29686695e939748e6a71d7442f6f837055
```

Canonical BODYSHOP repository at decision time:

```text
egaracode/AI-Control-Workshop
main = cae706403d4ffc03fb7118205d355508c3850db4
```

BODYSHOP evidence reviewed:

```text
.ai/00_AGENT_INDEX.md
.ai/00_EXECUTION_DISCIPLINE.md
.ai/01_PROJECT_CONTEXT.md
.ai/CURRENT_STATE.md
docs/00_PROJECT_CANONICAL_STATE.md
docs/ARCHITECTURE/CANONICAL_DECISION_INDEX.md
docs/DATA_CONTRACTS/BREAKDOWN_LIFECYCLE_ACTOR_MATRIX_V1.md
src/ai/routingContract.ts
src/ai/routingShadow.ts
src/types.ts
```

The recorded SHAs are historical provenance for this decision. Future implementation must revalidate live `main` and current owners.

## 3. Historical-plan contradiction

A supplied earlier analysis still described A5 as active and A6 as planned.

Live GitHub supersedes that history:

```text
A5 = MERGED / provider-control Phase 1 complete / provider result DRIFT
A6 = MERGED / evidence complete with retained limitations
VOICE_COMMUNICATION_WORKFLOW_V1 = MERGED
A7 = current decision block
```

A7 does not reopen A5 or A6.

## 4. Minimal integration decision

The Voice PoC boundary is:

```text
phone / ElevenLabs / Zello / simulator
        ↓
Voice-side channel/provider adapter
        ↓
provider-neutral Voice observation
        ↓
BODYSHOP boundary
```

From that boundary onward, BODYSHOP must retain ownership of validation, catalog/taxonomy resolution, routing, Shadow evaluation and lifecycle semantics.

The intended future shape, subject to separate acceptance inside canonical BODYSHOP, is:

```text
Voice observation
        ↓
BODYSHOP-side validation + domain normalization
        ↓
existing BODYSHOP Blind Shadow
        ↓
AI candidate evidence
        vs
human decision
        ↓
evaluation
```

Explicitly rejected on the Voice side:

```text
Voice → direct Supabase/RPC lifecycle mutation
Voice → second breakdown database
Voice → parallel lifecycle
Voice → authoritative technician assignment
Voice → authoritative pre-close/final-close
```

## 5. First integration should be intake-only

The smallest useful future handoff is the already approved operator intake:

```text
operator phone call
→ identity
→ platform
→ installation
→ operation
→ faulty element/device
→ problem description
→ line stopped yes/no
→ complete read-back
→ operator confirms
```

Only after operator confirmation may Voice emit a confirmed-intake observation.

The first implementation candidate must not include:

```text
real technician assignment
Zello transmit
delivery acknowledgement
technician arrival/intervention state
real pre-close
final close
production restoration
support/transfer
Cloud persistence
```

## 6. BODYSHOP capability available for reuse

Current BODYSHOP `AI_ROUTING_CONTRACT_V1` already owns this routing input:

```text
description
platform
installation
operation
faulty_element
element_type
line_stopped
```

Current `AI_ROUTING_SHADOW_V1` already owns:

```text
input snapshot
input fingerprint
capture time
human decision attached later
providerInvoked
DETERMINISTIC_RESOLVED
AI_RECOMMEND
AI_ABSTAIN
AI_INVALID
AI_ERROR
SHADOW_EXCLUDED
SHADOW_INVALID_INPUT
DRY_RUN_NOT_EXECUTED
```

Therefore Voice must not build its own competing routing evaluator, fingerprint model, human-comparison lifecycle or breakdown store.

Whether and how canonical BODYSHOP exposes an adapter to these existing capabilities is a later BODYSHOP-owned decision.

## 7. Minimal provider-neutral Voice observation

A7 defines a conceptual transport object, not a shared package or dependency:

```text
observation_id
source_channel           phone | zello | simulator
source_reference         provider/channel reference when available
speaker_role             operator | technician | control | unknown
sender_reference         network/provider identity when available
occurred_at
recorded_at
transcript
transcription_confidence | null
language                 | null
candidate_intent
confirmed_breakdown      | null
```

For the first integration candidate, only this intent is required:

```text
BREAKDOWN_INTAKE_CONFIRMED
```

and `confirmed_breakdown` contains:

```text
platform
installation
operation
faulty_element
description
line_stopped
```

Voice does **not** provide BODYSHOP maintenance area, specialty, selected technician or canonical `element_type`.

## 8. Catalog and element-type ownership

Voice captures the element/device exactly as understood and confirmed with the operator.

BODYSHOP currently owns canonical `CatalogElementType` and catalog metadata. A future BODYSHOP-side adapter should therefore resolve:

```text
platform + installation + operation + confirmed element
→ canonical catalog element
→ canonical element_type
→ AiRoutingInputV1
```

If the element cannot be resolved unambiguously:

```text
DO NOT GUESS element_type
DO NOT EVALUATE AS COMPLETE ROUTING INPUT
```

This prevents Voice from creating a competing workshop taxonomy.

## 9. Identity and timing boundary

The Voice workflow asks the operator for name and surname, but current BODYSHOP routing Shadow does not require operator identity.

Do not add worker identity to `AiRoutingInputV1` merely because Voice captured it. Public/versioned Voice evidence continues to use dummy identities only.

BODYSHOP canonical lifecycle also distinguishes event occurrence from system recording, including telephone/delayed reports. The conceptual observation therefore preserves:

```text
occurred_at
recorded_at
```

Any future private persistence of real worker identity or additional evidence fields requires a separately authorized BODYSHOP data/privacy boundary.

## 10. Transcript confidence is not decision confidence

Zello's official Channel API documents optional transcription events containing transcription confidence.

That value is evidence about transcription accuracy. It is **not**:

```text
routing confidence
pre-close confidence
safety confidence
permission to mutate BODYSHOP
```

Keep the layers separate:

```text
STT/channel confidence
→ transcript quality

BODYSHOP routing
→ deterministic / recommend / abstain / invalid / error

human decision
→ authoritative Shadow comparison target
```

## 11. ElevenLabs position

ElevenLabs official documentation supports two relevant future mechanisms:

### Post-call transcription webhooks

They arrive after the call has ended and analysis is complete, can contain transcript/conversation metadata and support HMAC signature validation.

Use case for BODYSHOP Voice:

```text
post-call audit/evidence
provider/version correlation
later evaluation
```

They must not be treated as the sole mechanism for a fact that needs to be handed off during a live call.

### Webhook tools

ElevenLabs agents can call external APIs during a conversation.

If used later, the destination should be a bounded Voice/Shadow endpoint. Voice must not expose authoritative BODYSHOP lifecycle mutation endpoints directly to the provider.

## 12. Zello position

The official Zello Channel API documents `features.transcriptions = true` and `on_transcription` events, when supported by the network, including:

```text
stream_id
sender
text
confidence
language
```

Therefore native Zello transcription is a reasonable **future test candidate** before adding another STT provider.

This document does not claim it is accurate enough for workshop noise, accents or vocabulary. That must be measured with dummy BODYSHOP language before adoption.

Zello Work also documents talk priorities:

```text
High   → interrupts Normal and Low
Normal → interrupts Low
Low    → cannot interrupt
```

A future lab may test AI at Low priority and humans above it, but this is a hypothesis for physical validation, not a Production policy and not an A7 implementation task.

## 13. Relevo lessons used only as design inspiration

Reviewed repository:

```text
https://github.com/Axerra1/relevo
```

Useful ideas:

- channel-adapter boundary;
- transcript separated from semantic interpretation;
- humans retain PTT priority;
- trace source utterance → interpretation → output → human response;
- use network sender identity instead of voice biometrics when the channel already provides identity.

The reviewed repository root showed no visible `LICENSE` file. Therefore:

```text
NO CODE COPY
NO IMPLEMENTATION-TEXT COPY
CONCEPTUAL INSPIRATION ONLY
```

Every adopted concept must still be independently supported by BODYSHOP contracts and/or official provider documentation.

## 14. Traceability target

A future integration should be able to correlate:

```text
Voice observation id
→ source/provider reference
→ transcript
→ confirmed intake
→ BODYSHOP Shadow input fingerprint
→ candidate routing evidence
→ later human decision
→ comparison
```

Voice must not create a second permanent event store merely to duplicate BODYSHOP evidence.

## 15. Technician-resolution voice is later scope

The merged Voice communication contract recognizes phrases such as:

```text
"Avería solucionada"
"Puedes cerrar la avería"
```

They may later map to a non-authoritative candidate intent such as:

```text
REQUEST_PRE_CLOSE_CANDIDATE
```

They are deliberately **not** part of the first integration candidate.

Current canonical BODYSHOP requires the current owner Technician to report physical resolution and active Control/Admin to perform normal pre-close; final technical close remains a later Technician action. A future voice path must preserve identity, current ownership, lifecycle state, timing, equipment-condition evidence and actor authority.

## 16. Provider DRIFT and missing transports

A5 provider result remains:

```text
DRIFT
```

Classification:

```text
A7 Voice-side architecture decision              NOT BLOCKED
provider-neutral contract/test work              NOT BLOCKED
claim of aligned ElevenLabs behavior             BLOCKED BY DRIFT
real ElevenLabs end-to-end acceptance            requires drift resolution or explicit new expected-state decision
```

A6 also established:

```text
DIRECT_PHONE_AI_PATH: NOT_AVAILABLE
FULL_AI_CONTROL_TO_F400_PATH: NOT_AVAILABLE
```

Classification:

```text
architecture/contract decision                   NOT BLOCKED
pure provider-neutral adapter work               NOT BLOCKED
real phone → BODYSHOP runtime proof               blocked until transport exists
full phone → AI → Zello/F400 visible proof        blocked until required transports exist
```

These are real limitations, but they are not reasons to add transport complexity before the provider-neutral boundary is proven.

## 17. Next implementation candidate

A7 identifies one candidate only:

# BODYSHOP Voice Shadow Intake Adapter V1

Candidate repository:

```text
egaracode/AI-Control-Workshop
```

Proposed responsibility:

```text
confirmed Voice intake fixture/observation
→ validate fields
→ resolve canonical BODYSHOP element/type
→ construct AiRoutingInputV1
→ use existing RoutingShadow capture/fingerprint
→ return Shadow-ready evidence
```

Prohibited in that candidate unless a future BODYSHOP Issue explicitly says otherwise:

```text
ElevenLabs calls
Zello calls
Supabase calls
real breakdown creation
real technician assignment
pre-close
final-close
Production mutation
```

This is a **candidate**, not authorization and not a canonical BODYSHOP decision. Before any implementation, `AI-Control-Workshop` must independently revalidate its current `main`, owners, open work and governance and Albert must authorize the BODYSHOP Issue.

A7 intentionally does not create a nested roadmap beyond this one candidate.

## 18. Official external sources consulted

Consulted: 2026-09-16.

### Zello Channel API specification

Publisher: Zello official GitHub organization

Reference:
https://github.com/zelloptt/zello-channel-api/blob/main/API.md

Supports:

- Channel API stream/sender metadata;
- optional `features.transcriptions`;
- `on_transcription` with `stream_id`, sender, transcript text, confidence and language when supported.

### Zello Work — Talk priority

Publisher: Zello

Reference:
https://support.zello.com/zw/talk-priority

Supports:

- High interrupts Normal/Low;
- Normal interrupts Low;
- Low cannot interrupt;
- same-priority timeout rules and emergency behavior remain provider-defined.

### ElevenLabs — Post-call webhooks

Publisher: ElevenLabs

Reference:
https://elevenlabs.io/docs/eleven-agents/workflows/post-call-webhooks

Supports:

- post-call transcription data after call analysis;
- transcript and conversation metadata;
- HMAC webhook verification.

### ElevenLabs — Webhook tools

Publisher: ElevenLabs

Reference:
https://elevenlabs.io/docs/eleven-agents/customization/tools/webhook-tools

Supports:

- agent calls to external REST APIs during a conversation.

## 19. Explicit exclusions

A7 does not authorize or implement:

```text
AI-Control-Workshop modification
Supabase / SQL / migrations / RLS / RPC / Auth
BODYSHOP lifecycle mutation
real breakdown creation
real technician assignment
real pre-close or final close
ElevenLabs write / Publish / configuration mutation
phone/SIP provisioning
Zello API runtime integration
Zello Work priority/role changes
F400 software/runtime modification
Production
corporate network integration
secrets/.env
new dependencies
CI/workflow changes
```

## 20. Acceptance result

A7 is complete as a Voice-lab decision when:

```text
ONE minimal boundary is documented
BODYSHOP authority is preserved
NO second breakdown system is introduced
NO direct Voice → Supabase lifecycle mutation is proposed
existing BODYSHOP routing Shadow is the reuse target
transcription confidence is separated from semantic authority
provider DRIFT is correctly classified
missing transports are correctly classified
ONE next implementation candidate is identified
current official-source basis is recorded
```

## 21. Stop point

```text
A7_BODYSHOP_VOICE_INTEGRATION_DECISION_V1: DOCUMENTED
NEXT_IMPLEMENTATION_CANDIDATE: BODYSHOP Voice Shadow Intake Adapter V1
NEXT_IMPLEMENTATION: NOT AUTHORIZED
```

Albert retains Ready, merge and authorization of any future BODYSHOP implementation.

No BODYSHOP canonical-state update required by this documentation-only Voice-lab decision.
