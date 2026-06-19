from __future__ import annotations

from http.server import BaseHTTPRequestHandler

from lib.vercel_api import read_json, send_json, simulation_to_dict, variable_from_dict
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
            send_json(
                self,
                200,
                {
                    "simulation": simulation_to_dict(simulation),
                    "confidenceIntervals": ci,
                },
            )
        except Exception as exc:  # noqa: BLE001
            send_json(self, 500, {"error": str(exc)})

    def do_OPTIONS(self) -> None:
        send_json(self, 204, {})
