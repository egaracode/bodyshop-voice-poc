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

## 4. Manual run A4-MANUAL-002

Date: `2026-09-04`

Provider configuration: refined seven-field operator prompt republished manually in ElevenLabs. Test values were ad-hoc/synthetic except that the raw provider transcript contained personal caller data; raw values are intentionally not committed.

### 4.1 Intended scenario

`OP-02` — guided operator flow with the refined hierarchy:

```text
identity
→ model
→ installation
→ operation
→ element type
→ element reference
→ problem description
```

### 4.2 Sanitized observed behavior

The agent:

1. asked for name and surname;
2. accepted only a partial identity and moved on instead of requesting the missing surname;
3. collected model;
4. collected installation;
5. collected operation;
6. asked for the affected element type;
7. interpreted the supplied element as a robot;
8. separately asked for the exact robot reference;
9. retained the exact element reference;
10. asked for the problem description;
11. retained the problem description without overwriting earlier hierarchy slots;
12. finished with an explicit test-mode acknowledgement and stated that no real breakdown was registered and no real operational system was notified.

### 4.3 Verdicts

| Assertion | Verdict | Rationale |
|---|---|---|
| Guided sequential questioning style | `PASS` | The agent led the caller through bounded one-field-at-a-time questions. |
| Model → installation → operation separation | `PASS` | The technical hierarchy remained distinct in this run. |
| Element type → exact element reference separation | `PASS` | The agent distinguished the generic element type from the exact element reference and asked a separate follow-up. |
| Problem-description boundary | `PASS` | The problem description remained a separate final field. |
| Sandbox no-real-action invariant | `PASS` | The agent explicitly stated that no real breakdown was registered and no real operational system was notified. |
| Identity completeness | `FAIL` | The first question required name + surname, but the agent accepted only a partial identity and continued to model. |
| `OP-02` overall | `FAIL` | All technical hierarchy slots passed, but one required identity field remained incomplete. |
| `OP-03` multi-slot retention | `NOT_RUN` | This run intentionally remained sequential. |

### 4.4 Root cause diagnosis

The provider prompt named the first slot only as `identity`. Although the first message asked for name and surname, the prompt did not explicitly define when identity is complete. The LLM therefore treated a single supplied name as sufficient.

### 4.5 Corrective action

Commit `08e59fa8e33b7ba707edf9eeb7048d800fb60e94` makes identity semantics explicit:

```text
identity = operator name + at least one surname
```

and requires a focused surname follow-up before progressing to model when only a first name is supplied.

Evidence from `A4-MANUAL-002` remains evidence for the previous provider prompt configuration only.

## 5. Required retest

After loading and publishing the identity-completeness correction in ElevenLabs:

1. rerun guided `OP-02` with entirely synthetic identity and technical values;
2. deliberately provide only a synthetic first name first;
3. verify AI Control asks for the missing surname and does not move to model until identity is complete;
4. continue model → installation → operation → element type → element reference → problem description;
5. verify every technical slot remains separated as in A4-MANUAL-002;
6. separately run `OP-03` later with multiple clear fields in one voluntary utterance.

## 6. Current evidence state

```text
A4_PROVIDER_AGENT: CREATED_AND_PUBLISHED_PRE_IDENTITY_FIX
A4-MANUAL-001_GUIDED_SEQUENCE_STYLE: PASS
A4-MANUAL-001_OP-02_SEMANTIC_COLLECTION: FAIL
A4-MANUAL-002_TECHNICAL_HIERARCHY: PASS
A4-MANUAL-002_IDENTITY_COMPLETENESS: FAIL
A4-MANUAL-002_OP-02_OVERALL: FAIL
A4-MANUAL-002_OP-03: NOT_RUN
SANDBOX_NO_REAL_ACTION: PASS
A4_OPERATOR_ELEMENT_REFINEMENT: ACCEPTED
ELEMENT_DYNAMIC_VARIABLES_REQUIRED: NO
IDENTITY_FIX_COMMIT: 08e59fa8e33b7ba707edf9eeb7048d800fb60e94
REFINED_PROMPT_REPUBLICATION: REQUIRED
RETEST_REQUIRED: YES
A4_OVERALL: NOT_PASS
READY: NO
MERGE: NO
```
