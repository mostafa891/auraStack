# Developer Onboarding & Contributing

This document describes how to boot the AuraStack SaaS engine locally and guidelines to contribute code that maintains project quality.

---

## 🚀 3-Step Quickstart

AuraStack is fully Dockerized to ensure zero-configuration setup for developers.

### Step 1: Copy Environment Template
Copy the template `.env.example` to create your local `.env` configuration file:
```bash
cp .env.example .env
```

### Step 2: Boot Services
Start the web application, database, and background task queue workers in containers:
```bash
docker compose up --build
```
*   **Web Application:** Runs at `http://localhost:8000`
*   **Hot-Reloading Frontend:** Vite monitors file changes in `/frontend/src/`

### Step 3: Run Database Migrations (If running without Docker)
If you prefer to run the application directly in a local virtual environment:
```bash
# Activate your virtual environment
.venv\Scripts\Activate.ps1   # Windows
source .venv/bin/activate    # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

---

## 🎨 Code Quality & Formatting

To maintain a clean and standardized codebase, AuraStack enforces strict checks before code commits are allowed.

### Ruff Linting & Formatting
We use **Ruff** for Python linting and formatting. It replaces flake8, black, and isort, running 10-100x faster.
*   **Format Code:**
    ```bash
    ruff format .
    ```
*   **Lint Check:**
    ```bash
    ruff check .
    ```

### Pre-commit Hooks
AuraStack is pre-configured with `.pre-commit-config.yaml`. To install hooks in your local git repository:
```bash
pre-commit install
```
On every `git commit`, Ruff formatting and lint checks will run automatically. If any checks fail, the commit will be rejected until the errors are fixed.
