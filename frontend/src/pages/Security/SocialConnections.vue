<script setup lang="ts">
import { useForm, Link } from "@inertiajs/vue3";
import AuthLayout from "@/layouts/AuthLayout.vue";
import { useFormErrors } from "@/composables/useFormErrors";

interface ConnectedAccount {
  id: number;
  provider: string;
  uid: string;
}

interface Provider {
  id: string;
  name: string;
}

interface Props {
  accounts: ConnectedAccount[];
  providers: Provider[];
}

const props = defineProps<Props>();

const { fieldErrors, hasGeneralError, generalError } = useFormErrors();

const inertiaForm = useForm({
  account: "",
});

const disconnectAccount = (accountId: number) => {
  if (confirm("Are you sure you want to disconnect this account?")) {
    inertiaForm.account = String(accountId);
    inertiaForm.post("/auth/social/connections/");
  }
};
</script>

<template>
  <AuthLayout title="Connected Accounts" subtitle="Manage your social logins and linked accounts">
    <!-- General Error Alert -->
    <div
      v-if="hasGeneralError"
      class="mb-6 rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-700"
    >
      {{ generalError }}
    </div>

    <!-- Error in specific fields -->
    <div
      v-if="fieldErrors.account"
      class="mb-6 rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-700"
    >
      {{ fieldErrors.account }}
    </div>

    <div class="space-y-6">
      <!-- Currently Connected Accounts -->
      <div class="space-y-3">
        <h3 class="text-sm font-semibold text-[var(--color-text)]">Active Connections</h3>
        <p class="text-xs text-[var(--color-text-muted)]">
          You can use any of these connected accounts to log in:
        </p>

        <div v-if="accounts.length > 0" class="space-y-2">
          <div
            v-for="account in accounts"
            :key="account.id"
            class="flex items-center justify-between p-3.5 rounded-xl bg-[var(--color-surface-muted)] border border-[var(--color-border)]"
          >
            <div class="flex items-center space-x-3">
              <!-- Provider Icon Placeholder / Logo -->
              <div class="w-8 h-8 rounded-lg bg-[var(--color-primary)]/10 text-[var(--color-primary)] flex items-center justify-center font-bold text-xs uppercase">
                {{ account.provider.substring(0, 2) }}
              </div>
              <div>
                <p class="text-sm font-semibold text-[var(--color-text)] capitalize">{{ account.provider }}</p>
                <p class="text-xs text-[var(--color-text-muted)] truncate max-w-[180px] sm:max-w-[240px]">{{ account.uid }}</p>
              </div>
            </div>

            <button
              @click="disconnectAccount(account.id)"
              class="px-3 py-1.5 rounded-lg text-xs font-medium bg-[var(--color-danger)]/10 hover:bg-[var(--color-danger)]/20 text-[var(--color-danger)] transition-all cursor-pointer"
            >
              Disconnect
            </button>
          </div>
        </div>

        <div
          v-else
          class="p-4 rounded-xl border border-dashed border-[var(--color-border)] text-center text-xs text-[var(--color-text-muted)]"
        >
          No social accounts connected yet.
        </div>
      </div>

      <!-- Add new connections -->
      <div class="space-y-3 pt-5 border-t border-[var(--color-border)]">
        <h3 class="text-sm font-semibold text-[var(--color-text)]">Add New Connection</h3>
        <p class="text-xs text-[var(--color-text-muted)]">
          Link another social account to your profile:
        </p>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
          <a
            v-for="provider in providers.filter(p => !accounts.some(a => a.provider === p.id))"
            :key="provider.id"
            :href="`/accounts/${provider.id}/login/?process=connect`"
            class="flex items-center space-x-3 p-3 rounded-xl border border-[var(--color-border)] hover:border-[var(--color-primary)] transition-all text-[var(--color-text)] hover:bg-[var(--color-primary)]/5"
          >
            <div class="w-8 h-8 rounded-lg bg-[var(--color-primary)]/10 text-[var(--color-primary)] flex items-center justify-center font-bold text-xs uppercase">
              {{ provider.name.substring(0, 2) }}
            </div>
            <span class="text-xs font-semibold">Connect {{ provider.name }}</span>
          </a>
        </div>

        <div
          v-if="providers.filter(p => !accounts.some(a => a.provider === p.id)).length === 0"
          class="p-3 rounded-xl bg-[var(--color-surface-muted)] text-center text-xs text-[var(--color-text-muted)]"
        >
          All available providers are already connected.
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
