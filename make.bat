@echo off
if "%1"=="dev" (
    start cmd /k ".venv\Scripts\python.exe manage.py runserver"
    npm run dev
) else if "%1"=="test" (
    .venv\Scripts\pytest.exe -v %2 %3
) else if "%1"=="verify" (
    .venv\Scripts\python.exe verify_all.py
) else if "%1"=="lint" (
    .venv\Scripts\ruff.exe check .
) else if "%1"=="migrate" (
    .venv\Scripts\python.exe manage.py makemigrations
    .venv\Scripts\python.exe manage.py migrate
) else (
    echo auraStack Commands:
    echo   make dev      - Start Django backend and Vite dev servers
    echo   make test     - Run pytest test suite
    echo   make verify   - Run full system verification
    echo   make lint     - Run Ruff linter
    echo   make migrate  - Run database migrations
)
