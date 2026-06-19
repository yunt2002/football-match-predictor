from __future__ import annotations

from http.server import BaseHTTPRequestHandler

from lib.plotly_export import fig_json
from lib.vercel_api import prediction_to_dict, read_json, send_json, variable_from_dict
from match_simulator.charts import contribution_bubble_chart, prob_stacked_bar, score_heatmap, variable_radar_chart
from match_simulator.engine import compute_half_time_predictions, compute_prediction, compute_score_matrix
from match_simulator.insights import build_sidebar_insights
from match_simulator.data import build_static_bundle
from match_simulator.tournament import project_standings_impact


class handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        try:
            body = read_json(self)
            variables = [variable_from_dict(v) for v in body.get("variables", [])]
            if not variables:
                send_json(self, 400, {"error": "variables required"})
                return

            prediction = compute_prediction(variables)
            halves = compute_half_time_predictions(variables)
            football_data = build_static_bundle()
            weight_total = sum(v.weight for v in variables)
            insights = build_sidebar_insights(
                prediction, variables, weight_total, False, football_data
            )
            projection = project_standings_impact(
                prediction.home_win_prob,
                prediction.draw_prob,
                prediction.away_win_prob,
            )
            matrix = compute_score_matrix(prediction.home_xg, prediction.away_xg)

            charts = {
                "probStackedBar": fig_json(
                    prob_stacked_bar(
                        prediction.home_win_prob,
                        prediction.draw_prob,
                        prediction.away_win_prob,
                        "이론적 승률 (누적)",
                    )
                ),
                "scoreHeatmap": fig_json(score_heatmap(matrix)),
                "variableRadar": fig_json(variable_radar_chart(variables)),
                "contributionBubble": fig_json(contribution_bubble_chart(variables)),
            }

            send_json(
                self,
                200,
                {
                    "prediction": prediction_to_dict(prediction),
                    "halves": halves,
                    "insights": insights,
                    "projection": {
                        "ifKorWin": projection.if_kor_win,
                        "ifDraw": projection.if_draw,
                        "ifMexWin": projection.if_mex_win,
                        "currentRankKor": projection.current_rank_kor,
                        "currentRankMex": projection.current_rank_mex,
                    },
                    "charts": charts,
                    "weightTotal": weight_total,
                },
            )
        except Exception as exc:  # noqa: BLE001
            send_json(self, 500, {"error": str(exc)})

    def do_OPTIONS(self) -> None:
        send_json(self, 204, {})
