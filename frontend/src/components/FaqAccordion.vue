<script setup lang="ts">
import { ref } from 'vue';

defineProps<{
  items: Array<{ question: string; answer: string }>;
}>();

const openIndex = ref<number | null>(0);

function toggle(index: number) {
  openIndex.value = openIndex.value === index ? null : index;
}
</script>

<template>
  <div class="space-y-4 max-w-4xl mx-auto">
    <div
      v-for="(item, idx) in items"
      :key="idx"
      class="border border-slate-800/80 rounded-2xl bg-slate-900/40 backdrop-blur-md overflow-hidden transition-colors"
      :class="{ 'border-indigo-500/40 bg-slate-900/80': openIndex === idx }"
    >
      <button
        @click="toggle(idx)"
        class="w-full px-6 py-5 flex items-center justify-between text-start cursor-pointer transition-colors hover:text-indigo-400"
      >
        <span class="text-lg font-semibold text-slate-100">{{ item.question }}</span>
        <div
          class="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 shrink-0 transition-transform duration-300"
          :class="{ 'rotate-180 bg-indigo-600/20 text-indigo-400': openIndex === idx }"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      <div
        v-if="openIndex === idx"
        class="px-6 pb-6 pt-1 text-slate-300 text-sm leading-relaxed border-t border-slate-800/40 mt-1"
      >
        {{ item.answer }}
      </div>
    </div>
  </div>
</template>
