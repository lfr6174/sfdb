<script setup lang="ts">
import { fetchPersons as fetchPersonsApi } from '../api/persons'
import type { Person } from '../types'
import PaginationControls from '../components/PaginationControls.vue'
import HoverListItem from '../components/HoverListItem.vue'
import ListState from '../components/ListState.vue'
import SkeletonList from '../components/SkeletonList.vue'
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

    <!-- ── Loading / Error / Empty / List ── -->
    <ListState
      :loading="isLoading"
      :error="hasError"
      :empty="persons.length === 0"
      empty-text="找不到符合條件的人物。"
    >
      <template #loading>
        <SkeletonList />
      </template>
      <div class="pb-20">
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
              <span
                class="text-main group-hover:text-primary text-xl font-medium transition-colors"
              >
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
    </ListState>
  </div>
</template>
