"""API-Football 연동 및 최신 데이터 로드."""

from __future__ import annotations

import os
from datetime import datetime, timezone

import requests

from match_simulator.data import (
    DATA_VERSION,
    H2H_MATCHES,
    KOR_FULL_SQUAD,
    KOR_RECENT_MATCHES,
    MEX_FULL_SQUAD,
    MEX_RECENT_MATCHES,
    build_static_bundle,
    get_key_players,
)
from match_simulator.models import FootballDataBundle, HistoricalMatch, Player, TeamProfile

API_BASE = "https://v3.football.api-sports.io"
TEAM_IDS = {"KOR": 776, "MEX": 16}
POSITION_MAP = {
    "Goalkeeper": "GK",
    "Defender": "DF",
    "Midfielder": "MF",
    "Attacker": "FW",
}


class DataLoadError(Exception):
    pass


def _headers() -> dict[str, str]:
    api_key = os.getenv("API_FOOTBALL_KEY") or os.getenv("APISPORTS_KEY")
    if not api_key:
        raise DataLoadError("API_FOOTBALL_KEY가 설정되지 않았습니다.")
    return {"x-apisports-key": api_key}


def _get(endpoint: str, params: dict) -> dict:
    response = requests.get(f"{API_BASE}/{endpoint}", headers=_headers(), params=params, timeout=20)
    response.raise_for_status()
    payload = response.json()
    if payload.get("errors"):
        raise DataLoadError(str(payload["errors"]))
    return payload


def _estimate_rating(position: str, index: int) -> int:
    base = {"GK": 76, "DF": 77, "MF": 78, "FW": 79}.get(position, 76)
    return max(70, min(92, base + (3 if index < 3 else 0)))


def _parse_squad(team_code: str, response: list) -> list[Player]:
    if not response:
        return []
    squad = response[0].get("players", [])
    players: list[Player] = []
    for idx, item in enumerate(squad):
        pos = POSITION_MAP.get(item.get("position", ""), "MF")
        players.append(
            Player(
                id=f"{team_code.lower()}_{idx}",
                name=item.get("name", "Unknown"),
                position=pos,
                club=item.get("team", {}).get("name", "-") if isinstance(item.get("team"), dict) else "-",
                rating=_estimate_rating(pos, idx),
                number=item.get("number"),
            )
        )
    return players


def _parse_result_for_team(team_name: str, home: dict, away: dict, goals_home: int, goals_away: int) -> str:
    is_home = team_name.lower() in home.get("name", "").lower()
    my_goals = goals_home if is_home else goals_away
    opp_goals = goals_away if is_home else goals_home
    if my_goals > opp_goals:
        return "W"
    if my_goals < opp_goals:
        return "L"
    return "D"


def _parse_fixtures(team_code: str, team_name: str, response: list, limit: int = 10) -> list[HistoricalMatch]:
    matches: list[HistoricalMatch] = []
    for idx, item in enumerate(response[:limit]):
        fixture = item["fixture"]
        league = item["league"]
        teams = item["teams"]
        goals = item["goals"]
        date_raw = fixture.get("date", "")[:10].replace("-", ".")
        home = teams["home"]
        away = teams["away"]
        gh = goals.get("home") or 0
        ga = goals.get("away") or 0
        is_home = team_name.lower() in home["name"].lower()
        score = f"{gh}:{ga}" if is_home else f"{ga}:{gh}"
        opponent = away["name"] if is_home else home["name"]
        result = _parse_result_for_team(team_name, home, away, gh, ga)
        matches.append(
            HistoricalMatch(
                id=f"{team_code.lower()}_api_{idx}",
                date=date_raw,
                competition=league.get("name", "경기"),
                score=score,
                result=result,
                opponent=opponent,
            )
        )
    return matches


def fetch_team_profile(team_code: str, last_fixtures: int = 10) -> TeamProfile:
    team_id = TEAM_IDS[team_code]
    meta = {"KOR": ("대한민국", "🇰🇷"), "MEX": ("멕시코", "🇲🇽")}[team_code]
    squad_payload = _get("players/squads", {"team": team_id})
    players = _parse_squad(team_code, squad_payload.get("response", []))
    if not players:
        fallback = KOR_FULL_SQUAD if team_code == "KOR" else MEX_FULL_SQUAD
        players = [p.copy() if hasattr(p, "copy") else p for p in fallback]

    fixture_payload = _get("fixtures", {"team": team_id, "last": last_fixtures})
    recent = _parse_fixtures(team_code, meta[0], fixture_payload.get("response", []), last_fixtures)
    if not recent:
        recent = KOR_RECENT_MATCHES if team_code == "KOR" else MEX_RECENT_MATCHES

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return TeamProfile(team_code, meta[0], meta[1], players, recent, "api", now)


def load_football_data(use_api: bool = True) -> FootballDataBundle:
    if not use_api:
        return build_static_bundle()

    api_key = os.getenv("API_FOOTBALL_KEY") or os.getenv("APISPORTS_KEY")
    if not api_key:
        bundle = build_static_bundle()
        bundle.korea.source = "static (API 키 없음)"
        bundle.mexico.source = "static (API 키 없음)"
        return bundle

    try:
        korea = fetch_team_profile("KOR")
        mexico = fetch_team_profile("MEX")
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        return FootballDataBundle(korea=korea, mexico=mexico, h2h_matches=H2H_MATCHES, updated_at=now)
    except Exception:
        return build_static_bundle()


def merge_api_with_static(bundle: FootballDataBundle) -> FootballDataBundle:
    """API squad가 비어 있으면 정적 2026 월드컵 명단으로 보완."""
    static = build_static_bundle()
    if len(bundle.korea.players) < 20:
        bundle.korea.players = static.korea.players
        bundle.korea.source = f"{bundle.korea.source}+static"
    if len(bundle.mexico.players) < 20:
        bundle.mexico.players = static.mexico.players
        bundle.mexico.source = f"{bundle.mexico.source}+static"
    return bundle
