# A4 ElevenLabs Sandbox Agent V1

## 1. Status

```text
A4_REPOSITORY_CONFIGURATION: GUIDED_PROCEDURES_REFINEMENT_PREPARED
ELEVENLABS_SANDBOX_AGENT: CREATED
CURRENT_PROVIDER_CONFIGURATION: MANUALLY_EVOLVED / NOT_EXACTLY_REPRODUCIBLE_FROM_REPO
LATEST_EXACT_TARGET: SYSTEM_PROMPT_V3 + OPERATOR_V2 + ELEMENT_IDENTIFICATION_V1 + TECHNICIAN_V1
LATEST_EXACT_TARGET_PROVIDER_LOAD: NOT_YET_DONE
LATEST_EXACT_TARGET_RUNTIME_TESTS: NOT_RUN
READY: NO
MERGE: NO
```

A4 is the provider-runtime block in the isolated `egaracode/bodyshop-voice-poc` laboratory. BODYSHOP semantics remain authoritative over provider behavior.

## 2. Repository baseline

```text
main = 2650665d60eb91b94eefb82cf13be85e93ac81d8
Issue = #12
branch = feat/a4-elevenlabs-sandbox-agent-v1
PR = #13 DRAFT
```

Current configuration assets:

- historical prompt: `elevenlabs/A4_AI_CONTROL_SYSTEM_PROMPT_V1.md`
- historical Procedures candidate: `elevenlabs/A4_AI_CONTROL_SYSTEM_PROMPT_V2.md`
- latest guided prompt target: `elevenlabs/A4_AI_CONTROL_SYSTEM_PROMPT_V3.md`
- historical operator candidate: `elevenlabs/A4_OPERATOR_BREAKDOWN_PROCEDURE_V1.md`
- latest guided operator target: `elevenlabs/A4_OPERATOR_BREAKDOWN_PROCEDURE_V2.md`
- latest element sub-procedure target: `elevenlabs/A4_ELEMENT_IDENTIFICATION_SUBPROCEDURE_V1.md`
- technician target: `elevenlabs/A4_TECHNICIAN_PRE_CLOSE_PROCEDURE_V1.md`

## 3. Safety boundary

A4 remains isolated sandbox only.

Do not connect Supabase, `AI-Control-Workshop`, BODYSHOP production runtime, corporate network, Zello, real phone/SIP, real operational webhook, real state-changing tool, real worker data or real operational identifiers.

The shared-walkie `addressed to Control` gate remains BODYSHOP-owned and external to ElevenLabs. F400/PTT/Zello/acoustic robustness remains A5-owned.

## 4. Authorized provider architecture

Albert authorized the internal A4 Procedures refactor and then the guided operator refinement:

```text
GLOBAL SYSTEM PROMPT V3
→ global role / sandbox / runtime context / safety
→ guided-first operator conversation
→ use known caller role when available

FREE-FORM PROCEDURE — Operator breakdown V2
→ one missing field at a time
→ identity → model → installation → operation → element → problem
→ retain clear extra fields without asking again
→ uncertainty / correction / slot boundaries

FREE-FORM SUB-PROCEDURE — Element identification V1
→ physical-element identification rules
→ reference required only when applicable
→ validated A4 examples: brida vs antorcha

FREE-FORM PROCEDURE — Technician pre-close V1
→ technician resolution / REQUEST_PRE_CLOSE semantics
```

No model, provisional voice, existing 10 dynamic variables, tool, integration, Supabase, phone/SIP/Zello, external activation ownership or BODYSHOP lifecycle authority change is authorized.

## 5. Guided operator contract

Default conversation structure:

```text
identity
→ model
→ installation
→ operation
→ affected physical element
→ exact element reference ONLY IF APPLICABLE
→ problem description
```

The agent controls the sequence. If the operator voluntarily provides additional clear required fields, retain them and skip redundant questions.

Definitions:

- `installation` = local production installation / area / equipment grouping relevant to the breakdown; do not reinterpret it as factory/corporate site unless explicitly meant.
- `operation` = exact operation/station/process reference or identifier; machine activity does not satisfy this slot.
- `problem` = observable symptom is sufficient; do not require root-cause diagnosis.
- element reference is conditional, not universal.

## 6. Element-identification boundary

`Element identification` is a sub-procedure with no independent trigger. It is invoked only by `Operator breakdown` at the affected-element step.

Current validated A4 examples:

```text
brida
→ individual identifier applies
→ ask for exact brida reference

antorcha
→ individual numbering may not exist
→ do not fabricate or require a number if equipment context identifies it clearly
```

Unknown element types must fail safe: ask only the minimum neutral clarification needed and never invent numbering rules or equipment relationships.

A future BODYSHOP Element Catalog / Knowledge Base may own a larger validated classification. It is not introduced in A4.

## 7. Dynamic-variable contract

Keep exactly the existing 10 variables:

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

If `caller_role` is already known, use it rather than asking again unless the runtime value is unavailable or genuinely ambiguous.

## 8. Evidence boundary after manual provider evolution

Previous manual provider tests remain historical evidence for the exact configuration actually present at that time.

At least one post-refactor test was executed while the `Operator breakdown` Procedure had been incompletely pasted in the provider UI. That run is **not valid evidence for the complete repository Procedure**.

A later guided run demonstrated useful behavior, but the provider configuration had already evolved manually and was not yet pinned byte-for-byte to a repository target. It therefore remains diagnostic evidence, not closure evidence.

No PASS may be claimed for V3 / Operator V2 / Element V1 until those exact assets are loaded, published together and retested.

## 9. Provider loading procedure — next exact target

In the existing ElevenLabs sandbox agent:

1. load `A4_AI_CONTROL_SYSTEM_PROMPT_V3.md` as the system prompt, excluding the repository-only header note;
2. replace `Operator breakdown` content with `A4_OPERATOR_BREAKDOWN_PROCEDURE_V2.md`;
3. create `Element identification` as a Free-form Procedure **without its own trigger**;
4. from the element step in `Operator breakdown`, reference/invoke `Element identification` using the provider Procedure reference UI;
5. keep `Technician pre-close` from `A4_TECHNICIAN_PRE_CLOSE_PROCEDURE_V1.md`;
6. keep Qwen, voice and existing 10 dynamic variables unchanged;
7. keep Knowledge Base, tools, integrations, phone/SIP/Zello and Supabase empty;
8. publish the exact configuration together;
9. restart A4 regression testing from this exact provider baseline.

## 10. Open contradiction before Ready

Merged A2/A3 still describe the earlier operator minimum ending:

```text
identity → model → installation → operation → problem description
```

A4 now refines this to conditional element identification. A2/A3 drift must be reconciled before Ready; A4 must not silently rewrite merged history.

## 11. Current stop point

```text
A4_ISSUE: #12 OPEN
A4_PR: #13 DRAFT
LATEST_REPOSITORY_TARGET: PREPARED
LATEST_PROVIDER_LOAD: NOT_YET_DONE
LATEST_RUNTIME_TESTS: NOT_RUN
CI: TO_REVALIDATE_ON_CURRENT_HEAD
A4_OVERALL: NOT_PASS
READY: NO
MERGE: NO
```

No canonical-state update required. Do not start A5.