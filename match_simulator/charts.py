from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from match_simulator.models import PredictionResult, SimulationResult, Variable

KOR_COLOR = "#E02020"
DRAW_COLOR = "#6B7280"
MEX_COLOR = "#059669"


def prob_donut_chart(
    home_pct: float,
    draw_pct: float,
    away_pct: float,
    title: str,
) -> go.Figure:
    fig = go.Figure(
        data=[
            go.Pie(
                labels=["대한민국", "무승부", "멕시코"],
                values=[home_pct, draw_pct, away_pct],
                hole=0.45,
                marker={"colors": [KOR_COLOR, DRAW_COLOR, MEX_COLOR]},
                textinfo="label+percent",
                textfont={"size": 12},
            )
        ]
    )
    fig.update_layout(title=title, height=320, margin=dict(t=50, b=20, l=20, r=20))
    return fig


def prob_stacked_bar(home_pct: float, draw_pct: float, away_pct: float, title: str) -> go.Figure:
    fig = go.Figure(
        data=[
            go.Bar(
                y=["승률"],
                x=[home_pct],
                name="대한민국",
                orientation="h",
                marker_color=KOR_COLOR,
            ),
            go.Bar(
                y=["승률"],
                x=[draw_pct],
                name="무승부",
                orientation="h",
                marker_color=DRAW_COLOR,
            ),
            go.Bar(
                y=["승률"],
                x=[away_pct],
                name="멕시코",
                orientation="h",
                marker_color=MEX_COLOR,
            ),
        ]
    )
    fig.update_layout(
        barmode="stack",
        title=title,
        height=180,
        xaxis={"range": [0, 100], "title": "확률 (%)"},
        margin=dict(t=50, b=20),
    )
    return fig


def score_heatmap(matrix: np.ndarray) -> go.Figure:
    labels = [[f"{h}:{a}<br>{matrix[h, a] * 100:.1f}%" for a in range(matrix.shape[1])] for h in range(matrix.shape[0])]
    fig = go.Figure(
        data=go.Heatmap(
            z=matrix * 100,
            x=[str(i) for i in range(matrix.shape[1])],
            y=[str(i) for i in range(matrix.shape[0])],
            colorscale=[[0, "#f9f9f7"], [0.5, "#E02020"], [1, "#1A1A1A"]],
            text=labels,
            texttemplate="%{text}",
            hovertemplate="한국 %{y} : 멕시코 %{x}<br>확률 %{z:.1f}%<extra></extra>",
        )
    )
    fig.update_layout(
        title="스코어 확률 히트맵 (Poisson)",
        xaxis_title="멕시코 득점",
        yaxis_title="대한민국 득점",
        height=380,
        margin=dict(t=50, b=40),
    )
    return fig


def simulation_score_heatmap(simulation: SimulationResult, max_goals: int = 4) -> go.Figure:
    total = simulation.total
    matrix = np.zeros((max_goals + 1, max_goals + 1))
    for key, count in simulation.score_histogram.items():
        h, a = map(int, key.split("-"))
        if h <= max_goals and a <= max_goals:
            matrix[h, a] = count / total * 100

    fig = go.Figure(
        data=go.Heatmap(
            z=matrix,
            x=[str(i) for i in range(max_goals + 1)],
            y=[str(i) for i in range(max_goals + 1)],
            colorscale=[[0, "#f9f9f7"], [0.5, "#059669"], [1, "#1A1A1A"]],
            text=[[f"{matrix[h, a]:.1f}%" if matrix[h, a] else "" for a in range(max_goals + 1)] for h in range(max_goals + 1)],
            texttemplate="%{text}",
            hovertemplate="한국 %{y} : 멕시코 %{x}<br>빈도 %{z:.1f}%<extra></extra>",
        )
    )
    fig.update_layout(
        title="몬테카를로 스코어 분포 히트맵",
        xaxis_title="멕시코 득점",
        yaxis_title="대한민국 득점",
        height=380,
        margin=dict(t=50, b=40),
    )
    return fig


def time_distribution_chart(simulation: SimulationResult) -> go.Figure:
    total = simulation.total
    buckets = sorted(simulation.time_distribution["home"].keys(), key=lambda x: int(x.split("-")[0]))
    home_rates = [simulation.time_distribution["home"][b] / total for b in buckets]
    away_rates = [simulation.time_distribution["away"][b] / total for b in buckets]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="🇰🇷 대한민국", x=buckets, y=home_rates, marker_color=KOR_COLOR))
    fig.add_trace(go.Bar(name="🇲🇽 멕시코", x=buckets, y=away_rates, marker_color=MEX_COLOR))
    fig.update_layout(
        barmode="group",
        title="시간대별 득점 (경기당 평균 득점 수)",
        xaxis_title="경기 시간 (분)",
        yaxis_title="경기 1회당 평균 득점",
        height=340,
        margin=dict(t=50, b=40),
    )
    return fig


def variable_radar_chart(variables: list[Variable]) -> go.Figure:
    names = [v.name for v in variables]
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=[v.home_score for v in variables],
            theta=names,
            fill="toself",
            name="🇰🇷 대한민국",
            line_color=KOR_COLOR,
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=[v.away_score for v in variables],
            theta=names,
            fill="toself",
            name="🇲🇽 멕시코",
            line_color=MEX_COLOR,
        )
    )
    fig.update_layout(
        polar={"radialaxis": {"visible": True, "range": [0, 100]}},
        title="변수별 전력 레이더",
        height=420,
        margin=dict(t=60, b=20),
    )
    return fig


def contribution_bubble_chart(variables: list[Variable]) -> go.Figure:
    total = sum(v.weight for v in variables) or 1
    df = pd.DataFrame(
        {
            "변수": [v.name for v in variables],
            "가중치": [v.weight for v in variables],
            "격차": [abs(v.home_score - v.away_score) for v in variables],
            "기여도": [abs(v.home_score - v.away_score) * (v.weight / total) for v in variables],
        }
    )
    fig = go.Figure(
        data=go.Scatter(
            x=df["가중치"],
            y=df["격차"],
            mode="markers+text",
            text=df["변수"],
            textposition="top center",
            marker={
                "size": df["기여도"] * 8 + 10,
                "color": df["기여도"],
                "colorscale": "Reds",
                "showscale": True,
                "colorbar": {"title": "기여도"},
            },
            hovertemplate="%{text}<br>가중치 %{x}%<br>격차 %{y}<extra></extra>",
        )
    )
    fig.update_layout(
        title="변수 기여도 버블 차트",
        xaxis_title="가중치 (%)",
        yaxis_title="팀 간 점수 격차 (Δ)",
        height=400,
        margin=dict(t=50, b=40),
    )
    return fig


def stability_line_chart(curve: list[dict]) -> go.Figure:
    df = pd.DataFrame(curve)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["시뮬레이션 횟수"], y=df["한국 승률 (%)"], mode="lines+markers", name="한국", line={"color": KOR_COLOR}))
    fig.add_trace(go.Scatter(x=df["시뮬레이션 횟수"], y=df["무승부 (%)"], mode="lines+markers", name="무승부", line={"color": DRAW_COLOR}))
    fig.add_trace(go.Scatter(x=df["시뮬레이션 횟수"], y=df["멕시코 승률 (%)"], mode="lines+markers", name="멕시코", line={"color": MEX_COLOR}))
    fig.update_layout(
        title="시뮬레이션 횟수 vs 결과 안정성",
        xaxis={"type": "log", "title": "시뮬레이션 횟수 (로그)"},
        yaxis={"title": "확률 (%)", "range": [0, 100]},
        height=360,
        margin=dict(t=50, b=40),
    )
    return fig


def ab_comparison_chart(pred_a: PredictionResult, pred_b: PredictionResult, label_a: str, label_b: str) -> go.Figure:
    categories = ["한국 승", "무승부", "멕시코 승"]
    fig = go.Figure(
        data=[
            go.Bar(
                name=label_a,
                x=categories,
                y=[pred_a.home_win_prob, pred_a.draw_prob, pred_a.away_win_prob],
                marker_color=KOR_COLOR,
            ),
            go.Bar(
                name=label_b,
                x=categories,
                y=[pred_b.home_win_prob, pred_b.draw_prob, pred_b.away_win_prob],
                marker_color=MEX_COLOR,
            ),
        ]
    )
    fig.update_layout(
        barmode="group",
        title="A/B 프리셋 이론적 승률 비교",
        yaxis_title="확률 (%)",
        height=360,
        margin=dict(t=50, b=40),
    )
    return fig
