🗄️ FASE 7 · Integración de datos: BBDD y API (sintetiza L7) — 7h

Contexto: Los datos en memoria se pierden al cerrar. El despachador necesita persistencia real y contexto externo de la ruta.

Actividades detalladas:

1. **Persistencia SQLite:** esquema de tablas (shipments, sucursales, logs), migración inicial y capa de acceso en models/. Alta/consulta/actualización/borrado (CRUD) completos.

2. **Consumo de API externa:** un RouteApiClient que enriquece cada envío con datos externos (p. ej. distancia/geocodificación de la dirección o clima de la ruta) vía httpx/requests.

3. **Manejo de errores de red:** timeouts, reintentos y un estado “sin conexión” visible; la app sigue usable con los datos locales aunque la API falle.

4. **Integración con async (L4):** la llamada a la API corre en segundo plano con su indicador de carga; el resultado se cachea en SQLite.

5. **Entregable de la fase:** app que persiste envíos entre reinicios y muestra datos enriquecidos por la API; docs/06-datos.md con el esquema de la BBDD, el contrato de la API y la estrategia de manejo de fallos.

Bonus +50 XP: Modo offline con cola de cambios pendientes en SQLite que se sincronizan al recuperar conexión.
