import { defineStore } from "pinia";
import { ref, watch, computed } from "vue";
import { usePage } from "@inertiajs/vue3";

export type Theme = "LIGHT" | "DARK" | "SYSTEM";
export type Language = "en" | "ar";

export const usePreferencesStore = defineStore("preferences", () => {
  const page = usePage() as any;

  // 1. تحديد القيم الافتراضية بناء على بيانات السيرفر أو التخزين المحلي
  const getInitialTheme = (): Theme => {
    const serverUser = page.props?.auth?.user as any;
    if (serverUser?.theme) return serverUser.theme as Theme;
    return (localStorage.getItem("theme") as Theme) || "SYSTEM";
  };

  const getInitialLanguage = (): Language => {
    const serverLocale = page.props?.locale as Language;
    if (serverLocale) return serverLocale;
    const serverUser = page.props?.auth?.user as any;
    if (serverUser?.language) return serverUser.language as Language;
    return (localStorage.getItem("language") as Language) || "en";
  };

  const getInitialTimezone = (): string => {
    const serverUser = page.props?.auth?.user as any;
    if (serverUser?.timezone) return serverUser.timezone;
    return localStorage.getItem("timezone") || "UTC";
  };

  // 2. التعريفات التفاعلية (Reactive State)
  const theme = ref<Theme>(getInitialTheme());
  const language = ref<Language>(getInitialLanguage());
  const timezone = ref<string>(getInitialTimezone());

  // 3. تحديث السمة بصرياً في المتصفح
  const applyTheme = (t: Theme) => {
    const root = document.documentElement;
    if (t === "DARK" || (t === "SYSTEM" && window.matchMedia("(prefers-color-scheme: dark)").matches)) {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
  };

  // 4. مراقبة التغييرات وحفظها محلياً للزوار
  watch(theme, (newTheme) => {
    localStorage.setItem("theme", newTheme);
    applyTheme(newTheme);
  }, { immediate: true });

  watch(language, (newLang) => {
    localStorage.setItem("language", newLang);
  }, { immediate: true });

  watch(timezone, (newTz) => {
    localStorage.setItem("timezone", newTz);
  }, { immediate: true });

  // 5. استقبال التحديثات من الخادم عند تغير البروبس الممررة من Inertia
  watch(() => page.props?.auth?.user, (newUser: any) => {
    if (newUser) {
      if (newUser.theme && newUser.theme !== theme.value) {
        theme.value = newUser.theme as Theme;
      }
      if (newUser.language && newUser.language !== language.value) {
        language.value = newUser.language as Language;
      }
      if (newUser.timezone && newUser.timezone !== timezone.value) {
        timezone.value = newUser.timezone;
      }
    }
  }, { deep: true });

  watch(() => page.props?.locale, (newLocale) => {
    if (newLocale && newLocale !== language.value) {
      language.value = newLocale as Language;
    }
  });

  return {
    theme,
    language,
    timezone,
    applyTheme,
  };
});
