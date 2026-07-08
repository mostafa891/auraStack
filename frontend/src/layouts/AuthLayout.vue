<script setup lang="ts">
/**
 * AuthLayout — Layout مشترك لكل صفحات المصادقة.
 *
 * بيوفر:
 * - هيكل مركزي (centered card) مع خلفية نظيفة
 * - عنوان ووصف ديناميكيين عبر Props
 * - Slot للمحتوى الداخلي (Form)
 * - Slot للروابط السفلية (مثل "عندك حساب؟ سجل دخول")
 */

interface Props {
  title: string;
  subtitle?: string;
}

defineProps<Props>();
</script>

<template>
  <div class="min-h-screen flex items-center justify-center px-4 py-12 bg-[var(--color-surface-muted)]">
    <div class="w-full max-w-md">
      <!-- Header -->
      <div class="text-center mb-8">
        <!-- Logo Slot — غيّره لشعارك -->
        <div
          class="mx-auto w-12 h-12 rounded-xl bg-[var(--color-primary)] flex items-center justify-center mb-4"
        >
          <svg
            class="w-6 h-6 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M13 10V3L4 14h7v7l9-11h-7z"
            />
          </svg>
        </div>

        <h1 class="text-2xl font-bold text-[var(--color-text)]">
          {{ title }}
        </h1>
        <p v-if="subtitle" class="mt-2 text-sm text-[var(--color-text-muted)]">
          {{ subtitle }}
        </p>
      </div>

      <!-- Card -->
      <div
        class="bg-[var(--color-surface)] rounded-2xl shadow-sm border border-[var(--color-border)] p-8"
      >
        <slot />
      </div>

      <!-- Footer Links -->
      <div class="mt-6 text-center text-sm text-[var(--color-text-muted)]">
        <slot name="footer" />
      </div>
    </div>
  </div>
</template>
