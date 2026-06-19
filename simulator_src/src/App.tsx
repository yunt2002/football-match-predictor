/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useMemo } from "react";
import { 
  Settings2, 
  BarChart3, 
  AlertCircle, 
  ShieldCheck,
  Zap,
  Info,
  RotateCcw,
  Target,
  BrainCircuit,
  Clock
} from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import Markdown from "react-markdown";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { Variable, PredictionResult, SimulationResult, Player, HistoricalMatch } from "./types";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const KOR_PLAYERS: Player[] = [
  { id: "p1", name: "손흥민", position: "FW", club: "토트넘", rating: 92 },
  { id: "p2", name: "김민재", position: "DF", club: "바이에른 뮌헨", rating: 89 },
  { id: "p3", name: "이강인", position: "MF", club: "PSG", rating: 86 },
  { id: "p4", name: "황희찬", position: "FW", club: "울버햄튼", rating: 84 },
  { id: "p5", name: "조현우", position: "GK", club: "울산 HD", rating: 81 },
];

const MEX_PLAYERS: Player[] = [
  { id: "m1", name: "산티아고 히메네스", position: "FW", club: "페예노르트", rating: 85 },
  { id: "m2", name: "에드손 알바레스", position: "MF", club: "웨스트햄", rating: 84 },
  { id: "m3", name: "이르빙 로사노", position: "FW", club: "PSV", rating: 82 },
  { id: "m4", name: "요한 바스케스", position: "DF", club: "제노아", rating: 79 },
  { id: "m5", name: "기예르모 오초아", position: "GK", club: "AVS", rating: 78 },
];

const H2H_MATCHES: HistoricalMatch[] = [
  { id: "h1", date: "2018.06.23", competition: "러시아 월드컵", score: "1:2", result: "L" },
  { id: "h2", date: "2010.05.16", competition: "친선 경기", score: "1:0", result: "W" },
  { id: "h3", date: "2002.01.27", competition: "골드컵", score: "0:0 (PK 승)", result: "W" },
  { id: "h4", date: "1998.06.13", competition: "프랑스 월드컵", score: "1:3", result: "L" },
];

const KOR_RECENT_MATCHES: HistoricalMatch[] = [
  { id: "k1", date: "2024.06.11", competition: "월드컵 예선", score: "1:0", result: "W" },
  { id: "k2", date: "2024.06.06", competition: "월드컵 예선", score: "7:0", result: "W" },
  { id: "k3", date: "2024.03.26", competition: "월드컵 예선", score: "3:0", result: "W" },
  { id: "k4", date: "2024.03.21", competition: "월드컵 예선", score: "1:1", result: "D" },
];

const MEX_RECENT_MATCHES: HistoricalMatch[] = [
  { id: "x1", date: "2024.07.01", competition: "코파 아메리카", score: "0:0", result: "D" },
  { id: "x2", date: "2024.06.27", competition: "코파 아메리카", score: "0:1", result: "L" },
  { id: "x3", date: "2024.06.23", competition: "코파 아메리카", score: "1:0", result: "W" },
  { id: "x4", date: "2024.06.09", competition: "친선 경기", score: "2:3", result: "L" },
];

const INITIAL_VARIABLES: Variable[] = [
  { id: "v1", name: "FIFA 랭킹", question: "장기 전력을 더 믿을까?", description: "공식 랭킹에 따른 객관적 전력 지표", homeScore: 75, awayScore: 82, weight: 15 },
  { id: "v2", name: "최근 흐름", question: "첫 경기 결과를 크게 볼까?", description: "최근 경기 승률 및 경기력 추세", homeScore: 80, awayScore: 60, weight: 15 },
  { id: "v3", name: "공격력", question: "득점 기대를 더 볼까?", description: "득점 생산력 및 슈팅 정확도", homeScore: 70, awayScore: 70, weight: 15 },
  { id: "v4", name: "수비 안정성", question: "실점 위험을 더 볼까?", description: "실점 억제력 및 조직력", homeScore: 60, awayScore: 75, weight: 15 },
  { id: "v5", name: "핵심 선수", question: "스타 선수 영향이 큰가?", description: "주축 선수의 컨디션 및 의존도", homeScore: 90, awayScore: 50, weight: 10 },
  { id: "v6", name: "전술 상성", question: "스타일 상성이 중요한가?", description: "상대 플레이 스타일 및 전술 대응력", homeScore: 65, awayScore: 65, weight: 10 },
  { id: "v7", name: "홈/환경", question: "개최국 분위기를 크게 볼까?", description: "기후, 고도 및 관중 응원 영향", homeScore: 85, awayScore: 40, weight: 10 },
  { id: "v8", name: "역대 전적", question: "과거 전적은 얼마나 반영할까?", description: "상대 팀과의 이전 매치 데이터", homeScore: 40, awayScore: 60, weight: 5 },
  { id: "v9", name: "불확실성", question: "정보가 부족하면 신뢰도를 낮출까?", description: "부상병동이나 정보 비대칭성 변수", homeScore: 50, awayScore: 50, weight: 5 },
];

export default function App() {
  const [variables, setVariables] = useState<Variable[]>(INITIAL_VARIABLES);
  const [simCount, setSimCount] = useState<number>(1000);
  const [simulation, setSimulation] = useState<SimulationResult | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [activeTab, setActiveTab] = useState<"input" | "output">("input");
  const [historyView, setHistoryView] = useState<"h2h" | "korea" | "mexico">("h2h");
  const [scenario, setScenario] = useState("");
  const [aiSimulationResult, setAiSimulationResult] = useState<string | null>(null);
  const [isAiSimulating, setIsAiSimulating] = useState(false);

  const weightSum = useMemo(() => variables.reduce((sum, v) => sum + v.weight, 0), [variables]);

  const normalizeWeights = () => {
    const sum = variables.reduce((s, v) => s + v.weight, 0);
    if (sum === 0) return;
    setVariables(prev => prev.map(v => ({
      ...v,
      weight: Number(((v.weight / sum) * 100).toFixed(0))
    })));
  };

  const prediction = useMemo((): PredictionResult => {
    const sum = variables.reduce((s, v) => s + v.weight, 0);
    const safeSum = sum === 0 ? 1 : sum;

    // 1. Team Score Calculation (Requirement 2)
    const homeTeamScore = variables.reduce((acc, v) => acc + (v.homeScore * (v.weight / safeSum)), 0);
    const awayTeamScore = variables.reduce((acc, v) => acc + (v.awayScore * (v.weight / safeSum)), 0);

    // 2. Expected Goals (xG) Calculation (Requirement 3) - Normalized -1 to 1 impact
    let homeXG = 1.0;
    let awayXG = 1.0;

    const mod = (score: number) => (score - 50) / 50; // Normalize 0-100 to -1 to 1

    const getMod = (id: string, side: "home" | "away") => mod(variables.find(v => v.id === id)?.[side === "home" ? "homeScore" : "awayScore"] || 50);
    
    // Korea xG = 1.0 + Korea Attack - Mexico Defense + Recent Form + Tactics
    homeXG = Math.max(0.1, homeXG + getMod("v3", "home") - getMod("v4", "away") + getMod("v2", "home") + getMod("v6", "home"));
    // Mexico xG = 1.0 + Mexico Attack - Korea Defense + Home/Env + Recent Form
    awayXG = Math.max(0.1, awayXG + getMod("v3", "away") - getMod("v4", "home") + getMod("v7", "away") + getMod("v2", "away"));

    // 3. Probability Inference
    const diffXG = homeXG - awayXG;
    const drawProb = Math.max(10, 30 - Math.abs(diffXG) * 10);
    const remProb = 100 - drawProb;
    const homeWinProb = Math.max(5, Math.min(remProb - 5, (remProb / 2) + (diffXG * 15)));
    const awayWinProb = 100 - drawProb - homeWinProb;

    // 4. Scenarios (Requirement 3)
    const factorial = (n: number): number => (n <= 1 ? 1 : n * factorial(n - 1));
    const poisson = (lambda: number, k: number) => (Math.pow(lambda, k) * Math.exp(-lambda)) / factorial(k);

    const scores: { h: number, a: number, p: number }[] = [];
    for (let h = 0; h <= 4; h++) {
      for (let a = 0; a <= 4; a++) {
        scores.push({ h, a, p: poisson(homeXG, h) * poisson(awayXG, a) });
      }
    }
    const top3 = scores.sort((a, b) => b.p - a.p).slice(0, 3);
    
    const scenarios = [
      { home: top3[0].h, away: top3[0].a, probability: Math.round(top3[0].p * 100), label: "가장 현실적인 시나리오" },
      { home: top3[1].h, away: top3[1].a, probability: Math.round(top3[1].p * 100), label: "차선 시나리오 1" },
      { home: top3[2].h, away: top3[2].a, probability: Math.round(top3[2].p * 100), label: "차선 시나리오 2" }
    ];

    // 5. Impact Factors (Requirement 5)
    const impacts = [...variables]
      .map(v => ({
        name: v.name,
        impact: Math.abs(v.homeScore - v.awayScore) * (v.weight / safeSum),
        description: v.description
      }))
      .sort((a, b) => b.impact - a.impact)
      .slice(0, 3);

    return {
      homeWinProb: Math.round(homeWinProb),
      drawProb: Math.round(drawProb),
      awayWinProb: Math.round(awayWinProb),
      homeXG: Number(homeXG.toFixed(1)),
      awayXG: Number(awayXG.toFixed(1)),
      homeTeamScore: Number(homeTeamScore.toFixed(2)),
      awayTeamScore: Number(awayTeamScore.toFixed(2)),
      topScenarios: scenarios,
      impactVariables: impacts
    };
  }, [variables]);

  const runSimulation = () => {
    setIsSimulating(true);
    setSimulation(null);
    
    setTimeout(() => {
      let homeWins = 0;
      let draws = 0;
      let awayWins = 0;
      const scoreHistogram: Record<string, number> = {};
      const timeDistribution = {
        home: {} as Record<string, number>,
        away: {} as Record<string, number>
      };

      // Initialize buckets
      for (let i = 0; i < 9; i++) {
        const key = `${i * 10}-${(i + 1) * 10}`;
        timeDistribution.home[key] = 0;
        timeDistribution.away[key] = 0;
      }

      const { homeXG, awayXG } = prediction;

      const getPoissonGoals = (lambda: number) => {
        let L = Math.exp(-lambda);
        let p = 1.0;
        let k = 0;
        do {
          k++;
          p *= Math.random();
        } while (p > L);
        return k - 1;
      };

      for (let i = 0; i < simCount; i++) {
        const h = getPoissonGoals(homeXG);
        const a = getPoissonGoals(awayXG);
        
        const scoreKey = `${h}-${a}`;
        scoreHistogram[scoreKey] = (scoreHistogram[scoreKey] || 0) + 1;

        // Simulate goal times
        for (let g = 0; g < h; g++) {
          const minute = Math.floor(Math.random() * 90);
          const bucket = `${Math.floor(minute / 10) * 10}-${(Math.floor(minute / 10) + 1) * 10}`;
          timeDistribution.home[bucket] = (timeDistribution.home[bucket] || 0) + 1;
        }
        for (let g = 0; g < a; g++) {
          const minute = Math.floor(Math.random() * 90);
          const bucket = `${Math.floor(minute / 10) * 10}-${(Math.floor(minute / 10) + 1) * 10}`;
          timeDistribution.away[bucket] = (timeDistribution.away[bucket] || 0) + 1;
        }

        if (h > a) homeWins++;
        else if (h === a) draws++;
        else awayWins++;
      }

      setSimulation({ homeWins, draws, awayWins, total: simCount, scoreHistogram, timeDistribution });
      setIsSimulating(false);
      setActiveTab("output");
    }, 1000);
  };

  const runAiScenarioSimulation = async () => {
    if (!scenario.trim()) return;
    setIsAiSimulating(true);
    setAiSimulationResult(null);
    try {
      const response = await fetch("/api/ai-scenario-simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          scenario,
          variables,
          homeTeam: { name: "대한민국" },
          awayTeam: { name: "멕시코" }
        })
      });
      const data = await response.json();
      setAiSimulationResult(data.result);
    } catch (error) {
      console.error("AI Simulation Error:", error);
      setAiSimulationResult("AI 시뮬레이션 중 오류가 발생했습니다.");
    } finally {
      setIsAiSimulating(false);
    }
  };

  const handleUpdate = (id: string, field: "homeScore" | "awayScore" | "weight", val: number) => {
    setVariables(prev => prev.map(v => v.id === id ? { ...v, [field]: val } : v));
  };

  return (
    <div className="min-h-screen bg-[#F0F0EE] text-[#1A1A1A] font-sans selection:bg-[#E02020] selection:text-white">
      <div className="max-w-7xl mx-auto p-4 md:p-10">
        
        {/* Header */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end border-b-4 border-[#1A1A1A] pb-6 mb-12">
          <div>
            <div className="text-[11px] font-mono tracking-[0.2em] uppercase opacity-50 mb-2">Computational Sports Modeling</div>
            <h1 className="text-4xl md:text-6xl font-black uppercase tracking-tighter leading-none">
              승부 예측 <span className="bg-[#1A1A1A] text-white px-3 ml-1">시뮬레이터</span>
            </h1>
          </div>
          <div className="flex items-center gap-8 mt-8 md:mt-0">
            <div className="text-right">
              <div className="text-[10px] font-mono uppercase opacity-40">Matchup ID</div>
              <div className="text-sm font-bold uppercase">KOR-MEX-2026-MC</div>
            </div>
            <div className="w-[1px] h-12 bg-[#1A1A1A]/10 hidden md:block" />
            <div className="text-center">
              <div className="text-[10px] font-mono uppercase opacity-40">Weight Status</div>
              <div className={cn(
                "text-sm font-black px-2 py-0.5",
                weightSum === 100 ? "bg-emerald-500 text-white" : "bg-[#E02020] text-white"
              )}>
                {weightSum}%
              </div>
            </div>
          </div>
        </header>

        <div className="grid grid-cols-1 xl:grid-cols-12 gap-12">
          
          {/* Left: Input Panel (Req 1, 2) */}
          <div className="xl:col-span-8 flex flex-col gap-10">
            
            {/* Actual Squad Comparison */}
            <section className="bg-white border-2 border-[#1A1A1A] p-8 shadow-[12px_12px_0px_0px_#1A1A1A]">
              <div className="flex items-center gap-4 mb-10 pb-4 border-b-2 border-[#1A1A1A]">
                <div className="w-12 h-12 bg-[#1A1A1A] flex items-center justify-center">
                  <ShieldCheck className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-black uppercase tracking-tight">주요 전력 스쿼드 분석</h2>
                  <p className="text-[10px] font-mono opacity-40 uppercase">Roster Strength & Club Status</p>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl bg-neutral-100 p-2 border border-[#1A1A1A]/10">🇰🇷</span>
                      <span className="font-black uppercase text-base tracking-tight">Korea Republic</span>
                    </div>
                    <span className="text-xs font-mono opacity-30">主力 5人</span>
                  </div>
                  <div className="space-y-2">
                    {KOR_PLAYERS.map(p => (
                      <div key={p.id} className="group flex justify-between items-center text-[11px] p-3 border border-[#1A1A1A]/5 bg-neutral-50/50 hover:bg-neutral-100 transition-colors">
                        <div className="flex gap-4 items-center">
                          <span className="font-mono text-[#E02020] font-bold w-4">{p.position}</span>
                          <span className="font-black">{p.name}</span>
                        </div>
                        <div className="flex gap-4 items-center">
                          <span className="opacity-40 italic">{p.club}</span>
                          <div className="w-8 text-right font-mono font-black border-l border-[#1A1A1A]/10 pl-2">{p.rating}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl bg-neutral-100 p-2 border border-[#1A1A1A]/10">🇲🇽</span>
                      <span className="font-black uppercase text-base tracking-tight">Mexico</span>
                    </div>
                    <span className="text-xs font-mono opacity-30">Principales 5</span>
                  </div>
                  <div className="space-y-2">
                    {MEX_PLAYERS.map(p => (
                      <div key={p.id} className="group flex justify-between items-center text-[11px] p-3 border border-[#1A1A1A]/5 bg-neutral-50/50 hover:bg-neutral-100 transition-colors">
                        <div className="flex gap-4 items-center">
                          <span className="font-mono text-emerald-600 font-bold w-4">{p.position}</span>
                          <span className="font-black">{p.name}</span>
                        </div>
                        <div className="flex gap-4 items-center">
                          <span className="opacity-40 italic">{p.club}</span>
                          <div className="w-8 text-right font-mono font-black border-l border-[#1A1A1A]/10 pl-2">{p.rating}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </section>

            {/* Match History */}
            <section className="bg-white border-2 border-[#1A1A1A] p-8 shadow-[12px_12px_0px_0px_#1A1A1A]">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8 pb-4 border-b-2 border-[#1A1A1A]">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-[#1A1A1A] flex items-center justify-center">
                    <RotateCcw className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-black uppercase tracking-tight">전적 데이터 분석</h2>
                    <p className="text-[10px] font-mono opacity-40 uppercase">Statistical History</p>
                  </div>
                </div>
                <div className="flex gap-1 bg-neutral-100 p-1 border border-[#1A1A1A]/10">
                  <button 
                    onClick={() => setHistoryView("h2h")}
                    className={cn(
                      "px-4 py-2 text-[10px] font-black uppercase transition-all",
                      historyView === "h2h" ? "bg-[#1A1A1A] text-white" : "hover:bg-neutral-200 opacity-50"
                    )}
                  >
                    H2H
                  </button>
                  <button 
                    onClick={() => setHistoryView("korea")}
                    className={cn(
                      "px-4 py-2 text-[10px] font-black uppercase transition-all",
                      historyView === "korea" ? "bg-[#E02020] text-white" : "hover:bg-neutral-200 opacity-50"
                    )}
                  >
                    KOREA
                  </button>
                  <button 
                    onClick={() => setHistoryView("mexico")}
                    className={cn(
                      "px-4 py-2 text-[10px] font-black uppercase transition-all",
                      historyView === "mexico" ? "bg-emerald-600 text-white" : "hover:bg-neutral-200 opacity-50"
                    )}
                  >
                    MEXICO
                  </button>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-xs text-left">
                  <thead>
                    <tr className="border-b border-[#1A1A1A] uppercase font-black text-[10px]">
                      <th className="pb-4">DATE</th>
                      <th className="pb-4">TOURNAMENT</th>
                      <th className="pb-4 text-center">SCORE</th>
                      <th className="pb-4 text-right">OUTCOME</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#1A1A1A]/5 text-[11px]">
                    {(historyView === "h2h" ? H2H_MATCHES : historyView === "korea" ? KOR_RECENT_MATCHES : MEX_RECENT_MATCHES).map(m => (
                      <tr key={m.id} className="hover:bg-neutral-50 transition-colors">
                        <td className="py-5 opacity-50 font-mono">{m.date}</td>
                        <td className="py-5 font-black uppercase tracking-tighter">{m.competition}</td>
                        <td className="py-5 text-center font-mono font-black text-base">{m.score}</td>
                        <td className="py-5 text-right">
                          <span className={cn(
                            "px-3 py-1 font-black uppercase text-[9px] tracking-widest",
                            m.result === "W" ? "bg-emerald-600 text-white" : m.result === "L" ? "bg-[#E02020] text-white" : "bg-neutral-800 text-white"
                          )}>
                            {m.result === "W" ? "Victory" : m.result === "L" ? "Defeat" : "Draw"}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="mt-6 pt-4 border-t border-[#1A1A1A]/5">
                <p className="text-[9px] font-mono opacity-30 text-right uppercase">
                  {historyView === "h2h" ? "* Both teams' direct history" : historyView === "korea" ? "* Korea Republic overall form" : "* Mexico overall form"}
                </p>
              </div>
            </section>

            <section className="bg-white border-2 border-[#1A1A1A] p-8 shadow-[12px_12px_0px_0px_#1A1A1A]">
              <div className="flex flex-col md:flex-row justify-between items-center gap-6 mb-12 pb-6 border-b border-[#1A1A1A]/10">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-[#1A1A1A] flex items-center justify-center">
                    <Settings2 className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-black uppercase tracking-tight">1. 전력 모델 파라미터 조정</h2>
                    <p className="text-xs opacity-50 font-medium">9가지 변수에 대한 가중치와 팀별 전력을 정의하십시오.</p>
                  </div>
                </div>
                <button 
                  onClick={normalizeWeights}
                  className={cn(
                    "px-8 py-3 text-xs font-black uppercase tracking-widest transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,0.1)] active:translate-x-1 active:translate-y-1 active:shadow-none",
                    weightSum === 100 
                      ? "bg-[#1A1A1A] text-white hover:bg-neutral-800" 
                      : "bg-[#E02020] text-white animate-pulse"
                  )}
                >
                  Auto Normalize
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-x-16 gap-y-12">
                {variables.map((v) => (
                  <div key={v.id} className="relative p-4 border border-transparent hover:border-[#1A1A1A]/5 transition-all bg-[#F9F9F7]">
                    <div className="flex justify-between items-start mb-2">
                       <div className="flex flex-col gap-1">
                          <div className="flex items-center gap-2">
                            <span className="font-black uppercase text-sm">{v.name}</span>
                            <div className="relative group cursor-help">
                              <Info className="w-3 h-3 opacity-30" />
                              <div className="absolute left-0 bottom-full mb-2 w-56 bg-[#1A1A1A] text-white text-[10px] p-3 leading-relaxed opacity-0 group-hover:opacity-100 transition-all z-50 pointer-events-none shadow-xl">
                                {v.description}
                              </div>
                            </div>
                          </div>
                          <span className="text-[10px] text-emerald-600 font-bold tracking-tight italic">"{v.question}"</span>
                       </div>
                       <div className="text-right">
                         <span className="text-[9px] font-mono opacity-40 uppercase block">Weight</span>
                         <span className="text-xl font-mono font-black">{v.weight}%</span>
                       </div>
                    </div>

                    <div className="mb-6">
                      <input 
                        type="range" min="0" max="100" step="1"
                        value={v.weight}
                        onChange={(e) => handleUpdate(v.id, "weight", parseInt(e.target.value))}
                        className="w-full h-1.5 bg-[#1A1A1A]/10 appearance-none cursor-pointer accent-[#1A1A1A]"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-8">
                       <div className="space-y-3">
                         <div className="flex justify-between items-baseline text-[10px] font-mono uppercase">
                           <span className="opacity-50">🇰🇷 대한민국</span>
                           <span className="text-lg font-black text-[#E02020]">{v.homeScore}</span>
                         </div>
                         <input 
                           type="range" min="0" max="100" step="1"
                           value={v.homeScore}
                           onChange={(e) => handleUpdate(v.id, "homeScore", parseInt(e.target.value))}
                           className="w-full h-1 bg-[#E02020]/10 appearance-none cursor-pointer accent-[#E02020]"
                         />
                       </div>
                       <div className="space-y-3">
                         <div className="flex justify-between items-baseline text-[10px] font-mono uppercase">
                           <span className="opacity-50">🇲🇽 멕시코</span>
                           <span className="text-lg font-black text-emerald-600">{v.awayScore}</span>
                         </div>
                         <input 
                           type="range" min="0" max="100" step="1"
                           value={v.awayScore}
                           onChange={(e) => handleUpdate(v.id, "awayScore", parseInt(e.target.value))}
                           className="w-full h-1 bg-emerald-600/10 appearance-none cursor-pointer accent-emerald-600"
                         />
                       </div>
                    </div>
                  </div>
                ))}
              </div>

              {weightSum !== 100 && (
                <div className="mt-12 p-4 bg-[#E02020]/5 border-l-4 border-[#E02020] flex items-center gap-4">
                  <AlertCircle className="w-5 h-5 text-[#E02020]" />
                  <p className="text-xs font-bold text-[#E02020] italic">
                    [System Warning] 가중치의 합계가 {weightSum}%입니다. 100%가 아닐 경우 모델의 신뢰도가 왜곡됩니다.
                  </p>
                </div>
              )}
            </section>

            {/* Monte Carlo Control (Req 4) */}
            <section className="bg-[#1A1A1A] p-6 md:p-8 lg:p-10 shadow-[12px_12px_0px_0px_#1A1A1A] w-full box-border">
                <div className="flex flex-col lg:flex-row items-center justify-between gap-8 w-full">
                  {/* Title Block */}
                  <div className="flex gap-4 md:gap-6 items-center w-full lg:w-auto min-w-0">
                    <div className="shrink-0 w-12 h-12 md:w-16 md:h-16 border-2 border-white/20 flex items-center justify-center rounded-none rotate-45">
                      <Zap className="-rotate-45 w-6 h-6 md:w-7 md:h-7 text-[#E02020]" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <h2 className="text-xl md:text-2xl lg:text-3xl font-black uppercase text-white tracking-widest truncate">2. 모의 시뮬레이션</h2>
                      <p className="text-[9px] md:text-[10px] font-mono text-white/40 uppercase tracking-[0.2em] md:tracking-[0.3em] truncate">Monte Carlo Iterative Engine</p>
                    </div>
                  </div>

                  {/* Controls Block */}
                  <div className="flex flex-col md:flex-row items-center gap-4 w-full lg:w-auto shrink-0">
                    <div className="flex flex-wrap justify-center gap-2 w-full md:w-auto">
                      {[10, 100, 1000, 10000].map(n => (
                        <button 
                          key={n}
                          onClick={() => setSimCount(n)}
                          className={cn(
                            "px-3 py-2 md:px-5 md:py-3 text-[10px] md:text-[11px] font-mono font-black border-2 transition-all whitespace-nowrap flex-1 md:flex-none min-w-[70px]",
                            simCount === n ? "bg-white text-[#1A1A1A] border-white" : "text-white border-white/20 hover:border-white/50"
                          )}
                        >
                          {n.toLocaleString()}회
                        </button>
                      ))}
                    </div>
                    <button 
                      onClick={runSimulation}
                      disabled={isSimulating || weightSum === 0}
                      className="w-full md:w-auto bg-[#E02020] text-white px-8 md:px-10 py-3.5 md:py-4 font-black uppercase tracking-[0.2em] text-[10px] md:text-xs hover:bg-[#E02020]/90 transition-all disabled:opacity-30 disabled:cursor-not-allowed shadow-[0px_0px_20px_rgba(224,32,32,0.3)] shrink-0 whitespace-nowrap"
                    >
                      {isSimulating ? "Processing..." : "Run Engine"}
                    </button>
                  </div>
                </div>
            </section>

            {/* AI Scenario Simulation (Req: 3 AI Simulation) */}
            <section className="bg-white border-2 border-[#1A1A1A] p-6 md:p-8 shadow-[12px_12px_0px_0px_#1A1A1A] overflow-hidden">
                <div className="flex items-center gap-4 mb-8 pb-4 border-b-2 border-[#1A1A1A] w-full overflow-hidden">
                  <div className="shrink-0 w-10 h-10 md:w-12 md:h-12 bg-emerald-600 flex items-center justify-center">
                    <BrainCircuit className="w-5 h-5 md:w-6 md:h-6 text-white" />
                  </div>
                  <div className="min-w-0 shrink-0">
                    <h2 className="text-xl md:text-2xl font-black uppercase tracking-tight whitespace-nowrap">3. AI 시나리오 시뮬레이션</h2>
                    <p className="text-[9px] md:text-[10px] font-mono opacity-40 uppercase whitespace-nowrap">AI Reasoning & Inference</p>
                  </div>
                </div>

                <div className="space-y-6">
                  <div className="flex flex-col gap-2">
                    <label className="text-[10px] font-mono font-black uppercase opacity-40">부여할 특정 상황 (Scenario)</label>
                    <textarea 
                      value={scenario}
                      onChange={(e) => setScenario(e.target.value)}
                      placeholder="예: 경기 10분 만에 손흥민 선수가 부상으로 교체된다면? 또는 폭우가 쏟아져서 그라운드가 엉망이 된다면?"
                      className="w-full h-32 p-4 bg-neutral-50 border border-[#1A1A1A]/10 text-sm font-medium focus:ring-2 focus:ring-[#E02020] focus:border-transparent outline-none transition-all resize-none"
                    />
                  </div>

                  <button 
                    onClick={runAiScenarioSimulation}
                    disabled={isAiSimulating || !scenario.trim()}
                    className="w-full bg-[#1A1A1A] text-white py-4 font-black uppercase tracking-[0.2em] text-xs hover:bg-neutral-800 transition-all disabled:opacity-30 disabled:cursor-not-allowed group flex items-center justify-center gap-3"
                  >
                    {isAiSimulating ? (
                      <>
                        <div className="w-3 h-3 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Zap className="w-4 h-4 fill-white" />
                        AI 시나리오 가동
                      </>
                    )}
                  </button>

                  <AnimatePresence>
                    {aiSimulationResult && (
                      <motion.div 
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mt-10 p-8 bg-[#F9F9F7] border-l-8 border-emerald-600 shadow-inner"
                      >
                         <div className="prose prose-sm max-w-none prose-headings:font-black prose-headings:uppercase prose-headings:tracking-tighter prose-neutral">
                           <div className="markdown-body">
                             <Markdown>{aiSimulationResult}</Markdown>
                           </div>
                         </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
            </section>
          </div>

          {/* Right: Output Panel (Req 3, 4, 5) */}
          <div className="xl:col-span-4 flex flex-col gap-10">
            
            {/* Score & xG Model (Req 3) - PROBABILITY CARDS AT TOP */}
            <section className={cn(
               "bg-white border-4 border-[#1A1A1A] p-8 shadow-[12px_12px_0px_0px_#1A1A1A] transition-all",
               activeTab === "output" ? "scale-100 opacity-100" : "opacity-30 blur-[2px] grayscale"
            )}>
               <h3 className="text-sm font-black uppercase mb-8 flex items-center gap-3">
                 <ShieldCheck className="w-5 h-5" />
                 경기 결과 예측 확률
               </h3>

               {simulation ? (
                 <div className="space-y-6">
                   <div className="grid grid-cols-3 gap-3">
                     <div className="bg-[#E02020] p-6 flex flex-col items-center text-white shadow-lg">
                       <span className="text-[10px] font-mono opacity-60 uppercase mb-1">Win</span>
                       <span className="text-4xl font-black tracking-tighter">{((simulation.homeWins / simulation.total) * 100).toFixed(1)}%</span>
                       <span className="text-[10px] font-bold mt-2">KOREA</span>
                     </div>
                     <div className="bg-[#1A1A1A] p-6 flex flex-col items-center text-white shadow-lg">
                       <span className="text-[10px] font-mono opacity-60 uppercase mb-1">Draw</span>
                       <span className="text-4xl font-black tracking-tighter">{((simulation.draws / simulation.total) * 100).toFixed(1)}%</span>
                       <span className="text-[10px] font-bold mt-2">-</span>
                     </div>
                     <div className="bg-emerald-600 p-6 flex flex-col items-center text-white shadow-lg">
                       <span className="text-[10px] font-mono opacity-60 uppercase mb-1">Win</span>
                       <span className="text-4xl font-black tracking-tighter">{((simulation.awayWins / simulation.total) * 100).toFixed(1)}%</span>
                       <span className="text-[10px] font-bold mt-2">MEXICO</span>
                     </div>
                   </div>
                   
                   <div className="flex h-4 w-full bg-[#1A1A1A]/5 rounded-full overflow-hidden">
                     <div className="h-full bg-[#E02020]" style={{ width: `${(simulation.homeWins / simulation.total) * 100}%` }} />
                     <div className="h-full bg-neutral-400" style={{ width: `${(simulation.draws / simulation.total) * 100}%` }} />
                     <div className="h-full bg-emerald-600" style={{ width: `${(simulation.awayWins / simulation.total) * 100}%` }} />
                   </div>
                 </div>
               ) : (
                 <div className="py-12 text-center border-4 border-dashed border-[#1A1A1A]/5 flex flex-col items-center gap-2">
                   <span className="text-xs font-mono font-black opacity-30 uppercase">Run engine to see probabilities</span>
                 </div>
               )}
            </section>

            {/* xG Model (Moved down) */}
            <section className="bg-white border-2 border-[#1A1A1A] p-8 shadow-[12px_12px_0px_0px_#1A1A1A]">
               <h3 className="text-xs font-black uppercase mb-8 flex items-center gap-3">
                 <Target className="w-5 h-5" />
                 기대 득점(xG) 및 스코어
               </h3>

               <div className="flex justify-around items-center py-6 border-y border-[#1A1A1A]/5 mb-8">
                 <div className="text-center">
                   <div className="text-[10px] font-mono opacity-40 uppercase mb-1">Exp Home</div>
                   <div className="text-4xl font-black">{prediction.homeXG}</div>
                 </div>
                 <div className="text-4xl font-light opacity-5">/</div>
                 <div className="text-center">
                   <div className="text-[10px] font-mono opacity-40 uppercase mb-1">Exp Away</div>
                   <div className="text-4xl font-black">{prediction.awayXG}</div>
                 </div>
               </div>

               <div className="space-y-4">
                 <span className="text-[10px] font-mono font-black uppercase opacity-40 tracking-[0.2em] mb-2 block">Probable Outcomes</span>
                 {prediction.topScenarios.map((s, i) => (
                   <div key={i} className="flex justify-between items-center p-4 bg-[#F9F9F7] border-l-4 border-[#1A1A1A]">
                     <div className="flex flex-col">
                       <span className="text-[10px] font-black opacity-60 uppercase">{s.label}</span>
                       <span className="text-[9px] font-mono opacity-40">{s.probability}% Chance</span>
                     </div>
                     <span className="text-xl font-mono font-black underline decoration-2 decoration-[#1A1A1A]/10 underline-offset-4">{s.home} : {s.away}</span>
                   </div>
                 ))}
               </div>
            </section>

            {/* Simulation Results (Moved down and simplified) */}
            <section className={cn(
               "bg-white border-2 border-[#1A1A1A] p-8 shadow-[12px_12px_0px_0px_#1A1A1A] transition-all",
               activeTab === "output" ? "scale-100 opacity-100" : "opacity-30 blur-[2px] grayscale"
            )}>
               <h3 className="text-sm font-black uppercase mb-6 flex items-center gap-3">
                 <BarChart3 className="w-5 h-5" />
                 시뮬레이션 상세
               </h3>
               
               <div className="text-[9px] font-mono text-[#1A1A1A]/40 uppercase leading-tight italic mb-8">
                 ※ {simCount.toLocaleString()}회 반복 실험 기반 가능성 분포입니다.
               </div>

               {simulation && (
                 <div className="grid grid-cols-2 gap-4">
                   <div className="p-4 bg-neutral-50 border border-neutral-100 flex flex-col">
                     <span className="text-[9px] font-mono opacity-40 uppercase">Sample Count</span>
                     <span className="text-xl font-black">{simulation.total.toLocaleString()}</span>
                   </div>
                   <div className="p-4 bg-neutral-50 border border-neutral-100 flex flex-col">
                     <span className="text-[9px] font-mono opacity-40 uppercase">Reliability</span>
                     <span className="text-xl font-black text-emerald-600">High</span>
                   </div>
                 </div>
               )}
            </section>

            {/* Time Distribution (New Req) */}
            <section className={cn(
               "bg-white border-2 border-[#1A1A1A] p-8 shadow-[12px_12px_0px_0px_#1A1A1A] transition-all",
               activeTab === "output" ? "scale-100 opacity-100" : "opacity-30 blur-[2px] grayscale"
            )}>
               <h3 className="text-sm font-black uppercase mb-6 flex items-center gap-3">
                 <Clock className="w-5 h-5" />
                 시간대별 득점 분석 (10분 간격)
               </h3>
               
               <div className="space-y-4">
                 {simulation ? (
                   Object.keys(simulation.timeDistribution.home).sort((a,b) => parseInt(a) - parseInt(b)).map((bucket) => {
                     const hCount = simulation.timeDistribution.home[bucket];
                     const aCount = simulation.timeDistribution.away[bucket];
                     const total = simulation.total;
                     
                     const hRate = (hCount / total);
                     const aRate = (aCount / total);
                     
                     return (
                       <div key={bucket} className="space-y-2">
                         <div className="flex justify-between text-[10px] font-mono font-black uppercase">
                           <span>{bucket}분</span>
                           <div className="flex gap-4">
                             <span className="text-[#E02020]">KOR: {hRate.toFixed(2)}</span>
                             <span className="text-emerald-700">MEX: {aRate.toFixed(2)}</span>
                           </div>
                         </div>
                         <div className="flex gap-1 h-1.5 w-full bg-neutral-100 rounded-full overflow-hidden">
                           <div className="h-full bg-[#E02020]" style={{ width: `${Math.min(100, hRate * 100)}%` }} />
                           <div className="h-full bg-emerald-600" style={{ width: `${Math.min(100, aRate * 100)}%` }} />
                         </div>
                       </div>
                     );
                   })
                 ) : (
                   <div className="py-8 text-center opacity-20 text-[10px] font-mono uppercase">데이터가 준비되지 않았습니다</div>
                 )}
               </div>
            </section>

            {/* Highlighted Top 3 Impact Variables (Req 4) */}
            <section className="bg-[#E02020] p-8 text-white shadow-[12px_12px_0px_0px_rgba(224,32,32,0.2)]">
               <h3 className="text-xs font-black uppercase mb-6 flex items-center gap-3">
                 <Zap className="w-5 h-5 fill-white" />
                 결과를 바꾼 핵심 변수 TOP 3
               </h3>
               <div className="grid grid-cols-1 gap-4">
                 {prediction.impactVariables.slice(0, 3).map((v, i) => (
                   <div key={i} className="bg-white/10 p-4 border-l-4 border-white">
                     <div className="flex justify-between items-center mb-1">
                       <span className="text-lg font-black uppercase">{v.name}</span>
                       <span className="text-xs font-mono font-bold">Score Δ: {(v.impact*10).toFixed(1)}</span>
                     </div>
                     <p className="text-[11px] opacity-70 leading-snug">{v.description}</p>
                   </div>
                 ))}
               </div>
            </section>

            {/* Variable Contribution Table (Req 3) */}
            <section className="bg-white border-2 border-[#1A1A1A] p-8 shadow-[12px_12px_0px_0px_#1A1A1A]">
               <h3 className="text-xs font-black uppercase mb-8 flex items-center gap-3">
                 <BarChart3 className="w-5 h-5" />
                 변수별 기여도 데이터 테이블
               </h3>
               <div className="overflow-x-auto">
                 <table className="w-full text-left text-[11px]">
                   <thead>
                     <tr className="border-b-2 border-[#1A1A1A] font-black uppercase">
                       <th className="pb-2">변수명</th>
                       <th className="pb-2 text-center">가중치</th>
                       <th className="pb-2 text-center">격차(Δ)</th>
                       <th className="pb-2 text-right">기여도</th>
                     </tr>
                   </thead>
                   <tbody className="divide-y divide-[#1A1A1A]/10">
                     {variables.map((v) => {
                       const impact = (Math.abs(v.homeScore - v.awayScore) * (v.weight / (weightSum || 1))).toFixed(2);
                       return (
                         <tr key={v.id} className="hover:bg-neutral-50">
                           <td className="py-3 font-bold">{v.name}</td>
                           <td className="py-3 text-center font-mono">{v.weight}%</td>
                           <td className="py-3 text-center font-mono">{Math.abs(v.homeScore - v.awayScore)}</td>
                           <td className="py-3 text-right font-mono font-black">{impact}</td>
                         </tr>
                       );
                     })}
                   </tbody>
                 </table>
               </div>
            </section>

            {/* Critical Variables Report (Req 5) - Replaced with the sections above if redundant, but keeping for stylistic consistency if needed. Actually let's remove it to keep UI clean */}

            {/* Reflecive Questions (Req 5) */}
            <section className="bg-white border-2 border-[#1A1A1A] p-8 shadow-[12px_12px_0px_0px_#1A1A1A]">
               <h3 className="text-xs font-black uppercase mb-8 flex items-center gap-3">
                 <BrainCircuit className="w-5 h-5" />
                 모델 설계자를 위한 질문
               </h3>
               <ul className="space-y-6 text-[11px] font-medium leading-relaxed">
                 {[
                   "랭킹 30%, 최근 흐름 10% 모델과 랭킹 10%, 최근 흐름 30% 모델은 무엇이 다를까요?",
                   "가중치를 바꿨더니 승부가 뒤집혔다면 무엇이 맞는 걸까요?",
                   "내 가중치에 한국 응원 편향이 들어갔는지 어떻게 확인할까요?",
                   "확률 35%인 팀이 이기면 모델은 틀린 걸까요?",
                   "한 번 계산한 예상 스코어 1-1과 1만 번 시뮬레이션한 1-1 확률은 무엇이 다를까요?",
                   "예상 스코어 1-1 확률이 14%라면 나머지 86%는 어디로 갔을까요?",
                   "시뮬레이션 횟수를 늘리면 정확해지는 걸까요, 안정적으로 보이는 걸까요?"
                 ].map((q, i) => (
                   <li key={i} className="flex gap-5 group">
                     <span className="text-xl font-mono font-black opacity-10">0{i+1}</span>
                     <span className="group-hover:text-[#E02020] transition-colors border-b border-[#1A1A1A]/10 pb-2 self-end">{q}</span>
                   </li>
                 ))}
               </ul>
            </section>

            {/* Legal / Warning (Req 5) */}
            <div className="bg-[#1A1A1A] text-white/40 p-6 text-[10px] leading-relaxed uppercase font-mono italic space-y-4">
              <div className="flex gap-3">
                <AlertCircle className="w-3 h-3 text-[#E02020] shrink-0" />
                <p>"※ 이 예측은 입력 데이터와 가정에 따른 교육용 모의 결과이며, 실제 경기 결과를 보장하지 않습니다."</p>
              </div>
              <div className="flex gap-3">
                <ShieldCheck className="w-3 h-3 text-emerald-500 shrink-0" />
                <p>"[데이터 부족 경고]: 현재 입력된 변수만으로는 축구의 모든 변수(부상, 날씨, 심판 판정 등)를 담을 수 없으므로 예측 신뢰도가 낮을 수 있습니다."</p>
              </div>
            </div>
          </div>
        </div>

        {/* Global Footer Rail */}
        <footer className="mt-24 pt-10 border-t-4 border-[#1A1A1A] flex flex-col md:flex-row justify-between items-center gap-8 opacity-60 text-[11px] font-mono uppercase font-bold text-center md:text-left">
           <div className="flex gap-8 items-center">
              <span>Predict Engine V5.2.0</span>
              <span className="bg-[#1A1A1A] text-white px-2">Status: Deployed</span>
              <span>Entropy: 0.81</span>
           </div>
           <div>© 2026 Sports Data Transparency Initiative</div>
        </footer>
      </div>

      {/* Full Screen Sim Loader */}
      <AnimatePresence>
        {isSimulating && (
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] bg-[#F0F0EE]/95 backdrop-blur-xl flex flex-col items-center justify-center p-12 overflow-hidden"
          >
            <div className="relative mb-16">
               <motion.div 
                 animate={{ rotate: 360 }}
                 transition={{ repeat: Infinity, duration: 4, ease: "linear" }}
                 className="w-32 h-32 border-4 border-[#1A1A1A]/10 flex items-center justify-center"
               >
                 <div className="w-1 h-1 bg-[#1A1A1A]" />
               </motion.div>
               <motion.div 
                 animate={{ scale: [1, 1.2, 1], opacity: [0.3, 1, 0.3] }}
                 transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }}
                 className="absolute inset-0 flex items-center justify-center"
               >
                 <Zap className="w-12 h-12 text-[#E02020]" />
               </motion.div>
            </div>
            <div className="text-center space-y-4">
               <h3 className="text-4xl md:text-5xl font-black uppercase tracking-tighter">Simulating Reality</h3>
               <p className="text-[11px] font-mono opacity-50 uppercase tracking-[0.5em] font-bold">Executing {simCount.toLocaleString()} Discrete Probabilities...</p>
            </div>
            {/* Progress bar dummy */}
            <div className="mt-16 w-full max-w-sm h-[2px] bg-[#1A1A1A]/5 relative overflow-hidden">
               <motion.div 
                 initial={{ x: "-100%" }} animate={{ x: "100%" }} 
                 transition={{ repeat: Infinity, duration: 1.2, ease: "linear" }}
                 className="absolute inset-0 w-full h-full bg-[#E02020]"
               />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
