<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'
import { marked } from 'marked'

const route = useRoute()
const pageData = ref<any>(null)
const isLoading = ref(true)
const hasError = ref(false)

const fetchPageDetail = async () => {
  isLoading.value = true
  hasError.value = false
  try {
    // 透過 URL 的 slug 去打 API，例如 /api/pages/about/
    const response = await api.get(`/pages/${route.params.slug}/`)
    pageData.value = response.data
  } catch (error) {
    console.error('Failed to fetch page details:', error)
    hasError.value = true
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchPageDetail()
})

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return dateStr.split('T')[0].replace(/-/g, '/')
}

const renderedBody = computed(() => {
  if (!pageData.value?.body) return '無內容'
  return marked.parse(pageData.value.body)
})
</script>

<template>
  <div class="max-w-4xl mx-auto space-y-6 pb-12">
    <div v-if="isLoading" class="text-center py-16 text-[#2d2016]/50 font-medium bg-[#ffffff] rounded-lg border border-[#2d2016]/10">
      正在讀取頁面資料...
    </div>

    <div v-else-if="hasError" class="text-center py-16 text-[#2d2016]/50 font-medium bg-[#ffffff] rounded-lg border border-[#2d2016]/10">
      找不到該頁面。
    </div>

    <template v-else-if="pageData">
      <article class="bg-[#ffffff] rounded-lg p-6 md:p-10 shadow-sm border border-[#2d2016]/10">
        <h1 class="text-3xl md:text-4xl font-bold text-[#2d2016] tracking-tight mb-4">{{ pageData.title }}</h1>

        <!-- 不像文章有作者，靜態頁面直接放分隔線即可 -->
        <hr class="my-6 border-[#2d2016]/10" />

        <!-- Markdown 內文區塊 -->
        <div class="prose prose-stone max-w-none text-[17px] text-[#2d2016]/80 leading-relaxed" v-html="renderedBody">
        </div>

        <div class="mt-12 pt-6 border-t border-[#2d2016]/5 text-right flex justify-between items-center">
          <router-link to="/" class="text-sm font-medium text-[#2d2016]/50 hover:text-[#ae5630] transition-colors">
            ← 返回首頁
          </router-link>
          <span class="text-sm font-mono text-[#2d2016]/40">最後更新於 {{ formatDate(pageData.updated_at) }}</span>
        </div>
      </article>
    </template>
  </div>
</template>
