<script setup lang="ts">
import { ref, computed, watchEffect } from "vue";
import { usePage, useForm, Link, router } from "@inertiajs/vue3";
import type { SharedProps } from "@/types/inertia";
import { useI18n } from "@/composables/useI18n";
import { usePreferencesStore } from "@/stores/preferences";

// تعريف أنواع الخصائص الممررة من الباك إند
const props = defineProps<{
  workspace: {
    id: string;
    name: string;
    slug: string;
    role: string;
  };
  members: Array<{
    id: string;
    email: string;
    role: string;
    role_display: string;
    avatar_url: string;
    joined_at: string;
    is_self: boolean;
  }>;
  invitations: Array<{
    id: string;
    token: string;
    email: string;
    role: string;
    role_display: string;
    status: string;
    status_display: string;
    expires_at: string;
  }>;
}>();

const page = usePage<SharedProps>();
const user = computed(() => page.props.auth?.user);
const preferencesStore = usePreferencesStore();

const { t, locale, toggleLocale } = useI18n();

watchEffect(() => {
  document.documentElement.dir = locale.value === "ar" ? "rtl" : "ltr";
  document.documentElement.lang = locale.value;
});

// التحقق مما إذا كان المستخدم يملك صلاحية التعديل (OWNER أو ADMIN)
const canManage = computed(() => props.workspace.role === "OWNER" || props.workspace.role === "ADMIN");
const isOwner = computed(() => props.workspace.role === "OWNER");

// 1. فورم تحديث إعدادات مساحة العمل
const settingsForm = useForm({
  name: props.workspace.name,
  slug: props.workspace.slug,
});

const updateWorkspace = () => {
  settingsForm.post(`/workspaces/${props.workspace.slug}/settings/`, {
    preserveScroll: true,
  });
};

// 2. فورم دعوة عضو جديد
const inviteForm = useForm({
  email: "",
  role: "MEMBER",
});

const sendInvitation = () => {
  inviteForm.post(`/workspaces/${props.workspace.slug}/invite/`, {
    preserveScroll: true,
    onSuccess: () => {
      inviteForm.reset("email");
    },
  });
};

// 3. تعديل دور عضو في الفريق
const updateMemberRole = (memberId: string, newRole: string) => {
  router.post(`/workspaces/${props.workspace.slug}/members/${memberId}/update/`, {
    role: newRole,
  }, {
    preserveScroll: true,
  });
};

// 4. حذف عضو أو مغادرة مساحة العمل
const removeMember = (memberId: string, isSelf: boolean) => {
  const confirmMsg = isSelf 
    ? t("workspace.confirm_leave")
    : t("workspace.confirm_remove");

  if (confirm(confirmMsg)) {
    router.post(`/workspaces/${props.workspace.slug}/members/${memberId}/delete/`, {}, {
      preserveScroll: true,
    });
  }
};

// 5. إلغاء دعوة معلقة
const showConfirmRevoke = ref(false);
const targetRevokeId = ref<string | null>(null);

const confirmRevoke = (invitationId: string) => {
  targetRevokeId.value = invitationId;
  showConfirmRevoke.value = true;
};

const executeRevoke = () => {
  if (targetRevokeId.value) {
    router.post(`/workspaces/${props.workspace.slug}/invitations/${targetRevokeId.value}/delete/`, {}, {
      preserveScroll: true,
      onSuccess: () => {
        showConfirmRevoke.value = false;
        targetRevokeId.value = null;
      }
    });
  }
};

// 6. نسخ رابط الدعوة إلى الحافظة
const copiedInviteId = ref<string | null>(null);

const copyInviteLink = (token: string, inviteId: string) => {
  const link = `${window.location.origin}/workspaces/invitations/${token}/accept/`;
  navigator.clipboard.writeText(link).then(() => {
    copiedInviteId.value = inviteId;
    setTimeout(() => {
      copiedInviteId.value = null;
    }, 2000);
  });
};
</script>

<template>
  <div class="min-h-screen bg-[var(--color-bg)] py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-5xl mx-auto space-y-8">
      
      <!-- Top Navigation Header -->
      <div class="flex items-center justify-between border-b border-[var(--color-border)] pb-6">
        <div class="flex items-center gap-3">
          <Link
            href="/workspaces/"
            class="p-2 rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)] hover:bg-[var(--color-surface-muted)] text-[var(--color-text-muted)] hover:text-[var(--color-text)] transition-colors text-sm"
          >
            ←
          </Link>
          <div>
            <span class="text-xs font-semibold text-[var(--color-primary)] uppercase tracking-wider">{{ t('nav.workspace_dashboard') }}</span>
            <h1 class="text-2xl font-extrabold text-[var(--color-text)] tracking-tight">
              {{ workspace.name }} {{ t('workspace.title_suffix') }}
            </h1>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <button
            @click="toggleLocale"
            class="inline-flex items-center justify-center px-3.5 py-1.5 rounded-xl text-xs font-semibold border border-[var(--color-border)] text-[var(--color-text)] bg-[var(--color-surface)] hover:bg-[var(--color-surface-muted)] transition-colors cursor-pointer select-none"
          >
            🌐 {{ locale === 'ar' ? 'English' : 'العربية' }}
          </button>
          <span 
            class="text-xs font-bold px-3 py-1.5 rounded-xl uppercase border"
            :class="{
              'bg-indigo-50 border-indigo-200 text-indigo-700 dark:bg-indigo-950/20 dark:border-indigo-900/50 dark:text-indigo-400': workspace.role === 'OWNER',
              'bg-emerald-50 border-emerald-200 text-emerald-700 dark:bg-emerald-950/20 dark:border-emerald-900/50 dark:text-emerald-400': workspace.role === 'ADMIN',
              'bg-gray-50 border-gray-200 text-gray-700 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-400': workspace.role === 'MEMBER',
            }"
          >
            {{ t('workspace.your_role') }}: {{ workspace.role }}
          </span>
        </div>
      </div>

      <!-- Main Columns -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <!-- Left Side: Settings Form (2/3 width on wide screens) -->
        <div class="lg:col-span-2 space-y-8">
          
          <!-- Workspace Profile Update -->
          <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl p-6 md:p-8 shadow-sm">
            <h2 class="text-lg font-bold text-[var(--color-text)] mb-4">{{ t('workspace.details_title') }}</h2>
            
            <form @submit.prevent="updateWorkspace" class="space-y-4">
              <div>
                <label for="name" class="block text-xs font-semibold text-[var(--color-text)] mb-1">
                  {{ t('workspace.name_label') }}
                </label>
                <input
                  id="name"
                  type="text"
                  v-model="settingsForm.name"
                  :disabled="!canManage"
                  class="w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-muted)] text-[var(--color-text)] px-4 py-2.5 text-sm outline-none transition-all focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20 disabled:opacity-50"
                  required
                />
                <span v-if="settingsForm.errors.name" class="text-xs text-red-500 mt-1 block">
                  {{ settingsForm.errors.name[0] }}
                </span>
              </div>

              <div>
                <label for="slug" class="block text-xs font-semibold text-[var(--color-text)] mb-1">
                  {{ t('workspace.slug_label') }}
                </label>
                <div class="flex rounded-xl overflow-hidden border border-[var(--color-border)] focus-within:ring-2 focus-within:ring-[var(--color-primary)]/20 focus-within:border-[var(--color-primary)]">
                  <span class="bg-[var(--color-surface-muted)] text-[var(--color-text-muted)] text-xs px-3 flex items-center border-r border-[var(--color-border)] font-medium select-none">
                    /workspaces/
                  </span>
                  <input
                    id="slug"
                    type="text"
                    v-model="settingsForm.slug"
                    :disabled="!canManage"
                    class="w-full bg-[var(--color-surface-muted)] text-[var(--color-text)] px-4 py-2.5 text-sm outline-none border-none disabled:opacity-50"
                    required
                  />
                </div>
                <p class="text-[10px] text-[var(--color-text-muted)] mt-1.5">
                  The slug is used in URLs to access this workspace. Allowed: alphanumeric characters, hyphens, and Arabic letters.
                </p>
                <span v-if="settingsForm.errors.slug" class="text-xs text-red-500 mt-1 block">
                  {{ settingsForm.errors.slug[0] }}
                </span>
              </div>

              <div v-if="canManage" class="flex justify-end pt-2">
                <button
                  type="submit"
                  :disabled="settingsForm.processing"
                  class="px-5 py-2 rounded-xl bg-[var(--color-primary)] text-white text-xs font-semibold hover:bg-[var(--color-primary-hover)] disabled:opacity-50 transition-all cursor-pointer"
                >
                  <span v-if="!settingsForm.processing">{{ t('common.save') }}</span>
                  <span v-else>{{ t('common.saving') }}</span>
                </button>
              </div>
            </form>
          </div>

          <!-- Team Members Management -->
          <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl p-6 md:p-8 shadow-sm">
            <h2 class="text-lg font-bold text-[var(--color-text)] mb-4">{{ t('workspace.members_title') }}</h2>
            
            <div class="overflow-x-auto">
              <table class="w-full text-left border-collapse">
                <thead>
                  <tr class="border-b border-[var(--color-border)] text-xs text-[var(--color-text-muted)] uppercase tracking-wider">
                    <th class="py-3 font-semibold">{{ t('workspace.invite_email') }}</th>
                    <th class="py-3 font-semibold">{{ t('workspace.joined') }}</th>
                    <th class="py-3 font-semibold">{{ t('common.role') }}</th>
                    <th class="py-3 font-semibold text-right"></th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-[var(--color-border)] text-sm">
                  <tr v-for="member in members" :key="member.id" class="align-middle">
                    <td class="py-4 flex items-center gap-3">
                      <img :src="member.avatar_url" class="w-8 h-8 rounded-full border border-[var(--color-border)]" alt="Avatar"/>
                      <div>
                        <div class="font-bold text-[var(--color-text)] flex items-center gap-1.5">
                          {{ member.email }}
                          <span v-if="member.is_self" class="text-[9px] font-bold px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 text-[var(--color-text-muted)] rounded">
                            {{ locale === 'ar' ? 'أنت' : 'You' }}
                          </span>
                        </div>
                      </div>
                    </td>
                    <td class="py-4 text-xs text-[var(--color-text-muted)]">
                      {{ member.joined_at }}
                    </td>
                    <td class="py-4">
                      <!-- Dropdown role select for Owner/Admin to change roles -->
                      <select
                        v-if="canManage && !member.is_self && (isOwner || member.role !== 'OWNER')"
                        :value="member.role"
                        @change="updateMemberRole(member.id, ($event.target as HTMLSelectElement).value)"
                        class="rounded-lg border border-[var(--color-border)] bg-[var(--color-surface-muted)] text-[var(--color-text)] px-2 py-1 text-xs outline-none transition-all focus:border-[var(--color-primary)]"
                      >
                        <option value="OWNER">{{ t('workspace.role_owner') }}</option>
                        <option value="ADMIN">{{ t('workspace.role_admin') }}</option>
                        <option value="MEMBER">{{ t('workspace.role_member') }}</option>
                      </select>
                      <span v-else class="text-xs font-semibold text-[var(--color-text)]">
                        {{ member.role_display }}
                      </span>
                    </td>
                    <td class="py-4 text-right">
                      <!-- Leave or Remove button -->
                      <button
                        v-if="member.is_self"
                        @click="removeMember(member.id, true)"
                        class="px-2.5 py-1 rounded bg-red-50 hover:bg-red-100 text-red-600 dark:bg-red-950/20 dark:hover:bg-red-950/30 text-xs font-medium transition-colors cursor-pointer"
                      >
                        {{ t('workspace.leave_workspace_btn') }}
                      </button>
                      <button
                        v-else-if="canManage && (isOwner || member.role !== 'OWNER')"
                        @click="removeMember(member.id, false)"
                        class="px-2.5 py-1 rounded bg-red-50 hover:bg-red-100 text-red-600 dark:bg-red-950/20 dark:hover:bg-red-950/30 text-xs font-medium transition-colors cursor-pointer"
                      >
                        {{ t('workspace.remove_member_btn') }}
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

        </div>

        <!-- Right Side: Invitations (1/3 width) -->
        <div class="space-y-8">
          
          <!-- Send Invitation Card -->
          <div v-if="canManage" class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl p-6 shadow-sm">
            <h3 class="text-base font-bold text-[var(--color-text)] mb-3">{{ t('workspace.invite_title') }}</h3>
            
            <form @submit.prevent="sendInvitation" class="space-y-4">
              <div>
                <label for="invite-email" class="block text-xs font-semibold text-[var(--color-text)] mb-1">
                  {{ t('workspace.invite_email') }}
                </label>
                <input
                  id="invite-email"
                  type="email"
                  v-model="inviteForm.email"
                  placeholder="name@example.com"
                  class="w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-muted)] text-[var(--color-text)] px-4 py-2 text-sm outline-none transition-all focus:border-[var(--color-primary)]"
                  required
                />
              </div>

              <div>
                <label for="invite-role" class="block text-xs font-semibold text-[var(--color-text)] mb-1">
                  {{ t('common.role') }}
                </label>
                <select
                  id="invite-role"
                  v-model="inviteForm.role"
                  class="w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-muted)] text-[var(--color-text)] px-4 py-2 text-sm outline-none transition-all focus:border-[var(--color-primary)]"
                >
                  <option value="MEMBER">{{ t('workspace.role_member') }}</option>
                  <option value="ADMIN">{{ t('workspace.role_admin') }}</option>
                  <option value="OWNER">{{ t('workspace.role_owner') }}</option>
                </select>
              </div>

              <button
                type="submit"
                :disabled="inviteForm.processing"
                class="w-full py-2.5 rounded-xl bg-[var(--color-primary)] text-white text-xs font-semibold hover:bg-[var(--color-primary-hover)] disabled:opacity-50 transition-all cursor-pointer"
              >
                <span v-if="!inviteForm.processing">{{ t('workspace.invite_btn') }}</span>
                <span v-else>{{ t('common.sending') }}</span>
              </button>
            </form>
          </div>

          <!-- Pending Invitations List -->
          <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl p-6 shadow-sm space-y-4">
            <h3 class="text-base font-bold text-[var(--color-text)]">{{ t('workspace.pending_title') }} ({{ invitations.length }})</h3>
            
            <div v-if="invitations.length === 0" class="text-center py-6 text-xs text-[var(--color-text-muted)]">
              {{ t('workspace.no_pending') }}
            </div>
            
            <div v-else class="space-y-3.5">
              <div 
                v-for="invite in invitations" 
                :key="invite.id" 
                class="p-3 rounded-xl bg-[var(--color-surface-muted)] border border-[var(--color-border)] space-y-2 flex flex-col justify-between"
              >
                <div>
                  <div class="text-xs font-bold text-[var(--color-text)] truncate" :title="invite.email">
                    {{ invite.email }}
                  </div>
                  <div class="flex justify-between items-center text-[10px] text-[var(--color-text-muted)] mt-1">
                    <span>{{ t('common.role') }}: {{ invite.role_display }}</span>
                    <span>{{ locale === 'ar' ? 'تاريخ الانتهاء' : 'Expires' }}: {{ invite.expires_at }}</span>
                  </div>
                </div>

                <div class="flex items-center gap-1.5 pt-2 border-t border-[var(--color-border)]/50 justify-end">
                  <button
                    v-if="canManage"
                    @click="confirmRevoke(invite.id)"
                    class="px-2 py-1 text-[10px] font-semibold rounded bg-red-50 text-red-600 dark:bg-red-950/20 hover:bg-red-100 transition-colors cursor-pointer"
                  >
                    {{ t('common.revoke') }}
                  </button>
                  
                  <!-- Copy Invite link simulation for easier testing -->
                  <button
                    @click="copyInviteLink(invite.token, invite.id)"
                    class="px-2 py-1 text-[10px] font-semibold rounded bg-indigo-50 text-indigo-600 dark:bg-indigo-950/20 hover:bg-indigo-100 transition-colors cursor-pointer flex items-center gap-1"
                  >
                    <span>{{ copiedInviteId === invite.id ? t('common.copied') : t('common.copy_link') }}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

        </div>

      </div>

    </div>

    <!-- Beautiful Modern Confirmation Modal for Revoking Invitations -->
    <div v-if="showConfirmRevoke" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm transition-all duration-300">
      <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-6 scale-100 transform transition-all">
        <div class="flex items-center gap-3 text-red-500">
          <span class="text-2xl">⚠️</span>
          <h3 class="text-lg font-bold text-[var(--color-text)]">{{ t('workspace.revoke_modal_title') }}</h3>
        </div>
        <p class="text-sm text-[var(--color-text-muted)] leading-relaxed">
          {{ t('workspace.revoke_modal_desc') }}
        </p>
        <div class="flex items-center justify-end gap-3 pt-2">
          <button
            @click="showConfirmRevoke = false"
            class="px-4 py-2 text-xs font-semibold rounded-xl border border-[var(--color-border)] text-[var(--color-text)] hover:bg-[var(--color-surface-muted)] transition-colors cursor-pointer"
          >
            {{ t('common.cancel') }}
          </button>
          <button
            @click="executeRevoke"
            class="px-4 py-2 text-xs font-semibold rounded-xl bg-red-500 hover:bg-red-600 text-white transition-colors cursor-pointer"
          >
            {{ locale === 'ar' ? 'تأكيد إلغاء الدعوة' : 'Confirm Revoke' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
