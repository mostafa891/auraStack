<script setup lang="ts">
import { computed, ref, watchEffect } from "vue";
import { usePage, Link } from "@inertiajs/vue3";
import type { SharedProps } from "@/types/inertia";
import { useI18n } from "@/composables/useI18n";
import { useToast } from "@/composables/useToast";

interface Props {
  stripe_publishable_key: string;
  prices: {
    pro_monthly: string;
  };
}

defineProps<Props>();

const page = usePage<SharedProps>();
const activeWorkspace = computed(() => page.props.auth?.active_workspace);
const { locale, toggleLocale } = useI18n();
const { toast } = useToast();

const isRedirecting = ref(false);
const selectedGateway = ref("stripe");

// Dynamic dir updating
watchEffect(() => {
  document.documentElement.dir = locale.value === "ar" ? "rtl" : "ltr";
  document.documentElement.lang = locale.value;
});

const handleSubscribe = async (planId: string) => {
  if (!activeWorkspace.value) return;

  isRedirecting.value = true;
  try {
    const response = await fetch("/api/v1/private/billing/checkout", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        // Django-ninja uses standard cookie-based CSRF protection, we need to pass CSRF token
        "X-CSRFToken": getCookie("XSRF-TOKEN") || "",
      },
      body: JSON.stringify({
        workspace_id: activeWorkspace.value.id,
        plan_id: planId,
        gateway: selectedGateway.value,
      }),
    });

    if (!response.ok) {
      throw new Error(locale.value === "ar" ? "فشل إنشاء جلسة الدفع." : "Failed to initiate payment.");
    }

    const data = await response.json();
    if (data.checkout_url) {
      window.location.href = data.checkout_url;
    }
  } catch (error: any) {
    toast.error(error.message);
    isRedirecting.value = false;
  }
};

const getCookie = (name: string) => {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
};
</script>

<template>
  <div class="min-h-screen bg-[var(--color-surface-muted)] py-16 px-4 sm:px-6 lg:px-8 transition-colors duration-300 relative overflow-hidden">
    <!-- Glow backgrounds -->
    <div class="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-[var(--color-primary)]/10 blur-[120px] pointer-events-none"></div>
    <div class="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-[var(--color-primary)]/10 blur-[120px] pointer-events-none"></div>

    <div class="max-w-5xl mx-auto relative z-10 space-y-12">
      <!-- Navbar / Header -->
      <div class="flex items-center justify-between bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl p-6 shadow-sm">
        <div class="flex items-center space-x-4">
          <Link href="/profile" class="w-10 h-10 rounded-xl bg-[var(--color-primary)] flex items-center justify-center text-white font-bold text-lg shadow-md cursor-pointer select-none">
            ←
          </Link>
          <div>
            <h1 class="text-lg font-bold text-[var(--color-text)]">{{ locale === 'ar' ? 'الرجوع للإعدادات' : 'Back to Settings' }}</h1>
            <p class="text-xs text-[var(--color-text-muted)]">{{ activeWorkspace ? activeWorkspace.name : '' }}</p>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <button
            @click="toggleLocale"
            class="inline-flex items-center justify-center px-4 py-2 rounded-xl text-sm font-medium border border-[var(--color-border)] text-[var(--color-text)] bg-[var(--color-surface-muted)] hover:bg-[var(--color-border)] transition-colors cursor-pointer select-none"
          >
            🌐 {{ locale === 'ar' ? 'English' : 'العربية' }}
          </button>
        </div>
      </div>

      <!-- Pricing Title -->
      <div class="text-center space-y-4">
        <h2 class="text-4xl font-extrabold text-[var(--color-text)] tracking-tight">
          {{ locale === 'ar' ? 'خطط أسعار بسيطة، بدون تعقيد' : 'Simple, transparent pricing' }}
        </h2>
        <p class="text-sm text-[var(--color-text-muted)] max-w-md mx-auto leading-relaxed">
          {{ locale === 'ar' ? 'اختر الخطة المناسبة لفريقك وابدأ رحلتك التوسعية اليوم مع AuraFlow.' : 'Choose the best plan for your team and unlock advanced capabilities today.' }}
        </p>
      </div>

      <!-- Plans Cards Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
        <!-- Free Plan -->
        <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-3xl p-8 flex flex-col justify-between shadow-sm relative group hover:border-[var(--color-border-hover)] transition-all">
          <div class="space-y-6">
            <div>
              <h3 class="text-lg font-bold text-[var(--color-text)]">{{ locale === 'ar' ? 'الخطة المجانية' : 'Free Plan' }}</h3>
              <p class="text-xs text-[var(--color-text-muted)] mt-1">{{ locale === 'ar' ? 'لتجربة أساسية للفرق الصغيرة' : 'For small teams getting started' }}</p>
            </div>

            <div class="flex items-baseline">
              <span class="text-4xl font-extrabold text-[var(--color-text)]">$0</span>
              <span class="text-sm text-[var(--color-text-muted)] ms-2">/ {{ locale === 'ar' ? 'شريحة العمر' : 'forever' }}</span>
            </div>

            <div class="border-t border-[var(--color-border)] pt-6 space-y-4">
              <div class="flex items-center gap-3">
                <span class="text-emerald-500 text-lg">✔</span>
                <span class="text-sm text-[var(--color-text)]">{{ locale === 'ar' ? 'حد أقصى 3 أعضاء' : 'Up to 3 workspace members' }}</span>
              </div>
              <div class="flex items-center gap-3">
                <span class="text-emerald-500 text-lg">✔</span>
                <span class="text-sm text-[var(--color-text)]">{{ locale === 'ar' ? 'أدوات إدارة أساسية' : 'Basic management tools' }}</span>
              </div>
              <div class="flex items-center gap-3">
                <span class="text-emerald-500 text-lg">✔</span>
                <span class="text-sm text-[var(--color-text)]">1,000 AI Tokens</span>
              </div>
            </div>
          </div>

          <div class="pt-8">
            <button
              disabled
              class="w-full py-3 px-4 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-muted)] text-[var(--color-text-muted)] text-sm font-semibold text-center cursor-not-allowed"
            >
              {{ locale === 'ar' ? 'الخطة الافتراضية النشطة' : 'Active Default Plan' }}
            </button>
          </div>
        </div>

        <!-- Pro Plan -->
        <div class="bg-[var(--color-surface)] border-2 border-[var(--color-primary)] rounded-3xl p-8 flex flex-col justify-between shadow-md relative group transition-all">
          <!-- Popular Badge -->
          <div class="absolute top-0 right-8 -translate-y-1/2 bg-[var(--color-primary)] text-white text-[10px] uppercase font-bold tracking-wider py-1 px-3 rounded-full">
            {{ locale === 'ar' ? 'الأكثر طلباً' : 'Most Popular' }}
          </div>

          <div class="space-y-6">
            <div>
              <h3 class="text-lg font-bold text-[var(--color-text)]">{{ locale === 'ar' ? 'خطة المحترفين' : 'Pro Plan' }}</h3>
              <p class="text-xs text-[var(--color-text-muted)] mt-1">{{ locale === 'ar' ? 'للاستفادة القصوى من ميزات الذكاء الاصطناعي والتعاون الكامل' : 'Unlock full power of AI and collaboration' }}</p>
            </div>

            <div class="flex items-baseline">
              <span class="text-4xl font-extrabold text-[var(--color-text)]">$19</span>
              <span class="text-sm text-[var(--color-text-muted)] ms-2">/ {{ locale === 'ar' ? 'شهرياً' : 'monthly' }}</span>
            </div>

            <!-- Gateway Selector -->
            <div class="space-y-2">
              <label class="block text-xs font-bold text-[var(--color-text-muted)] uppercase tracking-wider">
                {{ locale === 'ar' ? 'اختر بوابة الدفع المفضلة' : 'Select Payment Gateway' }}
              </label>
              <div class="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  @click="selectedGateway = 'stripe'"
                  :class="selectedGateway === 'stripe' ? 'border-[var(--color-primary)] bg-[var(--color-primary)]/5 text-[var(--color-primary)] shadow-sm' : 'border-[var(--color-border)] bg-[var(--color-surface-muted)] text-[var(--color-text-muted)] hover:border-[var(--color-border-hover)]'"
                  class="py-2.5 px-3 rounded-xl border text-xs font-bold transition-all text-center cursor-pointer flex items-center justify-center gap-1.5"
                >
                  💳 Stripe
                </button>
                <button
                  type="button"
                  @click="selectedGateway = 'paymob'"
                  :class="selectedGateway === 'paymob' ? 'border-[var(--color-primary)] bg-[var(--color-primary)]/5 text-[var(--color-primary)] shadow-sm' : 'border-[var(--color-border)] bg-[var(--color-surface-muted)] text-[var(--color-text-muted)] hover:border-[var(--color-border-hover)]'"
                  class="py-2.5 px-3 rounded-xl border text-xs font-bold transition-all text-center cursor-pointer flex items-center justify-center gap-1.5"
                >
                  📱 Paymob
                </button>
                <button
                  type="button"
                  @click="selectedGateway = 'paypal'"
                  :class="selectedGateway === 'paypal' ? 'border-[var(--color-primary)] bg-[var(--color-primary)]/5 text-[var(--color-primary)] shadow-sm' : 'border-[var(--color-border)] bg-[var(--color-surface-muted)] text-[var(--color-text-muted)] hover:border-[var(--color-border-hover)]'"
                  class="py-2.5 px-3 rounded-xl border text-xs font-bold transition-all text-center cursor-pointer flex items-center justify-center gap-1.5"
                >
                  🅿 PayPal
                </button>
                <button
                  type="button"
                  @click="selectedGateway = 'paddle'"
                  :class="selectedGateway === 'paddle' ? 'border-[var(--color-primary)] bg-[var(--color-primary)]/5 text-[var(--color-primary)] shadow-sm' : 'border-[var(--color-border)] bg-[var(--color-surface-muted)] text-[var(--color-text-muted)] hover:border-[var(--color-border-hover)]'"
                  class="py-2.5 px-3 rounded-xl border text-xs font-bold transition-all text-center cursor-pointer flex items-center justify-center gap-1.5"
                >
                  🏓 Paddle
                </button>
                <button
                  type="button"
                  @click="selectedGateway = 'lemonsqueezy'"
                  :class="selectedGateway === 'lemonsqueezy' ? 'border-[var(--color-primary)] bg-[var(--color-primary)]/5 text-[var(--color-primary)] shadow-sm' : 'border-[var(--color-border)] bg-[var(--color-surface-muted)] text-[var(--color-text-muted)] hover:border-[var(--color-border-hover)]'"
                  class="col-span-2 py-2.5 px-3 rounded-xl border text-xs font-bold transition-all text-center cursor-pointer flex items-center justify-center gap-1.5"
                >
                  🍋 LemonSqueezy
                </button>
              </div>
            </div>

            <div class="border-t border-[var(--color-border)] pt-6 space-y-4">
              <div class="flex items-center gap-3">
                <span class="text-emerald-500 text-lg">✔</span>
                <span class="text-sm text-[var(--color-text)]">{{ locale === 'ar' ? 'حد أقصى 20 عضو' : 'Up to 20 workspace members' }}</span>
              </div>
              <div class="flex items-center gap-3">
                <span class="text-emerald-500 text-lg">✔</span>
                <span class="text-sm text-[var(--color-text)]">{{ locale === 'ar' ? 'تحليلات متقدمة وميزات الذكاء الاصطناعي' : 'Advanced analytics & AI features' }}</span>
              </div>
              <div class="flex items-center gap-3">
                <span class="text-emerald-500 text-lg">✔</span>
                <span class="text-sm text-[var(--color-text)]">100,000 AI Tokens</span>
              </div>
              <div class="flex items-center gap-3">
                <span class="text-emerald-500 text-lg">✔</span>
                <span class="text-sm text-[var(--color-text)]">{{ locale === 'ar' ? 'دعم فني ذو أولوية' : 'Priority support' }}</span>
              </div>
            </div>
          </div>

          <div class="pt-8">
            <button
              @click="handleSubscribe(prices.pro_monthly)"
              :disabled="isRedirecting || !activeWorkspace"
              class="w-full py-3 px-4 rounded-xl bg-[var(--color-primary)] text-white text-sm font-bold hover:bg-[var(--color-primary-hover)] transition-all shadow-md shadow-indigo-500/10 cursor-pointer disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <span v-if="isRedirecting" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
              <span>{{ locale === 'ar' ? 'اشترك الآن' : 'Subscribe Now' }}</span>
            </button>
            <p v-if="!activeWorkspace" class="text-[10px] text-[var(--color-danger)] text-center mt-2">
              {{ locale === 'ar' ? 'يرجى تسجيل الدخول أو اختيار مساحة عمل أولاً.' : 'Please select or create a workspace first.' }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
