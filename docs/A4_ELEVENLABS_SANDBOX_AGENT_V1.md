# A4 ElevenLabs Sandbox Agent V1

## 1. Status

```text
A4_REPOSITORY_CONFIGURATION: PREPARED
ELEVENLABS_SANDBOX_AGENT: NOT_YET_CREATED
ELEVENLABS_NATIVE_TESTS: NOT_RUN
AUTHENTICATED_PROVIDER_WRITE: BLOCKED_IN_CURRENT_CHAT_ENVIRONMENT
```

A4 is the first provider-runtime block in the isolated `egaracode/bodyshop-voice-poc` laboratory.

The objective is to configure one real ElevenLabs sandbox agent for AI Control and execute only the provider-native portion of the merged A3 verification contract.

This document is not evidence that the provider agent already exists. Provider creation and test execution remain pending until an authenticated ElevenLabs write path is available.

---

## 2. Repository baseline

A4 starts from:

```text
main = 2650665d60eb91b94eefb82cf13be85e93ac81d8
Issue = #12
branch = feat/a4-elevenlabs-sandbox-agent-v1
```

Authoritative inputs:

1. `docs/A2_CONVERSATIONAL_FOUNDATION_V1.md`
2. `docs/A3_CONVERSATIONAL_VERIFICATION_AND_ELEVENLABS_TEST_CONTRACT_V1.md`
3. `docs/VOICE_POC_ROADMAP_A2_A6_V1.md`
4. `README.md`
5. `elevenlabs/A4_AI_CONTROL_SYSTEM_PROMPT_V1.md`

BODYSHOP semantics remain authoritative over provider behavior.

---

## 3. A4 provider boundary

A4 may use ElevenLabs runtime only in an isolated sandbox.

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

A4 does not validate F400, PTT, radio compression, workshop noise or real shared-walkie addressing. Those remain A5 concerns.

The shared-walkie `addressed to Control` gate remains BODYSHOP-owned and external to ElevenLabs.

---

## 4. Official ElevenLabs capability baseline

Revalidated on 2026-09-04 against current official ElevenLabs documentation.

### 4.1 Agent creation

ElevenLabs currently supports creating/managing agents through:

- Dashboard;
- API;
- CLI;
- hosted MCP server.

Current create-agent endpoint:

```text
POST /v1/convai/agents/create
```

A4 does not depend on deprecated `enable_versioning`; current documentation states agents are versioned by default and that parameter is ignored.

### 4.2 Agent Testing

Current Agent Testing supports:

```text
Simulation
Next Reply (Scenario)
Tool Call
Multi-run
```

Simulation supports:

- chat history;
- dynamic variables;
- tool mocking;
- configurable max turns.

Critical tool-mocking rule for A4:

```text
mocked tool has no matching mock response
→ fallback MUST be Finish with error
→ fallback MUST NOT be Call real tool
```

System tools and workflow tools are not mocked by Simulation; therefore A4 must not use either category for any hypothetical BODYSHOP state-changing action.

### 4.3 Dynamic variables

Dynamic variables can be used in prompts, messages and tool parameters. A4 uses them to inject safe test context instead of hard-coding real operational data.

### 4.4 Prompt structure

Current ElevenLabs prompting guidance recommends concise, explicit Markdown sections and dedicated guardrails. The repository system prompt follows that structure.

### 4.5 Language / voice

A4 is Spanish-first.

Voice quality, acoustic recognizability and final voice selection are not A4 acceptance criteria. A5 owns real audio validation.

---

## 5. Initial agent configuration contract

Provider-side bootstrap target:

| Setting | A4 target |
|---|---|
| Agent name | `AI Control — A4 Sandbox` |
| Template | Blank / minimal agent |
| Environment | isolated sandbox only |
| Primary working language | Spanish (`es`) |
| First message | `Hola, soy AI Control. Dime tu nombre y apellido.` |
| System prompt | exact content of `elevenlabs/A4_AI_CONTROL_SYSTEM_PROMPT_V1.md` excluding its repository-only header note |
| LLM | provider-native supported model; start with ElevenLabs current recommended/default unless deliberately changed |
| Temperature | low-variance target; prefer approximately `0.2` if exposed by the selected model/configuration |
| Voice | Spanish-capable provider voice; no voice cloning; exact voice is provisional until A5 |
| Knowledge base | none |
| External tools | none initially |
| Phone / SIP / Zello | none |
| Webhooks | none |
| Custom LLM / BYOK | none |
| Production deployment | forbidden |

### 5.1 Why no external tool initially

A4 can prove most A3 semantic behavior with Simulation and Next Reply before introducing any tool.

This gives the safest bootstrap state:

```text
agent can converse
+
agent cannot change BODYSHOP state
```

Tool Call Testing is therefore initially:

```text
NOT_RUN
```

until a separately reviewed sandbox-only, no-impact tool exists.

A4 completion does not require inventing a tool merely to make Tool Call Testing non-empty.

---

## 6. Dynamic-variable contract

Use synthetic values only.

Recommended variables:

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

Safe example values:

```text
channel_mode = direct_phone
activation_verified = true
caller_role = operator
known_identity = Operario Demo
known_model = Modelo Demo
known_installation = Instalación Demo
known_operation = Operación Demo
active_breakdown_count = 1
breakdown_ref = Avería Demo A
flow_stage = resolution
```

Do not use real names, actual plant identifiers, actual model/platform identifiers, real operations or real breakdown references in public fixtures.

---

## 7. Provider creation procedure

When authenticated ElevenLabs access is available:

1. Sign in to the intended ElevenLabs sandbox/workspace.
2. Create a new agent from a Blank/minimal template.
3. Name it `AI Control — A4 Sandbox`.
4. Set Spanish as the working language.
5. Configure the first message defined above.
6. Paste the repository system prompt.
7. Keep knowledge base empty.
8. Keep all external tools/integrations empty.
9. Keep phone/SIP/Zello integrations empty.
10. Use a low-variance LLM setting; record the exact model and temperature actually saved.
11. Use a normal Spanish-capable provider voice only as a provisional A4 voice; record it without treating audio quality as validated.
12. Save the agent.
13. Verify that no external state-changing integration appears in the agent configuration.
14. Record a sanitized configuration snapshot in this document or a follow-up evidence document.

Do not commit:

- API keys;
- secrets;
- full provider credentials;
- authentication tokens;
- real worker/customer data;
- real BODYSHOP operational data.

Because this repository is public, the full provider resource identifier should remain outside the repository unless there is a demonstrated need to publish it. A sanitized fingerprint/reference is sufficient for repository evidence.

---

## 8. A4 native test subset

A4 should execute the provider-native portion of A3. Adapter-owned and A5-only tests remain `NOT_RUN`.

### 8.1 Simulation targets

| A3 ID | A4 objective |
|---|---|
| `OP-02` | guided operator flow retains required fields |
| `OP-03` | multiple fields in one utterance are retained |
| `OP-05` | clear correction supersedes prior value safely |
| `OP-06` | incomplete context causes no irreversible claim/action |
| `TECH-01` | `puedes cerrar` -> pre-close semantics, not final close |
| `TECH-02` | unique pronoun reference may continue without redundant confirmation |
| `TECH-04` | `en marcha` interpreted only in correct technician resolution context |
| `TECH-05` | `solucionada` interpreted only in correct technician resolution context |
| `TECH-06` | multiple plausible breakdowns -> clarify |
| `TECH-08` | never claim final technical closure |
| `TECH-09` | operator `solucionada` does not inherit technician pre-close semantics |
| `SES-01` | active-session immediate follow-up does not require repeated `Control` |
| recovery scenario | three unresolved attempts -> human-Control fallback semantics |

### 8.2 Next Reply targets

Prioritize narrow response-policy assertions:

- `OP-04`: ask only for the ambiguous/missing field;
- `WA-03`: after externally supplied activation context, `Control me recibes?` produces acknowledgement only;
- `TECH-07`: clarify exact breakdown only;
- `TECH-08`: reply must distinguish pre-close from final closure;
- second recovery attempt: clearer reformulation rather than repeating identical wording.

### 8.3 Adapter-owned cases

The following remain outside provider-native PASS:

```text
WA-05
WA-06
WA-07
WA-08
WA-09 activation decision itself
```

They require the future BODYSHOP activation/non-intervention adapter and must remain:

```text
NOT_RUN / ADAPTER_TEST_REQUIRED
```

### 8.4 A5-owned cases

Any claim involving real:

```text
F400
PTT
Zello transport
factory noise
overlapping speakers
radio compression
real acoustic addressing
```

remains:

```text
NOT_RUN / A5_REAL_AUDIO_REQUIRED
```

---

## 9. Multi-run calibration

A3 intentionally deferred exact repetition counts to A4.

Initial A4 proposal:

- execute each selected native test once while stabilizing configuration;
- after no deterministic failure remains, run the most safety-sensitive native scenarios **5 independent times**;
- treat any hard-invariant violation in any run as BODYSHOP `FAIL` even when provider aggregate scoring is favorable.

Priority 5x candidates:

```text
OP-06 incomplete context / no operational claim
TECH-06 multiple breakdown ambiguity
TECH-08 no final technical closure
TECH-09 role/context isolation
three-attempt fallback
```

This is an A4 laboratory baseline, not a production SLA.

---

## 10. Evidence record

For each executed provider test record:

```text
A3 scenario ID
test type
sanitized agent/config reference
exact provider model
model temperature / relevant settings
language
safe dynamic variables
run/invocation identifier where publishable
number of independent runs
result per run
provider rationale
BODYSHOP verdict
forbidden behavior observed: yes/no
real tool reachable: must be no
```

If the agent configuration changes materially, previous provider-specific evidence must be treated as evidence for the old configuration.

---

## 11. A4 PASS/FAIL rules

A4 can be `PASS` only if:

- a real isolated ElevenLabs sandbox agent exists;
- its saved configuration matches this contract or any explicitly reviewed revision;
- no real BODYSHOP action/integration is reachable;
- the selected A3 provider-native tests have been executed;
- the safety-critical native scenarios pass the agreed multi-run baseline;
- no test falsely claims adapter/audio evidence;
- no secret or real operational data is committed.

A4 is `FAIL` if any run:

- claims final technical closure from technician pre-close wording;
- chooses an ambiguous breakdown;
- guesses unresolved critical data;
- produces or reaches a real state-changing integration;
- hides an adapter/audio requirement behind an ElevenLabs Simulation PASS.

A4 remains `BLOCKED`, not `FAIL`, when authenticated provider access is unavailable before actual creation/testing.

---

## 12. Current blocker

The current ChatGPT tool environment provides GitHub and web research but no authenticated ElevenLabs connector/account write tool.

Plugin discovery performed during A4 bootstrap did not return an ElevenLabs connector.

Therefore:

```text
repository-side configuration = possible
real ElevenLabs create/update/test = currently blocked
```

Do not substitute Retell, Pathors or another provider: A4 is specifically an ElevenLabs validation block.

Do not paste an ElevenLabs API key into GitHub or this public repository.

---

## 13. Official references

Revalidated 2026-09-04:

- ElevenLabs — Quickstart: https://elevenlabs.io/docs/eleven-agents/quickstart/
- ElevenLabs — Create agent API: https://elevenlabs.io/docs/eleven-agents/api-reference/agents/create
- ElevenLabs — Agent Testing: https://elevenlabs.io/docs/eleven-agents/customization/agent-testing
- ElevenLabs — Prompting guide: https://elevenlabs.io/docs/eleven-agents/best-practices/prompting-guide
- ElevenLabs — Dynamic variables: https://elevenlabs.io/docs/eleven-agents/customization/personalization/dynamic-variables
- ElevenLabs — Conversation flow: https://elevenlabs.io/docs/eleven-agents/customization/conversation-flow
- ElevenLabs — Language: https://elevenlabs.io/docs/eleven-agents/customization/voice/customization/language
- ElevenLabs — LLM models/configuration: https://elevenlabs.io/docs/eleven-agents/customization/llm

---

## 14. Stop point

Current state:

```text
A4_ISSUE: OPEN
A4_REPOSITORY_CONFIG: PREPARED
A4_PROVIDER_AGENT: BLOCKED_ON_AUTHENTICATED_WRITE
A4_TEST_EXECUTION: NOT_RUN
READY: NO
MERGE: NO
```

Next action is not A5.

Next action is to establish a safe authenticated ElevenLabs write path, create the A4 sandbox agent from this contract, execute the provider-native tests and then update the same A4 branch with evidence before Ready review.
