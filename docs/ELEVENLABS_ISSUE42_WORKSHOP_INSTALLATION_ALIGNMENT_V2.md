# ElevenLabs Issue #42 — Workshop / Installation semantic alignment V2

## Status

```text
PARENT_VERTICAL: AI-Control-Workshop#432
PAUSED_RUNTIME_CHILD: AI-Control-Workshop#442
ACTIVE_CORRECTIVE_CHILD: bodyshop-voice-poc#42
TARGET_GATE: Gate 3 — Development runtime validated
PROVIDER_WRITE: NOT AUTHORIZED
PROVIDER_MAIN_MERGE: NOT AUTHORIZED
SUPABASE / PRODUCTION / LIFECYCLE: FORBIDDEN
```

This document records the provider-adapter correction needed after a real Gate-3 spoken conversation demonstrated that ElevenLabs did not collect the canonical BODYSHOP workshop separately from installation.

It does not create or redefine BODYSHOP domain semantics.

## 1. Canonical authority comparison

The correction was designed only after comparing both repositories.

### AI-Control-Workshop controls domain semantics

Current canonical BODYSHOP hierarchy:

```text
workshop
→ model
→ installation
→ operation
→ device
→ optional subdevice
```

Current canonical evidence includes:

- `docs/DATA_CONTRACTS/REFERENCE_OBJECT_CATALOG_CONTRACT_V1.md`;
- `src/services/voiceDomainAdapter.ts`;
- `src/services/voiceDomainAdapter.test.ts`;
- #443 bounded spoken-Spanish digit equivalence;
- #444 human-facing installation-name adoption in Development.

The Voice Domain Adapter treats `workshop` and `installation` as different required fields and resolves them against different catalog entities.

The authenticated Gate-3 catalog probe on current canonical main already proved:

```text
taller uno
+ A02
+ Autobastidor
+ OP320
+ robot de adhesivo uno
→ BODYSHOP RESOLVED
```

Therefore no BODYSHOP catalog, resolver or source-of-truth correction is needed for Issue #42.

### bodyshop-voice-poc controls provider adaptation only

The current confirmed-intake Client Tool already requires both:

```text
workshop
installation
```

The Gate-2 V1 Operator Procedure also contains separate Ask steps.

Historical A2/A3 material predates the current Reference Object Catalog and originally described a smaller operator flow without a dedicated workshop slot. Those historical documents remain provenance only and do not override the current canonical BODYSHOP intake.

Issue #42 must not promote those older PoC semantics back into the current domain model.

## 2. Runtime failure evidence

Aborted Gate-3 conversation fingerprint:

`sha256:61273af5f98b5d2b7d88ff2f0d45d1dae780575f7aa26c9253f1a5fd88061b08`

GET-only transcript evidence:

- start: 2026-10-06 09:14:15 +02:00;
- duration: 59 seconds;
- transcript items: 13;
- Client Tool calls: 0;
- Tool results: 0;
- provider write: NO.

Observed order:

1. identity requested and answered;
2. agent asked `¿En qué instalación o área de producción te encuentras?`;
3. operator answered `Autobastidor`;
4. agent advanced to model;
5. agent advanced to operation;
6. agent correctly asked for the device and stayed on that Ask when the answer remained incomplete.

The device was not skipped.

The defect is that the provider runtime did not obtain the required top-level BODYSHOP workshop.

Classification:

```text
PROVIDER_RUNTIME_WORKSHOP_PROMPT_SEMANTIC_DRIFT
```

## 3. Why V1 is preserved

`elevenlabs/GATE2_CLIENT_TOOL_EXPECTED_PROVIDER_CONFIGURATION_V1.json` is historical evidence of the provider state adopted during Gate 2.

Issue #42 therefore does not rewrite that file.

The successor is:

`elevenlabs/GATE3_WORKSHOP_INSTALLATION_EXPECTED_PROVIDER_CONFIGURATION_V2.json`

V2 retains:

- agent identity;
- System Prompt;
- language;
- LLM;
- voice;
- dynamic-variable set;
- confirmed-intake Client Tool contract;
- Technician pre-close;
- Operator trigger;
- Operator step order;
- read-back / explicit confirmation / Tool-call semantics.

Only two Operator Ask instructions change:

```text
step 1 (zero-based index 1)
= workshop/Taller Ask

step 3 (zero-based index 3)
= installation Ask
```

No canonical catalog values are copied into V2.

## 4. Corrective semantics

### Workshop Ask

The provider must ask for the top-level BODYSHOP workshop/Taller.

The instruction explicitly states that workshop is not:

- installation;
- production area;
- operation;
- equipment.

An installation/area answer does not satisfy the workshop Ask.

### Installation Ask

Installation is collected separately after the workshop/model context exists.

The instruction explicitly forbids:

- reusing the workshop answer;
- reinterpreting the workshop answer as installation;
- copying one slot into the other.

BODYSHOP remains the authority that decides whether either value resolves.

## 5. Current first-party ElevenLabs basis

Revalidated 2026-10-06.

Structured Procedures:
https://elevenlabs.io/docs/eleven-agents/customization/procedures/structured-procedures

Procedures overview:
https://elevenlabs.io/docs/eleven-agents/customization/procedures

Update Procedure Draft:
https://elevenlabs.io/docs/api-reference/agents/procedures/update

Create agent branch:
https://elevenlabs.io/docs/api-reference/agents/branches/create

Merge preview:
https://elevenlabs.io/docs/api-reference/agents/branches/preview-merge

Merge branch:
https://elevenlabs.io/docs/api-reference/agents/branches/merge

Relevant current documented behavior:

- a structured Procedure is an ordered list of typed steps;
- an Ask waits for the user and keeps asking until an appropriate answer is supplied;
- use one question per Ask;
- when an acceptable answer is not obvious, give the Ask a clear exit condition;
- API structured Procedure type is `deterministic`;
- branch creation can be pinned to an exact parent version;
- merge preview is GET-only;
- provider Main merge is a separate POST operation;
- `force=false` remains the BODYSHOP merge requirement.

## 6. GET-only planner

`tools/elevenlabs_issue42_workshop_installation_alignment_v2.py`

The network client exposes only GET operations.

It verifies the exact adopted Gate-2 Main baseline before producing any plan:

- exact unique `AI Control`;
- exact accepted agent fingerprint;
- exact Main branch fingerprint;
- exact accepted provider version fingerprint;
- retained System Prompt hash/length;
- language;
- Qwen model id;
- exact 10 dynamic-variable names;
- voice fingerprint;
- public-agent auth classification;
- exactly one attached confirmed-intake Client Tool;
- exact Tool id fingerprint and Tool contract;
- Main is not archived and has no Procedure draft;
- exact Gate-2 V1 Operator fingerprint;
- exact unchanged Technician fingerprint.

It also materializes the GitHub-owned V1 Procedure with the current raw Tool id and requires the live provider Procedure to match it exactly.

That separates:

```text
raw provider content drift
```

from:

```text
runtime semantic drift despite source match
```

## 7. Sanitized future write-set

If the GET-only baseline passes, the planner emits a sanitized future write-set.

No operation is executed.

Planned sequence:

```text
1. POST isolated provider branch from exact current Main version
2. GET isolated branch verification
3. PATCH only Operator Procedure draft to V2
4. PATCH isolated agent to publish that Procedure draft
5. GET exact isolated Procedure/state readback
6. GET merge-preview into Main with force=false
7. BLOCKED_DECISION before provider Main merge
```

The write-set contains only:

- SHA-256 fingerprints;
- stable branch name/description;
- Procedure name/type;
- trigger/content fingerprints and content length;
- exact changed step indexes;
- the two non-secret V2 instructions;
- safe merge parameters.

It must not contain raw:

- agent id;
- branch id;
- version id;
- Procedure id;
- Tool id;
- API key.

## 8. Authorized isolated staging executor

After reviewing the GET-only sanitized write-set, Albert separately authorized
provider operations 1–6 only:

```text
1. POST isolated branch from the exact accepted Main version
2. GET branch verification
3. PATCH only the Operator Procedure draft to V2
4. PATCH the isolated branch agent to publish that draft
5. GET exact isolated readback
6. GET merge-preview into Main with force=false
```

Provider Main merge remains explicitly unauthorized.

The bounded executor is:

`tools/elevenlabs_issue42_provider_staging_v2.py`

Its network surface is fail-closed:

- GET for provider verification and merge-preview;
- POST only for the exact branch-create endpoint;
- PATCH only for the exact Operator Procedure draft endpoint and isolated
  branch publication through Update Agent + `branch_id`;
- no DELETE or PUT support;
- no branch-merge mutation method;
- no Production or Supabase operation.

The executor requires `--execute-authorized-staging` and fails closed when
that flag or `ELEVENLABS_API_KEY` is absent.

Before the first write it re-runs the exact Gate-2 Main baseline guard. It also
supports bounded recovery when the named zero-live staging branch already
exists, but only when the branch is still tied to exact Main and its current
Procedure state is either exact Gate-2 V1 or exact V2. Unexpected drafts,
published content, parentage, live traffic or behind state stop execution.

Post-publish verification requires:

- branch live percentage = 0;
- branch not archived;
- no remaining Procedure draft;
- branch not behind Main and at least one published change ahead;
- exact V2 Operator fingerprint;
- unchanged Technician fingerprint;
- unchanged conversation config and platform settings;
- unchanged confirmed-intake Client Tool contract;
- compiled workflow movement only inside the Operator Procedure namespace;
- no Technician compiled-workflow movement;
- isolated version advanced from Main.

Merge preview is GET-only and must return:

```text
force = false
conflicts = []
overridden_fields = []
preview target state = exact verified isolated source state
```

Main is re-read before and after preview and must remain the exact accepted
Gate-2 baseline. The isolated branch is also re-read after preview and must
remain unchanged.

## 9. Exact stop for the current authorization

Current authorization:

```text
repository-side executor
+ isolated provider branch at 0% live
+ exact Operator V2 draft
+ isolated publish
+ exact readback
+ GET merge-preview force=false
```

Explicitly not authorized:

```text
provider Main merge
repository Ready
repository merge
Gate-3 conversation retry
Supabase / SQL / RLS / RPC / Auth
Production
lifecycle mutation
```

Successful executor evidence must stop at:

```text
STOP_FOR_ALBERT_PROVIDER_MAIN_MERGE_AUTHORIZATION
```

No canonical-state update required.

The correction does not change BODYSHOP architecture, catalog ownership,
persistence, security boundary or domain authority. It only strengthens
provider-side adherence to an already-canonical field separation.
