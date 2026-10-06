> **CURRENT AUTHORITY NOTICE — 2026-10-06**
>
> This document is preserved as **HISTORICAL / PROVENANCE** evidence and is **SUPERSEDED AS CURRENT PRODUCT/PROVIDER AUTHORITY**.
>
> Current BODYSHOP Voice product authority lives in `egaracode/AI-Control-Workshop`, including `docs/DATA_CONTRACTS/VOICE_OPERATOR_INTAKE_CONTRACT_V1.md` and its MASTER-owned executable/provider-derivation tooling.
>
> The historical body below is intentionally preserved unchanged. Any words such as `current`, `authority`, `accepted target`, `next candidate` or Gate status must be read in the delivery context recorded by this document. Revalidate live GitHub and current first-party provider documentation before reuse.
>
> Repository classification: see `docs/VOICE_AUTHORITY_STATUS_V1.md`.

# A7 — BODYSHOP Voice Shadow Integration Decision V1

> Status: VOICE-LAB INTEGRATION DECISION / SHADOW-ONLY / NO RUNTIME INTEGRATION

## 1. Purpose and authority

Define the minimum boundary that `bodyshop-voice-poc` must respect in any future connection to canonical BODYSHOP PRO.

This document is authoritative only for the Voice PoC side. It does **not** create or modify a canonical BODYSHOP architecture decision. Any future change in `egaracode/AI-Control-Workshop` requires that repository's own bootstrap, Issue, authorization, branch, tests, CI and Albert decision.

Canonical BODYSHOP domain, catalog and lifecycle authority remains in `egaracode/AI-Control-Workshop`.

A7 implements nothing. No provider, telephony, Zello, BODYSHOP, Supabase or Production runtime is changed.


## 2. Current source basis

Revalidated on 2026-10-01.

Voice repository:

```text
egaracode/bodyshop-voice-poc
main = 30283d29686695e939748e6a71d7442f6f837055
A7 Issue = #24 OPEN
A7 PR = #25 OPEN / DRAFT
```

Canonical BODYSHOP repository:

```text
egaracode/AI-Control-Workshop
main = b232ad437888f0ee305a3393daf9a16553264179
Reference Object Catalog V1 = completed and durably synchronized
```

BODYSHOP evidence revalidated:

```text
.ai/00_AGENT_INDEX.md
.ai/00_EXECUTION_DISCIPLINE.md
.ai/CURRENT_STATE.md
docs/00_PROJECT_CANONICAL_STATE.md
docs/ARCHITECTURE/CANONICAL_DECISION_INDEX.md
docs/DATA_CONTRACTS/REFERENCE_OBJECT_CATALOG_CONTRACT_V1.md
docs/DATA_CONTRACTS/BREAKDOWN_LIFECYCLE_ACTOR_MATRIX_V1.md
src/services/referenceObjectCatalog.ts
src/ai/routingContract.ts
src/ai/routingShadow.ts
```

The canonical catalog now supersedes the earlier A7 design hypothesis that BODYSHOP still needed a flat `CatalogElement` extension. That historical hypothesis must not be treated as current architecture.

Additional supporting evidence:

- user-supplied internal maintenance-workflow evidence, reviewed read-only and not committed;
- SAP Maintenance Management documentation previously used as supporting technical-object hierarchy context;
- current first-party Zello and ElevenLabs documentation revalidated on 2026-10-01 and listed below.

The recorded SHAs are provenance for this A7 decision. Any later implementation must revalidate current GitHub and provider documentation again.

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

## 4. Reference-object finding from the maintenance workflow

The reviewed maintenance workflow establishes a material product rule that the initial A7 draft did not make explicit.

A breakdown is associated with an existing hierarchical reference object. The relevant structure is conceptually:

```text
technical location / workshop scope
→ model
→ installation
→ operation
→ element/device
→ child element/subdevice when applicable
→ responsible / priority
→ save
```

BODYSHOP does not need to copy SAP naming or codes, but it must preserve this invariant:

> A breakdown cannot be registered against a model, installation, operation, device or subdevice that does not exist in the active BODYSHOP reference catalog.

Free text remains valid for the symptom/description. Free text is **not** a substitute for the reference-object hierarchy.


## 5. Canonical BODYSHOP catalog capability now available

The prerequisite identified by the earlier A7 draft has now been completed in canonical BODYSHOP PRO.

Current canonical hierarchy:

```text
Taller
→ Modelo
→ Instalación
→ Operación
→ Dispositivo
→ Subdispositivo when applicable
```

BODYSHOP no longer represents the target merely as a flat display label. The canonical catalog separates:

```text
CatalogUnit
→ stable physical unit identity

CatalogUnitPlacement
→ time-bounded placement/context

CatalogReferencePath
→ selectable canonical path identity
```

A selectable `CatalogReferencePath` has:

```text
referencePathId
grain = DEVICE | DEVICE_SUBDEVICE
active
devicePlacementId
subdevicePlacementId | null
```

The canonical reference path is therefore the identity that a future Voice integration must ultimately resolve, rather than constructing an identity from concatenated spoken labels.

## 6. Accepted synthetic catalog shape

The earlier A7 target of:

```text
3 models
× 5 installations/model
× 10 operations/installation
= 150 operation nodes
```

was a planning hypothesis before the canonical BODYSHOP vertical was executed. It is now superseded by the accepted BODYSHOP contract.

Current accepted synthetic foundation includes:

```text
3 workshops
3 canonical models: A01 / A02 / A03
5 workshop-model associations
18 contextual installations
5 reusable operation definitions
90 installation-operation contexts
operation-specific device/subdevice units and placements
canonical DEVICE and DEVICE_SUBDEVICE reference paths
```

The operation definitions are reusable functional families:

```text
WELDING
FIXTURE
ADHESIVE
ELEVATION
MANIPULATION
```

Contextual operation codes remain installation-specific, for example OP100/OP200/... on Laterales and corresponding suffix variants on the other installation contexts.

A7 does not redefine these counts, codes, compositions or taxonomies. BODYSHOP owns them.

## 7. Reference-path authority

The future Voice integration must treat `referencePathId` as BODYSHOP-owned authority.

Voice may provide observations and aliases, but it must not mint, guess or concatenate its own canonical path identifier.

Conceptually:

```text
spoken/display values
→ resolve against BODYSHOP catalog
→ exactly one active selectable CatalogReferencePath
→ referencePathId
```

Possible canonical grains:

```text
DEVICE
DEVICE_SUBDEVICE
```

A device-only report remains valid only when BODYSHOP exposes that device path as selectable. A missing subdevice must never be fabricated merely to force DEVICE_SUBDEVICE grain.

## 8. Workshop scope is part of resolution

The canonical hierarchy begins at `Taller`, not at `Modelo`.

Therefore a future Voice session needs a trusted workshop scope before a canonical path can be resolved.

That scope may come from a deployment/session configuration when the Voice entry point is intentionally bound to one workshop. If no trusted workshop scope exists, Voice must obtain or clarify it.

Not allowed:

```text
same spoken model/installation appears in multiple workshop contexts
→ Voice silently picks one
```

Allowed:

```text
trusted workshop scope
+ confirmed model/installation/operation/device/subdevice
→ canonical resolution
```

## 9. Registration validity gate

The canonical BODYSHOP catalog already implements fail-closed path selectability.

For Voice integration, the rule is:

```text
exactly one active selectable reference path
= reference-valid candidate

zero matching paths
= NOT_FOUND / clarification required

multiple matching paths
= AMBIGUOUS / clarification required

incomplete required context
= INCOMPLETE / clarification required
```

Until one canonical selectable path is resolved:

```text
NO authoritative breakdown registration
NO invented catalog object
NO silent fallback to free text
NO guessed referencePathId
NO guessed canonical element type
```

The symptom/description remains free text and is separate from reference identity.

## 10. Voice alias rule

Voice may hear workshop synonyms, abbreviations or pronunciation variants, but language understanding does not grant catalog authority.

Allowed:

```text
spoken alias
→ match existing catalog candidates
→ one unique active selectable path after required context
→ canonical referencePathId
```

Not allowed:

```text
unknown term
→ create a new device
```

or:

```text
ambiguous alias
→ silently choose one path
```

A future language/alias library may improve matching. It remains a resolver aid only; it never becomes reference-object authority.


## 11. Minimal Voice integration decision

The minimal future boundary is now:

```text
phone / ElevenLabs / Zello / simulator
        ↓
Voice-side channel/provider adapter
        ↓
provider-neutral Voice observation
        ↓
BODYSHOP-side reference resolver
        ↓
existing active CatalogReferencePath
        ↓
referencePathId
        ↓
BODYSHOP routing-input mapping
        ↓
existing AI_ROUTING_SHADOW_V1
```

BODYSHOP retains ownership of:

```text
catalog validity
referencePathId
canonical hierarchy
canonical element/device type
routing taxonomy
Shadow evaluation
technician eligibility
lifecycle semantics
persistence
```

Explicitly rejected on the Voice side:

```text
Voice → direct Supabase/RPC lifecycle mutation
Voice → second breakdown database
Voice → parallel canonical catalog
Voice → self-issued referencePathId
Voice → parallel lifecycle
Voice → authoritative technician assignment
Voice → authoritative pre-close/final-close
```


## 12. First Voice handoff is confirmed intake, not authoritative registration

The approved operator conversation remains the Voice product contract.

Reference resolution adds one contextual requirement:

```text
trusted workshop scope
→ operator identity
→ model
→ installation
→ operation
→ device/element
→ subdevice when known/applicable
→ problem description
→ line stopped yes/no
→ complete read-back
→ operator confirms
```

The workshop scope does not need to become a spoken question when the deployment/session already provides one unambiguously. If it is absent or ambiguous, the system must clarify it.

After operator confirmation, Voice may emit an observation.

That observation is still **not** an authoritative BODYSHOP breakdown registration.

BODYSHOP must resolve the confirmed reference values to exactly one active selectable `referencePathId` before any later authoritative registration path could even be considered.


## 13. Minimal provider-neutral Voice observation

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

For the first integration path, only this intent is required:

```text
BREAKDOWN_INTAKE_CONFIRMED
```

`confirmed_breakdown` carries operator-confirmed observation values, not canonical authority:

```text
workshop_scope | null
model
installation
operation
device
subdevice | null
description
line_stopped
```

Voice does **not** provide authoritative:

```text
referencePathId
maintenance area
specialty
selected technician
canonical element_type
lifecycle state
```

A later BODYSHOP-side resolver may attach `referencePathId` only after the catalog confirms exactly one selectable path.


## 14. BODYSHOP Shadow remains the reuse target

Current BODYSHOP `AI_ROUTING_CONTRACT_V1` owns the provider-independent routing input:

```text
description
platform
installation
operation
faulty_element
element_type
line_stopped
```

Current `AI_ROUTING_SHADOW_V1` owns the immutable input snapshot/fingerprint, later human-decision attachment and explicit deterministic/recommend/abstain/invalid/error/excluded evidence states.

The future BODYSHOP-side adapter therefore has two separate jobs:

```text
1. resolve confirmed Voice reference values
   → canonical CatalogReferencePath / referencePathId

2. map the resolved canonical catalog data
   → existing AiRoutingInputV1
   → existing routing Shadow
```

The exact mapping from the canonical device/subdevice type to the current routing `element_type` must be decided in the future BODYSHOP adapter block against that repository's live contract. A7 does not invent that mapping.

Voice must not build a competing routing evaluator, fingerprint model, comparison lifecycle or breakdown store.

## 15. Transcript confidence is not domain confidence

Zello's official Channel API documents optional transcription events containing transcription confidence.

That value is evidence about transcription accuracy. It is not routing confidence, lifecycle confidence, safety confidence or permission to mutate BODYSHOP.

Keep separate:

```text
STT/channel confidence
→ transcript quality

catalog resolution
→ valid / invalid / ambiguous reference object

BODYSHOP routing
→ deterministic / recommend / abstain / invalid / error

human decision
→ authoritative Shadow comparison target
```

## 16. ElevenLabs position

ElevenLabs official documentation supports post-call transcription webhooks and in-call webhook tools.

Post-call webhooks are useful for audit/evidence and provider/version correlation, but arrive after call completion/analysis and must not be treated as the only real-time handoff mechanism.

If webhook tools are used later, the destination must be a bounded Voice/Shadow boundary. Voice must not expose authoritative BODYSHOP lifecycle mutation endpoints directly to the provider.

## 17. Zello position

The official Zello Channel API documents `features.transcriptions = true` and `on_transcription` events, where supported, including stream id, sender, text, confidence and language.

Native Zello transcription is therefore a reasonable future test candidate before adding another STT provider. Its workshop accuracy must be measured; A7 makes no adequacy claim.

Zello Work also documents talk priorities where High interrupts Normal/Low and Normal interrupts Low. A future laboratory may test AI at Low priority and humans above it, but this is a test hypothesis, not a Production policy.

## 18. Relevo lessons used only as design inspiration

Useful concepts retained:

```text
channel-adapter boundary
transcript separated from semantic interpretation
human-first PTT discipline
trace source utterance → interpretation → output → human response
network sender identity instead of voice biometrics when available
```

No Relevo code or implementation text is copied. The reviewed repository root showed no visible LICENSE file.

## 19. Provider DRIFT and missing transports

A5 provider result remains:

```text
DRIFT
```

Classification:

```text
A7 Voice-side decision                         NOT BLOCKED
canonical catalog design                       NOT BLOCKED
provider-neutral contract/test work            NOT BLOCKED
claim of aligned ElevenLabs behavior           BLOCKED BY DRIFT
real ElevenLabs end-to-end acceptance          requires drift resolution or explicit new expected-state decision
```

A6 also established:

```text
DIRECT_PHONE_AI_PATH: NOT_AVAILABLE
FULL_AI_CONTROL_TO_F400_PATH: NOT_AVAILABLE
```

These limitations block real transport proof, not the provider-neutral catalog/reference decision.


## 20. Next implementation candidate — after canonical catalog completion

The canonical BODYSHOP Reference Object Catalog prerequisite is now satisfied.

The smallest next implementation candidate should remain inside the isolated Voice laboratory:

# Voice Reference Resolution Harness V1

Candidate repository:

```text
egaracode/bodyshop-voice-poc
```

Single responsibility:

> Prove that confirmed spoken/display reference values can resolve fail-closed to one existing catalog-shaped reference path without connecting Voice to BODYSHOP runtime, Supabase or lifecycle mutation.

The harness should use a **small non-authoritative compatibility fixture**, not a full copied BODYSHOP database.

The fixture should preserve only the contract shape needed for testing:

```text
workshop
model
installation
operation
device
subdevice | null
reference_path_id
grain = DEVICE | DEVICE_SUBDEVICE
active
aliases[]
```

Required resolver outcomes:

```text
RESOLVED
INCOMPLETE
AMBIGUOUS
NOT_FOUND
```

Minimum tests should include:

```text
valid device-only path
valid device+subdevice path
wrong parent hierarchy
unknown device
unknown subdevice
ambiguous alias
missing workshop scope
inactive/non-selectable fixture path
free-text symptom kept separate from identity
```

The harness must not:

```text
call AI-Control-Workshop
call Supabase
copy the full canonical catalog
claim its fixture is authoritative
route to a technician
invoke AI routing
create a breakdown
mutate lifecycle state
call ElevenLabs or Zello
```

After this harness proves the resolver contract, a separate canonical BODYSHOP block may evaluate a real `Voice Shadow Intake Adapter` that consumes the authoritative catalog and existing routing Shadow.

This A7 document names the next candidate only. It does not authorize its implementation.


## 21. Official external sources consulted

Provider behavior revalidated: 2026-10-01.

### Zello Channel API specification

Publisher: Zello official GitHub organization

Reference:
https://github.com/zelloptt/zello-channel-api/blob/main/API.md

Engineering consequence:

- `features.transcriptions = true` can request transcription events where supported;
- `on_transcription` includes stream id, sender, text, confidence and language;
- transcription confidence remains transcript-quality evidence, not BODYSHOP decision authority.

### Zello Work — Talk priority

Publisher: Zello

Reference:
https://support.zello.com/zw/talk-priority

Engineering consequence:

- High interrupts Normal/Low;
- Normal interrupts Low;
- Low cannot interrupt;
- any future AI/human priority design still requires laboratory validation.

### ElevenLabs — Post-call webhooks

Publisher: ElevenLabs

Reference:
https://elevenlabs.io/docs/eleven-agents/workflows/post-call-webhooks

Engineering consequence:

- post-call transcription events contain conversation/transcript metadata after call completion/analysis;
- HMAC signature verification is supported;
- post-call delivery cannot be the sole mechanism for a live in-call handoff.

### ElevenLabs — Webhook tools

Publisher: ElevenLabs

Reference:
https://elevenlabs.io/docs/eleven-agents/customization/tools/webhook-tools

Engineering consequence:

- an agent can call external APIs during a conversation;
- A7 still forbids exposing authoritative BODYSHOP lifecycle mutation endpoints directly to the provider.

### Historical supporting maintenance-model evidence

The user-supplied maintenance workflow and previously reviewed SAP Maintenance Management technical-object documentation remain supporting design provenance. They no longer control the implemented reference-object shape; current canonical BODYSHOP GitHub does.

## 22. Explicit exclusions

A7 does not authorize or implement:

```text
AI-Control-Workshop modification
Supabase / SQL / migrations / RLS / RPC / Auth
BODYSHOP lifecycle mutation
real plant master data
real breakdown creation
real technician assignment
real pre-close or final close
ElevenLabs write / Publish / configuration mutation
phone/SIP provisioning
Zello API runtime integration
Zello Work priority/role changes
F400 runtime modification
Production
corporate network integration
secrets/.env
new dependencies
CI/workflow changes
```


## 23. Acceptance result

A7 is complete as a Voice-lab decision when:

```text
ONE provider-neutral boundary is documented
canonical BODYSHOP Reference Object Catalog is treated as existing authority
referencePathId is BODYSHOP-owned and never minted by Voice
workshop scope is included in canonical resolution
DEVICE and DEVICE_SUBDEVICE grains are preserved
NO second catalog or breakdown system is introduced
NO direct Voice → Supabase lifecycle mutation is proposed
existing BODYSHOP routing Shadow remains the reuse target after catalog resolution
transcription confidence is separated from catalog/routing authority
provider DRIFT is correctly classified
missing transports are correctly classified
ONE minimal next implementation candidate is identified
current official-source basis is recorded
```


## 24. Stop point

```text
A7_BODYSHOP_VOICE_INTEGRATION_DECISION_V1: DOCUMENTED
REFERENCE_OBJECT_GATE: SATISFIED_IN_CANONICAL_BODYSHOP
CANONICAL_BODYSHOP_MAIN_REVALIDATED: b232ad437888f0ee305a3393daf9a16553264179
NEXT_IMPLEMENTATION_CANDIDATE: Voice Reference Resolution Harness V1
NEXT_IMPLEMENTATION: NOT AUTHORIZED BY A7
```

Albert retains Ready, merge and authorization of the future implementation candidate.

No BODYSHOP canonical-state update is required by this documentation-only Voice-lab decision.
