from match_simulator.ai import adjust_variables_for_scenario, simulate_scenario
from match_simulator.data import INITIAL_VARIABLES
from match_simulator.engine import compute_prediction
from match_simulator.serialization import export_config, import_config


def test_scenario_adjustment_changes_prediction():
    baseline = compute_prediction(INITIAL_VARIABLES)
    adjusted_vars = adjust_variables_for_scenario("손흥민 부상 교체", INITIAL_VARIABLES)
    adjusted = compute_prediction(adjusted_vars)
    assert adjusted.home_team_score != baseline.home_team_score
    assert adjusted.home_xg != baseline.home_xg


def test_rule_based_scenario_returns_markdown():
    result = simulate_scenario("폭우로 경기 지연", INITIAL_VARIABLES)
    assert "시나리오" in result
    assert "%" in result


def test_config_roundtrip():
    raw = export_config(INITIAL_VARIABLES, 1000, "균형")
    variables, sim_count, preset = import_config(raw)
    assert sim_count == 1000
    assert preset == "균형"
    assert len(variables) == len(INITIAL_VARIABLES)
