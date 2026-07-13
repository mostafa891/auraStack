<script setup lang="ts">
import { Link } from '@inertiajs/vue3'
import AppHead from '../../components/AppHead.vue'

defineProps<{
  posts: Array<{
    id: string
    title: string
    slug: string
    summary: string
    published_at: string
  }>
}>()
</script>

<template>
  <AppHead 
    title="Blog & Product Updates" 
    description="Read latest announcements and guides about AuraStack SaaS Engine." 
  />

  <div class="min-h-screen bg-slate-950 text-slate-100 font-sans">
    <!-- Navbar -->
    <header class="border-b border-slate-900 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" class="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
          AuraStack
        </Link>
        <Link href="/auth/login/" class="text-sm font-medium text-slate-300 hover:text-slate-100">
          Sign In
        </Link>
      </div>
    </header>

    <main class="max-w-4xl mx-auto px-6 py-16">
      <div class="mb-12 border-b border-slate-900 pb-8">
        <h1 class="text-4xl font-extrabold mb-4 tracking-tight">Blog & Updates</h1>
        <p class="text-slate-400">Discover tips, tricks, and latest updates about building SaaS with Python and Django.</p>
      </div>

      <div v-if="posts.length === 0" class="text-center py-12 bg-slate-900/20 border border-slate-900 rounded-2xl">
        <p class="text-slate-400">No posts published yet. Stay tuned!</p>
      </div>

      <div v-else class="space-y-12">
        <article v-for="post in posts" :key="post.id" class="group border-b border-slate-900 pb-10">
          <span class="text-xs text-slate-500 font-semibold">{{ post.published_at }}</span>
          <h2 class="text-2xl font-bold mt-2 mb-3 group-hover:text-indigo-400 transition-colors">
            <Link :href="'/blog/' + post.slug + '/'">{{ post.title }}</Link>
          </h2>
          <p class="text-slate-400 text-sm leading-relaxed mb-4">{{ post.summary }}</p>
          <Link :href="'/blog/' + post.slug + '/'" class="text-sm font-medium text-indigo-400 hover:text-indigo-300 flex items-center space-x-1">
            <span>Read Article</span>
            <span>&rarr;</span>
          </Link>
        </article>
      </div>
    </main>
  </div>
</template>
