import { computed } from "vue";
import { usePage, router } from "@inertiajs/vue3";
import en from "@/locales/en.json";
import ar from "@/locales/ar.json";

const messages: Record<string, any> = { en, ar };

export function useI18n() {
  const page = usePage();
  
  // Get active locale from shared Inertia props, defaulting to 'en'
  const locale = computed(() => (page.props.locale as string) || "en");

  // Translation helper function
  const t = (key: string): string => {
    const lang = locale.value;
    const trans = messages[lang] || messages["en"];
    const value = key.split(".").reduce((o, i) => o?.[i], trans);
    return typeof value === "string" ? value : key;
  };

  // Toggle active language via POST request to Django SetLanguageView
  const toggleLocale = () => {
    const nextLang = locale.value === "ar" ? "en" : "ar";
    router.post(
      "/auth/set-language/",
      { language: nextLang },
      {
        preserveScroll: true,
        onSuccess: () => {
          // Adjust root document direction and lang attributes
          document.documentElement.dir = nextLang === "ar" ? "rtl" : "ltr";
          document.documentElement.lang = nextLang;
        },
      }
    );
  };

  return {
    t,
    locale,
    toggleLocale,
  };
}
