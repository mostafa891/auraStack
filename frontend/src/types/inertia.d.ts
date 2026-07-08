/**
 * TypeScript definitions for Inertia shared props.
 *
 * الأنواع دي بتحدد شكل البيانات اللي Django بيبعتها لـ Vue
 * عبر Inertia `share()` — أي حاجة تتغير في الباك إند لازم تتحدث هنا.
 */

/** شكل الخطأ الواحد كما يرجع من Django Form errors */
export interface FieldError {
  message: string;
  code: string;
}

/** الأخطاء المُشاركة عبر Inertia share() */
export type SharedErrors = Record<string, FieldError[]> | null;

/** كل الـ Shared Props اللي Inertia بيبعتها مع كل Response */
export interface SharedProps {
  errors?: SharedErrors;
  error_code?: string | null;
}

/** لتعريف props أي صفحة Inertia */
export type PageProps<T extends Record<string, unknown> = Record<string, unknown>> =
  T & SharedProps;
