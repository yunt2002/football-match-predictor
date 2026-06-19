@echo off
set PATH=C:\Program Files\Git\cmd;C:\Program Files\GitHub CLI;%PATH%
cd /d "%~dp0"

echo === GitHub 연동 스크립트 ===
echo.

where git >nul 2>&1 || (echo Git을 찾을 수 없습니다. Git for Windows를 설치하세요. & exit /b 1)
where gh >nul 2>&1 || (echo GitHub CLI(gh)를 찾을 수 없습니다. & exit /b 1)

gh auth status >nul 2>&1
if errorlevel 1 (
  echo GitHub 로그인이 필요합니다. 브라우저 창이 열립니다...
  gh auth login -h github.com -p https -w
)

set /p REPO_NAME="GitHub 저장소 이름 (예: kor-mex-simulator): "
if "%REPO_NAME%"=="" set REPO_NAME=kor-mex-simulator

echo.
echo 원격 저장소 생성 및 푸시 중...
gh repo create %REPO_NAME% --public --source=. --remote=origin --push

if errorlevel 1 (
  echo.
  echo 자동 생성 실패 시 GitHub에서 빈 저장소를 만든 뒤:
  echo   git remote add origin https://github.com/사용자명/%REPO_NAME%.git
  echo   git push -u origin main
)

echo.
echo 완료. gh repo view --web 로 확인하세요.
pause
