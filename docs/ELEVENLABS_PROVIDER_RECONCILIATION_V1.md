# ElevenLabs Provider Reconciliation V1 — Phase A Plan

## 1. Purpose

This document owns the repository-side planning boundary for:

- `egaracode/bodyshop-voice-poc#34`;
- parent Vertical Goal `egaracode/AI-Control-Workshop#432`.

Phase A does **not** mutate ElevenLabs.

Its only external behavior is authenticated GET inspection needed to prove:

1. the provider has not moved since the accepted V2 snapshot;
2. the GitHub-owned A5 target is unchanged;
3. the historical `structured` semantic target maps explicitly to the current API representation;
4. the exact historical Eric voice identity is still available;
5. the future provider write-set can be described without exposing raw IDs, prompts, Procedure bodies or the API key.

## 2. Current official source basis

Revalidated on 2026-10-03 against current ElevenLabs first-party documentation.

### Agent branching

Create agent branch:

https://elevenlabs.io/docs/api-reference/agents/branches/create

Relevant facts:

- POST creates a branch from an exact `parent_version_id`;
- `include_draft` defaults to false;
- the new branch has its own first version;
- this permits isolated configuration work before Main is changed.

Preview merged configuration:

https://elevenlabs.io/docs/api-reference/agents/branches/preview-merge

Relevant facts:

- GET-only;
- returns the would-be merged configuration;
- exposes overridden/conflicting fields;
- does not perform the merge.

Merge agent branch:

https://elevenlabs.io/docs/api-reference/agents/branches/merge

Relevant facts:

- POST is the actual branch-to-target merge boundary;
- `force` defaults to false;
- source archiving is independently controlled.

BODYSHOP policy for #34:

- never use force;
- Main merge requires a separate explicit Albert authorization;
- use merge-preview first.

### Procedures

Create Procedure:

https://elevenlabs.io/docs/api-reference/agents/procedures/create

Current raw Procedure type enum:

```text
free_form
deterministic
folder
```

Get Procedure Draft:

https://elevenlabs.io/docs/api-reference/agents/procedures/get-draft

Update Procedure Draft:

https://elevenlabs.io/docs/api-reference/agents/procedures/update

Compile Procedures:

https://elevenlabs.io/docs/api-reference/agents/procedures/compile

Get Procedure:

https://elevenlabs.io/docs/api-reference/agents/procedures/get

Current product documentation continues to distinguish free-form and structured Procedures. The historical A5 structured `Operator breakdown` therefore maps explicitly to:

```text
current raw API type = deterministic
content shape = JSON_STEPS
```

This is an intentional current-schema translation, not a claim that the obsolete raw label `structured` still exists.

### Update Agent

https://elevenlabs.io/docs/api-reference/agents/update

Relevant facts:

- PATCH can target an explicit `branch_id`;
- all agents are versioned;
- `version_description` records publication intent;
- when `procedures` is supplied, it replaces the current Procedure set;
- the map is keyed by Procedure ID and uses Procedure version references;
- when omitted, unpublished Procedure edits are used if present.

This allows #34 to create versioned Procedure material on the isolated provider branch before a later exact two-Procedure set is published there.

### Voice lookup

Current voice search:

https://elevenlabs.io/docs/api-reference/voices/search

Current API:

```text
GET /v2/voices
```

The legacy `GET /v1/voices` list endpoint is deprecated.

Phase A therefore searches voices through V2, then confirms the selected voice with the existing GET-by-ID endpoint.

## 3. Important correction to the earlier draft plan

The current ElevenLabs endpoint:

```text
DELETE /v1/convai/agents/{agent_id}/branches/{branch_id}/procedures/{procedure_id}/draft
```

deletes the caller's **draft** and resets to the committed Procedure.

It is not a committed-Procedure deletion endpoint.

Therefore #34 must not try to remove historical:

- `Element identification`;
- the old free-form `Operator breakdown`;

through draft deletion.

Historical versions remain provider history.

The effective reconciled branch must instead publish an exact Procedure set containing only:

```text
Operator breakdown
Technician pre-close
```

## 4. Controlling target

GitHub authority remains:

`elevenlabs/A5_EXPECTED_PROVIDER_CONFIGURATION_V1.json`

No new expected state has been accepted.

The current-schema target is therefore:

### Agent fields retained

```text
name = AI Control
language = es
llm = qwen35-397b-a17b
dynamic variables = exact existing 10-name set
```

### System Prompt restored

Expected normalized SHA-256:

```text
7e53fa089edbe9ae5da4af97e1f2fbb36833fffa504eb033d710b107d89972f2
```

Expected normalized length:

```text
2305
```

### Voice restored only by exact identity

Name:

```text
Eric - Smooth, Trustworthy
```

Expected raw voice-ID SHA-256:

```text
1e0c5d7793b1296cb88ddddf08040c9e901c241640ff7e88fcad1c31c7392bc9
```

A same-name voice with another fingerprint is not acceptable.

### Procedures

`Operator breakdown`

```text
new Procedure identity
raw API type = deterministic
trigger = exact A5 trigger
content = exact A5 canonical JSON steps
```

`Technician pre-close`

```text
retain existing Procedure identity when source guard still matches
raw API type = free_form
trigger = exact A5 trigger
content = exact A5 content
```

## 5. Exact stale-write source guard

Phase A pins the sanitized V2 evidence captured on 2026-10-02.

The planner fails closed if any pinned item moves, including:

- agent/version/main-branch fingerprints;
- current branch identity/state;
- current System Prompt fingerprint;
- current voice identity/settings;
- dynamic-variable set;
- current exact Procedure set;
- Procedure type/content-shape/trigger/content fingerprints;
- Procedure identity fingerprints;
- Procedure version-presence state;
- draft state.

A changed provider state is not automatically adopted.

It requires a new GET-only classification before write planning may continue.

## 6. Phase A implementation

Tool:

`tools/elevenlabs_provider_reconciliation_v1.py`

The tool is deliberately GET-only.

Implemented network methods:

```text
GET List Agents
GET Get Agent
GET List Branches
GET List Procedures
GET Get Procedure
GET Get Voice
GET /v2/voices search
```

There is no network method for:

```text
POST
PATCH
PUT
DELETE
```

Phase A cannot mutate the provider even if invoked incorrectly.

## 7. Sanitized future write plan

When all GET-only guards pass, the planner describes this ordered future sequence.

### Operation 1

```text
POST create isolated provider branch
parent = exact current Main version
name = bodyshop-a5-reconcile-issue-34
description = BODYSHOP #34 isolated A5 reconciliation staging
include_draft = false
```

### Operation 2

```text
POST create replacement Operator breakdown
type = deterministic
trigger/content = exact A5 values
```

### Operation 3

```text
PATCH existing Technician pre-close draft
type remains free_form
trigger/content = exact A5 values
```

### Operation 4

```text
PATCH isolated agent branch
procedures field omitted
purpose = publish staged Procedure drafts and obtain branch version refs
```

This intermediate state exists only on the isolated non-live provider branch.

### Operation 5

GET-read the isolated Procedure versions and verify their hashes.

### Operation 6

```text
PATCH isolated agent branch
System Prompt = exact A5 target
voice = exact Eric identity
procedures = exact two resolved Procedure version refs
```

The resulting effective Procedure set must contain exactly:

```text
Operator breakdown
Technician pre-close
```

### Operation 7

GET merge-preview from the isolated provider branch into Main.

Required result:

- expected target configuration;
- no unreviewed conflict/override;
- no unexpected Main movement.

### Operation 8

```text
POST merge isolated provider branch into Main
force = false
archive_source_branch = true
```

This operation is deliberately assigned a separate authorization gate.

It is not part of normal Phase A plan execution.

## 8. Secrets and evidence

The API key:

```text
local environment only
never CLI argument
never repository
never plan output
never chat
```

The sanitized report may contain:

- hashes of provider IDs;
- names of the controlled agent/Procedures;
- hashes and lengths of prompt/trigger/content;
- method names and endpoint templates;
- approval gates;
- provider branch name.

It must not contain raw:

- agent ID;
- branch ID;
- version ID;
- Procedure ID;
- voice ID;
- System Prompt;
- Procedure trigger;
- Procedure content;
- API key.

## 9. Tests

Focused test file:

`tests/test_elevenlabs_provider_reconciliation_v1.py`

It proves at minimum:

- A5 historical structured target maps only to current `deterministic`;
- exact source guard passes;
- stale source guard fails closed;
- existing draft state fails closed;
- pre-existing provider reconciliation branch fails closed;
- Eric selection requires exact fingerprint;
- output plan is sanitized;
- operation order is deterministic;
- DELETE-draft is not used as committed-Procedure removal;
- provider Main merge has a separate approval gate;
- provider Main merge uses `force=false`;
- Phase A API client is GET-only.

Full repository regression is also required.

## 10. Local validation

Focused:

```text
python -m unittest discover -s tests -p "test_elevenlabs_provider_reconciliation_v1.py" -v
```

Full:

```text
python -m unittest discover -s tests -v
```

Additional:

```text
git diff --check origin/main...HEAD
git status --short
```

No provider API key is needed for repository tests.

## 11. Live plan execution after repository validation

The live planner is still GET-only.

The API key must already be available locally in the environment.

Output must be outside the repository.

Example shape:

```text
python tools/elevenlabs_provider_reconciliation_v1.py \
  --expected elevenlabs/A5_EXPECTED_PROVIDER_CONFIGURATION_V1.json \
  --output <temporary-path-outside-repository>/elevenlabs-reconciliation-plan-v1.json
```

After execution:

1. remove the API key from the local environment;
2. confirm the Git worktree is still clean;
3. inspect the sanitized plan;
4. record safe evidence on #34;
5. STOP.

## 12. Mandatory decision boundary

Phase A stops after the exact sanitized plan is produced.

Before any provider mutation:

```text
Albert must explicitly approve the exact write-set
```

After isolated-branch staging and GET merge-preview:

```text
Albert must separately authorize merge into provider Main
```

No provider Main merge authorization is inherited from repository Ready/merge authority.

## 13. Explicit exclusions

This block does not authorize:

- Supabase;
- Edge Functions;
- SQL;
- RLS;
- RPC;
- Auth;
- Zello/F400 automation;
- phone/SIP;
- Production;
- real breakdown creation;
- technician assignment;
- lifecycle mutation;
- new expected provider state;
- force merge;
- provider Main merge without its explicit gate.

## 14. Current stop

```text
repository Phase-A capability
→ local tests
→ Draft PR
→ live GET-only plan
→ exact sanitized write-set
→ STOP for Albert approval
```

No provider mutation is performed by this Phase A implementation.
