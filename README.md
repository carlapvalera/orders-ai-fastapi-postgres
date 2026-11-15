# Orders AI API

Prueba técnica de Python, datos e IA. Requiere Python 3.14 para el desarrollo local, aunque la ejecución recomendada usa Docker.

## Qué pedía la prueba

1. Generar al menos 1.000 pedidos sintéticos con duplicados, fechas inválidas e importes vacíos; limpiarlos y cargarlos en una base SQL.
2. Crear dos vistas SQL: ventas por mes y país, y los 10 clientes que más compran.
3. Crear una API FastAPI que convierta preguntas en lenguaje natural a SQL mediante un LLM, valide la consulta y devuelva el resultado.
4. Añadir al menos tres tests con pytest.
5. Documentar ejecución, decisiones, mejoras futuras y uso de IA.

## Arranque completo con Docker

El revisor no necesita instalar Python, PostgreSQL ni las dependencias del proyecto. Solo necesita Docker Desktop, una cuenta/clave de Fireworks y Git.

### Paso a paso desde un repositorio clonado

1. Clona el repositorio y entra en su carpeta:

```bash
git clone https://github.com/carlapvalera/orders-ai-fastapi-postgres.git
cd orders-ai-fastapi-postgres
```

2. Copia `.env.example` a `.env`:

```bash
cp .env.example .env
```

```env
FIREWORKS_API_KEY=tu_clave_de_Fireworks
FIREWORKS_MODEL=accounts/fireworks/models/glm-5p3-flash
```

La URL de PostgreSQL del `.env.example` usa credenciales locales de Docker; no es una clave real ni una credencial de producción.

3. Levanta PostgreSQL y la API:

```bash
docker compose up --build
```

El primer arranque puede tardar porque Docker construye la imagen e instala las dependencias. El contenedor de la API espera a que PostgreSQL esté saludable y después genera el CSV, limpia/carga los datos, crea las vistas y arranca FastAPI.

4. Comprueba que los servicios están activos:

```bash
docker compose ps
```

Ambos servicios deben aparecer como `running`; PostgreSQL debe aparecer como `healthy`.

5. Abre la documentación interactiva en [http://localhost:8000/docs](http://localhost:8000/docs), ejecuta `GET /health` y después `POST /ask` con:

```json
{
  "question": "¿Cuánto vendimos en España en marzo?"
}
```

PostgreSQL queda publicado en el puerto `5433` del equipo y usa el puerto `5432` dentro de la red Docker. La API queda publicada en el puerto `8000`.

### Comandos útiles de Docker

Para detener los servicios:

```bash
docker compose down
```

Para borrar también los datos persistidos de PostgreSQL:

```bash
docker compose down -v
```

Para ver logs:

```bash
docker compose logs -f api
docker compose logs -f db
```

Si los puertos `8000` o `5433` ya están ocupados, detén el proceso que los usa o cambia el puerto izquierdo en `docker-compose.yml`. Si aparece un problema de inicialización de PostgreSQL en un entorno local anterior, ejecuta `docker compose down -v` y vuelve a ejecutar `docker compose up --build`.

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

La carga produce `data/orders_clean.csv` y guarda en PostgreSQL `order_quality_summary` (resumen) y `order_quality_issues` (fila original, tipo de error y valores recibidos) para que los descartes sean auditables.

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
- documenta las respuestas `400`, `422`, `502` y `503` en Swagger;
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
- Tabla detallada `order_quality_issues` para filas rechazadas.
- Health check que verifica la conexión real con PostgreSQL.
- Validación explícita de `FIREWORKS_API_KEY` y `DATABASE_URL`.
- Normalización de países y meses entre español e inglés.
- Makefile con comandos de generación, carga y tests.
- Historial de commits progresivos y repositorio público.

## Uso de IA

Usé Fireworks AI para convertir preguntas en SQL y usé IA como apoyo para proponer la estructura, revisar validaciones y sugerir tests. Acepté el esqueleto inicial, pero corregí manualmente la limpieza, la seguridad SQL, la gestión de errores, la normalización de idiomas, el funcionamiento con PostgreSQL, la configuración Docker y la documentación. La decisión clave fue no ejecutar nunca SQL generado por el LLM sin validarlo previamente.

## Qué haría con más tiempo

Añadiría migraciones con Alembic, autenticación de la API, rate limiting, tests de integración de PostgreSQL dentro de CI, una tabla detallada de filas rechazadas, métricas y tracing, y consultas semánticas más estructuradas para reducir la dependencia de SQL libre generado por el LLM.
