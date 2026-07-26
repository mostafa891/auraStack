param (
    [string]$Target = "help"
)

switch ($Target) {
    "dev" {
        Start-Process powershell -ArgumentList "-NoExit", "-Command", ".venv\Scripts\python.exe manage.py runserver"
        npm run dev
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
