@echo off
if "%1"=="dev" (
    start cmd /k ".venv\Scripts\python.exe manage.py runserver"
    npm run dev
) else if "%1"=="test" (
    .venv\Scripts\python.exe -m pytest -v %2 %3
) else if "%1"=="verify" (
    .venv\Scripts\python.exe verify_all.py
) else if "%1"=="lint" (
    .venv\Scripts\python.exe -m ruff check .
) else if "%1"=="migrate" (
    .venv\Scripts\python.exe manage.py makemigrations
    .venv\Scripts\python.exe manage.py migrate
) else (
    echo auraStack Commands:
    echo   .\make.bat dev      - Start Django backend and Vite dev servers
    echo   .\make.bat test     - Run pytest test suite
    echo   .\make.bat verify   - Run full system verification
    echo   .\make.bat lint     - Run Ruff linter
    echo   .\make.bat migrate  - Run database migrations
)
