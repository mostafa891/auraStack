<script setup lang="ts">
import { useForm, Link } from "@inertiajs/vue3";
import { useForm as useVeeForm, useField } from "vee-validate";
import { toTypedSchema } from "@/composables/zodSchema";
import { z } from "zod";
import AuthLayout from "@/layouts/AuthLayout.vue";
import { useFormErrors } from "@/composables/useFormErrors";

const registerSchema = toTypedSchema(
  z
    .object({
      email: z
        .string()
        .min(1, "Email is required.")
        .email("Please enter a valid email address."),
      password: z
        .string()
        .min(8, "Password must be at least 8 characters."),
      password_confirm: z
        .string()
        .min(1, "Please confirm your password."),
    })
    .refine((data) => data.password === data.password_confirm, {
      message: "Passwords do not match.",
      path: ["password_confirm"],
    })
);

const { handleSubmit, errors: clientErrors } = useVeeForm({
  validationSchema: registerSchema,
});

const { value: email } = useField<string>("email");
const { value: password } = useField<string>("password");
const { value: passwordConfirm } = useField<string>("password_confirm");

const inertiaForm = useForm({
  email: "",
  password: "",
  password_confirm: "",
});
const { fieldErrors, hasGeneralError, generalError } = useFormErrors();

const onSubmit = handleSubmit((values) => {
  inertiaForm.email = values.email;
  inertiaForm.password = values.password;
  inertiaForm.password_confirm = values.password_confirm;
  inertiaForm.post("/auth/register/");
});
</script>

<template>
  <AuthLayout title="Create your account" subtitle="Start building your SaaS platform in minutes">
    <!-- General Error Alert -->
    <div
      v-if="hasGeneralError"
      class="mb-6 rounded-xl bg-[var(--color-danger)]/10 border border-[var(--color-danger)]/20 p-4 text-sm text-[var(--color-danger)] flex items-start space-x-2"
    >
      <svg class="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
      <span>{{ generalError }}</span>
    </div>

    <form @submit.prevent="onSubmit" class="space-y-5">
      <!-- Email Field -->
      <div>
        <label
          for="email"
          class="block text-sm font-semibold text-[var(--color-text)] mb-1.5"
        >
          Email address
        </label>
        <input
          id="email"
          v-model="email"
          type="email"
          autocomplete="email"
          class="w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-muted)] px-4 py-3 text-sm
                 outline-none premium-input text-[var(--color-text)]"
          :class="{
            'border-[var(--color-danger)]': clientErrors.email || fieldErrors.email,
          }"
        />
        <p
          v-if="clientErrors.email || fieldErrors.email"
          class="mt-1.5 text-xs text-[var(--color-danger)] font-medium"
        >
          {{ clientErrors.email || fieldErrors.email }}
        </p>
      </div>

      <!-- Password Field -->
      <div>
        <label
          for="password"
          class="block text-sm font-semibold text-[var(--color-text)] mb-1.5"
        >
          Password
        </label>
        <input
          id="password"
          v-model="password"
          type="password"
          autocomplete="new-password"
          class="w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-muted)] px-4 py-3 text-sm
                 outline-none premium-input text-[var(--color-text)]"
          :class="{
            'border-[var(--color-danger)]': clientErrors.password || fieldErrors.password,
          }"
        />
        <p
          v-if="clientErrors.password || fieldErrors.password"
          class="mt-1.5 text-xs text-[var(--color-danger)] font-medium"
        >
          {{ clientErrors.password || fieldErrors.password }}
        </p>
      </div>

      <!-- Confirm Password Field -->
      <div>
        <label
          for="password_confirm"
          class="block text-sm font-semibold text-[var(--color-text)] mb-1.5"
        >
          Confirm password
        </label>
        <input
          id="password_confirm"
          v-model="passwordConfirm"
          type="password"
          autocomplete="new-password"
          class="w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-muted)] px-4 py-3 text-sm
                 outline-none premium-input text-[var(--color-text)]"
          :class="{
            'border-[var(--color-danger)]': clientErrors.password_confirm || fieldErrors.password_confirm,
          }"
        />
        <p
          v-if="clientErrors.password_confirm || fieldErrors.password_confirm"
          class="mt-1.5 text-xs text-[var(--color-danger)] font-medium"
        >
          {{ clientErrors.password_confirm || fieldErrors.password_confirm }}
        </p>
      </div>

      <!-- Submit Button -->
      <button
        type="submit"
        :disabled="inertiaForm.processing"
        class="w-full rounded-xl bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-primary-hover)] py-3 text-sm font-semibold
               text-white transition-all shadow-md shadow-indigo-500/10 hover:shadow-lg hover:shadow-indigo-500/20
               disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer active:scale-98"
      >
        <span v-if="!inertiaForm.processing">Create account</span>
        <span v-else>Creating...</span>
      </button>
    </form>

    <!-- Divider -->
    <div class="relative flex items-center justify-center my-6">
      <div class="absolute w-full border-t border-[var(--color-border)]"></div>
      <span class="relative px-3 bg-[var(--color-surface)] text-[10px] uppercase font-bold text-[var(--color-text-muted)] tracking-wider">
        Or register with
      </span>
    </div>

    <!-- Social Login Provider Buttons -->
    <div class="grid grid-cols-2 gap-3">
      <a
        href="/accounts/google/login/"
        class="flex items-center justify-center space-x-2 py-2.5 px-4 rounded-xl border border-[var(--color-border)] hover:border-gray-300 dark:hover:border-gray-600 bg-[var(--color-surface)] text-[var(--color-text)] font-semibold text-xs transition-all shadow-sm active:scale-98"
      >
        <svg class="w-4 h-4" viewBox="0 0 24 24">
          <path fill="#EA4335" d="M12 5.04c1.66 0 3.2.57 4.38 1.69l3.27-3.27C17.67 1.58 14.98 1 12 1 7.35 1 3.4 3.65 1.5 7.5l3.86 3C6.27 7.53 8.92 5.04 12 5.04z" />
          <path fill="#4285F4" d="M23.49 12.27c0-.81-.07-1.59-.2-2.27H12v4.51h6.47c-.29 1.48-1.14 2.73-2.4 3.58l3.74 2.9c2.18-2.01 3.68-4.96 3.68-8.72z" />
          <path fill="#FBBC05" d="M5.36 14.5c-.24-.72-.38-1.49-.38-2.3s.14-1.58.38-2.3L1.5 6.9C.54 8.84 0 11 0 13.3c0 2.3.54 4.46 1.5 6.4l3.86-3.2z" />
          <path fill="#34A853" d="M12 23c3.24 0 5.97-1.07 7.96-2.91l-3.74-2.9c-1.1.74-2.51 1.18-4.22 1.18-3.08 0-5.73-2.49-6.64-5.46L1.5 16.12C3.4 19.95 7.35 22.6 12 23z" />
        </svg>
        <span>Google</span>
      </a>
      <a
        href="/accounts/github/login/"
        class="flex items-center justify-center space-x-2 py-2.5 px-4 rounded-xl border border-[var(--color-border)] hover:border-gray-300 dark:hover:border-gray-600 bg-[var(--color-surface)] text-[var(--color-text)] font-semibold text-xs transition-all shadow-sm active:scale-98"
      >
        <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24">
          <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482C19.138 20.197 22 16.44 22 12.017 22 6.484 17.522 2 12 2z" />
        </svg>
        <span>GitHub</span>
      </a>
    </div>

    <!-- Footer -->
    <template #footer>
      Already have an account?
      <Link
        href="/auth/login/"
        class="font-semibold text-[var(--color-primary)] hover:text-[var(--color-primary-hover)] transition-colors underline decoration-2 decoration-transparent hover:decoration-[var(--color-primary)]"
      >
        Sign in
      </Link>
    </template>
  </AuthLayout>
</template>
