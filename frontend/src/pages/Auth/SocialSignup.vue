<script setup lang="ts">
import { useForm, Link } from "@inertiajs/vue3";
import { useForm as useVeeForm, useField } from "vee-validate";
import { toTypedSchema } from "@/composables/zodSchema";
import { z } from "zod";
import AuthLayout from "@/layouts/AuthLayout.vue";
import { useFormErrors } from "@/composables/useFormErrors";

interface Props {
  provider: string;
}

defineProps<Props>();

const signupSchema = toTypedSchema(
  z.object({
    email: z
      .string()
      .min(1, "Email is required.")
      .email("Please enter a valid email address."),
  })
);

const { handleSubmit, errors: clientErrors } = useVeeForm({
  validationSchema: signupSchema,
});

const { value: email } = useField<string>("email");

const inertiaForm = useForm({
  email: "",
});
const { fieldErrors, hasGeneralError, generalError } = useFormErrors();

const onSubmit = handleSubmit((values) => {
  inertiaForm.email = values.email;
  inertiaForm.post("/auth/social/signup/");
});
</script>

<template>
  <AuthLayout title="Complete Signup" :subtitle="`Finish setting up your account via ${provider}`">
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
          Confirm your email address
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

      <!-- Submit Button -->
      <button
        type="submit"
        :disabled="inertiaForm.processing"
        class="w-full rounded-xl bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-primary-hover)] py-3 text-sm font-semibold
               text-white transition-all shadow-md shadow-indigo-500/10 hover:shadow-lg hover:shadow-indigo-500/20
               disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer active:scale-98"
      >
        <span v-if="!inertiaForm.processing">Complete Sign Up</span>
        <span v-else>Completing...</span>
      </button>
    </form>

    <!-- Footer -->
    <template #footer>
      <Link
        href="/auth/login/"
        class="font-semibold text-[var(--color-primary)] hover:text-[var(--color-primary-hover)] transition-colors underline decoration-2 decoration-transparent hover:decoration-[var(--color-primary)]"
      >
        Cancel and go back
      </Link>
    </template>
  </AuthLayout>
</template>
