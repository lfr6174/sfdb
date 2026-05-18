<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'
import { formatDate } from '../utils/formatters'
import BackLink from '../components/BackLink.vue'

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
  <div class="mx-auto max-w-4xl space-y-4 pb-20">
    <div
      v-if="isLoading"
      class="text-main/50 py-16 text-center text-sm font-medium"
    >
      正在讀取頁面資料...
    </div>

    <div
      v-else-if="hasError"
      class="text-main/50 py-16 text-center text-sm font-medium"
    >
      找不到該頁面。
    </div>

    <template v-else-if="pageData">
      <article class="pt-10">
        <h1 class="text-main mb-6 text-3xl leading-snug font-normal md:text-4xl">
          {{ pageData.title }}
        </h1>

        <div class="border-main/10 mb-8 border-b"></div>

        <div
          class="prose prose-stone text-main/80 max-w-none text-base leading-loose whitespace-pre-wrap lg:text-lg"
        >
          {{ pageData.body || '無內容' }}
        </div>

        <div class="border-main/10 mt-16 flex items-center justify-between border-t pt-6">
          <BackLink
            to="/"
            text="返回首頁"
          />
          <span class="text-main/40 font-mono text-xs">
            最後更新於 {{ formatDate(pageData.updated_at) }}
          </span>
        </div>
      </article>
    </template>
  </div>
</template>
