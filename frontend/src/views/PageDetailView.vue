<script setup lang="ts">
import { formatDate } from '../utils/formatters'
import BackLink from '../components/BackLink.vue'
import { useDocumentMeta } from '../composables/useDocumentTitle'
import { fetchPageDetail } from '../api/pages'
import { useApiDetail } from '../composables/useApiDetail'

const {
  data: pageData,
  isLoading,
  hasError,
} = useApiDetail((params) => fetchPageDetail(params.slug as string))
useDocumentMeta(
  () => pageData.value?.title,
  () => pageData.value?.body?.slice(0, 160),
)
</script>

<template>
  <div class="mx-auto max-w-4xl space-y-4 pb-20">
    <div
      v-if="isLoading"
      class="text-main/50 animate-pulse py-16 text-center text-sm font-medium"
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
      <article class="pt-6 md:pt-10">
        <h1 class="text-main mb-6 text-2xl leading-snug font-normal md:text-3xl">
          {{ pageData.title }}
        </h1>

        <div class="border-main/10 mb-8 border-b"></div>

        <div class="text-main/80 max-w-none text-base leading-loose whitespace-pre-wrap lg:text-lg">
          {{ pageData.body || '無內容' }}
        </div>

        <div class="border-main/10 mt-16 flex items-center justify-between border-t pt-6">
          <BackLink
            to="/"
            text="返回首頁"
          />
          <span class="text-main/40 text-xs">最後更新於 {{ formatDate(pageData.updated_at) }}</span>
        </div>
      </article>
    </template>
  </div>
</template>
