<script setup lang="ts">
import { watchEffect } from "vue";
import { Link } from '@inertiajs/vue3'
import AppHead from '../../components/AppHead.vue'
import { useI18n } from "@/composables/useI18n";

interface Tag { name: string; slug: string }

defineProps<{
  post: {
    title: string; slug: string; summary: string; content: string;
    published_at: string; reading_time: number; cover_image: string | null;
    author: string | null; tags: Tag[]
  }
}>()

const { t, locale, toggleLocale } = useI18n();

// Dynamic update of HTML attributes for RTL/LTR and language code
watchEffect(() => {
  document.documentElement.dir = locale.value === "ar" ? "rtl" : "ltr";
  document.documentElement.lang = locale.value;
});

function parseMarkdown(md: string): string {
  if (!md) return "";

  // Safe HTML Escaping (excluding custom injected tags later)
  let html = md
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // Multi-line code block: ```lang\ncode\n```
  const codeBlocks: string[] = [];
  html = html.replace(/```([\s\S]*?)```/g, (_match, code) => {
    const lines = code.trim().split("\n");
    let codeContent = code.trim();
    if (lines.length > 0 && !lines[0].includes(" ") && lines[0].length < 15) {
      codeContent = lines.slice(1).join("\n");
    }
    const index = codeBlocks.length;
    codeBlocks.push(codeContent);
    return `\n\n___CODE_BLOCK_PLACEHOLDER_${index}___\n\n`;
  });

  const lines = html.split("\n");
  const result: string[] = [];
  let inList = false;

  for (let i = 0; i < lines.length; i++) {
    const rawLine = lines[i];
    const line = rawLine.trim();

    if (line.startsWith("___CODE_BLOCK_PLACEHOLDER_") && line.endsWith("___")) {
      if (inList) {
        result.push("</ul>");
        inList = false;
      }
      const indexStr = line.substring(26, line.length - 3);
      const index = parseInt(indexStr, 10);
      const code = codeBlocks[index] || "";
      result.push(`<pre class="bg-slate-900 border border-slate-800 p-4 rounded-xl overflow-x-auto my-6 text-sm font-mono text-indigo-300"><code>${code}</code></pre>`);
      continue;
    }

    if (line.startsWith("- ") || line.startsWith("* ") || line.startsWith("• ")) {
      if (!inList) {
        result.push('<ul class="list-disc pl-6 space-y-2 my-4 text-slate-300">');
        inList = true;
      }
      const content = inlineParser(line.substring(2));
      result.push(`<li>${content}</li>`);
      continue;
    }

    if (inList) {
      result.push("</ul>");
      inList = false;
    }

    if (line.startsWith("# ")) {
      result.push(`<h1 class="text-3xl font-extrabold text-white mt-8 mb-4 border-b border-slate-800/60 pb-2">${inlineParser(line.substring(2))}</h1>`);
    } else if (line.startsWith("## ")) {
      result.push(`<h2 class="text-2xl font-bold text-slate-100 mt-6 mb-3">${inlineParser(line.substring(3))}</h2>`);
    } else if (line.startsWith("### ")) {
      result.push(`<h3 class="text-xl font-bold text-slate-200 mt-5 mb-2">${inlineParser(line.substring(4))}</h3>`);
    } else if (line.startsWith("&gt; ") || line.startsWith("> ")) {
      const cleanLine = line.startsWith("&gt; ") ? line.substring(5) : line.substring(2);
      result.push(`<blockquote class="border-l-4 border-indigo-500 bg-slate-900/30 pl-4 py-2 my-6 text-slate-400 italic">${inlineParser(cleanLine)}</blockquote>`);
    } else if (line === "") {
      // empty lines
    } else {
      result.push(`<p class="leading-8 text-slate-300 text-base mb-4">${inlineParser(rawLine)}</p>`);
    }
  }

  if (inList) {
    result.push("</ul>");
  }

  return result.join("\n");
}

function inlineParser(text: string): string {
  let parsed = text;
  parsed = parsed.replace(/\*\*(.*?)\*\*/g, '<strong class="font-extrabold text-white">$1</strong>');
  parsed = parsed.replace(/__(.*?)__/g, '<strong class="font-extrabold text-white">$1</strong>');
  parsed = parsed.replace(/\*(.*?)\*/g, '<em class="italic text-slate-200">$1</em>');
  parsed = parsed.replace(/_(.*?)_/g, '<em class="italic text-slate-200">$1</em>');
  parsed = parsed.replace(/`(.*?)`/g, '<code class="bg-slate-900 px-1.5 py-0.5 rounded text-indigo-400 font-mono text-sm border border-slate-800">$1</code>');
  parsed = parsed.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" class="text-indigo-400 hover:text-indigo-300 hover:underline transition-colors font-medium" target="_blank" rel="noopener">$1</a>');
  return parsed;
}
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
        <div class="flex items-center gap-4">
          <!-- Language Switcher -->
          <button
            @click="toggleLocale"
            class="inline-flex items-center justify-center px-3 py-1.5 rounded-xl border border-slate-850 bg-slate-900/60 text-slate-200 text-xs font-semibold hover:bg-slate-800 transition-colors cursor-pointer select-none"
          >
            🌐 {{ locale === 'ar' ? 'English' : 'العربية' }}
          </button>
          
          <Link href="/blog/" class="text-sm font-medium text-slate-300 hover:text-indigo-400 transition-colors flex items-center gap-1">
            {{ t('blog.back_to_blog') }}
          </Link>
        </div>
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
            ⏱ {{ post.reading_time }} {{ t('blog.min_read') }}
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
        <div class="prose-content text-slate-300 leading-8 space-y-5 text-base" v-html="parseMarkdown(post.content)">
        </div>

        <!-- Footer nav -->
        <div class="mt-16 pt-8 border-t border-slate-800/60 flex items-center justify-between">
          <Link href="/blog/" class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-800/50 hover:bg-slate-800 border border-slate-700/60 hover:border-indigo-500/40 text-sm font-medium text-slate-300 hover:text-white transition-all">
            {{ t('blog.all_posts') }}
          </Link>
          <a
            :href="`https://twitter.com/intent/tweet?text=${encodeURIComponent(post.title)}`"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-800/50 hover:bg-slate-800 border border-slate-700/60 text-sm font-medium text-slate-300 hover:text-white transition-all"
          >{{ t('blog.share') }} →</a>
        </div>
      </article>
    </main>

    <footer class="border-t border-slate-800/60 mt-8 py-6 text-center text-sm text-slate-600">
      <p>{{ t('blog.built_with') }} AuraFlow · <Link href="/" class="hover:text-slate-400 transition-colors">{{ t('blog.back_to_app') }}</Link></p>
    </footer>
  </div>
</template>
