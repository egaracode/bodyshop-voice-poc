# Block-Oriented Working Method V1

## 1. Purpose

Define how work should progress inside the isolated `bodyshop-voice-poc` laboratory without fragmenting coherent outcomes into unnecessary micro-approval cycles.

This document complements, but does not override, BODYSHOP PRO repository discipline or Albert's final authority.

## 2. Core rule

Work progresses through **functional blocks**, not through arbitrary micro-steps.

A block groups the decisions, documentation and validation required to produce one coherent outcome.

Conceptually:

```text
need
→ diagnosis
→ block proposal
→ Albert authorization
→ Issue
→ branch
→ implementation/documentation
→ validation
→ Draft PR
→ review
→ Albert Ready decision
→ manual merge
→ post-merge verification
→ Issue closure
```

## 3. One coherent objective per block

Each block must preserve:

```text
one objective
one Issue
one branch
one PR
```

A block may contain several subordinate decisions when all of them are necessary to complete the same coherent objective.

Do not split a block merely because it contains multiple sections, files or small design choices.

Do split when a new request materially changes scope, architecture, safety, provider/runtime boundary or product behavior.

## 4. Assistant autonomy inside an authorized block

Once Albert authorizes a functional block, the assistant may resolve routine subordinate choices without asking for approval at every micro-step, provided those choices do not materially change:

- product behavior;
- architecture;
- scope;
- safety;
- privacy/data boundary;
- external provider/runtime boundary;
- repository sequencing;
- Ready/merge authority.

Examples of subordinate choices that normally do not require a new approval:

- document section organization;
- naming of internal headings;
- removing duplicate wording;
- choosing a concise clarification phrase consistent with the approved contract;
- grouping closely related acceptance criteria;
- selecting official sources that validate an already-authorized design question.

## 5. Mandatory stop conditions

Stop and return to Albert when evidence is insufficient or when a decision would materially alter:

```text
scope
architecture
product behavior
safety
privacy/data handling
external provider/runtime use
Supabase or canonical BODYSHOP integration
CI/workflows/dependencies/secrets
Ready
merge
```

Never use a micro-decision as a pretext to expand scope.

## 6. Repository discipline

The laboratory keeps the following discipline:

- do not work directly on `main`;
- no force-push;
- no auto-merge;
- Albert retains final Ready and merge authority;
- one active implementation block at a time unless Albert explicitly authorizes otherwise;
- preserve superseded branches/PR history when useful as evidence rather than rewriting history;
- do not weaken validation merely to obtain a green status.

## 7. Evidence hierarchy

For repository work, prefer evidence in this order:

```text
GitHub LIVE
→ current main content/configuration
→ active Issue contract
→ exact branch/head diff
→ exact CI/status evidence where applicable
→ official provider documentation
→ professional reference guidance
→ chat/handoff only as supporting context
```

If live evidence contradicts chat context, live evidence wins and the contradiction must be declared.

## 8. Official/professional source rule

Architecture and conversational recommendations should be contrasted with current official or professional sources whenever external technical behavior is involved.

For voice/AI-provider decisions, distinguish:

```text
what official documentation supports
what professional design guidance recommends
what BODYSHOP defines as its own domain rule
```

A source may validate feasibility or design quality, but it does not replace Albert's authority over BODYSHOP semantics.

## 9. ElevenLabs fit rule

When ElevenLabs is a likely future provider, each relevant design decision should be classified as:

```text
ELEVENLABS_NATIVE_FIT
ELEVENLABS_ADAPTER_REQUIRED
BODYSHOP_OWNED_DOMAIN_RULE
```

Definitions:

### ELEVENLABS_NATIVE_FIT

The required capability is documented as directly supported by ElevenLabs and can be evaluated/configured without transferring BODYSHOP domain authority to the provider.

### ELEVENLABS_ADAPTER_REQUIRED

The provider offers useful primitives, but BODYSHOP needs an external or surrounding adapter/gate to meet the requirement safely.

### BODYSHOP_OWNED_DOMAIN_RULE

The behavior represents workshop semantics, lifecycle authority or product policy and must remain controlled by BODYSHOP regardless of provider capabilities.

Provider-specific features and limits must be revalidated against official documentation before implementation.

## 10. Block validation

Before a block can be proposed for Ready, review the whole block as one unit:

- exact objective and scope;
- complete diff;
- acceptance criteria;
- contradictions;
- test/validation evidence;
- CI/status on the exact head where applicable;
- comments/reviews;
- residual risks;
- repository boundary;
- whether external provider claims are still current;
- whether the block accidentally expands into canonical BODYSHOP PRO.

A later change to the head invalidates prior exact-head validation evidence.

## 11. CI rule

If CI exists for the block, record:

```text
base SHA
head SHA
SHA actually executed
workflow/run
conclusion
head-vs-merge-ref evidence
```

More than three red CI results triggers STOP under BODYSHOP PRO governance unless Albert explicitly re-scopes the investigation.

For documentation-only laboratory blocks with no configured CI, state explicitly:

```text
CI: NOT CONFIGURED / NOT APPLICABLE
```

Do not invent validation evidence.

## 12. End-of-block report

At the end of each block, report at least:

- Issue;
- branch;
- PR;
- base SHA;
- head SHA;
- validated SHA;
- changed files;
- tests/validation performed;
- CI/status;
- contradictions;
- residual risks;
- exact stop point;
- decision still pending from Albert.

For canonical `AI-Control-Workshop` work, follow that repository's canonical documentation/update rules separately. This laboratory document does not modify them.

## 13. Public-laboratory data boundary

Because `bodyshop-voice-poc` is a public isolated laboratory repository, documentation and test artifacts must not introduce:

- real worker names;
- real sensitive operational data;
- production credentials;
- corporate-network information;
- secrets;
- real audio recordings containing protected data.

Use placeholders and dummy identities in versioned public artifacts.

## 14. Relationship to the Language Library

The language library may evolve continuously outside the implementation critical path.

Adding every newly observed phrase is not, by itself, a reason to open a separate implementation block.

When a language change materially alters canonical intent semantics, activation rules, safety or conversational behavior, it should be reviewed as part of the appropriate functional block.

## 15. Working-method acceptance

This method is considered documented when work can proceed as:

```text
coherent functional block
→ fewer unnecessary approval interruptions
→ explicit stop on material decisions
→ exact repository evidence
→ official/professional technical validation
→ Albert retains Ready and merge
```

## 16. Stop point

```text
BLOCK_ORIENTED_WORKING_METHOD_V1: DOCUMENTED
```

This document authorizes no implementation, provider integration, production action or merge by itself.
