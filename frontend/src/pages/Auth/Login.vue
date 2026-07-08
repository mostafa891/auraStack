<script setup lang="ts">
/**
 * Login Page — صفحة تسجيل الدخول.
 *
 * التدفق:
 * 1. المستخدم يملأ email + password
 * 2. Zod بيتحقق من الحقول في المتصفح (client-side)
 * 3. Inertia بيبعت POST لـ /auth/login/
 * 4. Django بيتحقق ويرجع redirect أو errors عبر share()
 * 5. useFormErrors بيعرض الأخطاء في المكان الصح
 */

import { useForm, Link } from "@inertiajs/vue3";
import { useForm as useVeeForm, useField } from "vee-validate";
import { toTypedSchema } from "@/composables/zodSchema";
import { z } from "zod";
import AuthLayout from "@/layouts/AuthLayout.vue";
import { useFormErrors } from "@/composables/useFormErrors";

// ============================
// Zod Schema — قواعد التحقق (Zod v4 API)
// ============================
const loginSchema = toTypedSchema(
  z.object({
    email: z
      .string()
      .min(1, "Email is required.")
      .email("Please enter a valid email address."),
    password: z
      .string()
      .min(1, "Password is required."),
  })
);

// ============================
// VeeValidate Form
// ============================
const { handleSubmit, errors: clientErrors } = useVeeForm({
  validationSchema: loginSchema,
});

const { value: email } = useField<string>("email");
const { value: password } = useField<string>("password");

// ============================
// Inertia Form + Server Errors
// ============================
const inertiaForm = useForm({ email: "", password: "" });
const { fieldErrors, hasGeneralError, generalError } = useFormErrors();

// ============================
// Submit Handler
// ============================
const onSubmit = handleSubmit((values) => {
  inertiaForm.email = values.email;
  inertiaForm.password = values.password;
  inertiaForm.post("/auth/login/");
});
</script>

<template>
  <AuthLayout title="Welcome back" subtitle="Sign in to your account">
    <!-- General Error Alert -->
    <div
      v-if="hasGeneralError"
      class="mb-6 rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-700"
    >
      {{ generalError }}
    </div>

    <form @submit.prevent="onSubmit" class="space-y-5">
      <!-- Email Field -->
      <div>
        <label
          for="email"
          class="block text-sm font-medium text-[var(--color-text)] mb-1.5"
        >
          Email address
        </label>
        <input
          id="email"
          v-model="email"
          type="email"
          autocomplete="email"
          class="w-full rounded-lg border border-[var(--color-border)] px-4 py-2.5 text-sm
                 outline-none transition-colors
                 focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"
          :class="{
            'border-[var(--color-danger)]': clientErrors.email || fieldErrors.email,
          }"
        />
        <p
          v-if="clientErrors.email || fieldErrors.email"
          class="mt-1.5 text-xs text-[var(--color-danger)]"
        >
          {{ clientErrors.email || fieldErrors.email }}
        </p>
      </div>

      <!-- Password Field -->
      <div>
        <label
          for="password"
          class="block text-sm font-medium text-[var(--color-text)] mb-1.5"
        >
          Password
        </label>
        <input
          id="password"
          v-model="password"
          type="password"
          autocomplete="current-password"
          class="w-full rounded-lg border border-[var(--color-border)] px-4 py-2.5 text-sm
                 outline-none transition-colors
                 focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"
          :class="{
            'border-[var(--color-danger)]': clientErrors.password || fieldErrors.password,
          }"
        />
        <p
          v-if="clientErrors.password || fieldErrors.password"
          class="mt-1.5 text-xs text-[var(--color-danger)]"
        >
          {{ clientErrors.password || fieldErrors.password }}
        </p>
      </div>

      <!-- Submit Button -->
      <button
        type="submit"
        :disabled="inertiaForm.processing"
        class="w-full rounded-lg bg-[var(--color-primary)] px-4 py-2.5 text-sm font-medium
               text-white transition-colors hover:bg-[var(--color-primary-hover)]
               disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
      >
        <span v-if="!inertiaForm.processing">Sign in</span>
        <span v-else>Signing in...</span>
      </button>
    </form>

    <!-- Footer (Inertia Link — بدون full page reload) -->
    <template #footer>
      Don't have an account?
      <Link
        href="/auth/register/"
        class="font-medium text-[var(--color-primary)] hover:text-[var(--color-primary-hover)] transition-colors"
      >
        Create one
      </Link>
    </template>
  </AuthLayout>
</template>
