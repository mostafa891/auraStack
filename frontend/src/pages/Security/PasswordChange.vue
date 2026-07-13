<script setup lang="ts">
import { useForm, Link } from "@inertiajs/vue3";
import { useForm as useVeeForm, useField } from "vee-validate";
import { toTypedSchema } from "@/composables/zodSchema";
import { z } from "zod";
import AuthLayout from "@/layouts/AuthLayout.vue";
import { useFormErrors } from "@/composables/useFormErrors";
import { useI18n } from "@/composables/useI18n";

const { t } = useI18n();

// Zod validation schema using local translation helper
const passwordChangeSchema = toTypedSchema(
  z.object({
    old_password: z.string().min(1, t("password_change.error_required_old")),
    password: z
      .string()
      .min(8, t("password_change.error_length_new"))
      .refine((val) => !/^\d+$/.test(val), t("password_change.error_numeric_new")),
    password_confirm: z.string().min(1, t("password_change.error_confirm_required")),
  }).refine((data) => data.password === data.password_confirm, {
    message: t("password_change.error_mismatch"),
    path: ["password_confirm"],
  })
);

const { handleSubmit, errors: clientErrors } = useVeeForm({
  validationSchema: passwordChangeSchema,
});

const { value: oldPassword } = useField<string>("old_password");
const { value: password } = useField<string>("password");
const { value: passwordConfirm } = useField<string>("password_confirm");

const inertiaForm = useForm({
  old_password: "",
  password: "",
  password_confirm: "",
});

const { fieldErrors, hasGeneralError, generalError } = useFormErrors();

const onSubmit = handleSubmit((values) => {
  inertiaForm.old_password = values.old_password;
  inertiaForm.password = values.password;
  inertiaForm.password_confirm = values.password_confirm;
  inertiaForm.post("/auth/password/change/");
});
</script>

<template>
  <AuthLayout :title="t('password_change.title')" :subtitle="t('password_change.subtitle')">
    <!-- General Error Alert -->
    <div
      v-if="hasGeneralError"
      class="mb-6 rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-700"
    >
      {{ generalError }}
    </div>

    <form @submit.prevent="onSubmit" class="space-y-5">
      <!-- Current Password Field -->
      <div>
        <label
          for="old_password"
          class="block text-sm font-medium text-[var(--color-text)] mb-1.5"
        >
          {{ t('password_change.current_password') }}
        </label>
        <input
          id="old_password"
          v-model="oldPassword"
          type="password"
          class="w-full rounded-lg border border-[var(--color-border)] px-4 py-2.5 text-sm
                 outline-none transition-colors bg-[var(--color-surface-muted)] text-[var(--color-text)]
                 focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"
          :class="{
            'border-[var(--color-danger)]': clientErrors.old_password || fieldErrors.old_password,
          }"
        />
        <p
          v-if="clientErrors.old_password || fieldErrors.old_password"
          class="mt-1.5 text-xs text-[var(--color-danger)]"
        >
          {{ clientErrors.old_password || fieldErrors.old_password }}
        </p>
      </div>

      <!-- New Password Field -->
      <div>
        <label
          for="password"
          class="block text-sm font-medium text-[var(--color-text)] mb-1.5"
        >
          {{ t('password_change.new_password') }}
        </label>
        <input
          id="password"
          v-model="password"
          type="password"
          class="w-full rounded-lg border border-[var(--color-border)] px-4 py-2.5 text-sm
                 outline-none transition-colors bg-[var(--color-surface-muted)] text-[var(--color-text)]
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

      <!-- Confirm New Password Field -->
      <div>
        <label
          for="password_confirm"
          class="block text-sm font-medium text-[var(--color-text)] mb-1.5"
        >
          {{ t('password_change.confirm_new_password') }}
        </label>
        <input
          id="password_confirm"
          v-model="passwordConfirm"
          type="password"
          class="w-full rounded-lg border border-[var(--color-border)] px-4 py-2.5 text-sm
                 outline-none transition-colors bg-[var(--color-surface-muted)] text-[var(--color-text)]
                 focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"
          :class="{
            'border-[var(--color-danger)]': clientErrors.password_confirm || fieldErrors.password_confirm,
          }"
        />
        <p
          v-if="clientErrors.password_confirm || fieldErrors.password_confirm"
          class="mt-1.5 text-xs text-[var(--color-danger)]"
        >
          {{ clientErrors.password_confirm || fieldErrors.password_confirm }}
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
        <span v-if="!inertiaForm.processing">{{ t('password_change.submit_btn') }}</span>
        <span v-else>{{ t('password_change.updating_btn') }}</span>
      </button>
    </form>

    <template #footer>
      <Link
        href="/profile/"
        class="font-medium text-[var(--color-primary)] hover:text-[var(--color-primary-hover)] transition-colors"
      >
        {{ t('mfa.cancel_return') }}
      </Link>
    </template>
  </AuthLayout>
</template>
