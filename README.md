# bolivIA 5.0

Aplicación web deportiva para explorar una arquitectura predictiva del Mundial 2026 con frontend React, backend FastAPI, simulación Monte Carlo reproducible y modo demostración explícito.

El repositorio arranca en modo demo porque no hay credenciales ni licencias externas configuradas. Los datos incluidos son locales y no se presentan como información oficial ni actual.

## Arquitectura implementada

- `frontend`: React + TypeScript + Vite, UI responsive con identidad corporativa planetaria, filtros, tarjetas de partidos, progreso SSE y resultados.
- `backend`: FastAPI + Pydantic, endpoints REST, Server-Sent Events, motor predictivo demo, contratos de dominio y modelos SQLAlchemy iniciales.
- `postgres`: servicio preparado para persistencia relacional.
- `redis`: servicio preparado para cache, rate limiting y trabajos async.
- `docker-compose.yml`: levanta frontend, backend, PostgreSQL y Redis.

## Comandos

```bash
cp .env.example .env
docker compose up --build
```

Frontend: http://localhost:5173
Backend: http://localhost:8000
OpenAPI: http://localhost:8000/docs

Pruebas backend:

```bash
cd backend
python -m pip install -r requirements.txt
pytest
```

Build frontend:

```bash
cd frontend
npm install
npm run build
```

## Endpoints principales

- `GET /api/v1/matches`
- `GET /api/v1/matches/{match_id}`
- `POST /api/v1/matches/{match_id}/predictions`
- `GET /api/v1/predictions/{prediction_id}`
- `GET /api/v1/predictions/{prediction_id}/stream`
- `GET /api/v1/predictions/{prediction_id}/explanation`
- `GET /api/v1/models`
- `GET /api/v1/models/metrics`
- `GET /api/v1/data-sources/status`
- `GET /api/v1/system/health`

## Motor predictivo MVP

El motor actual combina:

- señal Elo demo para fuerza relativa;
- modelo Poisson para goles esperados;
- simulación Monte Carlo reproducible con semilla;
- ajuste conservador de confianza;
- módulo Markov/Bellman marcado como conceptual hasta contar con eventos históricos reales.

Procedimiento del ensemble demo:

1. Calcula goles esperados desde ataque, defensa, Elo y contexto de sede.
2. Ejecuta 50.000 simulaciones por defecto.
3. Agrega victorias, empates, derrotas y marcadores.
4. Normaliza probabilidades para sumar exactamente 100.00%.
5. En eliminatorias separa resultado en 90 minutos y probabilidad de avanzar.
6. Declara `datos_insuficientes` en modo demo, aunque un favorito tenga ventaja amplia.

## Fuentes de datos

- `DemoDataProvider`: activo, local, visible como demostración.
- `OfficialTournamentProvider`: interfaz pendiente de credenciales/licencia.
- `RankingProvider`: interfaz pendiente de proveedor externo.

No hay claves API ni secretos en el repositorio.

## Métricas

El endpoint de métricas existe, pero devuelve `not_available_demo_mode`. No se reportan Accuracy, Brier Score, Log Loss ni ECE como reales hasta cargar datos históricos, snapshots temporales y backtesting walk-forward.

## Limitaciones conocidas

- La persistencia de predicciones está en memoria en el MVP.
- Celery/RQ, Alembic y autenticación administrativa están planificados, no integrados.
- Markov y Bellman están representados como componente conceptual con peso bajo; requieren eventos históricos para estimar transiciones.
- No se ejecutó calibración real fuera de muestra porque no hay dataset histórico licenciado.
- Las banderas se renderizan como emoji del sistema para evitar assets no licenciados.

## Criterio científico

El sistema no fabrica precisión del 95%, no usa datos posteriores al partido y no presenta mocks como datos reales. En modo demo toda predicción se muestra como demostración con incertidumbre y aviso de responsabilidad.
