<script setup lang="ts">
import { ref } from "vue";
import { useForm, Link } from "@inertiajs/vue3";
import { useForm as useVeeForm, useField } from "vee-validate";
import { toTypedSchema } from "@/composables/zodSchema";
import { z } from "zod";
import AuthLayout from "@/layouts/AuthLayout.vue";
import { useFormErrors } from "@/composables/useFormErrors";
import { useI18n } from "@/composables/useI18n";

const { t } = useI18n();

const loginSchema = toTypedSchema(
  z.object({
    email: z
      .string()
      .min(1, t("password_reset.email_required"))
      .email(t("password_reset.email_invalid")),
    password: z
      .string()
      .min(1, t("password_reset_key.confirm_required")),
  })
);

const { handleSubmit, errors: clientErrors } = useVeeForm({
  validationSchema: loginSchema,
});

const { value: email } = useField<string>("email");
const { value: password } = useField<string>("password");

const remember = ref(false);
const inertiaForm = useForm({ email: "", password: "", remember: false });
const { fieldErrors, hasGeneralError, generalError } = useFormErrors();

const socialLogin = (provider: string) => {
  const form = document.createElement("form");
  form.method = "POST";
  form.action = `/accounts/${provider}/login/`;
  
  const csrfInput = document.createElement("input");
  csrfInput.type = "hidden";
  csrfInput.name = "csrfmiddlewaretoken";
  const csrfToken = document.cookie.split("; ")
    .find(row => row.startsWith("XSRF-TOKEN="))
    ?.split("=")[1] || "";
  csrfInput.value = decodeURIComponent(csrfToken);
  
  form.appendChild(csrfInput);
  document.body.appendChild(form);
  form.submit();
};

const onSubmit = handleSubmit((values) => {
  inertiaForm.email = values.email;
  inertiaForm.password = values.password;
  inertiaForm.remember = remember.value;
  inertiaForm.post("/auth/login/");
});
</script>

<template>
  <AuthLayout :title="t('auth.login_title')" :subtitle="t('auth.login_subtitle')">
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
          {{ t('auth.email_label') }}
        </label>
        <input
          id="email"
          v-model="email"
          type="email"
          autocomplete="email"
          class="w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-muted)] px-4 py-3 text-sm outline-none premium-input text-[var(--color-text)]"
          :class="{ 'border-[var(--color-danger)] focus:border-[var(--color-danger)]': fieldErrors.email || clientErrors.email }"
        >
        <p v-if="clientErrors.email" class="mt-1.5 text-xs font-semibold text-[var(--color-danger)]">
          {{ clientErrors.email }}
        </p>
        <p v-else-if="fieldErrors.email" class="mt-1.5 text-xs font-semibold text-[var(--color-danger)]">
          {{ fieldErrors.email[0] }}
        </p>
      </div>

      <!-- Password Field -->
      <div>
        <div class="flex justify-between items-center mb-1.5">
          <label
            for="password"
            class="block text-sm font-semibold text-[var(--color-text)]"
          >
            {{ t('auth.password_label') }}
          </label>
          <Link
            href="/accounts/password/reset/"
            class="text-xs font-semibold text-[var(--color-primary)] hover:underline"
          >
            {{ t('auth.forgot_password') }}
          </Link>
        </div>
        <input
          id="password"
          v-model="password"
          type="password"
          autocomplete="current-password"
          class="w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-muted)] px-4 py-3 text-sm outline-none premium-input text-[var(--color-text)]"
          :class="{ 'border-[var(--color-danger)] focus:border-[var(--color-danger)]': fieldErrors.password || clientErrors.password }"
        >
        <p v-if="clientErrors.password" class="mt-1.5 text-xs font-semibold text-[var(--color-danger)]">
          {{ clientErrors.password }}
        </p>
        <p v-else-if="fieldErrors.password" class="mt-1.5 text-xs font-semibold text-[var(--color-danger)]">
          {{ fieldErrors.password[0] }}
        </p>
      </div>

      <!-- Remember Me & Forgot Password -->
      <div class="flex items-center justify-between">
        <label class="flex items-center space-x-2 text-xs font-semibold text-[var(--color-text-muted)] cursor-pointer select-none">
          <input
            v-model="remember"
            type="checkbox"
            class="rounded border-[var(--color-border)] text-[var(--color-primary)] focus:ring-[var(--color-primary)] w-4 h-4 cursor-pointer"
          >
          <span>{{ t('auth.remember_me') }}</span>
        </label>
      </div>

      <!-- Submit Button -->
      <button
        type="submit"
        :disabled="inertiaForm.processing"
        class="w-full rounded-xl bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-primary-hover)] py-3 text-sm font-semibold text-white transition-all shadow-md hover:shadow-lg disabled:opacity-50 cursor-pointer"
      >
        <span v-if="inertiaForm.processing">{{ t('auth.signing_in') }}</span>
        <span v-else>{{ t('common.sign_in') }}</span>
      </button>
    </form>

    <!-- Divider -->
    <div class="relative my-6">
      <div class="absolute inset-0 flex items-center">
        <div class="w-full border-t border-[var(--color-border)]" />
      </div>
      <div class="relative flex justify-center text-xs font-semibold uppercase">
        <span class="bg-[var(--color-surface)] px-3 text-[var(--color-text-muted)]">
          {{ t('auth.or_continue_with') }}
        </span>
      </div>
    </div>

    <!-- Social Login Provider Buttons -->
    <div class="grid grid-cols-2 gap-3">
      <button
        type="button"
        @click="socialLogin('google')"
        class="flex items-center justify-center space-x-2 py-2.5 px-4 rounded-xl border border-[var(--color-border)] hover:border-gray-300 dark:hover:border-gray-600 bg-[var(--color-surface)] text-[var(--color-text)] font-semibold text-xs transition-all shadow-sm active:scale-98 cursor-pointer"
      >
        <svg class="w-4 h-4" viewBox="0 0 24 24">
          <path fill="#EA4335" d="M12 5.04c1.66 0 3.2.57 4.38 1.69l3.27-3.27C17.67 1.58 14.98 1 12 1 7.35 1 3.4 3.65 1.5 7.5l3.86 3C6.27 7.53 8.92 5.04 12 5.04z" />
          <path fill="#4285F4" d="M23.49 12.27c0-.81-.07-1.59-.2-2.27H12v4.51h6.47c-.29 1.48-1.14 2.73-2.4 3.58l3.74 2.9c2.18-2.01 3.68-4.96 3.68-8.72z" />
          <path fill="#FBBC05" d="M5.36 14.5c-.24-.72-.38-1.49-.38-2.3s.14-1.58.38-2.3L1.5 6.9C.54 8.84 0 11 0 13.3c0 2.3.54 4.46 1.5 6.4l3.86-3.2z" />
          <path fill="#34A853" d="M12 23c3.24 0 5.97-1.07 7.96-2.91l-3.74-2.9c-1.1.74-2.51 1.18-4.22 1.18-3.08 0-5.73-2.49-6.64-5.46L1.5 16.12C3.4 19.95 7.35 22.6 12 23z" />
        </svg>
        <span>Google</span>
      </button>
      <button
        type="button"
        @click="socialLogin('github')"
        class="flex items-center justify-center space-x-2 py-2.5 px-4 rounded-xl border border-[var(--color-border)] hover:border-gray-300 dark:hover:border-gray-600 bg-[var(--color-surface)] text-[var(--color-text)] font-semibold text-xs transition-all shadow-sm active:scale-98 cursor-pointer"
      >
        <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24">
          <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482C19.138 20.197 22 16.44 22 12.017 22 6.484 17.522 2 12 2z" />
        </svg>
        <span>GitHub</span>
      </button>
    </div>

    <!-- Footer -->
    <template #footer>
      {{ t('auth.dont_have_account') }}
      <Link
        href="/auth/register/"
        class="font-semibold text-[var(--color-primary)] hover:text-[var(--color-primary-hover)] transition-colors underline decoration-2 decoration-transparent hover:decoration-[var(--color-primary)]"
      >
        {{ t('auth.create_one') }}
      </Link>
    </template>
  </AuthLayout>
</template>
