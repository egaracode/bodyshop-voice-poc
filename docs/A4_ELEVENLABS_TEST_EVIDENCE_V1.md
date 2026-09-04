# A4 ElevenLabs Test Evidence V1

## 1. Purpose

This document records sanitized provider-runtime evidence for A4 without publishing real names, spoken operational identifiers, provider credentials, secrets or raw screenshots/transcripts.

Repository: `egaracode/bodyshop-voice-poc`

A4 Issue: `#12`

A4 PR: `#13`

Provider: ElevenLabs Agents sandbox

---

## 2. Evidence policy

Only sanitized behavioral evidence may be committed to this public repository.

Do not commit:

- real caller names;
- raw conversation screenshots containing personal/operational data;
- real plant/model/installation/operation/breakdown identifiers;
- ElevenLabs API keys or credentials;
- unnecessary full provider resource identifiers.

Provider configuration changes that can affect behavior invalidate prior provider-specific evidence for the new configuration.

---

## 3. Manual run A4-MANUAL-001

Date: `2026-09-04`

Provider configuration branch head before corrective prompt change:

`30a93cc316fee1bff73f37463bc08104e19de773`

Observed provider configuration:

- ElevenLabs sandbox agent created and published;
- Spanish primary language;
- LLM: `Qwen3.5-397B-A17B`;
- provisional provider voice: `Eric`;
- expressive mode disabled;
- default personality disabled;
- no external tools or BODYSHOP integrations configured;
- dynamic-variable defaults configured for `direct_phone` + `operator` test context.

### 3.1 Intended scenarios

- `OP-02` — guided operator flow;
- `OP-03` — multi-slot retention.

`OP-03` was not actually exercised because the caller supplied the fields sequentially rather than in one multi-slot utterance.

### 3.2 Product clarification accepted by Albert

The sequential questioning observed in this run is desired behavior and is not itself a defect.

The preferred operator dialogue was subsequently refined during A4 to include explicit element identification:

```text
identity
→ model
→ installation
→ operation
→ element type
→ element reference
→ problem description
```

AI Control should normally lead the caller through bounded questions one field at a time because this reduces ambiguity and guides the conversation.

`OP-03` remains an opportunistic capability, not the preferred default questioning style: if the caller voluntarily supplies several valid fields in one utterance, AI Control should retain them and avoid asking for those fields again.

Therefore:

- sequential bounded questioning = desired;
- redundant questioning for already supplied clear fields = undesired;
- multi-slot extraction = supported when the human provides multiple slots, but AI Control does not need to solicit them all at once.

### 3.3 Sanitized observed behavior

The agent:

1. requested operator identity;
2. retained the supplied identity;
3. requested model;
4. retained the supplied model;
5. requested installation;
6. accepted a caller value into the installation slot without detecting that its semantic form could belong to another BODYSHOP slot;
7. requested operation;
8. received a breakdown/problem narrative instead of an operation identifier;
9. asked a follow-up about the activity being performed;
10. accepted an activity description as if it completed the operation requirement;
11. finished with an explicit sandbox-only acknowledgement and stated that no real breakdown was registered or real system notified.

No raw values are preserved here.

### 3.4 Verdicts

| Assertion | Verdict | Rationale |
|---|---|---|
| Guided sequential questioning style | `PASS` | The agent led the operator through bounded turns, which is the preferred product behavior. |
| `OP-02` semantic guided collection | `FAIL` | Despite correct dialogue pacing, the previous prompt did not preserve the semantic boundary between installation, operation and problem description. |
| `OP-03` multi-slot retention | `NOT_RUN` | The user did not provide the intended multi-slot input in one turn. |
| Sandbox no-real-action invariant | `PASS` | The agent explicitly kept the result in test mode and did not claim a real registration/notification. |
| No final technical closure claim | `PASS / NOT_APPLICABLE_TO_OPERATOR_FLOW` | No technician pre-close/final-close behavior was exercised. |

### 3.5 Root cause diagnosis

The failure is not that AI Control asked for the fields separately.

The defect is narrower: the compact A4 system prompt did not define the semantic boundary of each operator slot strongly enough.

A4 testing then exposed a further product need: after operation, the conversation must identify both the physical element type and the exact element reference before collecting the problem description.

This refinement is recorded in `docs/A4_OPERATOR_ELEMENT_REFINEMENT_V1.md`.

### 3.6 Corrective action

The active A4 provider prompt now defines:

- distinct model / installation / operation semantics;
- guided `element_type` and `element_ref` collection;
- natural element-specific follow-up questions;
- fail-safe cross-slot clarification;
- no requirement for `element_type` / `element_ref` to be ElevenLabs custom dynamic variables, because those values are collected during the conversation.

Evidence from `A4-MANUAL-001` remains evidence for the previous prompt configuration only.

### 3.7 Required retest

After loading and publishing the refined prompt in ElevenLabs:

1. rerun the guided operator flow using synthetic Demo values;
2. verify identity → model → installation → operation → element type → element reference → problem description are bound correctly;
3. verify element type and exact element reference remain distinct;
4. separately run multi-slot behavior by voluntarily supplying multiple synthetic fields in one utterance;
5. verify AI Control retains every clear supplied field and asks only for what remains missing;
6. keep all future test values synthetic.

---

## 4. Current evidence state

```text
A4_PROVIDER_AGENT: CREATED_AND_PUBLISHED_PREVIOUS_CONFIG
A4-MANUAL-001_GUIDED_SEQUENCE_STYLE: PASS
A4-MANUAL-001_OP-02_SEMANTIC_COLLECTION: FAIL
A4-MANUAL-001_OP-03: NOT_RUN
SANDBOX_NO_REAL_ACTION: PASS
A4_OPERATOR_ELEMENT_REFINEMENT: ACCEPTED
REFINED_PROMPT_REPUBLICATION: REQUIRED
RETEST_REQUIRED: YES
A4_OVERALL: NOT_PASS
READY: NO
MERGE: NO
```
