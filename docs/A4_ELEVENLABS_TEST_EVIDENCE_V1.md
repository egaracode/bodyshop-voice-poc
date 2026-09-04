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

### 3.2 Sanitized observed behavior

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

### 3.3 Verdicts

| Assertion | Verdict | Rationale |
|---|---|---|
| `OP-02` guided collection | `FAIL` | The agent did not preserve the semantic boundary between installation, operation and problem description. |
| `OP-03` multi-slot retention | `NOT_RUN` | The user did not provide the intended multi-slot input in one turn. |
| Sandbox no-real-action invariant | `PASS` | The agent explicitly kept the result in test mode and did not claim a real registration/notification. |
| No final technical closure claim | `PASS / NOT_APPLICABLE_TO_OPERATOR_FLOW` | No technician pre-close/final-close behavior was exercised. |

### 3.4 Root cause diagnosis

The compact A4 system prompt listed the required operator fields but did not define the semantic boundary of each slot strongly enough.

Specifically, it lacked explicit instructions that:

- `installation` and `operation` are distinct BODYSHOP references;
- a problem/failure narrative must not silently satisfy the `operation` slot;
- an activity verb/description must not be silently treated as an operation identifier;
- a value that appears to belong to a different requested slot requires focused clarification rather than silent binding.

Therefore this run is treated as a prompt-contract defect exposed by provider testing, not as acceptable behavior.

### 3.5 Corrective action

The A4 provider prompt was corrected in commit:

`7f2ae0e4377abadc24058ae795fd04c2973de232`

The correction adds explicit operator slot semantics and a fail-safe cross-slot clarification rule.

Evidence from `A4-MANUAL-001` remains evidence for the previous prompt configuration only.

### 3.6 Required retest

After loading and publishing the corrected prompt in ElevenLabs:

1. rerun `OP-02` using synthetic Demo values;
2. run `OP-03` with identity + model + installation + operation in one utterance;
3. verify the agent asks only for problem description;
4. verify that a problem narrative cannot silently satisfy the operation slot;
5. keep all future test values synthetic.

---

## 4. Current evidence state

```text
A4_PROVIDER_AGENT: CREATED_AND_PUBLISHED
A4-MANUAL-001_OP-02: FAIL
A4-MANUAL-001_OP-03: NOT_RUN
SANDBOX_NO_REAL_ACTION: PASS
CORRECTIVE_PROMPT_COMMIT: 7f2ae0e4377abadc24058ae795fd04c2973de232
RETEST_REQUIRED: YES
A4_OVERALL: NOT_PASS
READY: NO
MERGE: NO
```
