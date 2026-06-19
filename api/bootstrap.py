from __future__ import annotations

from http.server import BaseHTTPRequestHandler

from lib.vercel_api import football_bundle_to_dict, send_json, variable_to_dict
from match_simulator.data import INITIAL_VARIABLES, build_static_bundle
from match_simulator.insights import GLOSSARY, MATCH_INFO, QUICK_SCENARIOS
from match_simulator.presets import PRESET_NAMES
from match_simulator.tournament import format_next_match_banner, get_group_a_standings


class handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        bundle = build_static_bundle()
        send_json(
            self,
            200,
            {
                "variables": [variable_to_dict(v) for v in INITIAL_VARIABLES],
                "presetNames": PRESET_NAMES,
                "matchInfo": MATCH_INFO,
                "quickScenarios": QUICK_SCENARIOS,
                "glossary": GLOSSARY,
                "nextMatchBanner": format_next_match_banner(),
                "standings": get_group_a_standings(),
                "footballData": football_bundle_to_dict(bundle),
            },
        )

    def do_OPTIONS(self) -> None:
        send_json(self, 204, {})
