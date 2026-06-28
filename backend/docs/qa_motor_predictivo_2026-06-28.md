# QA motor predictivo Sof-IA BO - 2026-06-28

## Resultado ejecutivo

- El motor no debe prometer perfeccion ni 90% garantizado: el futbol tiene baja frecuencia de gol, lesiones, decisiones arbitrales, clima, penales y varianza competitiva.
- QA agregado: probabilidades suman 100, marcador coherente con resultado, scouting completo, calendario futuro completo, pesos del ensemble balanceados y avances de eliminacion directa validos.
- En modo demo se permite una probabilidad alta si el modelo la calcula, pero se bloquean textos de certeza absoluta y confianza alta sin validacion historica fuera de muestra.
- Para aspirar a precision industrial se requieren fuentes licenciadas y backtesting walk-forward, no scraping indiscriminado de internet.

## Auditoria de predicciones actuales

| Partido | Prediccion | Marcador | Probabilidad top | Confianza |
|---|---:|---:|---:|---|
| Sudáfrica vs Canadá | Canadá | 1-2 | 48.86% | media |
| Brasil vs Japón | Brasil | 2-0 | 77.82% | media |
| Alemania vs Paraguay | Alemania | 2-1 | 77.19% | media |
| Países Bajos vs Marruecos | Países Bajos | 1-0 | 64.56% | media |
| Costa de Marfil vs Noruega | Noruega | 1-2 | 62.72% | media |
| Francia vs Suecia | Francia | 2-0 | 80.75% | media |
| México vs Ecuador | Empate | 1-1 | 36.15% | baja |
| Inglaterra vs RD Congo | Inglaterra | 2-0 | 85.62% | media |
| Bélgica vs Senegal | Bélgica | 1-0 | 58.95% | media |
| Estados Unidos vs Bosnia y Herzegovina | Estados Unidos | 1-0 | 66.12% | media |
| España vs Austria | España | 2-1 | 76.19% | media |
| Portugal vs Croacia | Portugal | 1-0 | 68.69% | media |
| Suiza vs Argelia | Suiza | 1-0 | 57.63% | media |
| Australia vs Egipto | Empate | 1-1 | 38.22% | baja |
| Argentina vs Cabo Verde | Argentina | 3-0 | 92.48% | media |
| Colombia vs Ghana | Colombia | 2-0 | 79.15% | media |

## Gates QA implementados

- Ninguna prediccion demo puede declarar confianza alta ni certeza perfecta.
- Ninguna probabilidad top demo puede superar 95% en la suite QA.
- Todas las probabilidades deben sumar exactamente 100.00%.
- El marcador probable debe coincidir con ganador/empate.
- Todo partido futuro debe tener perfil de scouting para ambos equipos.
- En eliminacion directa, las probabilidades de avance deben sumar 100%.
- Los pesos del ensemble deben sumar 1.00.

## Fuentes de datos recomendadas para subir precision real

- Fixture oficial FIFA / cobertura fixture: calendario y sedes confirmadas.
- Opta / Stats Perform: eventos, xG, xA, alineaciones, datos historicos y datos de rendimiento.
- StatsBomb/Wyscout/Hudl: eventos, tracking, scouting y clips para validar estilos tacticos.
- Fuentes de lesiones y once probable: reportes oficiales de federaciones, conferencias y periodistas acreditados.
- Historico de partidos: ultimos 20-50 juegos por seleccion, fuerza del rival, sede, viajes, descanso y contexto competitivo.

## Camino tecnico hacia 90% metodologico

1. Ingesta diaria: fixtures, resultados, lesiones, suspensiones, titulares probables, clima, viajes y cuota de mercado como variable externa.
2. Feature store: xG/xGA, xThreat, PPDA, tiros, transiciones, pelota parada, arquero, edad/carga fisica, compatibilidad tactica y forma ajustada por rival.
3. Backtesting walk-forward: entrenar solo con datos anteriores al partido evaluado y medir accuracy, Brier score, log loss y calibration error.
4. Ensemble calibrado: Poisson bivariado, Elo dinamico, Bayes jerarquico, Markov de estados, Bellman para valor de partido, Monte Carlo y calibracion isotonic/Platt.
5. Monitoreo: si faltan titulares, lesiones o proveedor de xG, bajar confianza automaticamente.

## Referencias revisadas

- SBNation fixture ronda de 32: https://www.sbnation.com/soccer/1120771/world-cup-schedule-scores-round-32
- FIFA/World Cup schedule overview: https://en.wikipedia.org/wiki/2026_FIFA_World_Cup
- xG y calibracion probabilistica: https://en.wikipedia.org/wiki/Expected_goals
- Stats Perform/Opta como proveedor de datos deportivos: https://en.wikipedia.org/wiki/Stats_Perform
- Bayes-xG: https://arxiv.org/abs/2311.13707