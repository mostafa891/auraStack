import { computed } from "vue";
import { usePage } from "@inertiajs/vue3";
import type { SharedErrors } from "@/types/inertia";

/**
 * Composable to extract and format shared Inertia form errors.
 *
 * Details:
 * - Django shares form validation errors via `share(request, errors={...})`
 * - Formats raw `{ field: [{message, code}] }` into simplified `{ field: "first message string" }`
 */
export function useFormErrors() {
  const page = usePage();

  /** Raw errors payload returned from Django */
  const rawErrors = computed<SharedErrors>(
    () => (page.props.errors as unknown as SharedErrors) ?? null
  );

  /** Specific error code string (e.g. INVALID_CREDENTIALS, EMAIL_ALREADY_EXISTS) */
  const errorCode = computed<string | null>(
    () => (page.props.error_code as string | null) ?? null
  );

  /** Formatted errors: maps each field key to its primary message string */
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

  /** Get error message for a specific form field */
  function getFieldError(field: string): string | undefined {
    return fieldErrors.value[field];
  }

  /** Check if general non-field errors exist */
  const hasGeneralError = computed(() => {
    return !!fieldErrors.value["__all__"] || !!errorCode.value;
  });

  /** Primary general error message */
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
