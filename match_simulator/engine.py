from __future__ import annotations

import math
import random
from copy import deepcopy

import numpy as np

from match_simulator.models import (
    ImpactVariable,
    PredictionResult,
    ScoreScenario,
    SimulationResult,
    Variable,
)


def _probs_from_xg(home_xg: float, away_xg: float) -> tuple[float, float, float]:
    diff_xg = home_xg - away_xg
    draw_prob = max(10, 30 - abs(diff_xg) * 10)
    rem_prob = 100 - draw_prob
    home_win_prob = max(5, min(rem_prob - 5, (rem_prob / 2) + (diff_xg * 15)))
    away_win_prob = 100 - draw_prob - home_win_prob
    return round(home_win_prob, 1), round(draw_prob, 1), round(away_win_prob, 1)


def compute_half_time_predictions(variables: list[Variable]) -> dict[str, dict[str, float]]:
    full = compute_prediction(variables)
    stamina_mod = _get_mod(variables, "v2", "home") - _get_mod(variables, "v2", "away")
    fh_home = max(0.08, full.home_xg * 0.48)
    fh_away = max(0.08, full.away_xg * 0.48)
    sh_home = max(0.08, full.home_xg * 0.52 + stamina_mod * 0.15)
    sh_away = max(0.08, full.away_xg * 0.52 - stamina_mod * 0.15)
    fh_probs = _probs_from_xg(fh_home, fh_away)
    sh_probs = _probs_from_xg(sh_home, sh_away)
    return {
        "full_time": {
            "home_xg": full.home_xg,
            "away_xg": full.away_xg,
            "home_win": full.home_win_prob,
            "draw": full.draw_prob,
            "away_win": full.away_win_prob,
        },
        "first_half": {
            "home_xg": round(fh_home, 2),
            "away_xg": round(fh_away, 2),
            "home_win": fh_probs[0],
            "draw": fh_probs[1],
            "away_win": fh_probs[2],
        },
        "second_half": {
            "home_xg": round(sh_home, 2),
            "away_xg": round(sh_away, 2),
            "home_win": sh_probs[0],
            "draw": sh_probs[1],
            "away_win": sh_probs[2],
        },
    }


def compute_mc_confidence_intervals(sim: SimulationResult, z: float = 1.96) -> dict[str, dict[str, float]]:
    n = sim.total

    def interval(wins: int) -> dict[str, float]:
        p = wins / n
        margin = z * math.sqrt(max(p * (1 - p) / n, 1e-9)) * 100
        center = p * 100
        return {"point": round(center, 1), "low": round(max(0, center - margin), 1), "high": round(min(100, center + margin), 1)}

    return {
        "home": interval(sim.home_wins),
        "draw": interval(sim.draws),
        "away": interval(sim.away_wins),
    }


def normalize_weights(variables: list[Variable]) -> list[Variable]:
    total = sum(v.weight for v in variables)
    if total == 0:
        return variables
    result = [
        Variable(
            id=v.id,
            name=v.name,
            description=v.description,
            question=v.question,
            home_score=v.home_score,
            away_score=v.away_score,
            weight=round(v.weight / total * 100),
        )
        for v in variables
    ]
    diff = 100 - sum(v.weight for v in result)
    if diff != 0:
        max_idx = max(range(len(result)), key=lambda i: result[i].weight)
        fixed = result[max_idx]
        result[max_idx] = Variable(
            id=fixed.id,
            name=fixed.name,
            description=fixed.description,
            question=fixed.question,
            home_score=fixed.home_score,
            away_score=fixed.away_score,
            weight=fixed.weight + diff,
        )
    return result


def _mod(score: int) -> float:
    return (score - 50) / 50


def _get_mod(variables: list[Variable], var_id: str, side: str) -> float:
    var = next((v for v in variables if v.id == var_id), None)
    if var is None:
        return 0.0
    score = var.home_score if side == "home" else var.away_score
    return _mod(score)


def _poisson(lambda_val: float, k: int) -> float:
    return (lambda_val**k * math.exp(-lambda_val)) / math.factorial(k)


def compute_prediction(variables: list[Variable]) -> PredictionResult:
    total_weight = sum(v.weight for v in variables)
    safe_sum = total_weight if total_weight else 1

    home_team_score = sum(v.home_score * (v.weight / safe_sum) for v in variables)
    away_team_score = sum(v.away_score * (v.weight / safe_sum) for v in variables)

    home_xg = max(
        0.1,
        1.0
        + _get_mod(variables, "v3", "home")
        - _get_mod(variables, "v4", "away")
        + _get_mod(variables, "v2", "home")
        + _get_mod(variables, "v6", "home"),
    )
    away_xg = max(
        0.1,
        1.0
        + _get_mod(variables, "v3", "away")
        - _get_mod(variables, "v4", "home")
        + _get_mod(variables, "v7", "away")
        + _get_mod(variables, "v2", "away"),
    )

    diff_xg = home_xg - away_xg
    draw_prob = max(10, 30 - abs(diff_xg) * 10)
    rem_prob = 100 - draw_prob
    home_win_prob = max(5, min(rem_prob - 5, (rem_prob / 2) + (diff_xg * 15)))
    away_win_prob = 100 - draw_prob - home_win_prob

    scores: list[tuple[int, int, float]] = []
    for home_goals in range(5):
        for away_goals in range(5):
            prob = _poisson(home_xg, home_goals) * _poisson(away_xg, away_goals)
            scores.append((home_goals, away_goals, prob))

    top3 = sorted(scores, key=lambda item: item[2], reverse=True)[:3]
    labels = ["가장 현실적인 시나리오", "차선 시나리오 1", "차선 시나리오 2"]
    top_scenarios = [
        ScoreScenario(h, a, round(p * 100), labels[i]) for i, (h, a, p) in enumerate(top3)
    ]

    impacts = sorted(
        (
            ImpactVariable(
                name=v.name,
                impact=abs(v.home_score - v.away_score) * (v.weight / safe_sum),
                description=v.description,
            )
            for v in variables
        ),
        key=lambda item: item.impact,
        reverse=True,
    )[:3]

    return PredictionResult(
        home_win_prob=round(home_win_prob),
        draw_prob=round(draw_prob),
        away_win_prob=round(away_win_prob),
        home_xg=round(home_xg, 1),
        away_xg=round(away_xg, 1),
        home_team_score=round(home_team_score, 2),
        away_team_score=round(away_team_score, 2),
        top_scenarios=top_scenarios,
        impact_variables=impacts,
    )


def compute_score_matrix(home_xg: float, away_xg: float, max_goals: int = 4) -> np.ndarray:
    matrix = np.zeros((max_goals + 1, max_goals + 1))
    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            matrix[h, a] = _poisson(home_xg, h) * _poisson(away_xg, a)
    return matrix


def run_monte_carlo(
    home_xg: float,
    away_xg: float,
    sim_count: int,
    seed: int | None = None,
) -> SimulationResult:
    rng = np.random.default_rng(seed)
    home_goals = rng.poisson(home_xg, sim_count)
    away_goals = rng.poisson(away_xg, sim_count)

    home_wins = int(np.sum(home_goals > away_goals))
    draws = int(np.sum(home_goals == away_goals))
    away_wins = sim_count - home_wins - draws

    score_histogram: dict[str, int] = {}
    for h, a in zip(home_goals, away_goals, strict=True):
        key = f"{h}-{a}"
        score_histogram[key] = score_histogram.get(key, 0) + 1

    time_distribution = {
        "home": {f"{i * 10}-{(i + 1) * 10}": 0 for i in range(9)},
        "away": {f"{i * 10}-{(i + 1) * 10}": 0 for i in range(9)},
    }

    for goals in home_goals:
        for _ in range(int(goals)):
            minute = rng.integers(0, 90)
            bucket = f"{minute // 10 * 10}-{(minute // 10 + 1) * 10}"
            time_distribution["home"][bucket] += 1

    for goals in away_goals:
        for _ in range(int(goals)):
            minute = rng.integers(0, 90)
            bucket = f"{minute // 10 * 10}-{(minute // 10 + 1) * 10}"
            time_distribution["away"][bucket] += 1

    return SimulationResult(
        home_wins=home_wins,
        draws=draws,
        away_wins=away_wins,
        total=sim_count,
        score_histogram=score_histogram,
        time_distribution=time_distribution,
    )


def compute_sensitivity(
    variables: list[Variable],
    weight_delta: int = 10,
) -> list[dict[str, float | str]]:
    baseline = compute_prediction(variables)
    results: list[dict[str, float | str]] = []

    for target in variables:
        adjusted = clone_variables(variables)
        for var in adjusted:
            if var.id == target.id:
                var.weight = min(100, var.weight + weight_delta)
        adjusted = normalize_weights(adjusted)
        updated = compute_prediction(adjusted)
        results.append(
            {
                "변수": target.name,
                "기준 한국 승률 (%)": baseline.home_win_prob,
                "조정 후 (%)": updated.home_win_prob,
                "변화 (Δ)": updated.home_win_prob - baseline.home_win_prob,
            }
        )

    return sorted(results, key=lambda row: abs(float(row["변화 (Δ)"])), reverse=True)


def compute_stability_curve(
    home_xg: float,
    away_xg: float,
    counts: list[int] | None = None,
    seed: int = 42,
) -> list[dict[str, float | int]]:
    if counts is None:
        counts = [100, 500, 1000, 5000, 10000]

    curve: list[dict[str, float | int]] = []
    for count in counts:
        sim = run_monte_carlo(home_xg, away_xg, count, seed=seed)
        curve.append(
            {
                "시뮬레이션 횟수": count,
                "한국 승률 (%)": round(sim.home_wins / sim.total * 100, 1),
                "무승부 (%)": round(sim.draws / sim.total * 100, 1),
                "멕시코 승률 (%)": round(sim.away_wins / sim.total * 100, 1),
            }
        )
    return curve


def clone_variables(variables: list[Variable]) -> list[Variable]:
    return [v.copy() for v in deepcopy(variables)]
