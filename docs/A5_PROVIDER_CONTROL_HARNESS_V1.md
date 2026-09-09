# A5 Provider Control Harness V1

## 1. Status

```text
ISSUE: #14
PHASE: 1 READ_ONLY
PROVIDER_WRITES: FORBIDDEN
PUBLISH: FORBIDDEN
VERSIONING_MUTATION: FORBIDDEN
```

This document defines the A5 read-only control path for the isolated ElevenLabs `AI Control` sandbox.

## 2. Authority

A5 resolves the A4 reproducibility problem by separating semantic authority, expected provider configuration and historical evidence:

```text
A2 + A3
→ semantic authority

A5_EXPECTED_PROVIDER_CONFIGURATION_V1
→ provider configuration authority

PR #13 / head 1de7cf9cda806af7b355e3228585cb115347c049
→ historical evidence only
```

No A4 value is inherited automatically when it conflicts with the A5 authority decision.

Machine-readable expected state:

`elevenlabs/A5_EXPECTED_PROVIDER_CONFIGURATION_V1.json`

## 3. Expected A5 operator architecture

The operator path is expected to use one ElevenLabs Structured Procedure with ordered collection:

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

The conditional element-reference rule is preserved:

- require the exact individual reference only when that physical element has an applicable individual identifier;
- do not fabricate or universally require a reference;
- unknown applicability fails safe rather than inventing workshop relationships.

The previous A4 Free-form operator Procedure and element sub-procedure are not A5 authority. If they remain present in the provider as additional Procedures, the harness classifies them as `DRIFT`.

The technician pre-close semantics remain derived from A2/A3: technician `cerrar` or equivalent maps to `REQUEST_PRE_CLOSE` in the correct exact-breakdown context, never final technical closure by AI Control.

## 4. Initially preserved provider choices

A5 initially preserves the non-conflicting A4 evidence explicitly accepted by Albert:

```text
LLM: Qwen3.5-397B-A17B
VOICE DISPLAY NAME: Eric
DYNAMIC VARIABLES: exactly 10
```

Expected variable names:

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

Variable values/defaults are deliberately not persisted by the harness because they may contain runtime or operational data. A5 V1 compares the variable-name set.

The expected JSON reserves `voice.id_sha256` but leaves it `null` initially because no exact provider voice resource identifier is authoritative in GitHub. The harness compares the resolved display name (`Eric`) but reports `agent.voice.id_sha256 = UNVERIFIABLE` until a sanitized exact fingerprint is deliberately pinned. Therefore a full `NO_DRIFT` result cannot be claimed solely from a matching display name.

## 5. Official provider interfaces revalidated 2026-09-09

A5 uses only documented GET interfaces:

```text
GET /v1/convai/agents
GET /v1/convai/agents/{agent_id}
GET /v1/convai/agents/{agent_id}/branches/{branch_id}/procedures
GET /v1/convai/agents/{agent_id}/branches/{branch_id}/procedures/{procedure_id}
GET /v1/voices/{voice_id}
```

Official documentation establishes that:

- List Agents can search/list agent metadata;
- Get Agent exposes effective conversation configuration and version/branch identifiers where available;
- List Procedures exposes Procedure ID, version, name, type, trigger and draft status;
- Get Procedure exposes Procedure name, type, trigger and full content;
- Structured Procedure content is a JSON-encoded ordered `steps` document;
- Structured Procedure `Ask` waits for an appropriate user response and `branch` represents If/else branching;
- versioning is opt-in and, once enabled, cannot be disabled.

Official references:

- https://elevenlabs.io/docs/api-reference/authentication
- https://elevenlabs.io/docs/api-reference/agents/list
- https://elevenlabs.io/docs/api-reference/agents/get
- https://elevenlabs.io/docs/api-reference/agents/procedures/list
- https://elevenlabs.io/docs/api-reference/agents/procedures/get
- https://elevenlabs.io/docs/eleven-agents/customization/procedures
- https://elevenlabs.io/docs/eleven-agents/customization/procedures/structured-procedures
- https://elevenlabs.io/docs/eleven-agents/operate/versioning
- https://elevenlabs.io/docs/api-reference/voices/get

## 6. Authentication boundary

ElevenLabs authenticates API requests using an API key in the `xi-api-key` header.

A5 rules:

```text
API KEY
→ local environment only
→ never command-line argument
→ never repository
→ never chat
→ never output report
```

Use a dedicated restricted key where the ElevenLabs account UI permits the minimum required scope. ElevenLabs documents scope restrictions, quota restrictions and optional IP allowlisting for API keys.

The harness reads only `ELEVENLABS_API_KEY` from the local process environment.

If secure authentication cannot be provided without exposing the key, STOP.

## 7. Read-only implementation

Implementation:

`tools/a5_provider_control.py`

The implementation uses only Python standard-library modules. No dependency or workflow change is required.

Provider access is constructed through GET requests only. Endpoint paths must match one of the exact A5 read shapes; paths for drafts, compile, settings or mutation surfaces are rejected before any network call.

No POST, PATCH, PUT, DELETE, Publish, deployment, versioning enablement or provider branch mutation path exists in A5 V1.

Provider HTTP error bodies are never echoed into logs/output.

Agent selection fails closed:

```text
exact non-archived name == "AI Control"

0 matches
→ ERROR

>1 exact matches
→ ERROR

exactly 1
→ continue read-only
```

Provider resource IDs are used only in memory to address subsequent GET endpoints and are not written raw to the sanitized report.

## 8. Procedure/versioning boundary

The official Procedures endpoints require `branch_id` in their path.

A5 must never enable versioning merely to obtain it.

```text
branch_id available
→ List/Get Procedures

branch_id unavailable
→ Procedures = UNVERIFIABLE
→ do not mutate provider
```

The same rule applies to version metadata: missing provider metadata is reported rather than invented.

## 9. Normalization and comparison

Expected vs actual comparison uses:

```text
agent name                 exact
language                   exact
First Message              exact after line-ending normalization
System Prompt              exact after line-ending normalization
LLM                        exact
resolved voice name        exact
voice resource fingerprint exact when pinned; otherwise UNVERIFIABLE
10 variable names          exact set
Procedure set              exact by Procedure name
Procedure type             exact
Procedure trigger          exact after line-ending normalization
Free-form content          exact after line-ending normalization
Structured content         canonical JSON
```

Every field produces one of:

```text
NO_DRIFT
DRIFT
UNVERIFIABLE
```

Unexpected provider Procedures are `DRIFT`.

An expected Procedure missing from provider is `DRIFT`.

A Procedure with provider-reported unpublished draft changes is `DRIFT`.

Overall result precedence:

```text
any DRIFT
→ DRIFT

else any UNVERIFIABLE
→ UNVERIFIABLE

else
→ NO_DRIFT
```

## 10. Sanitized evidence

The harness intentionally does not emit raw:

- API keys;
- agent IDs;
- Procedure IDs;
- voice IDs;
- prompt text;
- First Message text;
- Procedure content;
- dynamic-variable values;
- provider HTTP error bodies;
- raw provider responses.

Textual provider content and resource identities needed for reproducible comparison are represented by SHA-256 fingerprints, plus lengths where useful.

The report may contain non-secret semantic metadata such as agent name, language, LLM, resolved voice display name, dynamic-variable names, Procedure names/types and Boolean draft/version-presence indicators.

Do not commit a report until it has been manually reviewed for the public-laboratory boundary.

## 11. Local execution

With the API key already loaded securely into the local `ELEVENLABS_API_KEY` environment variable:

```text
python tools/a5_provider_control.py \
  --expected elevenlabs/A5_EXPECTED_PROVIDER_CONFIGURATION_V1.json \
  --output <temporary-outside-repository-path>/a5-provider-report.json
```

On PowerShell, keep the output outside the repository, for example under `$env:TEMP`.

Never paste the key or a raw provider response into GitHub or ChatGPT.

Exit codes:

```text
0 → NO_DRIFT
1 → DRIFT or UNVERIFIABLE
2 → harness/auth/provider read error
```

## 12. Validation

Repository tests:

```text
python -m unittest discover -s tests -v
```

Current deterministic coverage verifies:

- fully pinned exact fixture → `NO_DRIFT`;
- unpinned exact voice identity → `UNVERIFIABLE` rather than false `NO_DRIFT`;
- material model/Procedure-type difference → `DRIFT`;
- missing Procedure branch metadata → `UNVERIFIABLE`;
- sanitized snapshot excludes raw prompt/First Message and provider resource IDs;
- endpoint allowlist accepts only the five required A5 GET endpoint shapes and rejects adjacent draft/compile/settings paths.

No live ElevenLabs call is represented by those unit tests.

## 13. Current official-risk finding: Structured Procedure + Qwen

Current official ElevenLabs documentation defines Structured Procedures as ordered typed steps. It also states that forced internal tool choice used for procedure transitions/completion is supported by major OpenAI, Anthropic, Gemini and Grok model families, while other models/custom providers may not guarantee those transitions.

A5 preserves Qwen because Albert explicitly authorized that preservation.

This produces the following classification:

```text
A5 READ_ONLY INSPECTION: NOT BLOCKED

FUTURE STRUCTURED-PROCEDURE RUNTIME RELIABILITY WITH QWEN:
EVIDENCE REQUIRED
```

Do not silently switch the model in A5 Phase 1.

## 14. Not authorized

```text
ELEVENLABS WRITE
ELEVENLABS PUBLISH
ENABLE VERSIONING
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
```

## 15. Current stop point

A5 repository-side reader, expected state and deterministic comparison can be prepared and tested without a provider secret.

A live authenticated provider read requires execution in an environment where the ElevenLabs key is available securely. If that execution is not available, the provider snapshot and actual `DRIFT / NO_DRIFT / UNVERIFIABLE` result remain `NOT_RUN`; they must not be guessed.

No canonical-state update required.
