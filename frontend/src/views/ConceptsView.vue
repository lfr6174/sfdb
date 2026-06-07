<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useDocumentMeta } from '../composables/useDocumentTitle'
import BaseSearchInput from '../components/BaseSearchInput.vue'
import { fetchAllConcepts as fetchAllConceptsApi } from '../api/concepts'
import type { Concept } from '../types'
import ConceptTag from '../components/ConceptTag.vue'
import SortSelect from '../components/SortSelect.vue'
import { CONCEPT_CATEGORY_MAP, CONCEPT_CATEGORY_ORDER } from '../utils/constants'

useDocumentMeta('概念探索', '')

const allConcepts = ref<Concept[]>([])
const isLoading = ref(true)

const searchQuery = ref('')
const sortBy = ref('alpha')

const fetchAllConcepts = async () => {
  isLoading.value = true
  try {
    const response = await fetchAllConceptsApi()
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

const groupedConcepts = computed(() => {
  let filtered = allConcepts.value

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    filtered = filtered.filter((c) => c.name.toLowerCase().includes(q))
  }

  // Inter-group sorting
  const groups: Record<string, Concept[]> = {}
  CONCEPT_CATEGORY_ORDER.forEach((cat) => {
    groups[cat] = []
  })

  filtered.forEach((c) => {
    const rawCat = c.category || '未分類'
    const cat = CONCEPT_CATEGORY_MAP[rawCat] || '未分類'
    groups[cat].push(c)
  })

  // Inner-group sorting
  CONCEPT_CATEGORY_ORDER.forEach((cat) => {
    groups[cat].sort((a, b) => {
      if (sortBy.value === 'alpha') return a.name.localeCompare(b.name)
      if (sortBy.value === 'count') return (b.works_count || 0) - (a.works_count || 0)
      if (sortBy.value === 'recent')
        return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
      return 0
    })
  })

  // Skip empty groups
  return Object.fromEntries(Object.entries(groups).filter(([_, concepts]) => concepts.length > 0))
})
</script>
<template>
  <div class="mx-auto max-w-4xl">
    <!-- ── Controls ── -->
    <div class="flex flex-col justify-between gap-4 pt-6 md:flex-row md:items-center md:pt-10">
      <div class="w-full md:w-56">
        <BaseSearchInput
          v-model="searchQuery"
          placeholder="搜尋概念名稱…"
          class="text-main placeholder:text-main/35 border-main/20 focus:border-main/50 w-full border-b bg-transparent py-1.5 pl-6 pr-8 text-sm transition-colors outline-none focus-visible:outline-2 focus-visible:outline-primary/50"
        />
      </div>
      <div class="relative w-28 shrink-0">
        <SortSelect
          v-model="sortBy"
          select-class="text-main/60 border-main/20 focus:border-main/50 w-28 cursor-pointer appearance-none border-b bg-transparent py-1.5 pr-6 pl-1 text-sm transition-colors outline-none focus-visible:outline-2 focus-visible:outline-primary/50"
          :options="[
            { value: 'alpha', label: '字母排序' },
            { value: 'count', label: '作品數排序' },
            { value: 'recent', label: '最近更新' },
          ]"
        />
      </div>
    </div>

    <!-- ── Loading ── -->
    <div
      v-if="isLoading"
      class="text-main/50 animate-pulse py-16 text-center text-base font-medium"
    >
      正在讀取全站概念...
    </div>

    <!-- ── Concept Groups ── -->
    <div
      v-else
      class="pb-20"
    >
      <div
        v-if="Object.keys(groupedConcepts).length > 0"
        class="flex flex-col"
      >
        <div
          v-for="(concepts, category) in groupedConcepts"
          :key="category"
          class="py-8"
        >
          <!-- Category eyebrow, no rule -->
          <span class="text-main/40 mb-5 block text-sm font-medium tracking-widest uppercase">
            {{ category }}
          </span>

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
      <div
        v-else
        class="text-main/50 py-16 text-center text-base"
      >
        找不到任何包含「
        <span class="text-primary">{{ searchQuery }}</span>
        」的概念。
      </div>
    </div>
  </div>
</template>
