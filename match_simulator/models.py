from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Player:
    id: str
    name: str
    position: str
    club: str
    rating: int
    number: int | None = None

    def copy(self) -> Player:
        return Player(self.id, self.name, self.position, self.club, self.rating, self.number)


@dataclass
class HistoricalMatch:
    id: str
    date: str
    competition: str
    score: str
    result: str  # W, D, L (한국 기준 — 멕시코 전적은 멕시코 기준으로 저장)
    opponent: str = ""


@dataclass
class Variable:
    id: str
    name: str
    description: str
    question: str
    home_score: int
    away_score: int
    weight: int

    def copy(self) -> Variable:
        return Variable(
            id=self.id,
            name=self.name,
            description=self.description,
            question=self.question,
            home_score=self.home_score,
            away_score=self.away_score,
            weight=self.weight,
        )


@dataclass
class ScoreScenario:
    home: int
    away: int
    probability: int
    label: str


@dataclass
class ImpactVariable:
    name: str
    impact: float
    description: str


@dataclass
class PredictionResult:
    home_win_prob: int
    draw_prob: int
    away_win_prob: int
    home_xg: float
    away_xg: float
    home_team_score: float
    away_team_score: float
    top_scenarios: list[ScoreScenario] = field(default_factory=list)
    impact_variables: list[ImpactVariable] = field(default_factory=list)


@dataclass
class SimulationResult:
    home_wins: int
    draws: int
    away_wins: int
    total: int
    score_histogram: dict[str, int] = field(default_factory=dict)
    time_distribution: dict[str, dict[str, int]] = field(default_factory=dict)


@dataclass
class TeamProfile:
    code: str
    name: str
    flag: str
    players: list[Player] = field(default_factory=list)
    recent_matches: list[HistoricalMatch] = field(default_factory=list)
    source: str = "static"
    updated_at: str = ""


@dataclass
class FootballDataBundle:
    korea: TeamProfile
    mexico: TeamProfile
    h2h_matches: list[HistoricalMatch] = field(default_factory=list)
    updated_at: str = ""

    @property
    def kor_key_players(self) -> list[Player]:
        return sorted(self.korea.players, key=lambda p: p.rating, reverse=True)[:5]

    @property
    def mex_key_players(self) -> list[Player]:
        return sorted(self.mexico.players, key=lambda p: p.rating, reverse=True)[:5]
