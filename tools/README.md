# `tools/` — Historical and laboratory tooling

## Current status

Scripts in this directory are **historical/laboratory tooling**.

Their presence does not mean:

- their expected-state source is still current;
- their provider baseline is still current;
- their mutation command is currently authorized;
- they are the current productive deployment path.

Current BODYSHOP Voice product/provider authority lives in `egaracode/AI-Control-Workshop`.

## Historical value

These tools remain useful because they record:

- how prior provider state was inspected;
- how specific branches/staging blocks were executed;
- historical fail-closed guards;
- provider evidence collection;
- Issue-specific recovery logic;
- past exact-state assumptions.

That evidence must be preserved.

## Execution rule

Do not execute a historical provider tool solely because it exists here.

Before any future provider operation, require:

1. a current authorized Issue;
2. fresh GitHub and provider state;
3. current first-party provider documentation;
4. explicit classification of whether the objective is LAB or productive BODYSHOP work;
5. for productive Voice work, a target derived from the MASTER;
6. Albert authorization for every required sensitive/provider write boundary.

## No silent reuse

If a historical script embeds or expects:

- old agent fingerprints;
- old branch/version fingerprints;
- old Procedure semantics;
- old expected-state JSONs;
- old feature-maturity assumptions;

treat those as historical preconditions, not current facts.

Prefer a new bounded tool in the correct authority repository rather than modifying an old historical executor until its provenance becomes unclear.
