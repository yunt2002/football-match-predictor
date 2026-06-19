from __future__ import annotations

from http.server import BaseHTTPRequestHandler

from lib.plotly_export import fig_json
from lib.vercel_api import read_json, send_json, simulation_to_dict, variable_from_dict
from match_simulator.charts import prob_donut_chart, simulation_score_heatmap, time_distribution_chart
from match_simulator.engine import compute_mc_confidence_intervals, run_monte_carlo


class handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        try:
            body = read_json(self)
            variables = [variable_from_dict(v) for v in body.get("variables", [])]
            sim_count = int(body.get("simCount", 1000))
            if not variables:
                send_json(self, 400, {"error": "variables required"})
                return
            if sim_count < 100 or sim_count > 10000:
                send_json(self, 400, {"error": "simCount must be between 100 and 10000"})
                return

            simulation = run_monte_carlo(variables, sim_count)
            ci = compute_mc_confidence_intervals(simulation)
            home_p = simulation.home_wins / simulation.total * 100
            draw_p = simulation.draws / simulation.total * 100
            away_p = simulation.away_wins / simulation.total * 100

            charts = {
                "probDonut": fig_json(prob_donut_chart(home_p, draw_p, away_p, "몬테카를로 승률")),
                "scoreHeatmap": fig_json(simulation_score_heatmap(simulation)),
                "timeDistribution": fig_json(time_distribution_chart(simulation)),
            }

            top_scores = sorted(simulation.score_histogram.items(), key=lambda x: x[1], reverse=True)[:10]
            score_rows = [
                {
                    "score": k.replace("-", ":"),
                    "count": v,
                    "probability": round(v / simulation.total * 100, 1),
                }
                for k, v in top_scores
            ]

            send_json(
                self,
                200,
                {
                    "simulation": simulation_to_dict(simulation),
                    "confidenceIntervals": ci,
                    "charts": charts,
                    "topScores": score_rows,
                },
            )
        except Exception as exc:  # noqa: BLE001
            send_json(self, 500, {"error": str(exc)})

    def do_OPTIONS(self) -> None:
        send_json(self, 204, {})
