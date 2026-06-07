<script setup lang="ts">
import { fetchPosts as fetchPostsApi } from '../api/posts'
import type { Post } from '../types'
import PaginationControls from '../components/PaginationControls.vue'
import HoverListItem from '../components/HoverListItem.vue'
import SortSelect from '../components/SortSelect.vue'
import { formatDate } from '../utils/formatters'
import { useDocumentMeta } from '../composables/useDocumentTitle'
import BaseSearchInput from '../components/BaseSearchInput.vue'
import { useListView } from '../composables/useListView'

useDocumentMeta('最新資訊', '')

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
      <div class="w-full md:w-56">
        <BaseSearchInput
          v-model="searchQuery"
          placeholder="搜尋標題、內容…"
          class="text-main placeholder:text-main/35 border-main/20 focus:border-main/50 focus-visible:outline-primary/50 w-full border-b bg-transparent py-1.5 pr-8 pl-6 text-sm transition-colors outline-none focus-visible:outline-2"
        />
      </div>
      <div class="relative w-28 shrink-0">
        <SortSelect
          v-model="ordering"
          select-class="text-main/60 border-main/20 focus:border-main/50 w-28 cursor-pointer appearance-none border-b bg-transparent py-1.5 pr-6 pl-1 text-sm transition-colors outline-none focus-visible:outline-2 focus-visible:outline-primary/50"
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
      class="flex flex-col items-center gap-2 py-16 text-center"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="1.2"
        stroke="currentColor"
        class="text-main/15 h-10 w-10"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          d="M3.75 9.776c.112-.017.227-.026.344-.026h15.812c.117 0 .232.009.344.026m-16.5 0a2.25 2.25 0 0 0-1.883 2.542l.857 6a2.25 2.25 0 0 0 2.227 1.932H19.05a2.25 2.25 0 0 0 2.227-1.932l.857-6a2.25 2.25 0 0 0-1.883-2.542m-16.5 0V6A2.25 2.25 0 0 1 6 3.75h3.879a1.5 1.5 0 0 1 1.06.44l2.122 2.12a1.5 1.5 0 0 0 1.06.44H18A2.25 2.25 0 0 1 20.25 9v.776"
        />
      </svg>
      <span class="text-main/35 text-sm">找不到符合條件的文章。</span>
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
