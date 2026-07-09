# 🎨 Tailwind CSS v4 Reference Guide

AuraFlow uses the CSS-first architecture of **Tailwind CSS v4** to manage themes, layouts, and typography.

---

## ⚙️ CSS-First Configuration

Tailwind v4 deprecates the javascript-based `tailwind.config.js` file. All theme configurations, design tokens, and utility extensions are defined inside [app.css](file:///a:/auraflow/frontend/src/app.css) using the `@theme` directive or native CSS variables.

### Design Tokens
Key styling tokens are defined at the `:root` level:
```css
:root {
  --color-primary: #6366f1;         /* Indigo base */
  --color-primary-hover: #4f46e5;   /* Hover state */
  --color-surface: #ffffff;         /* Cards background */
  --color-surface-muted: #f8fafc;   /* Main page background */
  --color-border: #e2e8f0;          /* Separators */
  --color-text: #0f172a;            /* Primary typography */
  --color-text-muted: #64748b;      /* Secondary typography */
  --color-danger: #ef4444;          /* Errors and alerts */
}
```
These are accessed inside components using standard Tailwind styling utility classes (e.g. `bg-[var(--color-surface)]`, `text-[var(--color-text-muted)]`).

---

## 🌓 Dark Mode Implementation

AuraFlow implements a reactive theme toggle that switches between `LIGHT`, `DARK`, and `SYSTEM` settings.

### Theme Swapper: `applyTheme()`
The active theme is updated dynamically on the client side via the `applyTheme` function in [Profile.vue](file:///a:/auraflow/frontend/src/pages/Profile.vue):
- **Dark Mode**: Appends the `.dark` class to the `<html>` element and overrides core theme CSS variables:
  ```typescript
  const applyTheme = (themeName: string) => {
    const root = document.documentElement;
    if (themeName === "DARK") {
      root.classList.add("dark");
      root.style.setProperty("--color-surface", "#0f172a");
      root.style.setProperty("--color-surface-muted", "#020617");
      root.style.setProperty("--color-border", "#1e293b");
      root.style.setProperty("--color-text", "#f8fafc");
      root.style.setProperty("--color-text-muted", "#94a3b8");
    }
    // Handles LIGHT and SYSTEM options...
  }
  ```
- **System Mode**: Detects browser theme preferences using `window.matchMedia("(prefers-color-scheme: dark)").matches` and dynamically applies either the light or dark styles accordingly.

---

## 🛠️ Tailwind Vite Integration

The Tailwind compiler is linked to Vite via the `@tailwindcss/vite` plugin registered in [vite.config.ts](file:///a:/auraflow/frontend/vite.config.ts). This compiles styling and strips unused classes automatically during production builds.
