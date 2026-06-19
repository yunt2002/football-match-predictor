"""Shared helpers for Vercel Python functions."""

from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from match_simulator.models import PredictionResult, SimulationResult, Variable  # noqa: E402


def read_json(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("Content-Length", 0))
    raw = handler.rfile.read(length) if length else b"{}"
    return json.loads(raw.decode("utf-8") or "{}")


def send_json(handler: BaseHTTPRequestHandler, status: int, payload: dict[str, Any]) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def variable_from_dict(data: dict[str, Any]) -> Variable:
    return Variable(
        id=str(data["id"]),
        name=str(data["name"]),
        description=str(data.get("description", "")),
        question=str(data.get("question", "")),
        home_score=int(data.get("homeScore", data.get("home_score", 50))),
        away_score=int(data.get("awayScore", data.get("away_score", 50))),
        weight=int(data.get("weight", 0)),
    )


def variable_to_dict(v: Variable) -> dict[str, Any]:
    return {
        "id": v.id,
        "name": v.name,
        "description": v.description,
        "question": v.question,
        "homeScore": v.home_score,
        "awayScore": v.away_score,
        "weight": v.weight,
    }


def prediction_to_dict(p: PredictionResult) -> dict[str, Any]:
    return {
        "homeWinProb": p.home_win_prob,
        "drawProb": p.draw_prob,
        "awayWinProb": p.away_win_prob,
        "homeXg": p.home_xg,
        "awayXg": p.away_xg,
        "homeTeamScore": p.home_team_score,
        "awayTeamScore": p.away_team_score,
        "topScenarios": [
            {"home": s.home, "away": s.away, "probability": s.probability, "label": s.label}
            for s in p.top_scenarios
        ],
        "impactVariables": [
            {"name": i.name, "impact": i.impact, "description": i.description}
            for i in p.impact_variables
        ],
    }


def simulation_to_dict(s: SimulationResult) -> dict[str, Any]:
    return {
        "homeWins": s.home_wins,
        "draws": s.draws,
        "awayWins": s.away_wins,
        "total": s.total,
        "scoreHistogram": s.score_histogram,
        "timeDistribution": s.time_distribution,
    }
