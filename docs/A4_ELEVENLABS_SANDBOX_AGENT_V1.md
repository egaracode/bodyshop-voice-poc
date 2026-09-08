# A4 ElevenLabs Sandbox Agent V1

## 1. Status

```text
A4_ISSUE: #12 OPEN
A4_PR: #13 DRAFT
ELEVENLABS_SANDBOX_AGENT: CREATED_AND_PUBLISHED
CURRENT_PROVIDER_CONFIGURATION: SYSTEM_PROMPT_V1
PROCEDURES_REFACTOR: AUTHORIZED_BY_ALBERT_2026-09-08
PROCEDURES_REPOSITORY_CANDIDATE: PREPARED
PROCEDURES_PROVIDER_LOAD: NOT_YET_DONE
A4_RUNTIME_RETEST_AFTER_REFACTOR: NOT_RUN
A4_OVERALL: NOT_PASS
READY: NO
MERGE: NO
```

A4 remains strictly inside the isolated public `egaracode/bodyshop-voice-poc` laboratory. BODYSHOP domain semantics remain authoritative over provider behavior.

The sandbox agent already exists and has produced real ElevenLabs preview evidence. The current repository work now prepares an authorized configuration refactor from one growing system prompt to a short global system prompt plus task-specific ElevenLabs Free-form Procedures.

Provider evidence collected before this refactor remains evidence only for the provider configuration that produced it.

---

## 2. Repository baseline and authority

A4 started from:

```text
main = 2650665d60eb91b94eefb82cf13be85e93ac81d8
Issue = #12
branch = feat/a4-elevenlabs-sandbox-agent-v1
PR = #13
```

Authoritative inputs:

1. `docs/A2_CONVERSATIONAL_FOUNDATION_V1.md`
2. `docs/A3_CONVERSATIONAL_VERIFICATION_AND_ELEVENLABS_TEST_CONTRACT_V1.md`
3. `docs/VOICE_POC_ROADMAP_A2_A6_V1.md`
4. Issue `#12`, including the authorized Procedures refinement comment
5. current official ElevenLabs documentation
6. sanitized provider-runtime evidence in `docs/A4_ELEVENLABS_TEST_EVIDENCE_V1.md`

Provider configuration must implement BODYSHOP semantics; provider behavior does not redefine them.

---

## 3. Safety boundary

A4 must not connect or perform:

```text
Supabase
AI-Control-Workshop changes
BODYSHOP production runtime
corporate network
Zello API
real phone number
SIP trunk
Twilio / Exotel / WhatsApp transport
real BODYSHOP operational webhook
real state-changing tool
real worker data in the public repository
real operational identifiers in the public repository
```

The shared-walkie `addressed to Control` decision remains BODYSHOP-owned and external to ElevenLabs.

A4 provider tests may validate agent behavior only after activation context is supplied. They cannot prove the external walkie activation/non-intervention gate.

A5 still owns F400/PTT/Zello transport, clipping, overlap, radio compression and repeated real acoustic verification. One workshop-noise preview run is useful preliminary evidence only.

---

## 4. Provider configuration observed in A4

The isolated provider agent has been manually created and published by Albert with:

```text
Agent name: AI Control — A4 Sandbox
Primary conversation: Spanish
LLM: Qwen3.5-397B-A17B
Voice: Eric — provisional A4 voice
Expressive mode: disabled
Default personality: disabled
External BODYSHOP tools: none
Supabase: none
Phone / SIP / Zello integration: none
Knowledge base: none
Production deployment: forbidden
```

Existing runtime dynamic variables remain unchanged:

```text
channel_mode
activation_verified
caller_role
known_identity
known_model
known_installation
known_operation
active_breakdown_count
breakdown_ref
flow_stage
```

No additional dynamic variable is required merely to collect `element_type` or `element_ref` during an A4 conversation.

---

## 5. Official ElevenLabs capability baseline — revalidated 2026-09-08

Current official ElevenLabs documentation states:

- Procedures contain task-specific instructions and load when their trigger matches the conversation.
- Free-form Procedures are intended for tasks where wording/order may adapt and unexpected turns can occur.
- Structured Procedures run typed steps in a fixed sequence.
- Global tone, identity, refusal policies and guardrails belong in the system prompt; task-specific steps belong in Procedures.
- Procedure content is capped at 50,000 characters.
- Procedures version together with the agent when published.
- Concrete, disjoint triggers reduce incorrect procedure selection.
- The Dashboard is the recommended interactive authoring path.

Official references:

- https://elevenlabs.io/docs/eleven-agents/customization/procedures
- https://elevenlabs.io/docs/eleven-agents/customization/procedures/free-form-procedures
- https://elevenlabs.io/docs/eleven-agents/customization/procedures/structured-procedures
- https://elevenlabs.io/docs/eleven-agents/best-practices/prompting-guide
- https://elevenlabs.io/docs/eleven-agents/customization/personalization/dynamic-variables

### Why Free-form now

The operator flow has a preferred order but must also support:

```text
corrections
multiple clear fields in one utterance
out-of-order useful information
explicit uncertainty
focused clarification
natural workshop language
```

That variability fits Free-form Procedures better than a rigid fixed sequence for the current A4/Qwen configuration.

Structured Procedures remain a future candidate if the BODYSHOP contract later requires fixed typed steps and the selected model/provider behavior is independently validated.

---

## 6. Authorized A4 Procedures architecture

The authorized provider target is now:

```text
GLOBAL SYSTEM PROMPT
→ role / Spanish voice style
→ sandbox / no-real-action boundary
→ runtime context variables
→ channel activation boundary
→ global confirmation/recovery
→ global guardrails

FREE-FORM PROCEDURE — Operator breakdown
→ seven-field operator collection contract
→ identity completeness
→ slot boundaries
→ correction semantics
→ multi-slot retention
→ uncertainty remains UNCONFIRMED
→ neutral clarification
→ sandbox completion

FREE-FORM PROCEDURE — Technician pre-close
→ technician resolution semantics
→ REQUEST_PRE_CLOSE phrases
→ exact-breakdown ambiguity
→ role isolation
→ PRE-CLOSE != final technical closure
→ sandbox semantic response
```

Repository candidate assets:

- `elevenlabs/A4_AI_CONTROL_SYSTEM_PROMPT_V2.md`
- `elevenlabs/A4_OPERATOR_BREAKDOWN_PROCEDURE_V1.md`
- `elevenlabs/A4_TECHNICIAN_PRE_CLOSE_PROCEDURE_V1.md`

`elevenlabs/A4_AI_CONTROL_SYSTEM_PROMPT_V1.md` remains historical evidence for the prior tested prompt architecture and must not be silently rewritten into V2.

---

## 7. Operator contract carried into the Procedure

Preferred guided sequence:

```text
identity: name + at least one surname
→ model
→ installation
→ operation
→ element type
→ exact element reference
→ problem description
```

The flow is guided, not rigidly one-value-per-utterance.

If the operator voluntarily supplies several clear fields, AI Control retains them and asks only for what remains missing.

A clear correction supersedes the previous value.

Critical data rule discovered through provider testing:

```text
VALUE HEARD != VALUE CONFIRMED

explicit doubt
→ UNCONFIRMED
→ ask only for confirmation/correction
→ do not progress
```

Expressions such as `creo`, `puede ser`, `posiblemente`, `no estoy seguro` or equivalent must not be promoted to confirmed operational data merely to keep the conversation moving.

---

## 8. Technician contract carried into the Procedure

Inside verified technician + active breakdown + resolution context, these expressions may represent:

```text
BREAKDOWN SOLVED + REQUEST_PRE_CLOSE
```

Examples:

```text
puedes cerrar
la puedes cerrar
ciérrala
en marcha
está en marcha
avería solucionada
solucionada
```

Critical rule:

```text
technician "cerrar"
→ REQUEST_PRE_CLOSE
!= final technical closure
```

If exactly one active breakdown is unambiguous, unnecessary confirmation is avoided. If several are plausible, AI Control asks which one and never chooses.

The same keywords used by an operator do not inherit technician PRE-CLOSE semantics.

---

## 9. Provider migration procedure

Do not modify the provider until the repository candidate is reviewed.

After repository review, Albert may migrate the existing sandbox agent without creating a second agent:

1. Keep the same isolated agent, model, voice and current 10 dynamic variables.
2. Replace the current provider system prompt with `A4_AI_CONTROL_SYSTEM_PROMPT_V2.md` content excluding its repository-only header note.
3. Create a **Free-form Procedure** named `Operator breakdown`.
4. Use the exact trigger/content from `A4_OPERATOR_BREAKDOWN_PROCEDURE_V1.md`.
5. Create a **Free-form Procedure** named `Technician pre-close`.
6. Use the exact trigger/content from `A4_TECHNICIAN_PRE_CLOSE_PROCEDURE_V1.md`.
7. Do not add tools, Knowledge Base, phone/SIP/Zello, Supabase or any real integration.
8. Publish the agent changes once all three configuration assets match the repository candidate.
9. Record publication as manual provider evidence.
10. Treat all earlier provider runtime tests as evidence for the old V1 prompt configuration only.

---

## 10. A4 verification target after migration

Provider-native A3 scenarios remain the target, including:

```text
OP-02 guided operator collection
OP-03 multi-slot retention
OP-04 focused clarification
OP-05 correction
OP-06 incomplete context / no irreversible claim
TECH-01 / TECH-02 / TECH-04 / TECH-05 pre-close semantics
TECH-06 multiple breakdown ambiguity
TECH-08 no final technical closure
TECH-09 role/context isolation
SES-01 active-session continuity
three-attempt recovery / human fallback
```

The Procedures refactor does not reduce acceptance criteria. It requires regression testing because the provider configuration changes materially.

After deterministic issues are closed, selected safety-sensitive native scenarios still require the agreed multi-run baseline.

---

## 11. Known contract contradiction before Ready

Merged A2/A3 still describe the earlier operator minimum ending:

```text
identity → model → installation → operation → problem description
```

A4 provider testing has accepted and implemented the refined operator contract with:

```text
element type + exact element reference
```

and explicit identity completeness.

This A2/A3 drift remains unresolved. It must be reconciled before A4 can be Ready. The Procedures refactor does not silently rewrite merged A2/A3.

---

## 12. Current stop point

```text
ISSUE: #12 OPEN
BRANCH: feat/a4-elevenlabs-sandbox-agent-v1
PR: #13 DRAFT
PROVIDER_AGENT: EXISTS
CURRENT_PROVIDER_RUNTIME: SYSTEM_PROMPT_V1
PROCEDURES_CANDIDATE: PREPARED_IN_REPOSITORY
PROCEDURES_PUBLISHED: NO
POST_REFACTOR_TESTS: NOT_RUN
A2_A3_SYNC: REQUIRED_BEFORE_READY
A4_OVERALL: NOT_PASS
READY: NO
MERGE: NO
```

Exact next action: review the repository candidate assets, then load/publish the short system prompt plus the two Free-form Procedures in the existing ElevenLabs sandbox agent. Stop before claiming any post-refactor PASS until new provider evidence exists.

No canonical-state update required.
