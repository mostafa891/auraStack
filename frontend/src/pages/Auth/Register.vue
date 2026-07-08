<script setup lang="ts">
/**
 * Register Page — صفحة إنشاء حساب جديد.
 *
 * التدفق:
 * 1. المستخدم يملأ email + password + password_confirm
 * 2. Zod بيتحقق (بما فيه تطابق كلمتي المرور) في المتصفح
 * 3. Inertia بيبعت POST لـ /auth/register/
 * 4. Django بيتحقق ويرجع redirect أو errors
 */

import { useForm, Link } from "@inertiajs/vue3";
import { useForm as useVeeForm, useField } from "vee-validate";
import { toTypedSchema } from "@/composables/zodSchema";
import { z } from "zod";
import AuthLayout from "@/layouts/AuthLayout.vue";
import { useFormErrors } from "@/composables/useFormErrors";

// ============================
// Zod Schema — قواعد التحقق مع مطابقة كلمات المرور
// ============================
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

// ============================
// VeeValidate Form
// ============================
const { handleSubmit, errors: clientErrors } = useVeeForm({
  validationSchema: registerSchema,
});

const { value: email } = useField<string>("email");
const { value: password } = useField<string>("password");
const { value: passwordConfirm } = useField<string>("password_confirm");

// ============================
// Inertia Form + Server Errors
// ============================
const inertiaForm = useForm({
  email: "",
  password: "",
  password_confirm: "",
});
const { fieldErrors, hasGeneralError, generalError } = useFormErrors();

// ============================
// Submit Handler
// ============================
const onSubmit = handleSubmit((values) => {
  inertiaForm.email = values.email;
  inertiaForm.password = values.password;
  inertiaForm.password_confirm = values.password_confirm;
  inertiaForm.post("/auth/register/");
});
</script>

<template>
  <AuthLayout title="Create an account" subtitle="Get started in seconds">
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
          autocomplete="new-password"
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

      <!-- Confirm Password Field -->
      <div>
        <label
          for="password_confirm"
          class="block text-sm font-medium text-[var(--color-text)] mb-1.5"
        >
          Confirm password
        </label>
        <input
          id="password_confirm"
          v-model="passwordConfirm"
          type="password"
          autocomplete="new-password"
          class="w-full rounded-lg border border-[var(--color-border)] px-4 py-2.5 text-sm
                 outline-none transition-colors
                 focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"
          :class="{
            'border-[var(--color-danger)]':
              clientErrors.password_confirm || fieldErrors.password_confirm,
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
        <span v-if="!inertiaForm.processing">Create account</span>
        <span v-else>Creating...</span>
      </button>
    </form>

    <!-- Footer (Inertia Link) -->
    <template #footer>
      Already have an account?
      <Link
        href="/auth/login/"
        class="font-medium text-[var(--color-primary)] hover:text-[var(--color-primary-hover)] transition-colors"
      >
        Sign in
      </Link>
    </template>
  </AuthLayout>
</template>
