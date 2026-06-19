from __future__ import annotations

from http.server import BaseHTTPRequestHandler

from lib.vercel_api import send_json, variable_to_dict
from match_simulator.data import INITIAL_VARIABLES, build_static_bundle
from match_simulator.insights import MATCH_INFO, QUICK_SCENARIOS
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
                "nextMatchBanner": format_next_match_banner(),
                "standings": get_group_a_standings(),
                "keyPlayers": {
                    "kor": [
                        {
                            "name": p.name,
                            "position": p.position,
                            "club": p.club,
                            "rating": p.rating,
                        }
                        for p in bundle.kor_key_players
                    ],
                    "mex": [
                        {
                            "name": p.name,
                            "position": p.position,
                            "club": p.club,
                            "rating": p.rating,
                        }
                        for p in bundle.mex_key_players
                    ],
                },
            },
        )

    def do_OPTIONS(self) -> None:
        send_json(self, 204, {})
