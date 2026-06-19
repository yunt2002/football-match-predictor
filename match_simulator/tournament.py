"""A조 순위·다음 경기 맥락."""

from __future__ import annotations

from dataclasses import dataclass

GROUP_A_BASE = [
    {"team": "멕시코", "code": "MEX", "played": 1, "won": 1, "drawn": 0, "lost": 0, "gf": 2, "ga": 0, "pts": 3},
    {"team": "대한민국", "code": "KOR", "played": 1, "won": 1, "drawn": 0, "lost": 0, "gf": 2, "ga": 1, "pts": 3},
    {"team": "남아프리카공화국", "code": "RSA", "played": 1, "won": 0, "drawn": 0, "lost": 1, "gf": 0, "ga": 2, "pts": 0},
    {"team": "체코", "code": "CZE", "played": 0, "won": 0, "drawn": 0, "lost": 0, "gf": 0, "ga": 0, "pts": 0},
]

NEXT_MATCH = {
    "date": "2026-06-19",
    "kickoff": "04:00 (KST)",
    "venue": "멕시코시티 · Estadio Azteca",
    "round": "A조 2차전",
    "home": "멕시코",
    "away": "대한민국",
}


@dataclass
class StandingsProjection:
    if_kor_win: str
    if_draw: str
    if_mex_win: str
    current_rank_kor: int
    current_rank_mex: int


def _sort_standings(rows: list[dict]) -> list[dict]:
    return sorted(rows, key=lambda r: (-r["pts"], -(r["gf"] - r["ga"]), -r["gf"], r["team"]))


def get_group_a_standings() -> list[dict]:
    rows = [dict(r) for r in GROUP_A_BASE]
    return _sort_standings(rows)


def project_standings_impact(home_win_prob: float, draw_prob: float, away_win_prob: float) -> StandingsProjection:
    standings = get_group_a_standings()
    kor_rank = next(i + 1 for i, r in enumerate(standings) if r["code"] == "KOR")
    mex_rank = next(i + 1 for i, r in enumerate(standings) if r["code"] == "MEX")

    return StandingsProjection(
        if_kor_win=f"한국 승 시 A조 {1 if kor_rank <= 2 else 2}위권 유지·결승 토너먼트 진출 유리 (예상 확률 {home_win_prob:.0f}%)",
        if_draw=f"무승부 시 양팀 {kor_rank}~{kor_rank+1}위 경쟁 지속 (예상 확률 {draw_prob:.0f}%)",
        if_mex_win=f"멕시코 승 시 한국 {kor_rank+1}위 이하 가능성·마지막 경기 부담 (예상 확률 {away_win_prob:.0f}%)",
        current_rank_kor=kor_rank,
        current_rank_mex=mex_rank,
    )


def format_next_match_banner() -> str:
    m = NEXT_MATCH
    return f"**{m['round']}** · {m['date']} {m['kickoff']} · {m['venue']} · 🇲🇽 {m['home']} vs 🇰🇷 {m['away']}"
