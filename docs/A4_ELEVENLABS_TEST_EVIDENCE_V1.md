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
- real plant/model/installation/operation/element/breakdown identifiers;
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

The preferred operator dialogue is now refined to:

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

Element identification is intentionally split into two concepts:

```text
element_type = what kind of physical element is affected
element_ref  = which exact element is affected
```

After learning the type, AI Control should adapt the next question naturally to that type, for example the equivalent of `¿Qué robot es?`, `¿Qué motor es?` or `¿Qué brida es?`.

`OP-03` remains an opportunistic capability, not the preferred default questioning style: if the caller voluntarily supplies several valid fields in one utterance, AI Control should retain them and avoid asking for those fields again.

Therefore:

- sequential bounded questioning = desired;
- redundant questioning for already supplied clear fields = undesired;
- element type and exact element reference must remain distinct;
- multi-slot extraction = supported when the human provides multiple slots, but AI Control does not need to solicit them all at once.

This A4 refinement is documented in `docs/A4_OPERATOR_ELEMENT_REFINEMENT_V1.md` and requires reconciliation with the earlier A2/A3 five-slot operator subset before A4 Ready.

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
| `OP-02` semantic guided collection | `FAIL` | Despite the correct dialogue pacing, the agent did not preserve the semantic boundary between installation, operation and problem description. |
| `OP-03` multi-slot retention | `NOT_RUN` | The user did not provide the intended multi-slot input in one turn. |
| Sandbox no-real-action invariant | `PASS` | The agent explicitly kept the result in test mode and did not claim a real registration/notification. |
| No final technical closure claim | `PASS / NOT_APPLICABLE_TO_OPERATOR_FLOW` | No technician pre-close/final-close behavior was exercised. |

### 3.5 Root cause diagnosis

The failure is not that AI Control asked for the fields separately.

The defect is narrower: the compact A4 system prompt did not define the semantic boundary of each slot strongly enough.

The accepted product refinement also exposed that the earlier operator contract did not explicitly capture the affected physical element at the desired level of detail.

Required boundaries now include:

- `installation` and `operation` are distinct BODYSHOP references;
- `element_type` and `element_ref` are distinct concepts;
- a problem/failure narrative must not silently satisfy the `operation` slot;
- an activity verb/description must not be silently treated as an operation identifier;
- a generic element type must not silently satisfy the exact element reference;
- a value that appears to belong to a different requested slot requires focused clarification rather than silent binding.

Therefore this run is treated as a prompt/contract defect exposed by provider testing, while the sequential dialogue strategy itself is accepted.

### 3.6 Corrective action

Initial slot-boundary correction:

`7f2ae0e4377abadc24058ae795fd04c2973de232`

Element type/reference provider-prompt refinement:

`52056a492457a08306780cc36f1e2f422c6e10a0`

Accepted A4 refinement document:

`docs/A4_OPERATOR_ELEMENT_REFINEMENT_V1.md`

Evidence from `A4-MANUAL-001` remains evidence for the previous provider configuration only.

### 3.7 Required retest

After loading and publishing the refined prompt in ElevenLabs:

1. add development variables `known_element_type=UNKNOWN` and `known_element_ref=UNKNOWN`;
2. rerun the guided operator flow using only synthetic Demo values;
3. verify the preferred sequence `identity → model → installation → operation → element type → element reference → problem description`;
4. verify every value is bound to the correct semantic slot;
5. verify the question for the exact element adapts naturally to the known element type;
6. separately run multi-slot behavior by voluntarily supplying several synthetic fields in one utterance;
7. verify AI Control retains every clear supplied field and asks only for what remains missing;
8. verify that a problem narrative cannot silently satisfy the operation slot;
9. keep all future test values synthetic.

---

## 4. Current evidence state

```text
A4_PROVIDER_AGENT: CREATED_AND_PUBLISHED_PREVIOUS_CONFIG
A4-MANUAL-001_GUIDED_SEQUENCE_STYLE: PASS
A4-MANUAL-001_OP-02_SEMANTIC_COLLECTION: FAIL
A4-MANUAL-001_OP-03: NOT_RUN
SANDBOX_NO_REAL_ACTION: PASS
A4_OPERATOR_ELEMENT_REFINEMENT: ACCEPTED
A4_PROVIDER_PROMPT_REFINEMENT_COMMIT: 52056a492457a08306780cc36f1e2f422c6e10a0
REPUBLICATION_REQUIRED: YES
RETEST_REQUIRED: YES
A4_OVERALL: NOT_PASS
READY: NO
MERGE: NO
```
