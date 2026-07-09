<script setup lang="ts">
import { useForm, Link } from "@inertiajs/vue3";
import { useForm as useVeeForm, useField } from "vee-validate";
import { toTypedSchema } from "@/composables/zodSchema";
import { z } from "zod";
import AuthLayout from "@/layouts/AuthLayout.vue";
import { useFormErrors } from "@/composables/useFormErrors";

// Zod validation for 6-digit TOTP code
const authenticateSchema = toTypedSchema(
  z.object({
    code: z
      .string()
      .min(6, "Code must be 6 digits.")
      .max(6, "Code must be 6 digits.")
      .regex(/^\d+$/, "Code must contain only numbers."),
  })
);

const { handleSubmit, errors: clientErrors } = useVeeForm({
  validationSchema: authenticateSchema,
});

const { value: code } = useField<string>("code");

const inertiaForm = useForm({
  code: "",
});

const { fieldErrors, hasGeneralError, generalError } = useFormErrors();

const onSubmit = handleSubmit((values) => {
  inertiaForm.code = values.code;
  inertiaForm.post("/auth/mfa/authenticate/");
});
</script>

<template>
  <AuthLayout title="Two-Factor Authentication" subtitle="Enter the 6-digit verification code from your authenticator app to log in">
    <!-- General Error Alert -->
    <div
      v-if="hasGeneralError"
      class="mb-6 rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-700"
    >
      {{ generalError }}
    </div>

    <form @submit.prevent="onSubmit" class="space-y-5">
      <div>
        <label
          for="code"
          class="block text-sm font-medium text-[var(--color-text)] mb-1.5 text-center"
        >
          Verification Code
        </label>
        <input
          id="code"
          v-model="code"
          type="text"
          placeholder="6-digit code"
          required
          autocomplete="one-time-code"
          class="w-full rounded-lg border border-[var(--color-border)] bg-[var(--color-surface-muted)] text-[var(--color-text)] px-4 py-2.5 text-center text-lg font-mono tracking-[0.5em] outline-none transition-colors focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"
          :class="{
            'border-[var(--color-danger)]': clientErrors.code || fieldErrors.code,
          }"
        />
        <p
          v-if="clientErrors.code || fieldErrors.code"
          class="mt-1.5 text-xs text-[var(--color-danger)] text-center"
        >
          {{ clientErrors.code || fieldErrors.code }}
        </p>
      </div>

      <button
        type="submit"
        :disabled="inertiaForm.processing"
        class="w-full rounded-lg bg-[var(--color-primary)] px-4 py-2.5 text-sm font-medium
               text-white transition-colors hover:bg-[var(--color-primary-hover)]
               disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer shadow-md shadow-indigo-500/10"
      >
        <span v-if="!inertiaForm.processing">Verify Code</span>
        <span v-else>Verifying...</span>
      </button>
    </form>

    <template #footer>
      <Link
        href="/auth/login/"
        class="font-medium text-[var(--color-primary)] hover:text-[var(--color-primary-hover)] transition-colors"
      >
        ← Back to Login
      </Link>
    </template>
  </AuthLayout>
</template>
