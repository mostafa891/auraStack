<script setup lang="ts">
import { computed, watch, onMounted } from "vue";
import { usePage, useForm, Link } from "@inertiajs/vue3";

// استخراج البيانات المشتركة من الباك إند
const page = usePage();
const user = computed(() => (page.props.auth as any)?.user);

// فورم تحديث التفضيلات الشخصية
const form = useForm({
  language: user.value?.language || "en",
  theme: user.value?.theme || "SYSTEM",
  timezone: user.value?.timezone || "UTC",
});

// قائمة اللغات المعتمدة
const languages = [
  { value: "en", label: "English" },
  { value: "ar", label: "العربية" },
];

// قائمة السمات
const themes = [
  { value: "LIGHT", label: "Light Mode / مضيء" },
  { value: "DARK", label: "Dark Mode / مظلم" },
  { value: "SYSTEM", label: "System Default / تلقائي" },
];

// بعض المناطق الزمنية الشائعة للتسهيل
const commonTimezones = [
  "UTC",
  "Africa/Cairo",
  "Asia/Riyadh",
  "Europe/London",
  "America/New_York",
  "Asia/Tokyo",
  "Asia/Dubai",
];

// دالة لتطبيق المظهر بصرياً في المتصفح فوراً
const applyTheme = (themeName: string) => {
  const root = document.documentElement;
  if (themeName === "DARK") {
    root.classList.add("dark");
    root.style.setProperty("--color-surface", "#0f172a");
    root.style.setProperty("--color-surface-muted", "#020617");
    root.style.setProperty("--color-border", "#1e293b");
    root.style.setProperty("--color-text", "#f8fafc");
    root.style.setProperty("--color-text-muted", "#94a3b8");
  } else if (themeName === "LIGHT") {
    root.classList.remove("dark");
    root.style.setProperty("--color-surface", "#ffffff");
    root.style.setProperty("--color-surface-muted", "#f8fafc");
    root.style.setProperty("--color-border", "#e2e8f0");
    root.style.setProperty("--color-text", "#0f172a");
    root.style.setProperty("--color-text-muted", "#64748b");
  } else {
    // SYSTEM
    const isDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    applyTheme(isDark ? "DARK" : "LIGHT");
  }
};

// مراقبة وحفظ التفضيلات
const savePreferences = () => {
  form.post("/auth/profile/update/", {
    preserveScroll: true,
    onSuccess: () => {
      if (user.value?.theme) {
        applyTheme(user.value.theme);
      }
    },
  });
};

// تطبيق المظهر المختار عند التحميل الأولي
onMounted(() => {
  if (user.value?.theme) {
    applyTheme(user.value.theme);
  }
});

// مراقبة تفضيلات المستخدم القادمة من السيرفر وتحديث الفورم تلقائياً
watch(
  user,
  (newUser) => {
    if (newUser) {
      form.language = newUser.language;
      form.theme = newUser.theme;
      form.timezone = newUser.timezone;
    }
  },
  { deep: true }
);
</script>

<template>
  <div class="min-h-screen bg-[var(--color-surface-muted)] py-12 px-4 sm:px-6 lg:px-8 transition-colors duration-300">
    <div class="max-w-4xl mx-auto space-y-8">
      
      <!-- Navbar / Header -->
      <div class="flex items-center justify-between bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl p-6 shadow-sm">
        <div class="flex items-center space-x-4">
          <div class="w-12 h-12 rounded-xl bg-[var(--color-primary)] flex items-center justify-center text-white font-bold text-xl shadow-md shadow-indigo-500/20">
            A
          </div>
          <div>
            <h1 class="text-xl font-bold text-[var(--color-text)]">AuraFlow Boilerplate</h1>
            <p class="text-sm text-[var(--color-text-muted)]">Secure Django + Inertia + Vue Starter</p>
          </div>
        </div>
        
        <div class="flex items-center space-x-3">
          <a
            href="/admin/"
            target="_blank"
            class="hidden sm:inline-flex items-center justify-center px-4 py-2 rounded-xl text-sm font-medium border border-[var(--color-border)] text-[var(--color-text)] bg-[var(--color-surface-muted)] hover:bg-[var(--color-border)] transition-colors cursor-pointer"
          >
            Admin Panel 🛡️
          </a>
          <Link
            href="/auth/logout/"
            method="post"
            as="button"
            class="px-4 py-2 rounded-xl text-sm font-medium bg-[var(--color-danger)] text-white hover:opacity-90 transition-opacity cursor-pointer"
          >
            Logout
          </Link>
        </div>
      </div>

      <!-- Main Profile & Settings Grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        
        <!-- Sidebar Info -->
        <div class="md:col-span-1 space-y-6">
          <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl p-6 shadow-sm text-center">
            <div class="relative w-24 h-24 mx-auto mb-4">
              <div class="w-full h-full rounded-full bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center text-white text-3xl font-bold shadow-inner">
                {{ user?.email?.charAt(0).toUpperCase() }}
              </div>
              <span class="absolute bottom-0 right-2 w-5 h-5 bg-green-500 border-4 border-[var(--color-surface)] rounded-full"></span>
            </div>
            
            <h2 class="text-lg font-bold text-[var(--color-text)] truncate">{{ user?.email }}</h2>
            <p class="text-xs text-[var(--color-text-muted)] mb-4">Verified Member</p>
            
            <div class="pt-4 border-t border-[var(--color-border)] text-left space-y-2">
              <div class="flex justify-between text-xs">
                <span class="text-[var(--color-text-muted)]">Language:</span>
                <span class="font-medium text-[var(--color-text)]">{{ user?.language === 'ar' ? 'العربية' : 'English' }}</span>
              </div>
              <div class="flex justify-between text-xs">
                <span class="text-[var(--color-text-muted)]">Theme:</span>
                <span class="font-medium text-[var(--color-text)]">{{ user?.theme }}</span>
              </div>
              <div class="flex justify-between text-xs">
                <span class="text-[var(--color-text-muted)]">Timezone:</span>
                <span class="font-medium text-[var(--color-text)] truncate max-w-[120px]">{{ user?.timezone }}</span>
              </div>
            </div>
          </div>

          <!-- Allauth Features Links -->
          <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl p-6 shadow-sm space-y-4">
            <h3 class="text-sm font-bold text-[var(--color-text)] uppercase tracking-wider">Allauth Security Features</h3>
            <p class="text-xs text-[var(--color-text-muted)]">Built-in authentication capabilities ready for exploration:</p>
            
            <div class="space-y-2.5">
              <a
                href="/accounts/password/change/"
                class="flex items-center justify-between p-3 rounded-xl bg-[var(--color-surface-muted)] border border-[var(--color-border)] hover:border-[var(--color-primary)] transition-all group"
              >
                <span class="text-xs font-medium text-[var(--color-text)]">Change Password</span>
                <span class="text-[var(--color-primary)] opacity-60 group-hover:opacity-100 transition-opacity">→</span>
              </a>
              <a
                href="/accounts/mfa/list/"
                class="flex items-center justify-between p-3 rounded-xl bg-[var(--color-surface-muted)] border border-[var(--color-border)] hover:border-[var(--color-primary)] transition-all group"
              >
                <span class="text-xs font-medium text-[var(--color-text)]">Configure Two-Factor (2FA)</span>
                <span class="text-[var(--color-primary)] opacity-60 group-hover:opacity-100 transition-opacity">→</span>
              </a>
              <a
                href="/accounts/social/connections/"
                class="flex items-center justify-between p-3 rounded-xl bg-[var(--color-surface-muted)] border border-[var(--color-border)] hover:border-[var(--color-primary)] transition-all group"
              >
                <span class="text-xs font-medium text-[var(--color-text)]">Linked Accounts (OAuth)</span>
                <span class="text-[var(--color-primary)] opacity-60 group-hover:opacity-100 transition-opacity">→</span>
              </a>
            </div>
          </div>
        </div>

        <!-- Form settings -->
        <div class="md:col-span-2 space-y-6">
          <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl p-8 shadow-sm">
            <h2 class="text-xl font-bold text-[var(--color-text)] mb-6">User Preferences & Settings</h2>
            
            <form @submit.prevent="savePreferences" class="space-y-6">
              
              <!-- Language Dropdown -->
              <div>
                <label for="language" class="block text-sm font-medium text-[var(--color-text)] mb-2">
                  Preferred Language / لغة التطبيق
                </label>
                <select
                  id="language"
                  v-model="form.language"
                  class="w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-muted)] text-[var(--color-text)] px-4 py-3 text-sm outline-none transition-all focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"
                >
                  <option v-for="lang in languages" :key="lang.value" :value="lang.value">
                    {{ lang.label }}
                  </option>
                </select>
              </div>

              <!-- Theme Dropdown -->
              <div>
                <label for="theme" class="block text-sm font-medium text-[var(--color-text)] mb-2">
                  Select Theme / مظهر الواجهة
                </label>
                <select
                  id="theme"
                  v-model="form.theme"
                  class="w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-muted)] text-[var(--color-text)] px-4 py-3 text-sm outline-none transition-all focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"
                >
                  <option v-for="t in themes" :key="t.value" :value="t.value">
                    {{ t.label }}
                  </option>
                </select>
              </div>

              <!-- Timezone Dropdown -->
              <div>
                <label for="timezone" class="block text-sm font-medium text-[var(--color-text)] mb-2">
                  Local Timezone / المنطقة الزمنية
                </label>
                <select
                  id="timezone"
                  v-model="form.timezone"
                  class="w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-muted)] text-[var(--color-text)] px-4 py-3 text-sm outline-none transition-all focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"
                >
                  <option v-for="tz in commonTimezones" :key="tz" :value="tz">
                    {{ tz }}
                  </option>
                </select>
                <p class="mt-2 text-xs text-[var(--color-text-muted)]">
                  Used for aligning schedulers, logging auditing trails, and date formats.
                </p>
              </div>

              <!-- Submit Button -->
              <div class="pt-4 border-t border-[var(--color-border)] flex items-center justify-end">
                <button
                  type="submit"
                  :disabled="form.processing"
                  class="px-6 py-2.5 rounded-xl bg-[var(--color-primary)] text-white font-medium text-sm hover:bg-[var(--color-primary-hover)] disabled:opacity-50 transition-colors shadow-md shadow-indigo-500/10 cursor-pointer"
                >
                  <span v-if="!form.processing">Save Preferences</span>
                  <span v-else>Saving Changes...</span>
                </button>
              </div>
            </form>
          </div>
        </div>

      </div>

    </div>
  </div>
</template>
