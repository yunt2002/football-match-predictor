# Cursor MCP — 프로젝트별 설정 (수업용)

수업에서는 **전역 설정(`~/.cursor/mcp.json`)보다 프로젝트별 설정**을 권장합니다.  
실습 프로젝트 안에 `.cursor/mcp.json`을 두면 **이 프로젝트에서만** 쓰는 MCP를 분리할 수 있습니다.

---

## 폴더 구조

```
football-match-predictor/          # (또는 my-project/)
├─ .cursor/
│  └─ mcp.json                     ← 이 프로젝트 전용 MCP 설정
├─ app.py                          # Streamlit 진입점
├─ requirements.txt
├─ match_simulator/
├─ docs/
└─ README.md
```

Next.js 실습이라면 `app.py` 대신 `package.json`, `src/` 등이 들어갑니다.

---

## Cursor에서 만드는 방법

1. **Cursor에서 실습 프로젝트 폴더를 엽니다.**  
   예: `D:\ict\test`

2. 왼쪽 파일 트리에서 **`.cursor` 폴더**를 만듭니다.

3. `.cursor` 폴더 안에 **`mcp.json`** 파일을 만듭니다.

4. **1단계 — 빈 템플릿** (수업 시작 시):

```json
{
  "mcpServers": {}
}
```

5. **2단계 — Supabase + Vercel 추가** (본 프로젝트 예시):

```json
{
  "mcpServers": {
    "supabase": {
      "url": "https://mcp.supabase.com/mcp"
    },
    "vercel": {
      "url": "https://mcp.vercel.com/mcp"
    }
  }
}
```

> ⚠️ Vercel URL은 `https://mcp.vercel.com` (끝에 `/mcp` 없음)

6. **저장 후 Cursor 재시작**  
   `Ctrl+Shift+P` → `Developer: Reload Window`

7. **Settings → Tools & MCP**  
   - `supabase` / `vercel` 옆 **Connect** 클릭  
   - 브라우저에서 OAuth 로그인·승인

---

## 이 저장소의 현재 설정

파일: [`.cursor/mcp.json`](../.cursor/mcp.json)

| 서버 | URL | 용도 |
|------|-----|------|
| supabase | `https://mcp.supabase.com/mcp` | DB·SQL·마이그레이션·advisor |
| vercel | `https://mcp.vercel.com` | 배포·로그·프로젝트 조회 |

**Plugin MCP** (Cursor Marketplace)와 **Installed MCP** (mcp.json)가 동시에 보일 수 있습니다.  
둘 다 Connect 되어 있으면 사용 가능합니다. 중복이 헷갈리면 **Plugin만** 켜고 `mcp.json`은 비워도 됩니다.

---

## Git에 올려도 되나?

**예.** `mcp.json`에는 URL만 있고 **API 키·토큰은 없습니다.**  
팀·수업원과 같은 MCP 설정을 공유하려면 커밋하세요.

```powershell
git add .cursor/mcp.json docs/MCP.md
git commit -m "Add project-local Cursor MCP config."
git push
```

---

## 연결 확인 (채팅에 입력)

- `Supabase 프로젝트 목록 보여줘`
- `Vercel 팀과 프로젝트 목록 보여줘`

---

## 전역 vs 프로젝트

| 위치 | 경로 (Windows) | 수업 권장 |
|------|----------------|---------|
| **프로젝트** | `my-project/.cursor/mcp.json` | ✅ 권장 |
| **전역** | `%USERPROFILE%\.cursor\mcp.json` | 선택 (모든 프로젝트 공통) |

수업 실습은 **프로젝트 폴더 안 `.cursor/mcp.json`만** 사용하는 것을 권장합니다.

---

## 관련 문서

- [STACK.md](STACK.md) — GitHub → Vercel → Supabase 전체 스택
- [DEPLOYMENT.md](DEPLOYMENT.md) — Streamlit Cloud 배포 (현재 Python 앱)
