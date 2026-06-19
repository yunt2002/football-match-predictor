# Streamlit Community Cloud one-click deploy helper
# GitHub: https://github.com/yunt2002/football-match-predictor

$deployUrl = "https://share.streamlit.io/deploy?repository=yunt2002/football-match-predictor&branch=main&mainModule=app.py&subdomain=kor-mex-match-predictor"

Write-Host "Opening Streamlit Cloud deploy page..."
Write-Host $deployUrl
Start-Process $deployUrl

Write-Host ""
Write-Host "=== Deploy settings (confirm in browser) ==="
Write-Host "Repository : yunt2002/football-match-predictor"
Write-Host "Branch     : main"
Write-Host "Main file  : app.py"
Write-Host "App URL    : kor-mex-match-predictor"
Write-Host "Expected   : https://kor-mex-match-predictor.streamlit.app"
Write-Host ""
Write-Host "=== Secrets (Advanced settings, optional) ==="
Write-Host "Copy from .streamlit/secrets.toml.example and paste real keys."
Write-Host "OPENAI_API_KEY, OPENAI_MODEL (gpt-5-mini), API_FOOTBALL_KEY (optional)"
Write-Host ""
Write-Host "Then click Deploy."
