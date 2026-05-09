<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'

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
</script>

<template>
  <div class="max-w-4xl mx-auto pb-20">
    <div v-if="isLoading" class="py-16 text-center text-main/45 text-[13px] font-medium">
      正在讀取文章資料...
    </div>

    <template v-else-if="post">
      <!-- Back Link -->
      <div class="pt-10 mb-9">
        <router-link
          to="/posts"
          class="inline-flex items-center gap-1.5 text-[11px] font-medium tracking-[0.1em] uppercase text-main/40 hover:text-primary transition-colors group no-underline"
        >
          <svg width="13" height="13" viewBox="0 0 14 14" fill="none" class="transition-transform group-hover:-translate-x-0.5">
            <path d="M9 2L4 7L9 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          返回文章列表
        </router-link>
      </div>

      <article class="flex flex-col">
        <h1 class="text-[1.75rem] md:text-[2rem] font-normal leading-[1.3] text-main mb-4">{{ post.title }}</h1>

        <div class="text-[12.5px] text-main/50 flex items-center gap-2 mb-8">
          <span>{{ post.author_name || '管理員' }}</span>
          <span class="text-main/20">·</span>
          <time class="font-mono">{{ formatDate(post.created_at) }}</time>
        </div>

        <!-- content -->
        <div class="prose prose-stone max-w-none text-[14.5px] text-main/80 leading-relaxed whitespace-pre-wrap">{{ post.body || '無內容' }}</div>

        <div class="mt-16 pt-6 border-t border-main/[0.08] flex justify-end">
          <span class="text-[11px] font-mono text-main/35">最後更新於 {{ formatDate(post.updated_at) }}</span>
        </div>
      </article>
    </template>
  </div>
</template>
