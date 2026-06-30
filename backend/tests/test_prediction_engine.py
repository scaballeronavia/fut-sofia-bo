from app.core.config import Settings
from app.data.demo_dataset import get_demo_match, get_demo_matches
from app.services.prediction_engine import simulate_prediction


def test_probabilities_sum_to_100():
    match = get_demo_match("today-rsa-can")
    assert match is not None
    result = simulate_prediction(match, Settings(default_simulations=5_000), seed=42, simulations=5_000)
    total = result.probabilities.home_win + result.probabilities.draw + result.probabilities.away_win
    assert round(total, 2) == 100.00


def test_prediction_is_reproducible_with_same_seed():
    match = get_demo_match("today-rsa-can")
    assert match is not None
    settings = Settings(default_simulations=5_000)
    first = simulate_prediction(match, settings, seed=123, simulations=5_000)
    second = simulate_prediction(match, settings, seed=123, simulations=5_000)
    assert first.probabilities == second.probabilities
    assert first.most_likely_score == second.most_likely_score


def test_demo_mode_uses_user_facing_confidence_copy():
    match = get_demo_match("today-rsa-can")
    assert match is not None
    result = simulate_prediction(match, Settings(default_simulations=5_000, demo_mode=True), seed=7, simulations=5_000)
    assert result.confidence in {"media", "baja"}
    assert "Modo demo" not in result.confidence_note
    assert "datos insuficientes" not in result.confidence_note.lower()


def test_most_likely_score_matches_primary_outcome():
    match = get_demo_match("today-rsa-can")
    assert match is not None
    result = simulate_prediction(match, Settings(default_simulations=5_000), seed=42, simulations=5_000)
    home_goals, away_goals = [int(value) for value in result.most_likely_score.split("-")]
    if result.primary_outcome == "home":
        assert home_goals > away_goals
    elif result.primary_outcome == "away":
        assert away_goals > home_goals
    else:
        assert home_goals == away_goals


def test_all_today_predictions_are_coherent():
    settings = Settings(default_simulations=3_000)
    for match in get_demo_matches():
        result = simulate_prediction(match, settings, seed=101, simulations=3_000)
        total = result.probabilities.home_win + result.probabilities.draw + result.probabilities.away_win
        assert round(total, 2) == 100.00
        home_goals, away_goals = [int(value) for value in result.most_likely_score.split("-")]
        if result.primary_outcome == "home":
            assert home_goals > away_goals
        elif result.primary_outcome == "away":
            assert away_goals > home_goals
        else:
            assert home_goals == away_goals


def test_prediction_exposes_professional_scouting_signals():
    match = get_demo_match("today-rsa-can")
    assert match is not None
    result = simulate_prediction(match, Settings(default_simulations=3_000), seed=77, simulations=3_000)
    factor_names = {factor.name for factor in result.factors}
    component_names = {component.name for component in result.model_components}
    assert "Titulares disponibles" in factor_names
    assert "Goles esperados/xG" in factor_names
    assert "Estabilidad tactica" in factor_names
    assert "Scouting titulares/xG" in component_names


def test_summary_explains_advanced_methodology():
    match = get_demo_match("today-rsa-can")
    assert match is not None
    result = simulate_prediction(match, Settings(default_simulations=3_000), seed=88, simulations=3_000)
    summary = result.executive_summary.lower()
    assert "titulares" in summary
    assert "markov" in summary
    assert "bellman" in summary
    assert "grafo de conocimiento" in summary
    assert "monte carlo" in summary


def test_model_version_is_scouting_calibrated():
    match = get_demo_match("today-rsa-can")
    assert match is not None
    result = simulate_prediction(match, Settings(), seed=42, simulations=3_000)
    assert result.model_version == "demo-audit-calibrado-0.4.0"


def test_future_fixture_is_loaded_from_today_onward():
    matches = get_demo_matches()
    assert len(matches) == 16
    assert matches[0].id == "today-rsa-can"
    assert all(match.kickoff.date().isoformat() >= "2026-06-28" for match in matches)
    assert {match.id for match in matches} >= {"r32-bra-jpn", "r32-arg-cpv", "r32-col-gha"}


def test_every_future_match_has_scouting_profile():
    from app.services.prediction_engine import SCOUTING_PROFILES

    for match in get_demo_matches():
        assert match.home_team.id in SCOUTING_PROFILES
        assert match.away_team.id in SCOUTING_PROFILES


def test_demo_quality_gate_blocks_fake_perfection_claims():
    settings = Settings(default_simulations=4_000, demo_mode=True)
    forbidden_copy = ("perfect", "seguro", "garant", "datos insuficientes", "modo demo")
    for match in get_demo_matches():
        result = simulate_prediction(match, settings, seed=20260628, simulations=4_000)
        top = max(result.probabilities.home_win, result.probabilities.draw, result.probabilities.away_win)
        assert 0 <= top <= 95
        assert result.confidence in {"media", "baja"}
        assert result.confidence != "alta"
        lowered = result.confidence_note.lower()
        assert all(word not in lowered for word in forbidden_copy)


def test_model_component_weights_are_balanced():
    match = get_demo_match("today-rsa-can")
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


def test_postmatch_audit_reduces_yesterday_favorite_bias():
    settings = Settings(default_simulations=4_000, demo_mode=True)

    germany = get_demo_match("r32-ger-par")
    assert germany is not None
    germany_result = simulate_prediction(germany, settings, seed=20260630, simulations=4_000)
    assert germany_result.probabilities.home_win < 72
    assert germany_result.most_likely_score in {"1-0", "2-1", "1-1"}

    netherlands = get_demo_match("r32-ned-mar")
    assert netherlands is not None
    netherlands_result = simulate_prediction(netherlands, settings, seed=20260630, simulations=4_000)
    assert netherlands_result.probabilities.home_win < 60
    assert "Auditoria postpartido" in {factor.name for factor in netherlands_result.factors}


def test_penalty_edge_uses_keeper_resilience_and_not_only_elo():
    from app.services.prediction_engine import penalty_home_edge, scouting

    match = get_demo_match("r32-ger-par")
    assert match is not None
    edge = penalty_home_edge(match, scouting(match.home_team.id), scouting(match.away_team.id))
    assert edge < 0.56


def test_today_mexico_ecuador_stays_cautious_after_audit():
    match = get_demo_match("r32-mex-ecu")
    assert match is not None
    result = simulate_prediction(match, Settings(default_simulations=4_000), seed=20260630, simulations=4_000)
    assert result.primary_outcome == "draw"
    assert result.probabilities.draw < 45
    assert abs((result.qualification_probability_home or 0) - (result.qualification_probability_away or 0)) < 8
