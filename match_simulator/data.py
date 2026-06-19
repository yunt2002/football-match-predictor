"""2026 북중미 월드컵 기준 정적 데이터 (API 실패 시 fallback)."""

from __future__ import annotations

from match_simulator.models import HistoricalMatch, Player, TeamProfile, Variable, FootballDataBundle

DATA_VERSION = "2026-06-19"

KOR_FULL_SQUAD: list[Player] = [
    Player("kor_gk1", "조현우", "GK", "울산 HD", 82, 21),
    Player("kor_gk2", "김승규", "GK", "FC 도쿄", 78, 1),
    Player("kor_gk3", "송범근", "GK", "전북 현대", 76, 12),
    Player("kor_df1", "김민재", "DF", "바이에른 뮌헨", 91, 4),
    Player("kor_df2", "조유민", "DF", "샤르자", 80, 3),
    Player("kor_df3", "이한범", "DF", "FC 미트윌란", 79, 2),
    Player("kor_df4", "김태현", "DF", "가시마 앤틀러스", 77, 15),
    Player("kor_df5", "박진섭", "DF", "저장 FC", 75, 5),
    Player("kor_df6", "이기혁", "DF", "강원 FC", 76, 19),
    Player("kor_df7", "이태석", "DF", "아우스트리아 빈", 74, 14),
    Player("kor_df8", "설영우", "DF", "FK 파르티잔", 78, 22),
    Player("kor_df9", "옌스 카스트로프", "DF", "보루시아 M'gladbach", 77, 18),
    Player("kor_df10", "김문환", "DF", "대전 하나", 75, 13),
    Player("kor_mf1", "양현준", "MF", "셀틱", 79, 17),
    Player("kor_mf2", "백승호", "MF", "버밍엄 시티", 78, 8),
    Player("kor_mf3", "황인범", "MF", "페예노르트", 84, 6),
    Player("kor_mf4", "김진규", "MF", "전북 현대", 77, 20),
    Player("kor_mf5", "배준호", "MF", "스토크 시티", 76, 16),
    Player("kor_mf6", "엄지성", "MF", "스완지 시티", 74, 23),
    Player("kor_mf7", "황희찬", "MF", "울버햄튼", 85, 11),
    Player("kor_mf8", "이동경", "MF", "울산 HD", 78, 10),
    Player("kor_mf9", "이재성", "MF", "FSV 마인츠 05", 83, 7),
    Player("kor_mf10", "이강인", "MF", "파리 생제르맹", 88, 9),
    Player("kor_fw1", "오현규", "FW", "베식타ş JK", 80, 24),
    Player("kor_fw2", "손흥민", "FW", "LA FC", 92, 7),
    Player("kor_fw3", "조규성", "FW", "FC 미트윌란", 81, 25),
]

MEX_FULL_SQUAD: list[Player] = [
    Player("mex_gk1", "라울 랑헬", "GK", "과달라하라", 79, 1),
    Player("mex_gk2", "카를로스 아세베도", "GK", "산토스 라구나", 77, 12),
    Player("mex_gk3", "기예르모 오초아", "GK", "AEL 리마솔", 78, 13),
    Player("mex_df1", "호르헤 산체스", "DF", "PAOK", 78, 2),
    Player("mex_df2", "세사르 몬테스", "DF", "로코모티프 모스크바", 82, 3),
    Player("mex_df3", "요한 바스케스", "DF", "제노아", 80, 5),
    Player("mex_df4", "이스라엘 레예스", "DF", "아메리카", 79, 15),
    Player("mex_df5", "마테오 차베스", "DF", "AZ 알크마르", 76, 20),
    Player("mex_df6", "헤수스 갈라르도", "DF", "톨루카", 77, 23),
    Player("mex_mf1", "에드손 알바레스", "MF", "페네르바흐체", 86, 4),
    Player("mex_mf2", "에릭 리라", "MF", "크루스 아술", 78, 6),
    Player("mex_mf3", "루이스 로모", "MF", "과달라하라", 79, 7),
    Player("mex_mf4", "알바로 피달고", "MF", "레알 베티스", 81, 8),
    Player("mex_mf5", "오벨린 피네다", "MF", "AEK 아테네", 80, 17),
    Player("mex_mf6", "오베드 바르가스", "MF", "AT 마드리드", 77, 18),
    Player("mex_mf7", "길베르토 모라", "MF", "티후아나", 75, 19),
    Player("mex_mf8", "세사르 우에르타", "MF", "안데를레흐트", 79, 21),
    Player("mex_mf9", "루이스 차베스", "MF", "디나모 모스크바", 81, 24),
    Player("mex_mf10", "브라이언 구티에레스", "MF", "과달라하라", 78, 26),
    Player("mex_fw1", "라울 히메네스", "FW", "풀럼", 85, 9),
    Player("mex_fw2", "알렉시스 베가", "FW", "톨루카", 80, 10),
    Player("mex_fw3", "산티아고 히메네스", "FW", "AC 밀란", 86, 11),
    Player("mex_fw4", "아르만도 곤살레스", "FW", "과달라하라", 77, 14),
    Player("mex_fw5", "줄리안 퀴노네스", "FW", "알 카디시야", 82, 16),
    Player("mex_fw6", "기예르모 마르티네스", "FW", "PUMAS", 78, 22),
    Player("mex_fw7", "로베르토 알바라도", "FW", "과달라하라", 79, 25),
]

KOR_RECENT_MATCHES: list[HistoricalMatch] = [
    HistoricalMatch("k1", "2026.06.12", "2026 월드컵", "2:1", "W", "체코"),
    HistoricalMatch("k2", "2026.06.04", "친선 경기", "1:0", "W", "엘살바도르"),
    HistoricalMatch("k3", "2026.05.31", "친선 경기", "5:0", "W", "트리니다드 토바고"),
    HistoricalMatch("k4", "2026.03.31", "친선 경기", "0:1", "L", "오스트리아"),
    HistoricalMatch("k5", "2026.03.28", "친선 경기", "0:4", "L", "코트디부아르"),
    HistoricalMatch("k6", "2025.06.10", "월드컵 예선", "4:0", "W", "쿠웨이트"),
    HistoricalMatch("k7", "2025.06.05", "월드컵 예선", "2:0", "W", "이라크"),
    HistoricalMatch("k8", "2025.03.25", "월드컵 예선", "1:1", "D", "요르단"),
    HistoricalMatch("k9", "2025.03.20", "월드컵 예선", "1:1", "D", "오만"),
]

MEX_RECENT_MATCHES: list[HistoricalMatch] = [
    HistoricalMatch("x1", "2026.06.12", "2026 월드컵", "2:0", "W", "남아프리카공화국"),
    HistoricalMatch("x2", "2026.06.08", "친선 경기", "1:0", "W", "호주"),
    HistoricalMatch("x3", "2024.07.01", "코파 아메리카", "0:0", "D", "베네수엘라"),
    HistoricalMatch("x4", "2024.06.27", "코파 아메리카", "0:1", "L", "베네수엘라"),
    HistoricalMatch("x5", "2024.06.23", "코파 아메리카", "1:0", "W", "과테말라"),
    HistoricalMatch("x6", "2024.06.09", "친선 경기", "2:3", "L", "브라질"),
]

H2H_MATCHES: list[HistoricalMatch] = [
    HistoricalMatch("h1", "2018.06.23", "2018 월드컵", "1:2", "L", "멕시코"),
    HistoricalMatch("h2", "2010.05.16", "친선 경기", "1:0", "W", "멕시코"),
    HistoricalMatch("h3", "2002.01.27", "골드컵", "0:0 (PK)", "W", "멕시코"),
    HistoricalMatch("h4", "1998.06.13", "1998 월드컵", "1:3", "L", "멕시코"),
]

INITIAL_VARIABLES: list[Variable] = [
    Variable("v1", "FIFA 랭킹", "공식 랭킹에 따른 객관적 전력 지표", "장기 전력을 더 믿을까?", 75, 82, 15),
    Variable("v2", "최근 흐름", "최근 경기 승률 및 경기력 추세", "첫 경기 결과를 크게 볼까?", 82, 68, 15),
    Variable("v3", "공격력", "득점 생산력 및 슈팅 정확도", "득점 기대를 더 볼까?", 72, 70, 15),
    Variable("v4", "수비 안정성", "실점 억제력 및 조직력", "실점 위험을 더 볼까?", 62, 75, 15),
    Variable("v5", "핵심 선수", "주축 선수의 컨디션 및 의존도", "스타 선수 영향이 큰가?", 90, 52, 10),
    Variable("v6", "전술 상성", "상대 플레이 스타일 및 전술 대응력", "스타일 상성이 중요한가?", 65, 65, 10),
    Variable("v7", "홈/환경", "기후, 고도 및 관중 응원 영향", "개최국 분위기를 크게 볼까?", 55, 88, 10),
    Variable("v8", "역대 전적", "상대 팀과의 이전 매치 데이터", "과거 전적은 얼마나 반영할까?", 40, 60, 5),
    Variable("v9", "불확실성", "부상병동이나 정보 비대칭성 변수", "정보가 부족하면 신뢰도를 낮출까?", 50, 50, 5),
]

RESULT_LABELS = {"W": "승리", "D": "무승부", "L": "패배"}

POSITION_ORDER = {"GK": 0, "DF": 1, "MF": 2, "FW": 3}


def get_key_players(players: list[Player], count: int = 5) -> list[Player]:
    return sorted(players, key=lambda p: p.rating, reverse=True)[:count]


def sort_players_by_number(players: list[Player]) -> list[Player]:
    return sorted(players, key=lambda p: (p.number if p.number is not None else 999, p.name))


def sort_players_by_position(players: list[Player]) -> list[Player]:
    return sorted(players, key=lambda p: (POSITION_ORDER.get(p.position, 9), -p.rating, p.name))


KOR_PLAYERS = get_key_players(KOR_FULL_SQUAD)
MEX_PLAYERS = get_key_players(MEX_FULL_SQUAD)


def build_static_bundle() -> FootballDataBundle:
    return FootballDataBundle(
        korea=TeamProfile("KOR", "대한민국", "🇰🇷", KOR_FULL_SQUAD, KOR_RECENT_MATCHES, "static", DATA_VERSION),
        mexico=TeamProfile("MEX", "멕시코", "🇲🇽", MEX_FULL_SQUAD, MEX_RECENT_MATCHES, "static", DATA_VERSION),
        h2h_matches=H2H_MATCHES,
        updated_at=DATA_VERSION,
    )
