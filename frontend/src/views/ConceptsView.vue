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
  <div class="max-w-4xl mx-auto space-y-6">

    <!-- Header Controls -->
    <section class="card flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl md:text-3xl font-bold text-main tracking-tight mb-1">概念探索</h1>
        <p class="text-sm md:text-base text-main/60">瀏覽全站所有的概念</p>
      </div>

      <div class="flex items-center gap-3 w-full md:w-auto">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜尋概念名稱…"
          class="form-input flex-1 md:w-64"
        >
        <select
          v-model="sortBy"
          class="form-select w-full md:w-auto"
        >
          <option value="alpha">字母排序</option>
          <option value="count">作品數排序</option>
          <option value="recent">最近更新</option>
        </select>
      </div>
    </section>

    <div v-if="isLoading" class="card text-center py-16 text-main/50 font-medium">
      正在讀取全站概念...
    </div>

    <!-- Concept Groups -->
    <div v-else class="card md:!p-8">
      <div v-if="Object.keys(groupedConcepts).length > 0" class="flex flex-col gap-8 md:gap-10">
        <template v-for="(concepts, category) in groupedConcepts" :key="category">
          <div class="flex flex-col">
            <!-- 分類標籤：套用模組化 section-label -->
            <h2 class="section-label">{{ category }}</h2>

            <!-- 概念 Chip 雲 -->
            <div class="flex flex-wrap gap-2 md:gap-3">
              <router-link
                v-for="concept in concepts"
                :key="concept.id"
                :to="`/concepts/${concept.slug}`"
                class="tag !rounded-lg flex items-center gap-2"
              >
                <span>{{ concept.name }}</span>
                <span class="text-xs font-mono opacity-60 pt-px">{{ concept.works_count }}</span>
              </router-link>
            </div>
          </div>
        </template>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-10 text-main/50">
        找不到任何包含「<span class="text-primary font-medium">{{ searchQuery }}</span>」的概念。
      </div>
    </div>

  </div>
</template>
