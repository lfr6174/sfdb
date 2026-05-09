<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import api from '../api/axios'
import PaginationControls from '../components/PaginationControls.vue'

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

const changePage = (dir: number) => {
  currentPage.value += dir
  fetchAgents()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  fetchAgents()
})
</script>

<template>
  <div class="max-w-4xl mx-auto">

    <!-- ── Page Header ── -->
    <div class="pt-10">
      <div class="flex flex-col md:flex-row md:items-end justify-between gap-5">
        <div>
          <h1 class="text-3xl font-normal text-main leading-tight mb-1">人物</h1>
          <p class="text-base text-main/50">瀏覽全站收錄的作品相關人物</p>
        </div>

        <div class="flex items-center gap-2">
          <input
            v-model="searchQuery"
            @input="onSearchInput"
            type="text"
            placeholder="搜尋姓名或別名…"
            class="text-base text-main placeholder:text-main/40 bg-transparent border border-main/15 px-3 py-2 outline-none focus:border-primary/50 transition-colors w-48 md:w-56"
          >
          <div class="relative">
            <select
              v-model="sortBy"
              class="text-base text-main/70 bg-transparent border border-main/15 px-3 py-2 pr-7 outline-none focus:border-primary/50 transition-colors cursor-pointer appearance-none"
            >
              <option value="-updated_at">最近更新</option>
              <option value="name">字母排序</option>
              <option value="-works_count">作品數排序</option>
            </select>
            <svg class="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 text-main/40" width="10" height="6" viewBox="0 0 10 6" fill="none">
              <path d="M0 0l5 6 5-6z" fill="currentColor"/>
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Loading ── -->
    <div v-if="isLoading && agents.length === 0" class="text-center py-16 text-main/50 text-base font-medium">
      正在讀取人物列表...
    </div>

    <!-- ── List ── -->
    <div v-else class="pb-20">

      <!-- Count -->
      <div v-if="totalCount > 0" class="flex items-center gap-3 mt-6 mb-1">
        <span class="text-sm font-medium tracking-widest uppercase text-main/40 whitespace-nowrap">
          共 {{ totalCount }} 位人物
        </span>
        <div class="flex-1 border-t border-main/10"></div>
      </div>

      <!-- Agent Rows -->
      <div
        v-for="agent in agents"
        :key="agent.id"
        class="group py-5 border-b border-main/10 cursor-pointer hover:bg-primary/5 hover:-mx-4 hover:px-4 transition-colors"
        @click="$router.push(`/agents/${agent.id}`)"
      >
        <!-- Name row -->
        <div class="flex flex-wrap items-baseline justify-between gap-3 mb-1.5">
          <div class="flex items-baseline gap-2.5 flex-wrap">
            <span class="text-xl font-medium text-main group-hover:text-primary transition-colors">{{ agent.name }}</span>
            <span v-if="agent.aliases && agent.aliases.length > 0" class="text-base text-main/40">
              {{ agent.aliases.map(a => a.name).join(' · ') }}
            </span>
          </div>
          <span class="font-mono text-sm text-main/40 shrink-0">{{ agent.works_count || 0 }} 部作品</span>
        </div>

        <!-- Bio -->
        <p class="text-base text-main/70 leading-relaxed mb-3.5 line-clamp-2">
          {{ agent.about || '暫無簡歷提供。' }}
        </p>

        <!-- Concept Tags -->
        <div v-if="agent.top_concepts && agent.top_concepts.length > 0" class="flex flex-wrap gap-1.5">
          <router-link
            v-for="concept in agent.top_concepts.slice(0, 5)"
            :key="concept.slug"
            :to="`/concepts/${concept.slug}`"
            class="inline-flex items-center text-xs text-main/60 border border-main/15 px-2.5 py-1 hover:text-primary hover:bg-primary/5 hover:border-primary/30 transition-all whitespace-nowrap no-underline"
            @click.stop
          >
            {{ concept.name }}
          </router-link>
        </div>
      </div>

      <!-- Pagination -->
      <PaginationControls
        v-if="totalPages > 1"
        :current-page="currentPage"
        :total-pages="totalPages"
        :has-prev="currentPage > 1"
        :has-next="currentPage < totalPages"
        @change-page="changePage"
      />
    </div>

  </div>
</template>
