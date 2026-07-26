import { createApp, h, type DefineComponent } from "vue";
import { createInertiaApp } from "@inertiajs/vue3";
import { createPinia } from "pinia";
import ToastContainer from "@/layouts/ToastContainer.vue";
import "@/app.css";

// Handle Inertia v2/v3 compatibility bridge with django-inertia backend container:
// Parses the dataset page attributes attached to the root mount element
const el = document.getElementById("app");
const page = el && el.dataset.page ? JSON.parse(el.dataset.page) : undefined;

createInertiaApp({
  page,
  resolve: (name: string) => {
    // Dynamically resolve page components lazily from pages/ directory
    const pages = import.meta.glob<DefineComponent>("./pages/**/*.vue");

    const pageModule = pages[`./pages/${name}.vue`];

    if (!pageModule) {
      throw new Error(
        `Page not found: ${name}. Check that ./pages/${name}.vue exists.`
      );
    }

    // Support async promise module imports in Inertia v3
    return typeof pageModule === "function" ? pageModule() : pageModule;
  },

  setup({ el, App, props, plugin }) {
    // Mount root wrapper containing the Inertia App and Toast notifications container
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
