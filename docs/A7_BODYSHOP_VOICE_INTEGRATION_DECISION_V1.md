# A7 — BODYSHOP Voice Shadow Integration Decision V1

> Status: VOICE-LAB INTEGRATION DECISION / SHADOW-ONLY / NO RUNTIME INTEGRATION

## 1. Purpose and authority

Define the minimum boundary that `bodyshop-voice-poc` must respect in any future connection to canonical BODYSHOP PRO.

This document is authoritative only for the Voice PoC side. It does **not** create or modify a canonical BODYSHOP architecture decision. Any future change in `egaracode/AI-Control-Workshop` requires that repository's own bootstrap, Issue, authorization, branch, tests, CI and Albert decision.

Canonical BODYSHOP domain, catalog and lifecycle authority remains in `egaracode/AI-Control-Workshop`.

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
src/types.ts
src/db.ts
src/components/ControlDashboard.tsx
src/ai/routingContract.ts
src/ai/routingShadow.ts
```

Additional product evidence reviewed:

- user-supplied internal maintenance-workflow evidence, reviewed read-only and not committed;
- SAP Help Portal, `Technical Objects (CS-BD/PM-EQM)`, current S/4HANA Maintenance Management documentation, https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/e98c7c41bbe8439e90daa5c114a7573b/59bdb853dcfcb44ce10000000a174cb4.html ;
- SAP Help Portal, `Equipment (CS-BD/PM-EQM-FL)`, current S/4HANA Maintenance Management documentation, https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/e72f747389b340229f7fa343975bfa57/a4c6b853dcfcb44ce10000000a174cb4.html ;
- current first-party Zello and ElevenLabs documentation listed below.

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

## 5. Existing BODYSHOP catalog capability and current gap

Current BODYSHOP already contains the correct first four catalog concepts:

```text
CatalogPlatform
→ CatalogInstallation
→ CatalogOperation
→ CatalogElement
```

The Control form already filters the hierarchy by parent identifiers and active catalog state.

For the future product vocabulary, `CatalogPlatform` may be presented to users as **Modelo** while the internal field/name may remain temporarily unchanged to avoid unnecessary migration churn.

Current gap:

```text
CatalogElement = one flat level under Operation
```

The reviewed workflow and Albert's product requirement need:

```text
Operation
→ Device / Element 1
→ Subdevice / Element 2 (when applicable)
```

Therefore the reference catalog must support a parent-child technical-object level before Voice can claim complete reference-object mapping.

## 6. Target synthetic catalog shape

The first non-production catalog fixture should use synthetic names only.

For this decision, **10 operations means 10 operation nodes under each installation**, because the reference hierarchy is `installation → operation`.

Target scale:

```text
3 models
× 5 installations per model
× 10 operations per installation
= 150 operation nodes
```

Illustrative model codes:

```text
A01
A02
A03
```

Illustrative installation names for each model:

```text
Laterales
Mascarón
Autobastidor
Puerta Derecha
Puerta Izquierda
```

Illustrative operation codes per installation:

```text
OP100
OP120
OP140
OP160
OP180
OP200
OP220
OP240
OP260
OP280
```

Internal identifiers must be unique by hierarchy even when the display operation code repeats, for example:

```text
A01-LATERALES-OP100
A01-MASCARON-OP100
A02-LATERALES-OP100
```

These are synthetic examples, not real plant master data.

Devices and subdevices are **not** generated as a blind Cartesian product. Each operation contains only the device instances that actually belong to that operation in the fixture/master data.

## 7. Device / subdevice model

Representative device families may include:

```text
ROBOT
CONTROL_SOLDADURA
MESA_TRABAJO
PINZA_SOLDADURA
FRESADORA
PLC_CONTROL
TRANSPORTE / AEROVIA when applicable
```

Representative child components may include:

```text
ROBOT
→ motor
→ teach pendant
→ armario eléctrico
→ cableado/dress pack

CONTROL_SOLDADURA
→ control pinza
→ control soldadura
→ potencia
→ comunicaciones

MESA_TRABAJO
→ brida
→ detector
→ cilindro
→ válvula
→ centrador

PINZA_SOLDADURA
→ servomotor/actuador
→ transformador
→ electrodos/caps
→ circuito de agua

FRESADORA
→ motor
→ cuchilla/fresa
→ sensor
→ accionamiento neumático
```

The definitive taxonomy belongs to BODYSHOP and must be accepted there. A7 does not make these illustrative component names canonical.

## 8. Minimal-change data-model direction

Because current BODYSHOP already owns `CatalogElement`, the preferred future direction is evolutionary rather than creating a second catalog system.

Conceptually extend the existing element model with parent/level metadata, for example:

```text
CatalogElement
  id
  operation_id
  parent_element_id | null
  node_level        DEVICE | SUBDEVICE
  element_type
  component_kind    | null
  name
  technical_area_hint
  specialty_hint
  active
```

A root device has `parent_element_id = null`.

A subdevice references exactly one valid parent device in the same operation.

This preserves the existing `CatalogPlatform → CatalogInstallation → CatalogOperation → CatalogElement` foundation while adding the missing Element-1/Element-2 relationship.

A future SQL design may express this as a self-reference or as separately normalized device/subdevice tables. That decision belongs to the canonical BODYSHOP Issue and is not authorized by A7.

## 9. Registration validity gate

Before a breakdown can be considered reference-valid, every supplied level must resolve through one active parent-child chain:

```text
model exists and active
AND installation belongs to model and is active
AND operation belongs to installation and is active
AND device belongs to operation and is active
AND, when supplied, subdevice belongs to device and is active
```

Failure at any level means:

```text
NO real breakdown registration
NO invented catalog object
NO silent fallback to free text
NO guessed canonical element type
```

The system must request correction/clarification or leave the intake incomplete.

A device-level report may remain valid when the catalog explicitly permits the device itself as the selected reference and the caller cannot identify a more specific child. The system must not fabricate a subdevice merely to fill the hierarchy.

## 10. Voice alias rule

Voice may hear workshop synonyms or variants, but language understanding does not grant catalog authority.

Allowed:

```text
spoken alias
→ resolve to one existing active catalog object
→ confirm with operator when needed
→ use canonical object id/name
```

Not allowed:

```text
spoken unknown term
→ create new device
```

or:

```text
ambiguous alias
→ choose one silently
```

A future alias library may improve matching, but every alias must terminate in an existing canonical catalog object.

## 11. Minimal Voice integration decision

The Voice PoC boundary is:

```text
phone / ElevenLabs / Zello / simulator
        ↓
Voice-side channel/provider adapter
        ↓
provider-neutral Voice observation
        ↓
BODYSHOP reference-object resolution boundary
```

From that boundary onward, BODYSHOP retains ownership of:

```text
catalog validity
reference-object identity
canonical element type
routing
Shadow evaluation
technician eligibility
lifecycle semantics
persistence
```

Explicitly rejected on the Voice side:

```text
Voice → direct Supabase/RPC lifecycle mutation
Voice → second breakdown database
Voice → parallel catalog
Voice → parallel lifecycle
Voice → authoritative technician assignment
Voice → authoritative pre-close/final-close
```

## 12. First Voice handoff is confirmed intake, not authoritative registration

The approved operator conversation remains:

```text
operator identity
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

After confirmation, Voice may emit an observation.

That observation is still **not** an authoritative BODYSHOP breakdown registration.

BODYSHOP must first resolve the reference hierarchy against the active catalog.

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

For the first integration candidate, only this intent is required:

```text
BREAKDOWN_INTAKE_CONFIRMED
```

`confirmed_breakdown` carries the operator-confirmed spoken/display values, not BODYSHOP authority:

```text
model
installation
operation
device
subdevice | null
description
line_stopped
```

Voice does **not** provide:

```text
maintenance area
specialty
selected technician
canonical element_type
catalog ids unless BODYSHOP supplied/confirmed them
```

## 14. BODYSHOP Shadow remains the reuse target

Current BODYSHOP `AI_ROUTING_CONTRACT_V1` already owns the provider-independent routing input:

```text
description
platform
installation
operation
faulty_element
element_type
line_stopped
```

Current `AI_ROUTING_SHADOW_V1` already owns input snapshot/fingerprint, later human-decision attachment and explicit recommend/abstain/invalid/error/excluded evidence states.

Voice must not build a competing routing evaluator, fingerprint model, comparison lifecycle or breakdown store.

After canonical BODYSHOP resolves a valid reference object, a future BODYSHOP-owned adapter may construct the existing routing input and reuse the existing Shadow capability.

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

## 20. Next implementation candidate — revised by the reference-object finding

A7 identifies one candidate only:

# BODYSHOP Reference Object Catalog V1

Candidate repository:

```text
egaracode/AI-Control-Workshop
```

Proposed responsibility:

```text
3 synthetic models
→ 5 installations per model
→ 10 operations per installation
→ operation-specific device instances
→ device-specific subdevices
→ active parent-child validation
→ deterministic catalog lookup for later Voice/Control use
```

It should reuse/evolve the existing catalog model rather than introduce a second catalog.

The candidate must establish the rule:

```text
NO valid active reference path
= NO authoritative breakdown registration
```

It must not, merely because A7 names it:

```text
change Supabase
add SQL
change Production
modify provider configuration
provision telephony
configure Zello
create real plant master data
```

This is a **candidate**, not authorization and not a canonical BODYSHOP decision. Before implementation, `AI-Control-Workshop` must independently revalidate its current main, canonical owners, open work and governance and Albert must authorize its exact Issue/scope.

Only after that catalog/reference block is accepted should the next BODYSHOP integration decision determine whether a `Voice Shadow Intake Adapter` is ready to consume it.

## 21. Official external sources consulted

Consulted: 2026-09-16.

### SAP Maintenance Management — Technical Objects / Equipment

Publisher: SAP Help Portal

References:

- https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/e98c7c41bbe8439e90daa5c114a7573b/59bdb853dcfcb44ce10000000a174cb4.html
- https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/e72f747389b340229f7fa343975bfa57/a4c6b853dcfcb44ce10000000a174cb4.html

Engineering consequence:

- maintenance structures may combine hierarchical functional locations with equipment;
- equipment/technical objects are maintained as master records and can be installed within functional locations;
- hierarchical technical-object structures are a standard maintenance-data pattern.

### Zello Channel API specification

Publisher: Zello official GitHub organization

Reference:
https://github.com/zelloptt/zello-channel-api/blob/main/API.md

Engineering consequence:

- channel stream/sender metadata;
- optional transcription events and confidence/language metadata.

### Zello Work — Talk priority

Publisher: Zello

Reference:
https://support.zello.com/zw/talk-priority

Engineering consequence:

- High interrupts Normal/Low;
- Normal interrupts Low;
- future human-priority assumptions require runtime validation.

### ElevenLabs — Post-call webhooks

Publisher: ElevenLabs

Reference:
https://elevenlabs.io/docs/eleven-agents/workflows/post-call-webhooks

Engineering consequence:

- post-call transcript/conversation evidence;
- HMAC webhook verification;
- post-call timing is unsuitable as the sole mechanism for live handoff.

### ElevenLabs — Webhook tools

Publisher: ElevenLabs

Reference:
https://elevenlabs.io/docs/eleven-agents/customization/tools/webhook-tools

Engineering consequence:

- an agent can call external REST APIs during a conversation;
- A7 keeps providers away from authoritative BODYSHOP lifecycle mutation endpoints.

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
reference-object validity is mandatory
BODYSHOP catalog authority is preserved
NO second catalog or breakdown system is introduced
NO direct Voice → Supabase lifecycle mutation is proposed
existing BODYSHOP routing Shadow remains the reuse target after catalog resolution
transcription confidence is separated from catalog/routing authority
provider DRIFT is correctly classified
missing transports are correctly classified
ONE next implementation candidate is identified
current official-source basis is recorded
```

## 24. Stop point

```text
A7_BODYSHOP_VOICE_INTEGRATION_DECISION_V1: DOCUMENTED
REFERENCE_OBJECT_GATE: REQUIRED
NEXT_IMPLEMENTATION_CANDIDATE: BODYSHOP Reference Object Catalog V1
NEXT_IMPLEMENTATION: NOT AUTHORIZED
```

Albert retains Ready, merge and authorization of any future BODYSHOP implementation.

No BODYSHOP canonical-state update required by this documentation-only Voice-lab decision.