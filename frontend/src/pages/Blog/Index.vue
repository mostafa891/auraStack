<script setup lang="ts">
import { watchEffect } from "vue";
import { Link, router } from '@inertiajs/vue3'
import AppHead from '../../components/AppHead.vue'
import { useI18n } from "@/composables/useI18n";

interface Tag { name: string; slug: string }
interface Post {
  id: string; title: string; slug: string; summary: string;
  published_at: string; reading_time: number; cover_image: string | null;
  author: string | null; tags: Tag[]
}

const props = defineProps<{
  posts: Post[]
  tags: Tag[]
  current_tag: string
  has_next: boolean
  has_previous: boolean
  current_page: number
  total_pages: number
}>()

const { t, locale, toggleLocale } = useI18n();

// Dynamic update of HTML attributes for RTL/LTR and language code
watchEffect(() => {
  document.documentElement.dir = locale.value === "ar" ? "rtl" : "ltr";
  document.documentElement.lang = locale.value;
});

function filterByTag(slug: string) {
  const tag = props.current_tag === slug ? '' : slug
  router.get('/blog/', tag ? { tag } : {}, { preserveState: true })
}
function goToPage(page: number) {
  const params: Record<string, any> = { page }
  if (props.current_tag) params.tag = props.current_tag
  router.get('/blog/', params, { preserveState: true })
}
</script>

<template>
  <AppHead
    :title="t('blog.title')"
    :description="t('blog.subtitle')"
  />

  <div class="min-h-screen bg-slate-950 text-slate-100 font-sans">
    <!-- Navbar -->
    <header class="border-b border-slate-800/60 bg-slate-950/90 backdrop-blur-xl sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" class="text-xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
          AuraFlow
        </Link>
        <div class="flex items-center gap-6">
          <Link href="/blog/" class="text-sm text-indigo-400 font-semibold">{{ locale === 'ar' ? 'المدونة' : 'Blog' }}</Link>
          
          <!-- Language Switcher -->
          <button
            @click="toggleLocale"
            class="inline-flex items-center justify-center px-3 py-1.5 rounded-xl border border-slate-850 bg-slate-900/60 text-slate-200 text-xs font-semibold hover:bg-slate-800 transition-colors cursor-pointer select-none"
          >
            🌐 {{ locale === 'ar' ? 'English' : 'العربية' }}
          </button>
          
          <Link href="/auth/login/" class="text-sm font-medium text-slate-300 hover:text-white transition-colors">
            {{ t('blog.sign_in') }}
          </Link>
        </div>
      </div>
    </header>

    <main class="max-w-6xl mx-auto px-6 py-16">
      <!-- Hero -->
      <div class="mb-14 text-center">
        <span class="inline-block px-3 py-1 text-xs font-semibold tracking-widest text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 rounded-full mb-4 uppercase">
          {{ t('blog.journal') }}
        </span>
        <h1 class="text-5xl font-extrabold tracking-tight mb-4 bg-gradient-to-br from-white to-slate-400 bg-clip-text text-transparent">
          {{ t('blog.title') }}
        </h1>
        <p class="text-slate-400 text-lg max-w-2xl mx-auto">
          {{ t('blog.subtitle') }}
        </p>
      </div>

      <!-- Tags filter -->
      <div v-if="tags.length" class="flex flex-wrap gap-2 mb-10 justify-center">
        <button
          @click="filterByTag('')"
          :class="[
            'px-4 py-1.5 rounded-full text-sm font-medium transition-all border',
            !current_tag
              ? 'bg-indigo-600 border-indigo-600 text-white'
              : 'border-slate-700 text-slate-400 hover:border-slate-500 hover:text-slate-200'
          ]"
        >{{ t('blog.all_tags') }}</button>
        <button
          v-for="tag in tags"
          :key="tag.slug"
          @click="filterByTag(tag.slug)"
          :class="[
            'px-4 py-1.5 rounded-full text-sm font-medium transition-all border',
            current_tag === tag.slug
              ? 'bg-indigo-600 border-indigo-600 text-white'
              : 'border-slate-700 text-slate-400 hover:border-slate-500 hover:text-slate-200'
          ]"
        >{{ tag.name }}</button>
      </div>

      <!-- Empty state -->
      <div v-if="posts.length === 0" class="text-center py-20">
        <div class="w-16 h-16 mx-auto mb-4 rounded-2xl bg-slate-800/60 flex items-center justify-center text-3xl">📝</div>
        <p class="text-slate-400 text-lg">
          {{ current_tag ? t('blog.no_posts_tag') : t('blog.no_posts') }}
        </p>
      </div>

      <!-- Posts grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
        <article
          v-for="post in posts"
          :key="post.id"
          class="group bg-slate-900/50 border border-slate-800/60 rounded-2xl overflow-hidden hover:border-indigo-500/40 hover:shadow-lg hover:shadow-indigo-500/5 transition-all duration-300"
        >
          <!-- Cover image -->
          <div class="aspect-video bg-gradient-to-br from-indigo-900/40 to-purple-900/30 overflow-hidden">
            <img
              v-if="post.cover_image"
              :src="post.cover_image"
              :alt="post.title"
              class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            />
            <div v-else class="w-full h-full flex items-center justify-center">
              <span class="text-4xl opacity-30">✍️</span>
            </div>
          </div>

          <div class="p-6">
            <!-- Tags -->
            <div v-if="post.tags.length" class="flex flex-wrap gap-1.5 mb-3">
              <span
                v-for="tag in post.tags"
                :key="tag.slug"
                class="px-2 py-0.5 text-xs font-medium bg-indigo-500/10 text-indigo-400 rounded-md border border-indigo-500/20"
              >{{ tag.name }}</span>
            </div>

            <!-- Title -->
            <h2 class="text-lg font-bold mb-2 leading-snug group-hover:text-indigo-300 transition-colors">
              <Link :href="`/blog/${post.slug}/`">{{ post.title }}</Link>
            </h2>

            <!-- Summary -->
            <p class="text-slate-400 text-sm leading-relaxed mb-4 line-clamp-3">{{ post.summary }}</p>

            <!-- Meta -->
            <div class="flex items-center justify-between text-xs text-slate-500">
              <span>{{ post.published_at }}</span>
              <div class="flex items-center gap-3">
                <span v-if="post.author" class="text-slate-500">{{ post.author }}</span>
                <span class="flex items-center gap-1">⏱ {{ post.reading_time }} {{ t('blog.min_read') }}</span>
              </div>
            </div>
          </div>
        </article>
      </div>

      <!-- Pagination -->
      <div v-if="total_pages > 1" class="flex items-center justify-center gap-3">
        <button
          @click="goToPage(current_page - 1)"
          :disabled="!has_previous"
          class="px-4 py-2 rounded-lg border border-slate-700 text-sm font-medium text-slate-300 hover:border-indigo-500 hover:text-white transition-all disabled:opacity-30 disabled:cursor-not-allowed"
        >
          {{ locale === 'ar' ? '← السابق' : '← Previous' }}
        </button>
        <span class="text-sm text-slate-500">
          {{ locale === 'ar' ? `صفحة ${current_page} من ${total_pages}` : `Page ${current_page} of ${total_pages}` }}
        </span>
        <button
          @click="goToPage(current_page + 1)"
          :disabled="!has_next"
          class="px-4 py-2 rounded-lg border border-slate-700 text-sm font-medium text-slate-300 hover:border-indigo-500 hover:text-white transition-all disabled:opacity-30 disabled:cursor-not-allowed"
        >
          {{ locale === 'ar' ? 'التالي →' : 'Next →' }}
        </button>
      </div>
    </main>

    <!-- Footer -->
    <footer class="border-t border-slate-800/60 mt-16 py-8 text-center text-sm text-slate-600">
      <p>{{ t('blog.built_with') }} AuraFlow · <Link href="/" class="hover:text-slate-400 transition-colors">{{ t('blog.back_to_app') }}</Link></p>
    </footer>
  </div>
</template>
