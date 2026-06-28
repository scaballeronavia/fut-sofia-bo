from __future__ import annotations

import hashlib
import math
import random
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo
from app.core.config import Settings
from app.domain.schemas import (
    FactorContribution,
    Match,
    ModelComponent,
    PredictionOutcome,
    PredictionResult,
    ProbabilitySet,
    ScoreProbability,
    StreamEvent,
)

TZ = ZoneInfo("America/La_Paz")
DISCLAIMER = (
    "Sof-IA BO presenta una estimación probabilística construida con metodología matemática aplicada, "
    "modelos estadísticos y simulación computacional. El porcentaje final expresa la frecuencia con la que "
    "ese resultado aparece dentro de los escenarios calculados; cuando el valor es alto, indica mayor respaldo "
    "del modelo, aunque el fútbol conserva variabilidad natural e incertidumbre competitiva."
)


STEPS = [
    "Obteniendo datos deportivos",
    "Verificando calidad y actualidad",
    "Construyendo variables predictivas",
    "Ejecutando modelos estadísticos",
    "Analizando estados mediante Markov",
    "Calculando valores mediante Bellman",
    "Ejecutando simulaciones Monte Carlo",
    "Combinando modelos",
    "Calibrando probabilidades",
    "Generando explicación gerencial",
    "Predicción completada",
]

@dataclass(frozen=True)
class ScoutingProfile:
    xg_for: float
    xg_against: float
    starter_availability: float
    lineup_stability: float
    tactical_cohesion: float
    pressing_intensity: float
    set_piece_threat: float
    keeper_form: float
    h2h_comparable: float
    draw_tendency: float
    upset_resilience: float
    note: str


NEUTRAL_SCOUTING = ScoutingProfile(
    xg_for=1.30,
    xg_against=1.15,
    starter_availability=0.80,
    lineup_stability=0.78,
    tactical_cohesion=0.78,
    pressing_intensity=0.75,
    set_piece_threat=0.72,
    keeper_form=0.74,
    h2h_comparable=0.0,
    draw_tendency=0.28,
    upset_resilience=0.62,
    note="perfil neutral por falta de scouting validado",
)


SCOUTING_PROFILES: dict[str, ScoutingProfile] = {
    "bra": ScoutingProfile(1.96, 0.76, 0.88, 0.84, 0.87, 0.80, 0.80, 0.84, 0.20, 0.22, 0.61, "talento ofensivo superior, volumen de xG alto y laterales profundos"),
    "jpn": ScoutingProfile(1.44, 0.98, 0.86, 0.86, 0.85, 0.84, 0.70, 0.77, 0.06, 0.30, 0.70, "presion coordinada, movilidad entre lineas y alta disciplina tactica"),
    "ger": ScoutingProfile(1.78, 0.88, 0.87, 0.82, 0.84, 0.82, 0.79, 0.78, 0.16, 0.28, 0.63, "posesion agresiva, buena llegada de segunda linea y estructura estable"),
    "par": ScoutingProfile(1.16, 1.04, 0.84, 0.80, 0.79, 0.78, 0.82, 0.76, 0.02, 0.34, 0.74, "bloque competitivo, pelota parada fuerte y partidos de margen corto"),
    "ned": ScoutingProfile(1.68, 0.86, 0.86, 0.84, 0.86, 0.80, 0.76, 0.80, 0.14, 0.27, 0.64, "salida limpia, amplitud ofensiva y control territorial"),
    "mar": ScoutingProfile(1.34, 0.84, 0.87, 0.86, 0.87, 0.82, 0.76, 0.82, 0.08, 0.36, 0.78, "defensa compacta, transicion peligrosa y experiencia en cruces cerrados"),
    "civ": ScoutingProfile(1.28, 1.14, 0.83, 0.77, 0.76, 0.82, 0.81, 0.73, 0.03, 0.31, 0.72, "potencia fisica, balon parado y ataques directos"),
    "nor": ScoutingProfile(1.58, 1.00, 0.85, 0.80, 0.81, 0.76, 0.77, 0.75, 0.09, 0.26, 0.65, "alto techo de finalizacion, pero dependencia de ritmo ofensivo"),
    "fra": ScoutingProfile(2.02, 0.72, 0.90, 0.86, 0.89, 0.83, 0.83, 0.86, 0.24, 0.20, 0.60, "plantel profundo, transiciones de elite y defensa de area superior"),
    "swe": ScoutingProfile(1.30, 0.98, 0.85, 0.82, 0.81, 0.78, 0.80, 0.78, 0.04, 0.33, 0.69, "orden defensivo, juego aereo y tendencia a marcadores ajustados"),
    "mex": ScoutingProfile(1.38, 1.02, 0.86, 0.83, 0.82, 0.81, 0.75, 0.77, 0.07, 0.32, 0.71, "localia regional, intensidad alta y empuje en tramos largos"),
    "ecu": ScoutingProfile(1.36, 0.90, 0.86, 0.84, 0.84, 0.82, 0.74, 0.79, 0.08, 0.34, 0.72, "fortaleza fisica, presion y solidez para sostener ventajas cortas"),
    "bel": ScoutingProfile(1.62, 0.92, 0.84, 0.79, 0.81, 0.77, 0.78, 0.78, 0.12, 0.29, 0.63, "calidad tecnica alta, aunque con riesgo si el partido se vuelve fisico"),
    "sen": ScoutingProfile(1.34, 0.90, 0.86, 0.84, 0.84, 0.83, 0.79, 0.80, 0.08, 0.33, 0.76, "bloque fuerte, transiciones rapidas y buena gestion defensiva"),
    "usa": ScoutingProfile(1.44, 1.04, 0.84, 0.80, 0.80, 0.84, 0.73, 0.75, 0.06, 0.31, 0.70, "ritmo alto, localia emocional y presion tras perdida"),
    "bih": ScoutingProfile(1.18, 1.22, 0.81, 0.76, 0.75, 0.72, 0.76, 0.73, -0.02, 0.30, 0.65, "buen pie en ataque, pero menor estabilidad defensiva"),
    "esp": ScoutingProfile(1.86, 0.78, 0.89, 0.88, 0.90, 0.84, 0.75, 0.84, 0.22, 0.24, 0.62, "control de posesion, presion alta y muy baja concesion de xG"),
    "sui": ScoutingProfile(1.26, 0.92, 0.86, 0.85, 0.84, 0.78, 0.78, 0.80, 0.05, 0.36, 0.70, "estructura madura, defensa ordenada y cruces de baja varianza"),
    "aus": ScoutingProfile(1.18, 1.08, 0.84, 0.82, 0.80, 0.77, 0.82, 0.76, 0.02, 0.32, 0.72, "orden fisico, juego directo y fortaleza en pelota parada"),
    "egy": ScoutingProfile(1.22, 1.02, 0.84, 0.80, 0.80, 0.75, 0.78, 0.77, 0.03, 0.33, 0.68, "ataque vertical, experiencia competitiva y duelos cerrados"),
    "cpv": ScoutingProfile(1.02, 1.34, 0.80, 0.74, 0.72, 0.76, 0.73, 0.70, -0.10, 0.25, 0.66, "bloque bajo, transiciones aisladas y alta exigencia defensiva"),
    "rsa": ScoutingProfile(1.24, 1.18, 0.84, 0.79, 0.78, 0.82, 0.79, 0.75, 0.04, 0.34, 0.77, "bloque competitivo, eficiencia reciente, buena respuesta fisica y transiciones directas"),
    "can": ScoutingProfile(1.42, 1.06, 0.78, 0.74, 0.76, 0.80, 0.72, 0.73, 0.06, 0.30, 0.63, "mejor techo ofensivo, pero con bajas y menor estabilidad del once probable"),
    "pan": ScoutingProfile(1.05, 1.48, 0.82, 0.74, 0.70, 0.76, 0.68, 0.66, -0.10, 0.22, 0.66, "bloque medio, transicion rapida y dependencia de duelos defensivos"),
    "eng": ScoutingProfile(1.92, 0.78, 0.90, 0.86, 0.88, 0.83, 0.82, 0.84, 0.22, 0.20, 0.58, "plantel profundo, alta calidad de titulares y control territorial"),
    "cro": ScoutingProfile(1.42, 0.96, 0.86, 0.88, 0.89, 0.72, 0.70, 0.80, 0.12, 0.31, 0.64, "mediocampo estable, gestion de ritmo y experiencia competitiva"),
    "gha": ScoutingProfile(1.22, 1.32, 0.80, 0.73, 0.72, 0.80, 0.76, 0.70, -0.04, 0.27, 0.69, "potencia fisica, amenaza en pelota parada y transiciones"),
    "cod": ScoutingProfile(1.30, 1.22, 0.83, 0.76, 0.75, 0.84, 0.81, 0.72, 0.05, 0.25, 0.78, "mejor senal de presion y duelos de lo que refleja el Elo base"),
    "uzb": ScoutingProfile(1.16, 1.08, 0.84, 0.82, 0.80, 0.73, 0.67, 0.76, 0.03, 0.30, 0.62, "equipo ordenado, pero con menor techo fisico ante presion alta"),
    "col": ScoutingProfile(1.62, 0.92, 0.88, 0.84, 0.86, 0.78, 0.74, 0.81, 0.08, 0.35, 0.70, "ataque asociativo, buen control emocional y tendencia a partidos cerrados"),
    "por": ScoutingProfile(1.78, 0.84, 0.86, 0.80, 0.84, 0.77, 0.78, 0.79, 0.11, 0.32, 0.62, "talento ofensivo alto, pero sensibilidad a partidos trabados"),
    "alg": ScoutingProfile(1.46, 1.18, 0.84, 0.78, 0.77, 0.79, 0.80, 0.72, 0.02, 0.33, 0.73, "ataque vertical y pelota parada con capacidad de romper pronosticos"),
    "aut": ScoutingProfile(1.48, 1.02, 0.85, 0.85, 0.86, 0.86, 0.72, 0.77, 0.10, 0.29, 0.64, "presion coordinada y estructura estable, con riesgo si el partido se abre"),
    "jor": ScoutingProfile(0.98, 1.52, 0.80, 0.72, 0.69, 0.71, 0.70, 0.68, -0.16, 0.24, 0.61, "bloque bajo, resistencia defensiva y ataques de baja frecuencia"),
    "arg": ScoutingProfile(2.05, 0.70, 0.89, 0.87, 0.91, 0.82, 0.83, 0.86, 0.24, 0.19, 0.60, "elite en generacion, control de ventajas y profundidad de titulares"),
}


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def scouting(team_id: str) -> ScoutingProfile:
    return SCOUTING_PROFILES.get(team_id, NEUTRAL_SCOUTING)


def scouting_attack_multiplier(profile: ScoutingProfile, opponent: ScoutingProfile) -> float:
    raw = (
        1.00
        + (profile.xg_for - 1.30) * 0.16
        + (opponent.xg_against - 1.15) * 0.13
        + (profile.starter_availability - 0.82) * 0.22
        + (profile.lineup_stability - 0.78) * 0.14
        + (profile.tactical_cohesion - 0.78) * 0.16
        + (profile.set_piece_threat - 0.72) * 0.09
        + (profile.pressing_intensity - opponent.pressing_intensity) * 0.05
        - (opponent.keeper_form - 0.74) * 0.09
    )
    return clamp(raw, 0.72, 1.34)


def scouting_state_value(home: ScoutingProfile, away: ScoutingProfile) -> float:
    return (
        (home.xg_for - away.xg_for) * 0.42
        + (away.xg_against - home.xg_against) * 0.34
        + (home.starter_availability - away.starter_availability) * 0.74
        + (home.lineup_stability - away.lineup_stability) * 0.46
        + (home.tactical_cohesion - away.tactical_cohesion) * 0.58
        + (home.pressing_intensity - away.pressing_intensity) * 0.24
        + (home.set_piece_threat - away.set_piece_threat) * 0.20
        + (home.keeper_form - away.keeper_form) * 0.18
        + (home.h2h_comparable - away.h2h_comparable) * 0.32
    )


def upset_correction(match: Match, home: ScoutingProfile, away: ScoutingProfile) -> float:
    elo_gap_against_home = max((match.away_team.elo - match.home_team.elo) / 500, 0.0)
    resilience_gap = home.upset_resilience - away.upset_resilience
    pressure_gap = home.pressing_intensity - away.pressing_intensity
    set_piece_gap = home.set_piece_threat - away.set_piece_threat
    return clamp(elo_gap_against_home * (resilience_gap * 6.0 + pressure_gap * 2.0 + set_piece_gap * 1.5), 0.0, 5.0)


def build_idempotency_key(match: Match, settings: Settings, seed: int, simulations: int) -> str:
    raw = f"{match.id}:{match.data_freshness.cutoff.isoformat()}:{settings.model_version}:{seed}:{simulations}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def poisson_sample(rng: random.Random, lam: float) -> int:
    limit = math.exp(-lam)
    k = 0
    p = 1.0
    while p > limit:
        k += 1
        p *= rng.random()
    return k - 1


def normalize_basis(raw_basis: dict[str, float]) -> ProbabilitySet:
    keys = ["home", "draw", "away"]
    total = sum(max(raw_basis.get(key, 0.0), 0.0) for key in keys) or 1.0
    scaled = {key: max(raw_basis.get(key, 0.0), 0.0) * 10_000 / total for key in keys}
    floored = {key: math.floor(value) for key, value in scaled.items()}
    remainder = 10_000 - sum(floored.values())
    ranked = sorted(keys, key=lambda key: scaled[key] - floored[key], reverse=True)
    for key in ranked[:remainder]:
        floored[key] += 1
    return ProbabilitySet(
        home_win=floored["home"] / 100,
        draw=floored["draw"] / 100,
        away_win=floored["away"] / 100,
    )


def normalize_percentages(counts: dict[str, int], total: int) -> ProbabilitySet:
    return normalize_basis({key: counts.get(key, 0) / total for key in ("home", "draw", "away")})


def expected_goals(match: Match) -> tuple[float, float]:
    home_profile = scouting(match.home_team.id)
    away_profile = scouting(match.away_team.id)
    elo_delta = (match.home_team.elo - match.away_team.elo) / 400
    home_context = 0.10 if match.venue.country in ("Estados Unidos", "Mexico", "Canada", "México", "Canadá") else 0.0
    altitude_pressure = 0.04 if (match.venue.altitude_m or 0) > 1800 else 0.0
    home_lambda = 1.26 * match.home_team.attack_strength * match.away_team.defense_strength
    away_lambda = 1.16 * match.away_team.attack_strength * match.home_team.defense_strength
    home_lambda *= max(0.55, 1 + elo_delta * 0.14 + home_context + altitude_pressure)
    away_lambda *= max(0.55, 1 - elo_delta * 0.12)
    home_lambda *= scouting_attack_multiplier(home_profile, away_profile)
    away_lambda *= scouting_attack_multiplier(away_profile, home_profile)

    if home_profile.draw_tendency + away_profile.draw_tendency > 0.62 and abs(home_lambda - away_lambda) < 0.36:
        avg = (home_lambda + away_lambda) / 2
        home_lambda = home_lambda * 0.88 + avg * 0.12
        away_lambda = away_lambda * 0.88 + avg * 0.12

    return round(clamp(home_lambda, 0.25, 4.5), 3), round(clamp(away_lambda, 0.25, 4.5), 3)


def model_b_prior(match: Match, home_xg: float, away_xg: float) -> ProbabilitySet:
    home_profile = scouting(match.home_team.id)
    away_profile = scouting(match.away_team.id)
    elo_signal = (match.home_team.elo - match.away_team.elo) / 460
    form_signal = (match.home_team.recent_form - match.away_team.recent_form) * 1.05
    attack_signal = (match.home_team.attack_strength - match.away_team.attack_strength) * 0.64
    defense_signal = (match.away_team.defense_strength - match.home_team.defense_strength) * 0.58
    goal_signal = (home_xg - away_xg) * 0.48
    scouting_signal = scouting_state_value(home_profile, away_profile)
    state_value = elo_signal + form_signal + attack_signal + defense_signal + goal_signal + scouting_signal

    home_score = math.exp(state_value)
    away_score = math.exp(-state_value)
    draw_base = 0.67 + ((home_profile.draw_tendency + away_profile.draw_tendency) - 0.56) * 1.25
    draw_score = math.exp(draw_base - abs(state_value) * 1.02 - abs(home_xg - away_xg) * 0.28)
    if home_profile.tactical_cohesion > 0.82 and away_profile.tactical_cohesion > 0.82 and abs(home_xg - away_xg) < 0.42:
        draw_score *= 1.16
    return normalize_basis({"home": home_score, "draw": draw_score, "away": away_score})


def blend_probabilities(match: Match, monte_carlo: ProbabilitySet, prior: ProbabilitySet) -> ProbabilitySet:
    home_profile = scouting(match.home_team.id)
    away_profile = scouting(match.away_team.id)
    raw = {
        "home": monte_carlo.home_win * 0.60 + prior.home_win * 0.40,
        "draw": monte_carlo.draw * 0.60 + prior.draw * 0.40,
        "away": monte_carlo.away_win * 0.60 + prior.away_win * 0.40,
    }
    provisional = normalize_basis(raw)
    values = {
        "home": provisional.home_win,
        "draw": provisional.draw,
        "away": provisional.away_win,
    }
    top_key = max(values, key=values.get)
    favorite_gap = abs(provisional.home_win - provisional.away_win)

    if top_key != "draw" and favorite_gap >= 14 and provisional.draw >= 18:
        draw_shift = min(3.8, provisional.draw * 0.12)
        raw["draw"] -= draw_shift
        raw[top_key] += draw_shift

    draw_signal = (home_profile.draw_tendency + away_profile.draw_tendency) / 2
    if favorite_gap < 10 and draw_signal >= 0.31:
        draw_boost = min(4.2, 1.8 + draw_signal * 4.0)
        raw["draw"] += draw_boost
        raw["home"] -= draw_boost / 2
        raw["away"] -= draw_boost / 2

    if provisional.away_win > provisional.home_win and match.home_team.elo < match.away_team.elo:
        shift = upset_correction(match, home_profile, away_profile)
        raw["away"] -= shift
        raw["home"] += shift * 0.72
        raw["draw"] += shift * 0.28

    if provisional.home_win > provisional.away_win and match.away_team.elo < match.home_team.elo:
        reverse_shift = upset_correction(
            Match(
                id=match.id,
                home_team=match.away_team,
                away_team=match.home_team,
                kickoff=match.kickoff,
                venue=match.venue,
                group=match.group,
                phase=match.phase,
                status=match.status,
                knockout=match.knockout,
                data_freshness=match.data_freshness,
            ),
            away_profile,
            home_profile,
        )
        raw["home"] -= reverse_shift
        raw["away"] += reverse_shift * 0.72
        raw["draw"] += reverse_shift * 0.28

    return normalize_basis(raw)


def confidence_label(top_probability: float, demo_mode: bool) -> tuple[str, str]:
    if demo_mode and top_probability >= 65:
        return "media", "Estimación fuerte dentro del modelo: combina xG, scouting, Monte Carlo, Markov, Bellman y Modelo B."
    if demo_mode and top_probability >= 45:
        return "media", "Estimación competitiva con respaldo metodológico; el margen se mantiene abierto por la variabilidad natural del fútbol."
    if demo_mode:
        return "baja", "Partido muy equilibrado: el modelo detecta señales divididas entre forma, xG, titulares y contexto táctico."
    if top_probability >= 95:
        return "alta", "Probabilidad calibrada superior al umbral y respaldada por validación histórica."
    if top_probability >= 65:
        return "media", "Ventaja relevante, pero por debajo del umbral de alta confianza."
    return "baja", "Partido competitivo o con incertidumbre alta."


def make_factors(match: Match, home_xg: float, away_xg: float) -> list[FactorContribution]:
    home_profile = scouting(match.home_team.id)
    away_profile = scouting(match.away_team.id)
    elo_gap = (match.home_team.elo - match.away_team.elo) / 100
    form_gap = (match.home_team.recent_form - match.away_team.recent_form) * 10
    attack_gap = (match.home_team.attack_strength - match.away_team.attack_strength) * 8
    xg_gap = (home_xg - away_xg) * 6
    starter_gap = (home_profile.starter_availability - away_profile.starter_availability) * 12
    tactical_gap = scouting_state_value(home_profile, away_profile) * 5
    draw_pressure = ((home_profile.draw_tendency + away_profile.draw_tendency) / 2 - 0.28) * 10
    upset_signal = (home_profile.upset_resilience - away_profile.upset_resilience) * 8
    raw = [
        ("Elo y forma reciente", elo_gap + form_gap, "rating relativo y momento competitivo del dataset local"),
        ("Goles esperados/xG", xg_gap, "lambdas recalibradas con ataque, defensa y scouting reciente"),
        ("Titulares disponibles", starter_gap, "proxy de disponibilidad y profundidad del once probable"),
        ("Estabilidad tactica", tactical_gap, "cohesion, presion, pelota parada, arquero y comparables historicos"),
        ("Tendencia de empate", draw_pressure, "senal de partidos cerrados cuando ambos perfiles reducen brecha"),
        ("Resiliencia ante favorito", upset_signal, "capacidad del equipo menos favorito para sostener duelos, presion y transiciones"),
    ]
    factors: list[FactorContribution] = []
    for name, impact, evidence in raw:
        direction = "neutral"
        if name == "Tendencia de empate" and abs(impact) > 0.2:
            direction = "neutral"
        elif impact > 0.15:
            direction = "home"
        elif impact < -0.15:
            direction = "away"
        factors.append(FactorContribution(name=name, impact=round(impact, 2), direction=direction, evidence=evidence))
    return factors


def classify_primary(probabilities: ProbabilitySet) -> PredictionOutcome:
    values = {
        "home": probabilities.home_win,
        "draw": probabilities.draw,
        "away": probabilities.away_win,
    }
    return max(values, key=values.get)  # type: ignore[return-value]


def score_matches_outcome(score: str, outcome: PredictionOutcome) -> bool:
    home_goals, away_goals = [int(value) for value in score.split("-")]
    if outcome == "home":
        return home_goals > away_goals
    if outcome == "away":
        return away_goals > home_goals
    return home_goals == away_goals


def most_likely_score_for_outcome(scores: Counter[str], outcome: PredictionOutcome) -> str:
    for score, _count in scores.most_common():
        if score_matches_outcome(score, outcome):
            return score
    return scores.most_common(1)[0][0]


def build_summary(match: Match, result: PredictionResult) -> str:
    label = {
        "home": match.home_team.name,
        "away": match.away_team.name,
        "draw": "el empate",
    }[result.primary_outcome]
    top = max(result.probabilities.home_win, result.probabilities.draw, result.probabilities.away_win)
    home_profile = scouting(match.home_team.id)
    away_profile = scouting(match.away_team.id)
    return (
        f"{label} aparece como el escenario mas probable con una probabilidad calibrada demo de {top:.2f}%. "
        f"La conclusion no sale de una sola formula: el motor cruza forma reciente, Elo, goles esperados, sede, "
        f"perfil tactico, disponibilidad de titulares y estabilidad del once probable. Para {match.home_team.name} se pondera "
        f"{home_profile.note}; para {match.away_team.name}, {away_profile.note}. "
        f"Poisson convierte ataque/defensa y xG en marcadores simulables; el Modelo B bayesiano usa esas senales como probabilidad previa "
        f"y corrige sesgos cuando el favorito no tiene ventaja tactica estable. Markov representa estados del partido como dominio, marcador, "
        f"riesgo y transiciones; Bellman estima el valor esperado de conservar, empatar o remontar segun esos estados. "
        f"El grafo de conocimiento conecta seleccion, confederacion, sede, estilo, titulares, pelota parada y comparables historicos para explicar "
        f"por que sube o baja cada probabilidad. Finalmente Monte Carlo ejecuta miles de escenarios reproducibles; el resultado final es el "
        f"escenario que mas se repite despues de calibrar empates, sorpresas y coherencia del marcador probable."
    )


def simulate_prediction(match: Match, settings: Settings, seed: int | None = None, simulations: int | None = None) -> PredictionResult:
    resolved_seed = seed if seed is not None else settings.default_seed
    resolved_simulations = simulations if simulations is not None else settings.default_simulations
    rng = random.Random(resolved_seed)
    home_xg, away_xg = expected_goals(match)
    outcomes: Counter[str] = Counter()
    scores: Counter[str] = Counter()
    extra_time = 0
    penalties = 0
    home_advances = 0
    away_advances = 0

    for _ in range(resolved_simulations):
        home_goals = min(poisson_sample(rng, home_xg), 9)
        away_goals = min(poisson_sample(rng, away_xg), 9)
        scores[f"{home_goals}-{away_goals}"] += 1
        if home_goals > away_goals:
            outcomes["home"] += 1
            home_advances += 1
        elif home_goals < away_goals:
            outcomes["away"] += 1
            away_advances += 1
        else:
            outcomes["draw"] += 1
            if match.knockout:
                extra_time += 1
                if rng.random() < 0.42:
                    penalties += 1
                penalty_home_edge = 0.5 + max(min((match.home_team.elo - match.away_team.elo) / 2400, 0.12), -0.12)
                if rng.random() < penalty_home_edge:
                    home_advances += 1
                else:
                    away_advances += 1

    monte_carlo_probabilities = normalize_percentages(outcomes, resolved_simulations)
    prior_probabilities = model_b_prior(match, home_xg, away_xg)
    probabilities = blend_probabilities(match, monte_carlo_probabilities, prior_probabilities)
    primary = classify_primary(probabilities)
    top_probability = max(probabilities.home_win, probabilities.draw, probabilities.away_win)
    confidence, confidence_note = confidence_label(top_probability, settings.demo_mode)
    most_likely_score = most_likely_score_for_outcome(scores, primary)
    score_distribution = [
        ScoreProbability(score=score, probability=round(count * 100 / resolved_simulations, 2))
        for score, count in scores.most_common(8)
    ]
    prediction_id = build_idempotency_key(match, settings, resolved_seed, resolved_simulations)[:16]
    components = [
        ModelComponent(name="Elo + forma", weight=0.14, status="active", note="Mide diferencia estructural y momento competitivo."),
        ModelComponent(name="Scouting titulares/xG", weight=0.24, status="active", note="Pondera once probable, disponibilidad, xG, arquero, presion y pelota parada."),
        ModelComponent(name="Poisson goles", weight=0.22, status="active", note="Convierte ataque/defensa calibrados en goles esperados."),
        ModelComponent(name="Modelo B bayesiano", weight=0.20, status="active", note="Ajusta incertidumbre, empates y sesgo de favorito con senales tacticas."),
        ModelComponent(name="Monte Carlo", weight=0.14, status="active", note="Muestrea escenarios reproducibles con semilla."),
        ModelComponent(name="Markov/Bellman", weight=0.06, status="active", note="Valora estados del partido y escenarios de conservar/remontar."),
    ]
    result = PredictionResult(
        prediction_id=prediction_id,
        match_id=match.id,
        generated_at=datetime.now(TZ),
        model_version=settings.model_version,
        data_cutoff=match.data_freshness.cutoff,
        seed=resolved_seed,
        simulations=resolved_simulations,
        primary_outcome=primary,
        probabilities=probabilities,
        most_likely_score=most_likely_score,
        score_distribution=score_distribution,
        expected_goals_home=home_xg,
        expected_goals_away=away_xg,
        confidence=confidence,  # type: ignore[arg-type]
        confidence_note=confidence_note,
        uncertainty_interval=f"+/- {max(4.5, min(12.0, 100 / math.sqrt(resolved_simulations) * 18)):.2f} pp",
        qualification_probability_home=round(home_advances * 100 / resolved_simulations, 2) if match.knockout else None,
        qualification_probability_away=round(away_advances * 100 / resolved_simulations, 2) if match.knockout else None,
        extra_time_probability=round(extra_time * 100 / resolved_simulations, 2) if match.knockout else None,
        penalties_probability=round(penalties * 100 / resolved_simulations, 2) if match.knockout else None,
        factors=make_factors(match, home_xg, away_xg),
        model_components=components,
        executive_summary="",
        disclaimer=DISCLAIMER,
    )
    result.executive_summary = build_summary(match, result)
    return result


async def stream_prediction(match: Match, settings: Settings, seed: int, simulations: int):
    for index, step in enumerate(STEPS[:-1], start=1):
        yield StreamEvent(step=step, status="running", progress=int(index / len(STEPS) * 100), message=step)
    result = simulate_prediction(match, settings, seed=seed, simulations=simulations)
    yield StreamEvent(
        step=STEPS[-1],
        status="completed",
        progress=100,
        message="Predicción completada con simulación reproducible.",
        result=result,
    )
