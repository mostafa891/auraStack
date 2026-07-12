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

export interface AuthUser {
  id: string;
  email: string;
  avatar_url: string;
  language: string;
  theme: string;
  timezone: string;
  is_staff: boolean;
  is_superuser: boolean;
}

export interface WorkspaceSubscription {
  plan_id: string;
  status: string;
  current_period_end?: string | null;
  cancel_at_period_end: boolean;
  is_locked: boolean;
  max_members: number;
  member_count: number;
}

export interface WorkspaceInfo {
  id: string;
  name: string;
  slug: string;
  role: string;
  role_display: string;
  subscription?: WorkspaceSubscription | null;
}

/** كل الـ Shared Props اللي Inertia بيبعتها مع كل Response */
export interface SharedProps {
  errors?: SharedErrors;
  error_code?: string | null;
  auth: {
    user: AuthUser | null;
    workspaces?: WorkspaceInfo[];
    active_workspace?: WorkspaceInfo | null;
  };
  [key: string]: any;
}

/** لتعريف props أي صفحة Inertia */
export type PageProps<T extends Record<string, unknown> = Record<string, unknown>> =
  T & SharedProps;
