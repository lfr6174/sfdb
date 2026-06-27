<script setup lang="ts">
import { formatDate } from '../utils/formatters'
import BackLink from '../components/BackLink.vue'
import ListState from '../components/ListState.vue'
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
  <div class="mx-auto max-w-4xl px-5 pb-20 md:px-0">
    <ListState
      :loading="isLoading"
      :error="hasError"
      size="sm"
      loading-text="正在讀取頁面資料..."
      error-text="找不到該頁面。"
    />

    <template v-if="pageData">
      <div class="mb-9 pt-8 md:pt-12">
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
