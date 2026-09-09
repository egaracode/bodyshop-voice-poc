# A5 Provider Control Harness V1

## 1. Status

```text
ISSUE: #14
PHASE: 1 READ_ONLY
PROVIDER_WRITES: FORBIDDEN
PUBLISH: FORBIDDEN
VERSIONING_MUTATION: FORBIDDEN
PR: #15 DRAFT
```

A5 establishes a reproducible read-only inspection path for the isolated ElevenLabs `AI Control` sandbox.

## 2. Authority

```text
A2 + A3
→ semantic authority

A5_EXPECTED_PROVIDER_CONFIGURATION_V1
→ provider-configuration authority

PR #13 / head 1de7cf9cda806af7b355e3228585cb115347c049
→ historical evidence only
```

No A4 value is inherited automatically when it conflicts with the A5 authority decision.

Machine-readable expected state:

`elevenlabs/A5_EXPECTED_PROVIDER_CONFIGURATION_V1.json`

## 3. Expected operator architecture

One Structured Procedure owns the operator collection sequence:

```text
identity
→ model
→ installation
→ operation
→ affected element/device
→ exact individual element reference only when applicable
→ problem/breakdown
→ sandbox-only summary
```

The conditional reference rule is mandatory: do not fabricate or universally require an individual element reference. Unknown applicability fails safe.

The former A4 Free-form operator Procedure and element sub-procedure are not A5 authority. If present as additional provider Procedures, they are `DRIFT`.

Technician `cerrar` or equivalent remains `REQUEST_PRE_CLOSE` in the correct technician/exact-breakdown context, never final technical closure by AI Control.

## 4. Initially preserved choices

Albert authorized A5 to preserve initially:

```text
LLM family/model: Qwen3.5-397B-A17B
ElevenLabs API LLM id: qwen35-397b-a17b
voice display name: Eric - Smooth, Trustworthy
voice resource fingerprint: 1e0c5d7793b1296cb88ddddf08040c9e901c241640ff7e88fcad1c31c7392bc9
dynamic-variable names: exactly 10
```

The API identifier is the machine-comparison value. ElevenLabs documents `qwen35-397b-a17b` as the API LLM option for the human-facing Qwen3.5-397B-A17B model, so those two spellings do not represent a model change.

For the current PoC, Albert authorizes `Eric - Smooth, Trustworthy` as the exact temporary provider voice corresponding to the earlier shorthand `Eric`. The raw provider `voice_id` is not committed; its SHA-256 fingerprint is the repository comparison authority. This is not the final production voice choice. Spanish-native voice evaluation is deferred to a later block.

The exact First Message was not specified by A2/A3 or the A5 authority decision. Therefore V1 deliberately leaves it unpinned and reports it `UNVERIFIABLE` while still reading and fingerprinting the provider value.

Likewise, provider settings that are officially exposed but were not explicitly pinned are read and normalized without being silently invented:

```text
LLM temperature
LLM max_tokens
TTS model_id
TTS stability
TTS speed
TTS similarity_boost
```

A null expected value means `UNVERIFIABLE`, not `NO_DRIFT`.

## 5. Dynamic variables

Expected names:

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

The harness compares the exact name set. Runtime/default values are not emitted because this public laboratory must not leak operational or personal data.

## 6. Official read interfaces revalidated 2026-09-09

A5 uses only documented GET operations:

```text
GET /v1/convai/agents
GET /v1/convai/agents/{agent_id}
GET /v1/convai/agents/{agent_id}/branches/{branch_id}/procedures
GET /v1/convai/agents/{agent_id}/branches/{branch_id}/procedures/{procedure_id}
GET /v1/voices/{voice_id}
```

Current official documentation confirms:

- Get Agent exposes conversation configuration including First Message, language, prompt/model parameters, dynamic-variable placeholders, TTS configuration and branch/version metadata where available.
- List Procedures exposes procedure metadata and draft state.
- Get Procedure exposes name, type, trigger and content.
- Structured Procedure content is JSON-encoded with a `steps` array.
- `ask`, `tell`, `say` and `branch` are current documented step types; `branch` uses ordered condition arms plus optional fallback.
- Structured Procedures rely on forced internal tool choice for transitions/completion; major OpenAI, Anthropic, Gemini and Grok families are explicitly supported, while other models may need runtime verification.
- The current Create Agent and Update Agent API schemas mark `enable_versioning` / `enable_versioning_if_not_enabled` deprecated and ignored, stating that all agents are versioned.

There is a current official-documentation contradiction: the separate Agent Versioning guide still describes versioning as opt-in, while the June 1, 2026 changelog and current Create/Update Agent API schemas state that all agents are versioned and the enable-versioning parameters are ignored. For A5 API behavior, the current endpoint schemas plus dated changelog are treated as the stronger evidence. A5 performs no provider version or branch mutation in either interpretation.

Official references:

- https://elevenlabs.io/docs/api-reference/authentication
- https://elevenlabs.io/docs/api-reference/agents/list
- https://elevenlabs.io/docs/api-reference/agents/get
- https://elevenlabs.io/docs/api-reference/agents/create
- https://elevenlabs.io/docs/api-reference/agents/update
- https://elevenlabs.io/docs/api-reference/agents/procedures/list
- https://elevenlabs.io/docs/api-reference/agents/procedures/get
- https://elevenlabs.io/docs/eleven-agents/customization/procedures/structured-procedures
- https://elevenlabs.io/docs/eleven-agents/operate/versioning
- https://elevenlabs.io/docs/changelog/2026/6/1
- https://elevenlabs.io/docs/api-reference/voices/get
- https://elevenlabs.io/docs/changelog/2026/5/18

The legacy `voices/get-all` documentation is not used by A5.

## 7. Authentication boundary

The harness reads the API key only from:

`ELEVENLABS_API_KEY`

Rules:

```text
local environment only
never CLI argument
never repository
never chat
never output report
```

Use a dedicated restricted ElevenLabs key where account controls allow the minimum required scope.

STOP if secure authentication is not available.

## 8. Read-only implementation

Implementation:

`tools/a5_provider_control.py`

Properties:

- Python standard library only;
- only GET network operations;
- endpoint construction is isolated in five explicit client methods;
- provider IDs are validated before path construction;
- adjacent mutation/draft tokens are rejected where relevant;
- no POST/PATCH/PUT/DELETE;
- no Publish;
- no provider version or branch mutation;
- HTTP error bodies are never echoed.

Agent selection fails closed unless there is exactly one non-archived agent named `AI Control`.

## 9. Procedure/version boundary

Procedures require a provider `branch_id`.

```text
branch_id available
→ List/Get Procedures

branch_id unavailable
→ Procedures = UNVERIFIABLE
→ no provider mutation
```

A5 does not call deprecated version-enablement parameters and never creates, publishes, merges, deploys or otherwise mutates provider version/branch state merely to obtain read metadata.

## 10. Normalization and verdicts

Comparison covers:

```text
agent name
language
First Message
System Prompt
LLM id
LLM temperature
LLM max_tokens
voice display name
voice resource fingerprint
TTS model_id
TTS stability
TTS speed
TTS similarity_boost
10 dynamic-variable names
Procedure set
Procedure type
Procedure trigger
Procedure content
Procedure draft state
```

Text uses normalized line endings. Structured content uses canonical JSON.

Field verdicts:

```text
NO_DRIFT
DRIFT
UNVERIFIABLE
```

Overall precedence:

```text
any DRIFT → DRIFT
else any UNVERIFIABLE → UNVERIFIABLE
else → NO_DRIFT
```

Unexpected Procedures are `DRIFT`; missing expected Procedures are `DRIFT`; unpublished Procedure draft state is `DRIFT`.

## 11. Sanitized evidence

The report never emits raw:

- API keys;
- agent/Procedure/voice IDs;
- First Message;
- System Prompt;
- Procedure content;
- dynamic-variable values;
- provider HTTP error bodies;
- raw provider responses.

Text and resource identities are represented with SHA-256 fingerprints where needed.

Do not commit a generated report until it has been manually reviewed against the public-laboratory data boundary.

## 12. Local execution

With `ELEVENLABS_API_KEY` already set securely in the local environment:

```text
python tools/a5_provider_control.py \
  --expected elevenlabs/A5_EXPECTED_PROVIDER_CONFIGURATION_V1.json \
  --output <temporary-outside-repository-path>/a5-provider-report.json
```

Use an output path outside the repository.

Exit codes:

```text
0 → NO_DRIFT
1 → DRIFT or UNVERIFIABLE
2 → harness/auth/provider read error
```

## 13. Validation

Repository tests:

```text
python -m unittest discover -s tests -v
```

Deterministic coverage includes:

- fully pinned exact fixture → `NO_DRIFT`;
- unpinned provider fields → `UNVERIFIABLE`;
- material model/Procedure drift → `DRIFT`;
- missing Procedure branch metadata → `UNVERIFIABLE`;
- sanitized output excludes raw sensitive/provider content;
- reserved adjacent endpoint tokens are rejected;
- malformed Structured Procedure content is rejected;
- outer whitespace remains material under exact text comparison;
- duplicate Procedure names fail closed instead of being silently collapsed.

These tests do not constitute a live ElevenLabs read.

## 14. Known runtime risk

A5 READ-ONLY inspection is not blocked by Qwen.

Future runtime reliance on Structured Procedure transitions with Qwen remains:

```text
EVIDENCE REQUIRED
```

A5 Phase 1 must not silently change model.

## 15. Not authorized

```text
ELEVENLABS WRITE
ELEVENLABS PUBLISH
PROVIDER VERSION / BRANCH MUTATION
CREATE/MERGE/DEPLOY PROVIDER BRANCH
CONTROLLED CONFIG MUTATION
PHONE / SIP
F400
ZELLO
SUPABASE
AI-CONTROL-WORKSHOP CHANGE
PRODUCTION / CORPORATE NETWORK
DEPENDENCY CHANGE
CI/WORKFLOW CHANGE
SECRET IN CHAT OR REPOSITORY
READY / MERGE
```

## 16. Current stop point

A5 Phase 1 repository-side harness is implemented and validated.

Exact validated GitHub head:

`ae1c23cb526b168004b84a8e8a7090d61e12d8c9`

Repository validation before this final-audit correction:

```text
8 tests / 8 PASS
CI: NOT CONFIGURED / NOT APPLICABLE
```

Authenticated LIVE read-only comparison was executed on that exact head and returned:

```text
A5_PROVIDER_RESULT: DRIFT
```

Confirmed aligned:

```text
agent.name
agent.language
agent.llm.id
agent.dynamic_variable_names
procedures.Technician pre-close.type
```

Material provider drift remains in System Prompt, temporary voice resource and expected Procedure configuration.

Final audit identified two repository-side exactness corrections required before Ready:

exact text comparison must not strip outer whitespace, and duplicate Procedure names must fail closed.

After those corrections change the head, repository tests and one authenticated READ-ONLY provider comparison must be repeated against the new exact SHA.

No provider write, Publish, Ready or merge is authorized by Phase 1.

No canonical-state update required.
