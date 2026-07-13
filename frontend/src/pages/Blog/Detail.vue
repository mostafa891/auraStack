<script setup lang="ts">
import { Link } from '@inertiajs/vue3'
import AppHead from '../../components/AppHead.vue'

interface Tag { name: string; slug: string }

defineProps<{
  post: {
    title: string; slug: string; summary: string; content: string;
    published_at: string; reading_time: number; cover_image: string | null;
    author: string | null; tags: Tag[]
  }
}>()
</script>

<template>
  <AppHead :title="post.title" :description="post.summary" />

  <div class="min-h-screen bg-slate-950 text-slate-100 font-sans">
    <!-- Navbar -->
    <header class="border-b border-slate-800/60 bg-slate-950/90 backdrop-blur-xl sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" class="text-xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
          AuraFlow
        </Link>
        <Link href="/blog/" class="text-sm font-medium text-slate-300 hover:text-indigo-400 transition-colors flex items-center gap-1">
          ← Back to Blog
        </Link>
      </div>
    </header>

    <main class="max-w-3xl mx-auto px-6 py-16">
      <article>
        <!-- Tags -->
        <div v-if="post.tags.length" class="flex flex-wrap gap-2 mb-6">
          <Link
            v-for="tag in post.tags"
            :key="tag.slug"
            :href="`/blog/?tag=${tag.slug}`"
            class="px-3 py-1 text-xs font-semibold bg-indigo-500/10 text-indigo-400 rounded-full border border-indigo-500/20 hover:bg-indigo-500/20 transition-colors"
          >{{ tag.name }}</Link>
        </div>

        <!-- Title -->
        <h1 class="text-4xl md:text-5xl font-extrabold tracking-tight leading-tight mb-6 bg-gradient-to-br from-white to-slate-300 bg-clip-text text-transparent">
          {{ post.title }}
        </h1>

        <!-- Meta bar -->
        <div class="flex flex-wrap items-center gap-4 mb-8 pb-8 border-b border-slate-800/60 text-sm text-slate-400">
          <span v-if="post.author" class="flex items-center gap-2">
            <span class="w-7 h-7 rounded-full bg-indigo-600/30 flex items-center justify-center text-xs font-bold text-indigo-300">
              {{ post.author[0]?.toUpperCase() }}
            </span>
            {{ post.author }}
          </span>
          <span class="flex items-center gap-1.5">
            <span class="text-slate-600">·</span>
            {{ post.published_at }}
          </span>
          <span class="flex items-center gap-1.5">
            <span class="text-slate-600">·</span>
            ⏱ {{ post.reading_time }} min read
          </span>
        </div>

        <!-- Cover image -->
        <div v-if="post.cover_image" class="mb-10 rounded-2xl overflow-hidden aspect-video">
          <img :src="post.cover_image" :alt="post.title" class="w-full h-full object-cover" />
        </div>

        <!-- Summary -->
        <p v-if="post.summary" class="text-xl text-slate-300 leading-relaxed mb-10 font-light border-l-4 border-indigo-500/40 pl-5">
          {{ post.summary }}
        </p>

        <!-- Content -->
        <div class="prose-content text-slate-300 leading-8 space-y-5 text-base">
          <p
            v-for="(paragraph, index) in post.content.split('\n\n')"
            :key="index"
            class="whitespace-pre-wrap text-slate-300 leading-8"
          >{{ paragraph }}</p>
        </div>

        <!-- Footer nav -->
        <div class="mt-16 pt-8 border-t border-slate-800/60 flex items-center justify-between">
          <Link href="/blog/" class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-800/50 hover:bg-slate-800 border border-slate-700/60 hover:border-indigo-500/40 text-sm font-medium text-slate-300 hover:text-white transition-all">
            ← All Posts
          </Link>
          <a
            :href="`https://twitter.com/intent/tweet?text=${encodeURIComponent(post.title)}`"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-800/50 hover:bg-slate-800 border border-slate-700/60 text-sm font-medium text-slate-300 hover:text-white transition-all"
          >Share →</a>
        </div>
      </article>
    </main>

    <footer class="border-t border-slate-800/60 mt-8 py-6 text-center text-sm text-slate-600">
      <p>Built with AuraFlow · <Link href="/" class="hover:text-slate-400 transition-colors">Go to App</Link></p>
    </footer>
  </div>
</template>
