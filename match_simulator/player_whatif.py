"""선수 단위 What-if → 변수 보정."""

from __future__ import annotations

from match_simulator.engine import clone_variables, normalize_weights
from match_simulator.models import Player, Variable

PLAYER_EFFECTS: dict[str, dict[str, tuple[int, int, str]]] = {
    "손흥민": {"v5": (-22, 0, "공격 허브"), "v3": (-10, 0, "왼쪽 측면 득점원")},
    "김민재": {"v4": (-18, 0, "수비 조직력"), "v2": (-8, 0, "볼 빌드업")},
    "이강인": {"v3": (-12, 0, "창의적 패스"), "v5": (-8, 0, "세트피스·연결")},
    "황희찬": {"v3": (-10, 0, "측면 돌파"), "v5": (-6, 0, "속도 옵션")},
    "황인범": {"v2": (-10, 0, "중원 커버"), "v6": (-6, 0, "전술 안정성")},
    "조규성": {"v3": (-8, 0, "공격 포인트")},
    "산티아고 히메네스": {"v5": (0, -20, "공격 허브"), "v3": (0, -12, "페널티 박스")},
    "에드손 알바레스": {"v3": (0, -14, "전방 압박·연결"), "v5": (0, -10, "경험")},
    "라울 히메네스": {"v3": (0, -12, "공격 전개"), "v5": (0, -8, "경험")},
    "세사르 몬테스": {"v4": (0, -16, "수비 리더"), "v2": (0, -6, "빌드업")},
    "기예르모 오초아": {"v4": (0, -10, "GK 안정감")},
    "오초아": {"v4": (0, -10, "GK 안정감")},
}


def find_player_by_name(players: list[Player], name: str) -> Player | None:
    for player in players:
        if player.name == name or name in player.name:
            return player
    return None


def list_whatif_options(players: list[Player]) -> list[str]:
    return [p.name for p in players if p.name in PLAYER_EFFECTS or any(k in p.name for k in PLAYER_EFFECTS)]


def _resolve_effects(name: str) -> dict[str, tuple[int, int, str]]:
    if name in PLAYER_EFFECTS:
        return PLAYER_EFFECTS[name]
    for key, effects in PLAYER_EFFECTS.items():
        if key in name or name in key:
            return effects
    return {}


def apply_player_whatif(
    variables: list[Variable],
    player_name: str,
    team: str,
    mode: str = "out",
) -> tuple[list[Variable], list[str]]:
    adjusted = clone_variables(variables)
    effects = _resolve_effects(player_name)
    if not effects:
        return adjusted, [f"{player_name}: 매핑된 변수 효과 없음"]

    notes: list[str] = []
    multiplier = -1 if mode == "out" else 1
    label = "부재" if mode == "out" else "풀타임/부스트"

    for var_id, (home_d, away_d, reason) in effects.items():
        for var in adjusted:
            if var.id != var_id:
                continue
            if team == "kor":
                var.home_score = max(0, min(100, var.home_score + home_d * multiplier))
            else:
                var.away_score = max(0, min(100, var.away_score + away_d * multiplier))
            notes.append(f"{player_name} {label} → {var.name} ({reason})")

    return normalize_weights(adjusted), notes
