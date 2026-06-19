from match_simulator.checklist import build_pre_match_checklist, checklist_progress
from match_simulator.comparison import compare_with_actual
from match_simulator.data import INITIAL_VARIABLES
from match_simulator.engine import compute_half_time_predictions, compute_mc_confidence_intervals, compute_prediction, run_monte_carlo
from match_simulator.player_whatif import apply_player_whatif
from match_simulator.tactics_link import apply_tactics_to_variables
from match_simulator.tournament import get_group_a_standings, project_standings_impact
from match_simulator.url_share import decode_share_payload, encode_share_payload


def test_tactics_link_adjusts_variables():
    adjusted, notes = apply_tactics_to_variables(
        INITIAL_VARIABLES,
        kor_formation="5-2-3",
        mex_formation="4-3-3",
        scenario="손흥민 부상 교체",
    )
    assert notes
    base = compute_prediction(INITIAL_VARIABLES)
    linked = compute_prediction(adjusted)
    assert linked.home_win_prob != base.home_win_prob or linked.home_xg != base.home_xg


def test_half_time_predictions():
    half = compute_half_time_predictions(INITIAL_VARIABLES)
    assert "first_half" in half
    assert half["first_half"]["home_win"] + half["first_half"]["draw"] + half["first_half"]["away_win"] == 100


def test_mc_confidence_intervals():
    pred = compute_prediction(INITIAL_VARIABLES)
    sim = run_monte_carlo(pred.home_xg, pred.away_xg, 2000, seed=1)
    ci = compute_mc_confidence_intervals(sim)
    assert ci["home"]["low"] <= ci["home"]["point"] <= ci["home"]["high"]


def test_compare_with_actual():
    pred = compute_prediction(INITIAL_VARIABLES)
    cmp = compare_with_actual(pred, None, 2, 1)
    assert cmp.actual_home == 2
    assert "실제 스코어" in cmp.narrative


def test_player_whatif():
    adjusted, notes = apply_player_whatif(INITIAL_VARIABLES, "손흥민", "kor", "out")
    assert notes
    assert compute_prediction(adjusted).home_xg != compute_prediction(INITIAL_VARIABLES).home_xg


def test_url_share_roundtrip():
    token = encode_share_payload(INITIAL_VARIABLES, 1000, "균형")
    data = decode_share_payload(token)
    assert data["sim_count"] == 1000
    assert len(data["variables"]) == len(INITIAL_VARIABLES)


def test_group_a_standings():
    rows = get_group_a_standings()
    assert len(rows) == 4
    assert rows[0]["pts"] >= rows[-1]["pts"]


def test_checklist():
    items = build_pre_match_checklist(
        weight_total=100,
        sim_count=1000,
        has_simulation=True,
        has_ai_scenario=True,
        has_report=False,
        has_board=False,
        tactics_linked=False,
    )
    done, total = checklist_progress(items)
    assert done >= 2
    assert total == 7


def test_standings_projection():
    proj = project_standings_impact(35, 28, 37)
    assert "한국" in proj.if_kor_win
