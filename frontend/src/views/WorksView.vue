<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'
import PaginationControls from '../components/PaginationControls.vue'
import ConceptTag from '../components/ConceptTag.vue'
import SectionTitle from '../components/SectionTitle.vue'
import { useDebounceFn } from '../composables/useDebounce'

// Filter Constants
const MEDIA_OPTIONS = [
  { value: 'novel', label: '小說' },
  { value: 'comic', label: '漫畫' },
]
const LENGTH_OPTIONS = [
  { value: 'long', label: '長篇' },
  { value: 'short', label: '中短篇' },
]
const CATEGORIES = ['新異 Novum', '敘事 Narrative', '主題 Theme', '未分類']
const CATEGORY_MAP: Record<string, string> = {
  novum: '新異 Novum',
  narrative: '敘事 Narrative',
  theme: '主題 Theme',
}
const PAGE_SIZE = 20 // FIX: needed to compute totalPages

// State
const searchQuery = ref('')
const selectedMedia = ref<string[]>([])
const selectedLengths = ref<string[]>([])
const selectedConcepts = ref<any[]>([])
const yearMin = ref<number | ''>('')
const yearMax = ref<number | ''>('')
const ordering = ref('-year')

const works = ref<any[]>([])
const totalWorks = ref(0)
const isLoading = ref(false)
const currentPage = ref(1)
const hasNext = ref(false)
const hasPrev = ref(false)

const allConcepts = ref<any[]>([])
const isModalOpen = ref(false)
const tempSelectedConcepts = ref<any[]>([])
const modalSearchQuery = ref('')

const isAdvancedMode = ref(false)

const route = useRoute()

// FIX: Compute total pages for pagination display
const totalPages = computed(() => Math.max(1, Math.ceil(totalWorks.value / PAGE_SIZE)))

// Data Fetching
const fetchAllConcepts = async () => {
  try {
    const res = await api.get('/concepts/all/')
    allConcepts.value = res.data || []
  } catch (err) {
    console.error('Failed to fetch concepts', err)
  }
}

const fetchWorks = async () => {
  isLoading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      ordering: ordering.value,
    }
    if (searchQuery.value) params.search = searchQuery.value
    if (selectedMedia.value.length) params.media_type = selectedMedia.value.join(',')
    if (selectedLengths.value.length) params.work_length = selectedLengths.value.join(',')
    if (selectedConcepts.value.length)
      params.concepts_in = selectedConcepts.value.map((c) => c.id).join(',')
    if (yearMin.value) params.year_min = yearMin.value
    if (yearMax.value) params.year_max = yearMax.value

    const res = await api.get('/works/', { params })
    works.value = res.data.results || []
    totalWorks.value = res.data.count || 0
    hasNext.value = !!res.data.next
    hasPrev.value = !!res.data.previous
  } catch (err) {
    console.error('Failed to fetch works', err)
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
  [searchQuery, selectedMedia, selectedLengths, selectedConcepts, yearMin, yearMax, ordering],
  () => {
    triggerFetch()
  },
  { deep: true },
)

onMounted(async () => {
  // 1. Wait for all concepts to load, so we can find the corresponding object by slug.
  await fetchAllConcepts()

  // 2. Check if the URL has a 'concept' query parameter.
  const conceptSlug = route.query.concept
  if (conceptSlug) {
    const matchedConcept = allConcepts.value.find((c) => c.slug === conceptSlug)
    if (matchedConcept) {
      selectedConcepts.value.push(matchedConcept)
      // The watcher will detect the change in selectedConcepts and automatically trigger fetchWorks(), so we can return here.
      return
    }
  }

  // 3. If there's no parameter or the concept is not found, fetch all works normally.
  fetchWorks()
})

// Concept Computed Properties
const mappedConcepts = computed(() => {
  return allConcepts.value.map((c) => ({
    ...c,
    mappedCategory: CATEGORY_MAP[c.category] || '未分類',
  }))
})

// Top 5 unselected concepts per category for the left panel
const leftPanelConcepts = computed(() => {
  const selectedIds = new Set(selectedConcepts.value.map((c) => c.id))
  const grouped: Record<string, any[]> = {
    '新異 Novum': [],
    '敘事 Narrative': [],
    '主題 Theme': [],
  }

  mappedConcepts.value.forEach((c) => {
    if (!selectedIds.has(c.id) && grouped[c.mappedCategory]) {
      grouped[c.mappedCategory].push(c)
    }
  })

  for (const cat in grouped) {
    grouped[cat].sort((a, b) => (b.works_count || 0) - (a.works_count || 0))
    grouped[cat] = grouped[cat].slice(0, 5)
  }
  return grouped
})

// Modal concepts grouped and filtered by modal search
const modalGroupedConcepts = computed(() => {
  const query = modalSearchQuery.value.toLowerCase()
  const filtered = mappedConcepts.value.filter((c) => c.name.toLowerCase().includes(query))

  const grouped: Record<string, any[]> = {}
  CATEGORIES.forEach((cat) => (grouped[cat] = []))

  filtered.forEach((c) => {
    if (grouped[c.mappedCategory]) {
      grouped[c.mappedCategory].push(c)
    }
  })

  for (const cat in grouped) {
    grouped[cat].sort((a, b) => a.name.localeCompare(b.name))
  }
  return grouped
})

// Methods
const toggleConcept = (concept: any) => {
  const index = selectedConcepts.value.findIndex((c) => c.id === concept.id)
  if (index === -1) {
    selectedConcepts.value.push(concept)
  } else {
    selectedConcepts.value.splice(index, 1)
  }
}

const openModal = () => {
  tempSelectedConcepts.value = [...selectedConcepts.value]
  modalSearchQuery.value = ''
  isModalOpen.value = true
}

// FIX: was calling undefined closeModal — now correctly closes the modal
const closeModal = () => {
  isModalOpen.value = false
}

const toggleTempConcept = (concept: any) => {
  const index = tempSelectedConcepts.value.findIndex((c) => c.id === concept.id)
  if (index === -1) {
    tempSelectedConcepts.value.push(concept)
  } else {
    tempSelectedConcepts.value.splice(index, 1)
  }
}

const applyModalConcepts = () => {
  selectedConcepts.value = [...tempSelectedConcepts.value]
  isModalOpen.value = false
}

const clearYearFilter = () => {
  yearMin.value = ''
  yearMax.value = ''
}

const clearAllFilters = () => {
  searchQuery.value = ''
  selectedMedia.value = []
  selectedLengths.value = []
  selectedConcepts.value = []
  yearMin.value = ''
  yearMax.value = ''
  tempSelectedConcepts.value = []
  modalSearchQuery.value = ''
}

const changePage = (dir: number) => {
  currentPage.value += dir
  fetchWorks()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<template>
  <div class="mx-auto flex max-w-4xl flex-col items-start gap-0 pb-20 lg:flex-row lg:gap-12">
    <!-- ══ Left Sidebar ══ -->
    <aside
      class="lg:border-main/10 w-full shrink-0 pt-10 lg:sticky lg:top-8 lg:w-56 lg:border-r lg:pr-8 lg:pb-20"
    >
      <!-- Search -->
      <div class="mb-7">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜尋標題、作者…"
          class="text-main placeholder:text-main/40 border-main/15 focus:border-primary/50 w-full border bg-transparent px-3 py-2 text-base transition-colors outline-none"
        />
        <button
          class="text-main/50 border-main/10 hover:text-primary hover:border-primary/30 mt-2 w-full border py-2 text-sm font-medium tracking-wide transition-colors"
          @click="isAdvancedMode = !isAdvancedMode"
        >
          {{ isAdvancedMode ? '返回一般結果' : '進階搜索' }}
        </button>
      </div>

      <!-- Media Type -->
      <div class="mb-6">
        <SectionTitle class="mb-3">作品媒體</SectionTitle>
        <div class="flex flex-col gap-2">
          <label
            v-for="opt in MEDIA_OPTIONS"
            :key="opt.value"
            class="group flex cursor-pointer items-center gap-2"
          >
            <input
              v-model="selectedMedia"
              type="checkbox"
              :value="opt.value"
              class="text-primary border-main/25 h-4 w-4 shrink-0 cursor-pointer rounded-none focus:ring-0 focus:ring-offset-0"
            />
            <span class="text-main/60 group-hover:text-primary text-sm transition-colors">
              {{ opt.label }}
            </span>
          </label>
        </div>
      </div>

      <!-- Work Length -->
      <div class="mb-6">
        <SectionTitle class="mb-3">作品篇幅</SectionTitle>
        <div class="flex flex-col gap-2">
          <label
            v-for="opt in LENGTH_OPTIONS"
            :key="opt.value"
            class="group flex cursor-pointer items-center gap-2"
          >
            <input
              v-model="selectedLengths"
              type="checkbox"
              :value="opt.value"
              class="text-primary border-main/25 h-4 w-4 shrink-0 cursor-pointer rounded-none focus:ring-0 focus:ring-offset-0"
            />
            <span class="text-main/60 group-hover:text-primary text-sm transition-colors">
              {{ opt.label }}
            </span>
          </label>
        </div>
      </div>

      <!-- Concept Tags -->
      <div>
        <SectionTitle class="mb-3">概念標籤</SectionTitle>

        <!-- Selected tags -->
        <div
          v-if="selectedConcepts.length > 0"
          class="mb-4"
        >
          <div class="flex flex-col gap-1.5">
            <label
              v-for="concept in selectedConcepts"
              :key="concept.id"
              class="group flex cursor-pointer items-center gap-2"
            >
              <input
                type="checkbox"
                :checked="true"
                class="text-primary border-main/25 h-4 w-4 shrink-0 cursor-pointer rounded-none focus:ring-0 focus:ring-offset-0"
                @change="toggleConcept(concept)"
              />
              <span class="text-primary text-sm font-medium">{{ concept.name }}</span>
            </label>
          </div>
          <div class="border-main/10 mt-3 mb-3 border-t"></div>
        </div>

        <!-- Top concept categories -->
        <div class="space-y-4">
          <div
            v-for="(concepts, cat) in leftPanelConcepts"
            :key="cat"
          >
            <div v-if="concepts.length > 0">
              <div class="text-main/30 mb-2 text-sm font-medium tracking-widest uppercase">
                {{ cat.split(' ')[0] }}
              </div>
              <div class="flex flex-col gap-1.5">
                <label
                  v-for="concept in concepts"
                  :key="concept.id"
                  class="group flex cursor-pointer items-center gap-2"
                >
                  <input
                    type="checkbox"
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
          </div>
        </div>

        <button
          class="text-primary border-primary/30 hover:bg-primary/5 mt-5 w-full border border-dashed py-2 text-xs font-medium transition-colors"
          @click="openModal"
        >
          展開所有標籤
        </button>
      </div>
    </aside>

    <!-- ══ Main Panel ══ -->
    <main class="min-w-0 flex-1 pt-10">
      <!-- ── Advanced Search ── -->
      <section
        v-if="isAdvancedMode"
        class="border-main/10 mb-8 border-b pb-10"
      >
        <SectionTitle class="mb-6">
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

        <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
          <div>
            <label class="text-main/40 mb-2 block text-sm font-medium tracking-widest uppercase">
              關鍵字
            </label>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="標題、作者、筆名等"
              class="text-main placeholder:text-main/40 border-main/15 focus:border-primary/50 w-full border bg-transparent px-3 py-2 text-base transition-colors outline-none"
            />
          </div>

          <div>
            <label class="text-main/40 mb-2 block text-sm font-medium tracking-widest uppercase">
              發表年份區間
            </label>
            <div class="flex items-center gap-2">
              <input
                v-model="yearMin"
                type="number"
                placeholder="YYYY"
                class="text-main placeholder:text-main/40 border-main/15 focus:border-primary/50 w-full border bg-transparent px-3 py-2 text-base transition-colors outline-none"
              />
              <span class="text-main/40 shrink-0 text-xs">至</span>
              <input
                v-model="yearMax"
                type="number"
                placeholder="YYYY"
                class="text-main placeholder:text-main/40 border-main/15 focus:border-primary/50 w-full border bg-transparent px-3 py-2 text-base transition-colors outline-none"
              />
            </div>
          </div>

          <div class="space-y-5">
            <div>
              <label
                class="text-main/40 mb-2.5 block text-sm font-medium tracking-widest uppercase"
              >
                媒體類型
              </label>
              <div class="flex flex-wrap gap-x-5 gap-y-2">
                <label
                  v-for="opt in MEDIA_OPTIONS"
                  :key="opt.value"
                  class="group flex cursor-pointer items-center gap-2"
                >
                  <input
                    v-model="selectedMedia"
                    type="checkbox"
                    :value="opt.value"
                    class="text-primary border-main/25 h-4 w-4 rounded-none focus:ring-0 focus:ring-offset-0"
                  />
                  <span class="text-main/60 group-hover:text-primary text-sm transition-colors">
                    {{ opt.label }}
                  </span>
                </label>
              </div>
            </div>
            <div>
              <label
                class="text-main/40 mb-2.5 block text-sm font-medium tracking-widest uppercase"
              >
                作品篇幅
              </label>
              <div class="flex flex-wrap gap-x-5 gap-y-2">
                <label
                  v-for="opt in LENGTH_OPTIONS"
                  :key="opt.value"
                  class="group flex cursor-pointer items-center gap-2"
                >
                  <input
                    v-model="selectedLengths"
                    type="checkbox"
                    :value="opt.value"
                    class="text-primary border-main/25 h-4 w-4 rounded-none focus:ring-0 focus:ring-offset-0"
                  />
                  <span class="text-main/60 group-hover:text-primary text-sm transition-colors">
                    {{ opt.label }}
                  </span>
                </label>
              </div>
            </div>
          </div>

          <div>
            <label class="text-main/40 mb-2.5 block text-sm font-medium tracking-widest uppercase">
              概念標籤
            </label>
            <button
              class="border-primary/30 text-primary hover:bg-primary/5 w-full border border-dashed px-3 py-2 text-left text-base transition-colors"
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
                class="text-primary bg-primary/10 border-primary/20 inline-flex items-center gap-1 border px-2.5 py-1 text-xs"
              >
                {{ concept.name }}
                <button
                  class="hover:text-primary/60 ml-0.5 text-sm leading-none transition-colors"
                  @click.stop="toggleConcept(concept)"
                >
                  &times;
                </button>
              </span>
            </div>
          </div>
        </div>

        <div class="border-main/10 mt-8 flex justify-end gap-3 border-t pt-5">
          <button
            class="text-main/50 hover:text-primary px-3 py-1.5 text-sm transition-colors"
            @click="clearAllFilters"
          >
            清除條件
          </button>
          <button
            class="text-bg bg-primary px-4 py-1.5 text-sm font-medium transition-opacity hover:opacity-85"
            @click="isAdvancedMode = false"
          >
            查看結果（{{ totalWorks }}）
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
              selectedMedia.length ||
              selectedLengths.length ||
              yearMin ||
              yearMax
            "
            class="flex flex-wrap items-center gap-1.5"
          >
            <span class="text-main/40 mr-1 shrink-0 text-xs">作用中：</span>

            <span
              v-for="m in selectedMedia"
              :key="m"
              class="text-primary bg-primary/10 border-primary/20 inline-flex items-center gap-1 border px-2.5 py-1 text-xs"
            >
              {{ MEDIA_OPTIONS.find((o) => o.value === m)?.label }}
              <button
                class="ml-0.5 text-sm leading-none transition-opacity hover:opacity-60"
                @click="selectedMedia = selectedMedia.filter((v) => v !== m)"
              >
                &times;
              </button>
            </span>

            <span
              v-for="l in selectedLengths"
              :key="l"
              class="text-primary bg-primary/10 border-primary/20 inline-flex items-center gap-1 border px-2.5 py-1 text-xs"
            >
              {{ LENGTH_OPTIONS.find((o) => o.value === l)?.label }}
              <button
                class="ml-0.5 text-sm leading-none transition-opacity hover:opacity-60"
                @click="selectedLengths = selectedLengths.filter((v) => v !== l)"
              >
                &times;
              </button>
            </span>

            <span
              v-for="c in selectedConcepts"
              :key="c.id"
              class="text-primary bg-primary/10 border-primary/20 inline-flex items-center gap-1 border px-2.5 py-1 text-xs"
            >
              {{ c.name }}
              <button
                class="ml-0.5 text-sm leading-none transition-opacity hover:opacity-60"
                @click="toggleConcept(c)"
              >
                &times;
              </button>
            </span>

            <span
              v-if="yearMin || yearMax"
              class="text-primary bg-primary/10 border-primary/20 inline-flex items-center gap-1 border px-2.5 py-1 text-xs"
            >
              {{ yearMin || '…' }}–{{ yearMax || '…' }}
              <button
                class="ml-0.5 text-sm leading-none transition-opacity hover:opacity-60"
                @click="clearYearFilter"
              >
                &times;
              </button>
            </span>

            <button
              class="text-main/40 hover:text-primary ml-auto text-xs transition-colors"
              @click="clearAllFilters"
            >
              清除全部
            </button>
          </div>

          <!-- Count + Sort -->
          <div class="flex items-center justify-between">
            <span class="text-main/50 text-sm">
              共
              <span class="text-primary font-mono">{{ totalWorks }}</span>
              部作品
            </span>

            <div class="flex items-center gap-2">
              <span class="text-main/40 text-xs">排序</span>
              <div class="relative">
                <select
                  v-model="ordering"
                  class="text-main/70 border-main/10 focus:border-primary/50 cursor-pointer appearance-none border bg-transparent py-1 pr-6 pl-2.5 text-sm transition-colors outline-none"
                >
                  <option value="-year">年份（新到舊）</option>
                  <option value="year">年份（舊到新）</option>
                  <option value="title">標題</option>
                  <option value="-updated_at">最近更新</option>
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
            </div>
          </div>
        </div>

        <!-- Works List -->
        <div
          v-if="isLoading"
          class="text-main/40 py-16 text-center text-base"
        >
          搜尋中…
        </div>
        <div
          v-else-if="works.length === 0"
          class="text-main/40 py-16 text-center text-base"
        >
          找不到符合條件的作品。
        </div>

        <div
          v-else
          class="flex flex-col"
        >
          <div
            v-for="work in works"
            :key="work.id"
            class="group border-main/10 relative z-0 flex flex-col justify-between gap-3 border-b py-4 transition-colors last:border-0 md:flex-row md:items-start"
          >
            <!-- Hover Background Overlay -->
            <div
              class="pointer-events-none absolute -inset-x-3 inset-y-0 -z-10 rounded-sm bg-transparent transition-colors group-hover:bg-white/5"
            ></div>

            <!-- Accent line -->
            <div
              class="group-hover:bg-primary pointer-events-none absolute top-0 bottom-0 -left-3 w-0.5 bg-transparent transition-colors"
            ></div>

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
                <span class="text-main/20">·</span>
                <!-- Gray metadata badges -->
                <span class="text-main/50 bg-main/5 px-1.5 py-0.5 font-mono text-[10px]">
                  {{
                    [work.work_length_display, work.media_type_display]
                      .filter(Boolean)
                      .join(' · ') || '-'
                  }}
                </span>
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
          </div>
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
  <div
    v-if="isModalOpen"
    class="bg-main/40 fixed inset-0 z-50 flex items-center justify-center p-4"
    @click.self="closeModal"
  >
    <div
      class="bg-bg border-main/10 flex max-h-[88vh] w-full max-w-3xl flex-col overflow-hidden border"
    >
      <!-- Modal Header -->
      <div class="border-main/10 shrink-0 border-b px-6 pt-6 pb-5">
        <div class="mb-5 flex items-center justify-between">
          <h2 class="text-main text-xl font-normal">選取概念標籤</h2>
          <button
            class="text-main/40 border-main/10 hover:text-primary hover:border-primary/30 border px-3 py-1 text-sm transition-colors"
            @click="closeModal"
          >
            取消
          </button>
        </div>

        <input
          v-model="modalSearchQuery"
          type="text"
          placeholder="搜尋標籤…"
          class="text-main placeholder:text-main/40 border-main/15 focus:border-primary/50 w-full border bg-transparent px-3 py-2 text-base transition-colors outline-none"
        />

        <!-- Selected in modal -->
        <div class="mt-4 flex min-h-[28px] flex-wrap items-center gap-1.5">
          <span class="text-main/40 mr-1 shrink-0 text-sm font-medium tracking-widest uppercase">
            已選取
          </span>
          <span
            v-if="tempSelectedConcepts.length === 0"
            class="text-main/30 text-xs"
          >
            —
          </span>
          <span
            v-for="concept in tempSelectedConcepts"
            :key="concept.id"
            class="text-primary bg-primary/10 border-primary/20 inline-flex items-center gap-1 border px-2.5 py-1 text-xs"
          >
            {{ concept.name }}
            <button
              class="ml-0.5 text-sm leading-none transition-opacity hover:opacity-60"
              @click="toggleTempConcept(concept)"
            >
              &times;
            </button>
          </span>
        </div>
      </div>

      <!-- Modal Body -->
      <div class="flex-1 overflow-y-auto px-6 py-5">
        <div class="space-y-8">
          <div
            v-for="cat in CATEGORIES"
            :key="cat"
          >
            <template v-if="modalGroupedConcepts[cat]?.length > 0">
              <SectionTitle class="mb-4">{{ cat }}</SectionTitle>
              <div class="grid grid-cols-1 gap-x-4 gap-y-1 sm:grid-cols-2 md:grid-cols-3">
                <label
                  v-for="concept in modalGroupedConcepts[cat]"
                  :key="concept.id"
                  class="group hover:bg-primary/5 flex cursor-pointer items-center gap-2 px-2 py-1.5 transition-colors"
                >
                  <input
                    type="checkbox"
                    :checked="tempSelectedConcepts.some((c) => c.id === concept.id)"
                    class="text-primary border-main/25 h-4 w-4 shrink-0 cursor-pointer rounded-none focus:ring-0 focus:ring-offset-0"
                    @change="toggleTempConcept(concept)"
                  />
                  <span
                    class="text-main/60 group-hover:text-main/80 truncate text-sm transition-colors"
                  >
                    {{ concept.name }}
                  </span>
                </label>
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="border-main/10 flex shrink-0 justify-end gap-3 border-t px-6 py-4">
        <button
          class="text-main/50 hover:text-primary px-3 py-1.5 text-xs transition-colors"
          @click="clearAllFilters"
        >
          清除條件
        </button>
        <button
          class="text-bg bg-primary px-4 py-1.5 text-xs font-medium transition-opacity hover:opacity-85"
          @click="applyModalConcepts"
        >
          套用篩選
        </button>
      </div>
    </div>
  </div>
</template>
