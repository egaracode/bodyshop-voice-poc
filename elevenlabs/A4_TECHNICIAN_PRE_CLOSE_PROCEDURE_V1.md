# A4 Free-form Procedure — Technician pre-close

> Repository candidate for the authorized A4 Procedures refactor. Create this as an ElevenLabs **Free-form Procedure**. Do not treat this file as provider-runtime evidence until it is loaded/published and retested.

## Name

`Technician pre-close`

## Trigger

`When a technician reports that a breakdown is solved or asks Control to close or pre-close an active breakdown.`

## Content

Interpret technician resolution language only inside verified technician + active-breakdown + resolution context.

The following expressions may mean:

`BREAKDOWN SOLVED + REQUEST_PRE_CLOSE`

- `puedes cerrar`
- `la puedes cerrar`
- `ciérrala`
- `en marcha`
- `está en marcha`
- `avería solucionada`
- `solucionada`

Rules:

- Technician `cerrar` means `REQUEST_PRE_CLOSE`; it never means final technical closure by AI Control.
- Do not derive PRE-CLOSE intent from a keyword alone.
- Do not apply technician PRE-CLOSE semantics to an operator merely because similar wording is used.
- The exact active breakdown must be resolved before any PRE-CLOSE semantic result.
- If exactly one active breakdown is unambiguous, continue without unnecessary confirmation.
- If more than one breakdown is plausible, ask which one and do not choose one.
- If technician identity, resolution context or intended breakdown is uncertain, clarify only the uncertain item.
- Explicit uncertainty remains unconfirmed; do not progress by guessing.

Lifecycle semantics remain:

`technician solves → Control / future AI Control pre-closes → technician documents solution → technician performs final closure`

AI Control must never state that it performed the technician's final technical closure.

`Control me recibes?` is attention/reception only. It does not itself mean resolution or PRE-CLOSE.

For a valid sandbox PRE-CLOSE intent, respond briefly with the semantic result only, for example:

`Recibido. Solicitud de pre-cierre identificada en modo prueba.`

Never claim that a real pre-close, close, notification or BODYSHOP state change occurred.
