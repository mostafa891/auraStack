/**
 * TypeScript definitions for Inertia shared props.
 *
 * Defines the structure of data passed from Django to Vue
 * via Inertia `share()` — any backend payload changes must be updated here.
 */

/** Single field error structure returned from Django Form errors */
export interface FieldError {
  message: string;
  code: string;
}

/** Errors shared via Inertia share() */
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

/** Complete Shared Props payload sent by Inertia on every response */
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

/** Helper type to define props for any Inertia page */
export type PageProps<T extends Record<string, unknown> = Record<string, unknown>> =
  T & SharedProps;
