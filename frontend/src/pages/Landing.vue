<script setup lang="ts">
import { watchEffect, computed } from "vue";
import { Link } from '@inertiajs/vue3';
import AppHead from '../components/AppHead.vue';
import FaqAccordion from '../components/FaqAccordion.vue';
import { useI18n } from '@/composables/useI18n';

const { t, locale, toggleLocale } = useI18n();

watchEffect(() => {
  document.documentElement.dir = locale.value === "ar" ? "rtl" : "ltr";
  document.documentElement.lang = locale.value;
});

const faqItems = computed(() => {
  if (locale.value === 'ar') {
    return [
      {
        question: "ما الذي يميز auraStack عن باقي القوالب؟",
        answer: "يجمع auraStack بين أمان وقوة Django 5 في الباك إند وسرعة وسلاسة Vue 3 في الفرونت إند عبر جسر Inertia.js الفعّال، بدون الحاجة لكتابة كود معقد لـ REST API أو Serializers."
      },
      {
        question: "هل يدعم القالب بوابات الدفع المحلية والعالمية؟",
        answer: "نعم! يأتي القالب مدمجاً ببنية تحتية متعددة البوابات تشمل Paymob للمنطقة العربية، بجانب Stripe و LemonSqueezy و PayPal و Paddle للمبيعات العالمية."
      },
      {
        question: "هل يمكنني استخراج جزء معين فقط لاستخدامه في مشروعي الحالي؟",
        answer: "بالتأكيد. جميع الموديولات مبنية بشكل مستقل داخل مجلد apps/ (مثل نظام Multi-Tenancy ونظام 2FA/MFA) ويمكن استخراج أي موديول بسهولة وتضمينه في مشروع قائم."
      },
      {
        question: "كيف يتم اختبار جودة النظام وأمانه؟",
        answer: "يتضمن القالب تغطية كاملة بـ Pytest للباك إند واختبارات E2E حقيقية بـ Playwright لمحاكاة حركة المستخدم في المتصفح والتأكد من أمان الجلسات والصلاحيات."
      }
    ];
  }
  return [
    {
      question: "What sets auraStack apart from other boilerplates?",
      answer: "auraStack bridges Django 5 security and Vue 3 SPA user experience using Inertia.js — eliminating unnecessary REST API / Serializer boilerplate."
    },
    {
      question: "Does auraStack support regional & global payment gateways?",
      answer: "Yes! It features a multi-gateway engine supporting Paymob for MENA regional payments alongside Stripe, LemonSqueezy, PayPal, and Paddle."
    },
    {
      question: "Can I extract specific modules into my existing Django app?",
      answer: "Absolutely. All domain modules inside apps/ (such as Multi-tenancy or MFA) are decoupled and can be extracted individually into any existing codebase."
    },
    {
      question: "How is code quality & security verified?",
      answer: "auraStack comes pre-configured with Pytest for backend logic and Playwright for real Chromium browser E2E user flow testing."
    }
  ];
});

const stackModules = computed(() => [
  {
    title: "Django 5 & Inertia 2",
    tag: "Core Backend",
    desc: locale.value === 'ar' ? 'ربط سلس بين Django و Vue 3 بدون التعقيدات الإضافية لـ REST API.' : 'Seamless Monolith-feel SPA with zero REST API serializer glue code.',
    icon: "🐍",
  },
  {
    title: "Multi-Tenant Teams",
    tag: "Workspaces",
    desc: locale.value === 'ar' ? 'عزل كلي للبيانات مع أمن الصلاحيات وتدفق دعوات الأعضاء بالبريد.' : 'Strict workspace boundary isolation with RBAC and invitation magic links.',
    icon: "🏢",
  },
  {
    title: "5 Payment Gateways",
    tag: "Billing",
    desc: locale.value === 'ar' ? 'دعم جاهز لـ Stripe و Paymob و PayPal و LemonSqueezy و Paddle.' : 'Pre-wired subscriptions & checkout webhooks for global & regional payments.',
    icon: "💳",
  },
  {
    title: "Playwright E2E Suite",
    tag: "Testing",
    desc: locale.value === 'ar' ? '70+ اختبار آلي للباك إند والمتصفح لضمان الاستقرار الكلي.' : 'End-to-end browser testing suite with instant regression feedback.',
    icon: "🧪",
  },
  {
    title: "MFA & Security",
    tag: "Allauth",
    desc: locale.value === 'ar' ? 'مصادقة ثنائية بـ TOTP وتقييد الطلبات وتأمين الجلسات.' : 'Google Authenticator TOTP 2FA, rate limiting, and CSRF protection.',
    icon: "🛡️",
  },
  {
    title: "RTL & Dual i18n",
    tag: "Localization",
    desc: locale.value === 'ar' ? 'دعم ثنائي الاتجاه باللغة العربية والإنجليزية من اليوم الأول.' : 'Bidirectional LTR/RTL support tailored for global and MENA audiences.',
    icon: "🌐",
  },
]);
</script>

<template>
  <AppHead 
    :title="locale === 'ar' ? 'أورا ستاك - محرك تطبيقات الـ SaaS المفتوح المصدر' : 'auraStack - Free & Open-Source B2B SaaS Engine'" 
    :description="locale === 'ar' ? 'ابدأ بناء منصتك السحابية في دقائق معدودة بـ Django و Inertia و Vue 3.' : 'Build production-ready B2B SaaS applications in days with Django, Inertia.js, and Vue 3.'" 
  />

  <div class="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-indigo-500 selection:text-white">
    <!-- Navbar -->
    <header class="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <span class="text-2xl font-extrabold bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent select-none tracking-tight">
            auraStack
          </span>
          <span class="bg-indigo-500/10 text-indigo-400 text-xs px-2.5 py-0.5 rounded-full font-semibold border border-indigo-500/20 select-none">
            Free Open Source
          </span>
        </div>
        
        <nav class="hidden md:flex items-center gap-8 text-sm font-medium text-slate-400">
          <a href="#features" class="hover:text-slate-100 transition-colors">{{ locale === 'ar' ? 'الميزات' : 'Features' }}</a>
          <a href="#architecture" class="hover:text-slate-100 transition-colors">{{ locale === 'ar' ? 'البنية التحتية' : 'Architecture' }}</a>
          <a href="#faq" class="hover:text-slate-100 transition-colors">{{ locale === 'ar' ? 'الأسئلة الشائعة' : 'FAQ' }}</a>
          <Link href="/blog/" class="hover:text-slate-100 transition-colors">{{ t('blog.title') }}</Link>
        </nav>

        <div class="flex items-center gap-4">
          <!-- Language Switcher -->
          <button
            @click="toggleLocale"
            class="inline-flex items-center justify-center px-3.5 py-1.5 rounded-xl border border-slate-800 bg-slate-900/60 text-slate-200 text-xs font-semibold hover:bg-slate-800 transition-colors cursor-pointer select-none"
          >
            🌐 {{ locale === 'ar' ? 'English' : 'العربية' }}
          </button>
          
          <Link href="/auth/login/" class="text-sm font-medium text-slate-300 hover:text-slate-100 transition-colors">
            {{ locale === 'ar' ? 'دخول' : 'Sign In' }}
          </Link>
          <Link href="/auth/register/" class="text-sm font-medium bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-xl shadow-lg shadow-indigo-600/20 transition-all">
            {{ locale === 'ar' ? 'ابدأ الآن' : 'Get Started' }}
          </Link>
        </div>
      </div>
    </header>

    <!-- Hero Section -->
    <section class="relative pt-24 pb-16 overflow-hidden">
      <div class="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-96 bg-gradient-to-b from-indigo-600/10 via-purple-600/5 to-transparent rounded-full blur-3xl -z-10 pointer-events-none"></div>

      <div class="max-w-5xl mx-auto px-6 text-center">
        <!-- Badge -->
        <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold mb-8">
          <span>⚡ {{ locale === 'ar' ? 'محرك تطبيقات SaaS مفتوح المصدر ومجاني 100%' : '100% Free & Open Source Production Boilerplate' }}</span>
        </div>

        <h1 class="text-4xl md:text-6xl font-extrabold tracking-tight leading-tight mb-8">
          {{ t('landing.title_prefix') }} <br class="hidden md:block"/>
          <span class="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            {{ t('landing.title_suffix') }}
          </span>
        </h1>
        
        <p class="text-base md:text-lg text-slate-400 max-w-3xl mx-auto mb-10 leading-relaxed">
          {{ t('landing.subtitle') }}
        </p>

        <div class="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
          <Link href="/auth/register/" class="w-full sm:w-auto text-center font-semibold bg-indigo-600 hover:bg-indigo-500 text-white px-8 py-4 rounded-xl shadow-xl shadow-indigo-600/20 transition-all text-base">
            {{ t('landing.cta_primary') }}
          </Link>
          <a href="#architecture" class="w-full sm:w-auto text-center font-semibold bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 px-8 py-4 rounded-xl transition-all text-base">
            {{ locale === 'ar' ? 'استكشف البنية التحتية' : 'Explore Architecture' }}
          </a>
        </div>

        <!-- Dashboard Product Preview Mockup -->
        <div class="relative max-w-5xl mx-auto rounded-2xl p-3 bg-gradient-to-b from-slate-800/60 to-slate-900/90 border border-slate-700/80 shadow-2xl backdrop-blur-2xl">
          <div class="flex items-center justify-between px-4 py-2 border-b border-slate-800 bg-slate-950/60 rounded-t-xl mb-3">
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded-full bg-rose-500/80"></div>
              <div class="w-3 h-3 rounded-full bg-amber-500/80"></div>
              <div class="w-3 h-3 rounded-full bg-emerald-500/80"></div>
            </div>
            <div class="text-xs text-slate-400 font-mono bg-slate-900 px-3 py-1 rounded-md border border-slate-800">
              https://app.aurastack.com/workspaces/tech-corp/dashboard
            </div>
            <div class="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              Live System
            </div>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 text-start">
            <div class="bg-slate-900/80 p-4 rounded-xl border border-slate-800">
              <p class="text-xs text-slate-400 mb-1">{{ locale === 'ar' ? 'مساحة العمل النشطة' : 'Active Workspace' }}</p>
              <p class="text-lg font-bold text-slate-100">TechCorp Team</p>
              <span class="text-xs text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20 mt-2 inline-block">Multi-Tenant</span>
            </div>

            <div class="bg-slate-900/80 p-4 rounded-xl border border-slate-800">
              <p class="text-xs text-slate-400 mb-1">{{ locale === 'ar' ? 'حالة التأمين والـ 2FA' : 'Security Status' }}</p>
              <p class="text-lg font-bold text-emerald-400">TOTP Active</p>
              <span class="text-xs text-slate-400 mt-2 block">Google Authenticator</span>
            </div>

            <div class="bg-slate-900/80 p-4 rounded-xl border border-slate-800">
              <p class="text-xs text-slate-400 mb-1">{{ locale === 'ar' ? 'بوابات الدفع الجاهزة' : 'Pre-wired Gateways' }}</p>
              <p class="text-lg font-bold text-purple-400">5 Providers</p>
              <span class="text-xs text-slate-400 mt-2 block">Stripe, Paymob, Paypal...</span>
            </div>

            <div class="bg-slate-900/80 p-4 rounded-xl border border-slate-800">
              <p class="text-xs text-slate-400 mb-1">{{ locale === 'ar' ? 'اختبارات E2E' : 'E2E Testing' }}</p>
              <p class="text-lg font-bold text-teal-400">Playwright 100%</p>
              <span class="text-xs text-slate-400 mt-2 block">Chromium Automated</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="py-20 border-t border-slate-900 bg-slate-950">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center max-w-3xl mx-auto mb-16">
          <h2 class="text-3xl md:text-4xl font-bold mb-4">{{ t('landing.features_title') }}</h2>
          <p class="text-slate-400 leading-relaxed">{{ t('landing.features_subtitle') }}</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div class="bg-slate-900/50 border border-slate-800/80 p-8 rounded-2xl hover:border-slate-700/80 transition-all group">
            <div class="w-12 h-12 bg-indigo-500/10 rounded-xl flex items-center justify-center text-indigo-400 mb-6 group-hover:scale-110 transition-transform">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                <path stroke-linecap="round" stroke-linejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.97 5.97 0 00-.75-2.906M12 21a11.97 11.97 0 01-8.118-3.276m0 0a5.002 5.002 0 019.223-2.19M3.52 18.521l-.001.03a11.94 11.94 0 01-.037-.666 11.944 11.944 0 011.584-5.963C5.105 10.74 6.786 8.5 9 8.5h6c2.214 0 3.895 2.24 4.536 3.428A11.94 11.94 0 0121.5 18c0 .225-.012.447-.037.666M15 7.5a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold mb-3">{{ t('landing.feature_tenancy_title') }}</h3>
            <p class="text-slate-400 text-sm leading-relaxed">{{ t('landing.feature_tenancy_desc') }}</p>
          </div>

          <div class="bg-slate-900/50 border border-slate-800/80 p-8 rounded-2xl hover:border-slate-700/80 transition-all group">
            <div class="w-12 h-12 bg-purple-500/10 rounded-xl flex items-center justify-center text-purple-400 mb-6 group-hover:scale-110 transition-transform">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 8.25h19.5M2.25 9h19.5m-16.5 5.25h6m-6 2.25h3m-3.75 3h15a2.25 2.25 0 002.25-2.25V6.75A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25v10.5A2.25 2.25 0 004.5 19.5z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold mb-3">{{ t('landing.feature_billing_title') }}</h3>
            <p class="text-slate-400 text-sm leading-relaxed">{{ t('landing.feature_billing_desc') }}</p>
          </div>

          <div class="bg-slate-900/50 border border-slate-800/80 p-8 rounded-2xl hover:border-slate-700/80 transition-all group">
            <div class="w-12 h-12 bg-pink-500/10 rounded-xl flex items-center justify-center text-pink-400 mb-6 group-hover:scale-110 transition-transform">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 21l5.25-11.25L21 21m-9-3h7.5M3 5.621a48.474 48.474 0 016-.371m0 0c1.12 0 2.233.038 3.334.114M9 5.25V3m3.334 2.364C11.176 10.658 7.69 15.08 3 17.502m9.334-12.138A27.515 27.515 0 0010.5 13.5M9 13.5a15.42 15.42 0 01-3.343-6.425" />
              </svg>
            </div>
            <h3 class="text-xl font-bold mb-3">{{ t('landing.feature_rtl_title') }}</h3>
            <p class="text-slate-400 text-sm leading-relaxed">{{ t('landing.feature_rtl_desc') }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Architecture Section (Replacing Pricing Section) -->
    <section id="architecture" class="py-24 border-t border-slate-900 bg-slate-950/80 relative overflow-hidden">
      <!-- Glow effect -->
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-600/10 rounded-full blur-[140px] pointer-events-none"></div>

      <div class="max-w-7xl mx-auto px-6 relative z-10">
        <div class="text-center max-w-3xl mx-auto mb-16">
          <div class="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-bold uppercase tracking-wider mb-4">
            ✨ {{ t('landing.badge_open_source') }}
          </div>
          <h2 class="text-3xl md:text-5xl font-extrabold mb-4 tracking-tight">
            {{ t('landing.architecture_title') }}
          </h2>
          <p class="text-slate-400 leading-relaxed text-base">
            {{ t('landing.architecture_subtitle') }}
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto items-stretch">
          <div 
            v-for="(module, index) in stackModules" 
            :key="index"
            class="bg-slate-900/60 border border-slate-800 hover:border-indigo-500/40 p-6 rounded-2xl transition-all flex flex-col justify-between group hover:shadow-xl hover:shadow-indigo-500/5"
          >
            <div>
              <div class="flex items-center justify-between mb-4">
                <span class="text-3xl">{{ module.icon }}</span>
                <span class="text-[10px] font-bold tracking-wider uppercase px-2.5 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  {{ module.tag }}
                </span>
              </div>
              <h3 class="text-xl font-bold mb-2 group-hover:text-indigo-300 transition-colors">{{ module.title }}</h3>
              <p class="text-slate-400 text-sm leading-relaxed">{{ module.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- FAQ Section -->
    <section id="faq" class="py-24 border-t border-slate-900 bg-slate-950/40">
      <div class="max-w-7xl mx-auto px-6">
        <div class="text-center max-w-3xl mx-auto mb-16">
          <h2 class="text-3xl md:text-4xl font-extrabold mb-4">
            {{ t('landing.faq_title') }}
          </h2>
          <p class="text-slate-400 leading-relaxed">
            {{ t('landing.faq_subtitle') }}
          </p>
        </div>

        <FaqAccordion :items="faqItems" />
      </div>
    </section>

    <!-- Footer -->
    <footer class="border-t border-slate-900 py-12 bg-slate-950">
      <div class="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-6 text-sm text-slate-500">
        <p>&copy; 2026 auraStack. {{ t('landing.footer_text') }}</p>
        <div class="flex space-x-6">
          <Link href="/auth/login/" class="hover:text-slate-300">{{ locale === 'ar' ? 'دخول' : 'Sign In' }}</Link>
          <Link href="/auth/register/" class="hover:text-slate-300">{{ locale === 'ar' ? 'إنشاء حساب' : 'Register' }}</Link>
          <Link href="/blog/" class="hover:text-slate-300">{{ t('blog.title') }}</Link>
        </div>
      </div>
    </footer>
  </div>
</template>
