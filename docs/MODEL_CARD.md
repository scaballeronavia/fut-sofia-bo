# Model Card - demo-ensemble-calibrado-0.2.0

## Uso previsto

Validar la arquitectura técnica de bolivIA 5.0 y demostrar el flujo completo de predicción probabilística.

## No uso previsto

- No debe usarse para apuestas.
- No debe interpretarse como predicción oficial.
- No debe presentarse como modelo calibrado de producción.

## Entradas

- Elo demo.
- Fortaleza ofensiva demo.
- Fortaleza defensiva demo.
- Forma reciente demo.
- Contexto básico de sede.

## Salidas

- Probabilidad de victoria local.
- Probabilidad de empate.
- Probabilidad de victoria visitante.
- Marcador más probable.
- Goles esperados.
- Intervalo de incertidumbre.
- Factores explicativos derivados de las variables usadas.

## Calibración

No disponible en modo demo. El sistema se abstiene de declarar alta confianza y etiqueta los resultados como `datos_insuficientes`.

## Riesgos

- Dataset pequeño y sintético.
- Sin lesiones, alineaciones reales ni xG histórico.
- Sin validación temporal.
- Sin medición de drift.
