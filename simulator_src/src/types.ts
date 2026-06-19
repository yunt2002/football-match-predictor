/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export interface Player {
  id: string;
  name: string;
  position: "GK" | "DF" | "MF" | "FW";
  club: string;
  rating: number; // 1-100
}

export interface HistoricalMatch {
  id: string;
  date: string;
  competition: string;
  score: string;
  result: "W" | "D" | "L"; // From Korea's perspective
}

export interface Variable {
  id: string;
  name: string;
  description: string;
  question: string;
  homeScore: number; // 1-10
  awayScore: number; // 1-10
  weight: number; // 0-100 (%)
}

export interface SimulationResult {
  homeWins: number;
  draws: number;
  awayWins: number;
  total: number;
  scoreHistogram: Record<string, number>; // "1-1" -> count
  timeDistribution: {
    home: Record<string, number>; // "0-10" -> count
    away: Record<string, number>; // "0-10" -> count
  };
}

export interface PredictionResult {
  homeWinProb: number;
  drawProb: number;
  awayWinProb: number;
  homeXG: number;
  awayXG: number;
  homeTeamScore: number;
  awayTeamScore: number;
  topScenarios: { home: number; away: number; probability: number; label: string }[];
  impactVariables: {
    name: string;
    impact: number;
    description: string;
  }[];
}
