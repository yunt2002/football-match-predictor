export type Variable = {
  id: string;
  name: string;
  description: string;
  question: string;
  homeScore: number;
  awayScore: number;
  weight: number;
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
  nextMatchBanner: string;
  standings: {
    team: string;
    code: string;
    played: number;
    won: number;
    drawn: number;
    lost: number;
    gf: number;
    ga: number;
    pts: number;
  }[];
  keyPlayers: {
    kor: { name: string; position: string; club: string; rating: number }[];
    mex: { name: string; position: string; club: string; rating: number }[];
  };
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
