# A7 — BODYSHOP Voice Shadow Integration Decision V1

> Status: ARCHITECTURE DECISION / SHADOW-ONLY / NO RUNTIME INTEGRATION

## 1. Purpose

Define the minimum future integration boundary between the isolated `bodyshop-voice-poc` laboratory and canonical BODYSHOP PRO without creating a second breakdown system, duplicating BODYSHOP domain rules or granting Voice authority over lifecycle state.

A7 is a decision block only. It does not implement provider calls, telephony, Zello automation, BODYSHOP code, Supabase or production integration.

## 2. Source and authority hierarchy

This decision was evaluated against, in order:

1. live GitHub state of `egaracode/bodyshop-voice-poc`;
2. live GitHub state and current `main` code/contracts of `egaracode/AI-Control-Workshop`;
3. active BODYSHOP canonical owner documents;
4. current first-party Zello and ElevenLabs documentation;
5. Relevo only as non-authoritative design inspiration.

BODYSHOP domain and lifecycle authority remain in `egaracode/AI-Control-Workshop`.

The Voice PoC owns only voice/channel/provider experimentation and communication semantics.

## 3. Historical-plan contradiction

A previously supplied planning note described:

```text
A5 active
A6 future
A7 gated
```

That sequence is historical.

At the source basis used for this decision:

```text
A5 = merged / provider-control Phase 1 complete / provider result DRIFT
A6 = merged / voice-audio evidence complete with retained limitations
VOICE_COMMUNICATION_WORKFLOW_V1 = merged
A7 = next gated decision block
```

Therefore A7 does not reopen A5 or A6 simply because an older plan still describes them as unfinished.

## 4. Core decision

The integration model is:

```text
VOICE CHANNEL / PROVIDER
        ↓
voice-side observation capture
        ↓
provider/channel-neutral observation
        ↓
BODYSHOP-side validation + domain normalization
        ↓
existing BODYSHOP Blind Shadow
        ↓
AI candidate evidence
        versus
human decision
        ↓
evaluation
```

Explicitly rejected:

```text
Voice PoC
→ direct Supabase RPC
→ authoritative breakdown mutation
```

Also rejected:

```text
Voice PoC
→ second breakdown database
→ parallel lifecycle
```

BODYSHOP remains the only owner of breakdown lifecycle, routing taxonomy, technician eligibility, assignment, pre-close and final close.

## 5. Why the first integration is intake-only

The smallest useful integration is the confirmed operator intake already defined in `VOICE_COMMUNICATION_WORKFLOW_V1`:

```text
operator phone call
→ identity
→ platform
→ installation
→ operation
→ faulty element/device
→ problem description
→ line stopped yes/no
→ full read-back
→ operator confirms
```

Only after that confirmation may a future Voice integration emit an intake observation.

The first integration does **not** include:

- real technician assignment;
- Zello transmit;
- technician arrival state;
- real pre-close;
- final close;
- production restoration;
- support/transfer;
- direct Cloud persistence.

This keeps the first implementation aligned with the existing BODYSHOP routing Shadow capability rather than trying to integrate the whole operational lifecycle at once.

## 6. BODYSHOP capability to reuse

Current BODYSHOP `AI_ROUTING_CONTRACT_V1` already defines the provider-independent routing input:

```text
description
platform
installation
operation
faulty_element
element_type
line_stopped
```

Current `AI_ROUTING_SHADOW_V1` already provides:

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

A7 therefore decides:

> do not build a second Voice-specific routing evaluator, fingerprint system, human-comparison store or lifecycle engine.

The future integration must adapt Voice evidence into the existing BODYSHOP Shadow boundary.

## 7. Minimum Voice observation boundary

A7 defines a conceptual provider/channel-neutral observation. It is intentionally not a shared package or new runtime dependency.

Minimum information needed for future integration:

```text
observation_id
source_channel          phone | zello | simulator
source_reference        provider/channel message reference when available
speaker_role            operator | technician | control | unknown
sender_reference        provider/network identity reference when available
occurred_at
recorded_at
transcript
transcription_confidence | null
language                 | null
candidate_intent
confirmed_breakdown      | null
```

For the first implementation, the only candidate intent required is:

```text
BREAKDOWN_INTAKE_CONFIRMED
```

and `confirmed_breakdown` contains only:

```text
platform
installation
operation
faulty_element
description
line_stopped
```

No BODYSHOP maintenance area, specialty or selected technician is supplied by Voice.

Those values would leak downstream decisions into the Shadow input and remain BODYSHOP-owned.

## 8. Operator identity boundary

The conversational workflow asks the operator for name and surname because this is part of the user interaction and BODYSHOP registration context.

However the existing routing Shadow input does not require operator identity.

Therefore the first routing integration must not add worker identity to `AiRoutingInputV1` merely because Voice captured it.

Public/versioned Voice artifacts continue to use dummy identities only.

Any future private operational persistence of real worker identity requires its own authorized BODYSHOP data/privacy boundary.

## 9. Canonical element type stays in BODYSHOP

Voice captures the faulty element/device as spoken and confirmed by the operator.

Voice does not own BODYSHOP `CatalogElementType` classification.

Current BODYSHOP catalog elements already carry canonical `element_type` metadata.

Therefore the future BODYSHOP-side adapter must:

```text
confirmed platform / installation / operation / element
→ resolve against canonical BODYSHOP catalog
→ obtain canonical element_type
→ construct AiRoutingInputV1
```

If the element cannot be resolved unambiguously:

```text
DO NOT GUESS element_type
DO NOT RUN routing Shadow as if complete
RETURN / RECORD incomplete mapping evidence
```

This preserves BODYSHOP taxonomy ownership and prevents Voice from creating a competing catalog.

## 10. Timing and evidence provenance

BODYSHOP canonical lifecycle distinguishes:

```text
occurred_at
recorded_at
reported_by
recorded_by
evidence_source
evidence_confidence
```

Telephone and delayed reports must preserve the difference between when an event occurred and when it was recorded.

A future Voice observation therefore keeps both `occurred_at` and `recorded_at` available rather than collapsing them into one timestamp.

Voice/provider confidence and BODYSHOP evidence confidence must not be silently treated as the same measurement.

## 11. Transcript confidence is not decision confidence

Current Zello Channel API documentation can expose transcription confidence with `on_transcription`.

That value means confidence in the transcription result.

It must not be interpreted as:

```text
probability that the routing is correct
probability that a pre-close should occur
probability that a lifecycle action is safe
```

The separation is:

```text
channel/STT confidence
→ quality of transcript evidence

BODYSHOP routing result
→ deterministic rule / recommend / abstain / invalid / error

human decision
→ authoritative comparison target in Shadow
```

A high transcription confidence never authorizes a BODYSHOP action.

## 12. ElevenLabs integration position

### 12.1 Post-call webhooks

ElevenLabs documents post-call transcription webhooks that contain conversation/transcript metadata after the call and analysis are complete, with HMAC authentication support.

A7 classifies them as useful for:

```text
post-call audit evidence
conversation trace
provider/version correlation
later evaluation
```

They are not sufficient as the only mechanism for an action that must occur during a live call because they arrive after call completion/analysis.

### 12.2 Webhook tools

ElevenLabs documents webhook tools for calling external APIs during a conversation.

If a future block uses this capability, the target must be a bounded Voice/Shadow adapter endpoint.

It must not directly call:

```text
BODYSHOP lifecycle mutation RPC
Supabase privileged endpoint
pre-close endpoint
final-close endpoint
technician-assignment endpoint
```

This keeps the provider replaceable and BODYSHOP authoritative.

## 13. Zello integration position

Current official Zello Channel API documentation supports channel voice send/receive and, where the network supports it and `features.transcriptions = true`, `on_transcription` events containing:

```text
stream_id
sender
text
confidence
language
```

This makes native Zello transcription a reasonable future first option before adding another STT provider.

A7 does not claim its workshop accuracy is adequate. Accuracy for noise, accents and workshop vocabulary must be measured with BODYSHOP dummy language before adoption.

If inadequate, another STT provider may later sit behind the same observation boundary without changing BODYSHOP semantics.

## 14. Zello human-priority constraint

Current Zello Work documentation defines talk priority:

```text
High   → interrupts Normal and Low
Normal → interrupts Low
Low    → cannot interrupt
```

If a later laboratory block uses Zello Work transmit, a reasonable test configuration is:

```text
AI Control      LOW
technician      NORMAL
human Control   HIGH, where the laboratory role model supports it
```

This is a test hypothesis, not a production policy.

It must be physically validated because provider documentation describes configured priority behavior but does not prove the exact future BODYSHOP channel/runtime configuration.

A7 itself performs no Zello configuration or transmission.

## 15. Relevo lessons adopted conceptually

Relevo provides useful design inspiration for:

- a channel-adapter boundary;
- separating transcript from semantic interpretation;
- keeping humans dominant on a PTT channel;
- traceability from source utterance to interpretation and emitted communication;
- not inferring speaker identity from voice biometrics when the channel already exposes sender identity.

These ideas are not imported as code.

At the time of review, the Relevo repository root did not show a visible `LICENSE` file.

Therefore:

```text
NO CODE COPY
NO TEXTUAL IMPLEMENTATION COPY
CONCEPTUAL INSPIRATION ONLY
```

Any adopted behavior must independently satisfy BODYSHOP contracts and current official provider documentation.

## 16. Traceability model

Future evidence should be able to answer:

```text
who/source spoke?
what transcript was produced?
what was operator-confirmed?
what BODYSHOP mapping was possible?
what input fingerprint was evaluated?
what candidate routing resulted?
what human decision was later attached?
where did they agree/disagree?
```

The minimum trace chain is:

```text
voice observation id
→ source/provider reference
→ transcript
→ confirmed intake
→ BODYSHOP Shadow input fingerprint
→ candidate routing evidence
→ human decision
→ comparison
```

Do not add a second permanent event store in Voice merely to duplicate BODYSHOP evidence.

## 17. Technician resolution messages

The merged Voice communication contract defines technician phrases such as:

```text
"Avería solucionada"
"Puedes cerrar la avería"
"La avería está solucionada"
```

These remain semantically useful as a future:

```text
REQUEST_PRE_CLOSE_CANDIDATE
```

But A7 decides that they are **not part of the first integration implementation**.

Reason: BODYSHOP lifecycle authority for normal pre-close is already explicit and safety-sensitive:

```text
current owner technician reports physical resolution
→ active Control/Admin may record pre-close
→ technician later documents solution and performs final close
```

A future technician-voice integration must preserve actor authentication/identity, ownership, lifecycle state, timing, equipment-condition evidence and Control/Admin authority. It requires its own bounded block.

## 18. Provider DRIFT classification

A5 demonstrated that the effective ElevenLabs sandbox configuration differs from the GitHub-owned expected configuration.

A7 classifies this as follows:

```text
A7 architecture decision                     NOT BLOCKED
provider-neutral adapter contract/tests       NOT BLOCKED
claim of aligned ElevenLabs behavior          BLOCKED BY DRIFT
real ElevenLabs end-to-end acceptance         REQUIRES drift resolution or an explicit new expected-state decision
```

The drift is real evidence and must not be ignored.

It also must not be turned into an artificial blocker for provider-independent architecture work.

## 19. Missing real transport paths

A6 established:

```text
DIRECT_PHONE_AI_PATH: NOT_AVAILABLE
FULL_AI_CONTROL_TO_F400_PATH: NOT_AVAILABLE
```

A7 classifies these as:

```text
architecture decision                         NOT BLOCKED
pure BODYSHOP-side Shadow adapter             NOT BLOCKED
real phone → BODYSHOP runtime proof            BLOCKED until transport exists
full phone → AI → Zello/F400 visible E2E       BLOCKED until both transport directions exist
```

Do not claim an end-to-end product path before those transports exist and are tested.

## 20. Single next implementation goal

A7 selects exactly one next implementation goal:

# BODYSHOP Voice Shadow Intake Adapter V1

Repository owner:

```text
egaracode/AI-Control-Workshop
```

Reason: BODYSHOP owns the routing contract, canonical element taxonomy and Blind Shadow implementation.

The next goal should implement and test a **pure provider-neutral inbound adapter** that accepts one confirmed Voice intake fixture/observation and:

```text
validate required fields
→ resolve canonical BODYSHOP element/catalog type
→ construct AiRoutingInputV1
→ capture existing RoutingShadow input/fingerprint
→ return Shadow-ready evidence
```

It must not:

```text
call ElevenLabs
call Zello
call Supabase
create a real breakdown
assign a real technician
pre-close
final-close
write Production
```

This is the shortest path that proves the cross-domain contract without introducing external runtime complexity.

## 21. What comes after that goal

Not authorized by A7, and intentionally not pre-expanded into a nested roadmap.

Later work will be chosen from evidence after the adapter exists.

Potential future domains include:

```text
real ElevenLabs/phone emitter
Zello receive adapter
Zello transmit/delivery/priority validation
technician resolution observation
visible dummy end-to-end Shadow evaluation
```

None is a prerequisite to complete A7 itself.

## 22. Official external sources consulted

Consulted: 2026-09-16.

### Zello Channel API specification

Publisher/owner: Zello official GitHub organization

Reference:
https://github.com/zelloptt/zello-channel-api/blob/main/API.md

Engineering consequence:

- secure WebSocket Channel API;
- channel stream identifiers/sender metadata;
- optional `features.transcriptions`;
- `on_transcription` with transcript/confidence/language where supported.

### Talk priority

Publisher: Zello Work

Reference:
https://support.zello.com/zw/talk-priority

Engineering consequence:

- High interrupts Normal/Low;
- Normal interrupts Low;
- Low cannot interrupt;
- future human-priority assumptions must be runtime tested.

### Post-call webhooks

Publisher: ElevenLabs

Reference:
https://elevenlabs.io/docs/eleven-agents/workflows/post-call-webhooks

Engineering consequence:

- post-call transcription evidence is available after call analysis;
- payload includes conversation metadata/transcript information;
- webhook authenticity can be verified using HMAC signatures.

### Webhook tools

Publisher: ElevenLabs

Reference:
https://elevenlabs.io/docs/eleven-agents/customization/tools/webhook-tools

Engineering consequence:

- an agent can call an external API during a conversation;
- A7 keeps such calls behind a Voice/Shadow boundary rather than exposing authoritative BODYSHOP mutations directly to the provider.

## 23. BODYSHOP primary repository evidence consulted

Source basis at decision time:

```text
AI-Control-Workshop main:
cae706403d4ffc03fb7118205d355508c3850db4
```

Principal files:

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

This SHA is recorded as historical decision provenance. Future implementation must revalidate live `main` and current owners before acting.

## 24. Explicit exclusions

A7 does not authorize or implement:

```text
AI-Control-Workshop modification
Supabase / SQL / migrations / RLS / RPC / Auth
BODYSHOP Cloud mutation
real breakdown creation
real assignment
real pre-close
real final close
ElevenLabs write / Publish / provider mutation
phone/SIP provisioning
Zello API runtime integration
Zello Work role/priority changes
F400 software/runtime modification
Production
corporate network integration
secrets/.env
new dependencies
CI/workflow changes
```

## 25. Acceptance result

A7 is complete as a decision when the following are true:

```text
ONE integration boundary defined
BODYSHOP remains sole domain authority
NO second breakdown system
NO direct Voice → Supabase lifecycle mutation
existing routing Shadow reused
transcription confidence separated from semantic authority
provider DRIFT correctly classified
missing transport paths correctly classified
one next implementation goal selected
current official-source basis recorded
```

## 26. Stop point

```text
A7_BODYSHOP_VOICE_INTEGRATION_DECISION_V1: DOCUMENTED
NEXT_IMPLEMENTATION_GOAL: BODYSHOP Voice Shadow Intake Adapter V1
NEXT_IMPLEMENTATION: NOT AUTHORIZED BY THIS DOCUMENT
```

Albert retains Ready, merge and authorization of the next implementation goal.

No BODYSHOP canonical-state update required by this documentation-only Voice-lab decision.