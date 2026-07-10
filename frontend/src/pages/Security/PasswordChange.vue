<script setup lang="ts">
import { useForm, Link } from "@inertiajs/vue3";
import { useForm as useVeeForm, useField } from "vee-validate";
import { toTypedSchema } from "@/composables/zodSchema";
import { z } from "zod";
import AuthLayout from "@/layouts/AuthLayout.vue";
import { useFormErrors } from "@/composables/useFormErrors";

// Zod validation schema
const passwordChangeSchema = toTypedSchema(
  z.object({
    old_password: z.string().min(1, "Current password is required."),
    password: z
      .string()
      .min(8, "New password must be at least 8 characters.")
      .refine((val) => !/^\d+$/.test(val), "Password cannot be entirely numeric."),
    password_confirm: z.string().min(1, "Please confirm your new password."),
  }).refine((data) => data.password === data.password_confirm, {
    message: "New passwords do not match.",
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
  <AuthLayout title="Change Password" subtitle="Update your account credentials to keep it secure">
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
          Current Password
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
          New Password
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
          Confirm New Password
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
        <span v-if="!inertiaForm.processing">Change Password</span>
        <span v-else>Updating Password...</span>
      </button>
    </form>

    <template #footer>
      <Link
        href="/profile/"
        class="font-medium text-[var(--color-primary)] hover:text-[var(--color-primary-hover)] transition-colors"
      >
        ← Back to Profile
      </Link>
    </template>
  </AuthLayout>
</template>
