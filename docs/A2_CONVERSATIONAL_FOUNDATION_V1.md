# A2 Conversational Foundation V1

## 1. Status

```text
A2_CONVERSATIONAL_FOUNDATION_V1: DOCUMENTED_CANDIDATE
```

This document defines the minimum conversational architecture for the isolated `bodyshop-voice-poc` laboratory.

It does not authorize production use, corporate-network use, Supabase, AI-Control-Workshop changes, Zello API, ElevenLabs API/runtime, Azure, Twilio, OpenAI, dependencies, CI, or any real operational action.

The language library is an incremental supporting asset. A large corpus is **not** a prerequisite for progressing with A2.

## 2. Core decision

AI Control leads the conversation.

```text
AI Control asks one bounded question at a time
→ receives a constrained human answer
→ preserves any useful context already obtained
→ normalizes meaning using role + context + flow stage
→ clarifies only when information is incomplete or ambiguous
→ continues the BODYSHOP conversational flow
```

Initial A2 does not attempt unrestricted free-form industrial-language understanding.

## 3. Channel-specific activation

A2 distinguishes a direct phone call from a shared walkie channel.

### 3.1 Direct phone call

A dedicated call to AI Control is itself an activation signal.

```text
DIRECT CALL TO AI CONTROL
→ SESSION ACTIVE
```

Once the call is active, the operator does not need to repeat a wake phrase before every answer.

The session ends when the call ends or when the conversation reaches an explicit terminal/fallback state.

### 3.2 Shared walkie channel

The default walkie state is passive.

```text
PASSIVE / NOT ADDRESSED
→ no conversational response
→ no BODYSHOP intent execution
→ no workflow action
```

Technician-to-technician traffic must not activate AI Control merely because the word `Control` is heard.

AI Control may enter a walkie conversation only when the utterance is sufficiently clearly addressed to Control as the intended recipient/call-sign.

Confirmed workshop activation forms for A2:

```text
"De [Nombre o Nombre y Apellido] a Control"
"Control puedes cerrar [Nombre Instalación]"
"Control soy [Nombre o Nombre y Apellido]"
"Control me recibes?"
```

These forms are linguistic patterns. This public laboratory document must not contain real worker names or real operational identifiers.

### 3.3 Activation is not action

Activation and operational intent are separate gates.

```text
ACTIVATION GATE
→ ACTIVE CONVERSATION CONTEXT
→ HUMAN UTTERANCE
→ SEMANTIC INTENT
→ DOMAIN / AUTHORITY VALIDATION
→ ALLOWED LAB / FUTURE BODYSHOP ACTION
```

Never:

```text
heard keyword
→ direct action
```

A single utterance may both activate AI Control and contain an operational intent, but the intent still requires context/domain validation.

Example:

```text
"Control puedes cerrar [Instalación]"
→ activation detected
→ REQUEST_PRE_CLOSE candidate detected
→ exact breakdown/context must be resolved
→ only then may the pre-close flow continue
```

## 4. Walkie active-session window

Once AI Control has been explicitly addressed and replies, a bounded conversational window may be active.

A technician does not need to repeat `Control` before every immediate follow-up answer inside that active exchange.

However, shared-channel safety takes priority:

- an active window exists only while AI Control is logically awaiting the next reply or completing the current bounded exchange;
- after AI Control completes the requested interaction and no reply is pending, the walkie session returns to passive;
- later unrelated walkie traffic requires a new activation;
- timeout values are implementation configuration to be validated in the PoC, not hard-coded as a production rule in A2;
- if speaker/context continuity is uncertain, AI Control must clarify or return to passive rather than absorb unrelated traffic.

Conceptual lifecycle:

```text
PASSIVE
→ ACTIVATION_DETECTED
→ ACTIVE
→ [AI asks / human answers / intent resolved]
→ COMPLETE or TIMEOUT or FALLBACK
→ PASSIVE
```

## 5. Operator conversational contract

The operator flow is guided by AI Control.

Minimum required information for the laboratory conversation:

```text
identity
model
installation
operation
problem description
```

Conceptual flow:

```text
Operator calls AI Control
→ AI Control obtains identity
→ obtains model
→ obtains installation
→ obtains operation
→ obtains problem description
→ clarifies only missing/ambiguous values
→ produces a bounded breakdown summary / next-step response
```

AI Control must reuse information already provided.

If the operator supplies several valid fields in one utterance, AI Control must not force them to repeat those fields one by one. It should ask only for what is still missing or uncertain.

## 6. Technician conversational contract

The technician flow initially focuses on resolution communication and pre-close request.

Conceptual flow:

```text
Technician addresses Control
→ AI Control activates walkie session
→ technician identity/context is resolved
→ exact breakdown is resolved
→ technician communicates resolution / pre-close request
→ AI Control interprets intent
→ domain/context validation
→ simulated/future PRE-CLOSE flow
→ short unambiguous response
→ session complete
```

## 7. Confirmed technician resolution semantics

Within the correct context — technician + identified active breakdown + resolution stage — the following confirmed workshop expressions map to the same canonical semantic family:

```text
"puedes cerrar"
"la puedes cerrar"
"ciérrala"
"en marcha"
"está en marcha"
"avería solucionada"
"solucionada"
```

Canonical intent:

```text
REQUEST_PRE_CLOSE
```

Critical domain rule:

```text
technician says "cerrar" / equivalent
≠ final technical closure

meaning in this flow:
BREAKDOWN SOLVED
+
REQUEST PRE-CLOSE
```

The durable operational sequence remains conceptually:

```text
Technician reports physical resolution
→ Control / future AI Control performs pre-close
→ Technician documents the solution
→ Technician performs final closure
```

AI Control must never represent that it performed the technician's final technical closure.

## 8. Exact-breakdown resolution

AI Control must not guess which breakdown a technician means.

If exactly one breakdown is unambiguously associated with the active context, a phrase such as:

```text
"la puedes cerrar"
```

may map directly to `REQUEST_PRE_CLOSE`.

If more than one breakdown is plausible, clarification is mandatory before pre-close.

```text
one unambiguous breakdown
→ continue

several plausible breakdowns
→ ask which one
→ do not pre-close until resolved
```

## 9. Contextual interpretation model

A2 interpretation must use more than isolated keywords.

```text
ACTIVATION STATE
+
ROLE
+
CONVERSATION CONTEXT
+
FLOW STAGE
+
UTTERANCE
```

Example:

`solucionada` in isolation can be ambiguous.

Inside an active technician session with one identified breakdown in resolution stage, it can safely map to `REQUEST_PRE_CLOSE`.

## 10. Confirmation policy

A2 adopts **selective confirmation**, not universal confirmation.

If identity, exact breakdown, context and intent are all unambiguous, AI Control should not add an unnecessary confirmation turn before continuing the pre-close flow.

If a critical value or reference is uncertain, AI Control must confirm only that uncertain element.

Preferred pattern:

```text
"¿Te refieres a [dato dudoso]?"
```

rather than restarting the whole conversation or asking the user to repeat everything.

## 11. Recovery and human fallback

A2 adopts a maximum of three recovery attempts for the same unresolved critical conversational item.

```text
1st failure
→ focused reprompt

2nd failure
→ clearer reformulation

3rd failure
→ STOP automatic operational progression
→ human Control fallback
```

No action may be guessed merely to keep the conversation moving.

This rule applies to meaningful No-Match / No-Input / unresolved-critical-data situations, not to harmless conversational fillers.

The exact technical handoff mechanism is future work and is not authorized by this document.

## 12. Minimum intent foundation

Initial A2 intent families:

```text
ATTENTION_CONTROL
PROVIDE_IDENTITY
PROVIDE_MODEL
PROVIDE_INSTALLATION
PROVIDE_OPERATION
REPORT_BREAKDOWN
REQUEST_PRE_CLOSE
```

`Control me recibes?` is currently an activation/attention check. It requires a conversational response but no lifecycle action by itself.

This is a minimum foundation, not a frozen exhaustive ontology.

## 13. Language Library role

The language library is classified as:

```text
ITERATIVE SUPPORTING ASSET
```

not:

```text
DEVELOPMENT GATE
```

Expected evolution:

```text
development
↔ real conversation samples collected outside public repo constraints
↔ validated linguistic variants
↔ language library
↔ future linguistic regression tests
```

Raw workshop language and normalized semantic meaning are separate concepts.

## 14. ElevenLabs compatibility rule

BODYSHOP owns domain semantics. ElevenLabs is a future provider/adapter layer.

Every future A2 implementation decision should be classified as one of:

```text
ELEVENLABS_NATIVE_FIT
ELEVENLABS_ADAPTER_REQUIRED
BODYSHOP_OWNED_DOMAIN_RULE
```

Current fit assessment:

| Concern | Classification | Rationale |
|---|---|---|
| conversation duration / silence / turn-taking / interruptions | ELEVENLABS_NATIVE_FIT | ElevenLabs exposes conversation-flow configuration for these concerns. |
| contextual STT vocabulary | ELEVENLABS_NATIVE_FIT | Scribe v2 supports keyterm prompting; realtime has provider limits and must use selected context-relevant terms. |
| shared-walkie `addressed to Control` activation gate | ELEVENLABS_ADAPTER_REQUIRED + BODYSHOP_OWNED_DOMAIN_RULE | The semantic rule belongs to BODYSHOP and must surround/provider-gate the voice layer. |
| `cerrar` means pre-close, not final close | BODYSHOP_OWNED_DOMAIN_RULE | Provider transcription cannot own lifecycle semantics. |
| three-failure operational fallback policy | BODYSHOP_OWNED_DOMAIN_RULE with professional design support | BODYSHOP decides the operational boundary; professional voice-agent guidance supports limited recovery loops and human escalation. |

The system must not be architected on the assumption that ElevenLabs understands all workshop vocabulary from day one.

## 15. Official/professional references

Validated during A2 design on 2026-09-04:

- ElevenLabs — Conversation flow: https://elevenlabs.io/docs/eleven-agents/customization/conversation-flow
- ElevenLabs — Speech-to-Text keyterm prompting: https://elevenlabs.io/docs/eleven-api/guides/how-to/speech-to-text/batch/keyterm-prompting
- ElevenLabs — Speech-to-Text capabilities: https://elevenlabs.io/docs/overview/capabilities/speech-to-text/
- Google Cloud Dialogflow CX — Voice agent design best practices: https://docs.cloud.google.com/dialogflow/cx/docs/concept/voice-agent-design

Provider-specific limits and capabilities must be revalidated against official documentation before implementation because they can change.

## 16. Safety and repository boundary

This document does not authorize:

```text
production
corporate network
real worker names in public repo
real operational data in public repo
Supabase
AI-Control-Workshop changes
Zello API
ElevenLabs API/runtime
Azure
Twilio
OpenAI
app code
dependencies
CI/workflow changes
automation with real impact
```

## 17. A2 acceptance summary

A2 conversational foundation is considered documented when all of the following are explicit:

- AI Control leads the conversation;
- large language corpus is not a prerequisite;
- direct-phone and shared-walkie activation are separated;
- shared walkie is passive by default;
- confirmed activation phrases are documented;
- activation and operational intent are separate;
- technician-to-technician traffic does not automatically activate AI Control;
- active walkie sessions are bounded and safely return to passive;
- operator and technician flows are separated;
- `REQUEST_PRE_CLOSE` semantics reflect confirmed workshop language;
- `cerrar` is not final technical closure;
- ambiguous breakdown references require clarification;
- confirmation is selective, not universal;
- unresolved critical data uses a maximum three-attempt recovery policy, then human fallback;
- Language Library is incremental;
- ElevenLabs fit is explicit without transferring BODYSHOP domain authority to the provider.

## 18. Stop point

```text
A2_CONVERSATIONAL_ARCHITECTURE: DOCUMENTED
IMPLEMENTATION: NOT AUTHORIZED BY THIS DOCUMENT
```
