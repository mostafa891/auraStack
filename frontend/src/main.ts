import { createApp, h, type DefineComponent } from "vue";
import { createInertiaApp } from "@inertiajs/vue3";
import { createPinia } from "pinia";
import ToastContainer from "@/layouts/ToastContainer.vue";
import "@/app.css";

// حل توافقية Inertia v2/v3 مع django-inertia:
// حزم الباك إند القديمة تنشئ حاوية <div> بينما الإصدارات الحديثة للفرونت إند تتوقع عنصر <script>
const el = document.getElementById("app");
const page = el && el.dataset.page ? JSON.parse(el.dataset.page) : undefined;

createInertiaApp({
  page,
  resolve: (name: string) => {
    // تحميل الصفحات ديناميكياً ومجزءاً (Lazy Loading) من مجلد pages/
    const pages = import.meta.glob<DefineComponent>("./pages/**/*.vue");

    const pageModule = pages[`./pages/${name}.vue`];

    if (!pageModule) {
      throw new Error(
        `Page not found: ${name}. Check that ./pages/${name}.vue exists.`
      );
    }

    // دعم استيراد الوعد (Promise) في Inertia v3
    return typeof pageModule === "function" ? pageModule() : pageModule;
  },

  setup({ el, App, props, plugin }) {
    // بناء غلاف جذري يضم تطبيق Inertia بالإضافة لحاوية التنبيهات (Toasts)
    const RootApp = {
      render() {
        return h("div", [
          h(App, props),
          h(ToastContainer),
        ]);
      },
    };

    const app = createApp(RootApp);

    app.use(plugin);
    app.use(createPinia());

    app.mount(el);
  },
});
