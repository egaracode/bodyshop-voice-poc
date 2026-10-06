# `elevenlabs/` — Historical provider configuration evidence

## Current status

Files in this directory are **historical provider snapshots / expected-state evidence**.

They are not the current productive BODYSHOP Voice authority.

Current productive Voice semantics and provider-target derivation live in:

```text
egaracode/AI-Control-Workshop
docs/DATA_CONTRACTS/VOICE_OPERATOR_INTAKE_CONTRACT_V1.md
src/services/voiceOperatorIntakePolicy.ts
scripts/voice/elevenlabsProviderTarget.ts
```

## Interpretation rule

A JSON file in this directory may accurately record:

- a historical expected provider state;
- a Gate-2 staging target;
- a Gate-3 corrective target;
- a Client Tool contract used in a completed historical block.

That does **not** mean the file remains the current provider target.

Names such as:

```text
EXPECTED_PROVIDER_CONFIGURATION
GATE2
GATE3
V1
V2
```

are historical identifiers, not current-authority markers.

## Do not

Do not:

- use one of these JSONs as the sole source for a new productive provider change;
- infer current ElevenLabs state from a historical JSON;
- rewrite old JSONs to make them look current;
- delete historical snapshots merely because the MASTER has superseded them.

## Future provider work

For productive BODYSHOP Voice work:

```text
MASTER contract
→ MASTER-derived provider target
→ current provider/version verification
→ authorized provider action
```

Historical JSONs may still be used as provenance or comparison evidence.

Any external-provider claim must be revalidated against current first-party documentation before reuse.
