"""상황판·포메이션·시나리오 → 전력 변수 연동."""

from __future__ import annotations

from copy import deepcopy

from match_simulator.engine import clone_variables, normalize_weights
from match_simulator.models import Variable
from match_simulator.tactics_board import KOR_LINEUPS, MEX_LINEUPS

FORMATION_EFFECTS: dict[str, dict[str, tuple[int, int]]] = {
    "4-3-3": {"v3": (4, 2), "v4": (-2, -1)},
    "5-2-3": {"v4": (5, -3), "v3": (-2, 1)},
    "4-4-2": {"v4": (2, 2), "v3": (-1, -1), "v6": (2, 2)},
}

INJURY_KEYWORDS = ["부상", "퇴장", "OUT", "교체"]
STAR_PLAYERS = {
    "kor": ["손흥민", "김민재", "이강인", "황희찬"],
    "mex": ["산티아고 히메네스", "에드손 알바레스", "라울 히메네스", "세사르 몬테스"],
}


def _clamp(value: int, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, value))


def _apply_var_delta(variables: list[Variable], var_id: str, home_d: int, away_d: int) -> None:
    for var in variables:
        if var.id == var_id:
            var.home_score = _clamp(var.home_score + home_d)
            var.away_score = _clamp(var.away_score + away_d)


def detect_injured_from_scenario(scenario: str) -> dict[str, list[str]]:
    injured: dict[str, list[str]] = {"kor": [], "mex": []}
    if not any(k in scenario for k in INJURY_KEYWORDS):
        return injured
    for name in STAR_PLAYERS["kor"]:
        if name in scenario and any(k in scenario for k in INJURY_KEYWORDS):
            injured["kor"].append(name)
    for name in STAR_PLAYERS["mex"]:
        if name in scenario and any(k in scenario for k in INJURY_KEYWORDS):
            injured["mex"].append(name)
    if "손흥민" in scenario and "손흥민" not in injured["kor"]:
        if any(k in scenario for k in INJURY_KEYWORDS):
            injured["kor"].append("손흥민")
    return injured


def apply_tactics_to_variables(
    variables: list[Variable],
    *,
    kor_formation: str = "4-3-3",
    mex_formation: str = "4-4-2",
    scenario: str = "",
    board_frames: list[dict] | None = None,
) -> tuple[list[Variable], list[str]]:
    adjusted = clone_variables(variables)
    notes: list[str] = []

    for formation, team_label, team_key in [
        (kor_formation, "🇰🇷", "kor"),
        (mex_formation, "🇲🇽", "mex"),
    ]:
        effects = FORMATION_EFFECTS.get(formation, {})
        for var_id, (home_d, away_d) in effects.items():
            if team_key == "kor":
                _apply_var_delta(adjusted, var_id, home_d, away_d)
            else:
                _apply_var_delta(adjusted, var_id, away_d, home_d)
        notes.append(f"{team_label} {formation} 포메이션 반영")

    injured = detect_injured_from_scenario(scenario)
    if board_frames:
        last = board_frames[-1]
        for piece in last.get("pieces", []):
            if piece.get("status") == "injured":
                team = piece.get("team", "")
                name = piece.get("name", "")
                if name and name not in injured.get(team, []):
                    injured.setdefault(team, []).append(name)

    for name in injured.get("kor", []):
        _apply_var_delta(adjusted, "v5", -12, 0)
        _apply_var_delta(adjusted, "v3", -8, 0)
        notes.append(f"🇰🇷 {name} 부상/교체 → v5·v3 하향")
    for name in injured.get("mex", []):
        _apply_var_delta(adjusted, "v5", 0, -12)
        _apply_var_delta(adjusted, "v3", 0, -8)
        notes.append(f"🇲🇽 {name} 부상/교체 → v5·v3 하향")

    if any(k in scenario for k in ["폭우", "비", "잔디", "악천후"]):
        _apply_var_delta(adjusted, "v7", -5, -5)
        _apply_var_delta(adjusted, "v3", -3, -3)
        notes.append("악천후 → 템포·환경 변수 보정")

    if "홈" in scenario or "관중" in scenario or "응원" in scenario:
        _apply_var_delta(adjusted, "v7", -5, 8)
        notes.append("멕시코 홈 어드밴티지 → v7 보정")

    if "역습" in scenario or "속공" in scenario:
        _apply_var_delta(adjusted, "v3", 6, -4)
        notes.append("한국 역습 시나리오 → v3 상향")

    adjusted = normalize_weights(adjusted)
    return adjusted, notes


def lineup_names(kor_formation: str, mex_formation: str) -> tuple[list[str], list[str]]:
    kor = [n for n, _ in KOR_LINEUPS.get(kor_formation, KOR_LINEUPS["4-3-3"])]
    mex = [n for n, _ in MEX_LINEUPS.get(mex_formation, MEX_LINEUPS["4-3-3"])]
    return kor, mex
