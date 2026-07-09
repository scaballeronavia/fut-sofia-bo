from app.core.config import Settings
from app.data.demo_dataset import get_demo_match, get_demo_matches
from app.services.prediction_engine import simulate_prediction

TODAY_MATCH_ID = "today-mar-fra"
MODEL_VERSION = "demo-quarterfinal-calibrado-0.5.0"


def assert_score_matches_outcome(score: str, outcome: str):
    home_goals, away_goals = [int(value) for value in score.split("-")]
    if outcome == "home":
        assert home_goals > away_goals
    elif outcome == "away":
        assert away_goals > home_goals
    else:
        assert home_goals == away_goals


def test_probabilities_sum_to_100():
    match = get_demo_match(TODAY_MATCH_ID)
    assert match is not None
    result = simulate_prediction(match, Settings(default_simulations=5_000), seed=42, simulations=5_000)
    total = result.probabilities.home_win + result.probabilities.draw + result.probabilities.away_win
    assert round(total, 2) == 100.00


def test_prediction_is_reproducible_with_same_seed():
    match = get_demo_match(TODAY_MATCH_ID)
    assert match is not None
    settings = Settings(default_simulations=5_000)
    first = simulate_prediction(match, settings, seed=123, simulations=5_000)
    second = simulate_prediction(match, settings, seed=123, simulations=5_000)
    assert first.probabilities == second.probabilities
    assert first.most_likely_score == second.most_likely_score


def test_demo_mode_uses_user_facing_confidence_copy():
    match = get_demo_match(TODAY_MATCH_ID)
    assert match is not None
    result = simulate_prediction(match, Settings(default_simulations=5_000, demo_mode=True), seed=7, simulations=5_000)
    assert result.confidence in {"media", "baja"}
    assert "Modo demo" not in result.confidence_note
    assert "datos insuficientes" not in result.confidence_note.lower()


def test_most_likely_score_matches_primary_outcome():
    match = get_demo_match(TODAY_MATCH_ID)
    assert match is not None
    result = simulate_prediction(match, Settings(default_simulations=5_000), seed=42, simulations=5_000)
    assert_score_matches_outcome(result.most_likely_score, result.primary_outcome)


def test_all_quarterfinal_predictions_are_coherent():
    settings = Settings(default_simulations=3_000)
    for match in get_demo_matches():
        result = simulate_prediction(match, settings, seed=101, simulations=3_000)
        total = result.probabilities.home_win + result.probabilities.draw + result.probabilities.away_win
        assert round(total, 2) == 100.00
        assert_score_matches_outcome(result.most_likely_score, result.primary_outcome)


def test_prediction_exposes_professional_scouting_signals():
    match = get_demo_match(TODAY_MATCH_ID)
    assert match is not None
    result = simulate_prediction(match, Settings(default_simulations=3_000), seed=77, simulations=3_000)
    factor_names = {factor.name for factor in result.factors}
    component_names = {component.name for component in result.model_components}
    assert "Titulares disponibles" in factor_names
    assert "Goles esperados/xG" in factor_names
    assert "Estabilidad tactica" in factor_names
    assert "Scouting titulares/xG" in component_names


def test_summary_explains_advanced_methodology():
    match = get_demo_match(TODAY_MATCH_ID)
    assert match is not None
    result = simulate_prediction(match, Settings(default_simulations=3_000), seed=88, simulations=3_000)
    summary = result.executive_summary.lower()
    assert "titulares" in summary
    assert "markov" in summary
    assert "bellman" in summary
    assert "grafo de conocimiento" in summary
    assert "monte carlo" in summary


def test_model_version_is_quarterfinal_calibrated():
    match = get_demo_match(TODAY_MATCH_ID)
    assert match is not None
    result = simulate_prediction(match, Settings(), seed=42, simulations=3_000)
    assert result.model_version == MODEL_VERSION


def test_quarterfinal_fixture_is_loaded_from_today_onward():
    matches = get_demo_matches()
    assert len(matches) == 4
    assert matches[0].id == TODAY_MATCH_ID
    assert all(match.kickoff.date().isoformat() >= "2026-07-09" for match in matches)
    assert {match.id for match in matches} == {"today-mar-fra", "qf-esp-bel", "qf-nor-eng", "qf-arg-sui"}
    assert all("Cuartos" in match.phase for match in matches)


def test_every_quarterfinal_match_has_scouting_profile():
    from app.services.prediction_engine import SCOUTING_PROFILES

    for match in get_demo_matches():
        assert match.home_team.id in SCOUTING_PROFILES
        assert match.away_team.id in SCOUTING_PROFILES


def test_demo_quality_gate_blocks_fake_perfection_claims():
    settings = Settings(default_simulations=4_000, demo_mode=True)
    forbidden_copy = ("perfect", "seguro", "garant", "datos insuficientes", "modo demo")
    for match in get_demo_matches():
        result = simulate_prediction(match, settings, seed=20260709, simulations=4_000)
        top = max(result.probabilities.home_win, result.probabilities.draw, result.probabilities.away_win)
        assert 0 <= top <= 95
        assert result.confidence in {"media", "baja"}
        assert result.confidence != "alta"
        lowered = result.confidence_note.lower()
        assert all(word not in lowered for word in forbidden_copy)


def test_model_component_weights_are_balanced():
    match = get_demo_match(TODAY_MATCH_ID)
    assert match is not None
    result = simulate_prediction(match, Settings(default_simulations=3_000), seed=1234, simulations=3_000)
    assert round(sum(component.weight for component in result.model_components), 2) == 1.00
    assert all(component.status == "active" for component in result.model_components)


def test_knockout_advancement_probabilities_are_valid():
    settings = Settings(default_simulations=3_000)
    for match in get_demo_matches():
        result = simulate_prediction(match, settings, seed=909, simulations=3_000)
        assert result.qualification_probability_home is not None
        assert result.qualification_probability_away is not None
        assert 0 <= result.extra_time_probability <= 100
        assert 0 <= result.penalties_probability <= 100
        total_advancement = result.qualification_probability_home + result.qualification_probability_away
        assert abs(total_advancement - 100) <= 0.02


def test_morocco_france_prediction_respects_elimination_resistance():
    match = get_demo_match("today-mar-fra")
    assert match is not None
    result = simulate_prediction(match, Settings(default_simulations=8_000), seed=26062026, simulations=8_000)
    assert result.primary_outcome == "away"
    assert result.probabilities.away_win < 65
    assert result.qualification_probability_home is not None
    assert result.qualification_probability_home >= 30
    assert result.most_likely_score in {"0-1", "1-2", "1-1", "0-2"}


def test_norway_england_accounts_for_elite_finishing_threat():
    match = get_demo_match("qf-nor-eng")
    assert match is not None
    result = simulate_prediction(match, Settings(default_simulations=8_000), seed=26062026, simulations=8_000)
    assert result.primary_outcome == "away"
    assert result.probabilities.away_win < 60
    assert result.qualification_probability_home is not None
    assert result.qualification_probability_home >= 38
    assert_score_matches_outcome(result.most_likely_score, result.primary_outcome)


def test_switzerland_keeps_argentina_forecast_from_fake_certainty():
    match = get_demo_match("qf-arg-sui")
    assert match is not None
    result = simulate_prediction(match, Settings(default_simulations=8_000), seed=26062026, simulations=8_000)
    assert result.primary_outcome == "home"
    assert result.probabilities.home_win < 88
    assert result.qualification_probability_away is not None
    assert result.qualification_probability_away >= 15
    assert_score_matches_outcome(result.most_likely_score, result.primary_outcome)
