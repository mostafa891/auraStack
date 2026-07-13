# Claude Code Project Guide: AuraStack

This guide helps Claude Code understand the project commands, architecture, and coding standards.

## Build and Run Commands
* Run Backend Development Server: `.venv\Scripts\python.exe manage.py runserver`
* Run Frontend Development Server: `npm run dev`
* Run Q2 Task Worker: `.venv\Scripts\python.exe manage.py qcluster`
* Apply Migrations: `.venv\Scripts\python.exe manage.py migrate`
* Create Migrations: `.venv\Scripts\python.exe manage.py makemigrations`
* Populate Seed Data: `.venv\Scripts\python.exe manage.py shell -c "from scripts import seed_data; seed_data.run()"`

## Testing and Verification
* Run All Verifications (Fastest): `.venv\Scripts\python.exe verify_all.py`
* Run Pytest Suite: `.venv\Scripts\python.exe -m pytest`
* Run Single Test: `.venv\Scripts\python.exe -m pytest tests/path_to_test.py::test_name`
* Run Playwright E2E Tests: `set DJANGO_ALLOW_ASYNC_UNSAFE=true && .venv\Scripts\python.exe -m pytest tests/e2e/`

## Code Architecture Standards
1. **Multi-Tenancy Isolation:** Always ensure database queries filter by the active workspace:
   `WorkspaceModel.objects.filter(workspace=request.active_workspace)`
2. **Layer Separation:** Use **Selectors** (e.g. `selectors.py`) for data reads/queries and **Services** (e.g. `services.py`) for mutations and database writes. Keep views thin.
3. **Inertia Rendering:** Use Inertia's `render(request, "Folder/Component", props)` instead of JSON response wrappers.
4. **Vite Vue 3 Standards:** Use `<script setup lang="ts">` for Vue components. Rely on page props for state where possible.
5. **Bidirectional Styling (RTL):** Use Tailwind logical properties (e.g., `ms-4`, `pe-2`) instead of physical classes (`ml-4`, `pr-2`) to support RTL.
6. **Django Ninja API Development:**
   * Private endpoints (authenticated, CSRF protected): use `private_api` (`from apps.payments.api import private_api`).
   * Public endpoints (webhooks, public integrations): use `public_api`.
   * Use Pydantic `Schema` for type hints and requests/response schemas validation.

