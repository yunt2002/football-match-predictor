import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import { GoogleGenAI } from "@google/genai";
import dotenv from "dotenv";

dotenv.config();

const app = express();
const PORT = 3000;

app.use(express.json());

const ai = new GoogleGenAI({
  apiKey: process.env.GEMINI_API_KEY || "AI_STUDIO_MANAGED_KEY",
});

// API endpoint for match analysis
app.post("/api/analyze", async (req, res) => {
  const { homeTeam, awayTeam, result } = req.body;

  const prompt = `
당신은 스포츠 데이터 기반 경기 결과 예측 AI입니다. 
다음은 사용자가 입력한 데이터와 계산된 예측 결과입니다.

홈팀: ${homeTeam.name} (${homeTeam.variables.map((v: any) => `${v.name}: 점수 ${v.score}, 가중치 ${v.weight}`).join(", ")})
원정팀: ${awayTeam.name} (${awayTeam.variables.map((v: any) => `${v.name}: 점수 ${v.score}, 가중치 ${v.weight}`).join(", ")})

예측 결과:
- ${homeTeam.name} 승리 확률: ${result.homeWinProb}%
- 무승부 확률: ${result.drawProb}%
- ${awayTeam.name} 승리 확률: ${result.awayWinProb}%
- 예상 득점: ${homeTeam.name} ${result.homeExpScore} / ${awayTeam.name} ${result.awayExpScore}
- 유력 스코어: ${result.mostLikelyScore.home} : ${result.mostLikelyScore.away}

이 데이터를 바탕으로 다음 구조의 마크다운 리포트를 작성하세요.
절대로 응원이나 편향된 감정을 넣지 마세요.

## 📊 매치 예측 리포트: ${homeTeam.name} vs ${awayTeam.name}

### 1. 경기 결과 확률
- 🇰🇷 ${homeTeam.name} 승리: [XX]%
- 🤝 무승부: [XX]%
- 🇲🇽 ${awayTeam.name} 승리: [XX]%

### 2. 예상 득점 및 스코어
- 예상 득점(기대치): ${homeTeam.name} [X.X]골 / ${awayTeam.name} [X.X]골
- 가장 유력한 예상 스코어: [X] : [X] 
*(설명: 득점 기대치를 바탕으로 가장 현실적인 스코어를 추정합니다.)*

### 3. 결과에 영향을 미친 핵심 변수 TOP 3
*(사용자가 부여한 가중치가 높고, 양 팀 간 격차가 큰 변수를 중심으로 3가지를 선정하여 짧게 분석합니다.)*
1. [변수명]: [분석 내용]
2. [변수명]: [분석 내용]
3. [변수명]: [분석 내용]

### 4. ⚠️ 모델의 가정 및 한계 (필수 확인)
- 이 예측은 사용자가 임의로 설정한 변수와 가중치에 기반한 '근거 있는 추정'일 뿐, 미래를 확정하는 정답이 아닙니다.
- [확률의 함정]: 만약 ${homeTeam.name}의 승률이 35%로 예측되었으나 실제 경기에서 승리하더라도, 이는 모델이 틀린 것이 아니라 35%의 확률이 실현된 것입니다.
- [데이터 한계]: 부상, 당일 날씨, 심판 성향 등 수치화하기 힘든 돌발 변수는 현재 모델에 반영되지 않았습니다. 실제 의사결정 시에는 반드시 사람이 데이터 출처와 가정을 교차 검증해야 합니다.

주의: 결과값(확률, 스코어 등)은 반드시 위에서 제공된 '예측 결과' 값과 일치해야 합니다.
`;

  try {
    const interaction = await ai.interactions.create({
      model: "gemini-1.5-flash",
      input: prompt,
    });
    res.json({ report: interaction.output_text });
  } catch (error: any) {
    console.error("Gemini Error:", error);
    res.status(500).json({ error: "분석 리포트 생성에 실패했습니다. AI 모델 연결을 확인하세요." });
  }
});

// AI Scenario Simulation Endpoint
app.post("/api/ai-scenario-simulate", async (req, res) => {
  const { scenario, variables, homeTeam, awayTeam } = req.body;

  const prompt = `
당신은 세계적인 축구 전술 분석가이자 데이터 전문가입니다.
사용자가 제안한 '특정 돌발 상황'을 바탕으로 대한민국 vs 멕시코의 월드컵 경기를 시뮬레이션하십시오.

[현재 설정된 핵심 지표]
${variables.map((v: any) => `- ${v.name}: 한국(${v.homeScore}), 멕시코(${v.awayScore}), 중요도(${v.weight}%)`).join("\n")}

[부여된 특정 상황/시나리오]
"${scenario}"

위 상황이 발생했을 때, 경기의 흐름이 어떻게 바뀔지 논리적으로 추론하여 다음 구조로 답변하세요.

## 🤖 AI 시나리오 시뮬레이션 결과

### 1. 전술적 영향 분석
- 부여된 상황이 양 팀의 전술에 미치는 구체적인 영향 (가중치 변동 포함)

### 2. 경기 흐름 및 결정적 장면
- 해당 시나리오에서 발생할 수 있는 구체적인 경기 상황 묘사

### 3. 최종 예측 결과 (수정된 확률)
- 🇰🇷 한국 승리: [XX]%
- 🤝 무승부: [XX]%
- 🇲🇽 멕시코 승리: [XX]%
- 예상 최종 스코어: [X] : [X]

### 4. 분석 결과 총평
- 전문적인 시각에서의 한 줄 요약

주의: 사용자가 입력한 상황을 최대한 진지하게 분석에 반영하십시오.
`;

  try {
    const interaction = await ai.interactions.create({
      model: "gemini-1.5-flash",
      input: prompt,
    });
    res.json({ result: interaction.output_text });
  } catch (error: any) {
    console.error("Gemini Scenario Error:", error);
    res.status(500).json({ error: "AI 시나리오 시뮬레이션에 실패했습니다. AI 모델 연결을 확인하세요." });
  }
});

async function startServer() {
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
