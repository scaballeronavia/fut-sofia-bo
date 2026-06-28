# Arquitectura

## Capas

- Bronze: respuestas originales de proveedores, fecha de extracción, hash e identificador de fuente.
- Silver: equipos, jugadores y fechas normalizadas con conflictos registrados.
- Gold: features temporales listas para entrenamiento, simulación y auditoría.

## Separación de responsabilidades

- `app/data`: adaptadores y datasets.
- `app/domain`: contratos Pydantic usados por API y motor.
- `app/services`: lógica predictiva, streaming y store temporal.
- `app/db`: mapa inicial de entidades relacionales.
- `app/api`: rutas HTTP y SSE.

## Flujo predictivo

1. Ingesta de datos.
2. Validación de calidad y actualidad.
3. Construcción de variables.
4. Modelos base.
5. Simulación Monte Carlo.
6. Ensemble.
7. Calibración.
8. Explicabilidad.
9. Resultado gerencial.

El MVP implementa el flujo de punta a punta con datos demo. La transición a producción requiere proveedores externos, snapshots históricos y jobs asincrónicos persistentes.
