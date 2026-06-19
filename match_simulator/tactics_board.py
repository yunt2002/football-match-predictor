"""전술 상황판 — 시나리오 기반 선수 말 이동 시뮬레이션."""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field

FORMATION_OPTIONS = ["4-3-3", "5-2-3", "4-4-2"]

KOR_LINEUPS: dict[str, list[tuple[str, str]]] = {
    "4-3-3": [
        ("조현우", "GK"),
        ("김민재", "DF"), ("설영우", "DF"), ("이기혁", "DF"), ("김문환", "DF"),
        ("황인범", "MF"), ("이강인", "MF"), ("이재성", "MF"),
        ("손흥민", "FW"), ("황희찬", "FW"), ("조규성", "FW"),
    ],
    "5-2-3": [
        ("조현우", "GK"),
        ("김민재", "DF"), ("설영우", "DF"), ("이기혁", "DF"), ("김문환", "DF"), ("박진섭", "DF"),
        ("황인범", "MF"), ("이강인", "MF"),
        ("손흥민", "FW"), ("황희찬", "FW"), ("조규성", "FW"),
    ],
    "4-4-2": [
        ("조현우", "GK"),
        ("김민재", "DF"), ("설영우", "DF"), ("이기혁", "DF"), ("김문환", "DF"),
        ("황인범", "MF"), ("이강인", "MF"), ("이재성", "MF"), ("김진규", "MF"),
        ("손흥민", "FW"), ("황희찬", "FW"),
    ],
}

MEX_LINEUPS: dict[str, list[tuple[str, str]]] = {
    "4-3-3": [
        ("오초아", "GK"),
        ("몬테스", "DF"), ("바스케스", "DF"), ("레예스", "DF"), ("산체스", "DF"),
        ("알바레스", "MF"), ("차베스", "MF"), ("피네다", "MF"),
        ("산티아고 히메네스", "FW"), ("라울 히메네스", "FW"), ("베가", "FW"),
    ],
    "5-2-3": [
        ("오초아", "GK"),
        ("몬테스", "DF"), ("바스케스", "DF"), ("레예스", "DF"), ("산체스", "DF"), ("갈라르도", "DF"),
        ("알바레스", "MF"), ("차베스", "MF"),
        ("산티아고 히메네스", "FW"), ("라울 히메네스", "FW"), ("베가", "FW"),
    ],
    "4-4-2": [
        ("오초아", "GK"),
        ("몬테스", "DF"), ("바스케스", "DF"), ("레예스", "DF"), ("산체스", "DF"),
        ("알바레스", "MF"), ("차베스", "MF"), ("피네다", "MF"), ("로모", "MF"),
        ("산티아고 히메네스", "FW"), ("라울 히메네스", "FW"),
    ],
}

KOR_FORMATION_SLOTS: dict[str, list[tuple[float, float]]] = {
    "4-3-3": [
        (50, 90), (18, 74), (38, 76), (62, 76), (82, 74),
        (28, 58), (50, 55), (72, 58), (28, 38), (50, 36), (72, 38),
    ],
    "5-2-3": [
        (50, 90), (12, 76), (30, 78), (50, 76), (70, 78), (88, 76),
        (38, 58), (62, 58), (28, 38), (50, 36), (72, 38),
    ],
    "4-4-2": [
        (50, 90), (18, 74), (38, 76), (62, 76), (82, 74),
        (15, 58), (38, 56), (62, 56), (85, 58), (35, 40), (65, 40),
    ],
}

MEX_FORMATION_SLOTS: dict[str, list[tuple[float, float]]] = {
    "4-3-3": [
        (50, 10), (18, 26), (38, 24), (62, 24), (82, 26),
        (28, 42), (50, 45), (72, 42), (28, 62), (50, 64), (72, 62),
    ],
    "5-2-3": [
        (50, 10), (12, 24), (30, 22), (50, 24), (70, 22), (88, 24),
        (38, 42), (62, 42), (28, 62), (50, 64), (72, 62),
    ],
    "4-4-2": [
        (50, 10), (18, 26), (38, 24), (62, 24), (82, 26),
        (15, 42), (38, 44), (62, 44), (85, 42), (35, 60), (65, 60),
    ],
}

SUBSTITUTE_NAMES = {"kor": "이동경", "mex": "우에르타"}


@dataclass
class Piece:
    id: str
    name: str
    team: str
    role: str
    x: float
    y: float
    active: bool = True
    status: str = "active"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "team": self.team,
            "role": self.role,
            "x": round(self.x, 1),
            "y": round(self.y, 1),
            "active": self.active,
            "status": self.status,
        }


@dataclass
class Arrow:
    x1: float
    y1: float
    x2: float
    y2: float
    kind: str

    def to_dict(self) -> dict:
        return {
            "x1": round(self.x1, 1),
            "y1": round(self.y1, 1),
            "x2": round(self.x2, 1),
            "y2": round(self.y2, 1),
            "kind": self.kind,
        }


@dataclass
class BoardFrame:
    label: str
    minute: str
    pieces: list[Piece]
    ball_x: float
    ball_y: float
    arrows: list[Arrow] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "minute": self.minute,
            "pieces": [p.to_dict() for p in self.pieces],
            "ball": [round(self.ball_x, 1), round(self.ball_y, 1)],
            "arrows": [a.to_dict() for a in self.arrows],
        }


def _clamp(value: float, low: float = 8, high: float = 92) -> float:
    return max(low, min(high, value))


def build_initial_pieces(
    kor_formation: str = "4-3-3",
    mex_formation: str = "4-3-3",
    custom_positions: dict[str, tuple[float, float]] | None = None,
) -> list[Piece]:
    custom_positions = custom_positions or {}
    pieces: list[Piece] = []

    kor_lineup = KOR_LINEUPS.get(kor_formation, KOR_LINEUPS["4-3-3"])
    kor_slots = KOR_FORMATION_SLOTS.get(kor_formation, KOR_FORMATION_SLOTS["4-3-3"])
    for idx, ((name, role), (x, y)) in enumerate(zip(kor_lineup, kor_slots, strict=True)):
        pid = f"k{idx}"
        if pid in custom_positions:
            x, y = custom_positions[pid]
        pieces.append(Piece(pid, name, "kor", role, x, y))

    mex_lineup = MEX_LINEUPS.get(mex_formation, MEX_LINEUPS["4-3-3"])
    mex_slots = MEX_FORMATION_SLOTS.get(mex_formation, MEX_FORMATION_SLOTS["4-3-3"])
    for idx, ((name, role), (x, y)) in enumerate(zip(mex_lineup, mex_slots, strict=True)):
        pid = f"m{idx}"
        if pid in custom_positions:
            x, y = custom_positions[pid]
        pieces.append(Piece(pid, name, "mex", role, x, y))

    return pieces


def get_formation_layout_json(kor_formation: str, mex_formation: str) -> list[dict]:
    return [p.to_dict() for p in build_initial_pieces(kor_formation, mex_formation)]


def _find_piece(pieces: list[Piece], keyword: str, team: str | None = None) -> Piece | None:
    for piece in pieces:
        if keyword in piece.name:
            if team is None or piece.team == team:
                return piece
    return None


def _nearest_active(pieces: list[Piece], team: str, x: float, y: float) -> Piece | None:
    candidates = [p for p in pieces if p.team == team and p.active and p.role != "GK"]
    if not candidates:
        return None
    return min(candidates, key=lambda p: (p.x - x) ** 2 + (p.y - y) ** 2)


def _move_team(pieces: list[Piece], team: str, dx: float, dy: float, roles: set[str] | None = None) -> None:
    for piece in pieces:
        if piece.team != team or not piece.active:
            continue
        if roles and piece.role not in roles:
            continue
        piece.x = _clamp(piece.x + dx)
        piece.y = _clamp(piece.y + dy)


def _substitute(
    pieces: list[Piece],
    out_keyword: str,
    team: str,
    sub_name: str | None = None,
    injured: bool = False,
) -> None:
    sub_name = sub_name or SUBSTITUTE_NAMES[team]
    outgoing = _find_piece(pieces, out_keyword, team)
    if not outgoing:
        return
    origin_x, origin_y = outgoing.x, outgoing.y
    outgoing.active = False
    outgoing.status = "injured" if injured else "subbed_out"
    outgoing.x = 96 if team == "kor" else 4
    outgoing.y = 50

    sub = _find_piece(pieces, sub_name, team)
    if sub:
        sub.active = True
        sub.status = "active"
        sub.x, sub.y = origin_x, origin_y
    else:
        pieces.append(
            Piece(f"sub_{team}", sub_name, team, outgoing.role, origin_x, origin_y, True, "active")
        )


def _infer_arrows(label: str, prev_ball: list[float], ball: list[float], pieces: list[Piece]) -> list[Arrow]:
    bx1, by1 = prev_ball
    bx2, by2 = ball
    if abs(bx2 - bx1) < 0.5 and abs(by2 - by1) < 0.5:
        return []

    kind = "pass"
    if any(k in label for k in ("골", "슛", "동점", "선제")):
        kind = "shot"
    elif any(k in label for k in ("크로스", "코너")):
        kind = "cross"

    team = "kor" if by2 < by1 else "mex"
    arrows: list[Arrow] = []
    passer = _nearest_active(pieces, team, bx1, by1)
    if passer and kind == "pass":
        arrows.append(Arrow(passer.x, passer.y, bx2, by2, "pass"))
    arrows.append(Arrow(bx1, by1, bx2, by2, kind))
    return arrows


def _build_steps(scenario: str) -> list[tuple[str, str]]:
    text = scenario.strip()
    steps: list[tuple[str, str]] = [("킥오프 — 중앙 패스 시작", "0'")]

    if "손흥민" in text and any(k in text for k in ("부상", "교체", "퇴장")):
        steps.append(("손흥민 부상/교체 — 측면으로 이탈, 이동경 투입", "10'"))
    if "멕시코" in text and any(k in text for k in ("선제", "먼저", "골", "득점")):
        steps.append(("멕시코 선제골 상황 — 페널티 박스 슛", "14'"))
    if any(k in text for k in ("한국", "대한민국")) and any(k in text for k in ("역습", "반격", "속공")):
        steps.append(("한국 역습 — 공격수 전진", "18'"))
    if any(k in text for k in ("프리킥", "프리 킥")):
        steps.append(("프리킥 — 벽 형성 및 세트피스", "22'"))
    if "코너" in text:
        steps.append(("코너킥 — 골문 앞 크로스", "27'"))
    if any(k in text for k in ("폭우", "비", "잔디", "날씨")):
        steps.append(("악천후 — 템포 저하, 후방 재조정", "32'"))
    if ("관중" in text or "응원" in text) or ("멕시코" in text and "홈" in text):
        steps.append(("멕시코 홈 어드밴티지 — 전진 압박", "38'"))
    if any(k in text for k in ("황인범", "이강인")) and any(k in text for k in ("골", "득점", "동점")):
        steps.append(("황인범/이강인 연계 — 동점 슛", "55'"))
    if "오현규" in text and "교체" in text:
        steps.append(("오현규 투입 — 박스 침투", "70'"))
    if any(k in text for k in ("연장", "추가", "90")):
        steps.append(("추가 시간 — 체력 저하, 장면 혼전", "90+2'"))

    if len(steps) == 1:
        steps.extend(
            [
                ("한국 좌측 build-up 패스", "6'"),
                ("멕시코 중원 차단", "12'"),
                ("한국 측면 크로스", "20'"),
                ("멕시코 롱볼 역습", "28'"),
                ("한국 페널티 박스 밀집", "36'"),
            ]
        )
    steps.append(("상황 종료 — 현재 포지션 유지", "FT"))
    return steps


def _apply_step(pieces: list[Piece], label: str, ball: list[float]) -> None:
    if "손흥민" in label and "교체" in label:
        _substitute(pieces, "손흥민", "kor", injured="부상" in label)
        ball[0], ball[1] = 45, 52
        _move_team(pieces, "kor", 0, -4, {"MF", "FW"})
        return

    if "멕시코 선제" in label:
        _move_team(pieces, "mex", 0, 12, {"MF", "FW"})
        _move_team(pieces, "kor", 0, 5, {"DF"})
        ball[0], ball[1] = 50, 72
        return

    if "한국 역습" in label:
        _move_team(pieces, "kor", 0, -14, {"MF", "FW"})
        _move_team(pieces, "mex", 0, 8, {"DF"})
        ball[0], ball[1] = 55, 42
        return

    if "프리킥" in label:
        ball[0], ball[1] = 62, 48
        for piece in pieces:
            if not piece.active:
                continue
            if piece.team == "kor" and piece.role != "GK":
                piece.x = _clamp(55 + (piece.x - 50) * 0.4)
                piece.y = _clamp(52 + (piece.y - 50) * 0.3)
            if piece.team == "mex" and piece.role in {"DF", "MF"}:
                piece.x = _clamp(ball[0] + (piece.x - ball[0]) * 0.2)
                piece.y = _clamp(ball[1] + 8)
        return

    if "코너" in label or "크로스" in label:
        ball[0], ball[1] = 78, 35
        team = "kor" if "한국" in label else "mex"
        _move_team(pieces, team, 5, -6 if team == "kor" else 6, {"FW"})
        return

    if "악천후" in label:
        _move_team(pieces, "kor", 0, 6, {"DF", "MF"})
        _move_team(pieces, "mex", 0, -6, {"DF", "MF"})
        ball[0], ball[1] = 50, 50
        return

    if "홈 어드밴티지" in label:
        _move_team(pieces, "mex", 0, 10, {"MF", "FW"})
        _move_team(pieces, "kor", 0, 4, {"MF"})
        ball[0], ball[1] = 48, 58
        return

    if "동점" in label or "슛" in label:
        _move_team(pieces, "kor", 0, -10, {"MF", "FW"})
        ball[0], ball[1] = 50, 28
        return

    if "오현규" in label:
        _substitute(pieces, "조규성", "kor", "오현규")
        _move_team(pieces, "kor", 0, -8, {"FW"})
        ball[0], ball[1] = 52, 32
        return

    if "추가 시간" in label:
        for piece in pieces:
            if piece.active and piece.role != "GK":
                piece.x = _clamp(piece.x + (2 if piece.team == "kor" else -2))
        ball[0], ball[1] = 50, 45
        return

    if "build-up" in label or "좌측" in label:
        _move_team(pieces, "kor", -6, -5, {"MF", "FW"})
        ball[0], ball[1] = 35, 52
        return

    if "차단" in label:
        _move_team(pieces, "mex", 0, 8, {"MF"})
        ball[0], ball[1] = 48, 55
        return

    if "롱볼" in label:
        _move_team(pieces, "mex", 4, 12, {"FW"})
        ball[0], ball[1] = 60, 65
        return

    if "밀집" in label:
        ball[0], ball[1] = 50, 30
        _move_team(pieces, "kor", 0, -6, {"MF", "FW"})
        _move_team(pieces, "mex", 0, 4, {"DF"})
        return

    ball[0] = _clamp(ball[0] + 4)
    ball[1] = _clamp(ball[1] - 3)


def generate_board_frames(
    scenario: str,
    kor_formation: str = "4-3-3",
    mex_formation: str = "4-3-3",
    custom_positions: dict[str, tuple[float, float]] | None = None,
) -> list[dict]:
    if not scenario.strip():
        scenario = "양팀이 중원에서 공을 나눠 갖는 공방전"

    pieces = build_initial_pieces(kor_formation, mex_formation, custom_positions)
    ball = [50.0, 50.0]
    frames: list[BoardFrame] = [
        BoardFrame("경기 시작 — 포메이션 배치", "0'", copy.deepcopy(pieces), ball[0], ball[1], [])
    ]

    for label, minute in _build_steps(scenario):
        prev_ball = ball.copy()
        _apply_step(pieces, label, ball)
        arrows = _infer_arrows(label, prev_ball, ball, pieces)
        frames.append(BoardFrame(label, minute, copy.deepcopy(pieces), ball[0], ball[1], arrows))

    return [frame.to_dict() for frame in frames]


def parse_custom_layout(raw: str | None) -> dict[str, tuple[float, float]] | None:
    if not raw or not raw.strip():
        return None
    data = json.loads(raw)
    return {pid: (float(pos["x"]), float(pos["y"])) for pid, pos in data.items()}
