<script setup lang="ts">
import { useForm, Link } from "@inertiajs/vue3";
import AuthLayout from "@/layouts/AuthLayout.vue";
import { useFormErrors } from "@/composables/useFormErrors";
import { useI18n } from "@/composables/useI18n";

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
const { t, locale } = useI18n();

const { fieldErrors, hasGeneralError, generalError } = useFormErrors();

const inertiaForm = useForm({
  account: "",
});

const disconnectAccount = (accountId: number) => {
  if (confirm(t("social_connections.disconnect_confirm"))) {
    inertiaForm.account = String(accountId);
    inertiaForm.post("/auth/social/connections/");
  }
};
</script>

<template>
  <AuthLayout :title="t('social_connections.title')" :subtitle="t('social_connections.subtitle')">
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
        <h3 class="text-sm font-semibold text-[var(--color-text)]">
          {{ t('social_connections.active_connections') }}
        </h3>
        <p class="text-xs text-[var(--color-text-muted)]">
          {{ t('social_connections.active_desc') }}
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
              {{ t('social_connections.disconnect_btn') }}
            </button>
          </div>
        </div>

        <div
          v-else
          class="p-4 rounded-xl border border-dashed border-[var(--color-border)] text-center text-xs text-[var(--color-text-muted)]"
        >
          {{ t('social_connections.no_connections') }}
        </div>
      </div>

      <!-- Add new connections -->
      <div class="space-y-3 pt-5 border-t border-[var(--color-border)]">
        <h3 class="text-sm font-semibold text-[var(--color-text)]">
          {{ t('social_connections.add_connection') }}
        </h3>
        <p class="text-xs text-[var(--color-text-muted)] leading-relaxed">
          {{ t('social_connections.add_desc') }}
        </p>

        <div class="flex flex-wrap gap-3">
          <a
            v-for="provider in providers"
            :key="provider.id"
            :href="`/accounts/${provider.id}/login/?process=connect`"
            class="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] text-[var(--color-text)] hover:bg-[var(--color-surface-muted)] text-xs font-bold transition-all shadow-xs cursor-pointer capitalize"
          >
            <span>🔗</span>
            <span>{{ provider.name }}</span>
          </a>
        </div>
        <div
          v-if="providers.filter(p => !accounts.some(a => a.provider === p.id)).length === 0"
          class="p-3 rounded-xl bg-[var(--color-surface-muted)] text-center text-xs text-[var(--color-text-muted)]"
        >
          {{ locale === 'ar' ? 'جميع الخدمات المتاحة مرتبطة بالفعل.' : 'All available providers are already connected.' }}
        </div>
      </div>
    </div>

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
