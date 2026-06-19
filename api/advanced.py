from __future__ import annotations

from http.server import BaseHTTPRequestHandler

from lib.plotly_export import fig_json
from lib.vercel_api import prediction_to_dict, read_json, send_json, variable_from_dict, variable_to_dict
from match_simulator.charts import ab_comparison_chart, stability_line_chart
from match_simulator.comparison import compare_with_actual
from match_simulator.engine import (
    compute_prediction,
    compute_sensitivity,
    compute_stability_curve,
    normalize_weights,
    run_monte_carlo,
)
from match_simulator.player_whatif import apply_player_whatif, list_whatif_options
from match_simulator.data import build_static_bundle, get_key_players
from match_simulator.presets import PRESET_NAMES, get_preset


class handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        try:
            body = read_json(self)
            action = body.get("action")
            if not action:
                send_json(self, 400, {"error": "action required"})
                return

            if action == "normalize":
                variables = [variable_from_dict(v) for v in body.get("variables", [])]
                normalized = normalize_weights(variables)
                send_json(self, 200, {"variables": [variable_to_dict(v) for v in normalized]})
                return

            if action == "whatif":
                variables = [variable_from_dict(v) for v in body.get("variables", [])]
                team = str(body.get("team", "kor"))
                player = str(body.get("player", ""))
                mode = str(body.get("mode", "out"))
                bundle = build_static_bundle()
                squad = bundle.korea.players if team == "kor" else bundle.mexico.players
                adjusted, notes = apply_player_whatif(variables, player, team, mode)
                send_json(
                    self,
                    200,
                    {"variables": [variable_to_dict(v) for v in adjusted], "notes": notes},
                )
                return

            if action == "whatifOptions":
                team = str(body.get("team", "kor"))
                bundle = build_static_bundle()
                squad = bundle.korea.players if team == "kor" else bundle.mexico.players
                options = list_whatif_options(squad) or [p.name for p in get_key_players(squad, 8)]
                send_json(self, 200, {"options": options})
                return

            if action == "sensitivity":
                variables = [variable_from_dict(v) for v in body.get("variables", [])]
                send_json(self, 200, {"rows": compute_sensitivity(variables)})
                return

            if action == "abCompare":
                preset_a = str(body.get("presetA", PRESET_NAMES[0]))
                preset_b = str(body.get("presetB", PRESET_NAMES[1]))
                pred_a = compute_prediction(get_preset(preset_a))
                pred_b = compute_prediction(get_preset(preset_b))
                chart = fig_json(ab_comparison_chart(pred_a, pred_b, preset_a, preset_b))
                send_json(
                    self,
                    200,
                    {
                        "presetA": preset_a,
                        "presetB": preset_b,
                        "predictionA": prediction_to_dict(pred_a),
                        "predictionB": prediction_to_dict(pred_b),
                        "chart": chart,
                    },
                )
                return

            if action == "stability":
                variables = [variable_from_dict(v) for v in body.get("variables", [])]
                prediction = compute_prediction(variables)
                curve = compute_stability_curve(prediction.home_xg, prediction.away_xg)
                send_json(
                    self,
                    200,
                    {"curve": curve, "chart": fig_json(stability_line_chart(curve))},
                )
                return

            if action == "compareActual":
                variables = [variable_from_dict(v) for v in body.get("variables", [])]
                prediction = compute_prediction(variables)
                sim_count = int(body.get("simCount", 1000))
                simulation = None
                if body.get("includeSimulation"):
                    simulation = run_monte_carlo(variables, sim_count)
                actual_home = int(body.get("actualHome", 0))
                actual_away = int(body.get("actualAway", 0))
                cmp = compare_with_actual(prediction, simulation, actual_home, actual_away)
                send_json(
                    self,
                    200,
                    {
                        "outcomeCorrect": cmp.outcome_correct,
                        "topScoreHit": cmp.top_score_hit,
                        "predictedTopScore": cmp.predicted_top_score,
                        "narrative": cmp.narrative,
                        "mcSummary": cmp.mc_summary,
                    },
                )
                return

            send_json(self, 400, {"error": f"unknown action: {action}"})
        except Exception as exc:  # noqa: BLE001
            send_json(self, 500, {"error": str(exc)})

    def do_OPTIONS(self) -> None:
        send_json(self, 204, {})
