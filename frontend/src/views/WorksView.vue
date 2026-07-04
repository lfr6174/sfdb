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
import HoverListItem from '../components/HoverListItem.vue'
import SortSelect from '../components/SortSelect.vue'
import ConceptTag from '../components/ConceptTag.vue'
import SectionTitle from '../components/SectionTitle.vue'
import FilterChip from '../components/FilterChip.vue'
import ConceptPickerModal from '../components/ConceptPickerModal.vue'
import CheckboxGroup from '../components/CheckboxGroup.vue'
import CustomCheckbox from '../components/CustomCheckbox.vue'
import ListState from '../components/ListState.vue'
import SkeletonList from '../components/SkeletonList.vue'
import BaseSearchInput from '../components/BaseSearchInput.vue'
import FormRow from '../components/FormRow.vue'
import AgentInline from '../components/AgentInline.vue'
import { useListView } from '../composables/useListView'
import { useUrlFilters } from '../composables/useUrlFilters'
import { useDocumentMeta } from '../composables/useDocumentTitle'

useDocumentMeta('作品列表', '')

// Filter Constants
const GENRE_OPTIONS = [
  { value: 'novel', label: '小說' },
  { value: 'poem', label: '詩' },
  { value: 'comic', label: '漫畫' },
]
const LENGTH_OPTIONS = [
  { value: 'long', label: '長篇' },
  { value: 'short', label: '中短篇' },
]
const PROVENANCE_OPTIONS = [
  { value: 'original', label: '原創' },
  { value: 'licensed', label: '代理' },
]
const LANGUAGE_OPTIONS = [
  { value: 'zh-hant', label: '繁體中文' },
  { value: 'zh-hans', label: '簡體中文' },
  { value: 'en', label: '英文' },
  { value: 'ja', label: '日文' },
  { value: 'other', label: '其他' },
]

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
      <!-- Left Sidebar -->
      <aside
        class="lg:border-main/10 hidden shrink-0 pt-6 md:pt-10 lg:block lg:w-56 lg:border-r lg:pr-8 lg:pb-20"
      >
        <!-- Search (Desktop) -->
        <div class="mb-7 hidden lg:block">
          <BaseSearchInput
            v-model="searchQuery"
            size="lg"
            placeholder="搜尋標題、作者…"
          />
          <div class="mt-2 flex justify-start">
            <button
              class="text-main/50 hover:text-primary decoration-main/20 hover:decoration-primary/50 text-sm font-medium tracking-wide underline underline-offset-4 transition-colors"
              @click="isAdvancedMode = !isAdvancedMode"
            >
              {{ isAdvancedMode ? '返回一般結果' : '進階搜索' }}
            </button>
          </div>
        </div>

        <!-- Genre Type -->
        <div class="mb-6">
          <SectionTitle class="mb-3">作品體裁</SectionTitle>
          <CheckboxGroup
            v-model="selectedGenres"
            :options="GENRE_OPTIONS"
          />
        </div>

        <!-- Work Length -->
        <div class="mb-6">
          <SectionTitle class="mb-3">作品篇幅</SectionTitle>
          <CheckboxGroup
            v-model="selectedLengths"
            :options="LENGTH_OPTIONS"
          />
        </div>

        <!-- Provenance -->
        <div class="mb-6">
          <SectionTitle class="mb-3">作品來源</SectionTitle>
          <CheckboxGroup
            v-model="selectedProvenances"
            :options="PROVENANCE_OPTIONS"
          />
        </div>

        <!-- Concept Tags -->
        <div>
          <SectionTitle class="mb-3">概念標籤</SectionTitle>

          <!-- Selected tags -->
          <div
            v-if="selectedConcepts.length > 0"
            class="mb-4"
          >
            <div class="flex flex-col gap-2">
              <label
                v-for="concept in selectedConcepts"
                :key="concept.id"
                class="group flex cursor-pointer items-center gap-2"
              >
                <CustomCheckbox
                  name="selected-concept"
                  :checked="true"
                  @change="toggleConcept(concept)"
                />
                <span class="text-primary text-sm font-medium">{{ concept.name }}</span>
              </label>
            </div>
            <div class="border-main/10 mt-3 mb-3 border-t"></div>
          </div>

          <!-- Featured concepts -->
          <div class="space-y-4">
            <div class="flex flex-col gap-2">
              <label
                v-for="concept in leftPanelConcepts"
                :key="concept.id"
                class="group flex cursor-pointer items-center gap-2"
              >
                <CustomCheckbox
                  name="featured-concept"
                  :checked="false"
                  @change="toggleConcept(concept)"
                />
                <span class="text-main/60 group-hover:text-primary text-sm transition-colors">
                  {{ concept.name }}
                </span>
              </label>
            </div>
          </div>

          <button
            class="text-main/70 hover:text-primary decoration-main/20 hover:decoration-primary/50 mt-5 w-full text-left text-sm underline underline-offset-4 transition-colors"
            @click="openModal"
          >
            展開所有標籤
          </button>
        </div>
      </aside>

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
        <section
          v-if="isAdvancedMode"
          class="border-main/10 mb-8 border-b pb-10"
        >
          <SectionTitle class="mb-4">
            進階搜尋
            <template #action>
              <button
                class="text-main/50 border-main/10 hover:text-primary hover:border-primary/30 border px-3 py-1 text-xs transition-colors"
                @click="isAdvancedMode = false"
              >
                返回結果列表
              </button>
            </template>
          </SectionTitle>

          <!-- Definition-list style form: each row = label (left) + content (right) -->
          <dl class="divide-main/10 divide-y">
            <FormRow label="關鍵字">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="標題、作者、筆名等"
                class="text-main placeholder:text-main/30 border-main/20 focus:border-primary/50 w-full border-b bg-transparent pb-2 text-base transition-colors outline-none"
              />
            </FormRow>

            <FormRow label="發表年份">
              <div
                class="search-input border-main/20 focus-within:border-primary/50 inline-flex items-center border-b transition-colors"
              >
                <input
                  v-model="yearMin"
                  type="number"
                  placeholder="YYYY"
                  class="text-main placeholder:text-main/30 w-20 bg-transparent py-2 text-center font-mono text-base outline-none"
                />
                <span class="text-main/30 px-3 font-mono">—</span>
                <input
                  v-model="yearMax"
                  type="number"
                  placeholder="YYYY"
                  class="text-main placeholder:text-main/30 w-20 bg-transparent py-2 text-center font-mono text-base outline-none"
                />
              </div>
            </FormRow>

            <FormRow label="作品體裁">
              <CheckboxGroup
                v-model="selectedGenres"
                :options="GENRE_OPTIONS"
                layout-class="flex flex-wrap gap-x-6 gap-y-2"
              />
            </FormRow>

            <FormRow label="作品篇幅">
              <CheckboxGroup
                v-model="selectedLengths"
                :options="LENGTH_OPTIONS"
                layout-class="flex flex-wrap gap-x-6 gap-y-2"
              />
            </FormRow>

            <FormRow label="作品來源">
              <CheckboxGroup
                v-model="selectedProvenances"
                :options="PROVENANCE_OPTIONS"
                layout-class="flex flex-wrap gap-x-6 gap-y-2"
              />
            </FormRow>

            <FormRow label="原始語言">
              <CheckboxGroup
                v-model="selectedLanguages"
                :options="LANGUAGE_OPTIONS"
                layout-class="flex flex-wrap gap-x-6 gap-y-2"
              />
            </FormRow>

            <FormRow label="精選／獎項">
              <div class="relative">
                <select
                  v-model="selectedCatalogueTitle"
                  class="text-main/70 border-main/20 focus:border-primary/50 focus-visible:outline-primary/50 w-full cursor-pointer appearance-none border-b bg-transparent py-1 pr-6 pl-0 text-sm transition-colors outline-none focus-visible:outline-2"
                >
                  <option value="">（不限）</option>
                  <template
                    v-for="[type, items] in cataloguesByType"
                    :key="type"
                  >
                    <optgroup :label="type">
                      <option
                        v-for="c in items"
                        :key="c.id"
                        :value="c.title"
                      >
                        {{ c.title }}
                      </option>
                    </optgroup>
                  </template>
                </select>
                <svg
                  class="text-main/40 pointer-events-none absolute top-1/2 right-2 -translate-y-1/2"
                  width="9"
                  height="5"
                  viewBox="0 0 10 6"
                  fill="none"
                >
                  <path
                    d="M0 0l5 6 5-6z"
                    fill="currentColor"
                  />
                </svg>
              </div>
            </FormRow>

            <FormRow
              label="概念標籤"
              align="top"
            >
              <button
                class="text-main/70 hover:text-primary decoration-main/20 hover:decoration-primary/50 text-left text-base underline underline-offset-4 transition-colors"
                @click="openModal"
              >
                + 點擊選取概念標籤
              </button>
              <div
                v-if="selectedConcepts.length > 0"
                class="mt-3 flex flex-wrap gap-1.5"
              >
                <span
                  v-for="concept in selectedConcepts"
                  :key="concept.id"
                  class="text-primary bg-primary/5 border-primary/15 inline-flex items-center gap-1 border px-2.5 py-1 text-xs"
                >
                  {{ concept.name }}
                  <button
                    class="hover:text-primary/60 ml-0.5 text-sm leading-none transition-colors"
                    :aria-label="`移除 ${concept.name}`"
                    @click.stop="toggleConcept(concept)"
                  >
                    &times;
                  </button>
                </span>
              </div>
            </FormRow>
          </dl>

          <!-- Footer Actions -->
          <div class="border-main/10 mt-10 flex justify-end gap-3 border-t pt-6">
            <button
              class="text-main/50 hover:text-primary px-3 py-1.5 text-sm transition-colors"
              @click="clearAllFilters"
            >
              清除條件
            </button>
            <button
              class="bg-primary text-bg px-4 py-1.5 text-sm font-medium transition-opacity hover:opacity-85"
              @click="isAdvancedMode = false"
            >
              查看結果 ({{ totalWorks }})
            </button>
          </div>
        </section>

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
              <HoverListItem
                v-for="work in works"
                :key="work.id"
                tag="div"
                class="flex flex-col justify-between gap-3 py-4 md:flex-row md:items-start"
              >
                <!-- Left: title + meta -->
                <div class="min-w-0 flex-1">
                  <router-link
                    :to="`/works/${work.id}`"
                    class="text-main group-hover:text-primary mb-1.5 block text-base font-medium no-underline transition-colors"
                  >
                    {{ work.title }}
                  </router-link>

                  <div class="text-main/50 flex flex-wrap items-center gap-x-1.5 gap-y-0.5 text-sm">
                    <span
                      v-if="work.byline && work.byline.length"
                      class="flex flex-wrap items-center gap-x-0.5"
                    >
                      <AgentInline :agents="work.byline" />
                    </span>
                    <span v-else>佚名</span>

                    <span class="text-main/20">·</span>
                    <span>{{ work.year || '未知' }}</span>
                    <template
                      v-if="[work.work_length_display, work.genre_display].filter(Boolean).length"
                    >
                      <span class="text-main/20">·</span>
                      <span>
                        {{
                          [work.work_length_display, work.genre_display].filter(Boolean).join('')
                        }}
                      </span>
                    </template>
                  </div>
                </div>

                <!-- Right: concept tags -->
                <div
                  v-if="work.work_concepts && work.work_concepts.length"
                  class="flex flex-wrap gap-1.5 md:max-w-[45%] md:justify-end"
                >
                  <ConceptTag
                    v-for="wc in work.work_concepts"
                    :key="wc.concept.slug"
                    :concept="wc.concept"
                  />
                </div>
              </HoverListItem>
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

<style scoped>
/* 移除 input number 的上下箭頭 */
input[type='number']::-webkit-inner-spin-button,
input[type='number']::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
input[type='number'] {
  -moz-appearance: textfield;
}

/* 自訂 Focus 狀態 */
.search-input:focus-within {
  border-color: rgba(194, 113, 78, 0.5); /* primary/50 */
}
</style>
