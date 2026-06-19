"""Plotly figure → JSON for react-plotly.js."""

from __future__ import annotations

import json

import plotly.graph_objects as go


def fig_json(fig: go.Figure) -> dict:
    return json.loads(fig.to_json())
