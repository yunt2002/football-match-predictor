# GitHub + Streamlit Community Cloud 배포 가이드

다른 Streamlit 프로젝트에도 **동일한 순서**로 적용할 수 있는 체크리스트입니다.

> **참고 프로젝트:** [football-match-predictor](https://github.com/yunt2002/football-match-predictor)

---

## 목차

1. [사전 준비](#1-사전-준비)
2. [프로젝트 Cloud 배포 준비](#2-프로젝트-cloud-배포-준비)
3. [GitHub에 코드 올리기](#3-github에-코드-올리기)
4. [Streamlit Community Cloud 배포](#4-streamlit-community-cloud-배포)
5. [배포 후 업데이트](#5-배포-후-업데이트)
6. [문제 해결](#6-문제-해결)
7. [새 프로젝트 빠른 체크리스트](#7-새-프로젝트-빠른-체크리스트)

---

## 1. 사전 준비

### 1-1. 설치

| 도구 | 용도 | 설치 |
|------|------|------|
| **Git** | 버전 관리 | [git-scm.com](https://git-scm.com/) |
| **GitHub CLI (`gh`)** | 저장소 생성·로그인 | `winget install GitHub.cli` |
| **Python 3.12+** | Streamlit 실행 | python.org |
| **GitHub 계정** | 코드 호스팅 | github.com |

### 1-2. PATH 확인 (Windows)

PowerShell에서 Git이 안 잡히면:

```powershell
$env:Path = "C:\Program Files\Git\cmd;C:\Program Files\GitHub CLI;" + $env:Path
git --version
gh --version
```

### 1-3. GitHub 로그인 (최초 1회)

```powershell
gh auth login -h github.com -p https -w
```

브라우저에서 디바이스 코드 입력 → `Logged in as <username>` 확인.

---

## 2. 프로젝트 Cloud 배포 준비

Streamlit Cloud는 **GitHub 저장소**에서 코드를 가져옵니다. 아래 파일을 프로젝트 루트에 맞춰 준비하세요.

### 2-1. 필수 파일 구조

```
my-project/
├── app.py                 # ← Streamlit 진입점 (이름은 자유, Cloud에서 지정)
├── requirements.txt       # ← 런타임 의존성만
├── requirements-dev.txt   # ← (선택) pytest, ruff 등 개발용
├── .gitignore
├── .env.example           # ← 키 이름만 예시 (실제 키 X)
├── .streamlit/
│   ├── config.toml        # ← (선택) 테마·서버 설정
│   └── secrets.toml.example
└── README.md
```

### 2-2. `.gitignore` (템플릿)

```gitignore
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.env
.streamlit/secrets.toml
*.log
.DS_Store
Thumbs.db
.idea/
.vscode/
*.zip
```

> **중요:** `.env`, `.streamlit/secrets.toml`은 **절대 커밋하지 않습니다.**

### 2-3. `requirements.txt` 분리

**Cloud용 (`requirements.txt`)** — 실행에 필요한 것만:

```text
streamlit>=1.42
python-dotenv>=1.2
# 프로젝트별 패키지...
```

**로컬 개발용 (`requirements-dev.txt`)**:

```text
-r requirements.txt
pytest>=9.1
black>=26.5
ruff>=0.15
```

### 2-4. Secrets — 로컬 vs Cloud

| 환경 | Secrets 위치 |
|------|----------------|
| **로컬** | `.env` 파일 (`load_dotenv()`) |
| **Streamlit Cloud** | 대시보드 → Advanced settings → Secrets (TOML) |

`.streamlit/secrets.toml.example` 예시:

```toml
OPENAI_API_KEY = "your_openai_api_key"
OPENAI_MODEL = "gpt-5-mini"
# API_FOOTBALL_KEY = "optional"
```

### 2-5. `app.py` — Cloud Secrets 연동 (권장)

로컬 `.env`와 Cloud Secrets를 **같은 환경변수 이름**으로 쓰려면 `app.py` 상단에 추가:

```python
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def _apply_streamlit_secrets() -> None:
    try:
        for key in ("OPENAI_API_KEY", "OPENAI_MODEL", "API_FOOTBALL_KEY"):
            if key in st.secrets and st.secrets[key]:
                os.environ.setdefault(key, str(st.secrets[key]))
    except (FileNotFoundError, AttributeError, RuntimeError, KeyError):
        pass

_apply_streamlit_secrets()
```

> 프로젝트마다 필요한 키 이름만 `for key in (...)` 목록에 추가하세요.

### 2-6. 로컬 실행 확인

```powershell
cd D:\path\to\my-project
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

---

## 3. GitHub에 코드 올리기

### 3-1. 저장소 초기화 & 첫 커밋

```powershell
cd D:\path\to\my-project
$env:Path = "C:\Program Files\Git\cmd;C:\Program Files\GitHub CLI;" + $env:Path

git init
git branch -M main
git add -A
git status   # .env 가 staged 되지 않았는지 확인!

git -c user.name="YOUR_GITHUB_USERNAME" `
    -c user.email="YOUR_GITHUB_USERNAME@users.noreply.github.com" `
    commit -m "Initial commit: my streamlit app."
```

> `git config` 전역 설정 대신 `-c user.name` / `-c user.email`을 쓰면 PC 정책과 충돌을 줄일 수 있습니다.

### 3-2. GitHub public 저장소 생성 + 푸시

**방법 A — GitHub CLI (권장)**

```powershell
gh auth setup-git
gh repo create my-repo-name --public --source=. --remote=origin --push `
  --description "My Streamlit app description"
```

**방법 B — 이미 원격이 있을 때**

```powershell
git remote add origin https://github.com/YOUR_USERNAME/my-repo-name.git
git push -u origin main
```

**방법 C — 배치 스크립트**

이 프로젝트의 `scripts/github_setup.bat` 참고.

### 3-3. 연동 확인

```powershell
git remote -v
gh repo view YOUR_USERNAME/my-repo-name --json name,url,visibility
```

- `visibility`: `PUBLIC` (Community Cloud 무료 배포는 public repo 권장)
- `origin` → `https://github.com/...` 연결됨
- `Your branch is up to date with 'origin/main'`

---

## 4. Streamlit Community Cloud 배포

> Streamlit Cloud는 **웹 UI에서 GitHub 계정 연결**이 필요합니다. CLI만으로 완전 자동 배포는 현재 불가합니다.

### 4-1. 배포 페이지 열기

아래 URL에서 `{owner}`, `{repo}`, `{entrypoint}`를 바꿉니다:

```
https://share.streamlit.io/deploy?repository={owner}/{repo}&branch=main&mainModule={entrypoint}&subdomain={subdomain}
```

**예시 (본 프로젝트):**

```
https://share.streamlit.io/deploy?repository=yunt2002/football-match-predictor&branch=main&mainModule=app.py&subdomain=football-match-predictor
```

또는 https://share.streamlit.io → **Create app** → **Yup, I have an app**

### 4-2. 배포 설정 입력

| 항목 | 값 |
|------|-----|
| Repository | `YOUR_USERNAME/my-repo-name` |
| Branch | `main` |
| Main file path | `app.py` (또는 진입점 파일) |
| App URL (선택) | `my-app-name` → `https://my-app-name.streamlit.app` |

### 4-3. Advanced settings

1. **Python version** — 기본 3.12 (프로젝트에 맞게 선택)
2. **Secrets** — `.streamlit/secrets.toml.example` 내용을 복사 후 **실제 키**로 교체:

```toml
OPENAI_API_KEY = "sk-..."
OPENAI_MODEL = "gpt-5-mini"
```

3. **Save** → **Deploy**

### 4-4. 배포 완료

- 로그 패널에서 `Installing dependencies` → `Running app` 확인
- URL 예: `https://my-app-name.streamlit.app`

---

## 5. 배포 후 업데이트

코드 수정 후 GitHub에 푸시하면 **Streamlit Cloud가 자동 재배포**합니다.

```powershell
cd D:\path\to\my-project
git add .
git commit -m "Fix: describe your change"
git push origin main
```

- **의존성 변경** (`requirements.txt`) → 재설치 후 배포 (수 분 소요)
- **코드만 변경** → 보통 1분 이내 반영

Secrets 변경은 Cloud 대시보드 → 앱 → **Settings** → **Secrets**에서 수정.

---

## 6. 문제 해결

### "The app's code is not connected to a remote GitHub repository"

| 원인 | 해결 |
|------|------|
| 로컬만 있고 GitHub 미연결 | [3. GitHub에 코드 올리기](#3-github에-코드-올리기) 수행 |
| Cloud에 GitHub 미연동 | share.streamlit.io에서 GitHub 로그인 |
| 다른 폴더/브랜치 선택 | Repository·Branch·Main file 다시 확인 |

### PowerShell `Activate.ps1` 실행 오류

```
스크립트를 실행할 수 없으므로 Activate.ps1 파일을 로드할 수 없습니다
```

**해결 — venv 없이 실행:**

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

**또는 세션만 Bypass:**

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev.ps1
```

### `git push` 인증 실패

```powershell
gh auth setup-git
git push origin main
```

### Cloud에서 API 키 미동작

- Secrets TOML 형식 확인 (`KEY = "value"`)
- `app.py`에 `_apply_streamlit_secrets()` 추가 여부 확인
- Cloud 로그에서 `KeyError` / import 오류 확인

### `git` / `gh` 명령을 찾을 수 없음

새 터미널을 열거나 PATH에 추가:

```powershell
$env:Path = "C:\Program Files\Git\cmd;C:\Program Files\GitHub CLI;" + $env:Path
```

---

## 7. 새 프로젝트 빠른 체크리스트

새 Streamlit 프로젝트마다 아래 순서를 그대로 반복하세요.

```
[ ] app.py (또는 streamlit_app.py) 진입점 확인
[ ] requirements.txt — 런타임만
[ ] .gitignore — .env, .venv, secrets.toml 제외
[ ] .env.example + secrets.toml.example 작성
[ ] app.py에 _apply_streamlit_secrets() 추가
[ ] 로컬 streamlit run 성공
[ ] git init → commit
[ ] gh repo create ... --public --push
[ ] share.streamlit.io 에서 Deploy
[ ] Advanced settings → Secrets 입력
[ ] streamlit.app URL 접속 확인
```

### 변수 치환표 (복사용)

| placeholder | 예시 |
|-------------|------|
| `YOUR_GITHUB_USERNAME` | `yunt2002` |
| `my-repo-name` | `football-match-predictor` |
| `{entrypoint}` | `app.py` |
| `{subdomain}` | `football-match-predictor` |

---

## 관련 문서 (이 저장소)

- [DEPLOYMENT.md](DEPLOYMENT.md) — GitHub + Streamlit Community Cloud
- [STACK.md](STACK.md) — GitHub + Vercel + Supabase + Cursor MCP
- [MCP.md](MCP.md) — 프로젝트별 `.cursor/mcp.json` (수업용)

## 참고 링크

- [Streamlit Community Cloud 문서](https://docs.streamlit.io/deploy/streamlit-community-cloud)
- [Secrets 관리](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)
- [GitHub CLI 문서](https://cli.github.com/manual/)

---

*마지막 업데이트: 2026-06-19 · Football Match Predictor 프로젝트 배포 경험 기준*
