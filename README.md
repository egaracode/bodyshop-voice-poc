# BODYSHOP Voice PoC

> **CURRENT AUTHORITY STATUS**
>
> This repository is a **laboratory / historical evidence / provenance repository**.
> It is **not** the current normative owner of BODYSHOP Voice product semantics or the current productive ElevenLabs target.
>
> Current BODYSHOP Voice authority lives in `egaracode/AI-Control-Workshop`, including:
>
> - `docs/DATA_CONTRACTS/VOICE_OPERATOR_INTAKE_CONTRACT_V1.md`
> - `src/services/voiceOperatorIntakePolicy.ts`
> - `scripts/voice/elevenlabsProviderTarget.ts`
>
> See `docs/VOICE_AUTHORITY_STATUS_V1.md` before using any historical document, JSON or tool in this repository.

Laboratorio externo y aislado para validar comunicación de voz, PoC walkie, Zello y evidencia histórica relacionada con BODYSHOP PRO.

## Propósito actual

Este repositorio conserva y permite consultar:

- evidencia histórica UNIWA F400;
- Zello / PoC walkie;
- comunicación bidireccional de voz;
- experimentos de proveedor de voz;
- snapshots históricos de configuración ElevenLabs;
- scripts y tests históricos de laboratorio;
- decisiones y razonamientos de diseño que sirven como provenance.

El repositorio puede alojar nuevos experimentos de laboratorio únicamente mediante un Issue autorizado y claramente acotado.

## Fuera de alcance

Este repositorio no es el runtime ni la autoridad normativa de BODYSHOP PRO y no autoriza por sí mismo:

- cambios de semántica Voice de producto;
- cambios del catálogo canónico;
- creación o modificación del lifecycle;
- uso en Production;
- uso de datos reales protegidos;
- integración o mutación de Supabase;
- escrituras o publicaciones en ElevenLabs;
- despliegues productivos;
- automatización con impacto real.

La existencia de un script histórico, JSON expected-state, test o documento en este repositorio **no equivale a autorización para ejecutarlo ni a que siga describiendo el target productivo actual**.

## Relación con AI-Control-Workshop

`egaracode/AI-Control-Workshop` es la única fuente canónica de BODYSHOP PRO y del contrato Voice vigente.

Los artefactos de este repositorio deben clasificarse como:

- `LAB`;
- `HISTORICAL / PROVENANCE`;
- `SUPERSEDED AS PRODUCT AUTHORITY`;

salvo que un futuro Issue autorizado defina explícitamente un nuevo experimento de laboratorio.

Cualquier cambio productivo de Voice debe comenzar en el MASTER, seguir su bootstrap/gobernanza y derivar desde allí cualquier target de proveedor.

## Evidencia histórica inicial

- Dispositivo principal del laboratorio inicial: UNIWA F400.
- Aplicación de comunicación: Zello.
- Prueba manual F400 ↔ móvil: PASS.
- PTT físico / segundo plano / pantalla apagada: PASS, según validación manual de Albert.
- Uso histórico autorizado: laboratorio aislado.

Estos puntos conservan valor histórico y no constituyen por sí solos estado productivo actual.
