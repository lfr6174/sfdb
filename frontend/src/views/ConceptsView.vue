<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useDocumentMeta } from '../composables/useDocumentTitle'
import BaseSearchInput from '../components/BaseSearchInput.vue'
import { fetchAllConcepts as fetchAllConceptsApi } from '../api/concepts'
import type { Concept } from '../types'
import ConceptTag from '../components/ConceptTag.vue'
import ListState from '../components/ListState.vue'
import SkeletonList from '../components/SkeletonList.vue'
import SortSelect from '../components/SortSelect.vue'
import { categoryOrder } from '../utils/constants'

useDocumentMeta('概念探索', '')

const allConcepts = ref<Concept[]>([])
const isLoading = ref(true)
const hasError = ref(false)

const searchQuery = ref('')
const sortBy = ref('count')

const fetchAllConcepts = async () => {
  isLoading.value = true
  hasError.value = false
  try {
    const response = await fetchAllConceptsApi()
    allConcepts.value = response.data || []
  } catch (error) {
    console.error('Failed to fetch concepts:', error)
    hasError.value = true
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

  // Group by the API's category_display: whatever categories arrive get a
  // group, so a future backend category shows up without frontend changes.
  const groups: Record<string, Concept[]> = {}
  filtered.forEach((c) => {
    if (!groups[c.category_display]) groups[c.category_display] = []
    groups[c.category_display].push(c)
  })

  // Inner-group sorting
  for (const concepts of Object.values(groups)) {
    concepts.sort((a, b) => {
      if (sortBy.value === 'alpha') return a.name.localeCompare(b.name)
      if (sortBy.value === 'count') return (b.works_count || 0) - (a.works_count || 0)
      if (sortBy.value === 'recent')
        return new Date(b.updated_at || 0).getTime() - new Date(a.updated_at || 0).getTime()
      return 0
    })
  }

  // Known categories in fixed order, unknown ones last
  return Object.fromEntries(
    Object.entries(groups).sort(([a], [b]) => categoryOrder(a) - categoryOrder(b)),
  )
})
</script>
<template>
  <div class="mx-auto max-w-4xl">
    <!-- Controls -->
    <div class="flex flex-col justify-between gap-4 pt-6 md:flex-row md:items-center md:pt-10">
      <div class="w-full md:w-56">
        <BaseSearchInput
          v-model="searchQuery"
          placeholder="搜尋概念名稱…"
        />
      </div>
      <div class="relative w-28 shrink-0">
        <SortSelect
          v-model="sortBy"
          select-class="text-main/60 border-main/20 focus:border-main/50 w-28 cursor-pointer appearance-none border-b bg-transparent py-1.5 pr-6 pl-1 text-sm transition-colors outline-none focus-visible:outline-2 focus-visible:outline-primary/50"
          :options="[
            { value: 'count', label: '作品數排序' },
            { value: 'recent', label: '最近更新' },
            { value: 'alpha', label: '字母排序' },
          ]"
        />
      </div>
    </div>

    <!-- Loading / Error / Concept Groups -->
    <ListState
      :loading="isLoading"
      :error="hasError"
    >
      <template #loading>
        <SkeletonList
          variant="tags"
          :tags="24"
        />
      </template>
      <div class="pb-20">
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
    </ListState>
  </div>
</template>
