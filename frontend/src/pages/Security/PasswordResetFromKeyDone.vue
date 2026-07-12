<script setup lang="ts">
import { Link } from "@inertiajs/vue3";
import AuthLayout from "@/layouts/AuthLayout.vue";
import { useI18n } from "@/composables/useI18n";

const { t } = useI18n();
</script>

<template>
  <AuthLayout :title="t('password_reset_key_done.title')" :subtitle="t('password_reset_key_done.subtitle')">
    <div class="text-center py-6 space-y-4">
      <div class="w-16 h-16 bg-emerald-50 dark:bg-emerald-950/20 text-emerald-500 rounded-full flex items-center justify-center mx-auto text-2xl">
        🎉
      </div>
      <p class="text-sm text-[var(--color-text-muted)] max-w-sm mx-auto leading-relaxed">
        {{ t('password_reset_key_done.done_info') }}
      </p>
      
      <div class="pt-4">
        <Link
          href="/auth/login/"
          class="inline-block px-6 py-2.5 rounded-xl bg-[var(--color-primary)] text-white text-xs font-semibold hover:bg-[var(--color-primary-hover)] transition-all shadow-md hover:shadow-lg"
        >
          {{ t('common.sign_in') }}
        </Link>
      </div>
    </div>
  </AuthLayout>
</template>
