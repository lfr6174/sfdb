<script setup lang="ts">
import { formatDate } from '../utils/formatters'
import BackLink from '../components/BackLink.vue'
import ListState from '../components/ListState.vue'
import { useDocumentMeta } from '../composables/useDocumentTitle'
import { fetchPostDetail } from '../api/posts'
import { useApiDetail } from '../composables/useApiDetail'

const {
  data: post,
  isLoading,
  hasError,
} = useApiDetail((params) => fetchPostDetail(params.id as string))
useDocumentMeta(
  () => post.value?.title,
  () => post.value?.body?.slice(0, 160),
)
</script>

<template>
  <div class="mx-auto max-w-4xl px-5 pb-20 md:px-0">
    <ListState
      :loading="isLoading"
      :error="hasError"
      size="sm"
      loading-text="正在讀取文章資料..."
    />

    <template v-if="post">
      <!-- Back Link -->
      <div class="mb-9 pt-8 md:pt-12">
        <BackLink
          to="/posts"
          text="返回文章列表"
        />
      </div>

      <article class="flex flex-col">
        <header class="border-main/10 mb-6 border-b pb-4">
          <h1 class="text-main mb-4 text-3xl font-medium tracking-tight md:text-4xl">
            {{ post.title }}
          </h1>

          <div class="text-main/45 flex items-center gap-3 text-sm font-medium tracking-wide">
            <span>{{ post.author_name || '管理員' }}</span>
            <span class="text-main/20">·</span>
            <time>{{ formatDate(post.created_at) }}</time>
          </div>
        </header>

        <!-- content -->
        <div
          class="text-main/70 max-w-none text-base leading-[1.8] tracking-wide whitespace-pre-wrap md:text-lg"
        >
          {{ post.body || '無內容' }}
        </div>

        <footer class="border-main/10 mt-20 flex justify-end border-t pt-8">
          <span class="text-main/45 text-sm tracking-wide">
            最後更新於 {{ formatDate(post.updated_at) }}
          </span>
        </footer>
      </article>
    </template>
  </div>
</template>
