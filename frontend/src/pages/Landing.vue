<script setup lang="ts">
import { watchEffect } from "vue";
import { Link } from '@inertiajs/vue3';
import AppHead from '../components/AppHead.vue';
import { useI18n } from '@/composables/useI18n';

const { t, locale, toggleLocale } = useI18n();

// Dynamic update of HTML attributes for RTL/LTR and language code
watchEffect(() => {
  document.documentElement.dir = locale.value === "ar" ? "rtl" : "ltr";
  document.documentElement.lang = locale.value;
});
</script>

<template>
  <AppHead 
    :title="locale === 'ar' ? 'أورافلو - محرك تطبيقات الـ SaaS الأقوى' : 'AuraFlow - The Ultimate B2B SaaS Engine'" 
    :description="locale === 'ar' ? 'ابدأ بناء منصتك السحابية في دقائق معدودة بـ Django و Inertia و Vue 3.' : 'Build production-ready B2B SaaS applications in days with Django, Inertia.js, and Vue 3.'" 
  />

  <div class="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-indigo-500 selection:text-white">
    <!-- Navbar -->
    <header class="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <span class="text-2xl font-bold bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent select-none">
            AuraFlow
          </span>
          <span class="bg-indigo-500/10 text-indigo-400 text-xs px-2.5 py-0.5 rounded-full font-medium border border-indigo-500/20 select-none">
            v1.0
          </span>
        </div>
        
        <nav class="hidden md:flex items-center gap-8 text-sm font-medium text-slate-400">
          <a href="#features" class="hover:text-slate-100 transition-colors">{{ locale === 'ar' ? 'الميزات' : 'Features' }}</a>
          <Link href="/blog/" class="hover:text-slate-100 transition-colors">{{ t('blog.title') }}</Link>
        </nav>

        <div class="flex items-center gap-4">
          <!-- Language Switcher -->
          <button
            @click="toggleLocale"
            class="inline-flex items-center justify-center px-3 py-1.5 rounded-xl border border-slate-850 bg-slate-900/60 text-slate-200 text-xs font-semibold hover:bg-slate-800 transition-colors cursor-pointer select-none"
          >
            🌐 {{ locale === 'ar' ? 'English' : 'العربية' }}
          </button>
          
          <Link href="/auth/login/" class="text-sm font-medium text-slate-300 hover:text-slate-100 transition-colors">
            {{ locale === 'ar' ? 'دخول' : 'Sign In' }}
          </Link>
          <Link href="/auth/register/" class="text-sm font-medium bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg shadow-lg shadow-indigo-600/20 transition-all">
            {{ locale === 'ar' ? 'ابدأ الآن' : 'Get Started' }}
          </Link>
        </div>
      </div>
    </header>

    <!-- Hero Section -->
    <section class="relative pt-24 pb-20 overflow-hidden">
      <!-- Background Gradients -->
      <div class="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-96 bg-gradient-to-b from-indigo-600/10 via-purple-600/5 to-transparent rounded-full blur-3xl -z-10 pointer-events-none"></div>

      <div class="max-w-5xl mx-auto px-6 text-center">
        <h1 class="text-4xl md:text-6xl font-extrabold tracking-tight leading-tight mb-8">
          {{ t('landing.title_prefix') }} <br class="hidden md:block"/>
          <span class="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            {{ t('landing.title_suffix') }}
          </span>
        </h1>
        
        <p class="text-base md:text-lg text-slate-400 max-w-3xl mx-auto mb-10 leading-relaxed">
          {{ t('landing.subtitle') }}
        </p>

        <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link href="/auth/register/" class="w-full sm:w-auto text-center font-semibold bg-indigo-600 hover:bg-indigo-500 text-white px-8 py-4 rounded-xl shadow-xl shadow-indigo-600/20 transition-all text-base">
            {{ t('landing.cta_primary') }}
          </Link>
          <a href="#features" class="w-full sm:w-auto text-center font-semibold bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 px-8 py-4 rounded-xl transition-all text-base">
            {{ t('landing.cta_secondary') }}
          </a>
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
          <!-- Feature 1: Multi-Tenancy -->
          <div class="bg-slate-900/50 border border-slate-800/80 p-8 rounded-2xl hover:border-slate-700/80 transition-all group">
            <div class="w-12 h-12 bg-indigo-500/10 rounded-xl flex items-center justify-center text-indigo-400 mb-6 group-hover:scale-110 transition-transform">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                <path stroke-linecap="round" stroke-linejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.97 5.97 0 00-.75-2.906M12 21a11.97 11.97 0 01-8.118-3.276m0 0a5.002 5.002 0 019.223-2.19M3.52 18.521l-.001.03a11.94 11.94 0 01-.037-.666 11.944 11.944 0 011.584-5.963C5.105 10.74 6.786 8.5 9 8.5h6c2.214 0 3.895 2.24 4.536 3.428A11.94 11.94 0 0121.5 18c0 .225-.012.447-.037.666M15 7.5a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold mb-3">{{ t('landing.feature_tenancy_title') }}</h3>
            <p class="text-slate-400 text-sm leading-relaxed">
              {{ t('landing.feature_tenancy_desc') }}
            </p>
          </div>

          <!-- Feature 2: Multiple Gateways -->
          <div class="bg-slate-900/50 border border-slate-800/80 p-8 rounded-2xl hover:border-slate-700/80 transition-all group">
            <div class="w-12 h-12 bg-purple-500/10 rounded-xl flex items-center justify-center text-purple-400 mb-6 group-hover:scale-110 transition-transform">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 8.25h19.5M2.25 9h19.5m-16.5 5.25h6m-6 2.25h3m-3.75 3h15a2.25 2.25 0 002.25-2.25V6.75A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25v10.5A2.25 2.25 0 004.5 19.5z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold mb-3">{{ t('landing.feature_billing_title') }}</h3>
            <p class="text-slate-400 text-sm leading-relaxed">
              {{ t('landing.feature_billing_desc') }}
            </p>
          </div>

          <!-- Feature 3: RTL & Arabic Support -->
          <div class="bg-slate-900/50 border border-slate-800/80 p-8 rounded-2xl hover:border-slate-700/80 transition-all group">
            <div class="w-12 h-12 bg-pink-500/10 rounded-xl flex items-center justify-center text-pink-400 mb-6 group-hover:scale-110 transition-transform">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 21l5.25-11.25L21 21m-9-3h7.5M3 5.621a48.474 48.474 0 016-.371m0 0c1.12 0 2.233.038 3.334.114M9 5.25V3m3.334 2.364C11.176 10.658 7.69 15.08 3 17.502m9.334-12.138A27.515 27.515 0 0010.5 13.5M9 13.5a15.42 15.42 0 01-3.343-6.425" />
              </svg>
            </div>
            <h3 class="text-xl font-bold mb-3">{{ t('landing.feature_rtl_title') }}</h3>
            <p class="text-slate-400 text-sm leading-relaxed">
              {{ t('landing.feature_rtl_desc') }}
            </p>
          </div>

          <!-- Feature 4: Hybrid Queue -->
          <div class="bg-slate-900/50 border border-slate-800/80 p-8 rounded-2xl hover:border-slate-700/80 transition-all group">
            <div class="w-12 h-12 bg-teal-500/10 rounded-xl flex items-center justify-center text-teal-400 mb-6 group-hover:scale-110 transition-transform">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 8.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 20.25v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25A2.25 2.25 0 0113.5 8.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold mb-3">{{ t('landing.feature_queue_title') }}</h3>
            <p class="text-slate-400 text-sm leading-relaxed">
              {{ t('landing.feature_queue_desc') }}
            </p>
          </div>

          <!-- Feature 5: Security & MFA -->
          <div class="bg-slate-900/50 border border-slate-800/80 p-8 rounded-2xl hover:border-slate-700/80 transition-all group">
            <div class="w-12 h-12 bg-amber-500/10 rounded-xl flex items-center justify-center text-amber-400 mb-6 group-hover:scale-110 transition-transform">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.57-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold mb-3">{{ t('landing.feature_security_title') }}</h3>
            <p class="text-slate-400 text-sm leading-relaxed">
              {{ t('landing.feature_security_desc') }}
            </p>
          </div>

          <!-- Feature 6: Playwright E2E Tests -->
          <div class="bg-slate-900/50 border border-slate-800/80 p-8 rounded-2xl hover:border-slate-700/80 transition-all group">
            <div class="w-12 h-12 bg-emerald-500/10 rounded-xl flex items-center justify-center text-emerald-400 mb-6 group-hover:scale-110 transition-transform">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold mb-3">{{ t('landing.feature_testing_title') }}</h3>
            <p class="text-slate-400 text-sm leading-relaxed">
              {{ t('landing.feature_testing_desc') }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="border-t border-slate-900 py-12 bg-slate-950/40">
      <div class="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-6 text-sm text-slate-500">
        <p>&copy; 2026 AuraFlow. {{ t('landing.footer_text') }}</p>
        <div class="flex space-x-6">
          <Link href="/auth/login/" class="hover:text-slate-300">{{ locale === 'ar' ? 'دخول' : 'Sign In' }}</Link>
          <Link href="/auth/register/" class="hover:text-slate-300">{{ locale === 'ar' ? 'إنشاء حساب' : 'Register' }}</Link>
        </div>
      </div>
    </footer>
  </div>
</template>
