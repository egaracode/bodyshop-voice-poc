# A4 ElevenLabs Test Evidence V1

## 1. Purpose

This document records sanitized provider-runtime evidence for A4 without publishing real names, spoken operational identifiers, provider credentials, secrets or raw screenshots/transcripts.

Repository: `egaracode/bodyshop-voice-poc`

A4 Issue: `#12`

A4 PR: `#13`

Provider: ElevenLabs Agents sandbox

## 2. Evidence policy

Only sanitized behavioral evidence may be committed to this public repository. Do not commit real caller names, raw conversation screenshots containing personal/operational data, real plant/model/installation/operation/breakdown identifiers, ElevenLabs API keys or credentials, or unnecessary full provider resource identifiers.

Provider configuration changes that can affect behavior invalidate prior provider-specific evidence for the new configuration.

## 3. Manual run A4-MANUAL-001

Date: `2026-09-04`

Provider configuration branch head before corrective prompt change: `30a93cc316fee1bff73f37463bc08104e19de773`.

Observed provider configuration: ElevenLabs sandbox agent created and published; Spanish primary language; LLM `Qwen3.5-397B-A17B`; provisional voice `Eric`; expressive mode disabled; default personality disabled; no external tools/BODYSHOP integrations; dynamic-variable defaults configured for direct-phone operator context.

### 3.1 Intended scenarios

- `OP-02` — guided operator flow;
- `OP-03` — multi-slot retention.

`OP-03` was not actually exercised because the caller supplied the fields sequentially rather than in one multi-slot utterance.

### 3.2 Product clarification accepted by Albert

Sequential questioning is desired behavior and is not itself a defect.

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

`OP-03` remains an opportunistic capability: if the caller voluntarily supplies several valid fields in one utterance, AI Control should retain them and avoid asking for those fields again.

### 3.3 Sanitized observed behavior

The agent retained identity/model, then failed to preserve semantic slot boundaries among installation, operation and problem description in the first published configuration. It nevertheless finished with an explicit sandbox-only acknowledgement and did not claim a real registration/notification.

No raw values are preserved here.

### 3.4 Verdicts

| Assertion | Verdict | Rationale |
|---|---|---|
| Guided sequential questioning style | `PASS` | Bounded guided turns are the preferred product behavior. |
| `OP-02` semantic guided collection | `FAIL` | Previous prompt did not preserve slot boundaries correctly. |
| `OP-03` multi-slot retention | `NOT_RUN` | Multi-slot input was not supplied. |
| Sandbox no-real-action invariant | `PASS` | No real registration/notification was claimed. |

### 3.5 Root cause diagnosis

The failure was not sequential questioning. The compact prompt did not define slot boundaries strongly enough. A4 testing then exposed a further need: after operation, identify both physical element type and exact element reference before problem description.

### 3.6 Corrective action

The active A4 provider prompt now defines distinct model/installation/operation semantics, guided `element_type` and `element_ref` collection, natural element-specific follow-up questions and fail-safe cross-slot clarification.

`element_type` / `element_ref` do not need to be ElevenLabs custom dynamic variables because those values are collected during the conversation.

### 3.7 Required retest

After loading and publishing the refined prompt in ElevenLabs:

1. rerun guided operator flow using synthetic Demo values;
2. verify identity → model → installation → operation → element type → element reference → problem description bind correctly;
3. verify element type and exact reference remain distinct;
4. separately run multi-slot behavior;
5. keep all future test values synthetic.

## 4. Current evidence state

```text
A4_PROVIDER_AGENT: CREATED_AND_PUBLISHED_PREVIOUS_CONFIG
A4-MANUAL-001_GUIDED_SEQUENCE_STYLE: PASS
A4-MANUAL-001_OP-02_SEMANTIC_COLLECTION: FAIL
A4-MANUAL-001_OP-03: NOT_RUN
SANDBOX_NO_REAL_ACTION: PASS
A4_OPERATOR_ELEMENT_REFINEMENT: ACCEPTED
ELEMENT_DYNAMIC_VARIABLES_REQUIRED: NO
REFINED_PROMPT_REPUBLICATION: REQUIRED
RETEST_REQUIRED: YES
A4_OVERALL: NOT_PASS
READY: NO
MERGE: NO
```
