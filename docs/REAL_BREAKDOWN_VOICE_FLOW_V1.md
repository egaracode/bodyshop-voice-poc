# Real Breakdown Voice Flow V1

## 1. Objetivo

Documentar el flujo real mínimo de una avería desde comunicación de operario hasta cierre final, únicamente para orientar el laboratorio `bodyshop-voice-poc`.

Este documento no define todavía una integración con BODYSHOP PRO. Sirve para transformar el flujo hablado real en futuros protocolos de voz, Zello y UNIWA F400.

Pregunta que responde este documento:

```text
¿Qué conversación real debe entender o simular una futura IA-Control antes de automatizar nada?
```

## 2. Alcance

Incluido:

- llamada inicial de operario a Control;
- datos mínimos que Control debe recoger;
- selección de técnico disponible según lista y especialidad;
- aviso a técnico por walkie/PoC;
- respuesta del técnico;
- resolución física;
- pre-cierre por Control;
- documentación técnica;
- cierre final por técnico;
- solicitud de ayuda técnica como variante simple;
- límites de V1.

Excluido:

- implementación de IA;
- integración con Zello API;
- integración con Azure, Twilio, OpenAI Realtime, ElevenLabs u otros servicios;
- integración con `AI-Control-Workshop`;
- cambios en BODYSHOP PRO;
- Supabase;
- código de aplicación;
- datos reales;
- red corporativa;
- producción;
- nombres reales de operarios o técnicos.

## 3. Principio principal del PoC

En este laboratorio, Control debe estar representado por IA, no por una persona humana.

```text
Operario
↓ llamada móvil
IA-Control
↓ mensaje por Zello / PoC
UNIWA F400
↓
Técnico dummy
```

La IA-Control futura debe ser capaz de mantener una conversación simple, pedir los datos necesarios, resumir la avería y emitir un aviso claro al técnico dummy.

## 4. Roles de V1

| Rol | Descripción |
|---|---|
| Operario dummy | Persona que detecta la avería en la instalación y llama por móvil. |
| IA-Control | Sustituto experimental de Control humano dentro del PoC. |
| Técnico dummy | Receptor del aviso por Zello/F400 y actor que confirma, interviene, pide ayuda o comunica resolución. |
| UNIWA F400 | Terminal PoC/Zello del técnico dummy. |
| Móvil de prueba | Terminal de llamada o comunicación auxiliar del operario/Control dummy según fase de prueba. |

No se usan nombres reales. Si en una conversación de diseño aparecen nombres de ejemplo, el documento público los sustituye por roles dummy.

## 5. Flujo real actual resumido

```text
1. El operario detecta una avería en una instalación.
2. El operario llama por móvil a Control.
3. Control pregunta nombre y apellido.
4. Control pregunta modelo, instalación y operación.
5. Control pregunta qué problema tiene.
6. Control decide un técnico disponible según lista y especialidad.
7. Control avisa al técnico por walkie talkie.
8. El técnico confirma que va a la avería.
9. El técnico interviene físicamente.
10. Si necesita ayuda, el técnico llama a Control por walkie.
11. Si resuelve la avería, el técnico llama a Control por walkie.
12. Control pre-cierra la avería.
13. El técnico documenta qué ha hecho.
14. El técnico cierra definitivamente la avería.
15. El ciclo queda totalmente cerrado.
```

## 6. Conversación de apertura: Operario -> Control

Versión normalizada para laboratorio:

```text
IA-Control:
Hola, ¿me puedes decir nombre y apellido?

Operario dummy:
Hola, soy Operario Dummy.

IA-Control:
¿Me puedes decir desde qué modelo, instalación y operación llamas?

Operario dummy:
Llamo de PQ27, Lateral Derecho, OP240.

IA-Control:
De acuerdo. ¿Qué problema tienes?

Operario dummy:
Tengo un detector de la mesa de trabajo que no funciona.

IA-Control:
De acuerdo, te mando un técnico disponible.

Operario dummy:
OK, gracias.
```

## 7. Datos mínimos que IA-Control debe recoger

Para V1, la IA-Control debe recoger como mínimo:

| Dato | Ejemplo dummy | Obligatorio V1 |
|---|---|---|
| Identidad del operario | Operario Dummy | Sí |
| Modelo | PQ27 | Sí |
| Instalación | Lateral Derecho | Sí |
| Operación | OP240 | Sí |
| Descripción del problema | Detector de mesa de trabajo no funciona | Sí |
| Línea parada | No decidido en este flujo V1 | Futuro |
| Área técnica | Inferida o seleccionada por Control/IA | Futuro |
| Técnico asignado | Técnico Dummy disponible | Sí para simulación |

En V1 no se debe forzar una clasificación técnica completa si todavía no está definida. La prioridad es comprobar la conversación y el aviso por voz.

## 8. Decisión de técnico

Regla mínima V1:

```text
IA-Control selecciona un técnico dummy disponible desde una lista simulada de técnicos y especialidades.
```

No se implementa todavía un algoritmo real de asignación. La selección puede ser manual, documentada o simulada.

Criterio de laboratorio:

```text
El mensaje de aviso debe decir claramente dónde ir y cuál es el problema.
```

## 9. Aviso al técnico: Control -> Técnico por walkie/PoC

Después de recoger la avería, la comunicación pasa a walkie/PoC.

Versión normalizada:

```text
IA-Control:
De Control a Técnico Dummy.

Técnico dummy:
Dime Control.

IA-Control:
Necesito que te acerques al Lateral Derecho de PQ27, OP240. Tienen un detector que no funciona.

Técnico dummy:
OK, voy.
```

Para el laboratorio, este mensaje se emitirá por Zello hacia el UNIWA F400.

## 10. Llegada e intervención

En el flujo hablado descrito para V1, no se detalla una frase obligatoria de llegada. La secuencia mínima queda así:

```text
1. Técnico confirma que va.
2. Técnico llega a la avería.
3. Técnico interviene físicamente.
```

La confirmación explícita de llegada o el botón de "Ya interviniendo" pertenecen a integración futura con BODYSHOP PRO, no a este documento de voz V1.

## 11. Resolución normal

Cuando el técnico resuelve físicamente la avería, vuelve a contactar con Control mediante walkie.

Versión normalizada:

```text
Técnico dummy:
De Técnico Dummy a Control.

IA-Control:
Dime.

Técnico dummy:
Puedes pre-cerrar la avería, ya está solucionada.

IA-Control:
De acuerdo, dejo la avería pre-cerrada. Documenta la solución y realiza el cierre final.
```

## 12. Regla de pre-cierre y cierre final

Esta es una regla funcional importante para V1:

```text
Control pre-cierra.
Técnico documenta.
Técnico cierra definitivamente.
```

Secuencia correcta:

```text
Técnico soluciona físicamente la avería
↓
Técnico avisa a Control por walkie
↓
Control pre-cierra la avería
↓
Técnico documenta qué ha hecho para solucionarla
↓
Técnico cierra definitivamente la avería
↓
Ciclo totalmente cerrado
```

La IA-Control no debe representar que cierra definitivamente la avería en nombre del técnico.

## 13. Solicitud de ayuda

Si el técnico necesita ayuda, vuelve a llamar a Control por walkie.

Versión normalizada:

```text
Técnico dummy:
De Técnico Dummy a Control.

IA-Control:
Dime.

Técnico dummy:
Necesito que me envíes un técnico robótico.

IA-Control:
De acuerdo, te envío un técnico robótico disponible.
```

En V1, esto solo se documenta como conversación. No se implementa transferencia, reasignación, segundo técnico real ni algoritmo de disponibilidad.

## 14. Variantes reales fuera de V1

Existen variantes del workflow real que se evaluarán más adelante. Por ejemplo:

```text
Un técnico puede llamar a Control para pedir que se abra una avería porque la ha detectado o solucionado estando ya en una instalación.
```

Estas variantes no forman parte de V1.

Clasificación:

```text
FUTURE_WORKFLOW_VARIANT_NOT_IN_V1
```

## 15. Traducción a Voice PoC

El flujo hablado se traduce al laboratorio así:

```text
Operario dummy llama o simula llamada a IA-Control
↓
IA-Control recoge datos mínimos
↓
IA-Control genera resumen de avería
↓
IA-Control avisa al técnico dummy por Zello/F400
↓
Técnico dummy confirma recepción
↓
Técnico dummy comunica resolución o pide ayuda
↓
IA-Control simula pre-cierre si procede
↓
Técnico dummy documentaría y cerraría en una integración futura
```

## 16. Mensajes mínimos derivados

Este documento habilita un siguiente bloque para crear un protocolo de mensajes dummy con estas familias:

| Familia | Propósito |
|---|---|
| Intake | Recoger datos del operario. |
| Assignment | Avisar al técnico dummy. |
| Acknowledgement | Confirmar recepción. |
| Support request | Pedir ayuda adicional. |
| Resolution | Comunicar resolución física. |
| Pre-close | Indicar que Control/IA pre-cierra. |
| Final close reminder | Recordar que el técnico debe documentar y cerrar. |

## 17. Límites de seguridad

Este documento mantiene los límites del laboratorio:

```text
No producción.
No red corporativa.
No datos reales.
No nombres reales.
No audio real en repositorio.
No integración con BODYSHOP PRO.
No Supabase.
No automatización con impacto real.
```

## 18. Criterio de aceptación V1

Este documento se considera correcto si permite entender:

- quién inicia la avería;
- qué datos pide Control;
- cómo se avisa al técnico;
- cómo responde el técnico;
- qué significa pedir ayuda;
- quién pre-cierra;
- quién documenta;
- quién cierra definitivamente;
- qué queda fuera de V1.

## 19. Decisión final

```text
REAL_BREAKDOWN_VOICE_FLOW_V1: DOCUMENTED
```

La siguiente pieza natural es:

```text
docs/ZELLO_DUMMY_MESSAGE_PROTOCOL_V1.md
```

Punto de parada: no implementar IA, automatización, Zello API ni integración con BODYSHOP PRO hasta una autorización separada.