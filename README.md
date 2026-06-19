# Football Match Predictor

**Korea vs Mexico** World Cup match prediction simulator — a **Streamlit** educational tool for exploring data-driven football modeling.

Repository: [football-match-predictor](https://github.com/yunt2002/football-match-predictor)

데이터와 가중치 설계를 통해 경기 결과를 추정하고 모델링 과정을 학습하는 **Streamlit** 교육용 시뮬레이터입니다.

원본 React/Vite 앱(`simulator_src/`)을 Python으로 리팩토링한 버전입니다.

## 기능

- 9개 변수 가중치·전력 조정 (실시간 이론적 승률 반영)
- Poisson xG 모델 + 몬테카를로 시뮬레이션 (numpy 벡터화)
- 스코어 히트맵, 레이더/버블 차트, 시간대별 득점
- 프리셋 (균형 / 한국 우세 / 멕시코 우세 / 최근 흐름 중시)
- 민감도 분석, A/B 프리셋 비교, 시뮬레이션 안정성 곡선
- AI 시나리오 & 매치 리포트 (OpenAI GPT 또는 규칙 기반)
- 설정 JSON 내보내기 / 불러오기
- **2026 월드컵 최종 26인 명단** (최신 소속 반영) + API 실시간 갱신
- 팀 선택 시 **전체 명단** 조회
- **반응형 UI** (모바일·태블릿 대응)

## 프로젝트 구조

```
app.py                 # Streamlit UI
match_simulator/
  data.py              # 선수·전적·변수 데이터
  engine.py            # 예측·시뮬레이션 엔진
  charts.py            # Plotly 차트
  presets.py           # 프리셋 정의
  ai.py                # AI 시나리오·리포트
  serialization.py     # JSON import/export
simulator_src/         # 원본 React 앱 (참고용, 실행 불필요)
tests/                 # 단위 테스트
```

## 실행

```powershell
cd d:\ict\test
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

브라우저: http://localhost:8501

## 환경 변수 (선택)

`.env` 파일:

```
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5-mini
API_FOOTBALL_KEY=your_api_key_here
```

- `API_FOOTBALL_KEY` 없음 → **2026 월드컵 정적 데이터** 사용
- `API_FOOTBALL_KEY` 있음 → API로 선수·전적 갱신 (사이드바 **최신 데이터 불러오기**)

## Docker

```bash
docker build -t football-match-predictor .
docker run -p 8501:8501 -e OPENAI_API_KEY=your_key -e OPENAI_MODEL=gpt-5-mini football-match-predictor
```

## 테스트

```powershell
pytest tests/ -v
```

## 주의

※ 교육용 모의 결과이며 실제 경기 결과를 보장하지 않습니다.
