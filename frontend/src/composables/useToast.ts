import { ref } from "vue";

export interface Toast {
  id: number;
  message: string;
  type: "success" | "error" | "info" | "warning";
  duration?: number;
}

const toasts = ref<Toast[]>([]);
let nextId = 0;

export function useToast() {
  function addToast(message: string, type: Toast["type"] = "info", duration = 4000) {
    const id = nextId++;
    const toast: Toast = { id, message, type, duration };
    toasts.value.push(toast);

    if (duration > 0) {
      setTimeout(() => {
        removeToast(id);
      }, duration);
    }
    return id;
  }

  function removeToast(id: number) {
    toasts.value = toasts.value.filter((t) => t.id !== id);
  }

  const toast = {
    success: (msg: string, duration?: number) => addToast(msg, "success", duration),
    error: (msg: string, duration?: number) => addToast(msg, "error", duration),
    info: (msg: string, duration?: number) => addToast(msg, "info", duration),
    warning: (msg: string, duration?: number) => addToast(msg, "warning", duration),
  };

  return {
    toasts,
    addToast,
    removeToast,
    toast,
  };
}
