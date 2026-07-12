<script setup lang="ts">
import { useForm, Link } from "@inertiajs/vue3";
import { useForm as useVeeForm, useField } from "vee-validate";
import { toTypedSchema } from "@/composables/zodSchema";
import { z } from "zod";
import AuthLayout from "@/layouts/AuthLayout.vue";
import { useFormErrors } from "@/composables/useFormErrors";
import { useI18n } from "@/composables/useI18n";

const props = defineProps<{
  token_fail: boolean;
}>();

const { t } = useI18n();

const newPasswordSchema = toTypedSchema(
  z.object({
    password: z
      .string()
      .min(8, t("password_reset_key.password_length")),
    password_confirm: z
      .string()
      .min(1, t("password_reset_key.confirm_required")),
  }).refine((data) => data.password === data.password_confirm, {
    message: t("password_reset_key.password_mismatch"),
    path: ["password_confirm"],
  })
);

const { handleSubmit, errors: clientErrors } = useVeeForm({
  validationSchema: newPasswordSchema,
});

const { value: password } = useField<string>("password");
const { value: password_confirm } = useField<string>("password_confirm");

const inertiaForm = useForm({
  password: "",
  password_confirm: "",
});
const { fieldErrors, hasGeneralError, generalError } = useFormErrors();

const onSubmit = handleSubmit((values) => {
  inertiaForm.password = values.password;
  inertiaForm.password_confirm = values.password_confirm;
  inertiaForm.post(window.location.pathname);
});
</script>

<template>
  <AuthLayout :title="t('password_reset_key.title')" :subtitle="t('password_reset_key.subtitle')">
    
    <!-- Token Fail State -->
    <div v-if="token_fail" class="text-center py-6 space-y-4">
      <div class="w-16 h-16 bg-red-50 dark:bg-red-950/20 text-red-500 rounded-full flex items-center justify-center mx-auto text-2xl">
        ⚠️
      </div>
      <h3 class="text-base font-bold text-[var(--color-text)]">{{ t('password_reset_key.invalid_title') }}</h3>
      <p class="text-sm text-[var(--color-text-muted)] max-w-sm mx-auto leading-relaxed">
        {{ t('password_reset_key.invalid_desc') }}
      </p>
      <div class="pt-4">
        <Link
          href="/accounts/password/reset/"
          class="inline-block px-5 py-2.5 rounded-xl bg-[var(--color-primary)] text-white text-xs font-semibold hover:bg-[var(--color-primary-hover)] transition-all"
        >
          {{ t('common.request_new_link') }}
        </Link>
      </div>
    </div>

    <!-- Active Reset Form -->
    <div v-else>
      <!-- General Error Alert -->
      <div
        v-if="hasGeneralError"
        class="mb-6 rounded-xl bg-[var(--color-danger)]/10 border border-[var(--color-danger)]/20 p-4 text-sm text-[var(--color-danger)] flex items-start space-x-2"
      >
        <span>{{ generalError }}</span>
      </div>

      <form @submit.prevent="onSubmit" class="space-y-5">
        <!-- New Password Field -->
        <div>
          <label for="password" class="block text-sm font-semibold text-[var(--color-text)] mb-1.5">
            {{ t('password_reset_key.new_password') }}
          </label>
          <input
            id="password"
            v-model="password"
            type="password"
            autocomplete="new-password"
            class="w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-muted)] px-4 py-3 text-sm outline-none premium-input text-[var(--color-text)]"
            :class="{
              'border-[var(--color-danger)]': clientErrors.password || fieldErrors.password,
            }"
          />
          <p v-if="clientErrors.password || fieldErrors.password" class="mt-1.5 text-xs text-[var(--color-danger)] font-medium">
            {{ clientErrors.password || fieldErrors.password }}
          </p>
        </div>

        <!-- Confirm Password Field -->
        <div>
          <label for="password_confirm" class="block text-sm font-semibold text-[var(--color-text)] mb-1.5">
            {{ t('password_reset_key.confirm_password') }}
          </label>
          <input
            id="password_confirm"
            v-model="password_confirm"
            type="password"
            autocomplete="new-password"
            class="w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-muted)] px-4 py-3 text-sm outline-none premium-input text-[var(--color-text)]"
            :class="{
              'border-[var(--color-danger)]': clientErrors.password_confirm || fieldErrors.password_confirm,
            }"
          />
          <p v-if="clientErrors.password_confirm || fieldErrors.password_confirm" class="mt-1.5 text-xs text-[var(--color-danger)] font-medium">
            {{ clientErrors.password_confirm || fieldErrors.password_confirm }}
          </p>
        </div>

        <button
          type="submit"
          :disabled="inertiaForm.processing"
          class="w-full rounded-xl bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-primary-hover)] py-3 text-sm font-semibold text-white transition-all shadow-md hover:shadow-lg disabled:opacity-50 cursor-pointer"
        >
          <span v-if="!inertiaForm.processing">{{ t('common.change_password') }}</span>
          <span v-else>{{ t('common.saving') }}</span>
        </button>
      </form>
    </div>

    <template #footer>
      {{ t('password_reset_done.return_to') }}
      <Link href="/auth/login/" class="font-semibold text-[var(--color-primary)] hover:underline">
        {{ t('common.sign_in') }}
      </Link>
    </template>
  </AuthLayout>
</template>
