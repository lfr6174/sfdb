<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import {
  fetchWorks as fetchWorksApi,
  fetchAllCatalogues as fetchAllCataloguesApi,
} from '../api/works'
import type { CatalogueOption } from '../api/works'
import { fetchAllConcepts as fetchAllConceptsApi } from '../api/concepts'
import type { Work, Concept } from '../types'
import PaginationControls from '../components/PaginationControls.vue'
import SortSelect from '../components/SortSelect.vue'
import FilterChip from '../components/FilterChip.vue'
import ConceptPickerModal from '../components/ConceptPickerModal.vue'
import ListState from '../components/ListState.vue'
import SkeletonList from '../components/SkeletonList.vue'
import BaseSearchInput from '../components/BaseSearchInput.vue'
import WorkFilterSidebar from '../components/WorkFilterSidebar.vue'
import WorkAdvancedSearch from '../components/WorkAdvancedSearch.vue'
import WorkListItem from '../components/WorkListItem.vue'
import { useListView } from '../composables/useListView'
import { useUrlFilters } from '../composables/useUrlFilters'
import { useDocumentMeta } from '../composables/useDocumentTitle'
import { GENRE_OPTIONS, LENGTH_OPTIONS } from '../utils/constants'

useDocumentMeta('作品列表', '')

// All filter state lives in the URL query (single source of truth): every
// value below is a writable computed that parses/patches the current URL,
// so shared links, refresh and back/forward all restore the same search.
const filters = useUrlFilters({
  search: { type: 'string', api: false }, // sent by useListView
  ordering: { type: 'string', default: '-updated_at', api: false },
  page: { type: 'number', default: 1, api: false },
  genre: { type: 'csv' },
  work_length: { type: 'csv' },
  provenance: { type: 'csv' },
  language: { type: 'csv' },
  concept: { type: 'csv', api: false }, // slugs; mapped to concepts_in ids below
  year_min: { type: 'number' },
  year_max: { type: 'number' },
  publication: { type: 'string' },
  publication_title: { type: 'string', api: false }, // display label only
  publication_series: { type: 'string' },
  publication_series_title: { type: 'string', api: false },
  publication_name: { type: 'string' },
  publisher: { type: 'string' },
  publisher_name: { type: 'string', api: false },
  catalogue: { type: 'string' },
})

const {
  genre: selectedGenres,
  work_length: selectedLengths,
  provenance: selectedProvenances,
  language: selectedLanguages,
  concept: selectedConceptSlugs,
  year_min: yearMin,
  year_max: yearMax,
  publication: selectedPublicationId,
  publication_title: selectedPublicationTitle,
  publication_series: selectedPublicationSeriesId,
  publication_series_title: selectedPublicationSeriesTitle,
  publication_name: selectedPublicationName,
  publisher: selectedPublisherId,
  publisher_name: selectedPublisherName,
  catalogue: selectedCatalogueTitle,
} = filters.values

const allConcepts = ref<Concept[]>([])
const allCatalogues = ref<CatalogueOption[]>([])
const isModalOpen = ref(false)
const isAdvancedMode = ref(false)

// The URL stores concept slugs; the UI needs full Concept objects. This is a
// derived join of URL state × loaded concepts, not a second copy of state.
const selectedConcepts = computed<Concept[]>({
  get: () =>
    selectedConceptSlugs.value
      .map((slug) => allConcepts.value.find((c) => c.slug === slug))
      .filter((c): c is Concept => !!c),
  set: (list) => {
    selectedConceptSlugs.value = list.map((c) => c.slug)
  },
})

// Active filters as API query params for the works endpoint.
const apiParams = computed(() => {
  const params: Record<string, string> = filters.toParams()
  if (selectedConcepts.value.length)
    params.concepts_in = selectedConcepts.value.map((c) => c.id).join(',')
  return params
})

const {
  items: works,
  isLoading,
  hasError,
  searchQuery,
  ordering,
  currentPage,
  totalPages,
  totalCount: totalWorks,
  changePage,
  triggerFetch,
} = useListView<Work>(fetchWorksApi, {
  searchQuery: filters.values.search,
  ordering: filters.values.ordering,
  currentPage: filters.values.page,
  extraParams: () => apiParams.value,
})

// Refetch (back to page 1) when a filter changes — including via back/forward,
// since apiParams derives from the URL. Search, ordering and page changes are
// already watched inside useListView.
watch(
  () => JSON.stringify(apiParams.value),
  () => triggerFetch(),
)

onMounted(async () => {
  await Promise.all([
    fetchAllConceptsApi()
      .then((res) => {
        allConcepts.value = res.data || []
      })
      .catch((err) => console.error('Failed to fetch concepts', err)),
    fetchAllCataloguesApi()
      .then((res) => {
        allCatalogues.value = res.data ?? []
      })
      .catch(() => {}),
  ])
})

// Catalogue grouped by type for <optgroup>
const cataloguesByType = computed(() => {
  const map = new Map<string, CatalogueOption[]>()
  for (const c of allCatalogues.value) {
    const group = map.get(c.catalogue_type_display) ?? []
    group.push(c)
    map.set(c.catalogue_type_display, group)
  }
  return map
})

// Featured concepts for the left panel
const leftPanelConcepts = computed(() => {
  const selectedIds = new Set(selectedConcepts.value.map((c) => c.id))
  return allConcepts.value
    .filter((c) => c.is_featured && !selectedIds.has(c.id))
    .sort((a, b) => (a.featured_order || 0) - (b.featured_order || 0))
})

// Methods
const toggleConcept = (concept: Concept) => {
  const current = selectedConcepts.value
  selectedConcepts.value = current.some((c) => c.id === concept.id)
    ? current.filter((c) => c.id !== concept.id)
    : [...current, concept]
}

const openModal = () => {
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
}

// Clearing URL params is enough; the refetch follows via the apiParams watcher.
const clearPublication = () =>
  filters.clear(
    'publication',
    'publication_title',
    'publication_series',
    'publication_series_title',
    'publication_name',
  )

const clearPublisher = () => filters.clear('publisher', 'publisher_name')

const clearAllFilters = () =>
  filters.clear(
    'search',
    'genre',
    'work_length',
    'provenance',
    'language',
    'concept',
    'year_min',
    'year_max',
    'publication',
    'publication_title',
    'publication_series',
    'publication_series_title',
    'publication_name',
    'publisher',
    'publisher_name',
    'catalogue',
  )

// The "作用中" chip row, derived from the same URL state the API params use.
const activeChips = computed(() => {
  const chips: { key: string; label: string; remove: () => void }[] = []

  if (selectedPublicationId.value)
    chips.push({
      key: 'publication',
      label: `出版物：${selectedPublicationTitle.value}`,
      remove: clearPublication,
    })
  if (selectedPublicationSeriesId.value)
    chips.push({
      key: 'publication_series',
      label: `出版物：${selectedPublicationSeriesTitle.value}`,
      remove: clearPublication,
    })
  if (selectedPublicationName.value)
    chips.push({
      key: 'publication_name',
      label: `出版物：${selectedPublicationName.value}`,
      remove: clearPublication,
    })
  if (selectedPublisherId.value)
    chips.push({
      key: 'publisher',
      label: `出版者：${selectedPublisherName.value}`,
      remove: clearPublisher,
    })
  if (selectedCatalogueTitle.value)
    chips.push({
      key: 'catalogue',
      label: `精選：${selectedCatalogueTitle.value}`,
      remove: () => filters.clear('catalogue'),
    })
  for (const value of selectedGenres.value)
    chips.push({
      key: `genre:${value}`,
      label: GENRE_OPTIONS.find((o) => o.value === value)?.label || '',
      remove: () => {
        selectedGenres.value = selectedGenres.value.filter((v) => v !== value)
      },
    })
  for (const value of selectedLengths.value)
    chips.push({
      key: `work_length:${value}`,
      label: LENGTH_OPTIONS.find((o) => o.value === value)?.label || '',
      remove: () => {
        selectedLengths.value = selectedLengths.value.filter((v) => v !== value)
      },
    })
  for (const concept of selectedConcepts.value)
    chips.push({
      key: `concept:${concept.slug}`,
      label: concept.name,
      remove: () => toggleConcept(concept),
    })
  if (yearMin.value || yearMax.value)
    chips.push({
      key: 'year',
      label: `${yearMin.value || '…'}–${yearMax.value || '…'}`,
      remove: () => filters.clear('year_min', 'year_max'),
    })

  return chips
})
</script>

<template>
  <div>
    <div class="mx-auto flex max-w-4xl flex-col gap-0 pb-20 lg:flex-row lg:items-start lg:gap-12">
      <!-- Left Sidebar (desktop filters) -->
      <WorkFilterSidebar
        v-model:search="searchQuery"
        v-model:advanced-mode="isAdvancedMode"
        v-model:genres="selectedGenres"
        v-model:lengths="selectedLengths"
        v-model:provenances="selectedProvenances"
        :selected-concepts="selectedConcepts"
        :featured-concepts="leftPanelConcepts"
        @toggle-concept="toggleConcept"
        @open-modal="openModal"
      />

      <!-- Main Panel -->
      <main class="min-w-0 flex-1 pt-6 md:pt-10">
        <!-- Search and Filter (Mobile) -->
        <div class="mb-6 flex items-center gap-3 lg:hidden">
          <div class="min-w-0 flex-1">
            <BaseSearchInput
              v-model="searchQuery"
              size="lg"
              placeholder="搜尋標題、作者…"
            />
          </div>
          <button
            :class="
              isAdvancedMode
                ? 'border-primary/60 text-primary bg-primary/5'
                : 'border-main/20 text-main'
            "
            class="hover:border-primary/50 flex h-10 w-10 shrink-0 items-center justify-center rounded border bg-transparent transition-colors"
            title="進階搜尋"
            aria-label="進階搜尋"
            :aria-pressed="isAdvancedMode"
            @click="isAdvancedMode = !isAdvancedMode"
          >
            <svg
              aria-hidden="true"
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>
            </svg>
          </button>
        </div>

        <!-- Advanced Search -->
        <WorkAdvancedSearch
          v-if="isAdvancedMode"
          v-model:search="searchQuery"
          v-model:advanced-mode="isAdvancedMode"
          v-model:year-min="yearMin"
          v-model:year-max="yearMax"
          v-model:genres="selectedGenres"
          v-model:lengths="selectedLengths"
          v-model:provenances="selectedProvenances"
          v-model:languages="selectedLanguages"
          v-model:catalogue-title="selectedCatalogueTitle"
          :catalogues-by-type="cataloguesByType"
          :selected-concepts="selectedConcepts"
          :total-works="totalWorks"
          @toggle-concept="toggleConcept"
          @open-modal="openModal"
          @clear-all="clearAllFilters"
        />

        <!-- Results View -->
        <template v-else>
          <!-- Active Filters + Sort Bar -->
          <div class="border-main/10 mb-1 flex flex-col gap-3 border-b pb-5">
            <!-- Active filter chips -->
            <div
              v-if="activeChips.length"
              class="flex flex-wrap items-center gap-1.5"
            >
              <span class="text-main/40 mr-1 shrink-0 text-xs">作用中：</span>

              <FilterChip
                v-for="chip in activeChips"
                :key="chip.key"
                :label="chip.label"
                @remove="chip.remove()"
              />

              <button
                class="text-main/40 hover:text-primary ml-auto text-xs transition-colors"
                @click="clearAllFilters"
              >
                清除全部
              </button>
            </div>

            <!-- Count + Sort -->
            <div class="flex flex-wrap items-center justify-between gap-4">
              <span class="text-main/50 text-sm">
                共
                <span class="text-primary">{{ totalWorks }}</span>
                部作品
              </span>

              <div class="flex items-center gap-2">
                <SortSelect
                  v-model="ordering"
                  select-class="text-main/70 border-main/20 focus:border-primary/50 cursor-pointer appearance-none border-b bg-transparent py-1 pr-6 pl-0 text-sm transition-colors outline-none focus-visible:outline-2 focus-visible:outline-primary/50"
                  :options="[
                    { value: '-ori_date', label: '日期（新到舊）' },
                    { value: 'ori_date', label: '日期（舊到新）' },
                    { value: 'title', label: '標題' },
                    { value: '-updated_at', label: '最近更新' },
                  ]"
                />
              </div>
            </div>
          </div>

          <!-- Works List (loading / error / empty / results) -->
          <ListState
            :loading="isLoading"
            :error="hasError"
            :empty="works.length === 0"
            empty-text="找不到符合條件的作品。"
          >
            <template #loading>
              <SkeletonList />
            </template>
            <div class="flex flex-col">
              <WorkListItem
                v-for="work in works"
                :key="work.id"
                :work="work"
              />
            </div>

            <PaginationControls
              v-if="totalPages > 1"
              :current-page="currentPage"
              :total-pages="totalPages"
              @change-page="changePage"
            />
          </ListState>
        </template>
      </main>
    </div>

    <!-- Concept Modal -->
    <ConceptPickerModal
      v-model="selectedConcepts"
      :all-concepts="allConcepts"
      :open="isModalOpen"
      @close="closeModal"
    />
  </div>
</template>
