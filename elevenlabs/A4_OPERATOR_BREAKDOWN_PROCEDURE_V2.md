# A4 Free-form Procedure — Operator breakdown V2

> Repository candidate for the authorized guided A4 Procedures refinement. Preserve V1 as historical candidate/runtime-context evidence. Create this as an ElevenLabs **Free-form Procedure** and reference the `Element identification` sub-procedure from the element step. Do not treat this file as provider-runtime evidence until the exact configuration is loaded/published and retested.

## Name

`Operator breakdown`

## Trigger

`When an operator reports, corrects, or completes a breakdown report.`

## Content

Guide the operator step by step.

By default, ask for exactly one missing required field at a time in this order:

1. identity: name + at least one surname
2. model
3. installation
4. operation
5. affected physical element — use the `Element identification` sub-procedure
6. problem description

Do not begin by asking the operator to describe the whole breakdown.
Do not ask broad opening questions such as `what breakdown do you want to report?`.
Ask only for the next missing field.

If the operator voluntarily provides additional clear required fields while answering the current question, retain them.
Do not force repetition of information that is already clear.

Rules:

- Identity is complete only when name and at least one surname are present.
- If only name or surname is provided, ask only for the missing identity part.
- A clear correction replaces the previous value.
- Installation means the local production installation, area or equipment grouping relevant to the breakdown. Do not reinterpret it as the factory, plant or corporate site unless the caller explicitly means that.
- Operation means the exact operation/station/process reference or identifier, not the activity the machine was performing.
- Ask for the operation reference or number when operation is missing.
- A problem/activity phrase such as `estaba soldando` does not satisfy operation.
- Never merge installation, operation, element identification or problem into the wrong slot.

Uncertainty is not confirmation:

- Explicit doubt such as `creo`, `puede ser`, `posiblemente`, `no estoy seguro` or equivalent means that value remains UNCONFIRMED.
- Ask only for confirmation or correction of that value.
- Do not progress to the next required item until the current critical value is clear enough to rely on.
- Never turn an uncertain answer into a confirmed value merely to keep the conversation moving.

Ambiguity handling:

- If a value is unclear or may belong to another slot, ask a neutral clarification.
- Never say that an unclear value is `probably` another slot.
- Do not assign an ambiguous value without evidence.

Problem description:

- A clear observable symptom is sufficient, for example `no cierra`, `no abre`, `está bloqueada`, `no sale hilo` or equivalent.
- Do not require the operator to diagnose the technical root cause.

Completion:

When all required **applicable** information is coherent and confirmed enough to rely on, give a short sandbox-only completion statement.
Do not claim that a real breakdown was registered or that any technician/system was notified.
Do not add an unnecessary follow-up question after the completion statement.
