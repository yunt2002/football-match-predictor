from match_simulator.tactics_board import (
    FORMATION_OPTIONS,
    build_initial_pieces,
    generate_board_frames,
    parse_custom_layout,
)


def test_generate_frames_default():
    frames = generate_board_frames("")
    assert len(frames) >= 5
    assert "pieces" in frames[0]
    assert len(frames[0]["pieces"]) == 22
    assert "arrows" in frames[1]


def test_injury_scenario_includes_substitution_step():
    frames = generate_board_frames("10분 만에 손흥민 부상으로 교체된다면?")
    labels = " ".join(f["label"] for f in frames)
    assert "손흥민" in labels
    injured = [p for frame in frames for p in frame["pieces"] if p.get("status") == "injured"]
    assert injured


def test_formation_changes_lineup():
    frames_433 = generate_board_frames("중원 패스", kor_formation="4-3-3")
    frames_523 = generate_board_frames("중원 패스", kor_formation="5-2-3")
    kor_433 = [p["name"] for p in frames_433[0]["pieces"] if p["team"] == "kor"]
    kor_523 = [p["name"] for p in frames_523[0]["pieces"] if p["team"] == "kor"]
    assert kor_433 != kor_523
    assert len(kor_433) == 11


def test_custom_layout_applied():
    custom = {"k10": (40.0, 35.0)}
    pieces = build_initial_pieces(custom_positions=custom)
    striker = next(p for p in pieces if p.id == "k10")
    assert striker.x == 40.0
    assert striker.y == 35.0


def test_parse_custom_layout():
    raw = '{"k0": {"x": 50, "y": 90}, "m0": {"x": 50, "y": 10}}'
    parsed = parse_custom_layout(raw)
    assert parsed["k0"] == (50.0, 90.0)


def test_formation_options():
    assert "4-3-3" in FORMATION_OPTIONS
    assert len(FORMATION_OPTIONS) == 3
