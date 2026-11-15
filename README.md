# Orders AI API

Prueba técnica: generación y limpieza de pedidos, vistas analíticas y una API FastAPI que convierte preguntas en lenguaje natural a consultas SQL mediante un LLM.

## Ejecución

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
docker compose up -d db
python scripts/generate_data.py
python scripts/load_data.py
uvicorn app.main:app --reload
```

La API queda disponible en `http://localhost:8000/docs`. Ejemplo:

```bash
curl -X POST http://localhost:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"¿Cuánto vendimos en España en marzo?"}'
```

## Datos y limpieza

`generate_data.py` crea 1.212 filas sintéticas deterministas: 1.200 pedidos base, 12 duplicados, fechas inválidas e importes vacíos. `load_data.py` convierte fechas e importes, normaliza texto, elimina duplicados y descarta filas irrecuperables. También conserva estadísticas de limpieza y escribe `data/orders_clean.csv`.

## SQL

Se crean dos vistas:

- `sales_by_month_country`: ventas y número de pedidos por mes y país.
- `top_customers`: los diez clientes con mayor gasto, excluyendo pedidos cancelados.

Elegí PostgreSQL porque es una base relacional habitual en backend, permite vistas SQL y representa mejor un entorno productivo. MongoDB no aporta ventaja aquí porque la interfaz solicitada y las vistas son SQL.

## Seguridad de la API

El LLM solo propone SQL. Antes de ejecutar, la API exige una única sentencia `SELECT`, rechaza palabras peligrosas, comentarios y múltiples sentencias, y limita las referencias a las dos vistas permitidas. La clave nunca se guarda en el repositorio: se lee de `OPENAI_API_KEY`.

## Tests

```bash
pytest -q
```

Los tests cubren la limpieza, la validación de SQL y el endpoint con el LLM simulado.

## Uso de IA

Usé IA como apoyo para proponer la estructura inicial, revisar casos de validación y sugerir tests. Acepté la generación del esqueleto y después corregí manualmente la limpieza, el control de tablas, los errores HTTP, la simulación del LLM y la documentación. La lógica de seguridad fue revisada explícitamente y no se confía en que el LLM genere consultas seguras por sí mismo.

## Qué haría con más tiempo

Añadiría migraciones, una tabla de errores de calidad, autenticación, límites de uso, logging estructurado, consultas parametrizadas para filtros y pruebas de integración en un entorno de staging.

