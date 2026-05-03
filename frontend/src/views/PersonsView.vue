<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import api from '../api/axios'

const agents = ref<any[]>([])
const isLoading = ref(true)

// Search, sort, and pagination states
const searchQuery = ref('')
const sortBy = ref('-updated_at') // Default: recently updated
const currentPage = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)

const fetchAgents = async () => {
  isLoading.value = true
  try {
    const response = await api.get('/agents/', {
      params: {
        page: currentPage.value,
        search: searchQuery.value,
        ordering: sortBy.value
      }
    })

    agents.value = response.data.results || []
    totalCount.value = response.data.count || 0

    // Calculate total pages based on backend's default page size (e.g., 20)
    const pageSize = 20 // Adjust if your DRF default page_size is different
    totalPages.value = Math.ceil(totalCount.value / pageSize) || 1

  } catch (error) {
    console.error('Failed to fetch agents:', error)
  } finally {
    isLoading.value = false
  }
}

// Implement simple debounce for search input to prevent excessive API calls
let searchTimeout: any = null
const onSearchInput = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchAgents()
  }, 300)
}

// When sort order changes, reset to first page and refetch
watch(sortBy, () => {
  currentPage.value = 1
  fetchAgents()
})

// Pagination controls
const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    fetchAgents()
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    fetchAgents()
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

onMounted(() => {
  fetchAgents()
})
</script>

<template>
  <div class="max-w-4xl mx-auto space-y-6">

    <!-- Header Controls -->
    <section class="bg-[#ffffff] rounded-lg p-5 md:p-6 shadow-sm border border-[#2d2016]/10 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl md:text-3xl font-bold text-[#2d2016] tracking-tight mb-1">人物</h1>
        <p class="text-sm md:text-base text-[#2d2016]/60">瀏覽全站收錄的作品相關人物</p>
      </div>

      <div class="flex items-center gap-3 w-full md:w-auto">
        <input
          v-model="searchQuery"
          @input="onSearchInput"
          type="text"
          placeholder="搜尋人物姓名或別名…"
          class="flex-1 md:w-64 h-10 px-3.5 border border-[#2d2016]/20 rounded-lg bg-[#ffffff] focus:outline-none focus:border-[#ae5630] focus:ring-1 focus:ring-[#ae5630] transition-colors text-[#2d2016] placeholder-[#2d2016]/40"
        >
        <select
          v-model="sortBy"
          class="h-10 px-3 border border-[#2d2016]/20 rounded-lg bg-[#ffffff] focus:outline-none focus:border-[#ae5630] focus:ring-1 focus:ring-[#ae5630] transition-colors text-[#2d2016] cursor-pointer"
        >
          <option value="-updated_at">最近更新</option> <!-- Sort by updated_at descending -->
          <option value="name">字母排序</option>       <!-- Sort by name ascending -->
          <option value="-works_count">作品數排序</option> <!-- Sort by works_count descending -->
        </select>
      </div>
    </section>

    <div v-if="isLoading && agents.length === 0" class="text-center py-16 text-[#2d2016]/50 font-medium bg-[#ffffff] rounded-lg border border-[#2d2016]/10">
      正在讀取人物列表...
    </div>

    <!-- Agents List -->
    <div v-else class="space-y-4">
      <div v-if="totalCount > 0" class="text-sm text-[#2d2016]/50 font-medium px-1">
        共找到 {{ totalCount }} 位人物
      </div>

      <div
        v-for="agent in agents"
        :key="agent.id"
        class="bg-[#ffffff] rounded-lg p-5 shadow-sm border border-[#2d2016]/10 hover:border-[#ae5630]/30 transition-colors group cursor-pointer"
        @click="$router.push(`/agents/${agent.id}`)"
      >
        <!-- Name, Aliases and Works Count -->
        <div class="flex flex-wrap items-baseline justify-between gap-3 mb-2">
          <div class="flex items-baseline gap-3 flex-wrap">
            <h2 class="text-xl font-bold text-[#2d2016] group-hover:text-[#ae5630] transition-colors">{{ agent.name }}</h2>
            <span v-if="agent.aliases && agent.aliases.length > 0" class="text-[15px] text-[#2d2016]/50">
              {{ agent.aliases.map(a => a.name).join('、') }}
            </span>
          </div>
          <span class="text-sm font-medium text-[#2d2016]/40 shrink-0">{{ agent.works_count || 0 }} 部作品</span>
        </div>

        <!-- Biography (truncated to 2 lines) -->
        <p class="text-base text-[#2d2016]/70 leading-relaxed mb-4 line-clamp-2">
          {{ agent.about || '暫無簡歷提供。' }}
        </p>

        <!-- Concept Tags -->
        <div v-if="agent.top_concepts && agent.top_concepts.length > 0" class="flex flex-wrap items-center gap-2">
          <router-link
            v-for="concept in agent.top_concepts.slice(0, 5)"
            :key="concept.slug"
            :to="`/concepts/${concept.slug}`"
            class="px-2.5 py-1 bg-transparent border border-[#2d2016]/10 text-[#2d2016]/60 text-xs font-medium rounded-lg hover:bg-[#f5f0e8]/10 hover:border-[#ae5630]/30 hover:text-[#ae5630] transition-all duration-200"
            @click.stop
          >
            {{ concept.name }}
          </router-link>
        </div>
      </div>

      <!-- Pagination Controls -->
      <div v-if="totalPages > 1" class="flex items-center justify-center gap-4 pt-6 pb-4">
        <button @click="prevPage" :disabled="currentPage === 1" class="px-4 py-2 rounded-lg text-sm font-medium transition-colors border" :class="currentPage === 1 ? 'border-[#2d2016]/10 text-[#2d2016]/30 cursor-not-allowed bg-transparent' : 'border-[#2d2016]/20 text-[#2d2016]/70 hover:bg-[#ede8dc] hover:text-[#2d2016] bg-[#ffffff]'">上一頁</button>
        <span class="text-sm font-mono text-[#2d2016]/50">第 {{ currentPage }} / {{ totalPages }} 頁</span>
        <button @click="nextPage" :disabled="currentPage === totalPages" class="px-4 py-2 rounded-lg text-sm font-medium transition-colors border" :class="currentPage === totalPages ? 'border-[#2d2016]/10 text-[#2d2016]/30 cursor-not-allowed bg-transparent' : 'border-[#2d2016]/20 text-[#2d2016]/70 hover:bg-[#ede8dc] hover:text-[#2d2016] bg-[#ffffff]'">下一頁</button>
      </div>
    </div>
  </div>
</template>
