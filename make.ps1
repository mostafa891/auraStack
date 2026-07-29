param (
    [string]$Target = "help"
)

switch ($Target) {
    "dev" {
        $python = if (Test-Path ".venv\Scripts\python.exe") { ".venv\Scripts\python.exe" } else { "python" }
        Write-Host "🚀 Starting Django Backend & Vite Frontend..." -ForegroundColor Green
        $backend = Start-Process -FilePath $python -ArgumentList "manage.py", "runserver" -PassThru -NoNewWindow
        try {
            npm run dev
        } finally {
            if ($backend -and -not $backend.HasExited) {
                Write-Host "🛑 Stopping Django Backend process..." -ForegroundColor Yellow
                Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
            }
        }
    }
    "test" {
        & .venv\Scripts\python.exe -m pytest -v
    }
    "verify" {
        & .venv\Scripts\python.exe verify_all.py
    }
    "lint" {
        & .venv\Scripts\python.exe -m ruff check .
    }
    "migrate" {
        & .venv\Scripts\python.exe manage.py makemigrations
        & .venv\Scripts\python.exe manage.py migrate
    }
    default {
        Write-Host "auraStack PowerShell Commands:" -ForegroundColor Cyan
        Write-Host "  .\make.ps1 dev      - Start Django backend and Vite dev servers"
        Write-Host "  .\make.ps1 test     - Run pytest test suite"
        Write-Host "  .\make.ps1 verify   - Run full system verification"
        Write-Host "  .\make.ps1 lint     - Run Ruff linter"
        Write-Host "  .\make.ps1 migrate  - Run database migrations"
    }
}
