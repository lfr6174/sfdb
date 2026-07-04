<script setup lang="ts">
import { fetchPosts as fetchPostsApi } from '../api/posts'
import type { Post } from '../types'
import PaginationControls from '../components/PaginationControls.vue'
import HoverListItem from '../components/HoverListItem.vue'
import ListState from '../components/ListState.vue'
import SkeletonList from '../components/SkeletonList.vue'
import SortSelect from '../components/SortSelect.vue'
import { formatDate } from '../utils/formatters'
import { useDocumentMeta } from '../composables/useDocumentTitle'
import BaseSearchInput from '../components/BaseSearchInput.vue'
import { useListView } from '../composables/useListView'
import { useUrlFilters } from '../composables/useUrlFilters'

useDocumentMeta('最新資訊', '')

// List state lives in the URL query (like WorksView), so back/forward and
// refresh restore the same page, search and ordering.
const filters = useUrlFilters({
  search: { type: 'string', api: false }, // sent by useListView
  ordering: { type: 'string', default: '-created_at', api: false },
  page: { type: 'number', default: 1, api: false },
})

const {
  items: posts,
  isLoading,
  hasError,
  searchQuery,
  ordering,
  currentPage,
  totalPages,
  changePage,
  totalCount: totalPosts,
} = useListView<Post>(fetchPostsApi, {
  searchQuery: filters.values.search,
  ordering: filters.values.ordering,
  currentPage: filters.values.page,
})
</script>

<template>
  <div class="mx-auto max-w-4xl pb-20">
    <!-- Controls -->
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

    <!-- Loading / Error / Empty / List -->
    <ListState
      :loading="isLoading"
      :error="hasError"
      :empty="posts.length === 0"
      empty-text="找不到符合條件的文章。"
    >
      <template #loading>
        <SkeletonList />
      </template>
      <div class="flex flex-col">
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
            v-if="totalPages > 1"
            :current-page="currentPage"
            :total-pages="totalPages"
            @change-page="changePage"
          />
        </div>
      </div>
    </ListState>
  </div>
</template>
