# ElevenLabs Provider Compatibility Probe V2

## 1. Purpose

This document defines the current-schema, read-only provider-inspection boundary used by BODYSHOP Voice PoC after ElevenLabs changed the machine representation of Procedures.

It belongs to:

- `egaracode/bodyshop-voice-poc#32`;
- parent Vertical Goal `egaracode/AI-Control-Workshop#432`.

Historical A5 V1 remains historical evidence and is intentionally unchanged.

## 2. Why V2 exists

Historical A5 expected a Procedure machine type named:

```text
structured
```

Current ElevenLabs official API documentation, revalidated on 2026-10-02, exposes the Procedure API type enum as:

```text
free_form
deterministic
folder
```

Current ElevenLabs product documentation still uses the human-facing categories:

```text
free-form procedure
structured procedure
```

and documents structured Procedure content as JSON with a top-level `steps` array.

Therefore V2 must not silently treat a historical type label difference as provider configuration drift.

## 3. Current official source basis

Revalidated 2026-10-02:

- List Agents:
  https://elevenlabs.io/docs/api-reference/agents/list
- Get Agent:
  https://elevenlabs.io/docs/api-reference/agents/get
- List Agent Branches:
  https://elevenlabs.io/docs/api-reference/agents/branches/list
- List Procedures:
  https://elevenlabs.io/docs/api-reference/agents/procedures/list
- Get Procedure:
  https://elevenlabs.io/docs/api-reference/agents/procedures/get
- Procedures:
  https://elevenlabs.io/docs/eleven-agents/customization/procedures
- Structured Procedures:
  https://elevenlabs.io/docs/eleven-agents/customization/procedures/structured-procedures
- Get Voice:
  https://elevenlabs.io/docs/api-reference/voices/get

Current documented facts used by V2:

- agent / branch / Procedure / voice inspection is available through GET endpoints;
- Procedure API type values are `free_form | deterministic | folder`;
- List Procedures exposes `has_draft`;
- Get Procedure exposes raw type, trigger and content;
- a structured Procedure body is JSON containing a `steps` array;
- Procedure type cannot be changed after creation.

## 4. Core rule

V2 separates:

```text
raw provider representation
from
content shape
from
future semantic/drift interpretation
```

It does not perform:

```text
deterministic → structured
```

or any other implicit provider-label translation.

Instead it records:

```text
raw_api_type
content_shape
```

separately.

## 5. Content-shape classification

V2 uses these values:

```text
JSON_STEPS
TEXT
INVALID_JSON_STEPS
EMPTY
```

Definitions:

- `JSON_STEPS`: content parses as JSON object with a top-level `steps` list;
- `TEXT`: content is non-JSON text;
- `INVALID_JSON_STEPS`: content parses as JSON but does not have the required `steps` list shape;
- `EMPTY`: zero-length content.

Compatibility warnings are evidence only and are not DRIFT verdicts.

Examples:

```text
deterministic + non-JSON_STEPS
→ DETERMINISTIC_WITHOUT_JSON_STEPS

free_form + JSON_STEPS
→ FREE_FORM_WITH_JSON_STEPS
```

## 6. Provider access boundary

Implementation:

`tools/elevenlabs_provider_compat_v2.py`

Network behavior is GET-only.

Allowed methods implemented:

```text
GET /v1/convai/agents
GET /v1/convai/agents/{agent_id}
GET /v1/convai/agents/{agent_id}/branches
GET /v1/convai/agents/{agent_id}/branches/{branch_id}/procedures
GET /v1/convai/agents/{agent_id}/branches/{branch_id}/procedures/{procedure_id}
GET /v1/voices/{voice_id}
```

No POST, PATCH, PUT or DELETE method exists in this probe.

No Publish, provider branch/version mutation or configuration change is performed.

## 7. Authentication

The API key is read only from:

`ELEVENLABS_API_KEY`

Rules:

```text
local environment only
never CLI argument
never repository
never chat
never generated report
```

STOP if secure local authentication is unavailable.

## 8. Fail-closed behavior

The probe fails instead of guessing when:

- there is not exactly one non-archived agent named `AI Control`;
- the provider does not expose a current `branch_id`;
- the selected branch cannot be found exactly once in the current branch list;
- Procedure listing has malformed objects or missing IDs;
- Procedure names are duplicated;
- the provider returns a Procedure type outside the current documented enum;
- required current API structures are malformed.

Unknown provider evolution must be treated as compatibility evidence requiring review, not silently normalized.

## 9. Sanitized output

The generated snapshot contains only:

- agent name, language and LLM id;
- hashes and lengths for First Message/System Prompt;
- exact dynamic-variable names;
- hashed agent/branch/version/voice/Procedure identifiers;
- branch metadata that does not reveal raw IDs;
- voice display name and TTS settings;
- Procedure name;
- raw current API type;
- content shape;
- trigger/content hashes and lengths;
- draft/version-presence flags;
- compatibility warnings.

It does not emit raw:

- API key;
- agent/branch/version/voice/Procedure IDs;
- First Message;
- System Prompt;
- Procedure trigger;
- Procedure body.

## 10. No DRIFT verdict in V2 probe

The V2 compatibility probe deliberately emits:

```text
drift_verdict = NOT_EMITTED_BY_V2_COMPATIBILITY_PROBE
```

This prevents a historical schema label from becoming a false current provider-drift conclusion.

After one authenticated GET-only V2 read, the sanitized snapshot must be compared with:

- A2/A3 semantic authority;
- A5 V1 expected configuration;
- current official ElevenLabs schema.

Only then may the project classify:

```text
real provider drift
API/schema evolution
unverifiable field
current compatible state
```

## 11. Local validation

Repository tests:

```text
python -m unittest discover -s tests -v
```

Focused test:

```text
python -m unittest tests.test_elevenlabs_provider_compat_v2 -v
```

The tests prove at minimum:

- current API enum is explicitly bounded;
- `deterministic` remains raw `deterministic`;
- JSON `steps` shape is classified independently;
- raw IDs/prompt/Procedure content are absent from sanitized output;
- unknown Procedure API types fail closed;
- duplicate names fail closed;
- missing current branch fails closed;
- the client exposes no provider mutation method.

## 12. Authenticated execution

After repository validation, run from the exact candidate head with the API key already present securely in the local environment:

```text
python tools/elevenlabs_provider_compat_v2.py --output <temporary-path-outside-repository>/elevenlabs-provider-compat-v2.json
```

The output path must be outside the repository.

After the read:

1. inspect the sanitized report;
2. remove `ELEVENLABS_API_KEY` from the local session;
3. record only safe evidence;
4. classify current provider state;
5. STOP before any provider correction.

## 13. Explicit exclusions

This V2 block does not authorize:

- ElevenLabs write;
- Publish;
- provider branch/version mutation;
- expected-state rewrite;
- Supabase or Edge Function;
- BODYSHOP runtime integration;
- Zello/F400;
- phone/SIP;
- Production;
- secrets in repository/chat;
- workflow or dependency changes.

## 14. Stop point

```text
repository capability
→ local tests
→ Draft PR
→ authenticated GET-only current-provider snapshot
→ fresh classification
→ STOP before provider correction
```

Albert retains Ready and merge authority.
