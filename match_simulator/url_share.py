"""설정 URL 공유 (query param)."""

from __future__ import annotations

import base64
import json
import zlib
from typing import Any

from match_simulator.models import Variable
from match_simulator.serialization import variables_from_dict, variables_to_dict


def encode_share_payload(
    variables: list[Variable],
    sim_count: int,
    preset: str | None,
    *,
    kor_formation: str = "4-3-3",
    mex_formation: str = "4-3-3",
) -> str:
    payload: dict[str, Any] = {
        "v": 2,
        "sim_count": sim_count,
        "preset": preset,
        "kor_formation": kor_formation,
        "mex_formation": mex_formation,
        "variables": variables_to_dict(variables),
    }
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    compressed = zlib.compress(raw, level=9)
    return base64.urlsafe_b64encode(compressed).decode("ascii")


def decode_share_payload(token: str) -> dict[str, Any]:
    compressed = base64.urlsafe_b64decode(token.encode("ascii"))
    raw = zlib.decompress(compressed)
    payload = json.loads(raw.decode("utf-8"))
    return {
        "variables": variables_from_dict(payload["variables"]),
        "sim_count": int(payload.get("sim_count", 1000)),
        "preset": payload.get("preset"),
        "kor_formation": payload.get("kor_formation", "4-3-3"),
        "mex_formation": payload.get("mex_formation", "4-3-3"),
    }


def build_share_url(base_url: str, token: str) -> str:
    sep = "&" if "?" in base_url else "?"
    return f"{base_url}{sep}cfg={token}"
