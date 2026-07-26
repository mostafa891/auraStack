<script setup lang="ts">
import { Head } from '@inertiajs/vue3'

defineProps<{
  title: string
  description?: string
  image?: string
}>()
</script>

<template>
  <Head>
    <title>{{ title }} | auraStack</title>
    <meta v-if="description" name="description" :content="description" />
    <meta property="og:title" :content="title + ' | auraStack'" />
    <meta v-if="description" property="og:description" :content="description" />
    <meta property="og:image" :content="image || '/static/dist/images/default-share.png'" />
    <meta name="twitter:card" content="summary_large_image" />
  </Head>
</template>
