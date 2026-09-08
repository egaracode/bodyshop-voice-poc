# A4 ElevenLabs Sandbox Agent V1

## 1. Status

```text
A4_REPOSITORY_CONFIGURATION: PROCEDURES_REFACTOR_PREPARED
ELEVENLABS_SANDBOX_AGENT: CREATED_AND_PUBLISHED_WITH_V1
PROCEDURES_PROVIDER_LOAD: NOT_YET_DONE
POST_REFACTOR_NATIVE_TESTS: NOT_RUN
READY: NO
MERGE: NO
```

A4 is the first provider-runtime block in the isolated `egaracode/bodyshop-voice-poc` laboratory.

The objective is to configure one real ElevenLabs sandbox agent for AI Control and execute only the provider-native portion of the merged A3 verification contract.

BODYSHOP semantics remain authoritative over provider behavior.

## 2. Repository baseline

```text
main = 2650665d60eb91b94eefb82cf13be85e93ac81d8
Issue = #12
branch = feat/a4-elevenlabs-sandbox-agent-v1
PR = #13
```

Authoritative inputs:

1. `docs/A2_CONVERSATIONAL_FOUNDATION_V1.md`
2. `docs/A3_CONVERSATIONAL_VERIFICATION_AND_ELEVENLABS_TEST_CONTRACT_V1.md`
3. `docs/VOICE_POC_ROADMAP_A2_A6_V1.md`
4. `README.md`
5. historical tested prompt: `elevenlabs/A4_AI_CONTROL_SYSTEM_PROMPT_V1.md`
6. authorized candidate prompt: `elevenlabs/A4_AI_CONTROL_SYSTEM_PROMPT_V2.md`
7. authorized candidate procedure: `elevenlabs/A4_OPERATOR_BREAKDOWN_PROCEDURE_V1.md`
8. authorized candidate procedure: `elevenlabs/A4_TECHNICIAN_PRE_CLOSE_PROCEDURE_V1.md`

## 3. Safety boundary

A4 remains isolated sandbox only.

A4 must not connect:

```text
Supabase
AI-Control-Workshop
BODYSHOP production runtime
corporate network
Zello API
real phone number
SIP trunk
Twilio / Exotel / WhatsApp transport
real BODYSHOP operational webhook
real state-changing tool
real worker data
real operational identifiers
```

The shared-walkie `addressed to Control` gate remains BODYSHOP-owned and external to ElevenLabs.

F400, PTT, Zello transport, clipping, overlapping voices, radio compression and production acoustic reliability remain A5-owned.

## 4. Authorized provider architecture

Albert authorized on `2026-09-08` an internal A4 refactor from a monolithic prompt to:

```text
SHORT GLOBAL SYSTEM PROMPT
+ FREE-FORM PROCEDURE — Operator breakdown
+ FREE-FORM PROCEDURE — Technician pre-close
```

No model, provisional voice, existing 10 dynamic variables, tool, integration, Supabase, phone/SIP/Zello, external activation ownership or BODYSHOP lifecycle authority changes are authorized by this refactor.

### 4.1 Global System Prompt V2

Owns only:

- AI Control identity and Spanish voice style;
- test-only / no-real-action boundary;
- runtime context variables;
- direct-phone vs external shared-walkie activation boundary;
- global confirmation/recovery behavior;
- global safety guardrails.

### 4.2 Operator breakdown Procedure

Owns:

```text
identity
→ model
→ installation
→ operation
→ element type
→ exact element reference
→ problem description
```

It also owns:

- clear correction replaces previous value;
- multi-slot retention;
- neutral clarification;
- explicit uncertainty remains UNCONFIRMED;
- `VALUE HEARD != VALUE CONFIRMED`;
- no progress until the current critical value is clear enough to rely on.

### 4.3 Technician pre-close Procedure

Owns:

- technician resolution wording;
- `REQUEST_PRE_CLOSE` semantics;
- exact active-breakdown ambiguity;
- operator/technician role separation;
- `PRE-CLOSE != final technical closure`.

## 5. Dynamic-variable contract

Keep exactly the existing 10 dynamic variables:

```text
channel_mode
activation_verified
caller_role
known_identity
known_model
known_installation
known_operation
active_breakdown_count
breakdown_ref
flow_stage
```

No extra variables are required for element type/reference in A4.

## 6. Latest provider evidence before Procedures

The latest V1 runtime retest is recorded as `A4-MANUAL-004` in `docs/A4_ELEVENLABS_TEST_EVIDENCE_V1.md`.

Key result:

```text
identity correction: PASS
technical slot separation: PASS
element type + exact reference multi-slot: PASS_PARTIAL_OP03
previous cross-slot speculation regression: PASS
sandbox no-real-action: PASS
explicit uncertainty handling: FAIL
```

Root cause:

```text
VALUE HEARD != VALUE CONFIRMED
explicit doubt → UNCONFIRMED → clarify only that value → do not progress
```

This invariant is now represented in the Operator breakdown Procedure candidate rather than continuing to grow the global prompt.

## 7. Provider loading procedure

In the existing ElevenLabs sandbox agent:

1. replace the current V1 system prompt with the exact content of `A4_AI_CONTROL_SYSTEM_PROMPT_V2.md`, excluding its repository-only header note;
2. create a Free-form Procedure named `Operator breakdown` with trigger and content from `A4_OPERATOR_BREAKDOWN_PROCEDURE_V1.md`;
3. create a Free-form Procedure named `Technician pre-close` with trigger and content from `A4_TECHNICIAN_PRE_CLOSE_PROCEDURE_V1.md`;
4. keep the current Qwen model unchanged;
5. keep the provisional voice unchanged;
6. keep the existing 10 dynamic variables unchanged;
7. keep Knowledge Base empty;
8. keep all tools/integrations empty;
9. keep phone/SIP/Zello empty;
10. publish the three configuration assets together;
11. verify again that no external state-changing integration is reachable.

Provider publication changes the behavioral configuration, therefore all post-refactor runtime tests must be executed again against that exact published configuration.

## 8. Native regression target after publication

Restart with the highest-value A4 checks:

```text
OP-02 guided operator flow
OP-03 multi-slot retention
OP-04 focused clarification
OP-05 correction supersedes prior value
OP-06 incomplete/uncertain context causes no operational claim
TECH-01 / 04 / 05 pre-close semantics
TECH-06 multiple breakdown ambiguity
TECH-08 never final technical closure
TECH-09 role/context isolation
SES-01 active-session continuity
three-attempt recovery/fallback
```

After deterministic failures are removed, execute the selected safety-sensitive cases 5 independent times as already defined by A4.

## 9. Open contradiction before Ready

Merged A2/A3 still describe the earlier operator minimum ending:

```text
identity → model → installation → operation → problem description
```

The accepted A4 operator contract adds:

```text
element type
exact element reference
```

and clarifies full identity. This A2/A3 drift must be reconciled before Ready. The Procedures refactor does not silently rewrite merged A2/A3.

## 10. Current stop point

```text
A4_ISSUE: OPEN
A4_PR: DRAFT
A4_PROCEDURES_REFACTOR: AUTHORIZED
REPOSITORY_CANDIDATE: PREPARED
PROVIDER_V2_LOAD: NOT_YET_DONE
POST_REFACTOR_RUNTIME_TESTS: NOT_RUN
CI: NONE ON CURRENT HEAD
A4_OVERALL: NOT_PASS
READY: NO
MERGE: NO
```

Next action is manual provider loading/publishing of V2 + the two Free-form Procedures in the existing isolated ElevenLabs agent. Do not start A5 and do not change any real BODYSHOP integration.