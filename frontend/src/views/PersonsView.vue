<script setup lang="ts">
import { fetchPersons as fetchPersonsApi } from '../api/persons'
import type { Person } from '../types'
import PaginationControls from '../components/PaginationControls.vue'
import HoverListItem from '../components/HoverListItem.vue'
import SortSelect from '../components/SortSelect.vue'
import { useDocumentMeta } from '../composables/useDocumentTitle'
import { useListView } from '../composables/useListView'
import BaseSearchInput from '../components/BaseSearchInput.vue'

useDocumentMeta('人物列表', '')

const {
  items: persons,
  isLoading,
  hasError,
  searchQuery,
  ordering: sortBy,
  currentPage,
  totalPages,
  changePage,
  totalCount,
} = useListView<Person>(fetchPersonsApi, { defaultOrdering: 'name' })
</script>

<template>
  <div class="mx-auto max-w-4xl">
    <!-- ── Controls ── -->
    <div class="flex flex-col justify-between gap-4 pt-6 pb-8 md:flex-row md:items-center md:pt-10">
      <div class="w-full md:w-56">
        <BaseSearchInput
          v-model="searchQuery"
          placeholder="搜尋姓名、別名或簡介…"
          class="text-main placeholder:text-main/35 border-main/20 focus:border-main/50 focus-visible:outline-primary/50 w-full border-b bg-transparent py-1.5 pr-8 pl-6 text-sm transition-colors outline-none focus-visible:outline-2"
        />
      </div>
      <div class="relative w-28 shrink-0">
        <SortSelect
          v-model="sortBy"
          select-class="text-main/60 border-main/20 focus:border-main/50 w-28 cursor-pointer appearance-none border-b bg-transparent py-1.5 pr-6 pl-1 text-sm transition-colors outline-none focus-visible:outline-2 focus-visible:outline-primary/50"
          :options="[
            { value: 'name', label: '字母排序' },
            { value: '-updated_at', label: '最近更新' },
          ]"
        />
      </div>
    </div>

    <!-- ── Loading ── -->
    <div
      v-if="isLoading"
      class="text-main/50 animate-pulse py-16 text-center text-base font-medium"
    >
      正在讀取人物資料...
    </div>
    <div
      v-else-if="hasError"
      class="text-main/50 py-16 text-center text-base font-medium"
    >
      資料讀取發生問題，請稍後再試。
    </div>
    <div
      v-else-if="persons.length === 0"
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
      <span class="text-main/35 text-sm">找不到符合條件的人物。</span>
    </div>

    <!-- ── List ── -->
    <div
      v-else
      class="pb-20"
    >
      <!-- Count -->
      <p
        v-if="totalCount > 0"
        class="text-main/45 mb-1 text-sm tracking-wide"
      >
        共 {{ totalCount }} 位人物
      </p>

      <!-- Person Rows -->
      <HoverListItem
        v-for="person in persons"
        :key="person.id"
        :to="`/persons/${person.id}`"
        class="block cursor-pointer py-4"
      >
        <!-- Name row -->
        <div class="mb-1.5 flex flex-wrap items-baseline justify-between gap-3">
          <div class="flex flex-wrap items-baseline gap-2.5">
            <span class="text-main group-hover:text-primary text-xl font-medium transition-colors">
              {{ person.name }}
            </span>
            <span
              v-if="person.aliases && person.aliases.length > 0"
              class="text-main/40 text-base"
            >
              {{ person.aliases.map((a) => a.name).join(' · ') }}
            </span>
          </div>
        </div>

        <!-- Bio -->
        <p class="text-main/70 mb-3.5 line-clamp-2 text-base leading-relaxed">
          {{ person.about || '暫無簡歷提供。' }}
        </p>
      </HoverListItem>

      <!-- Pagination -->
      <PaginationControls
        v-if="totalPages > 1"
        :current-page="currentPage"
        :total-pages="totalPages"
        @change-page="changePage"
      />
    </div>
  </div>
</template>
