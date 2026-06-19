"""대한민국 vs 멕시코 승부 예측 시뮬레이터 — Streamlit 앱."""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

from match_simulator.board_html import render_tactics_board_html

from match_simulator.ai import generate_match_report, simulate_scenario
from match_simulator.checklist import build_pre_match_checklist, checklist_progress
from match_simulator.comparison import compare_with_actual
from match_simulator.charts import (
    ab_comparison_chart,
    contribution_bubble_chart,
    prob_donut_chart,
    prob_stacked_bar,
    score_heatmap,
    simulation_score_heatmap,
    stability_line_chart,
    time_distribution_chart,
    variable_radar_chart,
)
from match_simulator.data import (
    INITIAL_VARIABLES,
    RESULT_LABELS,
    build_static_bundle,
    get_key_players,
    sort_players_by_number,
)
from match_simulator.data_loader import load_football_data, merge_api_with_static
from match_simulator.insights import GLOSSARY, QUICK_SCENARIOS, build_sidebar_insights
from match_simulator.engine import (
    clone_variables,
    compute_half_time_predictions,
    compute_mc_confidence_intervals,
    compute_prediction,
    compute_score_matrix,
    compute_sensitivity,
    compute_stability_curve,
    normalize_weights,
    run_monte_carlo,
)
from match_simulator.player_whatif import apply_player_whatif, list_whatif_options
from match_simulator.report_export import markdown_to_html, report_to_pdf_bytes
from match_simulator.tactics_link import apply_tactics_to_variables
from match_simulator.tournament import format_next_match_banner, get_group_a_standings, project_standings_impact
from match_simulator.url_share import build_share_url, decode_share_payload, encode_share_payload
from match_simulator.models import FootballDataBundle, Player, Variable
from match_simulator.presets import PRESET_NAMES, get_preset
from match_simulator.serialization import export_config, import_config, variables_cache_key
from match_simulator.tactics_board import (
    FORMATION_OPTIONS,
    generate_board_frames,
    get_formation_layout_json,
    parse_custom_layout,
)

load_dotenv()

st.set_page_config(
    page_title="대한민국 vs 멕시코 승부 예측 시뮬레이터",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    .main-title { font-size: clamp(1.4rem, 4vw, 2.2rem); font-weight: 900; letter-spacing: -0.04em; }
    .sub-title { font-size: 0.75rem; letter-spacing: 0.2em; opacity: 0.5; text-transform: uppercase; }
    .prob-card { padding: clamp(0.6rem, 2vw, 1rem); border-radius: 6px; text-align: center; color: white; }
    .prob-kor { background: #E02020; }
    .prob-draw { background: #1A1A1A; }
    .prob-mex { background: #059669; }
    .prob-label { font-size: clamp(0.55rem, 1.5vw, 0.65rem); opacity: 0.85; text-transform: uppercase; }
    .prob-value { font-size: clamp(1.2rem, 4vw, 2rem); font-weight: 900; line-height: 1.1; }
    .team-btn-wrap { margin-bottom: 0.5rem; }
    .data-badge {
        display: inline-block; padding: 0.25rem 0.6rem; border-radius: 999px;
        background: #1A1A1A; color: #fff; font-size: 0.72rem; margin-right: 0.35rem;
    }
    .scroll-table { overflow-x: auto; -webkit-overflow-scrolling: touch; }

    @media (max-width: 992px) {
        div[data-testid="stHorizontalBlock"]:has(.layout-col) > div[data-testid="column"] {
            width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important;
        }
        section[data-testid="stSidebar"] { min-width: 280px !important; }
    }
    @media (max-width: 640px) {
        div[data-testid="stMetric"] { padding: 0.35rem !important; }
        .block-container { padding-left: 0.8rem !important; padding-right: 0.8rem !important; }
    }
</style>
"""

THEME_CSS = {
    "light": "",
    "dark": """
<style>
    .stApp { background-color: #0f172a !important; }
    [data-testid="stSidebar"] { background-color: #1e293b !important; }
    .main-title, .stMarkdown, label, p, span { color: #e2e8f0 !important; }
    .sub-title { color: #94a3b8 !important; }
    [data-testid="stMetricValue"] { color: #f8fafc !important; }
</style>
""",
    "presentation": """
<style>
    .main-title { font-size: 2.6rem !important; }
    .prob-value { font-size: 2.4rem !important; }
    .prob-card { padding: 1.2rem !important; }
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; }
    section.main > div { max-width: 1400px; }
</style>
""",
}

CHECKLIST_CSS = """
<style>
    .checklist-item { padding: 0.35rem 0; font-size: 0.85rem; }
    .check-done { color: #059669; font-weight: 700; }
    .check-todo { color: #94a3b8; }
</style>
"""
@st.cache_data(show_spinner=False)
def cached_monte_carlo(home_xg: float, away_xg: float, sim_count: int, cache_key: tuple, seed: int = 42):
    return run_monte_carlo(home_xg, away_xg, sim_count, seed=seed)


@st.cache_data(show_spinner=False)
def cached_stability(home_xg: float, away_xg: float, cache_key: tuple, seed: int = 42):
    return compute_stability_curve(home_xg, away_xg, seed=seed)


def init_session_state() -> None:
    defaults = {
        "variables": clone_variables(INITIAL_VARIABLES),
        "simulation": None,
        "sim_count": 1000,
        "ai_result": None,
        "report": None,
        "active_preset": "균형",
        "compare_a": "균형",
        "compare_b": "멕시코 우세",
        "scenario_text": "",
        "football_data": None,
        "selected_team": "both",
        "board_scenario": "",
        "board_frames": None,
        "kor_formation": "4-3-3",
        "mex_formation": "4-3-3",
        "board_custom_layout": "",
        "use_tactics_link": True,
        "tactics_adjusted_variables": None,
        "tactics_notes": [],
        "whatif_notes": [],
        "actual_home": 0,
        "actual_away": 0,
        "ui_theme": "light",
        "share_link_generated": False,
        "_url_applied": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if st.session_state.football_data is None:
        st.session_state.football_data = build_static_bundle()


def apply_query_params_once() -> None:
    if st.session_state._url_applied:
        return
    token = st.query_params.get("cfg")
    if not token:
        return
    try:
        data = decode_share_payload(token)
        st.session_state.variables = data["variables"]
        st.session_state.sim_count = data["sim_count"]
        if data.get("preset"):
            st.session_state.active_preset = data["preset"]
        st.session_state.kor_formation = data.get("kor_formation", "4-3-3")
        st.session_state.mex_formation = data.get("mex_formation", "4-3-3")
        st.session_state.simulation = None
        st.session_state._url_applied = True
        st.session_state.share_link_generated = True
    except Exception as exc:
        st.sidebar.error(f"URL 설정 불러오기 실패: {exc}")


def get_base_variables() -> list[Variable]:
    return st.session_state.variables


def refresh_tactics_variables(scenario: str = "", frames: list | None = None) -> None:
    if not st.session_state.use_tactics_link:
        st.session_state.tactics_adjusted_variables = None
        st.session_state.tactics_notes = []
        return
    adjusted, notes = apply_tactics_to_variables(
        get_base_variables(),
        kor_formation=st.session_state.kor_formation,
        mex_formation=st.session_state.mex_formation,
        scenario=scenario or st.session_state.board_scenario,
        board_frames=frames or st.session_state.board_frames,
    )
    st.session_state.tactics_adjusted_variables = adjusted
    st.session_state.tactics_notes = notes


def get_active_variables() -> list[Variable]:
    if st.session_state.use_tactics_link and st.session_state.tactics_adjusted_variables:
        return st.session_state.tactics_adjusted_variables
    return get_base_variables()


def weight_sum(variables: list[Variable] | None = None) -> int:
    src = variables if variables is not None else get_active_variables()
    return sum(v.weight for v in src)


def players_to_dataframe(players: list[Player]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "번호": p.number if p.number is not None else "-",
                "포지션": p.position,
                "선수": p.name,
                "소속": p.club,
                "레이팅": p.rating,
            }
            for p in sort_players_by_number(players)
        ]
    )


def render_prob_cards(home: float, draw: float, away: float, suffix: str = "", ci: dict | None = None) -> None:
    c1, c2, c3 = st.columns(3)
    for col, label, value, css, key in [
        (c1, f"🇰🇷 대한민국{suffix}", home, "prob-kor", "home"),
        (c2, f"🤝 무승부{suffix}", draw, "prob-draw", "draw"),
        (c3, f"🇲🇽 멕시코{suffix}", away, "prob-mex", "away"),
    ]:
        with col:
            ci_text = ""
            if ci and key in ci:
                ci_text = f'<div style="font-size:0.65rem;opacity:0.85">±{ci[key]["low"]:.1f}~{ci[key]["high"]:.1f}%</div>'
            st.markdown(
                f'<div class="prob-card {css}">'
                f'<div class="prob-label">{label}</div>'
                f'<div class="prob-value">{value:.1f}%</div>{ci_text}</div>',
                unsafe_allow_html=True,
            )


def render_header() -> None:
    c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
    with c1:
        st.markdown('<p class="sub-title">Computational Sports Modeling</p>', unsafe_allow_html=True)
        st.markdown('<p class="main-title">⚽ 승부 예측 시뮬레이터</p>', unsafe_allow_html=True)
        st.caption("KOR vs MEX · Matchup ID: KOR-MEX-2026-MC")
    with c2:
        total = weight_sum(get_base_variables())
        st.metric("가중치 합계", f"{total}%", delta="정상" if total == 100 else "조정 필요")
    with c3:
        st.metric("프리셋", st.session_state.active_preset)
    with c4:
        items = build_pre_match_checklist(
            weight_total=weight_sum(get_base_variables()),
            sim_count=st.session_state.sim_count,
            has_simulation=st.session_state.simulation is not None,
            has_ai_scenario=bool(st.session_state.ai_result),
            has_report=bool(st.session_state.report),
            has_board=bool(st.session_state.board_frames),
            tactics_linked=bool(st.session_state.tactics_adjusted_variables),
            has_url_or_export=st.session_state.share_link_generated,
        )
        done, total_items = checklist_progress(items)
        st.metric("경기 전 체크", f"{done}/{total_items}", delta="준비 완료" if done == total_items else "진행 중")


def render_checklist_panel() -> None:
    st.markdown(CHECKLIST_CSS, unsafe_allow_html=True)
    items = build_pre_match_checklist(
        weight_total=weight_sum(get_base_variables()),
        sim_count=st.session_state.sim_count,
        has_simulation=st.session_state.simulation is not None,
        has_ai_scenario=bool(st.session_state.ai_result),
        has_report=bool(st.session_state.report),
        has_board=bool(st.session_state.board_frames),
        tactics_linked=bool(st.session_state.tactics_adjusted_variables),
        has_url_or_export=st.session_state.share_link_generated,
    )
    done, total = checklist_progress(items)
    st.progress(done / total if total else 0, text=f"경기 준비 {done}/{total}")
    for item in items:
        icon = "✅" if item.done else "⬜"
        cls = "check-done" if item.done else "check-todo"
        st.markdown(f'<div class="checklist-item {cls}">{icon} {item.label} — <small>{item.hint}</small></div>', unsafe_allow_html=True)


def render_group_a_section(prediction) -> None:
    st.subheader("🏆 A조 순위 & 다음 경기")
    st.info(format_next_match_banner())
    standings = get_group_a_standings()
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "순위": i + 1,
                    "팀": r["team"],
                    "경기": r["played"],
                    "승": r["won"],
                    "무": r["drawn"],
                    "패": r["lost"],
                    "득실": r["gf"] - r["ga"],
                    "승점": r["pts"],
                }
                for i, r in enumerate(standings)
            ]
        ),
        hide_index=True,
        use_container_width=True,
    )
    proj = project_standings_impact(
        prediction.home_win_prob, prediction.draw_prob, prediction.away_win_prob
    )
    st.caption(f"현재 순위 — 🇰🇷 {proj.current_rank_kor}위 · 🇲🇽 {proj.current_rank_mex}위")
    st.markdown(f"- {proj.if_kor_win}")
    st.markdown(f"- {proj.if_draw}")
    st.markdown(f"- {proj.if_mex_win}")


def render_sidebar(prediction, football_data: FootballDataBundle) -> None:
    with st.sidebar:
        st.header("⚙️ 설정")
        insights = build_sidebar_insights(
            prediction,
            get_active_variables(),
            weight_sum(get_base_variables()),
            st.session_state.simulation is not None,
            football_data,
        )

        st.subheader("🏟️ 경기 정보")
        for key, value in insights["match_info"].items():
            st.caption(f"**{key}** · {value}")

        st.divider()
        st.subheader("📊 모델 스냅샷")
        st.metric("유력 결과", insights["favored"], delta=f"{insights['favored_prob']}%")
        c1, c2 = st.columns(2)
        c1.metric("유력 스코어", insights["likely_score"])
        c2.metric("xG", f"{prediction.home_xg} : {prediction.away_xg}")
        st.metric("모델 신뢰도", f"{insights['confidence']}%", delta=insights["confidence_label"])
        st.caption(f"편향 감지: {insights['bias_label']} (Δ {insights['bias_delta']})")
        st.caption(f"핵심 변수: **{insights['top_impact']}**")

        st.divider()
        st.subheader("⚔️ 팀 전력 비교")
        t1, t2 = st.columns(2)
        t1.metric("🇰🇷 평균 레이팅", insights["kor_rating"])
        t2.metric("🇲🇽 평균 레이팅", insights["mex_rating"])
        st.caption(f"최근 승률 — 🇰🇷 {insights['kor_form']}% · 🇲🇽 {insights['mex_form']}%")
        st.caption(f"상대 전적: {insights['h2h']}")
        st.caption(f"데이터: {insights['data_updated']}")

        if st.button("🔄 최신 데이터 불러오기", use_container_width=True):
            with st.spinner("선수·전적 데이터 갱신 중..."):
                loaded = load_football_data(use_api=True)
                st.session_state.football_data = merge_api_with_static(loaded)
            st.rerun()

        st.divider()
        st.subheader("프리셋")
        for name in PRESET_NAMES:
            if st.button(name, use_container_width=True, key=f"preset_{name}"):
                st.session_state.variables = get_preset(name)
                st.session_state.active_preset = name
                st.session_state.simulation = None
                st.rerun()

        if st.button("초기값 리셋", use_container_width=True):
            st.session_state.variables = clone_variables(INITIAL_VARIABLES)
            st.session_state.active_preset = "균형"
            st.session_state.simulation = None
            st.session_state.ai_result = None
            st.session_state.report = None
            st.rerun()

        st.divider()
        st.subheader("설정 내보내기 / 불러오기")
        export_data = export_config(
            st.session_state.variables,
            st.session_state.sim_count,
            st.session_state.active_preset,
        )
        st.download_button(
            "JSON 다운로드",
            export_data,
            file_name="match_simulator_config.json",
            mime="application/json",
            use_container_width=True,
        )
        uploaded = st.file_uploader("JSON 불러오기", type=["json"])
        if uploaded is not None:
            try:
                variables, sim_count, preset = import_config(uploaded.getvalue().decode("utf-8"))
                st.session_state.variables = variables
                st.session_state.sim_count = sim_count
                if preset:
                    st.session_state.active_preset = preset
                st.session_state.simulation = None
                st.success("설정을 불러왔습니다.")
                st.rerun()
            except Exception as exc:
                st.error(f"불러오기 실패: {exc}")

        st.divider()
        st.subheader("⚡ 빠른 AI 시나리오")
        for idx, text in enumerate(QUICK_SCENARIOS):
            if st.button(text, use_container_width=True, key=f"quick_scenario_{idx}"):
                st.session_state.scenario_text = text
                st.rerun()

        with st.expander("📖 용어 설명"):
            for term, desc in GLOSSARY.items():
                st.markdown(f"**{term}** — {desc}")

        st.divider()
        st.subheader("🎨 UI 모드")
        st.session_state.ui_theme = st.radio(
            "테마",
            ["light", "dark", "presentation"],
            index=["light", "dark", "presentation"].index(st.session_state.ui_theme),
            format_func=lambda x: {"light": "라이트", "dark": "다크", "presentation": "발표 모드"}[x],
            horizontal=True,
        )

        st.divider()
        st.subheader("🔗 설정 URL 공유")
        token = encode_share_payload(
            get_base_variables(),
            st.session_state.sim_count,
            st.session_state.active_preset,
            kor_formation=st.session_state.kor_formation,
            mex_formation=st.session_state.mex_formation,
        )
        share_url = build_share_url("http://localhost:8501", token)
        st.text_input("공유 링크", share_url, key="share_url_display")
        if st.button("링크 생성 완료 표시", use_container_width=True):
            st.session_state.share_link_generated = True
        st.caption("같은 설정을 `?cfg=...` 파라미터로 불러올 수 있습니다.")

        st.divider()
        st.subheader("경기 전 체크리스트")
        render_checklist_panel()

        st.divider()
        st.warning("※ 교육용 모의 결과이며 실제 경기 결과를 보장하지 않습니다.")
        if not st.session_state.simulation:
            st.info("💡 시뮬레이션을 실행하면 몬테카를로 결과가 우측에 추가됩니다.")
        st.caption("AI: `.env`에 `OPENAI_API_KEY` 설정 시 GPT(gpt-5-mini) 사용")


@st.fragment
def render_variable_controls() -> None:
    st.subheader("1. 전력 모델 파라미터")
    if st.button("가중치 자동 정규화 (100%)", key="normalize_weights"):
        st.session_state.variables = normalize_weights(st.session_state.variables)
        st.rerun()

    total = weight_sum()
    if total != 100:
        st.warning(f"가중치 합계 {total}% — 100%로 맞추는 것을 권장합니다.")

    updated: list[Variable] = []
    for var in st.session_state.variables:
        with st.expander(f"{var.name} (가중치 {var.weight}%)", expanded=False):
            st.caption(f"💬 {var.question}")
            st.info(var.description)
            weight = st.slider("가중치 (%)", 0, 100, var.weight, key=f"w_{var.id}")
            c1, c2 = st.columns(2)
            with c1:
                home = st.slider("🇰🇷 대한민국", 0, 100, var.home_score, key=f"h_{var.id}")
            with c2:
                away = st.slider("🇲🇽 멕시코", 0, 100, var.away_score, key=f"a_{var.id}")
            updated.append(
                Variable(var.id, var.name, var.description, var.question, home, away, weight)
            )

    st.session_state.variables = updated
    st.session_state.active_preset = "사용자 정의"


def render_squad_and_history(football_data: FootballDataBundle) -> None:
    st.subheader("📋 전력 & 전적")
    st.markdown(
        f'<span class="data-badge">업데이트 {football_data.updated_at}</span>'
        f'<span class="data-badge">{football_data.korea.source}</span>',
        unsafe_allow_html=True,
    )

    team_choice = st.segmented_control(
        "팀 선택 (전체 명단 보기)",
        options=["both", "kor", "mex"],
        default=st.session_state.selected_team,
        format_func=lambda x: {"both": "양팀 요약", "kor": "🇰🇷 대한민국", "mex": "🇲🇽 멕시코"}[x],
    )
    st.session_state.selected_team = team_choice

    if team_choice == "both":
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**🇰🇷 대한민국 — 주요 5인**")
            st.dataframe(
                players_to_dataframe(get_key_players(football_data.korea.players)),
                hide_index=True,
                use_container_width=True,
            )
            if st.button("🇰🇷 전체 26인 명단 보기", key="show_kor_full", use_container_width=True):
                st.session_state.selected_team = "kor"
                st.rerun()
        with c2:
            st.markdown("**🇲🇽 멕시코 — 주요 5인**")
            st.dataframe(
                players_to_dataframe(get_key_players(football_data.mexico.players)),
                hide_index=True,
                use_container_width=True,
            )
            if st.button("🇲🇽 전체 26인 명단 보기", key="show_mex_full", use_container_width=True):
                st.session_state.selected_team = "mex"
                st.rerun()
    elif team_choice == "kor":
        st.markdown(f"### 🇰🇷 대한민국 — 2026 월드컵 최종 26인")
        st.dataframe(
            players_to_dataframe(football_data.korea.players),
            hide_index=True,
            use_container_width=True,
            height=420,
        )
    else:
        st.markdown(f"### 🇲🇽 멕시코 — 2026 월드컵 최종 26인")
        st.dataframe(
            players_to_dataframe(football_data.mexico.players),
            hide_index=True,
            use_container_width=True,
            height=420,
        )

    st.divider()
    st.markdown("**📜 최근 경기 전적**")
    history_view = st.radio(
        "전적 유형",
        ["H2H (상대 전적)", "대한민국 최근", "멕시코 최근"],
        horizontal=True,
        key="history_view",
    )
    if history_view.startswith("H2H"):
        matches = football_data.h2h_matches
        result_note = "한국 기준"
    elif "대한민국" in history_view:
        matches = football_data.korea.recent_matches
        result_note = "대한민국 기준"
    else:
        matches = football_data.mexico.recent_matches
        result_note = "멕시코 기준"

    history_df = pd.DataFrame(
        [
            {
                "날짜": m.date,
                "상대": m.opponent or "-",
                "대회": m.competition,
                "스코어": m.score,
                "결과": RESULT_LABELS.get(m.result, m.result),
            }
            for m in matches
        ]
    )
    st.caption(f"※ {result_note}")
    st.dataframe(history_df, hide_index=True, use_container_width=True)

    st.divider()
    st.markdown("**🎯 선수 What-if**")
    st.caption("선수 부재/부스트 시나리오를 변수에 반영합니다.")
    wc1, wc2, wc3 = st.columns([1, 1, 1])
    with wc1:
        whatif_team = st.selectbox("팀", ["kor", "mex"], format_func=lambda x: "🇰🇷 한국" if x == "kor" else "🇲🇽 멕시코", key="whatif_team")
    squad = football_data.korea.players if whatif_team == "kor" else football_data.mexico.players
    options = list_whatif_options(squad) or [p.name for p in get_key_players(squad, 8)]
    with wc2:
        whatif_player = st.selectbox("선수", options, key="whatif_player")
    with wc3:
        whatif_mode = st.selectbox("시나리오", ["out", "boost"], format_func=lambda x: "부재/부상" if x == "out" else "풀타임/부스트", key="whatif_mode")
    if st.button("What-if 모델에 적용", key="apply_whatif"):
        adjusted, notes = apply_player_whatif(get_base_variables(), whatif_player, whatif_team, whatif_mode)
        st.session_state.variables = adjusted
        st.session_state.whatif_notes = notes
        st.session_state.simulation = None
        refresh_tactics_variables()
        st.success("적용됨: " + "; ".join(notes))
        st.rerun()
    if st.session_state.whatif_notes:
        for note in st.session_state.whatif_notes:
            st.caption(f"· {note}")


def render_simulation_controls(prediction) -> None:
    st.subheader("2. 몬테카를로 시뮬레이션")
    counts = [10, 100, 1000, 10000]
    idx = counts.index(st.session_state.sim_count) if st.session_state.sim_count in counts else 2
    st.session_state.sim_count = st.selectbox(
        "시뮬레이션 횟수",
        counts,
        index=idx,
    )

    if st.button("시뮬레이션 실행", type="primary", disabled=weight_sum(get_base_variables()) == 0):
        key = variables_cache_key(get_active_variables(), st.session_state.sim_count)
        with st.spinner(f"{st.session_state.sim_count:,}회 실행 중..."):
            st.session_state.simulation = cached_monte_carlo(
                prediction.home_xg,
                prediction.away_xg,
                st.session_state.sim_count,
                key,
            )
        st.success("완료!")


def render_tactics_board_section() -> None:
    st.subheader("5. 🎮 상황판 모의 시뮬레이션")
    st.caption(
        "포메이션 선택 · 드래그 배치 · 패스/슛 화살표 · 교체·부상 표시를 지원하는 워게임형 상황판입니다."
    )

    presets = [
        "10분 만에 손흥민 부상으로 교체된다면?",
        "멕시코가 전반 선제골을 넣는다면?",
        "후반 한국 역습과 황인범 동점골 상황",
        "멕시코 홈 관중 응원 + 프리킥",
        "폭우로 템포가 느려지는 경기",
    ]
    preset_cols = st.columns(len(presets))
    for idx, preset in enumerate(presets):
        if preset_cols[idx].button(f"예시 {idx + 1}", key=f"board_preset_{idx}"):
            st.session_state.board_scenario = preset
            st.rerun()

    form_col, mex_col = st.columns(2)
    with form_col:
        kor_formation = st.selectbox(
            "🇰🇷 한국 포메이션",
            FORMATION_OPTIONS,
            index=FORMATION_OPTIONS.index(st.session_state.kor_formation),
            key="kor_formation",
        )
    with mex_col:
        mex_formation = st.selectbox(
            "🇲🇽 멕시코 포메이션",
            FORMATION_OPTIONS,
            index=FORMATION_OPTIONS.index(st.session_state.mex_formation),
            key="mex_formation",
        )

    st.session_state.use_tactics_link = st.checkbox(
        "상황판·포메이션을 승률 모델에 연동",
        value=st.session_state.use_tactics_link,
        help="포메이션, 부상/교체 시나리오를 v3·v4·v5 등 변수에 반영합니다.",
    )
    if st.session_state.tactics_notes:
        st.caption("연동 보정: " + " · ".join(st.session_state.tactics_notes))

    with st.expander("✋ 드래그 배치 편집", expanded=False):
        st.caption("선수를 드래그한 뒤 **배치 JSON** 버튼으로 복사해 아래 입력란에 붙여넣으세요.")
        layout_pieces = get_formation_layout_json(kor_formation, mex_formation)
        editor_html = render_tactics_board_html(
            None, "포메이션 초기 배치", edit_mode=True, initial_pieces=layout_pieces
        )
        components.html(editor_html, height=720, scrolling=True)
        st.text_area(
            "커스텀 배치 JSON (선택)",
            placeholder='{"k0": {"x": 50, "y": 90}, ...}',
            height=100,
            key="board_custom_layout",
        )

    board_scenario = st.text_area(
        "부여할 상황",
        placeholder="예: 10분 손흥민 부상 교체 후 한국이 역습한다면?",
        height=90,
        key="board_scenario",
    )

    if st.button("▶ 상황판 시뮬레이션 시작", type="primary", disabled=not board_scenario.strip()):
        custom_positions = None
        try:
            custom_positions = parse_custom_layout(st.session_state.board_custom_layout)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            st.error("커스텀 배치 JSON 형식이 올바르지 않습니다.")
            return
        with st.spinner("상황 분석 및 전술 보드 생성 중..."):
            st.session_state.board_frames = generate_board_frames(
                board_scenario,
                kor_formation=kor_formation,
                mex_formation=mex_formation,
                custom_positions=custom_positions,
            )
            refresh_tactics_variables(board_scenario, st.session_state.board_frames)
            st.session_state.simulation = None

    if st.session_state.board_frames:
        html = render_tactics_board_html(st.session_state.board_frames, board_scenario)
        components.html(html, height=780, scrolling=True)

        with st.expander("📋 장면 타임라인"):
            for idx, frame in enumerate(st.session_state.board_frames, start=1):
                arrow_note = ""
                if frame.get("arrows"):
                    kinds = {a["kind"] for a in frame["arrows"]}
                    arrow_note = f" ({', '.join(sorted(kinds))} 화살표)"
                st.markdown(f"{idx}. **{frame['minute']}** — {frame['label']}{arrow_note}")


def render_ai_sections() -> None:
    st.subheader("3. AI 시나리오")
    scenario = st.text_area(
        "특정 상황",
        placeholder="예: 10분 만에 손흥민 부상 교체, 폭우로 잔디 상태 악화",
        height=100,
        key="scenario_text",
    )
    auto_board = st.checkbox("AI 분석 후 상황판 자동 생성", value=True, key="ai_auto_board")
    if st.button("AI 시나리오 가동", disabled=not scenario.strip()):
        with st.spinner("분석 중..."):
            active = get_active_variables()
            st.session_state.ai_result = simulate_scenario(scenario, active)
            if auto_board:
                st.session_state.board_scenario = scenario
                custom_positions = None
                try:
                    custom_positions = parse_custom_layout(st.session_state.board_custom_layout)
                except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                    custom_positions = None
                st.session_state.board_frames = generate_board_frames(
                    scenario,
                    kor_formation=st.session_state.kor_formation,
                    mex_formation=st.session_state.mex_formation,
                    custom_positions=custom_positions,
                )
                refresh_tactics_variables(scenario, st.session_state.board_frames)
        st.rerun()
    if st.session_state.ai_result:
        st.markdown(st.session_state.ai_result)
        if st.session_state.board_frames and auto_board:
            st.success("상황판 타임라인이 함께 생성되었습니다. 아래 5번 섹션에서 확인하세요.")

    st.subheader("4. 매치 리포트")
    if st.button("리포트 생성"):
        with st.spinner("리포트 작성 중..."):
            st.session_state.report = generate_match_report(
                get_active_variables(),
                compute_prediction(get_active_variables()),
                st.session_state.simulation,
            )
    if st.session_state.report:
        st.markdown(st.session_state.report)
        col_md, col_html, col_pdf = st.columns(3)
        with col_md:
            st.download_button(
                "MD 다운로드",
                st.session_state.report,
                file_name="match_report.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with col_html:
            html_report = markdown_to_html(st.session_state.report)
            st.download_button(
                "HTML 다운로드",
                html_report,
                file_name="match_report.html",
                mime="text/html",
                use_container_width=True,
            )
        with col_pdf:
            try:
                pdf_bytes = report_to_pdf_bytes(st.session_state.report)
                st.download_button(
                    "PDF 다운로드",
                    pdf_bytes,
                    file_name="match_report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as exc:
                st.caption(f"PDF: {exc}")


def render_output_panel(prediction) -> None:
    st.subheader("📊 실시간 예측")
    if st.session_state.use_tactics_link and st.session_state.tactics_notes:
        st.info("🔗 상황판 연동 활성: " + " · ".join(st.session_state.tactics_notes[:3]))

    st.markdown("**이론적 승률 (xG 모델)**")
    render_prob_cards(
        prediction.home_win_prob,
        prediction.draw_prob,
        prediction.away_win_prob,
    )
    st.plotly_chart(
        prob_stacked_bar(
            prediction.home_win_prob,
            prediction.draw_prob,
            prediction.away_win_prob,
            "이론적 승률 (누적)",
        ),
        use_container_width=True,
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("🇰🇷 xG", prediction.home_xg)
    c2.metric("🇲🇽 xG", prediction.away_xg)
    c3.metric("전력 점수", f"{prediction.home_team_score} vs {prediction.away_team_score}")

    st.markdown("**⏱️ 전반 / 후반 분리 예측**")
    half = compute_half_time_predictions(get_active_variables())
    hcols = st.columns(3)
    for col, label, data in zip(
        hcols,
        ["전반 (45')", "후반 (45')", "풀타임"],
        [half["first_half"], half["second_half"], half["full_time"]],
        strict=True,
    ):
        with col:
            st.markdown(f"**{label}**")
            st.caption(f"xG {data['home_xg']} : {data['away_xg']}")
            st.progress(data["home_win"] / 100, text=f"🇰🇷 {data['home_win']}%")
            st.progress(data["draw"] / 100, text=f"무 {data['draw']}%")
            st.progress(data["away_win"] / 100, text=f"🇲🇽 {data['away_win']}%")

    st.markdown("**유력 스코어**")
    for s in prediction.top_scenarios:
        st.markdown(f"- {s.label}: **{s.home}:{s.away}** ({s.probability}%)")

    matrix = compute_score_matrix(prediction.home_xg, prediction.away_xg)
    st.plotly_chart(score_heatmap(matrix), use_container_width=True)

    st.markdown("**핵심 변수 TOP 3**")
    for i, impact in enumerate(prediction.impact_variables, 1):
        st.markdown(f"{i}. **{impact.name}** — 영향도 {impact.impact * 10:.1f}")
        st.caption(impact.description)

    st.plotly_chart(variable_radar_chart(get_active_variables()), use_container_width=True)
    st.plotly_chart(contribution_bubble_chart(get_active_variables()), use_container_width=True)

    sim = st.session_state.simulation
    if sim:
        st.divider()
        st.subheader("🎲 시뮬레이션 결과")
        home_p = sim.home_wins / sim.total * 100
        draw_p = sim.draws / sim.total * 100
        away_p = sim.away_wins / sim.total * 100
        ci = compute_mc_confidence_intervals(sim)

        st.markdown("**몬테카를로 승률 (95% 신뢰 구간)**")
        render_prob_cards(home_p, draw_p, away_p, suffix=" (MC)", ci=ci)
        st.caption(
            f"한국 {ci['home']['low']:.1f}~{ci['home']['high']:.1f}% · "
            f"무 {ci['draw']['low']:.1f}~{ci['draw']['high']:.1f}% · "
            f"멕시코 {ci['away']['low']:.1f}~{ci['away']['high']:.1f}%"
        )
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(prob_donut_chart(home_p, draw_p, away_p, "몬테카를로 승률"), use_container_width=True)
        with col2:
            st.plotly_chart(simulation_score_heatmap(sim), use_container_width=True)

        st.plotly_chart(time_distribution_chart(sim), use_container_width=True)

        top_scores = sorted(sim.score_histogram.items(), key=lambda x: x[1], reverse=True)[:10]
        st.dataframe(
            pd.DataFrame(
                [{"스코어": k.replace("-", ":"), "횟수": v, "확률 (%)": round(v / sim.total * 100, 1)} for k, v in top_scores]
            ),
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("왼쪽에서 시뮬레이션을 실행하면 몬테카를로 결과가 표시됩니다.")

    st.divider()
    st.subheader("📈 예측 vs 실제")
    st.caption("경기 후 실제 스코어를 입력해 모델 적중률을 검증하세요.")
    ac1, ac2 = st.columns(2)
    with ac1:
        actual_home = st.number_input("🇰🇷 한국 득점", 0, 15, st.session_state.actual_home, key="actual_home_input")
    with ac2:
        actual_away = st.number_input("🇲🇽 멕시코 득점", 0, 15, st.session_state.actual_away, key="actual_away_input")
    st.session_state.actual_home = actual_home
    st.session_state.actual_away = actual_away
    if st.button("실제 결과 비교", key="compare_actual"):
        cmp = compare_with_actual(prediction, sim, actual_home, actual_away)
        o1, o2, o3 = st.columns(3)
        o1.metric("승부 예측", "적중 ✅" if cmp.outcome_correct else "빗나감 ❌")
        o2.metric("스코어 예측", "적중 ✅" if cmp.top_score_hit else "빗나감 ❌")
        o3.metric("유력 스코어", cmp.predicted_top_score)
        st.markdown(cmp.narrative)
        st.caption(cmp.mc_summary)


def render_analysis_sections(prediction) -> None:
    st.subheader("🔬 고급 분석")

    with st.expander("민감도 분석 (가중치 +10%p)", expanded=False):
        sensitivity = compute_sensitivity(get_active_variables())
        st.dataframe(pd.DataFrame(sensitivity), hide_index=True, use_container_width=True)

    with st.expander("A/B 프리셋 비교", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            idx_a = PRESET_NAMES.index(st.session_state.compare_a) if st.session_state.compare_a in PRESET_NAMES else 0
            preset_a = st.selectbox("프리셋 A", PRESET_NAMES, index=idx_a, key="ab_a")
        with c2:
            idx_b = PRESET_NAMES.index(st.session_state.compare_b) if st.session_state.compare_b in PRESET_NAMES else 1
            preset_b = st.selectbox("프리셋 B", PRESET_NAMES, index=idx_b, key="ab_b")
        st.session_state.compare_a = preset_a
        st.session_state.compare_b = preset_b

        pred_a = compute_prediction(get_preset(preset_a))
        pred_b = compute_prediction(get_preset(preset_b))
        st.plotly_chart(ab_comparison_chart(pred_a, pred_b, preset_a, preset_b), use_container_width=True)

        compare_df = pd.DataFrame(
            {
                "항목": ["한국 승 (%)", "무승부 (%)", "멕시코 승 (%)", "한국 xG", "멕시코 xG"],
                preset_a: [
                    pred_a.home_win_prob,
                    pred_a.draw_prob,
                    pred_a.away_win_prob,
                    pred_a.home_xg,
                    pred_a.away_xg,
                ],
                preset_b: [
                    pred_b.home_win_prob,
                    pred_b.draw_prob,
                    pred_b.away_win_prob,
                    pred_b.home_xg,
                    pred_b.away_xg,
                ],
            }
        )
        st.dataframe(compare_df, hide_index=True, use_container_width=True)

    with st.expander("시뮬레이션 안정성 곡선", expanded=False):
        key = variables_cache_key(st.session_state.variables, 10000)
        curve = cached_stability(prediction.home_xg, prediction.away_xg, key)
        st.plotly_chart(stability_line_chart(curve), use_container_width=True)
        st.caption("횟수를 늘리면 **정확해지기보다 결과가 안정적으로 수렴**하는 경향을 확인할 수 있습니다.")
        st.dataframe(pd.DataFrame(curve), hide_index=True, use_container_width=True)

    with st.expander("변수별 기여도 테이블", expanded=False):
        total = weight_sum() or 1
        rows = [
            {
                "변수": v.name,
                "가중치 (%)": v.weight,
                "격차": abs(v.home_score - v.away_score),
                "기여도": round(abs(v.home_score - v.away_score) * (v.weight / total), 2),
            }
            for v in get_active_variables()
        ]
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)


def main() -> None:
    init_session_state()
    apply_query_params_once()
    refresh_tactics_variables(st.session_state.board_scenario, st.session_state.board_frames)
    theme = st.session_state.ui_theme
    st.markdown(CUSTOM_CSS + THEME_CSS.get(theme, ""), unsafe_allow_html=True)

    active_vars = get_active_variables()
    prediction = compute_prediction(active_vars)
    football_data: FootballDataBundle = st.session_state.football_data
    render_header()
    render_sidebar(prediction, football_data)

    st.markdown('<div class="layout-col">', unsafe_allow_html=True)
    col_input, col_output = st.columns([1.4, 1], gap="large")

    with col_input:
        render_group_a_section(prediction)
        st.divider()
        render_squad_and_history(football_data)
        st.divider()
        render_variable_controls()
        st.divider()
        render_simulation_controls(prediction)
        st.divider()
        render_ai_sections()
        st.divider()
        render_tactics_board_section()
        st.divider()
        render_analysis_sections(prediction)

    with col_output:
        render_output_panel(prediction)

    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.caption("© 2026 Sports Data Transparency Initiative · Predict Engine V5.2.0 (Streamlit)")


if __name__ == "__main__":
    main()
