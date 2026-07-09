<script setup lang="ts">
interface Props {
  title: string;
  subtitle?: string;
}

defineProps<Props>();
</script>

<template>
  <div class="relative min-h-screen flex items-center justify-center px-4 py-16 bg-[var(--color-surface-muted)] overflow-hidden transition-colors duration-300">
    <!-- Glow Effects in Background -->
    <div class="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-[var(--color-primary)]/10 blur-[120px] pointer-events-none"></div>
    <div class="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-[var(--color-primary)]/15 blur-[120px] pointer-events-none"></div>

    <div class="relative w-full max-w-md z-10">
      <!-- Header -->
      <div class="text-center mb-8">
        <!-- Logo Container -->
        <div class="mx-auto w-14 h-14 rounded-2xl bg-gradient-to-tr from-[var(--color-primary-hover)] to-[var(--color-primary)] flex items-center justify-center mb-5 shadow-lg shadow-indigo-500/20 transform transition-transform hover:scale-105 duration-300">
          <svg
            class="w-7 h-7 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2.5"
              d="M13 10V3L4 14h7v7l9-11h-7z"
            />
          </svg>
        </div>

        <h1 class="text-3xl font-extrabold text-[var(--color-text)] tracking-tight">
          {{ title }}
        </h1>
        <p v-if="subtitle" class="mt-2.5 text-sm text-[var(--color-text-muted)] font-medium max-w-sm mx-auto leading-relaxed">
          {{ subtitle }}
        </p>
      </div>

      <!-- Card -->
      <div class="glass-panel rounded-3xl shadow-xl p-8 sm:p-10 transition-all duration-300 border border-[var(--color-border)]">
        <slot />
      </div>

      <!-- Footer Links -->
      <div class="mt-8 text-center text-sm text-[var(--color-text-muted)] font-medium">
        <slot name="footer" />
      </div>
    </div>
  </div>
</template>
