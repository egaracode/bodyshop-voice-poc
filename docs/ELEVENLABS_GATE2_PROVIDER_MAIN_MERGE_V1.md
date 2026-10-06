> **CURRENT AUTHORITY NOTICE — 2026-10-06**
>
> This document is preserved as **HISTORICAL / PROVENANCE** evidence and is **SUPERSEDED AS CURRENT PRODUCT/PROVIDER AUTHORITY**.
>
> Current BODYSHOP Voice product authority lives in `egaracode/AI-Control-Workshop`, including `docs/DATA_CONTRACTS/VOICE_OPERATOR_INTAKE_CONTRACT_V1.md` and its MASTER-owned executable/provider-derivation tooling.
>
> The historical body below is intentionally preserved unchanged. Any words such as `current`, `authority`, `accepted target`, `next candidate` or Gate status must be read in the delivery context recorded by this document. Revalidate live GitHub and current first-party provider documentation before reuse.
>
> Repository classification: see `docs/VOICE_AUTHORITY_STATUS_V1.md`.

# Gate 2 — ElevenLabs provider Main merge V1

## 1. Scope

This document owns the final provider-side Gate-2 adoption step for:

- parent Vertical Goal `AI-Control-Workshop#432`;
- `bodyshop-voice-poc#40`.

The objective is intentionally narrow:

```text
verified isolated Gate-2 branch
→ exact merge preview into provider Main
→ non-force merge
→ exact post-merge readback
→ STOP before Gate 3
```

This block does not execute a real conversation and does not mutate BODYSHOP operational state.

## 2. Current official ElevenLabs basis

Revalidated on 2026-10-04 against current first-party documentation.

### Merge preview

`GET /v1/convai/agents/{agent_id}/branches/{source_branch_id}/merge-preview`

Required query:

```text
target_branch_id = exact provider Main branch
force = false
```

The preview returns the merged agent configuration plus `overridden_fields` and structured `conflicts`. BODYSHOP requires both conflict collections to be empty before merge.

Official reference:

https://elevenlabs.io/docs/api-reference/agents/branches/preview-merge

### Merge

`POST /v1/convai/agents/{agent_id}/branches/{source_branch_id}/merge`

Required query/body:

```text
target_branch_id = exact provider Main branch
archive_source_branch = true
force = false
```

`force=true` causes source values to win timestamp-based conflicts and is forbidden by this block.

Official reference:

https://elevenlabs.io/docs/api-reference/agents/branches/merge

### Versioning behavior

ElevenLabs documents that a branch merge creates a new version on the target branch and may archive the source branch. Branch traffic and branch state remain separately observable.

Official reference:

https://elevenlabs.io/docs/eleven-agents/operate/versioning

Branch readback:

- https://elevenlabs.io/docs/api-reference/agents/branches/get
- https://elevenlabs.io/docs/api-reference/agents/branches/list

## 3. Why the historical A5 merge executor is not reused directly

`tools/elevenlabs_provider_merge_v1.py` was written for `bodyshop-voice-poc#34` and verifies historical A5 as the final provider target.

The current accepted Gate-2 target is different:

- A5 retained prompt/language/LLM/voice/dynamic variables;
- `bodyshop_resolve_confirmed_intake` attached;
- aligned `Operator breakdown` with workshop, `line_stopped`, complete read-back and explicit confirmation;
- unchanged `Technician pre-close`.

Using the A5-only merge verifier for this block would reject or misclassify the intended Gate-2 target. Issue #40 therefore owns a dedicated merge verifier.

## 4. Pre-merge stale-write guard

Before preview, the executor requires:

### Provider Main

Exact historical A5 baseline:

- exact agent fingerprint;
- exact Main branch fingerprint;
- exact Main version fingerprint;
- exact System Prompt fingerprint and length;
- exact language;
- exact Qwen model id;
- exact dynamic-variable set;
- exact Eric voice fingerprint;
- `tool_ids=[]`;
- public-agent auth classification unchanged;
- exact A5 `Operator breakdown`;
- exact A5 `Technician pre-close`.

### Isolated source branch

Exact branch:

`bodyshop-client-tool-issue-38`

Required:

- parent = exact Main;
- 0% live;
- not archived;
- no draft;
- `commits_behind=0`;
- `commits_ahead>0`.

The source branch must contain exactly:

- the verified confirmed-intake Client Tool;
- the Gate-2 aligned deterministic `Operator breakdown`;
- unchanged A5 `Technician pre-close`.

The executor additionally proves that, after normalizing `tool_ids`, the source `conversation_config` equals Main and that `platform_settings` and `workflow` remain unchanged. This prevents unrelated source-branch changes from piggybacking on the merge.

## 5. Provider-compiled artifact classification

The first live merge attempt correctly stopped in preflight before merge preview or POST because the source branch differed from Main in provider-generated fields.

GET-only evidence then established the exact pattern:

- Main `prompt.tool_ids=[]`;
- source `prompt.tool_ids=[<verified Client Tool>]`;
- Main `prompt.tools=[]`;
- source `prompt.tools` contains exactly one provider-materialized Tool;
- after normalizing only `tool_ids` and `tools`, no residual `conversation_config` differences remain;
- `platform_settings` remains unchanged;
- all Workflow differences are inside the exact compiled namespace of the aligned `Operator breakdown`;
- no Workflow difference touches `Technician pre-close`;
- the source Operator and Technician semantic fingerprints remain exact.

This behavior is consistent with current ElevenLabs documentation: attached tools are materialized in agent prompt configuration, and publishing a Structured Procedure compiles the Procedure into read-only Workflow nodes.

The merge executor therefore does not broadly ignore `workflow` or `prompt.tools`. It requires the separate GET-only classifier to return exactly:

```text
classification = EXPECTED_PROVIDER_COMPILED_ARTIFACTS_ONLY
prompt_tool_expected_subset_diff = []
conversation_config_residual_diff_after_tool_materialization_normalization = []
workflow_diff_only_in_operator_compiled_namespace = true
workflow_diff_touches_technician_namespace = false
platform_settings_diff = []
provider_main_write_performed = false
```

The classifier also verifies that the single materialized prompt Tool preserves every GitHub-owned expected Client Tool field and that the exact Operator/Technician Procedure fingerprints are still correct.

The classifier's sanitized result is part of the preflight safe-state signature. If its fingerprints/counts/classification move between preview and POST, the merge is blocked.

Any other provider delta remains fail-closed.

## 6. Merge preview gate

The preview is mandatory and GET-only.

Required result:

```text
overridden_fields = []
conflicts = []
preview conversation_config = verified source conversation_config
preview Procedures = verified source effective Procedure map
```

If `platform_settings` or `workflow` are returned in the preview, they must equal the verified source values.

After preview, the complete preflight is repeated. A safe-state fingerprint change blocks the merge before POST.

## 7. Merge operation

Only after both preflights match:

```text
POST merge
force = false
archive_source_branch = true
```

No retry loop exists in the executor.

If execution returns non-zero after the POST boundary, do not blindly rerun. Provider state must be inspected first.

## 8. Post-merge readback

The executor requires provider Main to:

- remain the exact Main branch;
- advance to a new version;
- retain A5 System Prompt/language/LLM/voice/dynamic variables;
- contain exactly the verified Client Tool;
- contain the exact aligned `Operator breakdown` fingerprint;
- retain the exact `Technician pre-close` fingerprint;
- retain public-agent auth classification;
- match the previously verified source configuration rather than a conflict-resolved hybrid.

The workspace Client Tool contract is re-read and revalidated.

The source branch must then be:

- archived;
- 0% live.

## 9. Sanitized evidence

Output may contain:

- SHA-256 fingerprints of provider resource ids;
- provider branch name;
- Main/source version fingerprints;
- Procedure content/trigger fingerprints;
- Tool fingerprint/name;
- merge controls;
- preview conflict counts;
- archival/live state;
- explicit provider-Main mutation flag.

Output must not contain:

- API key;
- raw agent id;
- raw branch ids;
- raw version ids;
- raw Procedure ids;
- raw Tool id;
- System Prompt or Procedure body.

## 10. Repository validation

Focused tests:

```text
python -m unittest discover -s tests -p "test_elevenlabs_gate2_provider_main_merge_v1.py" -v
```

Full suite:

```text
python -m unittest discover -s tests -v
```

Diff:

```text
git diff --check
```

## 11. Live execution

Execute only from the exact CI-validated repository head and only with the API key in the local environment.

```text
python tools/elevenlabs_gate2_provider_main_merge_v1.py \
  --expected elevenlabs/GATE2_CLIENT_TOOL_EXPECTED_PROVIDER_CONFIGURATION_V1.json \
  --tool-config elevenlabs/CONFIRMED_INTAKE_CLIENT_TOOL_V1.json \
  --output <temporary-path-outside-repo>/elevenlabs-issue40-main-merge-evidence-v1.json \
  --execute-provider-main-merge
```

After execution, remove the API key from the environment.

## 12. Residual runtime risk

Provider configuration success does not prove real spoken tool behavior.

Structured Procedures remain Alpha and Qwen forced-tool behavior remains:

`EVIDENCE_REQUIRED_IN_GATE_3`

## 13. Explicit exclusions

No:

- force merge;
- Production;
- Supabase / Edge Function;
- SQL / RLS / RPC / Auth;
- breakdown creation;
- technician assignment;
- lifecycle mutation;
- Zello/F400;
- phone/SIP;
- real conversation execution;
- repository Ready/merge without Albert.

## 14. Stop point

After successful provider Main merge + exact post-merge readback:

```text
provider Main = exact Gate-2 target
source branch = archived / 0% live
provider Main merge = complete
Gate 3 conversation = NOT EXECUTED
```

STOP for Albert's repository Ready decision and separate Gate-3 activation decision.
