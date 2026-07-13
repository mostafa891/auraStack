<script setup lang="ts">
import { computed, ref, watchEffect } from "vue";
import { usePage, Link } from "@inertiajs/vue3";
import type { SharedProps } from "@/types/inertia";
import { useI18n } from "@/composables/useI18n";
import { useToast } from "@/composables/useToast";

const page = usePage<SharedProps>();
const activeWorkspace = computed(() => page.props.auth?.active_workspace);
const subscription = computed(() => activeWorkspace.value?.subscription);
const { locale, toggleLocale } = useI18n();
const { toast } = useToast();

const isRedirecting = ref(false);

watchEffect(() => {
  document.documentElement.dir = locale.value === "ar" ? "rtl" : "ltr";
  document.documentElement.lang = locale.value;
});

const handleManageBilling = async () => {
  if (!activeWorkspace.value) return;

  isRedirecting.value = true;
  try {
    const response = await fetch(`/api/v1/private/billing/portal/${activeWorkspace.value.id}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(locale.value === "ar" ? "فشل فتح بوابة الإدارة المالية." : "Failed to open billing portal.");
    }

    const data = await response.json();
    if (data.portal_url) {
      window.location.href = data.portal_url;
    }
  } catch (error: any) {
    toast.error(error.message);
    isRedirecting.value = false;
  }
};

const formatDate = (isoString?: string | null) => {
  if (!isoString) return "";
  const date = new Date(isoString);
  return date.toLocaleDateString(locale.value === "ar" ? "ar-EG" : "en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
};
</script>

<template>
  <div class="min-h-screen bg-[var(--color-surface-muted)] py-16 px-4 sm:px-6 lg:px-8 transition-colors duration-300 relative overflow-hidden">
    <!-- Glow effects -->
    <div class="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-[var(--color-primary)]/10 blur-[120px] pointer-events-none"></div>
    <div class="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-[var(--color-primary)]/10 blur-[120px] pointer-events-none"></div>

    <div class="max-w-3xl mx-auto relative z-10 space-y-8">
      <!-- Navbar / Header -->
      <div class="flex items-center justify-between bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl p-6 shadow-sm">
        <div class="flex items-center space-x-4">
          <Link href="/profile" class="w-10 h-10 rounded-xl bg-[var(--color-primary)] flex items-center justify-center text-white font-bold text-lg shadow-md cursor-pointer select-none">
            ←
          </Link>
          <div>
            <h1 class="text-lg font-bold text-[var(--color-text)]">{{ locale === 'ar' ? 'إدارة الاشتراك والفوترة' : 'Billing & Subscription Settings' }}</h1>
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

      <!-- Graceful Downgrade / Limit Warning Alert -->
      <div
        v-if="subscription?.is_locked"
        class="bg-amber-500/10 border-2 border-amber-500/30 rounded-2xl p-6 flex gap-4 items-start"
      >
        <span class="text-2xl text-amber-500">⚠</span>
        <div class="space-y-2">
          <h4 class="text-sm font-bold text-[var(--color-text)]">
            {{ locale === 'ar' ? 'مساحة العمل مقيدة مؤقتاً' : 'Workspace Restricted' }}
          </h4>
          <p class="text-xs text-[var(--color-text-muted)] leading-relaxed">
            <span v-if="subscription.member_count > subscription.max_members">
              {{ locale === 'ar' 
                ? `لقد تجاوزت الحد الأقصى للأعضاء المسموح به لخطة ${subscription.plan_id.toUpperCase()} (${subscription.max_members} أعضاء). مساحة عملك حالياً بها ${subscription.member_count} أعضاء.` 
                : `You have exceeded the maximum members allowed for the ${subscription.plan_id.toUpperCase()} plan (${subscription.max_members} members). Your workspace currently has ${subscription.member_count} members.` 
              }}
              {{ locale === 'ar' 
                ? 'يرجى إزالة الأعضاء الإضافيين من إعدادات الفريق أو ترقية اشتراكك لإعادة فتح مساحة العمل.' 
                : 'Please remove additional members from Team settings or upgrade your plan to unlock the workspace.' 
              }}
            </span>
            <span v-else>
              {{ locale === 'ar'
                ? 'اشتراكك منتهي الصلاحية أو هناك مشكلة في تجديد عملية الدفع الأخيرة.'
                : 'Your subscription has expired or there was an issue processing your latest payment.'
              }}
              {{ locale === 'ar'
                ? 'يرجى تحديث بطاقة الدفع الخاصة بك لإعادة تنشيط الميزات.'
                : 'Please update your payment method to reactivate full features.'
              }}
            </span>
          </p>
          <div class="pt-2 flex gap-3">
            <Link href="/billing/pricing" class="inline-flex px-3 py-1.5 rounded-lg bg-[var(--color-primary)] text-white text-xs font-semibold hover:bg-[var(--color-primary-hover)] transition-colors">
              {{ locale === 'ar' ? 'ترقية الخطة' : 'Upgrade Plan' }}
            </Link>
            <Link href="/workspaces" class="inline-flex px-3 py-1.5 rounded-lg bg-[var(--color-surface-muted)] border border-[var(--color-border)] text-[var(--color-text)] text-xs font-semibold hover:bg-[var(--color-border)] transition-colors">
              {{ locale === 'ar' ? 'إدارة الفريق' : 'Manage Team' }}
            </Link>
          </div>
        </div>
      </div>

      <!-- Subscription Details Card -->
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-3xl p-8 shadow-sm space-y-8">
        <div class="flex justify-between items-start">
          <div class="space-y-1">
            <h3 class="text-sm font-bold text-[var(--color-text-muted)] uppercase tracking-wider">
              {{ locale === 'ar' ? 'الخطة النشطة الحالية' : 'Current Active Plan' }}
            </h3>
            <h2 class="text-3xl font-extrabold text-[var(--color-text)]">
              {{ subscription?.plan_id ? subscription.plan_id.toUpperCase() : 'FREE' }}
            </h2>
          </div>
          <span
            :class="subscription?.status === 'active' ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20' : 'bg-amber-500/10 text-amber-500 border border-amber-500/20'"
            class="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide"
          >
            {{ subscription?.status ? subscription.status : 'active' }}
          </span>
        </div>

        <div class="border-t border-[var(--color-border)] pt-6 grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
          <div class="flex justify-between py-2 border-b border-[var(--color-border)]/50">
            <span class="text-[var(--color-text-muted)]">{{ locale === 'ar' ? 'تاريخ التجديد/الانتهاء' : 'Renewal / Expiry Date' }}</span>
            <span class="font-bold text-[var(--color-text)]">
              {{ subscription?.current_period_end ? formatDate(subscription.current_period_end) : (locale === 'ar' ? 'غير محدود' : 'Never') }}
            </span>
          </div>

          <div class="flex justify-between py-2 border-b border-[var(--color-border)]/50">
            <span class="text-[var(--color-text-muted)]">{{ locale === 'ar' ? 'الأعضاء المتاحون' : 'Workspace Members' }}</span>
            <span class="font-bold text-[var(--color-text)]">
              {{ subscription?.member_count }} / {{ subscription?.max_members }}
            </span>
          </div>
        </div>

        <!-- Stripe Portal Action -->
        <div class="pt-6 flex justify-end gap-3">
          <Link
            v-if="subscription?.plan_id === 'free'"
            href="/billing/pricing"
            class="px-6 py-2.5 rounded-xl bg-[var(--color-primary)] text-white text-sm font-bold hover:bg-[var(--color-primary-hover)] transition-colors shadow-md shadow-indigo-500/10 cursor-pointer"
          >
            {{ locale === 'ar' ? 'الترقية لباقة مدفوعة' : 'Upgrade Workspace' }}
          </Link>
          <button
            v-else
            @click="handleManageBilling"
            :disabled="isRedirecting"
            class="px-6 py-2.5 rounded-xl bg-[var(--color-primary)] text-white text-sm font-bold hover:bg-[var(--color-primary-hover)] transition-colors shadow-md shadow-indigo-500/10 cursor-pointer flex items-center gap-2"
          >
            <span v-if="isRedirecting" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            <span>{{ locale === 'ar' ? 'إدارة الاشتراك المالي الفعلي' : 'Manage Subscription & Invoices' }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
