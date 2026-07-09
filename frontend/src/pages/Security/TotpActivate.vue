<script setup lang="ts">
import { useForm, Link } from "@inertiajs/vue3";
import { useForm as useVeeForm, useField } from "vee-validate";
import { toTypedSchema } from "@/composables/zodSchema";
import { z } from "zod";
import AuthLayout from "@/layouts/AuthLayout.vue";
import { useFormErrors } from "@/composables/useFormErrors";

interface Props {
  totp_svg: string;
  totp_key: string;
}

defineProps<Props>();

// Zod validation for 6-digit TOTP code
const activateSchema = toTypedSchema(
  z.object({
    code: z
      .string()
      .min(6, "Code must be 6 digits.")
      .max(6, "Code must be 6 digits.")
      .regex(/^\d+$/, "Code must contain only numbers."),
  })
);

const { handleSubmit, errors: clientErrors } = useVeeForm({
  validationSchema: activateSchema,
});

const { value: code } = useField<string>("code");

const inertiaForm = useForm({
  code: "",
});

const { fieldErrors, hasGeneralError, generalError } = useFormErrors();

const onSubmit = handleSubmit((values) => {
  inertiaForm.code = values.code;
  inertiaForm.post("/auth/mfa/totp/activate/");
});
</script>

<template>
  <AuthLayout title="Enable 2FA" subtitle="Secure your account using two-factor authentication">
    <!-- General Error Alert -->
    <div
      v-if="hasGeneralError"
      class="mb-6 rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-700"
    >
      {{ generalError }}
    </div>

    <div class="space-y-6">
      <!-- Step 1: Scan QR Code -->
      <div class="space-y-3">
        <div class="flex items-center space-x-2 text-sm font-semibold text-[var(--color-text)]">
          <span class="w-5 h-5 rounded-full bg-[var(--color-primary)]/10 text-[var(--color-primary)] flex items-center justify-center text-xs">1</span>
          <span>Scan this QR Code</span>
        </div>
        <p class="text-xs text-[var(--color-text-muted)] leading-relaxed">
          Open your authenticator app (such as Google Authenticator, Authy, or 1Password) and scan the QR code below:
        </p>

        <!-- QR Code Container -->
        <div class="flex justify-center p-4 bg-white rounded-xl border border-[var(--color-border)]">
          <div class="w-48 h-48 text-black flex items-center justify-center" v-html="totp_svg"></div>
        </div>
      </div>

      <!-- Key Fallback -->
      <div class="p-3 bg-[var(--color-surface-muted)] rounded-xl border border-[var(--color-border)] space-y-1">
        <span class="text-[10px] uppercase font-semibold text-[var(--color-text-muted)] tracking-wider">Cannot scan? Enter key manually:</span>
        <code class="block text-xs font-mono text-[var(--color-primary)] select-all break-all">{{ totp_key }}</code>
      </div>

      <!-- Step 2: Verify Code -->
      <div class="space-y-4 pt-5 border-t border-[var(--color-border)]">
        <div class="flex items-center space-x-2 text-sm font-semibold text-[var(--color-text)]">
          <span class="w-5 h-5 rounded-full bg-[var(--color-primary)]/10 text-[var(--color-primary)] flex items-center justify-center text-xs">2</span>
          <span>Enter Verification Code</span>
        </div>

        <form @submit.prevent="onSubmit" class="space-y-4">
          <div>
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
            <span v-if="!inertiaForm.processing">Activate 2FA</span>
            <span v-else>Activating...</span>
          </button>
        </form>
      </div>
    </div>

    <template #footer>
      <Link
        href="/auth/mfa/"
        class="font-medium text-[var(--color-primary)] hover:text-[var(--color-primary-hover)] transition-colors"
      >
        ← Cancel and return
      </Link>
    </template>
  </AuthLayout>
</template>
