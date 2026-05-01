<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'

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

const getUniqueCredits = (contributions: any[]) => {
  if (!contributions) return []
  const seen = new Set()
  return contributions.filter(c => {
    if (!c.agent_detail) return false
    if (seen.has(c.agent_detail.id)) return false
    seen.add(c.agent_detail.id)
    return true
  })
}

const changePage = (dir: number) => {
  currentPage.value += dir
  fetchWorks()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<template>
  <div class="max-w-5xl mx-auto flex flex-col lg:flex-row gap-6 items-start pb-12">

    <!-- Left Control Panel -->
    <aside class="w-full lg:w-3/12 bg-[#ffffff] rounded-lg shadow-sm border border-[#2d2016]/10 p-5 shrink-0 lg:sticky lg:top-4">
      <!-- Search -->
      <div class="mb-4">
        <input v-model="searchQuery" type="text" placeholder="搜尋標題、作者、筆名..." class="w-full h-10 px-3 border border-[#2d2016]/20 rounded bg-[#ffffff] focus:outline-none focus:border-[#ae5630] focus:ring-1 focus:ring-[#ae5630] transition-colors text-[#2d2016] placeholder-[#2d2016]/40" />
        <button @click="isAdvancedMode = !isAdvancedMode" class="w-full mt-2 py-2 text-sm font-medium text-[#2d2016]/70 border border-[#2d2016]/20 rounded hover:bg-[#ede8dc] hover:text-[#2d2016] transition-colors">
          {{ isAdvancedMode ? '返回一般結果' : '進階搜索' }}
        </button>
      </div>

      <!-- Media & Length Filters -->
      <div class="mb-6 space-y-4">
        <div>
          <h3 class="text-sm font-bold text-[#2d2016]/50 mb-2">作品媒體</h3>
          <div class="flex flex-col gap-2">
            <label v-for="opt in MEDIA_OPTIONS" :key="opt.value" class="flex items-center gap-2 cursor-pointer group">
              <input type="checkbox" :value="opt.value" v-model="selectedMedia" class="w-4 h-4 text-[#ae5630] border-[#2d2016]/20 rounded focus:ring-[#ae5630] cursor-pointer" />
              <span class="text-[15px] text-[#2d2016]/80 group-hover:text-[#2d2016]">{{ opt.label }}</span>
            </label>
          </div>
        </div>
        <div>
          <h3 class="text-sm font-bold text-[#2d2016]/50 mb-2">作品篇幅</h3>
          <div class="flex flex-col gap-2">
            <label v-for="opt in LENGTH_OPTIONS" :key="opt.value" class="flex items-center gap-2 cursor-pointer group">
              <input type="checkbox" :value="opt.value" v-model="selectedLengths" class="w-4 h-4 text-[#ae5630] border-[#2d2016]/20 rounded focus:ring-[#ae5630] cursor-pointer" />
              <span class="text-[15px] text-[#2d2016]/80 group-hover:text-[#2d2016]">{{ opt.label }}</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Concept Tags Section -->
      <div>
        <h3 class="text-sm font-bold text-[#2d2016]/50 mb-3">概念標籤</h3>

        <!-- Selected Tags -->
        <div v-if="selectedConcepts.length > 0" class="mb-4 p-3 bg-[#2d2016]/5 rounded-md border border-[#2d2016]/10">
          <div class="text-[13px] font-bold text-[#2d2016]/40 mb-2 uppercase">已勾選</div>
          <div class="flex flex-col gap-2">
            <label v-for="concept in selectedConcepts" :key="concept.id" class="flex items-center gap-2 cursor-pointer group">
              <input type="checkbox" :checked="true" @change="toggleConcept(concept)" class="w-4 h-4 text-[#ae5630] border-[#2d2016]/20 rounded focus:ring-[#ae5630] cursor-pointer" />
              <span class="text-[15px] text-[#ae5630] font-medium">{{ concept.name }}</span>
            </label>
          </div>
        </div>

        <!-- Top Categories -->
        <div class="space-y-4">
          <div v-for="(concepts, cat) in leftPanelConcepts" :key="cat">
            <div v-if="concepts.length > 0">
              <div class="text-[13px] font-bold text-[#2d2016]/40 mb-1.5 uppercase">{{ cat.split(' ')[0] }}</div>
              <div class="flex flex-col gap-2">
                <label v-for="concept in concepts" :key="concept.id" class="flex items-center gap-2 cursor-pointer group">
                  <input type="checkbox" :checked="false" @change="toggleConcept(concept)" class="w-4 h-4 text-[#ae5630] border-[#2d2016]/20 rounded focus:ring-[#ae5630] cursor-pointer" />
                  <span class="text-[15px] text-[#2d2016]/80 group-hover:text-[#2d2016]">{{ concept.name }}</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <button @click="openModal" class="w-full mt-5 py-2 text-sm font-medium text-[#ae5630] border border-[#ae5630]/30 rounded hover:bg-[#ae5630]/5 transition-colors">
          展開所有標籤
        </button>
      </div>
    </aside>

    <!-- Right Main Panel -->
    <main class="w-full lg:w-9/12 flex flex-col gap-4">

      <!-- Advanced Search Page -->
      <section v-if="isAdvancedMode" class="bg-[#ffffff] rounded-lg p-6 shadow-sm border border-[#2d2016]/10 animate-in fade-in slide-in-from-bottom-2 duration-300">
        <div class="flex items-center justify-between border-b border-[#2d2016]/10 pb-4 mb-6">
          <h2 class="text-2xl font-bold text-[#2d2016] tracking-tight">進階搜尋</h2>
          <button @click="isAdvancedMode = false" class="text-sm px-4 py-1.5 bg-[#ede8dc] text-[#2d2016] rounded hover:bg-[#2d2016]/10 transition-colors">
            返回結果列表
          </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <label class="block text-sm font-bold text-[#2d2016]/50 mb-2">關鍵字</label>
            <input v-model="searchQuery" type="text" placeholder="標題、作者、筆名等" class="w-full h-10 px-3 border border-[#2d2016]/20 rounded bg-[#ffffff] focus:outline-none focus:border-[#ae5630] focus:ring-1 focus:ring-[#ae5630] transition-colors" />
          </div>
          <div>
            <label class="block text-sm font-bold text-[#2d2016]/50 mb-2">發表年份區間</label>
            <div class="flex items-center gap-2">
              <input v-model="yearMin" type="number" placeholder="YYYY" class="w-full h-10 px-3 border border-[#2d2016]/20 rounded bg-[#ffffff] focus:outline-none focus:border-[#ae5630] focus:ring-1 focus:ring-[#ae5630]" />
              <span class="text-[#2d2016]/40">至</span>
              <input v-model="yearMax" type="number" placeholder="YYYY" class="w-full h-10 px-3 border border-[#2d2016]/20 rounded bg-[#ffffff] focus:outline-none focus:border-[#ae5630] focus:ring-1 focus:ring-[#ae5630]" />
            </div>
          </div>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-bold text-[#2d2016]/50 mb-2">媒體類型</label>
              <div class="flex flex-wrap gap-4">
                <label v-for="opt in MEDIA_OPTIONS" :key="opt.value" class="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" :value="opt.value" v-model="selectedMedia" class="w-4 h-4 text-[#ae5630] border-[#2d2016]/20 rounded focus:ring-[#ae5630]" />
                  <span class="text-[15px] text-[#2d2016]/80">{{ opt.label }}</span>
                </label>
              </div>
            </div>
            <div>
              <label class="block text-sm font-bold text-[#2d2016]/50 mb-2">作品篇幅</label>
              <div class="flex flex-wrap gap-4">
                <label v-for="opt in LENGTH_OPTIONS" :key="opt.value" class="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" :value="opt.value" v-model="selectedLengths" class="w-4 h-4 text-[#ae5630] border-[#2d2016]/20 rounded focus:ring-[#ae5630]" />
                  <span class="text-[15px] text-[#2d2016]/80">{{ opt.label }}</span>
                </label>
              </div>
            </div>
          </div>
          <div>
            <label class="block text-sm font-bold text-[#2d2016]/50 mb-2">概念標籤</label>
            <button @click="openModal" class="w-full text-left px-3 py-2 border border-dashed border-[#ae5630]/40 rounded text-[#ae5630] hover:bg-[#ae5630]/5 transition-colors">
              + 點擊選取概念標籤
            </button>
            <!-- FIX: consistent tag bubble style matching right panel -->
            <div v-if="selectedConcepts.length > 0" class="mt-3 flex flex-wrap gap-2">
              <span v-for="concept in selectedConcepts" :key="concept.id" class="px-2.5 py-1 rounded-full bg-[#f5f0e8] border border-[#2d2016]/10 text-[#2d2016]/60 text-sm font-medium flex items-center gap-1.5">
                {{ concept.name }}
                <!-- FIX: larger × button for easier tapping -->
                <button @click.stop="toggleConcept(concept)" class="flex items-center justify-center w-4 h-4 text-base leading-none hover:text-[#ae5630] transition-colors">&times;</button>
              </span>
            </div>
          </div>
        </div>

        <div class="mt-8 pt-4 border-t border-[#2d2016]/10 flex justify-end gap-3">
          <button @click="clearAllFilters" class="px-5 py-2 text-[#2d2016]/60 hover:text-[#2d2016] transition-colors">清除條件</button>
          <button @click="isAdvancedMode = false" class="px-6 py-2 bg-[#ae5630] text-white rounded hover:bg-[#ae5630]/90 transition-colors shadow-sm">
            查看結果 ({{ totalWorks }})
          </button>
        </div>
      </section>

      <!-- Works List Results Page -->
      <template v-else>
        <!-- Active Filters Bar & Sorting -->
        <section class="bg-[#ffffff] rounded-lg p-4 shadow-sm border border-[#2d2016]/10 flex flex-col gap-3">
          <div v-if="selectedConcepts.length || selectedMedia.length || selectedLengths.length || yearMin || yearMax" class="flex flex-wrap items-center gap-2 text-sm pb-3 border-b border-[#2d2016]/5">
            <span class="text-[#2d2016]/50 font-bold mr-1">作用中篩選：</span>

            <span v-for="m in selectedMedia" :key="m" class="px-2 py-0.5 rounded-full bg-[#f5f0e8] border border-[#2d2016]/10 text-[#2d2016]/60 flex items-center gap-1.5">
              {{ MEDIA_OPTIONS.find(o => o.value === m)?.label }}
              <button @click="selectedMedia = selectedMedia.filter(v => v !== m)" class="flex items-center justify-center w-4 h-4 text-base leading-none hover:text-[#ae5630] transition-colors">&times;</button>
            </span>
            <span v-for="l in selectedLengths" :key="l" class="px-2 py-0.5 rounded-full bg-[#f5f0e8] border border-[#2d2016]/10 text-[#2d2016]/60 flex items-center gap-1.5">
              {{ LENGTH_OPTIONS.find(o => o.value === l)?.label }}
              <button @click="selectedLengths = selectedLengths.filter(v => v !== l)" class="flex items-center justify-center w-4 h-4 text-base leading-none hover:text-[#ae5630] transition-colors">&times;</button>
            </span>
            <!-- FIX: consistent tag bubble style for selected concepts -->
            <span v-for="c in selectedConcepts" :key="c.id" class="px-2 py-0.5 rounded-full bg-[#f5f0e8] border border-[#2d2016]/10 text-[#2d2016]/60 flex items-center gap-1.5">
              {{ c.name }}
              <button @click="toggleConcept(c)" class="flex items-center justify-center w-4 h-4 text-base leading-none hover:text-[#ae5630] transition-colors">&times;</button>
            </span>
            <span v-if="yearMin || yearMax" class="px-2 py-0.5 rounded-full bg-[#f5f0e8] border border-[#2d2016]/10 text-[#2d2016]/60 flex items-center gap-1.5">
              {{ yearMin || '...' }} - {{ yearMax || '...' }}
              <button @click="yearMin = ''; yearMax = ''" class="flex items-center justify-center w-4 h-4 text-base leading-none hover:text-[#ae5630] transition-colors">&times;</button>
            </span>

            <button @click="clearAllFilters" class="ml-auto text-[#ae5630] hover:underline text-[13px]">
              清除全部篩選
            </button>
          </div>

          <div class="flex items-center justify-between">
            <div class="text-[#2d2016]/70 font-medium">
              顯示 <span class="text-[#ae5630] font-bold">{{ totalWorks }}</span> 部作品
            </div>
            <div class="flex items-center gap-2">
              <span class="text-sm text-[#2d2016]/50">排序：</span>
              <select v-model="ordering" class="h-8 px-2 border border-[#2d2016]/20 rounded bg-[#ffffff] focus:outline-none focus:border-[#ae5630] text-sm text-[#2d2016] cursor-pointer">
                <option value="-year">年份 (新到舊)</option>
                <option value="year">年份 (舊到新)</option>
                <option value="title">標題排序</option>
                <option value="-updated_at">最近更新</option>
              </select>
            </div>
          </div>
        </section>

        <!-- Works List Content -->
        <div v-if="isLoading" class="py-12 text-center text-[#2d2016]/50 font-medium bg-[#ffffff] rounded-lg shadow-sm border border-[#2d2016]/10">
          搜尋中...
        </div>
        <div v-else-if="works.length === 0" class="py-12 text-center text-[#2d2016]/50 font-medium bg-[#ffffff] rounded-lg shadow-sm border border-[#2d2016]/10">
          找不到符合條件的作品。
        </div>
        <div v-else class="space-y-3">
          <div v-for="work in works" :key="work.id" class="bg-[#ffffff] rounded-lg p-4 md:p-5 shadow-sm border border-[#2d2016]/10 flex flex-col md:flex-row md:items-start justify-between gap-4 transition-all hover:border-[#ae5630]/30 hover:shadow-md group">

            <!-- Basic Info Left -->
            <div class="flex-1">
              <router-link :to="`/works/${work.id}`" class="text-xl font-bold text-[#2d2016] group-hover:text-[#ae5630] transition-colors inline-block mb-1.5">
                {{ work.title }}
              </router-link>
              <!-- FIX: removed px padding from · separators to tighten spacing -->
              <div class="flex flex-wrap items-center gap-1 text-[15px] text-[#2d2016]/70 font-medium">
                <span v-if="getUniqueCredits(work.contributions).length > 0" class="flex flex-wrap items-center">
                  <span v-for="(credit, cIdx) in getUniqueCredits(work.contributions)" :key="credit.id">
                    <router-link :to="`/agents/${credit.agent_detail.id}`" class="hover:text-[#ae5630] transition-colors">{{ credit.display_name || credit.agent_detail.name }}</router-link>
                    <span v-if="cIdx < getUniqueCredits(work.contributions).length - 1" class="mx-0.5">、</span>
                  </span>
                </span>
                <span v-else>{{ work.byline || '佚名' }}</span>

                <span class="text-[#2d2016]/30">·</span>
                <span>{{ work.year || '未知年份' }}</span>
                <span class="text-[#2d2016]/30">·</span>
                <span>{{ work.work_length_display || '未知篇幅' }}</span>
                <span class="text-[#2d2016]/30">·</span>
                <span>{{ work.media_type_display || '未知媒體' }}</span>
              </div>
            </div>

            <!-- Tags Right -->
            <div class="md:w-5/12 flex-shrink-0 flex flex-wrap justify-start md:justify-end content-start gap-1.5">
              <router-link
                v-for="wc in work.work_concepts"
                :key="wc.concept_detail.slug"
                :to="`/concepts/${wc.concept_detail.slug}`"
                class="px-2.5 py-1 bg-[#f5f0e8]/10 border border-[#2d2016]/10 text-[#2d2016]/60 text-sm font-medium rounded hover:bg-[#f5f0e8]/10 hover:border-[#ae5630]/30 hover:text-[#ae5630] transition-all"
              >
                {{ wc.concept_detail.name }}
              </router-link>
            </div>
          </div>
        </div>

        <!-- FIX: Pagination with current page and total pages display -->
        <div v-if="works.length > 0 && (hasPrev || hasNext)" class="flex items-center justify-center gap-4 mt-4">
          <button :disabled="!hasPrev" @click="changePage(-1)" class="px-5 py-2 rounded-lg font-medium transition-colors border border-[#2d2016]/20" :class="hasPrev ? 'bg-[#ffffff] text-[#2d2016] hover:bg-[#ede8dc]' : 'bg-[#f5f0e8] text-[#2d2016]/30 cursor-not-allowed'">
            上一頁
          </button>
          <span class="text-sm text-[#2d2016]/60 font-medium tabular-nums">
            第 <span class="text-[#2d2016] font-bold">{{ currentPage }}</span> / <span class="text-[#2d2016] font-bold">{{ totalPages }}</span> 頁
          </span>
          <button :disabled="!hasNext" @click="changePage(1)" class="px-5 py-2 rounded-lg font-medium transition-colors border border-[#2d2016]/20" :class="hasNext ? 'bg-[#ffffff] text-[#2d2016] hover:bg-[#ede8dc]' : 'bg-[#f5f0e8] text-[#2d2016]/30 cursor-not-allowed'">
            下一頁
          </button>
        </div>
      </template>
    </main>
  </div>

  <!-- Modal for all tags -->
  <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-[#2d2016]/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
    <div class="bg-[#ffffff] w-full max-w-5xl max-h-[90vh] rounded-xl shadow-2xl flex flex-col overflow-hidden">

      <div class="p-5 border-b border-[#2d2016]/10 shrink-0 bg-[#ffffff] relative z-10">
        <h2 class="text-2xl font-bold text-[#2d2016] tracking-tight mb-4">選取概念標籤</h2>
        <input v-model="modalSearchQuery" type="text" placeholder="在此搜尋標籤..." class="w-full h-11 px-4 border border-[#2d2016]/20 rounded-lg bg-[#ffffff] focus:outline-none focus:border-[#ae5630] focus:ring-1 focus:ring-[#ae5630] transition-colors text-lg" />
        <div class="mt-4 min-h-[40px]">
          <span class="text-sm font-bold text-[#2d2016]/50 mr-2">已選取：</span>
          <div v-if="tempSelectedConcepts.length === 0" class="inline-block text-sm text-[#2d2016]/40">尚未選取任何標籤</div>
          <!-- FIX: consistent tag bubble style + larger × -->
          <div v-else class="inline-flex flex-wrap gap-2 align-middle">
            <span v-for="concept in tempSelectedConcepts" :key="concept.id" class="px-2.5 py-1 rounded-full bg-[#f5f0e8] border border-[#2d2016]/10 text-[#2d2016]/60 text-[15px] font-medium flex items-center gap-1.5">
              {{ concept.name }}
              <button @click="toggleTempConcept(concept)" class="flex items-center justify-center w-4 h-4 text-base leading-none text-[#2d2016]/40 hover:text-[#ae5630] transition-colors">&times;</button>
            </span>
          </div>
        </div>
      </div>

      <div class="p-5 overflow-y-auto flex-1 bg-[#ffffff]">
        <div class="space-y-8">
          <div v-for="cat in CATEGORIES" :key="cat">
            <template v-if="modalGroupedConcepts[cat]?.length > 0">
              <div class="flex items-center gap-3 mb-4">
                <h3 class="text-lg font-bold text-[#2d2016]">{{ cat }}</h3>
                <div class="h-px bg-[#2d2016]/10 flex-1"></div>
              </div>
              <!-- FIX: concept cards are transparent — no visible card, just checkbox + text -->
              <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-x-4 gap-y-1">
                <label v-for="concept in modalGroupedConcepts[cat]" :key="concept.id" class="flex items-center gap-2 cursor-pointer group px-2 py-1.5 rounded hover:bg-[#f5f0e8]/30 transition-colors">
                  <input
                    type="checkbox"
                    :checked="tempSelectedConcepts.some(c => c.id === concept.id)"
                    @change="toggleTempConcept(concept)"
                    class="w-4 h-4 text-[#ae5630] border-[#2d2016]/20 rounded focus:ring-[#ae5630] cursor-pointer shrink-0"
                  />
                  <span class="text-[15px] text-[#2d2016]/80 group-hover:text-[#2d2016] truncate">{{ concept.name }}</span>
                </label>
              </div>
            </template>
          </div>
        </div>
      </div>

      <div class="p-5 border-t border-[#2d2016]/10 shrink-0 bg-[#ffffff] flex justify-end gap-3 relative z-10">
        <!-- FIX: was calling undefined closeModal, now correctly defined and called -->
        <button @click="closeModal" class="px-6 py-2.5 text-[#2d2016]/70 border border-[#2d2016]/20 rounded hover:bg-[#ede8dc] transition-colors font-medium">
          取消
        </button>
        <button @click="applyModalConcepts" class="px-8 py-2.5 bg-[#ae5630] text-white rounded hover:bg-[#ae5630]/90 transition-colors font-medium shadow-sm">
          套用篩選
        </button>
      </div>

    </div>
  </div>
</template>
