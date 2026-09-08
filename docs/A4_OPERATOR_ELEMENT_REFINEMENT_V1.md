# A4 Operator Element Refinement V1

## 1. Status

```text
A4_OPERATOR_ELEMENT_REFINEMENT: ACCEPTED_BY_ALBERT
A4_PROCEDURES_REFACTOR: AUTHORIZED
```

This document records the A4 product refinement discovered during live ElevenLabs sandbox testing.

It does not authorize SQL, Supabase, AI-Control-Workshop changes, production persistence, real operational data, or any state-changing integration.

## 2. Accepted operator sequence

AI Control should guide the operator through this preferred sequence:

```text
identity
→ model
→ installation
→ operation
→ element type
→ element reference
→ problem description
```

The conversation remains guided and bounded. Asking the fields one by one is preferred because it reduces ambiguity and helps preserve data quality.

If the operator spontaneously supplies several clear fields in one utterance, AI Control should retain them and ask only for what is still missing or uncertain.

## 3. Element semantics

`element_type` answers what kind of physical element is affected, for example robot, motor, brida or pinza.

`element_ref` answers which exact element is affected, using a synthetic reference such as `ST12` in public tests.

AI Control must not collapse `element_type` and `element_ref` into one slot when the exact element is still unresolved.

After learning the element type, the next question should adapt naturally, for example `¿Qué robot es?`, `¿Qué motor es?` or `¿Qué brida es?`.

## 4. Slot boundary

The operator slots are distinct:

```text
model
installation
operation
element_type
element_ref
problem_description
```

A problem narrative must not silently satisfy `operation`; an activity description must not silently satisfy `operation`; an operation-like value must not silently satisfy `installation`; a generic element type must not silently satisfy the exact element reference; ambiguous cross-slot answers require focused clarification rather than guessing.

## 5. Explicit uncertainty invariant

A value being heard does not make it confirmed.

```text
VALUE HEARD != VALUE CONFIRMED
explicit doubt → UNCONFIRMED → clarify only that value → do not progress
```

Expressions semantically equivalent to `creo`, `puede ser`, `posiblemente` or `no estoy seguro` must keep the current critical value unresolved until the caller confirms or corrects it.

This is a domain-quality rule, not a phrase-specific patch.

## 6. Conceptual persistence hierarchy

The conversational data should be compatible with the future conceptual workshop hierarchy:

```text
MODEL
└─ INSTALLATION
   └─ OPERATION
      └─ ELEMENT
         ├─ type
         ├─ reference
         └─ problem
```

This is a conversational/domain requirement only. It is not evidence of an existing SQL schema and does not authorize SQL or persistence changes.

## 7. ElevenLabs state handling

`element_type` and `element_ref` are collected during the conversation and do not need to be custom dynamic variables for A4.

The existing 10 ElevenLabs dynamic variables remain unchanged and are used only for session/runtime context.

The operator-provided element type/reference may remain in ordinary conversation context during A4 testing.

## 8. Procedures architecture

The accepted operator task-specific rules now live in the repository candidate:

`elevenlabs/A4_OPERATOR_BREAKDOWN_PROCEDURE_V1.md`

The global agent rules live in:

`elevenlabs/A4_AI_CONTROL_SYSTEM_PROMPT_V2.md`

This refactor does not change BODYSHOP semantic authority and is not provider-runtime evidence until V2 + Procedures are loaded/published and retested.

## 9. Contract impact

Merged A2 currently defines the earlier minimum operator sequence `identity → model → installation → operation → problem description` and merged A3 `OP-02` / `OP-03` currently verify that earlier field set.

Albert's accepted A4 refinement adds `element_type` and `element_ref` between operation and problem description and clarifies full identity and explicit-uncertainty handling.

Before A4 can be considered Ready, repository documentation must be reconciled so the active provider configuration, verification evidence and upstream A2/A3 operator contract do not contradict one another.

## 10. Retest consequence

After publishing V2 + Procedures, the operator retest should verify:

```text
identity
model
installation
operation
element_type
element_ref
problem_description
```

PASS requires each clear slot retained correctly, only the next missing/uncertain slot requested, explicit uncertainty left unresolved, element type and exact reference kept distinct, corrections replacing prior values safely, spontaneous multi-slot information retained, and no real BODYSHOP action claimed.
