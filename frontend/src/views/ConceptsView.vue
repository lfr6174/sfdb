<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '../api/axios'
import ConceptTag from '../components/ConceptTag.vue'
import SectionTitle from '../components/SectionTitle.vue'

const allConcepts = ref<any[]>([])
const isLoading = ref(true)

const searchQuery = ref('')
const sortBy = ref('alpha')

// Map backend category names to bilingual display formats
const categoryMap: Record<string, string> = {
  'novum': '新異 Novum',
  'narrative': '敘事 Narrative',
  'theme': '主題 Theme',
}

const fetchAllConcepts = async () => {
  isLoading.value = true
  try {
    const response = await api.get('/concepts/all/')
    allConcepts.value = response.data || []
  } catch (error) {
    console.error('Failed to fetch concepts:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchAllConcepts()
})

const GROUP_ORDER = ['新異 Novum', '敘事 Narrative', '主題 Theme', '未分類']

const groupedConcepts = computed(() => {
  let filtered = allConcepts.value

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    filtered = filtered.filter(c => c.name.toLowerCase().includes(q))
  }

  // Inter-group sorting
  const groups: Record<string, any[]> = {}
  GROUP_ORDER.forEach(cat => { groups[cat] = [] })

  filtered.forEach(c => {
    const rawCat = c.category || '未分類'
    const cat = categoryMap[rawCat] || '未分類'
    groups[cat].push(c)
  })

  // Inner-group sorting
  GROUP_ORDER.forEach(cat => {
    groups[cat].sort((a, b) => {
      if (sortBy.value === 'alpha') return a.name.localeCompare(b.name)
      if (sortBy.value === 'count') return (b.works_count || 0) - (a.works_count || 0)
      if (sortBy.value === 'recent') return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
      return 0
    })
  })

  // Skip empty groups
  return Object.fromEntries(
    Object.entries(groups).filter(([_, concepts]) => concepts.length > 0)
  )
})

</script>
<template>
  <div class="max-w-4xl mx-auto">

    <!-- ── Controls ── -->
    <div class="pt-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="搜尋概念名稱…"
        class="text-sm text-main placeholder:text-main/35 bg-transparent border-b border-main/20 px-0 py-1.5 outline-none focus:border-main/50 transition-colors w-full md:w-56"
      >
      <div class="relative shrink-0">
        <select
          v-model="sortBy"
          class="w-28 text-sm text-main/60 bg-transparent border-b border-main/20 pl-1 pr-6 py-1.5 outline-none focus:border-main/50 transition-colors cursor-pointer appearance-none"
        >
          <option value="alpha">字母排序</option>
          <option value="count">作品數排序</option>
          <option value="recent">最近更新</option>
        </select>
        <svg class="pointer-events-none absolute right-1.5 top-1/2 -translate-y-1/2 text-main/35" width="9" height="5" viewBox="0 0 10 6" fill="none">
          <path d="M0 0l5 6 5-6z" fill="currentColor"/>
        </svg>
      </div>
    </div>

    <!-- ── Loading ── -->
    <div v-if="isLoading" class="text-center py-16 text-main/50 text-base font-medium">
      正在讀取全站概念...
    </div>

    <!-- ── Concept Groups ── -->
    <div v-else class="pb-20">
      <div v-if="Object.keys(groupedConcepts).length > 0" class="flex flex-col">
        <div
          v-for="(concepts, category) in groupedConcepts"
          :key="category"
          class="py-8"
        >
          <!-- Category eyebrow, no rule -->
          <span class="mb-5 block text-sm font-medium tracking-widest uppercase text-main/40">{{ category }}</span>

          <!-- Tag cloud -->
          <div class="flex flex-wrap gap-1.5">
            <ConceptTag
              v-for="concept in concepts"
              :key="concept.id"
              :concept="concept"
              size="md"
            />
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-16 text-base text-main/50">
        找不到任何包含「<span class="text-primary">{{ searchQuery }}</span>」的概念。
      </div>
    </div>

  </div>
</template>
