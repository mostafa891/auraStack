<script setup lang="ts">
import { Link } from '@inertiajs/vue3'
import AppHead from '../../components/AppHead.vue'

defineProps<{
  post: {
    title: string
    slug: string
    summary: string
    content: string
    published_at: string
  }
}>()
</script>

<template>
  <AppHead 
    :title="post.title" 
    :description="post.summary" 
  />

  <div class="min-h-screen bg-slate-950 text-slate-100 font-sans">
    <!-- Navbar -->
    <header class="border-b border-slate-900 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" class="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
          AuraStack
        </Link>
        <Link href="/blog/" class="text-sm font-medium text-slate-300 hover:text-slate-100">
          &larr; Back to Blog
        </Link>
      </div>
    </header>

    <main class="max-w-3xl mx-auto px-6 py-16">
      <article>
        <header class="mb-10 border-b border-slate-900 pb-8">
          <span class="text-xs text-slate-500 font-semibold">{{ post.published_at }}</span>
          <h1 class="text-4xl md:text-5xl font-extrabold mt-2 mb-4 tracking-tight leading-tight">
            {{ post.title }}
          </h1>
          <p class="text-slate-400 text-lg leading-relaxed">{{ post.summary }}</p>
        </header>

        <!-- Body content -->
        <div class="prose prose-invert max-w-none text-slate-300 leading-relaxed space-y-6">
          <p class="whitespace-pre-wrap">{{ post.content }}</p>
        </div>
      </article>
    </main>
  </div>
</template>
