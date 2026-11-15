# Orders AI API

Prueba técnica de Python, datos e IA. Requiere Python 3.14 para el desarrollo local, aunque la ejecución recomendada usa Docker.

## Qué pedía la prueba

1. Generar al menos 1.000 pedidos sintéticos con duplicados, fechas inválidas e importes vacíos; limpiarlos y cargarlos en una base SQL.
2. Crear dos vistas SQL: ventas por mes y país, y los 10 clientes que más compran.
3. Crear una API FastAPI que convierta preguntas en lenguaje natural a SQL mediante un LLM, valide la consulta y devuelva el resultado.
4. Añadir al menos tres tests con pytest.
5. Documentar ejecución, decisiones, mejoras futuras y uso de IA.

## Arranque completo con Docker

1. Copia `.env.example` a `.env` y añade tu clave de Fireworks:

```bash
cp .env.example .env
```

```env
FIREWORKS_API_KEY=tu_clave_de_Fireworks
FIREWORKS_MODEL=accounts/fireworks/models/glm-5p3-flash
```

La URL de PostgreSQL del `.env.example` usa credenciales locales de Docker; no es una clave real ni una credencial de producción.

2. Levanta PostgreSQL y la API, genera el CSV, limpia los datos, crea las vistas y arranca FastAPI:

```bash
docker compose up --build
```

La API queda disponible en [http://localhost:8000/docs](http://localhost:8000/docs). PostgreSQL queda publicado en el puerto `5433` del equipo y usa el puerto `5432` dentro de la red Docker.

Para detener los servicios:

```bash
docker compose down
```

Para borrar también los datos persistidos de PostgreSQL:

```bash
docker compose down -v
```

## Desarrollo local sin Docker para la API

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
docker compose up -d db
python scripts/generate_data.py
python -m scripts.load_data
uvicorn app.main:app --reload
```

En desarrollo local, `.env` debe usar `localhost:5433`. La aplicación carga `.env` automáticamente mediante `python-dotenv`.

## Ejemplo de uso

En Swagger, ejecuta `POST /ask` con:

```json
{
  "question": "¿Cuánto vendimos en España en marzo?"
}
```

También puedes usar curl:

```bash
curl -X POST http://localhost:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"¿Cuánto vendimos en España en marzo?"}'
```

El proyecto soporta preguntas en español e inglés mediante un glosario de países y meses en el prompt. Por ejemplo, `Spain` y `España` se normalizan al valor canónico `España` usado en el dataset.

## Datos y limpieza

`generate_data.py` crea 1.225 filas deterministas: 1.200 pedidos base, 25 duplicados, 20 fechas inválidas y 20 importes vacíos. `load_data.py` convierte fechas e importes, normaliza texto, elimina duplicados y descarta filas irrecuperables.

La carga produce `data/orders_clean.csv` y guarda en PostgreSQL la tabla `order_quality_summary`, con filas de entrada, errores detectados, duplicados eliminados y filas finales.

## Vistas SQL

Se crean en `sql/views.sql`:

- `sales_by_month_country`: ventas y número de pedidos por mes y país; `month` usa formato `YYYY-MM`.
- `top_customers`: los diez clientes con mayor gasto, excluyendo pedidos cancelados.

PostgreSQL se eligió porque es una base relacional habitual en backend y permite demostrar tablas, agregaciones y vistas SQL. MongoDB no aportaba ventaja para este requisito analítico.

## API, LLM y seguridad

La API usa Fireworks AI mediante su endpoint compatible con OpenAI. El LLM solo propone SQL. Antes de ejecutar, la API:

- exige una única sentencia `SELECT`;
- analiza el SQL con `sqlglot` usando el dialecto PostgreSQL;
- permite únicamente las vistas autorizadas;
- rechaza operaciones peligrosas, comentarios y nombres cualificados;
- aplica timeout y reintentos limitados al proveedor;
- devuelve errores claros si falla el LLM, la validación o la ejecución;
- registra errores sin escribir claves ni secretos en logs.

La clave se lee de `FIREWORKS_API_KEY` y `.env` está excluido del repositorio.

## Tests y calidad

```bash
pytest -q
```

Hay 8 tests: limpieza de datos, validación SQL, endpoint con LLM simulado, fallo del LLM y rechazo de SQL inválido. GitHub Actions ejecuta los tests automáticamente en cada push y pull request.

## Mejoras añadidas además de la prueba

- Dockerfile y Docker Compose para levantar API y PostgreSQL juntos.
- CI con GitHub Actions y Python 3.14.
- Parser SQL real con `sqlglot`.
- Contrato de respuesta FastAPI con Pydantic.
- Timeout y reintentos limitados para Fireworks.
- Logging seguro de errores.
- Tabla auditable `order_quality_summary`.
- Normalización de países y meses entre español e inglés.
- Makefile con comandos de generación, carga y tests.
- Historial de commits progresivos y repositorio público.

## Uso de IA

Usé Fireworks AI para convertir preguntas en SQL y usé IA como apoyo para proponer la estructura, revisar validaciones y sugerir tests. Acepté el esqueleto inicial, pero corregí manualmente la limpieza, la seguridad SQL, la gestión de errores, la normalización de idiomas, el funcionamiento con PostgreSQL, la configuración Docker y la documentación. La decisión clave fue no ejecutar nunca SQL generado por el LLM sin validarlo previamente.

## Qué haría con más tiempo

Añadiría migraciones con Alembic, autenticación de la API, rate limiting, tests de integración de PostgreSQL dentro de CI, una tabla detallada de filas rechazadas, métricas y tracing, y consultas semánticas más estructuradas para reducir la dependencia de SQL libre generado por el LLM.
