# ⚡ Django-Vite Integration Guide

This guide explains how asset bundling, TypeScript, and Hot Module Replacement (HMR) are managed in **AuraFlow** using **django-vite** and **Vite**.

---

## ⚙️ Django-Vite Configurations

django-vite bridges Django templates with the Vite development server and production assets.

### Configurations in `base.py`
```python
DJANGO_VITE = {
    "default": {
        "dev_mode": False,
        "dev_server_host": "localhost",
        "dev_server_port": 5173,
        "manifest_path": BASE_DIR / "static" / "dist" / ".vite" / "manifest.json",
        "static_url_prefix": "dist",
    }
}
```

### Dev Mode Overrides in `local.py`
For development, AuraFlow enables hot reloads but disables it during automated tests:
```python
TESTING = "test" in sys.argv or any("pytest" in arg for arg in sys.argv)

DJANGO_VITE = {
    "default": {
        **DJANGO_VITE["default"],
        "dev_mode": not TESTING, # Disable HMR during Playwright/Pytest runs
    }
}
```
> [!IMPORTANT]
> Disabling `dev_mode` during testing ensures that Playwright is testing the actual production-ready compiled bundle rather than relying on a separate Vite server running in the background.

---

## 🛠️ Vite Configuration (`vite.config.ts`)

Located at [vite.config.ts](file:///a:/auraflow/frontend/vite.config.ts), Vite is configured to process the assets in `frontend/`:
- **Plugins**: Uses Vue and Tailwind CSS plugins.
- **Root Directory**: Mapped to the root directory `frontend/`.
- **Base Path**: `/static/dist/` matches Django's static files setup.
- **Output Directory**: Mapped to `../static/dist/`, placing bundled assets directly where Django staticfiles can serve them.
- **Manifest**: `manifest: true` creates a manifest list matching original source names with bundled names.

---

## 🏷️ Asset Injection in Django Templates

In [base.html](file:///a:/auraflow/templates/base.html), Vite assets are injected using custom Django tags:
```html
{% load django_vite %}

<!-- Injects HMR script during local development -->
{% vite_hmr_client %}

<!-- Injects entry-point script (and associated CSS chunks) -->
{% vite_asset "src/main.ts" %}
```
If `dev_mode` is `True`, it fetches resources directly from `http://localhost:5173/static/dist/src/main.ts`.
If `dev_mode` is `False`, it reads the manifest file (`static/dist/.vite/manifest.json`) and injects the bundled stylesheet and javascript files.
