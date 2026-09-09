# ElevenLabs Capability Radar and Adoption Plan V1

## 0. Status and purpose

Repository: `egaracode/bodyshop-voice-poc`

Date of review: `2026-09-09`

Provider: ElevenLabs / ElevenAgents

This document records the most relevant current ElevenLabs capabilities for the BODYSHOP Voice PoC, why they matter, how they could be used, and when they should or should not be introduced.

This document is **research and adoption guidance only**. It does not itself authorize runtime changes.

Current A4 safety boundaries remain unchanged:

```text
NO REAL BODYSHOP ACTION
NO SUPABASE
NO AI-CONTROL-WORKSHOP CHANGE
NO PRODUCTION / CORPORATE NETWORK
NO REAL PHONE / SIP / ZELLO INTEGRATION
NO REAL STATE-CHANGING TOOL
NO REAL WORKER OR OPERATIONAL DATA IN THE PUBLIC REPOSITORY
```

The objective is to prevent ad-hoc provider configuration and to introduce new ElevenLabs capabilities only when they solve a concrete BODYSHOP problem with controlled evidence.

---

## 1. Executive summary

ElevenAgents is no longer only a voice agent driven by one system prompt. The platform now provides several layers that can be combined deliberately:

```text
GLOBAL SYSTEM PROMPT
        │
        ├── Procedures / Sub-procedures
        │
        ├── Knowledge Base
        │
        ├── Conversation Flow / VAD
        │
        ├── System / Webhook / Client / Code / MCP Tools
        │
        ├── Agent Testing
        │
        ├── Success Evaluation / Data Collection / Spotlight
        │
        ├── Versioning / Branches / Experiments
        │
        └── CLI / API deployment tooling
```

For BODYSHOP, the highest-value capabilities are not all for immediate use.

Recommended order:

```text
A4 NOW
→ Procedures + Sub-procedures
→ exact provider baseline
→ native Agent Testing

AFTER A4
→ Provider Versioning / Branch governance
→ CLI / API agents-as-code evaluation

A5
→ background_voice_detection
→ turn eagerness / silence / interruptions
→ Skip Turn candidate
→ pronunciation / acoustic robustness work

POST-A4 / PRE-PILOT
→ BODYSHOP Element Catalog in Knowledge Base
→ Success Evaluation
→ Data Collection
→ privacy / retention policy

LATER CONTROLLED EXPERIMENTS
→ Guardrails
→ Structured Procedures
→ alternative LLMs
→ Workflows
→ DTMF fallback
→ Queueing / scale controls
```

The guiding principle is:

```text
ONE BEHAVIORAL VARIABLE AT A TIME
→ TEST
→ RECORD EXACT VERSION
→ COMPARE
→ ACCEPT OR REJECT
```

---

## 2. Capability priority map

| Capability | BODYSHOP value | Recommended timing | Primary use |
|---|---:|---|---|
| Free-form Procedures | 10/10 | A4 now | Keep task logic out of the global prompt |
| Sub-procedures | 10/10 | A4 now | Reusable specialized steps such as element identification |
| Agent Testing | 10/10 | A4 immediately after exact publish | Deterministic semantic regression |
| Agent Versioning / branches | 10/10 | After A4 | Exact provider evidence and safe change isolation |
| ElevenLabs CLI / agents-as-code | 10/10 | After A4 | Remove fragile manual copy/paste and add deployment diffs |
| VAD `background_voice_detection` | 10/10 | A5 | Industrial background speech/noise evaluation |
| Conversation Flow controls | 9/10 | A5 | Silence, interruptions and patient turn-taking |
| Knowledge Base | 9/10 | Post-A4 | BODYSHOP vocabulary and element catalog |
| Success Evaluation | 9/10 | Post-A4 / shadow | Automated quality scoring |
| Data Collection | 9/10 | Post-A4 / shadow | Structured post-call extraction |
| Skip Turn system tool | 9/10 | A5 candidate | Respect "un segundo, lo miro" without speaking |
| Pronunciation Dictionary | 8/10 | A5/A6 | Correct TTS of acronyms and technical terms |
| Structured Procedures | 8/10 potential | Later experiment | Fixed-order flows if model support is proven |
| Guardrails 2.0 | 7/10 now | After semantic baseline | Security and prompt-injection defense |
| Workflows | 6/10 now, 9/10 later | Later | Complex branching / sub-agent orchestration |
| DTMF input | 5/10 | Future fallback | Numeric/reference fallback over keypad |
| Queueing | 5/10 now, higher at scale | Future | Handle concurrency limits without dropped calls |
| Experiments / traffic splitting | High for pilot | Pilot maturity | Evidence-based A/B comparison |

---

## 3. Procedures and sub-procedures — use now

### 3.1 Why they fit BODYSHOP

Free-form Procedures hold task-specific instructions that are loaded when relevant instead of putting all behavior in one system prompt.

For BODYSHOP this enables a cleaner separation:

```text
SYSTEM PROMPT
→ global identity
→ Spanish voice behavior
→ sandbox / no-real-action boundary
→ runtime context
→ global confirmation / recovery
→ global guardrails

OPERATOR BREAKDOWN PROCEDURE
→ guided breakdown collection
→ slot semantics
→ uncertainty handling
→ corrections
→ completion logic

TECHNICIAN PRE-CLOSE PROCEDURE
→ technician resolution semantics
→ REQUEST_PRE_CLOSE
→ active-breakdown ambiguity

ELEMENT IDENTIFICATION SUB-PROCEDURE
→ specialized affected-element rules
```

### 3.2 Sub-procedures

A Free-form Procedure with an empty trigger acts as a sub-procedure. It is only available when another Procedure references it.

This is especially useful for BODYSHOP because specialized knowledge can be isolated without adding more entry-point routing choices.

Current example:

```text
Operator breakdown
        │
        └── Element identification
                ├── brida → individual reference applies
                ├── antorcha → individual number may not exist
                └── unknown type → neutral clarification, no invented rule
```

### 3.3 How BODYSHOP should use Procedures

Rules:

```text
Global behavior                   → System Prompt
Task-specific flow                → Procedure
Reusable specialized task step   → Sub-procedure
Large domain knowledge            → Knowledge Base
Complex deterministic graph       → Workflow only if later justified
```

### 3.4 SOP import

ElevenLabs can import Procedures from SOP files such as PDF, DOCX, TXT, MD, HTML and EPUB and produce draft Procedures.

Potential BODYSHOP use:

```text
existing maintenance / operational SOP
→ import
→ generated draft Procedures
→ human technical audit
→ simplify
→ sandbox tests
→ accept only validated behavior
```

Generated Procedures must never become authoritative without BODYSHOP review.

---

## 4. Agent Testing — highest-priority next capability

### 4.1 Why this matters

A large part of A3/A4 semantic verification is currently manual. ElevenLabs Agent Testing can automate deterministic behavior before acoustic testing.

The current framework provides:

```text
Simulation Test
→ end-to-end multi-turn conversation

Next Reply / Scenario Test
→ evaluate only the next agent response

Tool Call Test
→ validate tool selection and parameters
```

### 4.2 BODYSHOP test allocation

Recommended mapping:

```text
SLOT / UNCERTAINTY / ROLE / SEMANTIC RULE
→ Next Reply Test

COMPLETE OPERATOR REPORT
→ Simulation Test

TECHNICIAN PRE-CLOSE FLOW
→ Simulation + focused Next Reply tests

FUTURE TOOL EXECUTION
→ Tool Call Test with mock only

MIC / NOISE / F400 / PTT / ZELLO
→ NOT native semantic testing
→ A5 real acoustic verification
```

### 4.3 Example — uncertainty invariant

Scenario history:

```text
AI Control: ¿Cuál es la instalación?
Operator: Creo que es Demo 01, no estoy seguro.
```

Success criteria:

```text
PASS if:
- installation remains unconfirmed
- agent asks only to confirm or correct installation
- agent does not advance to operation
- agent does not guess another slot

FAIL if:
- agent asks for operation
- agent treats Demo 01 as confirmed
- agent assigns the answer to another slot
```

This directly tests:

```text
VALUE HEARD != VALUE CONFIRMED
```

### 4.4 Repeat runs

Critical semantic tests should be run repeatedly rather than accepted after one success.

Recommended A4 policy candidate:

```text
ordinary deterministic semantic case → 3 runs minimum
safety / lifecycle / ambiguity case   → 5 runs minimum
known unstable case                   → 10+ runs for diagnosis
```

The current Agent Testing API supports repeated executions, enabling pass-rate measurement and failure grouping.

### 4.5 Dynamic-variable test contexts

Tests should set explicit context rather than depending on Dashboard defaults.

Example:

```text
channel_mode=direct_phone
activation_verified=true
caller_role=operator
known_identity=UNKNOWN
known_model=UNKNOWN
known_installation=UNKNOWN
known_operation=UNKNOWN
active_breakdown_count=0
breakdown_ref=UNKNOWN
flow_stage=reporting
```

This is the preferred way to prove that a result belongs to an exact scenario.

### 4.6 Future tool tests

When BODYSHOP eventually introduces state-changing or external tools, testing must use mocks.

Policy:

```text
MOCK AVAILABLE
→ run Tool Call Test

MOCK NOT AVAILABLE
→ finish with error
→ never substitute real operational execution
```

---

## 5. Agent Versioning and branches — post-A4 governance priority

### 5.1 What it solves

Provider-side versioning addresses a problem already observed in A4: manual configuration can evolve faster than repository evidence.

Desired evidence model:

```text
Git SHA
+ ElevenLabs agent version
+ Procedure versions
+ exact test run
= reproducible provider evidence
```

### 5.2 Capabilities

Current ElevenLabs versioning provides:

- immutable snapshots;
- isolated branches;
- merge;
- rebase;
- rollback;
- traffic percentage deployment.

### 5.3 Proposed BODYSHOP use

```text
provider/main
→ accepted sandbox baseline

provider/experiment-guardrails
→ one security variable

provider/experiment-structured
→ one Procedure architecture variable

provider/experiment-llm-x
→ one model variable
```

No provider branch should be promoted until its exact configuration and tests are recorded.

### 5.4 Important documentation contradiction

The current narrative Versioning documentation states that versioning is opt-in and cannot be disabled once enabled. Other current API material has evolved around automatic version tracking.

BODYSHOP must verify the actual behavior of the current account before depending on a specific activation model.

---

## 6. ElevenLabs CLI / agents-as-code — post-A4 governance priority

### 6.1 Why this matters

The CLI can reduce fragile Dashboard copy/paste and create auditable configuration diffs.

Current official workflow includes:

```text
elevenlabs agents init
elevenlabs auth login
elevenlabs agents pull
elevenlabs agents push --dry-run
elevenlabs agents push
elevenlabs agents status
```

### 6.2 Target BODYSHOP model

```text
Git
│
├── provider agent configuration
├── tests
├── tool definitions later
└── documented expected provider state
        │
        ↓
ElevenLabs CLI --dry-run
        │
        ↓
review diff
        │
        ↓
explicit authorized push
```

This could remove the failure class:

```text
"the complete prompt / Procedure was not pasted"
```

### 6.3 Required caution: Procedures

Current official Procedures documentation explicitly states:

```text
The ElevenLabs CLI does not currently support managing procedures.
```

At the same time, the August 24 CLI release states that the full ElevenLabs API is exposed through CLI subcommands.

Therefore BODYSHOP must **not assume** that `agents pull/push` serializes Procedures correctly.

Required evaluation before adoption:

```text
1. pull current sandbox agent
2. inspect whether Procedures are present and complete
3. compare exact Procedure IDs / version IDs / content
4. make no provider write
5. test procedure-specific API/CLI operations separately
6. only then design deployment automation
```

Until proven, Procedures remain dashboard/API-managed rather than assumed to be covered by agents-as-code sync.

### 6.4 Security rule

Any future CLI automation must use secure credential storage or CI secrets.

Never commit:

```text
ELEVENLABS_API_KEY
provider secrets
auth tokens
```

---

## 7. Conversation Flow and VAD — A5 priority

Prompt quality cannot solve every acoustic or turn-taking problem.

ElevenLabs provides provider-level controls for:

```text
maximum conversation duration
silence timeout
soft timeout
interruptions
turn eagerness
VAD
```

### 7.1 `background_voice_detection`

The current agent schema includes:

```text
vad.background_voice_detection
```

with default `false`.

This is a high-priority A5 candidate because BODYSHOP environments can contain:

```text
primary caller
+ nearby workers
+ radio speech
+ machinery
+ reflections / echo
```

Proposed controlled A5 experiment:

```text
A5-VAD-BASELINE
background_voice_detection=false

A5-VAD-CANDIDATE
background_voice_detection=true
```

Everything else must remain identical.

Measure:

```text
false starts
background-speaker capture
missed caller speech
interruptions
turn latency
semantic transcript accuracy
```

### 7.2 Turn eagerness

Modes include eager, normal and patient behavior.

For guided industrial data collection, `patient` is a strong candidate because operators may need to look at an installation, robot or component before answering.

Do not change this during A4 semantic validation.

### 7.3 Silence timeout

ElevenLabs recommends moderate waits for information-collection use cases.

BODYSHOP should test rather than assume a value.

Candidate matrix:

```text
10 s
12 s
15 s
```

Metrics:

```text
premature reprompts
user frustration
call duration
missed continuation
```

### 7.4 Interruptions

Allowing interruption creates more natural conversation but may create clipping or partial-turn ambiguity.

A5 should compare:

```text
interruptions enabled
vs
interruptions disabled where message completion is critical
```

No global choice should be made without acoustic evidence.

---

## 8. Skip Turn system tool — A5 candidate

The Skip Turn system tool allows the agent to remain silent when the user needs a moment.

BODYSHOP example:

```text
Operator:
"Un segundo, voy a mirar qué brida es."

AI Control:
[remains silent]

Operator:
"Es la Z14."
```

This is preferable to repeated prompts such as:

```text
"¿Me puedes confirmar la brida?"
"¿Sigues ahí?"
```

Potential benefit:

- less pressure on the operator;
- fewer overlapping turns;
- less accidental interruption while inspecting equipment;
- more natural guided dialogue.

A4 currently keeps all tools disabled, so Skip Turn must be evaluated only in a later authorized block.

---

## 9. Knowledge Base — BODYSHOP domain catalog

### 9.1 Best initial use

Knowledge Base is suitable for domain-specific information such as:

- technical terminology;
- validated element families;
- aliases;
- identifier rules;
- controlled vocabularies;
- non-procedural reference data.

This makes it a natural future home for:

```text
BODYSHOP_ELEMENT_CATALOG_V1
BODYSHOP_VOICE_VOCABULARY_V1
```

### 9.2 Proposed element catalog schema

```text
element_type
aliases
identifier_required
identifier_pattern
parent_context_required
valid_examples
notes
source / owner
status
```

Example conceptually:

```text
brida
→ identifier_required = true

antorcha
→ identifier_required = false when machine/equipment context identifies it clearly
```

Only validated BODYSHOP knowledge should enter the catalog.

### 9.3 Full context first, not RAG

For a small critical catalog, use Knowledge Base `prompt` / Full Context mode first.

Reason:

```text
critical classification
→ should always be available
→ small enough to fit in context
```

RAG should be considered only when the library grows enough that full context becomes inefficient.

### 9.4 RAG later

RAG is appropriate for:

```text
large manuals
large troubleshooting libraries
large technical documentation sets
```

Current ElevenLabs documentation states that RAG adds roughly 250 ms of latency.

Therefore:

```text
small critical catalog → Full Context
large documentation    → evaluate RAG
```

---

## 10. Success Evaluation and Data Collection — post-A4 / shadow

### 10.1 Success Evaluation

Success Evaluation scores completed conversations against explicit criteria and returns success / failure / unknown with rationale.

Potential BODYSHOP criteria:

```text
identity_complete
slot_separation_preserved
uncertainty_not_promoted
no_guessing
operator_flow_guided
sandbox_no_real_action
technician_preclose_semantics_correct
```

Example criterion:

```text
Did AI Control avoid progressing past any explicitly uncertain critical value and ask only for confirmation or correction of that value?
```

Use this for post-call QA, not as live lifecycle authority.

### 10.2 Data Collection

Data Collection can extract structured values after a conversation.

Candidate fields:

```text
identity
model
installation
operation
element_type
element_ref
problem
uncertainty_detected
uncertainty_resolved
```

Important boundary:

```text
POST-CALL EXTRACTION != LIVE CONFIRMATION
```

A value extracted after the call must not retroactively justify a live decision that the agent should not have made.

### 10.3 Future shadow use

During shadow mode:

```text
conversation
→ provider analysis
→ BODYSHOP evaluation
→ compare agent understanding vs human ground truth
```

This could produce structured quality metrics without giving ElevenLabs lifecycle authority.

---

## 11. Spotlight and conversation analytics — later shadow / pilot

Once there are enough conversations, Spotlight can help discover recurring patterns that were not explicitly encoded as tests.

Potential findings:

```text
frequent operation-reference confusion
frequent installation repetition
certain element families causing clarification loops
pre-close phrases with low success
specific acoustic contexts with negative outcomes
```

Use Spotlight as a diagnostic discovery layer, not as an authoritative rule engine.

Any new rule discovered from analytics must still pass the normal BODYSHOP process:

```text
finding
→ validate domain meaning
→ define expected behavior
→ implement in correct owner
→ test
```

---

## 12. Pronunciation Dictionary and speech recognition boundary

### 12.1 Pronunciation Dictionary

Pronunciation dictionaries can improve how AI Control **speaks** domain terms, acronyms and identifiers.

Potential future examples:

```text
MIG
PAM
platform codes
operation prefixes
technical acronyms
```

### 12.2 Important limitation

Pronunciation dictionaries primarily influence TTS output.

They do not automatically solve the inverse problem:

```text
operator says technical identifier
→ ASR misrecognizes it
```

Therefore TTS pronunciation and ASR vocabulary must be treated as separate problems.

### 12.3 Future ASR research

ElevenLabs Scribe capabilities include domain-oriented speech recognition features outside the simple agent prompt model.

If A5 proves that technical identifiers are systematically misrecognized, investigate an ASR-specific vocabulary/keyterm architecture as a separate design decision rather than adding more prompt examples.

---

## 13. Guardrails 2.0 — security branch after semantic baseline

Guardrails is currently documented as Alpha.

It can add:

- system prompt hardening;
- focus enforcement;
- user input manipulation / prompt-injection detection;
- response validation;
- custom policies.

Potential BODYSHOP value:

```text
user attempts to override system policy
requests unsupported operational actions
tries to force final closure
tries to invent tools or external actions
```

Do not activate Guardrails before the semantic baseline is stable.

Reason:

```text
failure observed
→ must know whether cause is:
   prompt
   procedure
   model
   guardrail
```

Recommended later experiment:

```text
branch A: baseline
branch B: baseline + selected guardrail
same tests
compare false positives / safety gains
```

---

## 14. Structured Procedures — promising but defer

Structured Procedures run a fixed sequence of typed steps and are attractive for a guided BODYSHOP flow.

Conceptually:

```text
identity
→ model
→ installation
→ operation
→ element
→ problem
```

is a good candidate for deterministic step execution.

However, BODYSHOP currently uses Qwen in A4 and must not assume that every model provides the same forced-tool-choice guarantees used by Structured Procedures.

Recommended later experiment:

```text
BASELINE
Qwen + Free-form guided Procedure

CANDIDATE
supported model + Structured Procedure
```

Evaluate:

```text
slot accuracy
latency
interruptions
correction behavior
uncertainty handling
cost
voice naturalness
```

Do not change model and Procedure architecture in the same uncontrolled comparison.

---

## 15. Workflows — powerful but not justified yet

Workflows provide visual graph-based conversation control with branching and sub-agent behavior.

Potential future architecture:

```text
ENTRY
  │
  ├── OPERATOR REPORT
  │
  ├── TECHNICIAN RESOLUTION
  │
  ├── AMBIGUITY / FALLBACK
  │
  └── OTHER
```

They become useful when BODYSHOP needs real branching, distinct subagent responsibilities or per-node configuration.

Current A4 does not need this complexity.

Decision rule:

```text
If Procedures remain clear and testable
→ keep Procedures

If branching becomes complex and deterministic control is required
→ evaluate Workflow
```

---

## 16. DTMF input — future fallback

ElevenAgents now supports optional keypad input, including `#` as a terminator and redaction options.

Possible future fallback:

```text
AI Control:
"No puedo confirmar la referencia. Si quieres, introdúcela con el teclado y pulsa #."
```

Potential use cases:

```text
operation number
numeric equipment reference
PIN-like non-sensitive routing code
```

Do not introduce DTMF unless voice recognition data shows a real need.

If used, verify redaction and privacy behavior before any sensitive input.

---

## 17. Queueing — future scale control

ElevenAgents can queue callers when concurrency is exhausted instead of rejecting them immediately.

This is not important for A4, but may matter if multiple BODYSHOP callers eventually reach AI Control concurrently.

Future policy questions:

```text
maximum acceptable wait
fallback to human Control
queue timeout
priority rules
what the caller hears while waiting
```

Queueing must not become a hidden operational bottleneck.

---

## 18. Privacy and retention — mandatory pre-pilot gate

ElevenLabs retention is configurable separately for transcripts and audio. Current documentation states that the default conversation-data retention is two years.

Before any systematic use with real workers, BODYSHOP must explicitly define:

```text
transcript retention
audio retention
whether audio saving is enabled
personal-data handling
access controls
legal basis / transparency
purpose limitation
deletion policy
provider evidence requirements
```

The sandbox can retain synthetic evidence needed for A4 debugging, but production/pilot privacy must be designed separately.

No real-worker rollout should occur merely because the agent is technically functional.

---

## 19. Experiments — use after versioning maturity

Experiments are built on agent versioning and can route a portion of traffic to a variant.

Potential future comparisons:

```text
baseline vs background_voice_detection
baseline vs guardrail
Qwen vs alternative model
Free-form vs Structured Procedure
voice A vs voice B
Knowledge Base configuration A vs B
```

BODYSHOP should use experiments only after:

```text
stable baseline
clear metric
one controlled variable
sufficient sample
privacy / pilot authorization
```

Do not use live operational traffic as an uncontrolled experiment.

---

## 20. Recommended adoption sequence

### Stage 1 — close A4 exact semantic baseline

Use now:

```text
System Prompt V3
Operator breakdown V2
Element identification V1 sub-procedure
Technician pre-close V1
```

Then:

```text
publish exact configuration
→ record provider version / identifiers where safe
→ run focused native tests
→ run selected manual voice checks
```

Do not add Guardrails, Knowledge Base, tools, VAD experiments or another LLM before this is stable.

### Stage 2 — A4 native regression suite

Create:

```text
Next Reply tests
Simulation tests
repeat-run safety cases
```

Minimum first targets:

```text
identity completeness
known caller-role use
installation semantics
operation vs activity
uncertainty invariant
correction supersedes prior value
brida reference required
antorcha reference not fabricated
completion only when applicable data complete
technician REQUEST_PRE_CLOSE
multiple-breakdown ambiguity
never final technical closure
sandbox no-real-action
```

### Stage 3 — provider governance / agents-as-code

Separate authorized block:

```text
Versioning audit
CLI pull read-only
CLI dry-run
Procedure serialization/API audit
exact config reconciliation
Git SHA ↔ provider version evidence model
```

No automated deployment until the read-only reconciliation is proven.

### Stage 4 — A5 acoustic / turn-taking experiments

One variable at a time:

```text
background_voice_detection
turn eagerness
silence timeout
interruptions
Skip Turn
```

Test in representative workshop noise with explicit acoustic metrics.

### Stage 5 — BODYSHOP domain knowledge

Create a controlled small Knowledge Base:

```text
BODYSHOP Element Catalog
BODYSHOP Voice Vocabulary
```

Use Full Context first.

Move to RAG only when size / context pressure justifies it.

### Stage 6 — shadow analytics

Add only after semantic behavior is stable:

```text
Success Evaluation
Data Collection
Spotlight review
```

These remain observational and non-authoritative.

### Stage 7 — security and architectural experiments

Evaluate separately:

```text
Guardrails
Structured Procedures
alternative LLMs
Workflows
DTMF
queueing
```

Each experiment requires an explicit objective and acceptance criteria.

---

## 21. Capabilities deliberately NOT activated by this document

This document does not authorize:

```text
Knowledge Base
RAG
Guardrails
Structured Procedures
Workflows
Skip Turn
DTMF
queueing
CLI deployment
API deployment
MCP
webhook tools
client tools
code tools
model change
voice change
VAD change
privacy-policy change
real phone / SIP / Zello
Supabase
BODYSHOP production action
```

They remain candidates only.

---

## 22. Decision rules for future ElevenLabs changes

Before enabling any new provider capability, answer:

```text
1. What concrete BODYSHOP failure or need does it solve?
2. Which current owner should hold that responsibility?
3. Is ElevenLabs the correct layer for it?
4. Does it alter semantic behavior, audio behavior, security, persistence or external action?
5. What exact baseline is being compared?
6. What test proves improvement?
7. What test proves no regression?
8. Can the change be isolated to one variable?
9. What provider version actually executed the test?
10. What is the rollback path?
```

If these cannot be answered, do not enable the capability.

---

## 23. Evidence model target

Long-term provider evidence should move toward:

```text
GIT BASE SHA
GIT HEAD SHA
ELEVENLABS AGENT VERSION
PROCEDURE VERSION(S)
MODEL
VOICE
DYNAMIC VARIABLE TEST CONTEXT
TEST ID
RUN COUNT
PASS RATE
PROVIDER CONVERSATION / TEST REFERENCE
SAFETY BOUNDARY
```

Any provider configuration change that can affect behavior invalidates earlier provider-specific evidence for the new configuration.

---

## 24. Official source register

All research in this document is based on current official ElevenLabs sources reviewed on `2026-09-09`.

### Procedures

- Procedures overview: https://elevenlabs.io/docs/eleven-agents/customization/procedures
- Free-form Procedures: https://elevenlabs.io/docs/eleven-agents/customization/procedures/free-form-procedures
- Structured Procedures: https://elevenlabs.io/docs/eleven-agents/customization/procedures/structured-procedures
- August 24, 2026 changelog: https://elevenlabs.io/docs/changelog/2026/8/24

### Testing

- Agent Testing: https://elevenlabs.io/docs/eleven-agents/customization/agent-testing

### Versioning / experiments

- Agent Versioning: https://elevenlabs.io/docs/eleven-agents/operate/versioning
- Experiments: https://elevenlabs.io/docs/eleven-agents/operate/experiments

### CLI / provider configuration

- ElevenLabs CLI: https://elevenlabs.io/docs/eleven-agents/operate/cli
- CLI v1 announcement: https://elevenlabs.io/blog/elevenlabs-cli-v1

### Conversation / audio behavior

- Conversation Flow: https://elevenlabs.io/docs/eleven-agents/customization/conversation-flow
- System Tools: https://elevenlabs.io/docs/eleven-agents/customization/tools/system-tools
- Skip Turn: https://elevenlabs.io/docs/eleven-agents/customization/tools/system-tools/skip-turn
- August 2026 changelog index: https://elevenlabs.io/docs/changelog

### Knowledge

- Knowledge Base: https://elevenlabs.io/docs/eleven-agents/customization/knowledge-base
- RAG: https://elevenlabs.io/docs/eleven-agents/customization/knowledge-base/rag

### Analysis

- Conversation Analysis: https://elevenlabs.io/docs/eleven-agents/customization/agent-analysis
- Success Evaluation: https://elevenlabs.io/docs/eleven-agents/customization/agent-analysis/success-evaluation
- Data Collection: https://elevenlabs.io/docs/eleven-agents/customization/agent-analysis/data-collection

### Security / privacy

- Guardrails: https://elevenlabs.io/docs/eleven-agents/best-practices/guardrails
- Privacy: https://elevenlabs.io/docs/eleven-agents/customization/privacy
- Retention: https://elevenlabs.io/docs/eleven-agents/customization/privacy/retention

### Workflows and tools

- Workflows: https://elevenlabs.io/docs/eleven-agents/customization/agent-workflows
- Tools: https://elevenlabs.io/docs/eleven-agents/customization/tools

### Recent platform changes

- August 31, 2026 changelog: https://elevenlabs.io/docs/changelog/2026/8/31
- August 24, 2026 changelog: https://elevenlabs.io/docs/changelog/2026/8/24
- August 17, 2026 changelog: https://elevenlabs.io/docs/changelog/2026/8/17

---

## 25. Current project recommendation

The current project should remain deliberately narrow:

```text
FIRST
prove the exact A4 Procedures configuration

THEN
move semantic regression into native Agent Testing

THEN
establish provider versioning / agents-as-code governance

THEN
use A5 to evaluate industrial voice behavior

THEN
introduce domain knowledge and analytics
```

The goal is not to activate every ElevenLabs feature.

The goal is to use only the provider capabilities that measurably improve BODYSHOP while preserving:

```text
traceability
minimal complexity
safe failure
human authority
semantic correctness
provider isolation
reproducible evidence
```

---

## 26. Canonical-state impact

```text
No canonical-state update required
```

This document does not change BODYSHOP architecture, lifecycle authority, persistence, security ownership or production capabilities. It records provider capabilities and a controlled adoption path only.
