export type Variable = {
  id: string;
  name: string;
  description: string;
  question: string;
  homeScore: number;
  awayScore: number;
  weight: number;
};

export type Player = {
  id: string;
  name: string;
  position: string;
  club: string;
  rating: number;
  number?: number | null;
};

export type HistoricalMatch = {
  id: string;
  date: string;
  competition: string;
  score: string;
  result: string;
  opponent: string;
};

export type FootballData = {
  updatedAt: string;
  korea: { name: string; source: string; players: Player[]; recentMatches: HistoricalMatch[] };
  mexico: { name: string; source: string; players: Player[]; recentMatches: HistoricalMatch[] };
  h2hMatches: HistoricalMatch[];
};

export type Prediction = {
  homeWinProb: number;
  drawProb: number;
  awayWinProb: number;
  homeXg: number;
  awayXg: number;
  homeTeamScore: number;
  awayTeamScore: number;
  topScenarios: { home: number; away: number; probability: number; label: string }[];
  impactVariables: { name: string; impact: number; description: string }[];
};

export type Bootstrap = {
  variables: Variable[];
  presetNames: string[];
  matchInfo: Record<string, string>;
  quickScenarios: string[];
  glossary: Record<string, string>;
  nextMatchBanner: string;
  standings: { team: string; code: string; played: number; won: number; drawn: number; lost: number; gf: number; ga: number; pts: number }[];
  footballData: FootballData;
};

export type Insights = {
  favored: string;
  favored_prob: number;
  likely_score: string;
  confidence: number;
  confidence_label: string;
  bias_label: string;
  bias_delta: number;
  top_impact: string;
  kor_rating: number;
  mex_rating: number;
  kor_form: number;
  mex_form: number;
  h2h: string;
  data_updated: string;
  match_info: Record<string, string>;
};

export type Halves = {
  full_time: { home_xg: number; away_xg: number; home_win: number; draw: number; away_win: number };
  first_half: { home_xg: number; away_xg: number; home_win: number; draw: number; away_win: number };
  second_half: { home_xg: number; away_xg: number; home_win: number; draw: number; away_win: number };
};

export type Projection = {
  ifKorWin: string;
  ifDraw: string;
  ifMexWin: string;
  currentRankKor: number;
  currentRankMex: number;
};

export type PredictResponse = {
  prediction: Prediction;
  halves: Halves;
  insights: Insights;
  projection: Projection;
  charts: Record<string, object>;
  weightTotal: number;
};

export type SimulateResponse = {
  simulation: { homeWins: number; draws: number; awayWins: number; total: number };
  confidenceIntervals: Record<string, { point: number; low: number; high: number }>;
  charts: Record<string, object>;
  topScores: { score: string; count: number; probability: number }[];
};

export const RESULT_LABELS: Record<string, string> = { W: "승", D: "무", L: "패" };
