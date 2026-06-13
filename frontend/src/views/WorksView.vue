<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchWorks as fetchWorksApi } from '../api/works'
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
import BaseSearchInput from '../components/BaseSearchInput.vue'
import { useDebounceFn } from '../composables/useDebounce'
import { useDocumentMeta } from '../composables/useDocumentTitle'
import { CONCEPT_CATEGORY_MAP, DEFAULT_PAGE_SIZE } from '../utils/constants'

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

// State
const searchQuery = ref('')
const selectedGenres = ref<string[]>([])
const selectedLengths = ref<string[]>([])
const selectedProvenances = ref<string[]>([])
const selectedLanguages = ref<string[]>([])
const selectedConcepts = ref<Concept[]>([])
const yearMin = ref<number | ''>('')
const yearMax = ref<number | ''>('')
const ordering = ref('-year')
const selectedPublicationId = ref('')
const selectedPublicationTitle = ref('')
const selectedCatalogueTitle = ref('')

const works = ref<Work[]>([])
const totalWorks = ref(0)
const isLoading = ref(false)
const hasError = ref(false)
const currentPage = ref(1)
const hasNext = ref(false)
const hasPrev = ref(false)

const allConcepts = ref<Concept[]>([])
const isModalOpen = ref(false)

const isAdvancedMode = ref(false)

const route = useRoute()
const router = useRouter()

// FIX: Compute total pages for pagination display
const totalPages = computed(() => Math.max(1, Math.ceil(totalWorks.value / DEFAULT_PAGE_SIZE)))

// Data Fetching
const fetchAllConcepts = async () => {
  try {
    const res = await fetchAllConceptsApi()
    allConcepts.value = res.data || []
  } catch (err) {
    console.error('Failed to fetch concepts', err)
  }
}

const fetchWorks = async () => {
  isLoading.value = true
  hasError.value = false
  try {
    const params: Record<string, string | number | boolean> = {
      page: currentPage.value,
      ordering: ordering.value,
    }
    if (searchQuery.value) params.search = searchQuery.value
    if (selectedGenres.value.length) params.genre = selectedGenres.value.join(',')
    if (selectedLengths.value.length) params.work_length = selectedLengths.value.join(',')
    if (selectedProvenances.value.length) params.provenance = selectedProvenances.value.join(',')
    if (selectedLanguages.value.length) params.language = selectedLanguages.value.join(',')
    if (selectedConcepts.value.length)
      params.concepts_in = selectedConcepts.value.map((c) => c.id).join(',')
    if (yearMin.value) params.year_min = yearMin.value
    if (yearMax.value) params.year_max = yearMax.value
    if (selectedPublicationId.value) params.publication = selectedPublicationId.value
    if (selectedCatalogueTitle.value) params.catalogue = selectedCatalogueTitle.value

    const res = await fetchWorksApi(params)
    works.value = res.data.results || []
    totalWorks.value = res.data.count || 0
    hasNext.value = !!res.data.next
    hasPrev.value = !!res.data.previous
  } catch (err) {
    console.error('Failed to fetch works', err)
    hasError.value = true
  } finally {
    isLoading.value = false
  }
}

// Debounce Strategy for Real-time Search
const triggerFetch = useDebounceFn(() => {
  currentPage.value = 1
  fetchWorks()
}, 300)

// Watch all filter states and trigger fetch
watch(
  [
    searchQuery,
    selectedGenres,
    selectedLengths,
    selectedProvenances,
    selectedLanguages,
    selectedConcepts,
    yearMin,
    yearMax,
    ordering,
  ],
  () => {
    triggerFetch()
  },
  { deep: true },
)

watch(
  () => route.query,
  (q) => {
    selectedPublicationId.value = (q.publication as string) || ''
    selectedPublicationTitle.value = (q.publication_title as string) || ''
    selectedCatalogueTitle.value = (q.catalogue as string) || ''
    triggerFetch()
  },
  { immediate: true },
)

onMounted(async () => {
  // 1. Wait for all concepts to load, so we can find the corresponding object by slug.
  await fetchAllConcepts()

  // 2. Check if the URL has a 'concept' query parameter.
  const conceptSlug = route.query.concept
  if (conceptSlug) {
    const matchedConcept = allConcepts.value.find((c) => c.slug === conceptSlug)
    if (matchedConcept && !selectedConcepts.value.some((c) => c.id === matchedConcept.id)) {
      selectedConcepts.value.push(matchedConcept)
    }
  }
})

// Concept Computed Properties
const mappedConcepts = computed(() => {
  return allConcepts.value.map((c) => ({
    ...c,
    mappedCategory: CONCEPT_CATEGORY_MAP[c.category] || '未分類',
  }))
})

// Featured concepts for the left panel
const leftPanelConcepts = computed(() => {
  const selectedIds = new Set(selectedConcepts.value.map((c) => c.id))
  return mappedConcepts.value
    .filter((c) => c.is_featured && !selectedIds.has(c.id))
    .sort((a, b) => (a.featured_order || 0) - (b.featured_order || 0))
})

// Methods
const toggleConcept = (concept: Concept) => {
  const index = selectedConcepts.value.findIndex((c) => c.id === concept.id)
  if (index === -1) {
    selectedConcepts.value.push(concept)
  } else {
    selectedConcepts.value.splice(index, 1)
  }
}

const openModal = () => {
  isModalOpen.value = true
}

// FIX: was calling undefined closeModal — now correctly closes the modal
const closeModal = () => {
  isModalOpen.value = false
}

const clearYearFilter = () => {
  yearMin.value = ''
  yearMax.value = ''
}

const clearAllFilters = () => {
  searchQuery.value = ''
  selectedGenres.value = []
  selectedLengths.value = []
  selectedProvenances.value = []
  selectedLanguages.value = []
  selectedConcepts.value = []
  yearMin.value = ''
  yearMax.value = ''
  if (route.query.publication || route.query.catalogue) {
    const query = { ...route.query }
    delete query.publication
    delete query.publication_title
    delete query.catalogue
    router.replace({ query })
  }
}

const clearPublication = () => {
  const query = { ...route.query }
  delete query.publication
  delete query.publication_title
  router.replace({ query })
}

const clearCatalogue = () => {
  const query = { ...route.query }
  delete query.catalogue
  router.replace({ query })
}

const changePage = (dir: number) => {
  currentPage.value += dir
  fetchWorks()
}
</script>

<template>
  <div>
    <div class="mx-auto flex max-w-4xl flex-col items-start gap-0 pb-20 lg:flex-row lg:gap-12">
      <!-- ══ Left Sidebar ══ -->
      <aside
        class="lg:border-main/10 hidden shrink-0 pt-6 md:pt-10 lg:block lg:w-56 lg:border-r lg:pr-8 lg:pb-20"
      >
        <!-- Search (Desktop) -->
        <div class="mb-7 hidden lg:block">
          <BaseSearchInput
            v-model="searchQuery"
            placeholder="搜尋標題、作者…"
            class="text-main placeholder:text-main/40 border-main/20 focus:border-primary/50 focus-visible:outline-primary/50 w-full border-b bg-transparent py-2 pr-8 pl-6 text-base transition-colors outline-none focus-visible:outline-2"
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
                <input
                  type="checkbox"
                  name="selected-concept"
                  :checked="true"
                  class="text-primary border-main/25 h-4 w-4 shrink-0 cursor-pointer rounded-none focus:ring-0 focus:ring-offset-0"
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
                <input
                  type="checkbox"
                  name="featured-concept"
                  :checked="false"
                  class="text-primary border-main/25 h-4 w-4 shrink-0 cursor-pointer rounded-none focus:ring-0 focus:ring-offset-0"
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

      <!-- ══ Main Panel ══ -->
      <main class="min-w-0 flex-1 pt-6 md:pt-10">
        <!-- Search and Filter (Mobile) -->
        <div class="mb-6 flex items-center gap-3 lg:hidden">
          <div class="min-w-0 flex-1">
            <BaseSearchInput
              v-model="searchQuery"
              placeholder="搜尋標題、作者…"
              class="text-main placeholder:text-main/40 border-main/20 focus:border-primary/50 focus-visible:outline-primary/50 w-full border-b bg-transparent py-2 pr-8 pl-6 text-base transition-colors outline-none focus-visible:outline-2"
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

        <!-- ── Advanced Search ── -->
        <section
          v-if="isAdvancedMode"
          class="border-main/10 mb-8 border-b pb-10"
        >
          <SectionTitle class="mb-8">
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
            <!-- 關鍵字 -->
            <div class="pt-0 pb-6 md:flex md:items-baseline md:gap-6">
              <dt
                class="text-main/40 mb-2 shrink-0 text-sm font-medium tracking-widest uppercase md:mb-0 md:w-28"
              >
                關鍵字
              </dt>
              <dd class="flex-1">
                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="標題、作者、筆名等"
                  class="text-main placeholder:text-main/30 border-main/20 focus:border-primary/50 w-full border-b bg-transparent pb-2 text-base transition-colors outline-none"
                />
              </dd>
            </div>

            <!-- 發表年份 -->
            <div class="py-6 md:flex md:items-baseline md:gap-6">
              <dt
                class="text-main/40 mb-2 shrink-0 text-sm font-medium tracking-widest uppercase md:mb-0 md:w-28"
              >
                發表年份
              </dt>
              <dd class="flex-1">
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
              </dd>
            </div>

            <!-- 作品體裁 -->
            <div class="py-6 md:flex md:items-baseline md:gap-6">
              <dt
                class="text-main/40 mb-2 shrink-0 text-sm font-medium tracking-widest uppercase md:mb-0 md:w-28"
              >
                作品體裁
              </dt>
              <dd class="flex-1">
                <CheckboxGroup
                  v-model="selectedGenres"
                  :options="GENRE_OPTIONS"
                  layout-class="flex flex-wrap gap-x-6 gap-y-2"
                />
              </dd>
            </div>

            <!-- 作品篇幅 -->
            <div class="py-6 md:flex md:items-baseline md:gap-6">
              <dt
                class="text-main/40 mb-2 shrink-0 text-sm font-medium tracking-widest uppercase md:mb-0 md:w-28"
              >
                作品篇幅
              </dt>
              <dd class="flex-1">
                <CheckboxGroup
                  v-model="selectedLengths"
                  :options="LENGTH_OPTIONS"
                  layout-class="flex flex-wrap gap-x-6 gap-y-2"
                />
              </dd>
            </div>

            <!-- 作品來源 -->
            <div class="py-6 md:flex md:items-baseline md:gap-6">
              <dt
                class="text-main/40 mb-2 shrink-0 text-sm font-medium tracking-widest uppercase md:mb-0 md:w-28"
              >
                作品來源
              </dt>
              <dd class="flex-1">
                <CheckboxGroup
                  v-model="selectedProvenances"
                  :options="PROVENANCE_OPTIONS"
                  layout-class="flex flex-wrap gap-x-6 gap-y-2"
                />
              </dd>
            </div>

            <!-- 原始語言 -->
            <div class="py-6 md:flex md:items-baseline md:gap-6">
              <dt
                class="text-main/40 mb-2 shrink-0 text-sm font-medium tracking-widest uppercase md:mb-0 md:w-28"
              >
                原始語言
              </dt>
              <dd class="flex-1">
                <CheckboxGroup
                  v-model="selectedLanguages"
                  :options="LANGUAGE_OPTIONS"
                  layout-class="flex flex-wrap gap-x-6 gap-y-2"
                />
              </dd>
            </div>

            <!-- 概念標籤 -->
            <div class="pt-6 pb-0 md:flex md:gap-6">
              <dt
                class="text-main/40 mb-2 shrink-0 pt-0.5 text-sm font-medium tracking-widest uppercase md:mb-0 md:w-28"
              >
                概念標籤
              </dt>
              <dd class="flex-1">
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
              </dd>
            </div>
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

        <!-- ── Results View ── -->
        <template v-else>
          <!-- Active Filters + Sort Bar -->
          <div class="border-main/10 mb-1 flex flex-col gap-3 border-b pb-5">
            <!-- Active filter chips -->
            <div
              v-if="
                selectedConcepts.length ||
                selectedGenres.length ||
                selectedLengths.length ||
                yearMin ||
                yearMax ||
                selectedPublicationId ||
                selectedCatalogueTitle
              "
              class="flex flex-wrap items-center gap-1.5"
            >
              <span class="text-main/40 mr-1 shrink-0 text-xs">作用中：</span>

              <FilterChip
                v-if="selectedPublicationId"
                :label="`出版物：${selectedPublicationTitle}`"
                @remove="clearPublication"
              />
              <FilterChip
                v-if="selectedCatalogueTitle"
                :label="`精選：${selectedCatalogueTitle}`"
                @remove="clearCatalogue"
              />
              <FilterChip
                v-for="m in selectedGenres"
                :key="m"
                :label="GENRE_OPTIONS.find((o) => o.value === m)?.label || ''"
                @remove="selectedGenres = selectedGenres.filter((v) => v !== m)"
              />
              <FilterChip
                v-for="l in selectedLengths"
                :key="l"
                :label="LENGTH_OPTIONS.find((o) => o.value === l)?.label || ''"
                @remove="selectedLengths = selectedLengths.filter((v) => v !== l)"
              />
              <FilterChip
                v-for="c in selectedConcepts"
                :key="c.id"
                :label="c.name"
                @remove="toggleConcept(c)"
              />
              <FilterChip
                v-if="yearMin || yearMax"
                :label="`${yearMin || '…'}–${yearMax || '…'}`"
                @remove="clearYearFilter"
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

          <!-- Works List -->
          <div
            v-if="isLoading"
            class="text-main/40 animate-pulse py-16 text-center text-base"
          >
            搜尋中…
          </div>
          <div
            v-else-if="hasError"
            class="text-main/50 py-16 text-center text-base font-medium"
          >
            資料讀取發生問題，請稍後再試。
          </div>
          <div
            v-else-if="works.length === 0"
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
            <span class="text-main/35 text-sm">找不到符合條件的作品。</span>
          </div>

          <div
            v-else
            class="flex flex-col"
          >
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
                    <template
                      v-for="(agent, idx) in work.byline"
                      :key="idx"
                    >
                      <router-link
                        v-if="agent.id && agent.agent_type === 'person'"
                        :to="`/persons/${agent.id}`"
                        class="hover:text-primary no-underline transition-colors"
                      >
                        {{ agent.text }}
                      </router-link>
                      <span v-else>{{ agent.text }}</span>
                      <span v-if="idx < work.byline.length - 1">、</span>
                    </template>
                  </span>
                  <span v-else>佚名</span>

                  <span class="text-main/20">·</span>
                  <span>{{ work.year || '未知' }}</span>
                  <template
                    v-if="[work.work_length_display, work.genre_display].filter(Boolean).length"
                  >
                    <span class="text-main/20">·</span>
                    <span>
                      {{ [work.work_length_display, work.genre_display].filter(Boolean).join('') }}
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
            v-if="works.length > 0 && (hasPrev || hasNext)"
            :current-page="currentPage"
            :total-pages="totalPages"
            :has-prev="hasPrev"
            :has-next="hasNext"
            @change-page="changePage"
          />
        </template>
      </main>
    </div>

    <!-- ══ Concept Modal ══ -->
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
