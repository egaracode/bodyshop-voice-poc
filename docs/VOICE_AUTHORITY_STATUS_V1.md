# BODYSHOP Voice PoC — Authority Status V1

## 1. Purpose

This document is the current repository-level authority map for `egaracode/bodyshop-voice-poc`.

It exists to prevent historical Voice PoC artifacts from being mistaken for current BODYSHOP product authority after the MASTER Voice Authority Cutover.

## 2. Current authority

The only current normative BODYSHOP Voice product authority is:

```text
egaracode/AI-Control-Workshop
```

Current MASTER owners include:

```text
docs/DATA_CONTRACTS/VOICE_OPERATOR_INTAKE_CONTRACT_V1.md
src/services/voiceOperatorIntakePolicy.ts
scripts/voice/elevenlabsProviderTarget.ts
.ai/CURRENT_STATE.md
docs/00_PROJECT_CANONICAL_STATE.md
docs/ARCHITECTURE/CANONICAL_DECISION_INDEX.md
```

This PoC repository does not override those owners.

## 3. Classification vocabulary

### CURRENT AUTHORITY

Current BODYSHOP product semantics, canonical catalog identity, lifecycle rules, provider-target derivation and exact-version acceptance criteria.

Location:

```text
AI-Control-Workshop
```

### HISTORICAL / PROVENANCE

Evidence that records what was designed, tested, staged, merged or observed at a particular time.

Historical evidence remains valuable and must not be silently rewritten to appear current.

### LAB

Experimental work that is intentionally isolated from productive BODYSHOP authority.

Examples include:

- UNIWA F400;
- Zello/PTT;
- audio experiments;
- transport experiments;
- provider experiments under a separately authorized lab Issue.

### SUPERSEDED AS PRODUCT AUTHORITY

An artifact may remain historically correct while no longer being allowed to define current BODYSHOP product/provider semantics.

This is the default classification for earlier Voice product/provider expected-state material in this repository after the MASTER cutover.

## 4. Repository classification

### Root README

`README.md`

Classification:

```text
CURRENT REPOSITORY STATUS OWNER
```

It explains that this repository is lab/provenance only.

### A2 / A3 / A5 / A6 / A7 and Voice workflow documents

Classification:

```text
HISTORICAL / PROVENANCE
SUPERSEDED AS CURRENT PRODUCT AUTHORITY
```

They remain useful for rationale, experiments and historical constraints.

They do not override the current MASTER Voice contract.

### Gate-2 / Gate-3 provider documents

Examples:

```text
docs/ELEVENLABS_GATE2_OPERATOR_CLIENT_TOOL_STAGING_V1.md
docs/ELEVENLABS_GATE2_PROVIDER_MAIN_MERGE_V1.md
docs/ELEVENLABS_ISSUE42_WORKSHOP_INSTALLATION_ALIGNMENT_V2.md
```

Classification:

```text
HISTORICAL DELIVERY EVIDENCE
SUPERSEDED AS CURRENT PROVIDER TARGET AUTHORITY
```

Their recorded execution evidence remains valid for the historical block that produced it.

Any statement using words such as `current`, `accepted target`, `authority`, `next candidate` or `Gate` must be read in that historical delivery context unless revalidated in the MASTER.

### `elevenlabs/`

Classification:

```text
HISTORICAL PROVIDER SNAPSHOTS / EXPECTED-STATE EVIDENCE
NOT CURRENT PRODUCTIVE TARGET AUTHORITY
```

See `elevenlabs/README.md`.

### `tools/`

Classification:

```text
HISTORICAL / LAB TOOLING
NOT CURRENT PRODUCTIVE DEPLOYMENT AUTHORITY
```

See `tools/README.md`.

### `tests/`

Classification:

```text
HISTORICAL / LAB VALIDATION EVIDENCE
```

Tests prove the behavior of the PoC artifact they cover. Passing historical tests does not prove that the artifact is the current productive target.

## 5. Rules for future work

### Productive Voice semantics

Start in:

```text
AI-Control-Workshop
```

Do not create a new product contract in this PoC and later attempt to synchronize it back into the MASTER.

### Provider target changes

Current productive provider-target semantics must be derived from the MASTER.

Historical JSON files in this PoC may be used only as provenance/comparison input, never as the sole source for a new productive target.

### Provider operations

The presence of a historical executor does not authorize its execution.

Any future provider read/write requires:

1. an explicitly authorized current Issue;
2. fresh provider/runtime evidence;
3. current first-party provider documentation;
4. a MASTER-derived target or explicitly authorized laboratory-only objective;
5. the required Albert decision boundary.

### Laboratory experiments

New lab experiments may live here when the Issue explicitly classifies them as non-authoritative and isolated from BODYSHOP runtime/lifecycle authority.

## 6. Historical evidence preservation

Do not:

- delete old expected-state JSONs merely because they are superseded;
- rewrite historical provider evidence to match today's product;
- alter past timestamps, SHAs or execution outcomes;
- retroactively convert historical FAIL/DRIFT/NOT_FOUND evidence into PASS.

Preferred pattern:

```text
preserve historical body
+ add current-authority banner when ambiguity is material
+ point current product work to MASTER
```

## 7. External-provider claims

Provider API behavior, feature maturity, model support and runtime behavior recorded in historical documents are time-bound evidence.

Before reuse, revalidate them against current first-party documentation and current provider/runtime evidence.

This repository-level status document does not certify old external-provider statements as current.

## 8. Sources / roadmaps / handoffs

User-provided Sources, PDFs, roadmaps and handoffs are supporting context and provenance.

They do not override:

```text
live GitHub
→ current MASTER code/config
→ canonical MASTER contracts
→ authorized Issue
→ exact-head CI/runtime evidence
```

## 9. Stop rule

If a PoC artifact conflicts with current MASTER authority:

```text
STOP
→ use MASTER
→ preserve PoC artifact as historical evidence
→ do not reconcile silently
```
