from match_simulator.data import build_static_bundle, INITIAL_VARIABLES
from match_simulator.engine import compute_prediction
from match_simulator.insights import build_sidebar_insights, detect_bias


def test_bias_detection_balanced():
    label, _ = detect_bias(INITIAL_VARIABLES)
    assert "균형" in label or "기울" in label


def test_sidebar_insights_keys():
    prediction = compute_prediction(INITIAL_VARIABLES)
    bundle = build_static_bundle()
    insights = build_sidebar_insights(prediction, INITIAL_VARIABLES, 100, False, bundle)
    assert "favored" in insights
    assert insights["kor_rating"] > 0
    assert len(bundle.korea.players) == 26
