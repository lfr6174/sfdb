<script setup lang="ts">
import { fetchPosts as fetchPostsApi } from '../api/posts'
import type { Post } from '../types'
import PaginationControls from '../components/PaginationControls.vue'
import HoverListItem from '../components/HoverListItem.vue'
import SortSelect from '../components/SortSelect.vue'
import { formatDate } from '../utils/formatters'
import { useDocumentTitle } from '../composables/useDocumentTitle'
import { useListView } from '../composables/useListView'

useDocumentTitle('最新資訊')

const {
  items: posts,
  isLoading,
  searchQuery,
  ordering,
  currentPage,
  totalPages,
  hasNext,
  hasPrev,
  changePage,
  totalCount: totalPosts,
} = useListView<Post>(fetchPostsApi, { defaultOrdering: '-created_at' })
</script>

<template>
  <div class="mx-auto max-w-4xl pb-20">
    <!-- ── Controls ── -->
    <div class="flex flex-col justify-between gap-4 pt-6 pb-8 md:flex-row md:items-center md:pt-10">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="搜尋標題、內容…"
        class="text-main placeholder:text-main/35 border-main/20 focus:border-main/50 w-full border-b bg-transparent px-0 py-1.5 text-sm transition-colors outline-none md:w-56"
      />
      <div class="relative w-28 shrink-0">
        <SortSelect
          v-model="ordering"
          select-class="text-main/60 border-main/20 focus:border-main/50 w-28 cursor-pointer appearance-none border-b bg-transparent py-1.5 pr-6 pl-1 text-sm transition-colors outline-none"
          :options="[
            { value: '-created_at', label: '最新發布' },
            { value: 'created_at', label: '最早發布' },
            { value: '-updated_at', label: '最近更新' },
            { value: 'updated_at', label: '最早更新' },
          ]"
        />
      </div>
    </div>

    <!-- ── List ── -->
    <div
      v-if="isLoading"
      class="text-main/50 animate-pulse py-16 text-center text-base font-medium"
    >
      正在讀取文章列表...
    </div>
    <div
      v-else-if="posts.length === 0"
      class="text-main/50 py-16 text-center text-base font-medium"
    >
      找不到符合條件的文章。
    </div>
    <div
      v-else
      class="flex flex-col"
    >
      <!-- Count -->
      <p
        v-if="totalPosts > 0"
        class="text-main/45 mb-1 text-sm tracking-wide"
      >
        共 {{ totalPosts }} 篇文章
      </p>

      <HoverListItem
        v-for="post in posts"
        :key="post.id"
        :to="`/posts/${post.id}`"
        class="flex flex-col gap-1 py-4 no-underline"
      >
        <span class="text-main/40 text-xs">
          {{ formatDate(post.created_at) }}
        </span>
        <span
          class="text-main group-hover:text-primary block text-lg font-medium transition-colors"
        >
          {{ post.title }}
        </span>
      </HoverListItem>

      <div class="mt-6">
        <!-- Pagination -->
        <PaginationControls
          v-if="posts.length > 0 && (hasPrev || hasNext)"
          :current-page="currentPage"
          :total-pages="totalPages"
          :has-prev="hasPrev"
          :has-next="hasNext"
          @change-page="changePage"
        />
      </div>
    </div>
  </div>
</template>
