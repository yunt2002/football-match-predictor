import type { VercelRequest, VercelResponse } from "@vercel/node";
import { GoogleGenAI } from "@google/genai";

type Variable = {
  name: string;
  homeScore: number;
  awayScore: number;
  weight: number;
};

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    return res.status(500).json({
      error: "GEMINI_API_KEY가 설정되지 않았습니다. Vercel → Settings → Environment Variables에서 추가하세요.",
    });
  }

  const { scenario, variables } = req.body as {
    scenario?: string;
    variables?: Variable[];
  };

  if (!scenario?.trim()) {
    return res.status(400).json({ error: "scenario is required" });
  }

  const prompt = `
당신은 세계적인 축구 전술 분석가이자 데이터 전문가입니다.
사용자가 제안한 '특정 돌발 상황'을 바탕으로 대한민국 vs 멕시코의 월드컵 경기를 시뮬레이션하십시오.

[현재 설정된 핵심 지표]
${(variables ?? [])
  .map(
    (v) =>
      `- ${v.name}: 한국(${v.homeScore}), 멕시코(${v.awayScore}), 중요도(${v.weight}%)`,
  )
  .join("\n")}

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

  const ai = new GoogleGenAI({ apiKey });

  try {
    const interaction = await ai.interactions.create({
      model: "gemini-1.5-flash",
      input: prompt,
    });
    return res.status(200).json({ result: interaction.output_text });
  } catch (error) {
    console.error("Gemini Scenario Error:", error);
    return res.status(500).json({
      error: "AI 시나리오 시뮬레이션에 실패했습니다. AI 모델 연결을 확인하세요.",
    });
  }
}
