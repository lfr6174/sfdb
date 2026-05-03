<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'
import PaginationControls from '../components/PaginationControls.vue'

// Filter Constants
const MEDIA_OPTIONS = [
  { value: 'novel', label: '小說' },
  { value: 'comic', label: '漫畫' }
]
const LENGTH_OPTIONS = [
  { value: 'long', label: '長篇' },
  { value: 'short', label: '中短篇' }
]
const CATEGORIES = ['新異 Novum', '敘事 Narrative', '主題 Theme', '未分類']
const CATEGORY_MAP: Record<string, string> = {
  'novum': '新異 Novum',
  'narrative': '敘事 Narrative',
  'theme': '主題 Theme',
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
    if (selectedConcepts.value.length) params.concepts_in = selectedConcepts.value.map(c => c.id).join(',')
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
let fetchTimeout: any
const triggerFetch = () => {
  clearTimeout(fetchTimeout)
  fetchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchWorks()
  }, 300)
}

// Watch all filter states and trigger fetch
watch([searchQuery, selectedMedia, selectedLengths, selectedConcepts, yearMin, yearMax, ordering], () => {
  triggerFetch()
}, { deep: true })

onMounted(async () => {
  // 1. Wait for all concepts to load, so we can find the corresponding object by slug.
  await fetchAllConcepts()

  // 2. Check if the URL has a 'concept' query parameter.
  const conceptSlug = route.query.concept
  if (conceptSlug) {
    const matchedConcept = allConcepts.value.find(c => c.slug === conceptSlug)
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
  return allConcepts.value.map(c => ({
    ...c,
    mappedCategory: CATEGORY_MAP[c.category] || '未分類'
  }))
})

// Top 5 unselected concepts per category for the left panel
const leftPanelConcepts = computed(() => {
  const selectedIds = new Set(selectedConcepts.value.map(c => c.id))
  const grouped: Record<string, any[]> = { '新異 Novum': [], '敘事 Narrative': [], '主題 Theme': [] }

  mappedConcepts.value.forEach(c => {
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
  const filtered = mappedConcepts.value.filter(c => c.name.toLowerCase().includes(query))

  const grouped: Record<string, any[]> = {}
  CATEGORIES.forEach(cat => grouped[cat] = [])

  filtered.forEach(c => {
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
  const index = selectedConcepts.value.findIndex(c => c.id === concept.id)
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
  const index = tempSelectedConcepts.value.findIndex(c => c.id === concept.id)
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

const clearAllFilters = () => {
  searchQuery.value = ''
  selectedMedia.value = []
  selectedLengths.value = []
  selectedConcepts.value = []
  yearMin.value = ''
  yearMax.value = ''
}

const changePage = (dir: number) => {
  currentPage.value += dir
  fetchWorks()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<template>
  <div class="max-w-4xl mx-auto flex flex-col lg:flex-row gap-4 items-start pb-12">

    <!-- Left Control Panel -->
    <aside class="w-full lg:w-4/15 card shrink-0 lg:sticky lg:top-4 !p-5">
      <!-- Search -->
      <div class="mb-4">
        <input v-model="searchQuery" type="text" placeholder="搜尋標題、作者、筆名..." class="w-full h-10 px-3 border border-main/10 rounded bg-bg focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors text-sm text-main placeholder-main/50" />
        <button @click="isAdvancedMode = !isAdvancedMode" class="w-full mt-2 py-2 text-xs font-medium text-main/50 border border-main/10 rounded hover:text-primary hover:border-primary/30 transition-colors">
          {{ isAdvancedMode ? '返回一般結果' : '進階搜索' }}
        </button>
      </div>

      <!-- Media & Length Filters -->
      <div class="mb-6 space-y-4">
        <div>
          <h3 class="text-xs font-bold tracking-widest uppercase text-main/40 mb-2">作品媒體</h3>
          <div class="flex flex-col gap-2">
            <label v-for="opt in MEDIA_OPTIONS" :key="opt.value" class="flex items-center gap-2 cursor-pointer group">
              <input type="checkbox" :value="opt.value" v-model="selectedMedia" class="w-4 h-4 text-primary border-main/10 rounded focus:ring-primary cursor-pointer" />
              <span class="text-sm text-main/60 group-hover:text-primary transition-colors">{{ opt.label }}</span>
            </label>
          </div>
        </div>
        <div>
          <h3 class="text-xs font-bold tracking-widest uppercase text-main/40 mb-2">作品篇幅</h3>
          <div class="flex flex-col gap-2">
            <label v-for="opt in LENGTH_OPTIONS" :key="opt.value" class="flex items-center gap-2 cursor-pointer group">
              <input type="checkbox" :value="opt.value" v-model="selectedLengths" class="w-4 h-4 text-primary border-main/10 rounded focus:ring-primary cursor-pointer" />
              <span class="text-sm text-main/60 group-hover:text-primary transition-colors">{{ opt.label }}</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Concept Tags Section -->
      <div>
        <h3 class="text-xs font-bold tracking-widest uppercase text-main/40 mb-3">概念標籤</h3>

        <!-- Selected Tags -->
        <div v-if="selectedConcepts.length > 0" class="mb-4 p-3 bg-main/5 rounded-md border border-main/10">
          <div class="text-xs font-bold text-main/40 mb-2 uppercase tracking-widest">已勾選</div>
          <div class="flex flex-col gap-2">
            <label v-for="concept in selectedConcepts" :key="concept.id" class="flex items-center gap-2 cursor-pointer group">
              <input type="checkbox" :checked="true" @change="toggleConcept(concept)" class="w-4 h-4 text-primary border-main/10 rounded focus:ring-primary cursor-pointer" />
              <span class="text-sm text-primary font-medium">{{ concept.name }}</span>
            </label>
          </div>
        </div>

        <!-- Top Categories -->
        <div class="space-y-4">
          <div v-for="(concepts, cat) in leftPanelConcepts" :key="cat">
            <div v-if="concepts.length > 0">
              <div class="text-xs font-bold text-main/40 mb-1.5 uppercase tracking-widest">{{ cat.split(' ')[0] }}</div>
              <div class="flex flex-col gap-2">
                <label v-for="concept in concepts" :key="concept.id" class="flex items-center gap-2 cursor-pointer group">
                  <input type="checkbox" :checked="false" @change="toggleConcept(concept)" class="w-4 h-4 text-primary border-main/10 rounded focus:ring-primary cursor-pointer" />
                  <span class="text-sm text-main/60 group-hover:text-primary transition-colors">{{ concept.name }}</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <button @click="openModal" class="w-full mt-5 py-2 text-xs font-medium text-primary border border-primary/30 rounded hover:bg-primary/5 transition-colors">
          展開所有標籤
        </button>
      </div>
    </aside>

    <!-- Right Main Panel -->
    <main class="w-full lg:w-11/15 flex flex-col gap-4">

      <!-- Advanced Search Page -->
      <section v-if="isAdvancedMode" class="card !p-5 animate-in fade-in slide-in-from-bottom-2 duration-300">
        <div class="flex items-center justify-between border-b border-main/10 pb-3 mb-4">
          <h2 class="text-base font-bold text-main/50 tracking-widest uppercase">進階搜尋</h2>
          <button @click="isAdvancedMode = false" class="text-xs px-3 py-1 rounded-full border border-main/10 text-main/50 hover:text-primary hover:border-primary/30 transition-colors">
            返回結果列表
          </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <label class="block text-xs font-bold tracking-widest uppercase text-main/40 mb-2">關鍵字</label>
            <input v-model="searchQuery" type="text" placeholder="標題、作者、筆名等" class="w-full h-10 px-3 border border-main/10 rounded bg-bg focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors text-sm text-main" />
          </div>
          <div>
            <label class="block text-xs font-bold tracking-widest uppercase text-main/40 mb-2">發表年份區間</label>
            <div class="flex items-center gap-2">
              <input v-model="yearMin" type="number" placeholder="YYYY" class="w-full h-10 px-3 border border-main/10 rounded bg-bg focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary text-sm text-main" />
              <span class="text-xs text-main/40">至</span>
              <input v-model="yearMax" type="number" placeholder="YYYY" class="w-full h-10 px-3 border border-main/10 rounded bg-bg focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary text-sm text-main" />
            </div>
          </div>
          <div class="space-y-4">
            <div>
              <label class="block text-xs font-bold tracking-widest uppercase text-main/40 mb-2">媒體類型</label>
              <div class="flex flex-wrap gap-4">
                <label v-for="opt in MEDIA_OPTIONS" :key="opt.value" class="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" :value="opt.value" v-model="selectedMedia" class="w-4 h-4 text-primary border-main/10 rounded focus:ring-primary" />
                  <span class="text-sm text-main/60">{{ opt.label }}</span>
                </label>
              </div>
            </div>
            <div>
              <label class="block text-xs font-bold tracking-widest uppercase text-main/40 mb-2">作品篇幅</label>
              <div class="flex flex-wrap gap-4">
                <label v-for="opt in LENGTH_OPTIONS" :key="opt.value" class="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" :value="opt.value" v-model="selectedLengths" class="w-4 h-4 text-primary border-main/10 rounded focus:ring-primary" />
                  <span class="text-sm text-main/60">{{ opt.label }}</span>
                </label>
              </div>
            </div>
          </div>
          <div>
            <label class="block text-xs font-bold tracking-widest uppercase text-main/40 mb-2">概念標籤</label>
            <button @click="openModal" class="w-full text-left px-3 py-2 border border-dashed border-primary/40 rounded text-primary hover:bg-primary/5 transition-colors">
              + 點擊選取概念標籤
            </button>
            <div v-if="selectedConcepts.length > 0" class="mt-3 flex flex-wrap gap-2">
              <span v-for="concept in selectedConcepts" :key="concept.id" class="tag !text-xs !py-1 !px-2.5 !gap-1.5 flex items-center">
                {{ concept.name }}
                <button @click.stop="toggleConcept(concept)" class="flex items-center justify-center w-4 h-4 text-base leading-none hover:text-primary transition-colors">&times;</button>
              </span>
            </div>
          </div>
        </div>

        <div class="mt-8 pt-4 border-t border-main/10 flex justify-end gap-3">
          <button @click="clearAllFilters" class="px-3 py-1 rounded-full border border-transparent text-xs font-medium text-main/50 hover:text-primary transition-colors">清除條件</button>
          <button @click="isAdvancedMode = false" class="px-3 py-1 rounded-full border border-primary bg-primary text-white text-xs font-medium hover:bg-primary/90 transition-colors">
            查看結果 ({{ totalWorks }})
          </button>
        </div>
      </section>

      <!-- Works List Results Page -->
      <template v-else>
        <!-- Active Filters Bar & Sorting -->
        <section class="card !p-5 flex flex-col gap-3">
          <div v-if="selectedConcepts.length || selectedMedia.length || selectedLengths.length || yearMin || yearMax" class="flex flex-wrap items-center gap-2 text-sm pb-3 border-b border-main/5">
            <span class="text-xs font-medium text-main/50 mr-1">作用中篩選：</span>

            <span v-for="m in selectedMedia" :key="m" class="tag !text-xs !py-1 !px-2.5 !gap-1.5 flex items-center">
              {{ MEDIA_OPTIONS.find(o => o.value === m)?.label }}
              <button @click="selectedMedia = selectedMedia.filter(v => v !== m)" class="flex items-center justify-center w-4 h-4 text-base leading-none hover:text-primary transition-colors">&times;</button>
            </span>
            <span v-for="l in selectedLengths" :key="l" class="tag !text-xs !py-1 !px-2.5 !gap-1.5 flex items-center">
              {{ LENGTH_OPTIONS.find(o => o.value === l)?.label }}
              <button @click="selectedLengths = selectedLengths.filter(v => v !== l)" class="flex items-center justify-center w-4 h-4 text-base leading-none hover:text-primary transition-colors">&times;</button>
            </span>
            <span v-for="c in selectedConcepts" :key="c.id" class="tag !text-xs !py-1 !px-2.5 !gap-1.5 flex items-center">
              {{ c.name }}
              <button @click="toggleConcept(c)" class="flex items-center justify-center w-4 h-4 text-base leading-none hover:text-primary transition-colors">&times;</button>
            </span>
            <span v-if="yearMin || yearMax" class="tag !text-xs !py-1 !px-2.5 !gap-1.5 flex items-center">
              {{ yearMin || '...' }} - {{ yearMax || '...' }}
              <button @click="yearMin = ''; yearMax = ''" class="flex items-center justify-center w-4 h-4 text-base leading-none hover:text-primary transition-colors">&times;</button>
            </span>

            <button @click="clearAllFilters" class="ml-auto text-primary hover:text-primary/70 text-xs font-medium">
              清除全部篩選
            </button>
          </div>

          <div class="flex items-center justify-between">
            <div class="text-main/50 text-xs font-medium">
              顯示 <span class="text-primary">{{ totalWorks }}</span> 部作品
            </div>
            <div class="flex items-center gap-2">
              <span class="text-xs text-main/50">排序：</span>
              <select v-model="ordering" class="h-8 px-2 border border-main/10 rounded bg-bg focus:outline-none focus:border-primary text-sm text-main cursor-pointer">
                <option value="-year">年份 (新到舊)</option>
                <option value="year">年份 (舊到新)</option>
                <option value="title">標題排序</option>
                <option value="-updated_at">最近更新</option>
              </select>
            </div>
          </div>
        </section>

        <!-- Works List Content -->
        <div v-if="isLoading" class="card text-center py-12 text-main/50 text-sm font-medium">
          搜尋中...
        </div>
        <div v-else-if="works.length === 0" class="card text-center py-12 text-main/50 text-sm font-medium">
          找不到符合條件的作品。
        </div>
        <div v-else class="space-y-3">
          <div v-for="work in works" :key="work.id" class="card !p-5 flex flex-col md:flex-row md:items-start justify-between gap-4 transition-colors hover:border-primary/30 group">

            <!-- Basic Info Left -->
            <div class="flex-1">
              <router-link :to="`/works/${work.id}`" class="text-base font-medium text-main group-hover:text-primary transition-colors inline-block mb-1.5">
                {{ work.title }}
              </router-link>
              <div class="flex flex-wrap items-center gap-1 text-sm text-main/50">
                <span v-if="work.byline && work.byline.length" class="flex flex-wrap items-center">
                  <template v-for="(agent, idx) in work.byline" :key="idx">
                    <router-link v-if="agent.id" :to="`/agents/${agent.id}`" class="hover:text-primary transition-colors">{{ agent.text }}</router-link>
                    <span v-else>{{ agent.text }}</span>
                    <span v-if="idx < work.byline.length - 1" class="mx-0.5">、</span>
                  </template>
                </span>
                <span v-else>佚名</span>

                <span class="text-main/25">·</span>
                <span>{{ work.year || '未知年份' }}</span>
                <span class="text-main/25">·</span>
                <span>{{ work.work_length_display || '未知篇幅' }}</span>
                <span class="text-main/25">·</span>
                <span>{{ work.media_type_display || '未知媒體' }}</span>
              </div>
            </div>

            <!-- Tags Right -->
            <div class="md:w-5/12 flex-shrink-0 flex flex-wrap justify-start md:justify-end content-start gap-1.5">
              <router-link
                v-for="wc in work.work_concepts"
                :key="wc.concept.slug"
                :to="`/concepts/${wc.concept.slug}`"
                class="tag !text-xs !py-1 !px-2.5"
              >
                {{ wc.concept.name }}
              </router-link>
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

  <!-- Modal for all tags -->
  <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-main/50 backdrop-blur-sm p-4 animate-in fade-in duration-200">
    <div class="bg-bg w-full max-w-4xl max-h-[90vh] rounded-xl shadow-2xl flex flex-col overflow-hidden">

      <div class="p-5 border-b border-main/10 shrink-0 bg-bg relative z-10">
        <h2 class="text-2xl font-bold text-main mb-4">選取概念標籤</h2>
        <input v-model="modalSearchQuery" type="text" placeholder="在此搜尋標籤..." class="w-full h-10 px-3 border border-main/10 rounded bg-bg focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors text-sm text-main" />
        <div class="mt-4 min-h-[40px]">
          <span class="text-xs font-bold tracking-widest uppercase text-main/40 mr-2">已選取：</span>
          <div v-if="tempSelectedConcepts.length === 0" class="inline-block text-sm text-main/25">尚未選取任何標籤</div>
          <div v-else class="inline-flex flex-wrap gap-2 align-middle">
            <span v-for="concept in tempSelectedConcepts" :key="concept.id" class="tag !text-xs !py-1 !px-2.5 !gap-1.5 flex items-center">
              {{ concept.name }}
              <button @click="toggleTempConcept(concept)" class="flex items-center justify-center w-4 h-4 text-base leading-none hover:text-primary transition-colors">&times;</button>
            </span>
          </div>
        </div>
      </div>

      <div class="p-5 overflow-y-auto flex-1 bg-bg">
        <div class="space-y-8">
          <div v-for="cat in CATEGORIES" :key="cat">
            <template v-if="modalGroupedConcepts[cat]?.length > 0">
              <div class="flex items-center gap-3 mb-4">
                <h3 class="text-sm font-bold text-main">{{ cat }}</h3>
                <div class="h-px bg-main/10 flex-1"></div>
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-x-4 gap-y-1">
                <label v-for="concept in modalGroupedConcepts[cat]" :key="concept.id" class="flex items-center gap-2 cursor-pointer group px-2 py-1.5 rounded hover:bg-primary/5 transition-colors">
                  <input
                    type="checkbox"
                    :checked="tempSelectedConcepts.some(c => c.id === concept.id)"
                    @change="toggleTempConcept(concept)"
                    class="w-4 h-4 text-primary border-main/10 rounded focus:ring-primary cursor-pointer shrink-0"
                  />
                  <span class="text-sm text-main/50 group-hover:text-main truncate">{{ concept.name }}</span>
                </label>
              </div>
            </template>
          </div>
        </div>
      </div>

      <div class="p-5 border-t border-main/10 shrink-0 bg-bg flex justify-end gap-3 relative z-10">
        <button @click="closeModal" class="px-3 py-1 rounded-full border border-transparent text-xs font-medium text-main/50 hover:text-primary transition-colors">
          取消
        </button>
        <button @click="applyModalConcepts" class="px-3 py-1 rounded-full border border-primary bg-primary text-white text-xs font-medium hover:bg-primary/90 transition-colors">
          套用篩選
        </button>
      </div>

    </div>
  </div>
</template>
