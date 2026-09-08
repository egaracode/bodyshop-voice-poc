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

It does **not** establish F400 microphone/speaker performance, PTT timing, Zello transport behavior, clipped syllables, overlapping-speaker safety, repeated-run robustness or production acoustic reliability. Those remain A5-owned.

## 6. Corrective prompt delta after A4-MANUAL-003

Commit `4351f7d569db3fe61382e4f337a221f3ee7ce240` strengthened the no-guess boundary with one explicit rule:

```text
Never say an unclear value is "probably" another slot. Ask a neutral clarification without assigning it.
```

## 7. Manual run A4-MANUAL-004 — exact V1 baseline retest

Date: `2026-09-08`

Provider configuration tested: published V1 prompt corresponding to repository head `3973e9043e44d0b2fa862f13066e9f3a0ea2b259` before the Procedures refactor was prepared.

### 7.1 Sanitized observed behavior

The agent:

- required a complete identity and accepted a later explicit identity correction;
- kept model / installation / operation structurally distinct;
- accepted element type + exact element reference from one utterance without asking for redundant repetition;
- no longer reproduced the previous verbal `probably another slot` speculation defect;
- preserved the sandbox no-real-action boundary;
- incorrectly accepted explicit operator uncertainty as if the value were confirmed and progressed.

Examples of the uncertainty class observed were semantically equivalent to `possibly`, `I think so`, and `I'm not sure`; raw transcript values are intentionally not committed.

### 7.2 Verdicts

| Assertion | Verdict | Rationale |
|---|---|---|
| Identity completeness | `PASS` | Full identity was required before progression. |
| Clear correction supersedes prior value (`OP-05`) | `PASS` | Explicit correction replaced the earlier identity value. |
| Technical slot separation | `PASS` | Model / installation / operation remained distinct. |
| Element type + exact reference in one utterance | `PASS_PARTIAL_OP03` | Both clear element fields were retained without redundant questioning. |
| No cross-slot speculation regression | `PASS` | Previous `probably another slot` wording did not recur. |
| Sandbox no-real-action invariant | `PASS` | No real BODYSHOP action was claimed. |
| Explicit uncertainty handling | `FAIL` | The agent converted an explicitly uncertain critical value into a confirmed value and advanced. |
| `OP-02` overall | `FAIL` | A critical unconfirmed value was treated as confirmed. |

### 7.3 Root cause classification

This is a general domain invariant, not a phrase-specific patch:

```text
VALUE HEARD != VALUE CONFIRMED
explicit doubt → UNCONFIRMED → clarify only that value → do not progress
```

## 8. Authorized A4 Procedures refactor

Albert authorized the refactor on `2026-09-08` after review against current official ElevenLabs Procedures guidance.

Repository candidate architecture:

```text
SHORT GLOBAL SYSTEM PROMPT
+ FREE-FORM PROCEDURE — Operator breakdown
+ FREE-FORM PROCEDURE — Technician pre-close
```

Candidate repository assets:

- `elevenlabs/A4_AI_CONTROL_SYSTEM_PROMPT_V2.md`
- `elevenlabs/A4_OPERATOR_BREAKDOWN_PROCEDURE_V1.md`
- `elevenlabs/A4_TECHNICIAN_PRE_CLOSE_PROCEDURE_V1.md`

The V1 prompt remains preserved as historical evidence of the configuration actually tested before this refactor.

The Procedures candidate does not change model, voice, the current 10 dynamic variables, tools, integrations, Supabase, phone/SIP/Zello, external walkie activation ownership or BODYSHOP lifecycle authority.

Provider publication of V2 + Procedures is not yet runtime evidence. All provider-runtime assertions for the new configuration remain `NOT_RUN` until those three assets are loaded, published and retested together.

## 9. Current next action

1. Load `A4_AI_CONTROL_SYSTEM_PROMPT_V2.md` into the existing ElevenLabs sandbox agent.
2. Create `Operator breakdown` as a Free-form Procedure using the exact repository trigger/content.
3. Create `Technician pre-close` as a Free-form Procedure using the exact repository trigger/content.
4. Keep Qwen, current provisional voice and the existing 10 dynamic variables unchanged.
5. Do not add tools, Knowledge Base, integrations, phone/SIP/Zello or Supabase.
6. Publish the three configuration assets together.
7. Restart A4 native regression testing on that exact provider configuration.

## 10. Current evidence state

```text
A4_PROVIDER_AGENT: CREATED_AND_PUBLISHED_WITH_V1
A4-MANUAL-001_OP-02: FAIL
A4-MANUAL-002_TECHNICAL_HIERARCHY: PASS
A4-MANUAL-002_IDENTITY_COMPLETENESS: FAIL
A4-MANUAL-003_IDENTITY_COMPLETENESS: PASS
A4-MANUAL-003_TECHNICAL_HIERARCHY: PASS
A4-MANUAL-003_REAL_WORKSHOP_NOISE: PRELIMINARY_PASS
A4-MANUAL-003_NO_CROSS_SLOT_SPECULATION: FAIL
A4-MANUAL-004_IDENTITY_COMPLETENESS: PASS
A4-MANUAL-004_CORRECTION: PASS
A4-MANUAL-004_SLOT_SEPARATION: PASS
A4-MANUAL-004_ELEMENT_MULTI_SLOT: PASS_PARTIAL_OP03
A4-MANUAL-004_NO_CROSS_SLOT_SPECULATION: PASS
A4-MANUAL-004_EXPLICIT_UNCERTAINTY: FAIL
SANDBOX_NO_REAL_ACTION: PASS_SO_FAR
A4_PROCEDURES_REFACTOR: AUTHORIZED
PROCEDURES_PROVIDER_LOAD: NOT_YET_DONE
POST_REFACTOR_RUNTIME_TESTS: NOT_RUN
A5_ACOUSTIC_VERIFICATION: NOT_CLOSED
A2_A3_OPERATOR_CONTRACT_SYNC: REQUIRED_BEFORE_READY
A4_OVERALL: NOT_PASS
READY: NO
MERGE: NO
```

Current repository head after evidence/documentation sync: `df178632ad9bbec9e4a44868a154c090afa3d1b4` was superseded by this documentation commit. Provider runtime remains V1 until manual publication of V2 + Procedures.
