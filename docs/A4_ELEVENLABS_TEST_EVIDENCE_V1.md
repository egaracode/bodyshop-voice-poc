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

### 3.4 Verdicts

| Assertion | Verdict | Rationale |
|---|---|---|
| Guided sequential questioning style | `PASS` | Bounded guided turns are the preferred product behavior. |
| `OP-02` semantic guided collection | `FAIL` | Previous prompt did not preserve slot boundaries correctly. |
| `OP-03` multi-slot retention | `NOT_RUN` | Multi-slot input was not supplied. |
| Sandbox no-real-action invariant | `PASS` | No real registration/notification was claimed. |

## 4. Manual run A4-MANUAL-002

Date: `2026-09-04`

Provider configuration: refined seven-field operator prompt republished manually in ElevenLabs. Test values were ad-hoc/synthetic except that the raw provider transcript contained personal caller data; raw values are intentionally not committed.

### 4.1 Intended scenario

`OP-02` — guided operator flow with the refined hierarchy.

### 4.2 Sanitized observed behavior

The technical hierarchy passed from model through problem, including separate element type and exact element reference. The agent maintained the sandbox no-real-action boundary. However, it accepted only a partial identity and progressed to model.

### 4.3 Verdicts

| Assertion | Verdict | Rationale |
|---|---|---|
| Guided sequential questioning style | `PASS` | One-field-at-a-time flow behaved as intended. |
| Model → installation → operation separation | `PASS` | Technical hierarchy remained distinct. |
| Element type → exact element reference separation | `PASS` | Generic type and exact reference remained separate. |
| Problem-description boundary | `PASS` | Problem remained the final distinct field. |
| Sandbox no-real-action invariant | `PASS` | No real action was claimed. |
| Identity completeness | `FAIL` | Partial identity was incorrectly accepted. |
| `OP-02` overall | `FAIL` | Required identity was incomplete. |
| `OP-03` multi-slot retention | `NOT_RUN` | Sequential run only. |

### 4.4 Corrective action

Commit `08e59fa8e33b7ba707edf9eeb7048d800fb60e94` made identity semantics explicit: operator identity requires name + at least one surname and must not progress to model until complete.

## 5. Manual run A4-MANUAL-003 — real workshop ambient noise

Date: `2026-09-04`

Execution context reported by Albert:

- physical workshop environment;
- real ambient workshop noise present;
- ElevenLabs preview/direct conversation path;
- no F400/PTT/Zello transport used;
- no real BODYSHOP state-changing integration connected.

The provider configuration used the consolidated prompt manually loaded and published by Albert. Repository commit `1a398687813946a781f9a3cc9664c8757307c84d` mirrors that tested provider prompt after the run; GitHub itself was not the runtime execution surface.

### 5.1 Sanitized observed behavior

The agent:

1. requested name + surname;
2. received one ambiguous single-token reply;
3. did **not** accept identity as complete and requested a complete name + surname;
4. then accepted a complete synthetic identity and moved to model;
5. retained the synthetic model/platform;
6. received an installation answer containing operation-like wording;
7. correctly detected installation/operation ambiguity and asked a focused clarification instead of silently binding both;
8. after clarification, retained installation and separately requested operation;
9. retained operation;
10. requested the affected element type;
11. received a robot-type answer and separately requested the exact robot reference;
12. retained the exact element reference;
13. requested and retained the problem description;
14. produced a test-mode completion statement and explicitly said no real breakdown was registered and no operational system was notified;
15. continued with an optional extra test-session question.

The raw transcript values and screenshot are intentionally not committed.

### 5.2 Important finding

On the first ambiguous identity reply, the agent verbally hypothesized that the token was **probably an installation** before asking again for complete identity.

It did not persist that hypothesis as the installation later in the flow, but the wording violates the no-guess / neutral-clarification guardrail. An unclear answer to the current slot must not be labeled as probably belonging to another operational slot.

### 5.3 Verdicts

| Assertion | Verdict | Rationale |
|---|---|---|
| Identity completeness | `PASS` | The agent did not proceed to model until name + surname were supplied. |
| Guided sequence | `PASS` | Identity → model → installation → operation → element type → exact reference → problem remained ordered. |
| Installation / operation ambiguity handling | `PASS` | The agent explicitly clarified an ambiguous cross-slot answer rather than binding it silently. |
| Element type / exact reference boundary | `PASS` | Generic element and exact identifier remained distinct. |
| Problem-description boundary | `PASS` | Problem remained separate from technical hierarchy slots. |
| Sandbox no-real-action invariant | `PASS` | No real registration/notification was claimed. |
| Real workshop-noise transcript continuity | `PRELIMINARY_PASS` | One real-noise conversation remained coherent end-to-end, but this is insufficient to close A5 acoustic/transport verification. |
| No cross-slot speculation | `FAIL` | The agent verbally guessed that one ambiguous token was probably an installation. |
| Final-response compactness | `MINOR_DEVIATION` | The agent restated collected data and asked an extra test-session question instead of giving only the minimal sandbox completion response. |
| `OP-02` overall | `FAIL` | Core collection succeeded, but a hard no-guess guardrail was violated verbally. |
| `OP-03` multi-slot retention | `NOT_RUN` | This run was not designed as multi-slot extraction. |

### 5.4 Acoustic interpretation boundary

This run is meaningful evidence that the current ElevenLabs preview conversation can preserve the guided semantic flow in at least one real workshop-noise condition.

It does **not** establish:

- F400 microphone/speaker performance;
- PTT timing;
- Zello transport behavior;
- clipped first/last syllables;
- overlapping-speaker safety;
- repeated-run robustness;
- production acoustic reliability.

Those remain A5-owned.

## 6. Corrective prompt delta after A4-MANUAL-003

Commit `4351f7d569db3fe61382e4f337a221f3ee7ce240` strengthens the no-guess boundary with one explicit rule:

```text
Never say an unclear value is "probably" another slot. Ask a neutral clarification without assigning it.
```

This commit changes the repository head and therefore requires the provider prompt to be updated/published before the next valid retest. A4-MANUAL-003 remains evidence for the immediately previous provider configuration only.

## 7. Current next action

1. Apply/publish the one-line no-cross-slot-speculation correction in ElevenLabs.
2. Rerun a focused ambiguous-identity/cross-slot test.
3. Confirm the agent asks a neutral clarification without hypothesizing another slot.
4. Run `OP-03` separately.
5. Reconcile merged A2/A3 with the accepted seven-field operator contract before Ready.

## 8. Current evidence state

```text
A4_PROVIDER_AGENT: CREATED_AND_PUBLISHED_PRE_CROSS_SLOT_FIX
A4-MANUAL-001_OP-02: FAIL
A4-MANUAL-002_TECHNICAL_HIERARCHY: PASS
A4-MANUAL-002_IDENTITY_COMPLETENESS: FAIL
A4-MANUAL-003_IDENTITY_COMPLETENESS: PASS
A4-MANUAL-003_TECHNICAL_HIERARCHY: PASS
A4-MANUAL-003_AMBIGUITY_CLARIFICATION: PASS
A4-MANUAL-003_REAL_WORKSHOP_NOISE: PRELIMINARY_PASS
A4-MANUAL-003_NO_CROSS_SLOT_SPECULATION: FAIL
A4-MANUAL-003_OP-02_OVERALL: FAIL
A4-MANUAL-003_OP-03: NOT_RUN
CROSS_SLOT_FIX_COMMIT: 4351f7d569db3fe61382e4f337a221f3ee7ce240
SANDBOX_NO_REAL_ACTION: PASS
A4_OPERATOR_ELEMENT_REFINEMENT: ACCEPTED
ELEMENT_DYNAMIC_VARIABLES_REQUIRED: NO
A5_ACOUSTIC_VERIFICATION: NOT_CLOSED
A2_A3_OPERATOR_CONTRACT_SYNC: REQUIRED_BEFORE_READY
A4_OVERALL: NOT_PASS
READY: NO
MERGE: NO
```
