"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import type { Bootstrap, Halves, Insights, Prediction, Projection, Variable } from "@/lib/types";

function weightSum(vars: Variable[]) {
  return vars.reduce((s, v) => s + v.weight, 0);
}

function ProbCards({
  home,
  draw,
  away,
  suffix = "",
}: {
  home: number;
  draw: number;
  away: number;
  suffix?: string;
}) {
  const items = [
    { label: `🇰🇷 대한민국${suffix}`, value: home, cls: "prob-kor" },
    { label: `🤝 무승부${suffix}`, value: draw, cls: "prob-draw" },
    { label: `🇲🇽 멕시코${suffix}`, value: away, cls: "prob-mex" },
  ];
  return (
    <div className="grid grid-cols-3 gap-3">
      {items.map((item) => (
        <div key={item.label} className={`prob-card ${item.cls}`}>
          <div className="prob-label">{item.label}</div>
          <div className="prob-value">{item.value.toFixed(1)}%</div>
        </div>
      ))}
    </div>
  );
}

export default function HomePage() {
  const [bootstrap, setBootstrap] = useState<Bootstrap | null>(null);
  const [variables, setVariables] = useState<Variable[]>([]);
  const [activePreset, setActivePreset] = useState("균형");
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [insights, setInsights] = useState<Insights | null>(null);
  const [halves, setHalves] = useState<Halves | null>(null);
  const [projection, setProjection] = useState<Projection | null>(null);
  const [simCount, setSimCount] = useState(1000);
  const [simulation, setSimulation] = useState<{
    homeWins: number;
    draws: number;
    awayWins: number;
    total: number;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/bootstrap")
      .then((r) => r.json())
      .then((data: Bootstrap) => {
        setBootstrap(data);
        setVariables(data.variables);
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
      setPrediction(data.prediction);
      setInsights(data.insights);
      setHalves(data.halves);
      setProjection(data.projection);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "예측 API 오류");
    }
  }, []);

  useEffect(() => {
    if (!variables.length) return;
    const t = setTimeout(() => refreshPrediction(variables), 250);
    return () => clearTimeout(t);
  }, [variables, refreshPrediction]);

  const totalWeight = useMemo(() => weightSum(variables), [variables]);

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
    }
  };

  const updateVariable = (id: string, field: "homeScore" | "awayScore" | "weight", value: number) => {
    setVariables((prev) => prev.map((v) => (v.id === id ? { ...v, [field]: value } : v)));
    setActivePreset("사용자 정의");
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
      if (!res.ok) throw new Error(data.error || "simulate failed");
      setSimulation(data.simulation);
    } catch (e) {
      setError(e instanceof Error ? e.message : "시뮬레이션 오류");
    } finally {
      setSimulating(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center">⚽ Football Match Predictor 로딩 중…</div>;
  }

  return (
    <div className="layout flex min-h-screen">
      <aside className="sidebar">
        <h2 className="text-lg font-bold mb-2">⚙️ 설정</h2>

        {insights && (
          <>
            <h3 className="text-sm font-semibold mt-4 mb-2">🏟️ 경기 정보</h3>
            {Object.entries(insights.match_info).map(([k, v]) => (
              <p key={k} className="text-xs text-gray-600 mb-1">
                <strong>{k}</strong> · {v}
              </p>
            ))}

            <hr className="my-4" />

            <h3 className="text-sm font-semibold mb-2">📊 모델 스냅샷</h3>
            <div className="text-sm space-y-2">
              <div>
                <div className="text-gray-500 text-xs">유력 결과</div>
                <div className="font-bold">{insights.favored} ({insights.favored_prob}%)</div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <div className="text-gray-500 text-xs">유력 스코어</div>
                  <div className="font-bold">{insights.likely_score}</div>
                </div>
                <div>
                  <div className="text-gray-500 text-xs">xG</div>
                  <div className="font-bold">
                    {prediction?.homeXg} : {prediction?.awayXg}
                  </div>
                </div>
              </div>
              <div>
                <div className="text-gray-500 text-xs">모델 신뢰도</div>
                <div className="font-bold">
                  {insights.confidence}% ({insights.confidence_label})
                </div>
              </div>
              <p className="text-xs text-gray-600">편향: {insights.bias_label}</p>
              <p className="text-xs text-gray-600">핵심 변수: {insights.top_impact}</p>
            </div>

            <hr className="my-4" />

            <h3 className="text-sm font-semibold mb-2">⚔️ 팀 전력 비교</h3>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>🇰🇷 {insights.kor_rating}</div>
              <div>🇲🇽 {insights.mex_rating}</div>
            </div>
            <p className="text-xs text-gray-600 mt-2">
              최근 승률 — 🇰🇷 {insights.kor_form}% · 🇲🇽 {insights.mex_form}%
            </p>
            <p className="text-xs text-gray-600">{insights.h2h}</p>
          </>
        )}

        <hr className="my-4" />
        <h3 className="text-sm font-semibold mb-2">프리셋</h3>
        <div className="space-y-2">
          {(bootstrap?.presetNames ?? []).map((name) => (
            <button
              key={name}
              type="button"
              onClick={() => applyPreset(name)}
              className={`w-full rounded px-3 py-2 text-sm border ${
                activePreset === name ? "bg-[#1A1A1A] text-white" : "bg-white"
              }`}
            >
              {name}
            </button>
          ))}
        </div>
      </aside>

      <main className="flex-1 p-4 md:p-6 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-start">
          <div className="md:col-span-2">
            <p className="sub-title">Computational Sports Modeling</p>
            <h1 className="main-title">⚽ Football Match Predictor</h1>
            <p className="text-sm text-gray-600">Korea vs Mexico · World Cup 2026 · KOR-MEX-2026-MC</p>
          </div>
          <div className="panel text-center">
            <div className="text-xs text-gray-500">가중치 합계</div>
            <div className="text-2xl font-bold">{totalWeight}%</div>
            <div className="text-xs">{totalWeight === 100 ? "정상" : "조정 필요"}</div>
          </div>
          <div className="panel text-center">
            <div className="text-xs text-gray-500">프리셋</div>
            <div className="text-lg font-bold">{activePreset}</div>
          </div>
        </div>

        {error && <div className="panel bg-red-50 text-red-700 text-sm">{error}</div>}

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
          <section className="panel space-y-4">
            <h2 className="font-bold text-lg">📈 실시간 예측</h2>
            {prediction && (
              <>
                <ProbCards
                  home={prediction.homeWinProb}
                  draw={prediction.drawProb}
                  away={prediction.awayWinProb}
                />
                <div className="stack-bar">
                  <span style={{ width: `${prediction.homeWinProb}%` }} />
                  <span style={{ width: `${prediction.drawProb}%` }} />
                  <span style={{ width: `${prediction.awayWinProb}%` }} />
                </div>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div className="panel bg-gray-50">
                    <div className="text-xs text-gray-500">🇰🇷 xG</div>
                    <div className="text-xl font-bold">{prediction.homeXg}</div>
                  </div>
                  <div className="panel bg-gray-50">
                    <div className="text-xs text-gray-500">🇲🇽 xG</div>
                    <div className="text-xl font-bold">{prediction.awayXg}</div>
                  </div>
                </div>
                <div>
                  <h3 className="text-sm font-semibold mb-2">유력 스코어</h3>
                  <ul className="text-sm space-y-1">
                    {prediction.topScenarios.slice(0, 3).map((s) => (
                      <li key={s.label}>
                        {s.label}: {s.home} : {s.away} ({s.probability}%)
                      </li>
                    ))}
                  </ul>
                </div>
              </>
            )}
          </section>

          <section className="panel space-y-3">
            <h2 className="font-bold text-lg">🏆 A조 순위 &amp; 다음 경기</h2>
            {bootstrap && (
              <>
                <p
                  className="text-sm bg-blue-50 p-2 rounded"
                  dangerouslySetInnerHTML={{ __html: bootstrap.nextMatchBanner.replace(/\*\*/g, "") }}
                />
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b text-left">
                        <th className="py-1">순위</th>
                        <th>팀</th>
                        <th>승점</th>
                        <th>득실</th>
                      </tr>
                    </thead>
                    <tbody>
                      {bootstrap.standings.map((row, i) => (
                        <tr key={row.code} className="border-b border-gray-100">
                          <td className="py-1">{i + 1}</td>
                          <td>{row.team}</td>
                          <td>{row.pts}</td>
                          <td>{row.gf - row.ga}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {projection && (
                  <div className="text-xs text-gray-700 space-y-1">
                    <p>
                      현재 — 🇰🇷 {projection.currentRankKor}위 · 🇲🇽 {projection.currentRankMex}위
                    </p>
                    <p>· {projection.ifKorWin}</p>
                    <p>· {projection.ifDraw}</p>
                    <p>· {projection.ifMexWin}</p>
                  </div>
                )}
              </>
            )}
          </section>
        </div>

        {halves && (
          <section className="panel">
            <h2 className="font-bold text-lg mb-3">⏱️ 전반 / 후반 분리 예측</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
              {(
                [
                  ["전반 (45분)", halves.first_half],
                  ["후반 (45분)", halves.second_half],
                  ["풀타임", halves.full_time],
                ] as const
              ).map(([label, h]) => (
                <div key={String(label)} className="panel bg-gray-50">
                  <div className="font-semibold mb-2">{label}</div>
                  <div>
                    xG {h.home_xg} : {h.away_xg}
                  </div>
                  <div className="text-xs mt-1">
                    🇰🇷 {h.home_win}% · 🤝 {h.draw}% · 🇲🇽 {h.away_win}%
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        <section className="panel space-y-4">
          <h2 className="font-bold text-lg">🎛️ 변수 조정</h2>
          <div className="space-y-4">
            {variables.map((v) => (
              <div key={v.id} className="border-b border-gray-100 pb-4">
                <div className="font-semibold text-sm">{v.name}</div>
                <p className="text-xs text-gray-500 mb-2">{v.question}</p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                  <label>
                    🇰🇷 {v.homeScore}
                    <input
                      type="range"
                      min={0}
                      max={100}
                      value={v.homeScore}
                      onChange={(e) => updateVariable(v.id, "homeScore", Number(e.target.value))}
                    />
                  </label>
                  <label>
                    🇲🇽 {v.awayScore}
                    <input
                      type="range"
                      min={0}
                      max={100}
                      value={v.awayScore}
                      onChange={(e) => updateVariable(v.id, "awayScore", Number(e.target.value))}
                    />
                  </label>
                  <label>
                    가중치 {v.weight}%
                    <input
                      type="range"
                      min={0}
                      max={40}
                      value={v.weight}
                      onChange={(e) => updateVariable(v.id, "weight", Number(e.target.value))}
                    />
                  </label>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="panel space-y-3">
          <h2 className="font-bold text-lg">🎲 몬테카를로 시뮬레이션</h2>
          <div className="flex flex-wrap items-center gap-3">
            <label className="text-sm">
              횟수 {simCount}
              <input
                type="range"
                min={500}
                max={5000}
                step={500}
                value={simCount}
                onChange={(e) => setSimCount(Number(e.target.value))}
                className="ml-2 w-40"
              />
            </label>
            <button
              type="button"
              onClick={runSimulation}
              disabled={simulating}
              className="rounded bg-[#E02020] text-white px-4 py-2 text-sm font-semibold disabled:opacity-50"
            >
              {simulating ? "시뮬레이션 중…" : "시뮬레이션 실행"}
            </button>
          </div>
          {simulation && (
            <ProbCards
              home={(simulation.homeWins / simulation.total) * 100}
              draw={(simulation.draws / simulation.total) * 100}
              away={(simulation.awayWins / simulation.total) * 100}
              suffix=" (MC)"
            />
          )}
        </section>
      </main>
    </div>
  );
}
