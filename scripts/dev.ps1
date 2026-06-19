Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force -ErrorAction SilentlyContinue
Set-Location (Split-Path $PSScriptRoot -Parent)
& .\.venv\Scripts\Activate.ps1
Write-Host "venv activated -> $(python --version) @ $(Get-Command python | Select-Object -ExpandProperty Source)"
