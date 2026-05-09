<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'
import { formatDate } from '../utils/formatters'

const route = useRoute()
const pageData = ref<any>(null)
const isLoading = ref(true)
const hasError = ref(false)

const fetchPageDetail = async () => {
  isLoading.value = true
  hasError.value = false
  try {
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
</script>

<template>
  <div class="max-w-4xl mx-auto space-y-4 pb-20">
    <div v-if="isLoading" class="text-center py-16 text-main/50 text-[13px] font-medium">
      正在讀取頁面資料...
    </div>

    <div v-else-if="hasError" class="text-center py-16 text-main/50 text-[13px] font-medium">
      找不到該頁面。
    </div>

    <template v-else-if="pageData">
      <article class="pt-10">
        <h1 class="text-[1.75rem] md:text-[2rem] font-normal leading-[1.3] text-main mb-6">{{ pageData.title }}</h1>

        <div class="mb-8 border-b border-main/[0.08]"></div>

        <div class="prose prose-stone max-w-none text-[14.5px] text-main/80 leading-relaxed whitespace-pre-wrap">{{ pageData.body || '無內容' }}</div>

        <div class="mt-16 pt-6 border-t border-main/[0.08] flex justify-between items-center">
          <router-link
            to="/"
            class="inline-flex items-center gap-1.5 text-[11px] font-medium tracking-[0.1em] uppercase text-main/40 hover:text-primary transition-colors group no-underline"
          >
            <svg width="13" height="13" viewBox="0 0 14 14" fill="none" class="transition-transform group-hover:-translate-x-0.5">
              <path d="M9 2L4 7L9 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            ← 返回首頁
          </router-link>
          <span class="font-mono text-[11px] text-main/35">最後更新於 {{ formatDate(pageData.updated_at) }}</span>
        </div>
      </article>
    </template>
  </div>
</template>
