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
  <div class="mx-auto max-w-4xl px-5 pb-24 md:px-0">
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
      <div class="mb-10 pt-8 md:pt-12">
        <BackLink
          to="/"
          text="返回首頁"
        />
      </div>

      <article class="flex flex-col">
        <header class="border-main/10 mb-6 border-b pb-4">
          <h1 class="text-main text-3xl font-normal tracking-tight md:text-4xl">
            {{ pageData.title }}
          </h1>
        </header>

        <div
          class="text-main/70 max-w-none text-base leading-[1.8] tracking-wide whitespace-pre-wrap md:text-lg"
        >
          {{ pageData.body || '無內容' }}
        </div>

        <footer class="border-main/10 mt-20 flex justify-end border-t pt-8">
          <span class="text-main/45 text-sm tracking-wide">
            最後更新於 {{ formatDate(pageData.updated_at) }}
          </span>
        </footer>
      </article>
    </template>
  </div>
</template>
