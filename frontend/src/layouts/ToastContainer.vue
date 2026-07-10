<script setup lang="ts">
import { useToast } from "@/composables/useToast";
import { usePage } from "@inertiajs/vue3";
import { watch } from "vue";

const page = usePage();
const { toasts, removeToast, toast } = useToast();

// مراقبة الرسائل المرسلة من الباك إند (Flash Messages)
watch(
  () => page.props.flash,
  (flash: any) => {
    if (flash && Array.isArray(flash)) {
      flash.forEach((msg: any) => {
        const tags = msg.tags || "";
        if (tags.includes("success")) {
          toast.success(msg.message);
        } else if (tags.includes("error")) {
          toast.error(msg.message);
        } else if (tags.includes("warning")) {
          toast.warning(msg.message);
        } else {
          toast.info(msg.message);
        }
      });
    }
  },
  { immediate: true, deep: true }
);

// مراقبة الأخطاء العامة غير المرتبطة بحقول محددة
watch(
  () => page.props.errors,
  (errors: any) => {
    if (errors && errors.__all__) {
      const messages = Array.isArray(errors.__all__) ? errors.__all__ : [errors.__all__];
      messages.forEach((msg: any) => {
        const text = typeof msg === "string" ? msg : msg.message;
        toast.error(text);
      });
    }
  },
  { deep: true }
);

// مراقبة أكواد الأخطاء الأمنية والمصادقة لعرض التنبيهات
watch(
  () => page.props.error_code,
  (code: any) => {
    if (code) {
      if (code === "INVALID_CREDENTIALS") {
        toast.error("Invalid email or password.");
      } else if (code === "EMAIL_ALREADY_EXISTS") {
        toast.error("This email is already registered.");
      } else if (code === "ACCOUNT_INACTIVE") {
        toast.error("This account has been deactivated.");
      }
    }
  }
);
</script>

<template>
  <div class="fixed top-5 right-5 z-50 flex flex-col space-y-3 max-w-sm w-full pointer-events-none px-4 sm:px-0">
    <TransitionGroup
      name="toast"
      tag="div"
      class="flex flex-col space-y-3 w-full"
    >
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="pointer-events-auto flex items-start ps-5 pe-4 py-4 rounded-xl border shadow-xl backdrop-blur-md transition-all duration-300 transform relative overflow-hidden
               bg-white/98 border-slate-150 text-slate-800
               dark:bg-slate-900/98 dark:border-slate-800 dark:text-slate-100"
      >
        <!-- شريط اللون الجانبي التفاعلي (Accent Left/Right Line) متوافق مع الاتجاهات -->
        <div
          class="absolute start-0 top-0 bottom-0 w-1.5"
          :class="{
            'bg-emerald-500': toast.type === 'success',
            'bg-rose-500': toast.type === 'error',
            'bg-indigo-500': toast.type === 'info',
            'bg-amber-500': toast.type === 'warning',
          }"
        ></div>

        <!-- Icon -->
        <span class="me-3 mt-0.5 flex-shrink-0">
          <!-- Success Icon -->
          <svg v-if="toast.type === 'success'" class="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <!-- Error Icon -->
          <svg v-else-if="toast.type === 'error'" class="w-5 h-5 text-rose-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <!-- Info Icon -->
          <svg v-else-if="toast.type === 'info'" class="w-5 h-5 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <!-- Warning Icon -->
          <svg v-else class="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </span>

        <!-- Message -->
        <div class="flex-1 text-sm font-semibold leading-5">
          {{ toast.message }}
        </div>

        <!-- Close Button -->
        <button
          @click="removeToast(toast.id)"
          class="ms-4 flex-shrink-0 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors cursor-pointer"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}
.toast-enter-from {
  opacity: 0;
  transform: translateY(-20px) scale(0.9);
}
.toast-leave-to {
  opacity: 0;
  transform: translateY(-20px) scale(0.9);
}
</style>
