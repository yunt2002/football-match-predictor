from match_simulator.data import INITIAL_VARIABLES
from match_simulator.engine import (
    compute_prediction,
    compute_score_matrix,
    normalize_weights,
    run_monte_carlo,
)


def test_prediction_probabilities_sum_to_100():
    result = compute_prediction(INITIAL_VARIABLES)
    assert result.home_win_prob + result.draw_prob + result.away_win_prob == 100


def test_score_matrix_sums_near_one():
    prediction = compute_prediction(INITIAL_VARIABLES)
    matrix = compute_score_matrix(prediction.home_xg, prediction.away_xg)
    # 0~4골까지만 계산하므로 꼬리 확률 일부는 제외됨
    assert 0.85 <= matrix.sum() <= 1.0


def test_monte_carlo_totals():
    prediction = compute_prediction(INITIAL_VARIABLES)
    sim = run_monte_carlo(prediction.home_xg, prediction.away_xg, 500, seed=42)
    assert sim.home_wins + sim.draws + sim.away_wins == sim.total == 500


def test_normalize_weights_sum_to_100():
    variables = [v.copy() for v in INITIAL_VARIABLES]
    for var in variables:
        var.weight = 10
    normalized = normalize_weights(variables)
    assert sum(v.weight for v in normalized) == 100


def test_xg_positive():
    result = compute_prediction(INITIAL_VARIABLES)
    assert result.home_xg > 0
    assert result.away_xg > 0
