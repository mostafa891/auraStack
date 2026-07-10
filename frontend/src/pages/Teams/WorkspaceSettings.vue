<script setup lang="ts">
import { ref, computed } from "vue";
import { usePage, useForm, Link, router } from "@inertiajs/vue3";
import type { SharedProps } from "@/types/inertia";

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
    ? "Are you sure you want to leave this workspace? / هل أنت متأكد من رغبتك في مغادرة مساحة العمل؟"
    : "Are you sure you want to remove this member? / هل أنت متأكد من رغبتك في إزالة هذا العضو؟";

  if (confirm(confirmMsg)) {
    router.post(`/workspaces/${props.workspace.slug}/members/${memberId}/delete/`, {}, {
      preserveScroll: true,
    });
  }
};

// 5. إلغاء دعوة معلقة
const revokeInvitation = (invitationId: string) => {
  if (confirm("Are you sure you want to revoke this invitation? / هل أنت متأكد من إلغاء هذه الدعوة؟")) {
    router.post(`/workspaces/${props.workspace.slug}/invitations/${invitationId}/delete/`, {}, {
      preserveScroll: true,
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
            <span class="text-xs font-semibold text-[var(--color-primary)] uppercase tracking-wider">Workspace Dashboard</span>
            <h1 class="text-2xl font-extrabold text-[var(--color-text)] tracking-tight">
              {{ workspace.name }} Settings
            </h1>
          </div>
        </div>
        <span 
          class="text-xs font-bold px-3 py-1.5 rounded-xl uppercase border"
          :class="{
            'bg-indigo-50 border-indigo-200 text-indigo-700 dark:bg-indigo-950/20 dark:border-indigo-900/50 dark:text-indigo-400': workspace.role === 'OWNER',
            'bg-emerald-50 border-emerald-200 text-emerald-700 dark:bg-emerald-950/20 dark:border-emerald-900/50 dark:text-emerald-400': workspace.role === 'ADMIN',
            'bg-gray-50 border-gray-200 text-gray-700 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-400': workspace.role === 'MEMBER',
          }"
        >
          Your Role: {{ workspace.role }}
        </span>
      </div>

      <!-- Main Columns -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <!-- Left Side: Settings Form (2/3 width on wide screens) -->
        <div class="lg:col-span-2 space-y-8">
          
          <!-- Workspace Profile Update -->
          <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl p-6 md:p-8 shadow-sm">
            <h2 class="text-lg font-bold text-[var(--color-text)] mb-4">Workspace Details / تفاصيل مساحة العمل</h2>
            
            <form @submit.prevent="updateWorkspace" class="space-y-4">
              <div>
                <label for="name" class="block text-xs font-semibold text-[var(--color-text)] mb-1">
                  Workspace Name
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
                  Workspace Slug (URL suffix)
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
                  <span v-if="!settingsForm.processing">Update Details</span>
                  <span v-else>Saving...</span>
                </button>
              </div>
            </form>
          </div>

          <!-- Team Members Management -->
          <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl p-6 md:p-8 shadow-sm">
            <h2 class="text-lg font-bold text-[var(--color-text)] mb-4">Team Members / أعضاء الفريق</h2>
            
            <div class="overflow-x-auto">
              <table class="w-full text-left border-collapse">
                <thead>
                  <tr class="border-b border-[var(--color-border)] text-xs text-[var(--color-text-muted)] uppercase tracking-wider">
                    <th class="py-3 font-semibold">User</th>
                    <th class="py-3 font-semibold">Joined At</th>
                    <th class="py-3 font-semibold">Role</th>
                    <th class="py-3 font-semibold text-right">Actions</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-[var(--color-border)] text-sm">
                  <tr v-for="member in members" :key="member.id" class="align-middle">
                    <td class="py-4 flex items-center gap-3">
                      <img :src="member.avatar_url" class="w-8 h-8 rounded-full border border-[var(--color-border)]" alt="Avatar"/>
                      <div>
                        <div class="font-bold text-[var(--color-text)] flex items-center gap-1.5">
                          {{ member.email }}
                          <span v-if="member.is_self" class="text-[9px] font-bold px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 text-[var(--color-text-muted)] rounded">You</span>
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
                        <option value="OWNER">Owner</option>
                        <option value="ADMIN">Admin</option>
                        <option value="MEMBER">Member</option>
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
                        Leave Workspace
                      </button>
                      <button
                        v-else-if="canManage && (isOwner || member.role !== 'OWNER')"
                        @click="removeMember(member.id, false)"
                        class="px-2.5 py-1 rounded bg-red-50 hover:bg-red-100 text-red-600 dark:bg-red-950/20 dark:hover:bg-red-950/30 text-xs font-medium transition-colors cursor-pointer"
                      >
                        Remove
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
            <h3 class="text-base font-bold text-[var(--color-text)] mb-3">Invite Team Member / دعوة عضو</h3>
            
            <form @submit.prevent="sendInvitation" class="space-y-4">
              <div>
                <label for="invite-email" class="block text-xs font-semibold text-[var(--color-text)] mb-1">
                  Email Address
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
                  Role
                </label>
                <select
                  id="invite-role"
                  v-model="inviteForm.role"
                  class="w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-muted)] text-[var(--color-text)] px-4 py-2 text-sm outline-none transition-all focus:border-[var(--color-primary)]"
                >
                  <option value="MEMBER">Member</option>
                  <option value="ADMIN">Admin</option>
                  <option value="OWNER">Owner</option>
                </select>
              </div>

              <button
                type="submit"
                :disabled="inviteForm.processing"
                class="w-full py-2.5 rounded-xl bg-[var(--color-primary)] text-white text-xs font-semibold hover:bg-[var(--color-primary-hover)] disabled:opacity-50 transition-all cursor-pointer"
              >
                <span v-if="!inviteForm.processing">Send Invitation</span>
                <span v-else>Inviting...</span>
              </button>
            </form>
          </div>

          <!-- Pending Invitations List -->
          <div class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl p-6 shadow-sm space-y-4">
            <h3 class="text-base font-bold text-[var(--color-text)]">Pending Invites ({{ invitations.length }})</h3>
            
            <div v-if="invitations.length === 0" class="text-center py-6 text-xs text-[var(--color-text-muted)]">
              No pending invitations / لا توجد دعوات معلقة
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
                    <span>Role: {{ invite.role_display }}</span>
                    <span>Expires: {{ invite.expires_at }}</span>
                  </div>
                </div>

                <div class="flex items-center gap-1.5 pt-2 border-t border-[var(--color-border)]/50 justify-end">
                  <button
                    v-if="canManage"
                    @click="revokeInvitation(invite.id)"
                    class="px-2 py-1 text-[10px] font-semibold rounded bg-red-50 text-red-600 dark:bg-red-950/20 hover:bg-red-100 transition-colors cursor-pointer"
                  >
                    Revoke
                  </button>
                  
                  <!-- Copy Invite link simulation for easier testing -->
                  <button
                    @click="copyInviteLink(invite.id, invite.id)"
                    class="px-2 py-1 text-[10px] font-semibold rounded bg-indigo-50 text-indigo-600 dark:bg-indigo-950/20 hover:bg-indigo-100 transition-colors cursor-pointer flex items-center gap-1"
                  >
                    <span>{{ copiedInviteId === invite.id ? 'Copied!' : 'Copy Link' }}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

        </div>

      </div>

    </div>
  </div>
</template>
