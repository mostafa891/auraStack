import { createApp, h, type DefineComponent } from "vue";
import { createInertiaApp } from "@inertiajs/vue3";
import { createPinia } from "pinia";
import "@/app.css";

// حل توافقية Inertia v2/v3 مع django-inertia:
// حزم الباك إند القديمة تنشئ حاوية <div> بينما الإصدارات الحديثة للفرونت إند تتوقع عنصر <script>
const el = document.getElementById("app");
const page = el && el.dataset.page ? JSON.parse(el.dataset.page) : undefined;

createInertiaApp({
  page,
  resolve: (name: string) => {
    // تحميل الصفحات ديناميكياً من مجلد pages/
    const pages = import.meta.glob<DefineComponent>("./pages/**/*.vue", {
      eager: true,
    });

    const pageModule = pages[`./pages/${name}.vue`];

    if (!pageModule) {
      throw new Error(
        `Page not found: ${name}. Check that ./pages/${name}.vue exists.`
      );
    }

    return pageModule;
  },

  setup({ el, App, props, plugin }) {
    const app = createApp({ render: () => h(App, props) });

    app.use(plugin);
    app.use(createPinia());

    app.mount(el);
  },
});
