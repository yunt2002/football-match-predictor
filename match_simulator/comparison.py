"""예측 vs 실제 경기 결과 비교."""

from __future__ import annotations

from dataclasses import dataclass

from match_simulator.models import PredictionResult, SimulationResult


@dataclass
class ActualComparison:
    actual_home: int
    actual_away: int
    actual_outcome: str
    predicted_outcome: str
    outcome_correct: bool
    top_score_hit: bool
    predicted_top_score: str
    xg_summary: str
    mc_summary: str
    narrative: str


def _outcome(h: int, a: int) -> str:
    if h > a:
        return "home"
    if h < a:
        return "away"
    return "draw"


def _outcome_label(code: str) -> str:
    return {"home": "🇰🇷 한국 승", "draw": "무승부", "away": "🇲🇽 멕시코 승"}[code]


def compare_with_actual(
    prediction: PredictionResult,
    simulation: SimulationResult | None,
    actual_home: int,
    actual_away: int,
) -> ActualComparison:
    actual = _outcome(actual_home, actual_away)
    probs = {
        "home": prediction.home_win_prob,
        "draw": prediction.draw_prob,
        "away": prediction.away_win_prob,
    }
    predicted = max(probs, key=probs.get)
    top = prediction.top_scenarios[0]
    top_score = f"{top.home}:{top.away}"
    actual_score = f"{actual_home}:{actual_away}"
    top_hit = actual_score == top_score

    mc_line = "몬테카를로 미실행"
    if simulation:
        mc_probs = {
            "home": simulation.home_wins / simulation.total * 100,
            "draw": simulation.draws / simulation.total * 100,
            "away": simulation.away_wins / simulation.total * 100,
        }
        mc_pred = max(mc_probs, key=mc_probs.get)
        mc_line = (
            f"MC 최빈 결과: {_outcome_label(mc_pred)} "
            f"(한국 {mc_probs['home']:.1f}% / 무 {mc_probs['draw']:.1f}% / 멕시코 {mc_probs['away']:.1f}%)"
        )

    correct = predicted == actual
    narrative_parts = [
        f"실제 스코어 **{actual_home}:{actual_away}** ({_outcome_label(actual)}).",
        f"이론적 최빈 결과: **{_outcome_label(predicted)}** ({probs[predicted]:.0f}%) — "
        + ("✅ 적중" if correct else "❌ 빗나감"),
        f"유력 스코어 {top_score} {'✅ 적중' if top_hit else '❌ 빗나감'}.",
        f"xG {prediction.home_xg}:{prediction.away_xg} 대비 실제 득점 "
        f"{'한국 과득' if actual_home > prediction.home_xg else '한국 저득' if actual_home < prediction.home_xg else '한국 xG 근접'} / "
        f"{'멕시코 과득' if actual_away > prediction.away_xg else '멕시코 저득' if actual_away < prediction.away_xg else '멕시코 xG 근접'}.",
    ]

    return ActualComparison(
        actual_home=actual_home,
        actual_away=actual_away,
        actual_outcome=actual,
        predicted_outcome=predicted,
        outcome_correct=correct,
        top_score_hit=top_hit,
        predicted_top_score=top_score,
        xg_summary=f"xG {prediction.home_xg} : {prediction.away_xg}",
        mc_summary=mc_line,
        narrative="\n\n".join(narrative_parts),
    )
