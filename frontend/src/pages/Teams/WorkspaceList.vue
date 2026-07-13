<script setup lang="ts">
import { ref, computed } from "vue";
import { usePage, useForm, Link, router } from "@inertiajs/vue3";
import type { SharedProps } from "@/types/inertia";

const props = defineProps<{
  deleted_workspaces: Array<{
    id: string;
    name: string;
    slug: string;
    deleted_at: string;
  }>;
}>();

const page = usePage<SharedProps>();
const user = computed(() => page.props.auth?.user);
const workspaces = computed(() => page.props.auth?.workspaces || []);
const activeWorkspace = computed(() => page.props.auth?.active_workspace);

const restoreWorkspace = (workspaceId: string) => {
  router.post(`/workspaces/${workspaceId}/restore/`);
};

// فورم إنشاء مساحة عمل جديدة
const form = useForm({
  name: "",
});

const isModalOpen = ref(false);

const openModal = () => {
  form.name = "";
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
};

const createWorkspace = () => {
  form.post("/workspaces/", {
    onSuccess: () => {
      closeModal();
      form.reset();
    },
  });
};

const switchActiveWorkspace = (workspaceId: string) => {
  router.post("/workspaces/switch/", { workspace_id: workspaceId });
};
</script>

<template>
  <div class="min-h-screen bg-[var(--color-bg)] py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto space-y-8">
      
      <!-- Header -->
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-[var(--color-border)] pb-6">
        <div>
          <h1 class="text-3xl font-extrabold text-[var(--color-text)] tracking-tight">
            Workspaces / مساحات العمل
          </h1>
          <p class="mt-2 text-sm text-[var(--color-text-muted)]">
            Manage your teams, collaborate with members, and switch between your workspaces.
          </p>
        </div>
        <button
          @click="openModal"
          class="px-5 py-2.5 rounded-xl bg-[var(--color-primary)] text-white font-medium text-sm hover:bg-[var(--color-primary-hover)] transition-all shadow-md shadow-indigo-500/10 cursor-pointer flex items-center gap-2"
        >
          <span>+</span>
          <span>Create Workspace</span>
        </button>
      </div>

      <!-- Active Workspace Alert Banner -->
      <div 
        v-if="activeWorkspace" 
        class="p-4 rounded-2xl bg-[var(--color-primary)]/5 border border-[var(--color-primary)]/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
      >
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-[var(--color-primary)] flex items-center justify-center text-white font-bold text-lg shadow-sm">
            {{ activeWorkspace.name.charAt(0).toUpperCase() }}
          </div>
          <div>
            <div class="text-xs text-[var(--color-text-muted)] uppercase tracking-wider font-semibold">Active Workspace</div>
            <div class="text-sm font-bold text-[var(--color-text)]">{{ activeWorkspace.name }}</div>
          </div>
        </div>
        <Link
          :href="`/workspaces/${activeWorkspace.slug}/settings/`"
          class="px-4 py-2 rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)] text-xs font-semibold text-[var(--color-text)] hover:border-[var(--color-primary)] transition-all"
        >
          Workspace Settings / الإعدادات
        </Link>
      </div>

      <!-- Workspaces Grid/List -->
      <div class="space-y-4">
        <h2 class="text-lg font-bold text-[var(--color-text)]">
          Your Workspaces ({{ workspaces.length }})
        </h2>

        <div v-if="workspaces.length === 0" class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl p-12 text-center shadow-sm">
          <div class="text-4xl mb-3">🏢</div>
          <h3 class="text-base font-bold text-[var(--color-text)]">No Workspaces Found</h3>
          <p class="text-xs text-[var(--color-text-muted)] mt-1 max-w-sm mx-auto">
            You are not currently a member of any workspaces. Create a new one or ask for an invitation.
          </p>
          <button
            @click="openModal"
            class="mt-4 px-4 py-2 rounded-xl bg-[var(--color-primary)] text-white font-medium text-xs hover:bg-[var(--color-primary-hover)] transition-all cursor-pointer"
          >
            Create Your First Workspace
          </button>
        </div>

        <div v-else class="grid gap-4 md:grid-cols-2">
          <div
            v-for="ws in workspaces"
            :key="ws.id"
            class="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl p-6 shadow-sm transition-all hover:shadow-md flex flex-col justify-between gap-4"
            :class="{ 'ring-2 ring-[var(--color-primary)] bg-[var(--color-primary)]/[0.01] border-[var(--color-primary)]/30': activeWorkspace && activeWorkspace.id === ws.id }"
          >
            <div>
              <div class="flex justify-between items-start">
                <h3 class="font-bold text-base text-[var(--color-text)] truncate max-w-[200px]" :title="ws.name">
                  {{ ws.name }}
                </h3>
                <span
                  class="text-[10px] font-bold px-2 py-0.5 rounded-full uppercase"
                  :class="{
                    'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300': ws.role === 'OWNER',
                    'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300': ws.role === 'ADMIN',
                    'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300': ws.role === 'MEMBER',
                  }"
                >
                  {{ ws.role_display }}
                </span>
              </div>
              <p class="text-xs text-[var(--color-text-muted)] mt-1 truncate">
                slug: {{ ws.slug }}
              </p>
            </div>

            <div class="flex items-center gap-2 pt-4 border-t border-[var(--color-border)]/50">
              <button
                v-if="!activeWorkspace || activeWorkspace.id !== ws.id"
                @click="switchActiveWorkspace(ws.id)"
                class="flex-1 px-3 py-2 rounded-lg bg-[var(--color-surface-muted)] border border-[var(--color-border)] text-xs font-semibold text-[var(--color-text)] hover:border-[var(--color-primary)] transition-all cursor-pointer text-center"
              >
                Switch Active
              </button>
              <span
                v-else
                class="flex-1 px-3 py-2 rounded-lg bg-indigo-50 dark:bg-indigo-950/20 border border-[var(--color-primary)]/20 text-xs font-semibold text-[var(--color-primary)] text-center"
              >
                ✓ Active Workspace
              </span>
              <Link
                :href="`/workspaces/${ws.slug}/settings/`"
                class="px-3 py-2 rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)] text-xs font-semibold text-[var(--color-text)] hover:bg-[var(--color-surface-muted)] transition-all text-center flex items-center justify-center"
              >
                ⚙ Settings
              </Link>
            </div>
          </div>
        </div>
      </div>

      <!-- Archived/Deleted Workspaces (Soft Deleted) -->
      <div v-if="deleted_workspaces && deleted_workspaces.length > 0" class="space-y-4 pt-6 border-t border-[var(--color-border)]">
        <h2 class="text-lg font-bold text-red-600 dark:text-red-500">
          Archived Workspaces / مساحات العمل المؤرشفة ({{ deleted_workspaces.length }})
        </h2>
        <div class="grid gap-4 md:grid-cols-2">
          <div
            v-for="ws in deleted_workspaces"
            :key="ws.id"
            class="bg-[var(--color-surface)] border border-red-200 dark:border-red-950/40 rounded-2xl p-6 shadow-sm flex flex-col justify-between gap-4"
          >
            <div>
              <h3 class="font-bold text-base text-[var(--color-text)] truncate max-w-[200px]" :title="ws.name">
                {{ ws.name }}
              </h3>
              <p class="text-[10px] text-[var(--color-text-muted)] mt-1">
                Archived on / تمت الأرشفة في: {{ ws.deleted_at }}
              </p>
            </div>
            <div class="flex items-center gap-2 pt-4 border-t border-[var(--color-border)]/50">
              <button
                @click="restoreWorkspace(ws.id)"
                class="flex-1 px-3 py-2 rounded-lg bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-500/20 text-xs font-semibold text-emerald-600 dark:text-emerald-400 hover:bg-emerald-100 dark:hover:bg-emerald-950/30 transition-all cursor-pointer text-center"
              >
                Restore / استعادة
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Back to Profile Link -->
      <div class="flex justify-center pt-6">
        <Link
          href="/profile/"
          class="text-xs text-[var(--color-text-muted)] hover:text-[var(--color-primary)] transition-colors"
        >
          ← Back to Profile / الرجوع للحساب الشخصي
        </Link>
      </div>

      <!-- Create Modal -->
      <div
        v-if="isModalOpen"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
      >
        <div 
          class="w-full max-w-md bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl p-6 shadow-2xl relative space-y-4"
        >
          <div class="flex justify-between items-center border-b border-[var(--color-border)] pb-3">
            <h3 class="text-lg font-bold text-[var(--color-text)]">Create Workspace</h3>
            <button 
              @click="closeModal" 
              class="text-[var(--color-text-muted)] hover:text-[var(--color-text)] text-lg font-semibold cursor-pointer"
            >
              ✕
            </button>
          </div>

          <form @submit.prevent="createWorkspace" class="space-y-4">
            <div>
              <label for="modal-name" class="block text-xs font-semibold text-[var(--color-text)] mb-1">
                Workspace Name
              </label>
              <input
                id="modal-name"
                type="text"
                v-model="form.name"
                placeholder="e.g. Acme Corporation or مساحة تطوير"
                class="w-full rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-muted)] text-[var(--color-text)] px-4 py-2.5 text-sm outline-none transition-all focus:border-[var(--color-primary)] focus:ring-2 focus:ring-[var(--color-primary)]/20"
                required
              />
              <p class="text-[10px] text-[var(--color-text-muted)] mt-1.5">
                Note: A unique, URL-safe slug will be automatically generated.
              </p>
              <span v-if="form.errors.name" class="text-xs text-red-500 mt-1 block">
                {{ form.errors.name[0] }}
              </span>
            </div>

            <div class="flex justify-end gap-3 pt-3 border-t border-[var(--color-border)]">
              <button
                type="button"
                @click="closeModal"
                class="px-4 py-2 rounded-xl bg-[var(--color-surface-muted)] border border-[var(--color-border)] text-[var(--color-text)] text-xs font-medium hover:bg-[var(--color-surface)] transition-all cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="form.processing"
                class="px-4 py-2 rounded-xl bg-[var(--color-primary)] text-white text-xs font-semibold hover:bg-[var(--color-primary-hover)] disabled:opacity-50 transition-all cursor-pointer"
              >
                <span v-if="!form.processing">Create Workspace</span>
                <span v-else>Creating...</span>
              </button>
            </div>
          </form>
        </div>
      </div>

    </div>
  </div>
</template>
