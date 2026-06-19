from __future__ import annotations

from copy import deepcopy

from match_simulator.data import INITIAL_VARIABLES
from match_simulator.engine import clone_variables, normalize_weights
from match_simulator.models import Variable

PRESET_NAMES = ["균형", "한국 우세", "멕시코 우세", "최근 흐름 중시"]


def _mutate(base: list[Variable], **updates: dict[str, tuple[int, int, int]]) -> list[Variable]:
    """updates: var_id -> (home_score, away_score, weight)"""
    result = clone_variables(base)
    for var in result:
        if var.id in updates:
            home, away, weight = updates[var.id]
            var.home_score = home
            var.away_score = away
            var.weight = weight
    return normalize_weights(result)


def get_preset(name: str) -> list[Variable]:
    base = clone_variables(INITIAL_VARIABLES)

    if name == "균형":
        return base

    if name == "한국 우세":
        mutated = deepcopy(base)
        for var in mutated:
            var.home_score = min(100, var.home_score + 8)
            var.away_score = max(0, var.away_score - 5)
        for var in mutated:
            if var.id == "v5":
                var.weight = 18
            if var.id == "v7":
                var.weight = 15
            if var.id == "v1":
                var.weight = 10
        return normalize_weights(mutated)

    if name == "멕시코 우세":
        mutated = deepcopy(base)
        for var in mutated:
            var.away_score = min(100, var.away_score + 8)
            var.home_score = max(0, var.home_score - 5)
        for var in mutated:
            if var.id == "v1":
                var.weight = 20
            if var.id == "v4":
                var.weight = 18
            if var.id == "v7":
                var.weight = 12
        return normalize_weights(mutated)

    if name == "최근 흐름 중시":
        return _mutate(
            base,
            v2=(85, 55, 30),
            v1=(70, 78, 8),
            v3=(72, 68, 12),
            v4=(58, 72, 10),
            v5=(88, 52, 8),
            v6=(65, 65, 7),
            v7=(80, 45, 8),
            v8=(42, 58, 4),
            v9=(50, 50, 3),
        )

    return base
