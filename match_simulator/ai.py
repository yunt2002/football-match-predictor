from __future__ import annotations

import os
from copy import deepcopy

from match_simulator.engine import compute_prediction, normalize_weights
from match_simulator.models import PredictionResult, SimulationResult, Variable

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")

SCENARIO_RULES: list[tuple[list[str], dict[str, tuple[int, int, int | None]]]] = [
    (
        ["부상", "손흥민", "교체", "퇴장"],
        {"v5": (-20, 0, 5), "v3": (-8, 0, None), "v9": (0, 0, 3)},
    ),
    (
        ["폭우", "날씨", "비", "잔디", "더위", "고도"],
        {"v7": (-10, 5, 5), "v3": (-5, -5, None), "v9": (0, 0, 3)},
    ),
    (
        ["수비", "실점", "카운터"],
        {"v4": (5, -10, 5), "v3": (-5, 5, None)},
    ),
    (
        ["공격", "득점", "골"],
        {"v3": (10, 5, 5), "v4": (-5, 0, None)},
    ),
    (
        ["응원", "홈", "관중", "원정"],
        {"v7": (10, -10, 8)},
    ),
]


def _apply_delta(value: int, delta: int, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, value + delta))


def adjust_variables_for_scenario(scenario: str, variables: list[Variable]) -> list[Variable]:
    adjusted = [v.copy() for v in deepcopy(variables)]
    lowered = scenario.lower()

    for keywords, changes in SCENARIO_RULES:
        if any(keyword in scenario or keyword in lowered for keyword in keywords):
            for var in adjusted:
                if var.id in changes:
                    home_delta, away_delta, weight_delta = changes[var.id]
                    var.home_score = _apply_delta(var.home_score, home_delta)
                    var.away_score = _apply_delta(var.away_score, away_delta)
                    if weight_delta is not None:
                        var.weight = _apply_delta(var.weight, weight_delta, 0, 100)

    return normalize_weights(adjusted)


def _call_openai(prompt: str) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", OPENAI_MODEL)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "당신은 축구 데이터·전술 분석 전문가입니다. 마크다운으로 명확하고 객관적으로 답합니다.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    content = response.choices[0].message.content
    return content.strip() if content else None


def simulate_scenario(
    scenario: str,
    variables: list[Variable],
    home_team: str = "대한민국",
    away_team: str = "멕시코",
) -> str:
    adjusted = adjust_variables_for_scenario(scenario, variables)
    baseline = compute_prediction(variables)
    adjusted_pred = compute_prediction(adjusted)

    var_lines = "\n".join(
        f"- {v.name}: {home_team}({v.home_score}), {away_team}({v.away_score}), 중요도({v.weight}%)"
        for v in variables
    )
    prompt = f"""
{home_team} vs {away_team} 경기에서 아래 시나리오를 분석하세요.

[현재 지표]
{var_lines}

[시나리오]
"{scenario}"

[기준 이론적 승률] 한국 {baseline.home_win_prob}% / 무 {baseline.draw_prob}% / 멕시코 {baseline.away_win_prob}%
[규칙 보정 후] 한국 {adjusted_pred.home_win_prob}% / 무 {adjusted_pred.draw_prob}% / 멕시코 {adjusted_pred.away_win_prob}%

마크다운으로 전술 영향, 경기 흐름, 수정 확률, 총평을 작성하세요.
수정 확률은 규칙 보정 값과 크게 어긋나지 않게 하세요.
"""
    try:
        ai_text = _call_openai(prompt)
        if ai_text:
            return ai_text
    except Exception as exc:
        return _rule_based_scenario(scenario, baseline, adjusted_pred, home_team, away_team, error=str(exc))

    return _rule_based_scenario(scenario, baseline, adjusted_pred, home_team, away_team)


def _rule_based_scenario(
    scenario: str,
    baseline: PredictionResult,
    adjusted: PredictionResult,
    home_team: str,
    away_team: str,
    error: str | None = None,
) -> str:
    matched = []
    for keywords, _ in SCENARIO_RULES:
        if any(k in scenario for k in keywords):
            matched.extend(keywords)
    matched = list(dict.fromkeys(matched))[:5]

    header = "## AI 시나리오 시뮬레이션 결과 (규칙 기반)\n\n"
    if error:
        header += f"> OpenAI 호출 실패: {error}\n\n"

    return header + f"""### 1. 전술적 영향 분석
입력 시나리오: **"{scenario}"**
감지된 키워드: {", ".join(matched) if matched else "일반적 불확실성"}

- 기준 xG: {baseline.home_xg} vs {baseline.away_xg}
- 보정 xG: {adjusted.home_xg} vs {adjusted.away_xg}

### 2. 경기 흐름 및 결정적 장면
- 돌발 상황 이후 템포와 수비 라인 높이 조정이 핵심 변수가 됩니다.
- {'공격 옵션 감소로 측면 돌파 비중이 줄어들 수 있습니다.' if '부상' in scenario or '손흥민' in scenario else '양 팀 모두 리스크 관리형 전술로 전환할 가능성이 있습니다.'}

### 3. 최종 예측 결과 (수정된 확률)
- {home_team} 승리: **{adjusted.home_win_prob}%** (기준 {baseline.home_win_prob}%)
- 무승부: **{adjusted.draw_prob}%** (기준 {baseline.draw_prob}%)
- {away_team} 승리: **{adjusted.away_win_prob}%** (기준 {baseline.away_win_prob}%)
- 예상 스코어: **{adjusted.top_scenarios[0].home} : {adjusted.top_scenarios[0].away}**

### 4. 분석 결과 총평
시나리오 반영 후 한국 승률 변화 **{adjusted.home_win_prob - baseline.home_win_prob:+d}%p**.
단일 스코어보다 **확률 분포 전체**를 함께 해석하는 것이 중요합니다.
"""


def generate_match_report(
    variables: list[Variable],
    prediction: PredictionResult,
    simulation: SimulationResult | None = None,
    home_team: str = "대한민국",
    away_team: str = "멕시코",
) -> str:
    top_scenario = prediction.top_scenarios[0]
    impacts = prediction.impact_variables

    sim_line = ""
    if simulation:
        sim_line = (
            f"\n몬테카를로({simulation.total:,}회): "
            f"한국 {simulation.home_wins / simulation.total * 100:.1f}% / "
            f"무 {simulation.draws / simulation.total * 100:.1f}% / "
            f"멕시코 {simulation.away_wins / simulation.total * 100:.1f}%"
        )

    var_lines = "\n".join(
        f"- {v.name}: {home_team} {v.home_score}, {away_team} {v.away_score}, 가중치 {v.weight}%"
        for v in variables
    )
    prompt = f"""
스포츠 데이터 분석가로서 마크다운 리포트를 작성하세요.

팀: {home_team} vs {away_team}
변수:
{var_lines}

이론적 승률: {home_team} {prediction.home_win_prob}%, 무 {prediction.draw_prob}%, {away_team} {prediction.away_win_prob}%
xG: {prediction.home_xg} vs {prediction.away_xg}
유력 스코어: {top_scenario.home}:{top_scenario.away}{sim_line}

섹션: 경기 결과 확률, 예상 득점, 핵심 변수 TOP3, 모델 한계.
숫자는 제공된 값과 일치해야 합니다. 편향 없이 작성하세요.
"""
    try:
        ai_text = _call_openai(prompt)
        if ai_text:
            return ai_text
    except Exception:
        pass

    impact_text = "\n".join(
        f"{i}. **{item.name}**: {item.description} (영향도 {item.impact * 10:.1f})"
        for i, item in enumerate(impacts, start=1)
    )

    return f"""## 매치 예측 리포트: {home_team} vs {away_team}

### 1. 경기 결과 확률 (이론적)
- {home_team} 승리: **{prediction.home_win_prob}%**
- 무승부: **{prediction.draw_prob}%**
- {away_team} 승리: **{prediction.away_win_prob}%**
{sim_line}

### 2. 예상 득점 및 스코어
- xG: {home_team} **{prediction.home_xg}** / {away_team} **{prediction.away_xg}**
- 유력 스코어: **{top_scenario.home} : {top_scenario.away}** ({top_scenario.probability}%)

### 3. 핵심 변수 TOP 3
{impact_text}

### 4. 모델의 가정 및 한계
- 사용자가 설정한 변수·가중치 기반 **교육용 추정**입니다.
- 35% 승률 팀이 이겨도 모델 오류가 아니라 **확률 실현**일 수 있습니다.
- 부상, 날씨, 심판 등 미반영 변수가 존재합니다.
"""
