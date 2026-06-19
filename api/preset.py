from __future__ import annotations

from http.server import BaseHTTPRequestHandler

from lib.vercel_api import read_json, send_json, variable_to_dict
from match_simulator.presets import get_preset


class handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        try:
            body = read_json(self)
            name = str(body.get("name", "균형"))
            variables = get_preset(name)
            send_json(self, 200, {"variables": [variable_to_dict(v) for v in variables], "preset": name})
        except Exception as exc:  # noqa: BLE001
            send_json(self, 500, {"error": str(exc)})

    def do_OPTIONS(self) -> None:
        send_json(self, 204, {})
