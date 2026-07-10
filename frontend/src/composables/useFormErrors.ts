import { computed } from "vue";
import { usePage } from "@inertiajs/vue3";
import type { SharedErrors } from "@/types/inertia";

/**
 * Composable لاستخراج أخطاء Inertia المُشاركة وتحويلها لصيغة سهلة الاستخدام.
 *
 * الفكرة:
 * - Django بيبعت الأخطاء عبر `share(request, errors={...})`
 * - الـ Composable ده بيحولها من `{ field: [{message, code}] }`
 *   لـ `{ field: "first error message" }` عشان تربطها بالـ Form بسهولة.
 */
export function useFormErrors() {
  const page = usePage();

  /** الأخطاء الخام من Django */
  const rawErrors = computed<SharedErrors>(
    () => (page.props.errors as unknown as SharedErrors) ?? null
  );

  /** كود الخطأ (مثل INVALID_CREDENTIALS, EMAIL_ALREADY_EXISTS) */
  const errorCode = computed<string | null>(
    () => (page.props.error_code as string | null) ?? null
  );

  /** أخطاء مبسّطة: كل حقل يرجع أول رسالة خطأ فقط */
  const fieldErrors = computed<Record<string, string>>(() => {
    const errors = rawErrors.value;
    if (!errors) return {};

    const result: Record<string, string> = {};
    for (const [field, messages] of Object.entries(errors)) {
      if (Array.isArray(messages) && messages.length > 0) {
        const msg = messages[0];
        if (typeof msg === "string") {
          result[field] = msg;
        } else if (msg && typeof msg === "object" && "message" in msg) {
          result[field] = (msg as any).message;
        }
      }
    }
    return result;
  });

  /** استخراج خطأ حقل معين */
  function getFieldError(field: string): string | undefined {
    return fieldErrors.value[field];
  }

  /** هل فيه أخطاء عامة (مش مرتبطة بحقل معين)? */
  const hasGeneralError = computed(() => {
    return !!fieldErrors.value["__all__"] || !!errorCode.value;
  });

  /** رسالة الخطأ العام */
  const generalError = computed(() => {
    if (fieldErrors.value["__all__"]) return fieldErrors.value["__all__"];
    if (errorCode.value === "INVALID_CREDENTIALS") return "Invalid email or password.";
    if (errorCode.value === "EMAIL_ALREADY_EXISTS") return "This email is already registered.";
    if (errorCode.value === "ACCOUNT_INACTIVE") return "This account has been deactivated.";
    return null;
  });

  return {
    rawErrors,
    errorCode,
    fieldErrors,
    getFieldError,
    hasGeneralError,
    generalError,
  };
}
