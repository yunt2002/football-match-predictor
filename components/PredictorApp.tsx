"use client";

import PlotlyChart from "@/components/PlotlyChart";
import type {
  Bootstrap,
  Halves,
  Insights,
  PredictResponse,
  Projection,
  SimulateResponse,
  Variable,
} from "@/lib/types";
import { RESULT_LABELS } from "@/lib/types";
import ReactMarkdown from "react-markdown";
import { useCallback, useEffect, useMemo, useState } from "react";

function weightSum(vars: Variable[]) {
  return vars.reduce((s, v) => s + v.weight, 0);
}

function ProbCards({
  home,
  draw,
  away,
  suffix = "",
  ci,
}: {
  home: number;
  draw: number;
  away: number;
  suffix?: string;
  ci?: Record<string, { low: number; high: number }>;
}) {
  const items = [
    { key: "home", label: `🇰🇷 대한민국${suffix}`, value: home, cls: "prob-kor" },
    { key: "draw", label: `🤝 무승부${suffix}`, value: draw, cls: "prob-draw" },
    { key: "away", label: `🇲🇽 멕시코${suffix}`, value: away, cls: "prob-mex" },
  ];
  return (
    <div className="grid grid-cols-3 gap-3">
      {items.map((item) => (
        <div key={item.label} className={`prob-card ${item.cls}`}>
          <div className="prob-label">{item.label}</div>
          <div className="prob-value">{item.value.toFixed(1)}%</div>
          {ci?.[item.key] && (
            <div className="text-[0.65rem] opacity-85">
              ±{ci[item.key].low.toFixed(1)}~{ci[item.key].high.toFixed(1)}%
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function Panel({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <section className={`panel ${className}`}>{children}</section>;
}

export default function PredictorApp() {
  const [bootstrap, setBootstrap] = useState<Bootstrap | null>(null);
  const [variables, setVariables] = useState<Variable[]>([]);
  const [activePreset, setActivePreset] = useState("균형");
  const [predictData, setPredictData] = useState<PredictResponse | null>(null);
  const [simData, setSimData] = useState<SimulateResponse | null>(null);
  const [simCount, setSimCount] = useState(1000);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [teamView, setTeamView] = useState<"both" | "kor" | "mex">("both");
  const [historyView, setHistoryView] = useState<"h2h" | "kor" | "mex">("h2h");
  const [scenario, setScenario] = useState("");
  const [aiResult, setAiResult] = useState<string | null>(null);
  const [report, setReport] = useState<string | null>(null);
  const [aiLoading, setAiLoading] = useState(false);

  const [compareA, setCompareA] = useState("균형");
  const [compareB, setCompareB] = useState("한국 우세");
  const [abData, setAbData] = useState<{ chart: object; predictionA: object; predictionB: object } | null>(null);
  const [sensitivity, setSensitivity] = useState<object[] | null>(null);
  const [stabilityChart, setStabilityChart] = useState<object | null>(null);
  const [actualHome, setActualHome] = useState(0);
  const [actualAway, setActualAway] = useState(0);
  const [compareResult, setCompareResult] = useState<object | null>(null);

  const [whatifTeam, setWhatifTeam] = useState("kor");
  const [whatifPlayer, setWhatifPlayer] = useState("");
  const [whatifMode, setWhatifMode] = useState("out");
  const [whatifOptions, setWhatifOptions] = useState<string[]>([]);

  const [hasAi, setHasAi] = useState(false);
  const [hasReport, setHasReport] = useState(false);
  const [exported, setExported] = useState(false);

  useEffect(() => {
    fetch("/api/bootstrap")
      .then((r) => r.json())
      .then((data: Bootstrap) => {
        setBootstrap(data);
        setVariables(data.variables);
        setCompareA(data.presetNames[0]);
        setCompareB(data.presetNames[1] ?? data.presetNames[0]);
      })
      .catch(() => setError("초기 데이터를 불러오지 못했습니다."))
      .finally(() => setLoading(false));
  }, []);

  const refreshPrediction = useCallback(async (vars: Variable[]) => {
    if (!vars.length) return;
    try {
      const res = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ variables: vars }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "predict failed");
      setPredictData(data);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "예측 API 오류");
    }
  }, []);

  useEffect(() => {
    if (!variables.length) return;
    const t = setTimeout(() => refreshPrediction(variables), 200);
    return () => clearTimeout(t);
  }, [variables, refreshPrediction]);

  useEffect(() => {
    fetch("/api/advanced", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "whatifOptions", team: whatifTeam }),
    })
      .then((r) => r.json())
      .then((d) => {
        setWhatifOptions(d.options ?? []);
        setWhatifPlayer(d.options?.[0] ?? "");
      });
  }, [whatifTeam]);

  const totalWeight = useMemo(() => weightSum(variables), [variables]);
  const prediction = predictData?.prediction ?? null;
  const insights = predictData?.insights ?? null;
  const halves = predictData?.halves ?? null;
  const projection = predictData?.projection ?? null;
  const charts = predictData?.charts ?? {};

  const checklistDone = useMemo(() => {
    let done = 0;
    if (totalWeight === 100) done++;
    if (simData && simCount >= 1000) done++;
    if (hasAi) done++;
    if (hasReport) done++;
    if (exported) done++;
    return done;
  }, [totalWeight, simData, simCount, hasAi, hasReport, exported]);

  const applyPreset = async (name: string) => {
    const res = await fetch("/api/preset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });
    const data = await res.json();
    if (res.ok) {
      setVariables(data.variables);
      setActivePreset(name);
      setSimData(null);
    }
  };

  const normalizeWeights = async () => {
    const res = await fetch("/api/advanced", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "normalize", variables }),
    });
    const data = await res.json();
    if (res.ok) setVariables(data.variables);
  };

  const updateVariable = (id: string, field: "homeScore" | "awayScore" | "weight", value: number) => {
    setVariables((prev) => prev.map((v) => (v.id === id ? { ...v, [field]: value } : v)));
    setActivePreset("사용자 정의");
    setSimData(null);
  };

  const runSimulation = async () => {
    setSimulating(true);
    try {
      const res = await fetch("/api/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ variables, simCount }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      setSimData(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "시뮬레이션 오류");
    } finally {
      setSimulating(false);
    }
  };

  const runAiScenario = async (text?: string) => {
    const s = (text ?? scenario).trim();
    if (!s) return;
    setScenario(s);
    setAiLoading(true);
    try {
      const res = await fetch("/api/ai", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "scenario", variables, scenario: s }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      setAiResult(data.markdown);
      setHasAi(true);
    } catch (e) {
      setAiResult(e instanceof Error ? e.message : "AI 오류");
    } finally {
      setAiLoading(false);
    }
  };

  const runReport = async () => {
    setAiLoading(true);
    try {
      const res = await fetch("/api/ai", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "report", variables }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error);
      setReport(data.markdown);
      setHasReport(true);
    } catch (e) {
      setReport(e instanceof Error ? e.message : "리포트 오류");
    } finally {
      setAiLoading(false);
    }
  };

  const exportJson = () => {
    const payload = { version: "1.0", preset: activePreset, sim_count: simCount, variables: variables.map((v) => ({ id: v.id, name: v.name, description: v.description, question: v.question, home_score: v.homeScore, away_score: v.awayScore, weight: v.weight })) };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "match_simulator_config.json";
    a.click();
    setExported(true);
  };

  const historyMatches = useMemo(() => {
    if (!bootstrap) return [];
    if (historyView === "h2h") return bootstrap.footballData.h2hMatches;
    if (historyView === "kor") return bootstrap.footballData.korea.recentMatches;
    return bootstrap.footballData.mexico.recentMatches;
  }, [bootstrap, historyView]);

  if (loading) return <div className="p-8 text-center">⚽ Football Match Predictor 로딩 중…</div>;

  return (
    <div className="min-h-screen">
      <header className="p-4 md:p-6 border-b bg-white">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-start max-w-[1600px] mx-auto">
          <div className="md:col-span-2">
            <p className="sub-title">Computational Sports Modeling</p>
            <h1 className="main-title">⚽ Football Match Predictor</h1>
            <p className="text-sm text-gray-600">Korea vs Mexico · World Cup 2026 · KOR-MEX-2026-MC</p>
          </div>
          <Panel className="text-center !p-3">
            <div className="text-xs text-gray-500">가중치 합계</div>
            <div className="text-2xl font-bold">{totalWeight}%</div>
            <div className="text-xs">{totalWeight === 100 ? "정상" : "조정 필요"}</div>
          </Panel>
          <Panel className="text-center !p-3">
            <div className="text-xs text-gray-500">경기 전 체크</div>
            <div className="text-2xl font-bold">{checklistDone}/5</div>
            <div className="text-xs">{activePreset}</div>
          </Panel>
        </div>
      </header>

      <div className="flex flex-col xl:flex-row max-w-[1600px] mx-auto">
        <aside className="sidebar xl:max-h-[calc(100vh-120px)]">
          <h2 className="text-lg font-bold mb-2">⚙️ 설정</h2>
          {insights && (
            <>
              <h3 className="text-sm font-semibold mt-3 mb-1">🏟️ 경기 정보</h3>
              {Object.entries(insights.match_info).map(([k, v]) => (
                <p key={k} className="text-xs text-gray-600 mb-0.5"><strong>{k}</strong> · {v}</p>
              ))}
              <h3 className="text-sm font-semibold mt-3 mb-1">📊 모델 스냅샷</h3>
              <p className="text-sm font-bold">{insights.favored} ({insights.favored_prob}%)</p>
              <p className="text-xs">유력 스코어 {insights.likely_score} · xG {prediction?.homeXg}:{prediction?.awayXg}</p>
              <p className="text-xs">신뢰도 {insights.confidence}% ({insights.confidence_label})</p>
              <p className="text-xs text-gray-600">핵심: {insights.top_impact}</p>
            </>
          )}
          <hr className="my-3" />
          <h3 className="text-sm font-semibold mb-2">프리셋</h3>
          <div className="space-y-1">
            {(bootstrap?.presetNames ?? []).map((name) => (
              <button key={name} type="button" onClick={() => applyPreset(name)} className={`w-full rounded px-2 py-1.5 text-sm border ${activePreset === name ? "bg-[#1A1A1A] text-white" : "bg-white"}`}>{name}</button>
            ))}
          </div>
          <button type="button" onClick={() => bootstrap && applyPreset("균형")} className="w-full mt-2 text-sm border rounded py-1.5">초기값 리셋</button>
          <hr className="my-3" />
          <button type="button" onClick={exportJson} className="w-full text-sm border rounded py-1.5 mb-2">JSON 다운로드</button>
          <input type="file" accept=".json" className="text-xs w-full" onChange={async (e) => {
            const file = e.target.files?.[0];
            if (!file) return;
            try {
              const raw = JSON.parse(await file.text());
              setVariables(raw.variables.map((v: Record<string, unknown>) => ({ id: v.id, name: v.name, description: v.description, question: v.question, homeScore: v.home_score, awayScore: v.away_score, weight: v.weight })));
              if (raw.sim_count) setSimCount(raw.sim_count);
              if (raw.preset) setActivePreset(raw.preset);
              setExported(true);
            } catch { setError("JSON 불러오기 실패"); }
          }} />
          <hr className="my-3" />
          <h3 className="text-sm font-semibold mb-1">⚡ 빠른 AI 시나리오</h3>
          {(bootstrap?.quickScenarios ?? []).slice(0, 3).map((text) => (
            <button key={text} type="button" onClick={() => runAiScenario(text)} className="w-full text-left text-xs border rounded px-2 py-1 mb-1">{text}</button>
          ))}
          <details className="mt-2 text-xs">
            <summary>📖 용어 설명</summary>
            {bootstrap && Object.entries(bootstrap.glossary).map(([t, d]) => <p key={t} className="mt-1"><strong>{t}</strong> — {d}</p>)}
          </details>
        </aside>

        <main className="flex-1 p-4 grid grid-cols-1 lg:grid-cols-[1.4fr_1fr] gap-4">
          <div className="space-y-4">
            {error && <Panel className="bg-red-50 text-red-700 text-sm">{error}</Panel>}

            <Panel>
              <h2 className="font-bold mb-2">🏆 A조 순위 &amp; 다음 경기</h2>
              <p className="text-sm bg-blue-50 p-2 rounded mb-2">{bootstrap?.nextMatchBanner.replace(/\*\*/g, "")}</p>
              <table className="w-full text-sm mb-2">
                <thead><tr className="border-b"><th className="text-left py-1">순위</th><th>팀</th><th>승점</th><th>득실</th></tr></thead>
                <tbody>
                  {bootstrap?.standings.map((row, i) => (
                    <tr key={row.code} className="border-b border-gray-100"><td>{i + 1}</td><td>{row.team}</td><td>{row.pts}</td><td>{row.gf - row.ga}</td></tr>
                  ))}
                </tbody>
              </table>
              {projection && <div className="text-xs space-y-0.5"><p>· {projection.ifKorWin}</p><p>· {projection.ifDraw}</p><p>· {projection.ifMexWin}</p></div>}
            </Panel>

            <Panel>
              <h2 className="font-bold mb-2">📋 전력 &amp; 전적</h2>
              <div className="flex gap-2 mb-3 text-sm">
                {(["both", "kor", "mex"] as const).map((t) => (
                  <button key={t} type="button" onClick={() => setTeamView(t)} className={`px-2 py-1 rounded border ${teamView === t ? "bg-gray-900 text-white" : ""}`}>{t === "both" ? "양팀" : t === "kor" ? "🇰🇷" : "🇲🇽"}</button>
                ))}
              </div>
              <div className="overflow-x-auto max-h-64 text-sm">
                <table className="w-full">
                  <thead><tr className="border-b"><th>선수</th><th>포지션</th><th>클럽</th><th>레이팅</th></tr></thead>
                  <tbody>
                    {(teamView === "both" ? [...(bootstrap?.footballData.korea.players.slice(0, 5) ?? []), ...(bootstrap?.footballData.mexico.players.slice(0, 5) ?? [])] : teamView === "kor" ? bootstrap?.footballData.korea.players : bootstrap?.footballData.mexico.players)?.map((p) => (
                      <tr key={p.id} className="border-b border-gray-50"><td>{p.name}</td><td>{p.position}</td><td>{p.club}</td><td>{p.rating}</td></tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="flex gap-2 mt-3 text-xs">
                {(["h2h", "kor", "mex"] as const).map((v) => (
                  <button key={v} type="button" onClick={() => setHistoryView(v)} className={`px-2 py-1 rounded border ${historyView === v ? "bg-gray-200" : ""}`}>{v === "h2h" ? "H2H" : v === "kor" ? "한국" : "멕시코"}</button>
                ))}
              </div>
              <table className="w-full text-xs mt-2">
                <thead><tr className="border-b"><th>날짜</th><th>대회</th><th>스코어</th><th>결과</th></tr></thead>
                <tbody>
                  {historyMatches.map((m) => (
                    <tr key={m.id} className="border-b border-gray-50"><td>{m.date}</td><td>{m.competition}</td><td>{m.score}</td><td>{RESULT_LABELS[m.result] ?? m.result}</td></tr>
                  ))}
                </tbody>
              </table>
              <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
                <select value={whatifTeam} onChange={(e) => setWhatifTeam(e.target.value)} className="border rounded p-1"><option value="kor">🇰🇷 한국</option><option value="mex">🇲🇽 멕시코</option></select>
                <select value={whatifPlayer} onChange={(e) => setWhatifPlayer(e.target.value)} className="border rounded p-1">{whatifOptions.map((o) => <option key={o}>{o}</option>)}</select>
                <select value={whatifMode} onChange={(e) => setWhatifMode(e.target.value)} className="border rounded p-1"><option value="out">부재</option><option value="boost">부스트</option></select>
              </div>
              <button type="button" className="mt-2 text-xs border rounded px-2 py-1" onClick={async () => {
                const res = await fetch("/api/advanced", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action: "whatif", variables, team: whatifTeam, player: whatifPlayer, mode: whatifMode }) });
                const d = await res.json();
                if (res.ok) setVariables(d.variables);
              }}>What-if 적용</button>
            </Panel>

            <Panel>
              <div className="flex justify-between items-center mb-2">
                <h2 className="font-bold">1. 전력 모델 파라미터</h2>
                <button type="button" onClick={normalizeWeights} className="text-xs border rounded px-2 py-1">가중치 100% 정규화</button>
              </div>
              {variables.map((v) => (
                <details key={v.id} className="mb-3 border-b pb-2">
                  <summary className="font-semibold text-sm cursor-pointer">{v.name} (가중치 {v.weight}%)</summary>
                  <p className="text-xs text-gray-500">{v.question}</p>
                  <p className="text-xs bg-gray-50 p-1 rounded my-1">{v.description}</p>
                  <label className="text-xs block">가중치 {v.weight}%<input type="range" min={0} max={100} value={v.weight} onChange={(e) => updateVariable(v.id, "weight", Number(e.target.value))} className="w-full" /></label>
                  <div className="grid grid-cols-2 gap-2">
                    <label className="text-xs">🇰🇷 {v.homeScore}<input type="range" min={0} max={100} value={v.homeScore} onChange={(e) => updateVariable(v.id, "homeScore", Number(e.target.value))} className="w-full" /></label>
                    <label className="text-xs">🇲🇽 {v.awayScore}<input type="range" min={0} max={100} value={v.awayScore} onChange={(e) => updateVariable(v.id, "awayScore", Number(e.target.value))} className="w-full" /></label>
                  </div>
                </details>
              ))}
            </Panel>

            <Panel>
              <h2 className="font-bold mb-2">2. 몬테카를로 시뮬레이션</h2>
              <select value={simCount} onChange={(e) => setSimCount(Number(e.target.value))} className="border rounded p-1 text-sm mb-2">
                {[10, 100, 1000, 10000].map((n) => <option key={n} value={n}>{n.toLocaleString()}회</option>)}
              </select>
              <button type="button" onClick={runSimulation} disabled={simulating} className="ml-2 rounded bg-[#E02020] text-white px-4 py-1.5 text-sm disabled:opacity-50">{simulating ? "실행 중…" : "시뮬레이션 실행"}</button>
            </Panel>

            <Panel>
              <h2 className="font-bold mb-2">3. AI 시나리오</h2>
              <textarea value={scenario} onChange={(e) => setScenario(e.target.value)} rows={3} className="w-full border rounded p-2 text-sm" placeholder="예: 손흥민이 전반 10분에 부상 퇴장…" />
              <button type="button" onClick={() => runAiScenario()} disabled={aiLoading} className="mt-2 rounded bg-[#1A1A1A] text-white px-4 py-1.5 text-sm">AI 시나리오 가동</button>
              {aiResult && <div className="prose prose-sm max-w-none mt-3 border-t pt-3"><ReactMarkdown>{aiResult}</ReactMarkdown></div>}
            </Panel>

            <Panel>
              <h2 className="font-bold mb-2">4. 매치 리포트</h2>
              <button type="button" onClick={runReport} disabled={aiLoading} className="rounded bg-[#059669] text-white px-4 py-1.5 text-sm">리포트 생성</button>
              {report && <div className="prose prose-sm max-w-none mt-3 border-t pt-3"><ReactMarkdown>{report}</ReactMarkdown></div>}
            </Panel>

            <Panel>
              <h2 className="font-bold mb-2">🔬 고급 분석</h2>
              <details className="mb-2"><summary className="cursor-pointer text-sm">민감도 분석</summary>
                <button type="button" className="text-xs border rounded px-2 py-1 mt-1" onClick={async () => {
                  const r = await fetch("/api/advanced", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action: "sensitivity", variables }) });
                  setSensitivity((await r.json()).rows);
                }}>실행</button>
                {sensitivity && <pre className="text-xs overflow-auto mt-2 bg-gray-50 p-2 rounded">{JSON.stringify(sensitivity, null, 2)}</pre>}
              </details>
              <details className="mb-2"><summary className="cursor-pointer text-sm">A/B 프리셋 비교</summary>
                <div className="flex gap-2 mt-1 text-sm">
                  <select value={compareA} onChange={(e) => setCompareA(e.target.value)}>{bootstrap?.presetNames.map((n) => <option key={n}>{n}</option>)}</select>
                  <select value={compareB} onChange={(e) => setCompareB(e.target.value)}>{bootstrap?.presetNames.map((n) => <option key={n}>{n}</option>)}</select>
                  <button type="button" className="text-xs border rounded px-2" onClick={async () => {
                    const r = await fetch("/api/advanced", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action: "abCompare", presetA: compareA, presetB: compareB }) });
                    setAbData(await r.json());
                  }}>비교</button>
                </div>
                {abData?.chart && <PlotlyChart data={abData.chart} className="h-[300px] mt-2" />}
              </details>
              <details><summary className="cursor-pointer text-sm">안정성 곡선</summary>
                <button type="button" className="text-xs border rounded px-2 py-1 mt-1" onClick={async () => {
                  const r = await fetch("/api/advanced", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action: "stability", variables }) });
                  const d = await r.json();
                  setStabilityChart(d.chart);
                }}>실행</button>
                {stabilityChart && <PlotlyChart data={stabilityChart} className="h-[280px] mt-2" />}
              </details>
            </Panel>
          </div>

          <div className="space-y-4 lg:sticky lg:top-4 lg:self-start">
            <Panel>
              <h2 className="font-bold mb-2">📊 실시간 예측</h2>
              {prediction && (
                <>
                  <p className="text-sm mb-2">이론적 승률 (xG 모델)</p>
                  <ProbCards home={prediction.homeWinProb} draw={prediction.drawProb} away={prediction.awayWinProb} />
                  {charts.probStackedBar && <PlotlyChart data={charts.probStackedBar} className="h-[180px] mt-2" />}
                  <div className="grid grid-cols-3 gap-2 text-sm mt-3">
                    <div className="bg-gray-50 rounded p-2 text-center"><div className="text-xs">🇰🇷 xG</div><div className="font-bold">{prediction.homeXg}</div></div>
                    <div className="bg-gray-50 rounded p-2 text-center"><div className="text-xs">🇲🇽 xG</div><div className="font-bold">{prediction.awayXg}</div></div>
                    <div className="bg-gray-50 rounded p-2 text-center"><div className="text-xs">전력</div><div className="font-bold">{prediction.homeTeamScore} vs {prediction.awayTeamScore}</div></div>
                  </div>
                  {halves && (
                    <div className="mt-4">
                      <p className="text-sm font-semibold mb-2">⏱️ 전반 / 후반 분리 예측</p>
                      <div className="grid grid-cols-3 gap-2 text-xs">
                        {([["전반", halves.first_half], ["후반", halves.second_half], ["풀타임", halves.full_time]] as const).map(([label, h]) => (
                          <div key={label} className="bg-gray-50 rounded p-2"><div className="font-semibold">{label}</div><div>xG {h.home_xg}:{h.away_xg}</div><div>🇰🇷 {h.home_win}% · 무 {h.draw}% · 🇲🇽 {h.away_win}%</div></div>
                        ))}
                      </div>
                    </div>
                  )}
                  <ul className="text-sm mt-3 space-y-1">
                    {prediction.topScenarios.map((s) => <li key={s.label}>{s.label}: <strong>{s.home}:{s.away}</strong> ({s.probability}%)</li>)}
                  </ul>
                  {charts.scoreHeatmap && <PlotlyChart data={charts.scoreHeatmap} className="h-[360px] mt-2" />}
                  <div className="mt-2 text-sm">
                    <p className="font-semibold">핵심 변수 TOP 3</p>
                    {prediction.impactVariables.map((imp, i) => <p key={imp.name} className="text-xs">{i + 1}. {imp.name} — {imp.description}</p>)}
                  </div>
                  {charts.variableRadar && <PlotlyChart data={charts.variableRadar} className="h-[400px]" />}
                  {charts.contributionBubble && <PlotlyChart data={charts.contributionBubble} className="h-[360px]" />}
                </>
              )}
            </Panel>

            {simData && (
              <Panel>
                <h2 className="font-bold mb-2">🎲 시뮬레이션 결과</h2>
                <ProbCards
                  home={(simData.simulation.homeWins / simData.simulation.total) * 100}
                  draw={(simData.simulation.draws / simData.simulation.total) * 100}
                  away={(simData.simulation.awayWins / simData.simulation.total) * 100}
                  suffix=" (MC)"
                  ci={simData.confidenceIntervals}
                />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2">
                  {simData.charts.probDonut && <PlotlyChart data={simData.charts.probDonut} className="h-[320px]" />}
                  {simData.charts.scoreHeatmap && <PlotlyChart data={simData.charts.scoreHeatmap} className="h-[320px]" />}
                </div>
                {simData.charts.timeDistribution && <PlotlyChart data={simData.charts.timeDistribution} className="h-[340px]" />}
                <table className="w-full text-xs mt-2"><thead><tr className="border-b"><th>스코어</th><th>횟수</th><th>확률</th></tr></thead>
                  <tbody>{simData.topScores.map((r) => <tr key={r.score} className="border-b"><td>{r.score}</td><td>{r.count}</td><td>{r.probability}%</td></tr>)}</tbody>
                </table>
              </Panel>
            )}

            <Panel>
              <h2 className="font-bold mb-2">📈 예측 vs 실제</h2>
              <div className="flex gap-2 text-sm mb-2">
                <label>🇰🇷 <input type="number" min={0} max={15} value={actualHome} onChange={(e) => setActualHome(Number(e.target.value))} className="w-16 border rounded ml-1" /></label>
                <label>🇲🇽 <input type="number" min={0} max={15} value={actualAway} onChange={(e) => setActualAway(Number(e.target.value))} className="w-16 border rounded ml-1" /></label>
              </div>
              <button type="button" className="text-sm border rounded px-3 py-1" onClick={async () => {
                const r = await fetch("/api/advanced", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action: "compareActual", variables, actualHome, actualAway, includeSimulation: !!simData, simCount }) });
                setCompareResult(await r.json());
              }}>실제 결과 비교</button>
              {compareResult && <pre className="text-xs mt-2 bg-gray-50 p-2 rounded whitespace-pre-wrap">{JSON.stringify(compareResult, null, 2)}</pre>}
            </Panel>
          </div>
        </main>
      </div>
      <footer className="text-center text-xs text-gray-500 py-4">© 2026 Sports Data Transparency Initiative · Predict Engine V5.2.0 (Vercel/Next.js)</footer>
    </div>
  );
}
