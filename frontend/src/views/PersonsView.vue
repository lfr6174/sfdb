<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import api from '../api/axios'
import PaginationControls from '../components/PaginationControls.vue'
import { useDebounceFn } from '../composables/useDebounce'

const persons = ref<any[]>([])
const isLoading = ref(true)

// Search, sort, and pagination states
const searchQuery = ref('')
const sortBy = ref('name') // Default: name
const currentPage = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)

const fetchPersons = async () => {
  isLoading.value = true
  try {
    const response = await api.get('/persons/', {
      params: {
        page: currentPage.value,
        search: searchQuery.value,
        ordering: sortBy.value,
      },
    })

    persons.value = response.data.results || []
    totalCount.value = response.data.count || 0

    // Calculate total pages based on backend's default page size (e.g., 20)
    const pageSize = 20 // Adjust if your DRF default page_size is different
    totalPages.value = Math.ceil(totalCount.value / pageSize) || 1
  } catch (error) {
    console.error('Failed to fetch persons:', error)
  } finally {
    isLoading.value = false
  }
}

// Implement simple debounce for search input to prevent excessive API calls
const onSearchInput = useDebounceFn(() => {
  currentPage.value = 1
  fetchPersons()
}, 300)

// When sort order changes, reset to first page and refetch
watch(sortBy, () => {
  currentPage.value = 1
  fetchPersons()
})

const changePage = (dir: number) => {
  currentPage.value += dir
  fetchPersons()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  fetchPersons()
})
</script>

<template>
  <div class="mx-auto max-w-4xl">
    <!-- ── Controls ── -->
    <div class="flex flex-col justify-between gap-4 pt-10 pb-8 md:flex-row md:items-center">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="搜尋姓名、別名或簡介…"
        class="text-main placeholder:text-main/35 border-main/20 focus:border-main/50 w-full border-b bg-transparent px-0 py-1.5 text-sm transition-colors outline-none md:w-56"
        @input="onSearchInput"
      />
      <div class="relative shrink-0">
        <select
          v-model="sortBy"
          class="text-main/60 border-main/20 focus:border-main/50 w-28 cursor-pointer appearance-none border-b bg-transparent py-1.5 pr-6 pl-1 text-sm transition-colors outline-none"
        >
          <option value="name">字母排序</option>
          <option value="-updated_at">最近更新</option>
        </select>
        <svg
          class="text-main/35 pointer-events-none absolute top-1/2 right-1.5 -translate-y-1/2"
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

    <!-- ── Loading ── -->
    <div
      v-if="isLoading && persons.length === 0"
      class="text-main/50 py-16 text-center text-base font-medium"
    >
      正在讀取人物列表...
    </div>

    <!-- ── List ── -->
    <div
      v-else
      class="pb-20"
    >
      <!-- Count -->
      <p
        v-if="totalCount > 0"
        class="text-main/35 mb-1 text-xs tracking-wide"
      >
        共 {{ totalCount }} 位人物
      </p>

      <!-- Person Rows -->
      <div
        v-for="person in persons"
        :key="person.id"
        class="group border-main/10 relative z-0 cursor-pointer border-b py-4 transition-colors"
        @click="$router.push(`/persons/${person.id}`)"
      >
        <!-- Hover Background Overlay -->
        <div
          class="pointer-events-none absolute -inset-x-3 inset-y-0 -z-10 rounded-sm bg-transparent transition-colors group-hover:bg-white/5"
        ></div>

        <!-- Accent line -->
        <div
          class="group-hover:bg-primary pointer-events-none absolute top-0 bottom-0 -left-3 w-0.5 bg-transparent transition-colors"
        ></div>

        <!-- Name row -->
        <div class="mb-1.5 flex flex-wrap items-baseline justify-between gap-3">
          <div class="flex flex-wrap items-baseline gap-2.5">
            <span class="text-main group-hover:text-primary text-xl font-medium transition-colors">
              {{ person.name }}
            </span>
            <span
              v-if="person.aliases && person.aliases.length > 0"
              class="text-main/40 text-base"
            >
              {{ person.aliases.map((a) => a.name).join(' · ') }}
            </span>
          </div>
        </div>

        <!-- Bio -->
        <p class="text-main/70 mb-3.5 line-clamp-2 text-base leading-relaxed">
          {{ person.excerpt || person.about || '暫無簡歷提供。' }}
        </p>
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
