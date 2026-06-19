from __future__ import annotations

from match_simulator.models import FootballDataBundle, HistoricalMatch, Player, PredictionResult, Variable

MATCH_INFO = {
    "대회": "2026 FIFA 월드컵",
    "라운드": "조별리그",
    "매치업": "대한민국 vs 멕시코",
    "개최": "멕시코 (공동개최)",
    "킥오프": "2026.06.19 (A조)",
}

QUICK_SCENARIOS = [
    "손흥민이 10분 만에 부상으로 교체된다면?",
    "전반 종료 직전 멕시코가 선제골을 넣는다면?",
    "후반 추가시간, 한국이 측면 프리킥을 얻는다면?",
    "폭우로 잔디가 매우 나빠진다면?",
    "멕시코 홈 관중 응원이 극대화된다면?",
]

GLOSSARY = {
    "xG": "기대 득점. 해당 팀이 평균적으로 넣을 것으로 예상되는 골 수입니다.",
    "몬테카를로": "같은 조건으로 수천 번 경기를 가상 재현해 확률 분포를 만드는 방법입니다.",
    "Poisson": "득점처럼 드물게 일어나는 사건의 확률을 계산하는 통계 모델입니다.",
    "민감도": "특정 변수 가중치를 바꿨을 때 결과가 얼마나 흔들리는지 보는 분석입니다.",
}


def average_rating(players: list[Player]) -> float:
    return round(sum(p.rating for p in players) / len(players), 1)


def form_record(matches: list[HistoricalMatch]) -> tuple[int, int, int]:
    wins = sum(1 for m in matches if m.result == "W")
    draws = sum(1 for m in matches if m.result == "D")
    losses = sum(1 for m in matches if m.result == "L")
    return wins, draws, losses


def form_rate(matches: list[HistoricalMatch]) -> float:
    if not matches:
        return 0.0
    wins, draws, _ = form_record(matches)
    return round((wins + draws * 0.5) / len(matches) * 100, 0)


def detect_bias(variables: list[Variable], threshold: float = 5.0) -> tuple[str, float]:
    total = sum(v.weight for v in variables) or 1
    advantage = sum((v.home_score - v.away_score) * (v.weight / total) for v in variables)
    if advantage > threshold:
        return "🇰🇷 대한민국 쪽으로 기울어짐", round(advantage, 1)
    if advantage < -threshold:
        return "🇲🇽 멕시코 쪽으로 기울어짐", round(abs(advantage), 1)
    return "⚖️ 양팀 균형", round(abs(advantage), 1)


def model_confidence(variables: list[Variable], weight_total: int) -> tuple[int, str]:
    score = 100
    if weight_total != 100:
        score -= 25
    uncertainty = next((v for v in variables if v.id == "v9"), None)
    if uncertainty and uncertainty.home_score >= 45 and uncertainty.away_score >= 45:
        score -= 10
    if score >= 75:
        label = "높음"
    elif score >= 50:
        label = "보통"
    else:
        label = "낮음"
    return score, label


def favored_outcome(prediction: PredictionResult) -> tuple[str, int]:
    options = [
        ("🇰🇷 대한민국", prediction.home_win_prob),
        ("🤝 무승부", prediction.draw_prob),
        ("🇲🇽 멕시코", prediction.away_win_prob),
    ]
    label, prob = max(options, key=lambda item: item[1])
    return label, prob


def build_sidebar_insights(
    prediction: PredictionResult,
    variables: list[Variable],
    weight_total: int,
    simulation_done: bool,
    football_data: FootballDataBundle,
) -> dict:
    bias_label, bias_delta = detect_bias(variables)
    confidence, confidence_label = model_confidence(variables, weight_total)
    favored, favored_prob = favored_outcome(prediction)
    h2h_w, h2h_d, h2h_l = form_record(football_data.h2h_matches)
    top_scenario = prediction.top_scenarios[0] if prediction.top_scenarios else None
    kor_form = form_rate(football_data.korea.recent_matches)
    mex_form = form_rate(football_data.mexico.recent_matches)

    return {
        "match_info": MATCH_INFO,
        "kor_rating": average_rating(football_data.korea.players),
        "mex_rating": average_rating(football_data.mexico.players),
        "kor_form": kor_form,
        "mex_form": mex_form,
        "h2h": f"{h2h_w}승 {h2h_d}무 {h2h_l}패 (한국 기준)",
        "favored": favored,
        "favored_prob": favored_prob,
        "likely_score": f"{top_scenario.home}:{top_scenario.away}" if top_scenario else "-",
        "bias_label": bias_label,
        "bias_delta": bias_delta,
        "confidence": confidence,
        "confidence_label": confidence_label,
        "simulation_done": simulation_done,
        "top_impact": prediction.impact_variables[0].name if prediction.impact_variables else "-",
        "data_updated": football_data.updated_at,
        "data_source": f"{football_data.korea.source} / {football_data.mexico.source}",
    }
