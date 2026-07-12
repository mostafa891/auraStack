<script setup lang="ts">
import { useForm, Link } from "@inertiajs/vue3";
import { useForm as useVeeForm, useField } from "vee-validate";
import { toTypedSchema } from "@/composables/zodSchema";
import { z } from "zod";
import AuthLayout from "@/layouts/AuthLayout.vue";
import { useFormErrors } from "@/composables/useFormErrors";
import { useI18n } from "@/composables/useI18n";

const { t } = useI18n();

const deactivateSchema = toTypedSchema(
  z.object({
    password: z.string().min(1, t("mfa.deactivate_password_required")),
  })
);

const { handleSubmit, errors: clientErrors } = useVeeForm({
  validationSchema: deactivateSchema,
});

const { value: password } = useField<string>("password");

const inertiaForm = useForm({
  password: "",
});

const { fieldErrors, hasGeneralError, generalError } = useFormErrors();

const onSubmit = handleSubmit((values) => {
  inertiaForm.password = values.password;
  inertiaForm.post("/auth/mfa/totp/deactivate/");
});
</script>

<template>
  <AuthLayout :title="t('mfa.deactivate_title')" :subtitle="t('mfa.deactivate_subtitle')">
    <!-- General Error Alert -->
    <div
      v-if="hasGeneralError"
      class="mb-6 rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-700"
    >
      {{ generalError }}
    </div>

    <div class="space-y-6">
      <p class="text-sm text-[var(--color-text-muted)] text-center leading-relaxed">
        {{ t('mfa.deactivate_desc') }}
      </p>

      <form @submit.prevent="onSubmit" class="space-y-4">
        <div>
          <label
            for="password"
            class="block text-sm font-medium text-[var(--color-text)] mb-1.5"
          >
            {{ t('mfa.deactivate_label') }}
          </label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            class="w-full rounded-lg border border-[var(--color-border)] bg-[var(--color-surface-muted)] text-[var(--color-text)] px-4 py-2.5 text-sm outline-none transition-colors focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"
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

        <button
          type="submit"
          :disabled="inertiaForm.processing"
          class="w-full rounded-lg bg-[var(--color-danger)] px-4 py-2.5 text-sm font-medium text-white transition-colors hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer shadow-md shadow-red-500/10"
        >
          <span v-if="!inertiaForm.processing">{{ t('mfa.confirm_deactivate_btn') }}</span>
          <span v-else>{{ t('mfa.deactivating_btn') }}</span>
        </button>
      </form>
    </div>

    <template #footer>
      <Link
        href="/auth/mfa/"
        class="font-medium text-[var(--color-primary)] hover:text-[var(--color-primary-hover)] transition-colors"
      >
        {{ t('mfa.cancel_return') }}
      </Link>
    </template>
  </AuthLayout>
</template>
