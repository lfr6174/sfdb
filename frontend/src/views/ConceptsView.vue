<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '../api/axios'

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
  <div class="max-w-5xl mx-auto space-y-6">

    <!-- Header Controls -->
    <section class="bg-[#ffffff] rounded-lg p-5 md:p-6 shadow-sm border border-[#2d2016]/10 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl md:text-3xl font-bold text-[#2d2016] tracking-tight mb-1">概念探索</h1>
        <p class="text-sm md:text-base text-[#2d2016]/60">瀏覽全站所有的概念</p>
      </div>

      <div class="flex items-center gap-3 w-full md:w-auto">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜尋概念名稱…"
          class="flex-1 md:w-64 h-10 px-3.5 border border-[#2d2016]/20 rounded-lg bg-[#ffffff] focus:bg-[#ffffff] focus:outline-none focus:border-[#ae5630] focus:ring-1 focus:ring-[#ae5630] transition-colors text-[#2d2016] placeholder-[#2d2016]/40"
        >
        <select
          v-model="sortBy"
          class="h-10 px-3 border border-[#2d2016]/20 rounded-lg bg-[#ffffff] focus:outline-none focus:border-[#ae5630] focus:ring-1 focus:ring-[#ae5630] transition-colors text-[#2d2016] cursor-pointer"
        >
          <option value="alpha">字母排序</option>
          <option value="count">作品數排序</option>
          <option value="recent">最近更新</option>
        </select>
      </div>
    </section>

    <div v-if="isLoading" class="text-center py-16 text-[#2d2016]/50 font-medium bg-[#ffffff] rounded-lg border border-[#2d2016]/10">
      正在讀取全站概念...
    </div>

    <!-- Concept Groups -->
    <div v-else class="space-y-6">
      <section
        v-for="(concepts, category) in groupedConcepts"
        :key="category"
        class="bg-[#ffffff] rounded-lg p-5 md:p-6 shadow-sm border border-[#2d2016]/10"
      >
        <div class="flex items-baseline gap-3 mb-5 border-b border-[#2d2016]/5 pb-3">
          <h2 class="text-xl md:text-2xl font-bold text-[#2d2016] tracking-tight">{{ category }}</h2>
          <span class="text-sm text-[#2d2016]/50 font-mono">{{ concepts.length }}</span>
        </div>

        <div v-if="concepts.length > 0" class="flex flex-wrap gap-2.5 md:gap-3">
          <router-link
            v-for="concept in concepts"
            :key="concept.id"
            :to="`/concepts/${concept.slug}`"
            class="group flex items-center gap-1.5 px-3 py-1.5 bg-transparent border border-[#2d2016]/10 text-[#2d2016]/60 text-base font-medium rounded-lg cursor-pointer hover:bg-[#f5f0e8]/10 hover:border-[#ae5630]/30 hover:text-[#ae5630] transition-all duration-200"
          >
            <span>{{ concept.name }}</span>
            <span class="text-[13px] font-mono text-[#2d2016]/40 group-hover:text-[#ae5630]/60 transition-colors">{{ concept.works_count }}</span>
          </router-link>
        </div>

        <div v-else class="text-[#2d2016]/40 py-2">
          此分類下沒有符合搜尋條件的概念。
        </div>
      </section>

      <!-- Empty State -->
      <div v-if="Object.keys(groupedConcepts).length === 0" class="text-center py-16 text-[#2d2016]/50 bg-[#ffffff] rounded-lg border border-[#2d2016]/10">
        找不到任何包含「<span class="text-[#ae5630] font-medium">{{ searchQuery }}</span>」的概念。
      </div>
    </div>

  </div>
</template>
