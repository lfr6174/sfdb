<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'
import { marked } from 'marked'

const route = useRoute()
const post = ref<any>(null)
const isLoading = ref(true)

const fetchPostDetail = async () => {
  isLoading.value = true
  try {
    const response = await api.get(`/posts/${route.params.id}/`)
    post.value = response.data
  } catch (error) {
    console.error('Failed to fetch post details:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchPostDetail()
})

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return dateStr.split('T')[0].replace(/-/g, '/')
}

const renderedBody = computed(() => {
  if (!post.value?.body) return '無內容'
  return marked.parse(post.value.body)
})
</script>

<template>
  <div class="max-w-4xl mx-auto space-y-6 pb-12">
    <div v-if="isLoading" class="text-center py-16 text-[#2d2016]/50 font-medium bg-[#ffffff] rounded-lg border border-[#2d2016]/10">
      正在讀取文章資料...
    </div>

    <template v-else-if="post">
      <router-link to="/posts" class="inline-flex items-center text-sm font-medium text-[#2d2016]/50 hover:text-[#ae5630] transition-colors mb-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        返回文章列表
      </router-link>

      <article class="bg-[#ffffff] rounded-lg p-6 md:p-10 shadow-sm border border-[#2d2016]/10">
        <h1 class="text-3xl md:text-4xl font-bold text-[#2d2016] tracking-tight mb-4">{{ post.title }}</h1>

        <div class="text-[#2d2016]/70 text-base font-medium flex items-center gap-2">
          <span>{{ post.author_name || '管理員' }}</span>
          <span class="text-[#2d2016]/30">·</span>
          <time class="font-mono">{{ formatDate(post.created_at) }}</time>
        </div>

        <hr class="my-6 border-[#2d2016]/10" />

        <div class="prose prose-stone max-w-none text-[17px] text-[#2d2016]/80 leading-relaxed" v-html="renderedBody">
        </div>

        <div class="mt-12 pt-6 border-t border-[#2d2016]/5 text-right">
          <span class="text-sm font-mono text-[#2d2016]/40">最後更新於 {{ formatDate(post.updated_at) }}</span>
        </div>
      </article>
    </template>
  </div>
</template>
