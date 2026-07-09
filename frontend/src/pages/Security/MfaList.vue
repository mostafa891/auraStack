<script setup lang="ts">
import { Link } from "@inertiajs/vue3";
import AuthLayout from "@/layouts/AuthLayout.vue";

interface Props {
  totp_active: boolean;
}

defineProps<Props>();
</script>

<template>
  <AuthLayout title="Two-Factor Authentication (2FA)" subtitle="Protect your account by requiring an extra verification code at login">
    <div class="space-y-6">
      <div class="flex items-start space-x-4">
        <div class="p-2.5 rounded-xl bg-[var(--color-primary)]/10 text-[var(--color-primary)] flex-shrink-0">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
          </svg>
        </div>
        <div>
          <h3 class="text-sm font-semibold text-[var(--color-text)]">Authenticator App (TOTP)</h3>
          <p class="text-xs text-[var(--color-text-muted)] mt-1 leading-relaxed">
            Generate one-time verification codes using mobile applications like Google Authenticator, Microsoft Authenticator, or 1Password.
          </p>
        </div>
      </div>

      <div class="pt-5 border-t border-[var(--color-border)] flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <span class="text-xs text-[var(--color-text-muted)] font-medium">Status:</span>
          <span
            v-if="totp_active"
            class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-green-500/10 text-green-500 border border-green-500/20"
          >
            Active / مفعل
          </span>
          <span
            v-else
            class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[var(--color-text-muted)]/10 text-[var(--color-text-muted)] border border-[var(--color-border)]"
          >
            Inactive / معطل
          </span>
        </div>

        <div>
          <Link
            v-if="totp_active"
            href="/auth/mfa/totp/deactivate/"
            class="px-4 py-2 rounded-lg text-xs font-medium bg-[var(--color-danger)]/10 hover:bg-[var(--color-danger)]/20 text-[var(--color-danger)] transition-all cursor-pointer inline-block"
          >
            Deactivate
          </Link>
          <Link
            v-else
            href="/auth/mfa/totp/activate/"
            class="px-4 py-2 rounded-lg text-xs font-medium bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white transition-all shadow-md shadow-indigo-500/10 cursor-pointer inline-block"
          >
            Set Up 2FA
          </Link>
        </div>
      </div>
    </div>

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
