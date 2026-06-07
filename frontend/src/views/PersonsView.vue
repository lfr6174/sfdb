<script setup lang="ts">
import { fetchPersons as fetchPersonsApi } from '../api/persons'
import type { Person } from '../types'
import PaginationControls from '../components/PaginationControls.vue'
import HoverListItem from '../components/HoverListItem.vue'
import SortSelect from '../components/SortSelect.vue'
import { useDocumentTitle } from '../composables/useDocumentTitle'
import { useListView } from '../composables/useListView'

useDocumentTitle('人物列表')

const {
  items: persons,
  isLoading,
  searchQuery,
  ordering: sortBy,
  currentPage,
  totalPages,
  hasNext,
  hasPrev,
  changePage,
  totalCount,
} = useListView<Person>(fetchPersonsApi, { defaultOrdering: 'name' })
</script>

<template>
  <div class="mx-auto max-w-4xl">
    <!-- ── Controls ── -->
    <div class="flex flex-col justify-between gap-4 pt-6 pb-8 md:flex-row md:items-center md:pt-10">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="搜尋姓名、別名或簡介…"
        class="text-main placeholder:text-main/35 border-main/20 focus:border-main/50 w-full border-b bg-transparent px-0 py-1.5 text-sm transition-colors outline-none md:w-56"
      />
      <div class="relative w-28 shrink-0">
        <SortSelect
          v-model="sortBy"
          select-class="text-main/60 border-main/20 focus:border-main/50 w-28 cursor-pointer appearance-none border-b bg-transparent py-1.5 pr-6 pl-1 text-sm transition-colors outline-none"
          :options="[
            { value: 'name', label: '字母排序' },
            { value: '-updated_at', label: '最近更新' },
          ]"
        />
      </div>
    </div>

    <!-- ── Loading ── -->
    <div
      v-if="isLoading && persons.length === 0"
      class="text-main/50 py-16 text-center text-base font-medium"
    >
      正在讀取人物列表...
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
          {{ person.excerpt || person.about || '暫無簡歷提供。' }}
        </p>
      </HoverListItem>

      <!-- Pagination -->
      <PaginationControls
        v-if="totalPages > 1"
        :current-page="currentPage"
        :total-pages="totalPages"
        :has-prev="hasPrev"
        :has-next="hasNext"
        @change-page="changePage"
      />
    </div>
  </div>
</template>
