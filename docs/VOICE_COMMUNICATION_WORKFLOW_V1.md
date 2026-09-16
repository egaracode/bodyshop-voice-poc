# BODYSHOP Voice PoC — Voice Communication Workflow V1

> Status: DOCUMENTED PRODUCT COMMUNICATION CONTRACT / SHADOW / NON-AUTHORITATIVE

## 1. Purpose

Define the Voice PoC communication workflow approved by Albert for the isolated `bodyshop-voice-poc` laboratory.

This document specifies **who communicates with whom, what information is requested, the required confirmation points, the walkie exchange, and the physical-resolution/pre-close communication boundary**.

It does not implement telephony, provider configuration, BODYSHOP lifecycle mutation or production integration.

## 2. Authority and relationship to BODYSHOP PRO

This document owns only the Voice PoC conversational/communication sequence.

Canonical BODYSHOP lifecycle authority remains in `egaracode/AI-Control-Workshop`, especially the active lifecycle owner:

```text
docs/DATA_CONTRACTS/BREAKDOWN_LIFECYCLE_ACTOR_MATRIX_V1.md
```

Therefore:

- this Voice contract may describe a Shadow record of a confirmed intake for later evaluation;
- it does not create a real authoritative breakdown;
- it does not assign a real production technician;
- it does not perform a real pre-close or final close;
- canonical lifecycle, actor authority, persistence and safety rules remain BODYSHOP-owned.

All workshop semantics in this document are classified as:

```text
BODYSHOP_OWNED_DOMAIN_RULE
```

Provider-specific implementation fit is deliberately not decided here and must be revalidated against current official provider documentation before implementation.

## 3. Public-laboratory data boundary

Versioned examples use dummy identities and generic locations only.

Do not commit:

- real worker names;
- real protected operational data;
- production credentials;
- corporate-network details;
- secrets;
- protected real audio or transcripts.

Example placeholders:

```text
OPERARIO_A
TECH_A
PLATAFORMA_X
INSTALACION_Y
OP_Z
ROBOT_R
```

## 4. End-to-end communication sequence

```text
plant operator
→ phone
→ AI Control
→ operator identification
→ platform
→ installation
→ operation
→ faulty element/device
→ problem description
→ line-stopped status
→ routing recommendation
→ complete verbal read-back
→ operator confirms/corrects
→ Shadow intake registration for later review
→ simulated technician/walkie notification
→ technician receipt acknowledgement
→ technician arrival/intervention acknowledgement
→ physical work
→ technician reports physical resolution
→ AI Control acknowledges or requests repetition
→ pre-close boundary
→ technician later documents technical solution
→ canonical final close remains technician-owned in BODYSHOP
```

## 5. Stage 1 — Operator starts the call

The communication is initiated by a plant operator using the telephone channel.

Target:

```text
Operator → AI Control
```

AI Control opens with the appropriate greeting for the time of day and asks for identity.

Example intent:

```text
"Buenos días / tardes / noches. ¿Puedes decirme tu nombre y apellido?"
```

The operator replies with their identity.

In the Shadow PoC, AI Control records the provided identity in the intake evidence using only dummy identities in public/versioned artifacts.

## 6. Stage 2 — Required breakdown intake

AI Control requests the breakdown information in this order:

1. operator name and surname;
2. platform;
3. installation;
4. operation;
5. faulty element or device;
6. symptom / problem description;
7. whether the line is stopped.

Example conversational prompts:

```text
"¿De qué plataforma llamas?"
"¿Qué instalación?"
"¿Qué operación?"
"¿Qué elemento o dispositivo está fallando?"
"¿Qué problema tiene / qué está ocurriendo?"
"¿La línea está parada?"
```

A required field that has not been understood or confirmed must not be silently invented.

## 7. Stage 3 — Routing recommendation boundary

After collecting the breakdown description, AI Control may determine the intended first routing category, for example electrical or mechanical, according to the applicable BODYSHOP routing rules.

In this Shadow contract:

```text
routing recommendation
≠ real production assignment
```

Any technician addressee used in the laboratory is simulated/dummy unless a later separately authorized block defines another boundary.

This document does not redefine canonical routing rules and does not authorize provider-side lifecycle or technician authority.

## 8. Stage 4 — Mandatory operator confirmation

Before the intake is treated as complete, AI Control reads back the **complete understood breakdown** to the operator.

Example structure:

```text
"Te confirmo:
llamas desde [PLATAFORMA_X],
[INSTALACION_Y],
operación [OP_Z],
el problema está en [ELEMENTO],
y la avería es [DESCRIPCION].
La línea está [PARADA / NO PARADA].
¿Es correcto?"
```

The operator either:

```text
CONFIRMS
or
CORRECTS
```

If the operator corrects a field, AI Control updates the understood intake and repeats the relevant confirmation.

No operator confirmation means:

```text
SHADOW_INTAKE_COMPLETE: NO
```

## 9. Stage 5 — Shadow registration for later review

After complete operator confirmation, AI Control may register the confirmed intake in the **Shadow evaluation path**.

Purpose:

```text
later human review
→ compare what was said
→ what AI Control understood
→ what was confirmed
→ what routing was recommended
→ identify errors / ambiguities / language gaps
```

The Shadow record may retain only the minimum authorized evidence needed for evaluation, such as:

- confirmed intake fields;
- normalized routing recommendation;
- timestamps;
- clarification/repetition flags;
- missing/uncertain-field evidence;
- sanitized transcript evidence when separately permitted.

This is not authorization to write a real BODYSHOP breakdown or lifecycle state.

## 10. Stage 6 — Walkie notification to the technician

AI Control initiates the walkie communication using the technician addressee.

Opening pattern:

```text
"De Control a [TECH_A]."
```

The breakdown message communicates the relevant confirmed operational context:

```text
platform
installation
operation
element/device/robot
problem/symptom
```

Example structure:

```text
"Llaman de [PLATAFORMA_X],
[INSTALACION_Y],
operación [OP_Z].
El [ELEMENTO / ROBOT / DISPOSITIVO] tiene [PROBLEMA]."
```

The message must not introduce details that were not captured or confirmed.

## 11. Stage 7 — Technician receipt acknowledgement

The technician may acknowledge receipt with semantically equivalent phrases such as:

```text
"Recibido."
"Ok, me acerco."
"Ok, lo he recibido."
```

The technician may also request repetition:

```text
"¿Puedes repetírmelo?"
```

When repetition is requested, AI Control repeats the requested fragment or the complete breakdown as needed, without inventing or reinterpreting missing details.

Important invariant:

```text
RECEIPT ACKNOWLEDGEMENT
≠
ARRIVAL / INTERVENTION START
```

Receiving the walkie message does not by itself prove that the technician has arrived or started physical intervention.

## 12. Stage 8 — Arrival / intervention acknowledgement

Arrival and intervention are separate from initial receipt.

Expected intents include:

```text
"De [TECH_A] a Control, ya he llegado."
"Ya estoy interviniendo."
```

In a future BODYSHOP-integrated implementation, authoritative state effects must follow the canonical lifecycle owner and its safety/actor requirements.

This documentation-only Shadow block performs no lifecycle mutation.

## 13. Stage 9 — Technician reports physical resolution

After the fault has been physically resolved, the technician communicates back to Control / AI Control by walkie.

Accepted semantic variants include:

```text
"De [TECH_A] a Control, avería solucionada."
"Puedes cerrar la avería."
"La avería está solucionada."
```

These phrases mean:

```text
PHYSICAL_RESOLUTION_REPORTED
```

They do **not** mean that the technician has already performed the canonical final technical close.

## 14. Stage 10 — AI Control response

When the physical-resolution communication is understood, AI Control acknowledges it.

Example:

```text
"Ok, recibido."
```

When the message is unclear or incomplete:

```text
"¿Puedes repetírmelo?"
```

AI Control must prefer repetition/clarification over invented content.

## 15. Stage 11 — Pre-close communication boundary

The pre-close boundary is reached only after a valid communication from the **technician responsible for the intervention** that the fault is physically resolved.

Conceptually:

```text
technician reports physical resolution
→ AI Control understands + acknowledges
→ case becomes eligible for the canonical pre-close path
```

This contract does not execute the pre-close.

The canonical BODYSHOP lifecycle controls the real transition and actor authority.

The technician's later technical solution and final close remain separate from physical-resolution reporting and pre-close.

## 16. Stage 12 — Missing information, ambiguity and no response

### 16.1 Unclear field

```text
unclear field
→ ask the speaker to repeat that field
```

### 16.2 Ambiguous field

```text
ambiguous field
→ repeat what AI Control understood
→ request confirmation or correction
```

### 16.3 Required field missing

```text
required field missing
→ do not mark intake complete
→ continue clarification
```

### 16.4 Operator does not confirm the complete breakdown

```text
no valid operator confirmation
→ SHADOW_INTAKE_COMPLETE: NO
→ do not continue as if confirmed
```

### 16.5 Technician does not answer the walkie call

```text
no technician response
→ repeat the walkie call according to the future retry policy
→ record NO_RESPONSE evidence
→ do not fabricate receipt, arrival or intervention
```

V1 deliberately does **not** define a fixed retry count or escalation timeout. That requires a later explicit operational decision and must not be invented here.

### 16.6 Technician message is not understood

```text
unclear technician message
→ request repetition
→ do not infer arrival, intervention or resolution
```

### 16.7 No valid physical-resolution communication

```text
no valid technician resolution communication
→ PRE_CLOSE_ELIGIBLE: NO
```

## 17. Intent separation invariants

The following intents must remain distinguishable:

```text
OPERATOR_IDENTITY_PROVIDED
BREAKDOWN_FIELD_PROVIDED
BREAKDOWN_CONFIRMATION_GRANTED
BREAKDOWN_CONFIRMATION_CORRECTED
TECHNICIAN_RECEIPT_ACKNOWLEDGED
TECHNICIAN_REPEAT_REQUESTED
TECHNICIAN_ARRIVAL_REPORTED
TECHNICIAN_INTERVENTION_REPORTED
TECHNICIAN_PHYSICAL_RESOLUTION_REPORTED
AI_CONTROL_ACKNOWLEDGED
NO_RESPONSE
UNCLEAR_INFORMATION
```

Do not collapse:

```text
receipt → intervention
intervention → resolution
resolution report → final close
```

## 18. Shadow evaluation purpose

The workflow is designed so that later evaluation can answer questions such as:

- Did AI Control capture the operator identity correctly?
- Were platform, installation and operation captured correctly?
- Was the faulty element/device captured correctly?
- Was the problem description understood correctly?
- Was line-stopped status understood correctly?
- Did the operator confirm the final intake?
- Was the routing recommendation consistent with the expected workshop routing?
- Was the technician message communicated without adding facts?
- Did AI Control distinguish receipt, arrival/intervention and physical resolution?
- Where were repetitions or clarifications required?
- Which workshop phrases should be added to the language library?

Evaluation evidence is non-authoritative and must remain separate from real BODYSHOP lifecycle truth.

## 19. Explicit exclusions

This contract does not authorize or implement:

```text
real BODYSHOP breakdown creation or mutation
real technician assignment
real pre-close or final close
ElevenLabs write / Publish / provider mutation
new provider version activation
Zello API or automation
phone/SIP provisioning
AI Control → Zello/F400 bridge
Supabase
SQL / RLS / RPC / Auth
AI-Control-Workshop changes
Production
corporate-network integration
new dependencies
CI/workflow changes
secrets
A7 implementation
```

## 20. Acceptance criteria

The contract is complete when it documents:

- operator-initiated phone contact;
- greeting and identity capture;
- ordered breakdown-data capture;
- complete operator read-back and confirmation;
- Shadow registration purpose and boundary;
- routing recommendation boundary;
- walkie technician notification;
- technician receipt/repeat intents;
- explicit separation of receipt from arrival/intervention;
- technician physical-resolution intents;
- AI Control acknowledgement/repetition behavior;
- pre-close eligibility boundary;
- missing/ambiguous/no-response rules;
- no fabricated lifecycle state;
- public-laboratory privacy boundary;
- canonical BODYSHOP lifecycle authority preserved.

## 21. Stop point

```text
VOICE_COMMUNICATION_WORKFLOW_V1: DOCUMENTED
RUNTIME_IMPLEMENTATION: NOT_AUTHORIZED_BY_THIS_BLOCK
A7_IMPLEMENTATION: NOT_AUTHORIZED
```

Albert retains Ready and merge authority.

No canonical-state update required.
