from __future__ import annotations

import json
from typing import Any

from match_simulator.engine import clone_variables
from match_simulator.models import Variable


def variables_to_dict(variables: list[Variable]) -> list[dict[str, Any]]:
    return [
        {
            "id": v.id,
            "name": v.name,
            "description": v.description,
            "question": v.question,
            "home_score": v.home_score,
            "away_score": v.away_score,
            "weight": v.weight,
        }
        for v in variables
    ]


def variables_from_dict(data: list[dict[str, Any]]) -> list[Variable]:
    return [
        Variable(
            id=item["id"],
            name=item["name"],
            description=item["description"],
            question=item["question"],
            home_score=int(item["home_score"]),
            away_score=int(item["away_score"]),
            weight=int(item["weight"]),
        )
        for item in data
    ]


def export_config(variables: list[Variable], sim_count: int, preset: str | None = None) -> str:
    payload = {
        "version": "1.0",
        "preset": preset,
        "sim_count": sim_count,
        "variables": variables_to_dict(variables),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def import_config(raw: str) -> tuple[list[Variable], int, str | None]:
    payload = json.loads(raw)
    variables = variables_from_dict(payload["variables"])
    sim_count = int(payload.get("sim_count", 1000))
    preset = payload.get("preset")
    return variables, sim_count, preset


def variables_cache_key(variables: list[Variable], sim_count: int, seed: int = 42) -> tuple:
    return tuple(
        (v.id, v.home_score, v.away_score, v.weight) for v in variables
    ) + (sim_count, seed)
