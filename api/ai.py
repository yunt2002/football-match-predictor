from __future__ import annotations

from http.server import BaseHTTPRequestHandler

from lib.vercel_api import read_json, send_json
from match_simulator.ai import generate_match_report, simulate_scenario
from match_simulator.engine import compute_prediction
from lib.vercel_api import prediction_to_dict, variable_from_dict


class handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        try:
            body = read_json(self)
            action = body.get("action", "scenario")
            variables = [variable_from_dict(v) for v in body.get("variables", [])]
            if not variables:
                send_json(self, 400, {"error": "variables required"})
                return

            prediction = compute_prediction(variables)

            if action == "scenario":
                scenario = str(body.get("scenario", "")).strip()
                if not scenario:
                    send_json(self, 400, {"error": "scenario required"})
                    return
                result = simulate_scenario(scenario, variables)
                send_json(self, 200, {"markdown": result, "action": "scenario"})
                return

            if action == "report":
                report = generate_match_report(variables, prediction)
                send_json(
                    self,
                    200,
                    {
                        "markdown": report,
                        "action": "report",
                        "prediction": prediction_to_dict(prediction),
                    },
                )
                return

            send_json(self, 400, {"error": f"unknown action: {action}"})
        except Exception as exc:  # noqa: BLE001
            send_json(self, 500, {"error": str(exc)})

    def do_OPTIONS(self) -> None:
        send_json(self, 204, {})
