# Streamlit Community Cloud + Vercel redirect one-shot setup
$ErrorActionPreference = "Stop"

$repo = "yunt2002/football-match-predictor"
$branch = "main"
$mainFile = "app.py"
$subdomain = "kor-mex-match-predictor"
$streamlitUrl = "https://$subdomain.streamlit.app"
$deployUrl = "https://share.streamlit.io/deploy?repository=$repo&branch=$branch&mainModule=$mainFile&subdomain=$subdomain"

Write-Host ""
Write-Host "=== Football Match Predictor 배포 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Streamlit Cloud URL: $streamlitUrl"
Write-Host "Deploy page: $deployUrl"
Write-Host ""
Write-Host "Secrets: .streamlit/secrets.toml 내용을 Cloud 대시보드에 붙여넣기"
Write-Host ""

Start-Process $deployUrl
Write-Host "브라우저에서 GitHub 연결 후 Deploy 클릭" -ForegroundColor Green
