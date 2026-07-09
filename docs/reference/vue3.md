# 🟢 Vue 3 Composition API & Frontend Architecture

This document describes the frontend architectural choices and structure of the **AuraFlow** SaaS web application.

---

## 📂 Frontend Directory Structure

The frontend code resides in the `/frontend/` workspace directory:
- `src/main.ts`: Application entry point. Mounts Inertia, registers Pinia, and imports base styles.
- `src/pages/`: Inertia pages. Each component in this directory corresponds to a route rendered by Django.
  - `Auth/`: `Login.vue`, `Register.vue`
  - `Security/`: `PasswordChange.vue`, `MfaList.vue`, `MfaAuthenticate.vue`, `TotpActivate.vue`, `TotpDeactivate.vue`, `SocialConnections.vue`
  - `Profile.vue`: User preferences and settings dashboard.
- `src/layouts/`: Global wrapper structures. Includes `AuthLayout.vue`.
- `src/composables/`: Reusable Vue hooks. Includes `useFormErrors.ts` and `zodSchema.ts`.
- `src/types/`: TypeScript definitions, including `inertia.d.ts`.

---

## ⚡ Compositions & Form Utilities

AuraFlow integrates client-side schema validation (Zod) and server-side Django Form error parsing.

### 1. Zod v4 Schema Adapter (`zodSchema.ts`)
Since standard validation adapters like `@vee-validate/zod` may lag behind the latest Zod v4 specs, AuraFlow implements a custom schema bridge in [zodSchema.ts](file:///a:/auraflow/frontend/src/composables/zodSchema.ts).
- `toTypedSchema(zodSchema)`: Standardizes validation responses so Zod issues are piped directly to VeeValidate's form state.

### 2. Django Error Parser (`useFormErrors.ts`)
Django form validation returns nested error dictionaries:
```json
{
  "email": [{"message": "Email address is required.", "code": "required"}]
}
```
The [useFormErrors](file:///a:/auraflow/frontend/src/composables/useFormErrors.ts) composable converts this server format to simple field-to-message mapping:
```json
{
  "email": "Email address is required."
}
```
It exposes:
- `fieldErrors`: Reactive key-value dictionary containing simplified field errors.
- `hasGeneralError`: Boolean checking for authentication-wide errors (e.g. `INVALID_CREDENTIALS` or `__all__` field errors).
- `generalError`: Computed string with user-friendly messages for general failures.

---

## 🏗️ SPA Page Components

All pages are built using the Vue 3 `<script setup lang="ts">` Composition API:
- **State Management**: Uses Pinia (registered in `main.ts`).
- **Reactive Forms**: Form submissions are triggered via Inertia's `useForm` hook, which intercepts standard form POST submissions to preserve SPA states:
  ```typescript
  import { useForm } from "@inertiajs/vue3";
  const form = useForm({ email: "", password: "" });
  form.post("/auth/login/");
  ```
