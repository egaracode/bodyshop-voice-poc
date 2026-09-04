# A4 Operator Element Refinement V1

## 1. Status

```text
A4_OPERATOR_ELEMENT_REFINEMENT: ACCEPTED_BY_ALBERT
DATE: 2026-09-04
```

This document records the A4 product refinement discovered during live ElevenLabs sandbox testing.

It does not authorize SQL, Supabase, AI-Control-Workshop changes, production persistence, real operational data, or any state-changing integration.

---

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

---

## 3. Element semantics

Two separate element concepts are required.

### 3.1 Element type

`element_type` answers what kind of physical element is affected.

Examples using synthetic/generic categories:

```text
robot
motor
brida
pinza
```

### 3.2 Element reference

`element_ref` answers which exact element is affected.

Example synthetic reference:

```text
ST12
```

AI Control must not collapse `element_type` and `element_ref` into one slot when the exact element is still unresolved.

After learning the element type, the next question should adapt naturally:

```text
robot → "¿Qué robot es?"
motor → "¿Qué motor es?"
brida → "¿Qué brida es?"
```

The goal is natural guided speech, not a rigid generic questionnaire.

---

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

Rules:

- a problem narrative must not silently satisfy `operation`;
- an activity description must not silently satisfy `operation`;
- an operation-like value must not silently satisfy `installation`;
- a generic element type must not silently satisfy the exact element reference;
- ambiguous cross-slot answers require focused clarification rather than guessing.

---

## 5. Conceptual persistence hierarchy

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

This is a conversational/domain requirement only.

It is not evidence of an existing SQL schema and does not authorize SQL or persistence changes.

---

## 6. A4 dynamic-variable delta

A4 adds these safe provider variables:

```text
known_element_type
known_element_ref
```

Recommended A4 development defaults:

```text
known_element_type = UNKNOWN
known_element_ref  = UNKNOWN
```

No real element identifiers may be committed to this public repository.

---

## 7. Contract impact

Merged A2 currently defines the earlier minimum operator sequence:

```text
identity → model → installation → operation → problem description
```

Merged A3 `OP-02` / `OP-03` currently verify that earlier field set.

Albert's accepted A4 refinement adds `element_type` and `element_ref` between operation and problem description.

Therefore, before A4 can be considered Ready, repository documentation must be reconciled so that the active provider prompt, verification evidence and upstream A2/A3 operator contract do not contradict one another.

Until that synchronization is complete, this document is the explicit A4 delta for the active sandbox testing block.

---

## 8. Retest consequence

The next operator retest should preserve the guided style and verify this sequence:

```text
identity
model
installation
operation
element_type
element_ref
problem_description
```

PASS requires:

- each slot is retained correctly;
- AI Control asks only the next missing/uncertain slot;
- element type and exact element reference remain distinct;
- the final problem description does not overwrite another slot;
- no real BODYSHOP action is claimed.

Multi-slot behavior remains a separate capability: if several clear fields arrive in one utterance, they should be retained without forcing repetition.
