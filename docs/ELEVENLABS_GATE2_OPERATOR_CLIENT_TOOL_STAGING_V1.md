> **CURRENT AUTHORITY NOTICE — 2026-10-06**
>
> This document is preserved as **HISTORICAL / PROVENANCE** evidence and is **SUPERSEDED AS CURRENT PRODUCT/PROVIDER AUTHORITY**.
>
> Current BODYSHOP Voice product authority lives in `egaracode/AI-Control-Workshop`, including `docs/DATA_CONTRACTS/VOICE_OPERATOR_INTAKE_CONTRACT_V1.md` and its MASTER-owned executable/provider-derivation tooling.
>
> The historical body below is intentionally preserved unchanged. Any words such as `current`, `authority`, `accepted target`, `next candidate` or Gate status must be read in the delivery context recorded by this document. Revalidate live GitHub and current first-party provider documentation before reuse.
>
> Repository classification: see `docs/VOICE_AUTHORITY_STATUS_V1.md`.

# Gate 2 — Operator expected-state alignment + Client Tool isolated staging V1

## 1. Status

```text
PARENT_VERTICAL: AI-Control-Workshop#432
ISSUE: bodyshop-voice-poc#38
TARGET_GATE: Gate 2 — Repository capability / isolated provider staging
PROVIDER_MAIN_MERGE: NOT_AUTHORIZED
GATE_3: NOT_ACTIVE
PRODUCTION: FORBIDDEN
SUPABASE: FORBIDDEN
```

This block is the final Gate-2 capability needed before a real ElevenLabs Development conversation can be attempted.

It extends the historical A5 provider authority without rewriting A5 evidence.

## 2. Why a new expected-state authority exists

A5 was correct for its historical scope, but the later accepted product contract in AI-Control-Workshop#433 requires additional operator behavior:

- trusted workshop context;
- line-stopped status;
- complete read-back;
- explicit operator confirmation;
- BODYSHOP canonical resolution after confirmation.

The historical A5 expected state did not explicitly guarantee those semantics.

Therefore the new authority is:

`elevenlabs/GATE2_CLIENT_TOOL_EXPECTED_PROVIDER_CONFIGURATION_V1.json`

It explicitly declares that it extends:

`A5_EXPECTED_PROVIDER_CONFIGURATION_V1`

without changing the historical file.

Retained from A5:

- agent name;
- language;
- System Prompt;
- LLM;
- temporary Eric voice;
- dynamic-variable set;
- Technician pre-close Procedure.

Changed only for this Gate-2 slice:

- effective Operator breakdown Procedure;
- one attached confirmed-intake Client Tool on the isolated branch.

## 3. Client Tool

The tool contract remains:

`elevenlabs/CONFIRMED_INTAKE_CLIENT_TOOL_V1.json`

Exact name:

`bodyshop_resolve_confirmed_intake`

The tool:

- is a Client Tool;
- waits for a response;
- receives only operator-confirmed bounded intake values;
- does not receive client-owned provenance;
- returns a BODYSHOP-owned resolution/clarification result;
- does not create a breakdown or mutate BODYSHOP.

## 4. Aligned Operator breakdown Procedure

The effective structured Procedure must execute the following sequence:

1. operator identity;
2. workshop;
3. model;
4. installation;
5. operation;
6. device;
7. subdevice/exact element only when applicable;
8. problem description;
9. line-stopped yes/no;
10. complete read-back;
11. explicit confirmation, with selective correction and repeated complete read-back until confirmed;
12. call `bodyshop_resolve_confirmed_intake`;
13. report only the BODYSHOP tool result.

The Client Tool may be called only after the confirmation step completes.

The final conversational result must remain non-mutating:

```text
RESOLVED
→ report canonical display context
→ Development resolution only
→ no breakdown creation

INCOMPLETE / AMBIGUOUS / NOT_FOUND / INVALID
→ report fail-closed result
→ ask only the missing or uncertain clarification
→ no fabricated canonical identity
→ no operational mutation
```

## 5. Current ElevenLabs API basis

Revalidated 2026-10-03 against current first-party documentation.

### Agent branches

Create isolated branch:

`POST /v1/convai/agents/{agent_id}/branches`

The request is pinned to the exact current Main version.

The isolated branch must read back:

- correct parent Main;
- expected name/description;
- zero live percentage;
- not archived.

### Workspace Client Tool

Create:

`POST /v1/convai/tools`

Read back:

`GET /v1/convai/tools/{tool_id}`

The returned tool must exactly match the bounded contract fields.

### Agent tool attachment

Update the isolated agent through:

`PATCH /v1/convai/agents/{agent_id}?branch_id={isolated_branch_id}`

The first isolated publication attaches exactly the new Client Tool while preserving all other conversation configuration.

### Procedure draft and publication

Update the inherited deterministic Operator Procedure draft through:

`PATCH /v1/convai/agents/{agent_id}/branches/{branch_id}/procedures/{procedure_id}/draft`

The Procedure draft is created only after the Client Tool attachment has been read back.

A second isolated agent publication then publishes that draft.

This ordering is deliberate because current Structured Procedure documentation requires a Tool step to reference a tool attached to the agent.

Official references:

- https://elevenlabs.io/docs/api-reference/agents/branches/create
- https://elevenlabs.io/docs/api-reference/agents/branches/get
- https://elevenlabs.io/docs/api-reference/agents/branches/list
- https://elevenlabs.io/docs/api-reference/tools/create
- https://elevenlabs.io/docs/api-reference/tools/get
- https://elevenlabs.io/docs/eleven-agents/customization/tools/client-tools
- https://elevenlabs.io/docs/api-reference/agents/update
- https://elevenlabs.io/docs/api-reference/agents/procedures/update
- https://elevenlabs.io/docs/eleven-agents/customization/procedures/structured-procedures

## 6. Exact Main stale-write guard

Before the first provider write, the executor requires the current reconciled Main evidence:

- exact AI Control agent fingerprint;
- exact Main branch fingerprint;
- exact current version fingerprint;
- A5 System Prompt fingerprint + length;
- exact language and Qwen API LLM id;
- exact dynamic-variable names;
- exact Eric voice fingerprint;
- effective Procedure set exactly:
  - Operator breakdown / deterministic;
  - Technician pre-close / free_form;
- exact current Procedure trigger/content fingerprints;
- no Main Procedure draft;
- Main agent `tool_ids=[]`;
- public-agent auth classification remains `enable_auth=false`;
- isolated branch name does not already exist;
- no workspace tool already exists with the target tool name.

Any stale baseline aborts before the first write.

## 7. Provider write ordering

`tools/elevenlabs_client_tool_staging_v1.py` performs only this authorized sequence:

```text
GET Main exact guard
→ POST isolated branch
→ GET isolated branch
→ POST workspace Client Tool
→ GET Client Tool
→ PATCH isolated agent: attach tool
→ GET isolated agent: verify tool attachment
→ PATCH inherited Operator Procedure draft
→ PATCH isolated agent: publish Procedure draft
→ GET isolated branch/agent/Procedures/tool
→ verify exact aligned target
→ GET Main exact guard again
→ STOP
```

No provider branch merge endpoint exists in this executor.

## 8. Main versus workspace mutation

Creating a workspace Client Tool is a real provider mutation.

The evidence therefore distinguishes:

```text
workspace_tool_created = true
provider_main_agent_modified = false
provider_main_merge_performed = false
```

The tool exists at workspace level after staging, but the Main AI Control agent must still have:

`tool_ids=[]`

until a separately authorized provider Main merge/configuration decision.

## 9. Sanitized evidence

The executor emits:

- SHA-256 resource fingerprints;
- branch name/description;
- safe Procedure fingerprints;
- tool contract fingerprint;
- live percentage;
- explicit mutation flags.

It does not emit:

- API key;
- raw agent id;
- raw branch id;
- raw version id;
- raw Procedure ids;
- raw tool id.

## 10. Runtime risk retained

Structured Procedures are currently Alpha in ElevenLabs.

The current provider documentation lists major OpenAI, Anthropic, Gemini and Grok model families for forced-tool compatibility guidance. Qwen is not explicitly guaranteed there.

Therefore the repository/provider staging result can establish exact configuration but cannot establish real Qwen structured-tool runtime reliability.

Classification:

`FORCED_TOOL_BEHAVIOR = EVIDENCE_REQUIRED_IN_GATE_3`

Gate 3 must test this with a real spoken Development conversation.

## 11. Local validation

Focused tests:

```text
python -m unittest discover -s tests -p "test_elevenlabs_client_tool_staging_v1.py" -v
```

Full suite:

```text
python -m unittest discover -s tests -v
```

Diff:

```text
git diff --check
```

## 12. Authorized live execution

Only after repository tests and exact-head CI are green.

The API key must remain local and never be pasted into chat or committed.

Executor:

```text
python tools/elevenlabs_client_tool_staging_v1.py \
  --expected elevenlabs/GATE2_CLIENT_TOOL_EXPECTED_PROVIDER_CONFIGURATION_V1.json \
  --tool-config elevenlabs/CONFIRMED_INTAKE_CLIENT_TOOL_V1.json \
  --output <temporary-path-outside-repo>/elevenlabs-issue38-staging-evidence-v1.json \
  --execute-isolated-staging
```

## 13. Interrupted-write recovery contract

The first authorized live staging attempt on 2026-10-04 stopped after provider Tool creation because the initial verifier compared the complete provider readback object byte-for-byte against the minimal GitHub Create Tool payload.

GET-only recovery evidence then proved:

- provider Main remained on the guarded A5 baseline and still had `tool_ids=[]`;
- the isolated branch existed, remained 0% live, had no Procedure draft, was one commit ahead and zero behind Main;
- the inherited Operator and Technician Procedures were still unchanged;
- exactly one workspace Client Tool named `bodyshop_resolve_confirmed_intake` existed;
- the Client Tool had not been attached to the isolated agent;
- every schema difference was a provider-added field; no GitHub-owned expected value had a semantic mismatch.

Current ElevenLabs Get Tool documentation returns provider-enriched Client Tool representations, including defaults and parameter metadata beyond the minimal create payload. Therefore readback validation now requires every GitHub-owned expected field/value recursively while allowing additional provider-owned fields.

The original staging mode remains fail-closed when the branch/tool already exist and must not be rerun after this partial write.

Recovery uses the separate flag:

```text
--resume-existing-staging
```

Before the first recovery PATCH it requires the exact observed partial state:

```text
Main = guarded baseline / tool_ids=[]
isolated branch = exact name + parent / 0% live / no draft / ahead=1 / behind=0
workspace tool = exactly one exact-name tool / expected semantic contract
isolated tool_ids = []
Operator Procedure = Main baseline
Technician Procedure = Main baseline
```

Recovery then performs only:

```text
PATCH isolated agent: attach existing Tool
→ GET verify exact attachment
→ PATCH existing Operator Procedure draft
→ PATCH isolated agent: publish draft
→ GET full isolated readback
→ GET exact Main guard
→ STOP
```

It performs no POST and creates no replacement branch or replacement Tool.

## 14. Explicit exclusions

This block does not authorize:

- merge of the isolated provider branch to Main;
- force merge;
- provider Main traffic change;
- Supabase / Edge Function;
- SQL / RLS / RPC / Auth;
- Production;
- breakdown creation;
- technician assignment;
- lifecycle mutation;
- Zello/F400;
- phone/SIP;
- workflow/dependency changes;
- Ready or repository merge without Albert.

## 15. Stop point

After successful isolated staging and GET readback:

```text
isolated branch = exact target / zero live
workspace Client Tool = created
isolated agent = tool attached
isolated Operator Procedure = aligned
Main agent = unchanged
provider Main merge = NOT PERFORMED
Gate 3 = NOT ACTIVE
```

STOP for Albert's repository Ready/merge decision and separate provider Main merge decision.

No canonical-state update required until the block is actually merged/closed.
