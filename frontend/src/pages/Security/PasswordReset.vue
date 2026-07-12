<script setup lang="ts">
import { useForm, Link } from "@inertiajs/vue3";
import { useForm as useVeeForm, useField } from "vee-validate";
import { toTypedSchema } from "@/composables/zodSchema";
import { z } from "zod";
import AuthLayout from "@/layouts/AuthLayout.vue";
import { useFormErrors } from "@/composables/useFormErrors";
import { useI18n } from "@/composables/useI18n";

const { t } = useI18n();

const resetSchema = toTypedSchema(
  z.object({
    email: z
      .string()
      .min(1, t("password_reset.email_required"))
      .email(t("password_reset.email_invalid")),
  })
);

const { handleSubmit, errors: clientErrors } = useVeeForm({
  validationSchema: resetSchema,
});

const { value: email } = useField<string>("email");
const inertiaForm = useForm({ email: "" });
const { fieldErrors, hasGeneralError, generalError } = useFormErrors();

const onSubmit = handleSubmit((values) => {
  inertiaForm.email = values.email;
  inertiaForm.post("/accounts/password/reset/");
});
</script>

<template>
  <AuthLayout :title="t('password_reset.title')" :subtitle="t('password_reset.subtitle')">
    <!-- General Error Alert -->
    <div
      v-if="hasGeneralError"
      class="mb-6 rounded-xl bg-[var(--color-danger)]/10 border border-[var(--color-danger)]/20 p-4 text-sm text-[var(--color-danger)] flex items-start space-x-2"
    >
      <span>{{ generalError }}</span>
    </div>

    <form @submit.prevent="onSubmit" class="space-y-5">
      <div>
        <label for="email" class="block text-sm font-semibold text-[var(--color-text)] mb-1.5">
          {{ t('password_reset.email_label') }}
        </label>
        <input
          id="email"
          v-model="email"
          type="email"
          autocomplete="email"
          class="w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-muted)] px-4 py-3 text-sm outline-none premium-input text-[var(--color-text)]"
          :class="{
            'border-[var(--color-danger)]': clientErrors.email || fieldErrors.email,
          }"
        />
        <p v-if="clientErrors.email || fieldErrors.email" class="mt-1.5 text-xs text-[var(--color-danger)] font-medium">
          {{ clientErrors.email || fieldErrors.email }}
        </p>
      </div>

      <button
        type="submit"
        :disabled="inertiaForm.processing"
        class="w-full rounded-xl bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-primary-hover)] py-3 text-sm font-semibold text-white transition-all shadow-md hover:shadow-lg disabled:opacity-50 cursor-pointer"
      >
        <span v-if="!inertiaForm.processing">{{ t('password_reset.send_btn') }}</span>
        <span v-else>{{ t('common.sending') }}</span>
      </button>
    </form>

    <template #footer>
      {{ t('password_reset_done.return_to') }}
      <Link href="/auth/login/" class="font-semibold text-[var(--color-primary)] hover:underline">
        {{ t('common.sign_in') }}
      </Link>
    </template>
  </AuthLayout>
</template>
