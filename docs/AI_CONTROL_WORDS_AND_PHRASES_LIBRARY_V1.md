# AI Control Words and Phrases Library V1

## 1. Objetivo

Crear una primera biblioteca controlada de palabras, expresiones y frases para que una futura IA-Control pueda entender y responder dentro del laboratorio `bodyshop-voice-poc`.

Esta biblioteca nace del flujo real mínimo ya documentado en `docs/REAL_BREAKDOWN_VOICE_FLOW_V1.md`.

La pregunta que responde este documento es:

```text
¿Qué vocabulario y qué frases mínimas debe reconocer o decir IA-Control para simular una avería por voz sin automatizar nada todavía?
```

## 2. Alcance

Incluido:

- vocabulario base del flujo Operario -> IA-Control -> Técnico dummy;
- frases de apertura de avería;
- frases para pedir datos que faltan;
- frases para confirmar la avería;
- frases para avisar al técnico dummy por Zello/F400;
- frases que el técnico dummy puede responder;
- frases de solicitud de ayuda;
- frases de resolución;
- frases de pre-cierre;
- recordatorio de documentación y cierre final por técnico;
- palabras prohibidas o peligrosas para V1.

Excluido:

- implementación de IA;
- prompts de sistema definitivos;
- integración con Zello API;
- integración con Azure, Twilio, OpenAI Realtime, ElevenLabs u otros servicios;
- integración con `AI-Control-Workshop`;
- Supabase;
- código;
- automatización;
- producción;
- red corporativa;
- datos reales;
- nombres reales de operarios o técnicos.

## 3. Principios de lenguaje para IA-Control

IA-Control debe hablar como Control, pero con frases cortas, verificables y seguras.

Reglas de estilo:

```text
1. Una pregunta cada vez.
2. Frases cortas.
3. Confirmar datos críticos antes de avisar al técnico.
4. No usar nombres reales en documentos ni pruebas públicas.
5. No prometer automatizaciones reales.
6. No cerrar definitivamente una avería en nombre del técnico.
7. Usar siempre "pre-cerrar" para la acción de Control.
8. Recordar que el técnico documenta y cierra definitivamente.
```

## 4. Roles y términos base

| Término | Significado V1 | Uso permitido |
|---|---|---|
| Operario dummy | Persona de prueba que detecta la avería. | Sí |
| IA-Control | Control representado por IA en el PoC. | Sí |
| Técnico dummy | Receptor de prueba por Zello/F400. | Sí |
| Control | Rol operativo que coordina el flujo. | Sí |
| UNIWA F400 | Terminal PoC/Zello del técnico dummy. | Sí |
| Zello | Canal PoC/walkie usado en laboratorio. | Sí |
| Avería | Incidencia comunicada por operario o técnico. | Sí |
| Pre-cierre | Acción de Control tras resolución física. | Sí |
| Cierre final | Acción del técnico tras documentar. | Sí |
| Producción | Uso real operativo. | No en V1 |
| Red corporativa | Red real de empresa/planta. | No en V1 |
| Datos reales | Información operativa real. | No en V1 |

## 5. Datos mínimos que IA-Control debe recoger

| Campo | Pregunta recomendada | Ejemplo dummy |
|---|---|---|
| Nombre y apellido | Hola, ¿me puedes decir nombre y apellido? | Operario Dummy |
| Modelo | ¿Desde qué modelo llamas? | PQ27 |
| Instalación | ¿Desde qué instalación llamas? | Lateral Derecho |
| Operación | ¿Desde qué operación llamas? | OP240 |
| Problema | ¿Qué problema tienes? | Un detector de la mesa de trabajo no funciona |

En V1, estos datos son suficientes para simular el aviso por voz.

## 6. Vocabulario de ubicación

Palabras que IA-Control debe reconocer como posibles datos de localización:

| Palabra o frase | Tipo | Ejemplo de uso |
|---|---|---|
| modelo | Campo de ubicación | Modelo PQ27 |
| instalación | Campo de ubicación | Instalación Lateral Derecho |
| operación | Campo de ubicación | Operación OP240 |
| OP | Abreviatura de operación | OP240 |
| línea | Ubicación general | Estoy en la línea |
| lateral derecho | Instalación dummy | Lateral Derecho |
| lateral izquierdo | Instalación posible | Lateral Izquierdo |
| mesa de trabajo | Zona / elemento | Detector de la mesa de trabajo |
| detector | Elemento de problema | Un detector no funciona |
| estación | Ubicación genérica | Estoy en la estación |
| zona | Ubicación genérica | Estoy en esta zona |

## 7. Vocabulario de problema

Palabras y expresiones que pueden aparecer en la descripción del operario:

| Palabra o frase | Interpretación V1 |
|---|---|
| no funciona | Fallo general |
| no detecta | Posible problema de sensor/detector |
| detector no funciona | Problema de detector |
| mesa de trabajo | Zona del problema |
| fallo | Avería genérica |
| avería | Incidencia comunicada |
| se ha parado | Posible línea parada, futuro campo |
| no responde | Fallo general |
| no marca | Posible fallo de señal |
| no entra | Posible problema mecánico o secuencia |
| no sale | Posible problema mecánico o secuencia |
| error | Fallo genérico |
| alarma | Señal de fallo |

En V1, IA-Control no debe diagnosticar técnicamente. Solo debe recoger, resumir y avisar.

## 8. Vocabulario de acción

| Acción | Quién la realiza | Uso V1 |
|---|---|---|
| llamar | Operario o técnico | Sí |
| preguntar | IA-Control | Sí |
| recoger datos | IA-Control | Sí |
| registrar verbalmente | IA-Control | Sí, simulado |
| avisar | IA-Control | Sí |
| asignar | IA-Control / Control | Simulado |
| acercarse | Técnico dummy | Sí |
| confirmar | Técnico dummy | Sí |
| intervenir | Técnico dummy | Sí |
| pedir ayuda | Técnico dummy | Sí |
| solucionar | Técnico dummy | Sí |
| pre-cerrar | IA-Control / Control | Sí |
| documentar | Técnico dummy | Sí |
| cerrar definitivamente | Técnico dummy | Sí |

## 9. Frases de apertura permitidas

IA-Control puede iniciar la llamada con frases como:

```text
Hola, soy Control. ¿Me puedes decir nombre y apellido?
```

```text
Hola, te atiende Control. ¿Me dices nombre y apellido?
```

```text
De acuerdo, dime nombre y apellido para abrir la avería.
```

Frase preferida V1:

```text
Hola, soy Control. ¿Me puedes decir nombre y apellido?
```

## 10. Frases para recoger ubicación

IA-Control debe pedir modelo, instalación y operación de forma simple.

Frase preferida:

```text
¿Me puedes decir desde qué modelo, instalación y operación llamas?
```

Variantes permitidas:

```text
¿Desde qué modelo llamas?
```

```text
¿Desde qué instalación llamas?
```

```text
¿Desde qué operación llamas?
```

```text
Dime modelo, instalación y operación, por favor.
```

## 11. Frases para recoger el problema

Frase preferida:

```text
¿Qué problema tienes?
```

Variantes permitidas:

```text
¿Qué avería tienes?
```

```text
¿Qué está fallando?
```

```text
Explícame brevemente qué ocurre.
```

```text
¿Qué no funciona?
```

## 12. Frases de confirmación antes de avisar

IA-Control debe confirmar de forma breve antes de avisar al técnico.

Frase preferida:

```text
De acuerdo, te mando un técnico disponible.
```

Variantes permitidas:

```text
OK, aviso a un técnico disponible.
```

```text
Recibido, preparo el aviso al técnico.
```

```text
De acuerdo, paso el aviso al técnico.
```

No debe decir todavía:

```text
La avería queda resuelta.
```

```text
La avería queda cerrada.
```

## 13. Frases para datos incompletos

Si falta el nombre:

```text
Necesito tu nombre y apellido para continuar.
```

Si falta el modelo:

```text
Me falta el modelo. ¿Desde qué modelo llamas?
```

Si falta la instalación:

```text
Me falta la instalación. ¿Desde qué instalación llamas?
```

Si falta la operación:

```text
Me falta la operación. ¿Qué OP es?
```

Si falta el problema:

```text
Me falta saber qué problema tienes.
```

Si no entiende:

```text
No lo he entendido bien. Repítemelo más corto, por favor.
```

## 14. Frases de resumen de avería

IA-Control puede resumir así:

```text
Recibido: avería en PQ27, Lateral Derecho, OP240. Problema: detector de mesa de trabajo no funciona.
```

Plantilla general:

```text
Recibido: avería en [modelo], [instalación], [operación]. Problema: [descripción breve].
```

Regla:

```text
El resumen debe contener ubicación y problema. Si falta uno, IA-Control debe preguntar antes de avisar.
```

## 15. Frases de aviso al técnico por Zello/F400

Frase preferida:

```text
De Control a Técnico Dummy.
```

Respuesta esperada del técnico:

```text
Dime Control.
```

Aviso preferido:

```text
Necesito que te acerques al Lateral Derecho de PQ27, OP240. Tienen un detector que no funciona.
```

Plantilla general:

```text
Necesito que te acerques a [instalación] de [modelo], [operación]. Tienen [problema].
```

Confirmación esperada:

```text
OK, voy.
```

## 16. Frases reconocidas del técnico

IA-Control debe aceptar como confirmación de recepción:

```text
Dime Control.
```

```text
OK, voy.
```

```text
Recibido, voy.
```

```text
Voy para allí.
```

```text
Ahora voy.
```

```text
Estoy en camino.
```

IA-Control debe aceptar como solicitud de ayuda:

```text
Necesito ayuda.
```

```text
Necesito que me envíes un técnico robótico.
```

```text
Necesito un técnico robótico.
```

```text
Mándame apoyo.
```

```text
Necesito apoyo.
```

IA-Control debe aceptar como resolución física:

```text
Puedes pre-cerrar la avería.
```

```text
Ya está solucionada.
```

```text
La avería está solucionada.
```

```text
Puedes dejarla pre-cerrada.
```

```text
He solucionado la avería.
```

## 17. Frases para solicitud de ayuda

Cuando el técnico pide ayuda, IA-Control debe responder sin sobreautomatizar.

Frase preferida:

```text
De acuerdo, te envío un técnico robótico disponible.
```

Variantes permitidas:

```text
Recibido, aviso a un técnico robótico disponible.
```

```text
OK, preparo apoyo robótico.
```

```text
Entendido, mando apoyo técnico disponible.
```

Regla V1:

```text
La solicitud de ayuda se documenta como conversación. No se implementa transferencia real ni reasignación real.
```

## 18. Frases de resolución y pre-cierre

Frase del técnico:

```text
Puedes pre-cerrar la avería, ya está solucionada.
```

Respuesta correcta de IA-Control:

```text
De acuerdo, dejo la avería pre-cerrada. Documenta la solución y realiza el cierre final.
```

Variantes permitidas:

```text
Recibido, la dejo pre-cerrada. Recuerda documentar y cerrar definitivamente.
```

```text
OK, avería pre-cerrada. Falta documentación técnica y cierre final.
```

Regla crítica:

```text
IA-Control puede pre-cerrar, pero no debe decir que ha cerrado definitivamente la avería.
```

## 19. Frases prohibidas en V1

IA-Control no debe decir:

```text
La avería queda cerrada definitivamente.
```

```text
Ya he cerrado la avería por ti.
```

```text
No hace falta que documentes nada.
```

```text
Esto ya está en producción.
```

```text
He actualizado BODYSHOP PRO.
```

```text
He cambiado Supabase.
```

```text
He avisado a un técnico real.
```

```text
He usado datos reales.
```

```text
Estoy conectado a la red corporativa.
```

Motivo:

```text
V1 es laboratorio aislado. No hay producción, datos reales, Supabase ni integración operativa.
```

## 20. Intenciones mínimas para futura IA-Control

Esta biblioteca no implementa IA, pero sí define intenciones conversacionales futuras.

| Intent | Qué significa | Ejemplo |
|---|---|---|
| `operator_identity` | El operario dice quién es. | Soy Operario Dummy |
| `breakdown_location` | El operario da modelo, instalación y OP. | PQ27, Lateral Derecho, OP240 |
| `problem_description` | El operario describe el fallo. | Detector no funciona |
| `missing_data` | Falta un dato obligatorio. | Me falta la operación |
| `assignment_notice` | IA-Control avisa al técnico. | Necesito que te acerques... |
| `technician_ack` | Técnico confirma recepción. | OK, voy |
| `support_request` | Técnico pide ayuda. | Necesito un técnico robótico |
| `physical_resolution` | Técnico comunica que ha solucionado. | Ya está solucionada |
| `pre_close` | Control pre-cierra. | Dejo la avería pre-cerrada |
| `final_close_reminder` | IA recuerda documentar/cerrar. | Documenta y realiza el cierre final |
| `unclear_input` | IA no entiende. | Repítemelo más corto |

## 21. Diccionario de equivalencias habladas

| Puede decirse | IA-Control debe entenderlo como |
|---|---|
| OP | Operación |
| op dos cuarenta | OP240 |
| lateral derecho | Instalación Lateral Derecho |
| detector | Elemento con fallo |
| no va | No funciona |
| no chuta | No funciona, expresión coloquial |
| se queda parado | Posible fallo / línea parada futura |
| mándame alguien | Solicitud de técnico disponible |
| manda robótico | Solicitud de técnico robótico |
| está solucionado | Resolución física |
| puedes cerrar | En V1 debe tratarse como petición de pre-cierre, no cierre final |

## 22. Regla especial: "puedes cerrar"

En el habla real, un técnico puede decir:

```text
Puedes cerrar la avería.
```

Pero en la lógica funcional documentada para este laboratorio debe interpretarse como:

```text
El técnico pide a Control que pre-cierre la avería porque la resolución física ya está hecha.
```

Respuesta segura de IA-Control:

```text
De acuerdo, la dejo pre-cerrada. Documenta la solución y realiza el cierre final.
```

No responder:

```text
La cierro definitivamente.
```

## 23. Plantillas de conversación V1

### 23.1 Apertura completa

```text
IA-Control: Hola, soy Control. ¿Me puedes decir nombre y apellido?
Operario dummy: Soy Operario Dummy.
IA-Control: ¿Me puedes decir desde qué modelo, instalación y operación llamas?
Operario dummy: PQ27, Lateral Derecho, OP240.
IA-Control: ¿Qué problema tienes?
Operario dummy: Tengo un detector de la mesa de trabajo que no funciona.
IA-Control: Recibido: avería en PQ27, Lateral Derecho, OP240. Problema: detector de mesa de trabajo no funciona. Te mando un técnico disponible.
```

### 23.2 Aviso al técnico

```text
IA-Control: De Control a Técnico Dummy.
Técnico dummy: Dime Control.
IA-Control: Necesito que te acerques al Lateral Derecho de PQ27, OP240. Tienen un detector que no funciona.
Técnico dummy: OK, voy.
```

### 23.3 Solicitud de ayuda

```text
Técnico dummy: De Técnico Dummy a Control.
IA-Control: Dime.
Técnico dummy: Necesito que me envíes un técnico robótico.
IA-Control: De acuerdo, te envío un técnico robótico disponible.
```

### 23.4 Resolución y pre-cierre

```text
Técnico dummy: De Técnico Dummy a Control.
IA-Control: Dime.
Técnico dummy: Puedes pre-cerrar la avería, ya está solucionada.
IA-Control: De acuerdo, dejo la avería pre-cerrada. Documenta la solución y realiza el cierre final.
```

## 24. Criterio PASS para esta biblioteca

La biblioteca se considera útil si permite preparar pruebas de voz donde IA-Control pueda:

- iniciar una llamada de avería;
- pedir datos mínimos;
- detectar datos incompletos;
- resumir la avería;
- avisar al técnico dummy;
- entender confirmación del técnico;
- entender solicitud de ayuda;
- entender resolución física;
- aplicar correctamente la regla de pre-cierre;
- recordar documentación y cierre final por técnico.

## 25. Decisión final

```text
AI_CONTROL_WORDS_AND_PHRASES_LIBRARY_V1: DOCUMENTED
```

La siguiente pieza natural será decidir si esta biblioteca se divide en:

```text
1. protocolo de mensajes Zello/F400;
2. pruebas manuales de conversación;
3. futuro prompt controlado para IA-Control.
```

Punto de parada: no implementar IA, no automatizar, no usar Zello API y no conectar con BODYSHOP PRO hasta una autorización separada.
