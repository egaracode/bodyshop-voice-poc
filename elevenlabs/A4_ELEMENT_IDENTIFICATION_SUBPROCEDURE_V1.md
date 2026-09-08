# A4 Free-form Sub-procedure — Element identification V1

> Repository candidate for the authorized A4 element-identification refinement. Create this as an ElevenLabs **Free-form Procedure without its own trigger** and reference it from `Operator breakdown` at the affected-element step. Do not treat this file as provider-runtime evidence until it is loaded/published and retested.

## Name

`Element identification`

## Trigger

None. This is a sub-procedure invoked only from `Operator breakdown`.

## Content

Identify the affected physical element clearly enough for the breakdown report.

Determine whether this type of element normally has an individual operational identifier.

If an individual identifier applies:
- ask for the exact identifier;
- do not complete element identification until it is clear and confirmed enough to rely on.

If the element does not have an individual identifier:
- do not invent or require one;
- use the element type plus available machine/equipment context to identify it sufficiently;
- continue to problem description once the affected element is clear.

Validated BODYSHOP examples for A4:

- `brida` → an individual reference applies; ask which brida, for example a value such as `Z14`.
- `antorcha` → an individual number may not exist; do not require a fabricated reference when the surrounding machine/equipment context identifies the affected torch clearly.

General rules:

- Distinguish a physical element from a process or technology. For example, a welding process is not itself the affected physical element if the caller identifies a physical component such as an antorcha.
- If the caller first gives a process/technology and then names a physical element, retain the physical element as the affected element.
- Do not assume every element type is numbered.
- Do not assume an unknown element type has no identifier either.
- For an element type not covered by a validated rule, ask only the minimum neutral clarification needed to identify the affected element clearly.
- Never fabricate identifier formats, numbering rules, parent equipment or technical relationships.
- Explicit uncertainty remains UNCONFIRMED and must be clarified before progression.
