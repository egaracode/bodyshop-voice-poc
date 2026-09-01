# F400 Smoke Test Report V1

## 1. Objetivo

Validar de forma mínima y aislada que el dispositivo UNIWA F400 puede funcionar como terminal PoC/Zello para un laboratorio externo de voz relacionado con BODYSHOP PRO.

La prueba responde solo a esta pregunta:

```text
¿El canal básico F400 ↔ móvil mediante Zello funciona de forma suficientemente fiable para seguir explorando el flujo de voz?
```

## 2. Alcance

Incluido:

- arranque y uso básico del UNIWA F400;
- Google Play disponible;
- Zello disponible y operativo;
- comunicación bidireccional entre UNIWA F400 y móvil;
- validación manual del botón PTT;
- validación manual de funcionamiento en segundo plano y con pantalla apagada;
- clasificación del dispositivo como laboratorio externo.

Excluido:

- integración con `AI-Control-Workshop`;
- integración con Supabase;
- integración con Azure, Twilio, OpenAI Realtime, ElevenLabs u otros servicios de voz IA;
- uso en producción;
- uso en red corporativa;
- uso de datos reales;
- automatización con impacto operativo real;
- almacenamiento de audios reales en repositorio.

## 3. Dispositivo

```text
Fabricante / marca comercial: UNIWA
Modelo: F400
Tipo: 4G PoC Walkie Talkie / rugged Android PDA
Uso actual: laboratorio aislado
Estado de compra: comprado
```

Características relevantes observadas o confirmadas para esta prueba:

- Android 15;
- Google Play confirmado;
- Zello operativo;
- PoC/PTT físico;
- funcionamiento en segundo plano y pantalla apagada confirmado manualmente;
- altavoz frontal 2.5W;
- batería extraíble 4350 mAh;
- conectividad WiFi / datos móviles según especificación de compra;
- certificación CE/RED revisada externamente antes de registrar este smoke test.

## 4. Dispositivos de prueba

```text
Dispositivo A: UNIWA F400
Rol de laboratorio: técnico dummy / receptor PoC

Dispositivo B: móvil personal de pruebas
Rol de laboratorio: Control dummy / emisor PoC

Aplicación: Zello
```

## 5. Resultado de pruebas

| Prueba | Resultado |
|---|---|
| F400 encendido y operativo | PASS |
| Google Play confirmado | PASS |
| Zello operativo en F400 | PASS |
| F400 y móvil conectados a Zello | PASS |
| Comunicación de voz F400 → móvil | PASS |
| Comunicación de voz móvil → F400 | PASS |
| Botón PTT físico | PASS |
| Funcionamiento en segundo plano | PASS |
| Funcionamiento con pantalla apagada | PASS |
| Uso como terminal técnico dummy | PASS |

## 6. Evidencia manual

```text
Fecha: 2026-09-01
Ejecutor: Albert
Resultado declarado: PASS
Descripción: Albert confirma haber conectado el UNIWA F400 y su móvil mediante Zello, haber hablado entre dispositivos y haber completado las pruebas previstas con resultado PASS.
```

No se incorporan audios, vídeos ni datos reales al repositorio.

## 7. Clasificación

```text
VOICE_POC_F400_MANUAL_SMOKE_TEST_V1: PASS
```

El UNIWA F400 queda validado únicamente como dispositivo de laboratorio externo para comunicación PoC/Zello.

Esta validación no implica:

- autorización de producción;
- autorización de red corporativa;
- autorización de datos reales;
- autorización de integración con BODYSHOP PRO;
- autorización de automatización IA.

## 8. Riesgos y límites

Riesgos pendientes antes de cualquier uso más amplio:

- validar comportamiento en entorno ruidoso real o simulado;
- medir latencia de forma más objetiva;
- comprobar estabilidad durante sesiones largas;
- confirmar política de actualizaciones Android/Zello;
- revisar permisos de cámara, micrófono, GPS, NFC y apps preinstaladas;
- mantener separación total de datos reales y red corporativa.

## 9. Próximos pasos posibles

Solo después de mantener esta evidencia aislada:

1. documentar protocolo de mensajes dummy;
2. probar mensajes tipo avería sin datos reales;
3. probar ruido ambiente;
4. probar sesión prolongada;
5. estudiar integración de voz IA en un bloque separado.

## 10. Decisión final

```text
UNIWA F400 aprobado como hardware de laboratorio para BODYSHOP Voice PoC.
```

Punto de parada: no implementar integración ni automatización hasta nueva autorización explícita.
