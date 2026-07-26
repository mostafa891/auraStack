<script setup lang="ts">
import { computed } from 'vue';
import { Link } from '@inertiajs/vue3';

export interface PlanFeature {
  feature_text: string;
  is_highlighted?: boolean;
}

export interface PricingPlan {
  id: string;
  name: string;
  description: string;
  price_monthly: string | number;
  price_yearly: string | number;
  currency_symbol?: string;
  max_members?: number;
  is_popular?: boolean;
  badge_text?: string;
  cta_text?: string;
  cta_url?: string;
  features: PlanFeature[];
}

const props = withDefaults(
  defineProps<{
    plan: PricingPlan;
    isYearly?: boolean;
    locale?: string;
    ctaUrl?: string;
  }>(),
  {
    isYearly: false,
    locale: 'en',
    ctaUrl: '/auth/register/',
  }
);

const currency = computed(() => props.plan.currency_symbol || '$');

const price = computed(() => {
  return props.isYearly ? props.plan.price_yearly : props.plan.price_monthly;
});

const billingPeriodText = computed(() => {
  if (props.locale === 'ar') {
    return props.isYearly ? '/ سنوياً' : '/ شهرياً';
  }
  return props.isYearly ? '/ yr' : '/ mo';
});

const defaultCtaText = computed(() => {
  if (props.plan.cta_text) return props.plan.cta_text;
  if (props.plan.id === 'free') {
    return props.locale === 'ar' ? 'ابدأ مجاناً' : 'Get Started Free';
  }
  return props.locale === 'ar' ? 'اشترك الآن' : 'Subscribe Now';
});

const badgeLabel = computed(() => {
  if (props.plan.badge_text) return props.plan.badge_text;
  if (props.plan.is_popular) {
    return props.locale === 'ar' ? 'الأكثر شعبية 🌟' : 'Most Popular 🌟';
  }
  return null;
});

const targetCtaUrl = computed(() => props.plan.cta_url || props.ctaUrl);
</script>

<template>
  <div
    class="relative flex flex-col rounded-3xl p-8 transition-all duration-300 backdrop-blur-xl border group hover:-translate-y-1.5"
    :class="[
      plan.is_popular
        ? 'bg-gradient-to-b from-slate-900/95 via-slate-900/90 to-slate-950/95 border-indigo-500/80 shadow-[0_0_50px_-12px_rgba(99,102,241,0.25)] z-10'
        : 'bg-slate-900/40 border-slate-800/80 hover:border-slate-700/90 hover:bg-slate-900/60 shadow-xl'
    ]"
  >
    <!-- Popular Glow & Badge -->
    <div
      v-if="badgeLabel"
      class="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full text-xs font-extrabold bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white shadow-lg tracking-wide uppercase flex items-center gap-1.5"
    >
      <span class="w-1.5 h-1.5 rounded-full bg-white animate-ping"></span>
      {{ badgeLabel }}
    </div>

    <!-- Header -->
    <div class="mb-6">
      <h3 class="text-2xl font-bold text-slate-100 mb-2 group-hover:text-indigo-300 transition-colors">{{ plan.name }}</h3>
      <p class="text-sm text-slate-400 min-h-[44px] leading-relaxed">{{ plan.description }}</p>
    </div>

    <!-- Pricing -->
    <div class="mb-8 flex items-baseline gap-1.5">
      <span class="text-4xl sm:text-5xl font-extrabold text-white tracking-tight">{{ currency }}{{ price }}</span>
      <span class="text-slate-400 text-sm font-semibold">{{ billingPeriodText }}</span>
    </div>

    <!-- CTA Button -->
    <Link
      :href="targetCtaUrl"
      class="w-full text-center py-3.5 px-6 rounded-xl font-bold transition-all duration-200 mb-8 cursor-pointer shadow-md select-none"
      :class="[
        plan.is_popular
          ? 'bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-600 hover:from-indigo-500 hover:to-purple-500 text-white shadow-indigo-600/30 hover:shadow-indigo-600/50'
          : 'bg-slate-800/90 hover:bg-slate-700 text-slate-200 border border-slate-700/80 hover:border-slate-600'
      ]"
    >
      {{ defaultCtaText }}
    </Link>

    <!-- Features list -->
    <div class="space-y-3.5 mt-auto text-sm">
      <p class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4">
        {{ locale === 'ar' ? 'المميزات المتضمنة:' : 'What\'s included:' }}
      </p>
      <div
        v-for="(feat, idx) in plan.features"
        :key="idx"
        class="flex items-center gap-3 text-slate-300"
      >
        <div
          class="w-5 h-5 rounded-full flex items-center justify-center shrink-0 transition-transform group-hover:scale-110"
          :class="feat.is_highlighted ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30' : 'bg-slate-800/80 text-emerald-400 border border-emerald-500/20'"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
        </div>
        <span :class="feat.is_highlighted ? 'font-semibold text-slate-100' : 'text-slate-300'">
          {{ feat.feature_text }}
        </span>
      </div>
    </div>
  </div>
</template>
