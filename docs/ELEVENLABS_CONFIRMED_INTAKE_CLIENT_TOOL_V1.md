# ElevenLabs Confirmed-Intake Client Tool V1

## 1. Status

```text
PARENT_VERTICAL: AI-Control-Workshop#432
ISSUE: bodyshop-voice-poc#36
TARGET_GATE: Gate 2 — Repository capability
BLOCK: FOUNDATION
PROVIDER_WRITES: FORBIDDEN
SUPABASE: FORBIDDEN
PRODUCTION: FORBIDDEN
```

This block defines the minimum repository-side Client Tool contract needed before a real ElevenLabs conversation can reach the existing BODYSHOP Voice Domain Adapter.

Visible result for Albert: none yet.

## 2. Root cause

Provider reconciliation is complete, but there is no runtime handoff from ElevenLabs into BODYSHOP.

Existing pieces are intentionally separate:

```text
real ElevenLabs AI Control
→ MISSING runtime handoff
→ provider-neutral confirmed observation
→ existing BODYSHOP Voice Domain Adapter
→ canonical result
```

A7 defines the provider-neutral concept and BODYSHOP already owns canonical resolution. This block does not duplicate either authority.

## 3. Current official ElevenLabs basis

Revalidated 2026-10-03 against current first-party documentation.

- Client Tools execute client-side functions and must be registered in application code.
- A Client Tool configured to wait for a response returns that response to the agent conversation context.
- Tool names and parameters in application code must match provider-side configuration.
- Server-side API calls belong in webhook tools rather than Client Tools.
- `POST /v1/convai/tools` creates a workspace tool. The current client-tool schema exposes `type`, `name`, `description`, `expects_response` and object parameters.
- Agent configuration exposes `conversation_config.agent.prompt.tool_ids`.
- Agent GET exposes `platform_settings.auth.enable_auth`.
- Public agents can connect with an agent id; private agents require a server-issued signed URL/token and the ElevenLabs API key must not be exposed client-side.

Official references:
- https://elevenlabs.io/docs/eleven-agents/customization/tools/client-tools
- https://elevenlabs.io/docs/eleven-agents/api-reference/tools/create
- https://elevenlabs.io/docs/eleven-agents/api-reference/agents/get
- https://elevenlabs.io/docs/eleven-agents/customization/personalization/overrides
- https://elevenlabs.io/docs/eleven-agents/customization/authentication
- https://elevenlabs.io/docs/eleven-agents/libraries/web-sockets
- https://elevenlabs.io/docs/eleven-agents/api-reference/conversations/get-signed-url

## 4. Tool identity

Versioned future Create Tool payload:

`elevenlabs/CONFIRMED_INTAKE_CLIENT_TOOL_V1.json`

Exact name:

`bodyshop_resolve_confirmed_intake`

The tool is a Client Tool with `expects_response=true`.

It may be called only after a complete read-back has been explicitly confirmed by the operator.

## 5. Provider-supplied input

Only confirmed values cross from the LLM/tool call:

```text
workshop
model
installation
operation
device
subdevice?
description
line_stopped
```

The LLM/provider does not own provenance.

The client creates:

```text
observation_id
source_channel = ELEVENLABS_WEB
occurred_at
recorded_at
confirmed_at
```

The resulting object is deliberately shaped to the canonical BODYSHOP `VoiceConfirmedIntakeObservationV1` boundary.

## 6. BODYSHOP result returned to the conversation

The Client Tool may return only these BODYSHOP status classes:

```text
RESOLVED
INCOMPLETE
AMBIGUOUS
NOT_FOUND
INVALID
```

For `RESOLVED`, the response sent back to ElevenLabs contains a bounded canonical display context.

It deliberately strips:

```text
reference_path_id
canonical object ids
provider resource ids
secrets
```

The browser/runtime may retain BODYSHOP-owned identity locally for evidence, but the provider does not need that identifier to speak the canonical result.

For fail-closed outcomes, only bounded reason/missing-field/candidate-count evidence is returned.

## 7. Authentication/access probe

`tools/elevenlabs_client_tool_contract_v1.py` performs authenticated GET-only inspection.

It classifies:

```text
auth.enable_auth = false
→ PUBLIC_AGENT_ID_ALLOWED

auth.enable_auth = true
→ SIGNED_URL_REQUIRED
```

It also records only SHA-256 fingerprints of agent/version/branch/tool resource ids.

No raw provider resource id is written to the evidence file.

## 8. Planned future provider write-set

The GET-only planner emits the intended staging sequence without executing it:

1. create a zero-live isolated provider branch from the exact current Main version;
2. GET-verify branch parent/live state;
3. create the workspace Client Tool from the versioned payload;
4. GET-verify the tool;
5. attach the new tool id to the isolated branch while retaining existing tool ids;
6. STOP on the behavioral expected-state decision described below.

No provider Main merge is part of this block.

## 9. Material compatibility finding

Gate 1 #433 requires:

```text
complete read-back
→ explicit operator confirmation
→ confirmed observation
```

Vertical Goal #432 also requires `line_stopped` in the bounded operator intake.

The current A5 expected System Prompt and `Operator breakdown` Procedure do not explicitly collect `line_stopped`, and the current Procedure does not explicitly perform the complete read-back/confirmation required by #433.

Therefore:

```text
CLIENT TOOL CONTRACT
= can be defined now

RELIABLE TOOL INVOCATION UNDER CURRENT A5 OPERATOR FLOW
= NOT YET PROVEN

provider behavior delta
= EXPECTED_STATE_DECISION_REQUIRED
```

This block does not silently rewrite A5.

Before provider staging writes, Albert must decide whether to accept the required expected-state delta that makes the current operator flow collect `line_stopped`, perform the complete read-back, obtain explicit confirmation and then invoke the Client Tool.

## 10. Local validation

Focused test:

```text
python -m unittest discover -s tests -p "test_elevenlabs_client_tool_contract_v1.py" -v
```

Full suite:

```text
python -m unittest discover -s tests -v
```

The tests cover:
- exact provider tool schema;
- required/optional parameter set;
- client-owned provenance;
- fail-closed malformed inputs;
- bounded agent-safe result projection;
- stripping internal canonical ids;
- public/private agent classification;
- sanitized write-set planning;
- GET-only network client.

## 11. Live GET-only execution

With `ELEVENLABS_API_KEY` set only in the local environment:

```text
python tools/elevenlabs_client_tool_contract_v1.py \
  --tool-config elevenlabs/CONFIRMED_INTAKE_CLIENT_TOOL_V1.json \
  --output <temporary-outside-repository-path>/elevenlabs-client-tool-plan-v1.json
```

The output is sanitized and may be reviewed without exposing the API key or raw provider ids.

## 12. Explicit exclusions

No:

```text
ElevenLabs POST / PATCH / DELETE
provider tool creation
provider tool attachment
provider Main merge
Supabase / Edge Function
SQL / RLS / RPC / Auth
Production
breakdown creation
technician assignment
lifecycle mutation
phone / SIP
Zello / F400
new dependency
workflow change
secret in repository/chat
```

## 13. Stop point

The block stops after repository validation, exact-head CI, authenticated GET-only auth/access evidence and sanitized write-set evidence.

The next decisions are reserved to Albert:

1. accept or reject the required provider expected-state delta;
2. authorize or reject the isolated provider staging write-set.

No canonical-state update required.
