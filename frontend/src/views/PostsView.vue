<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import api from '../api/axios'
import PaginationControls from '../components/PaginationControls.vue'
import { formatDate } from '../utils/formatters'

const PAGE_SIZE = 20
const posts = ref<any[]>([])
const totalPosts = ref(0)
const isLoading = ref(false)
const currentPage = ref(1)
const hasNext = ref(false)
const hasPrev = ref(false)

const searchQuery = ref('')
const ordering = ref('-created_at')

const totalPages = computed(() => Math.max(1, Math.ceil(totalPosts.value / PAGE_SIZE)))

const fetchPosts = async () => {
  isLoading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      ordering: ordering.value,
    }
    if (searchQuery.value) params.search = searchQuery.value

    const res = await api.get('/posts/', { params })
    posts.value = res.data.results || []
    totalPosts.value = res.data.count || 0
    hasNext.value = !!res.data.next
    hasPrev.value = !!res.data.previous
  } catch (err) {
    console.error('Failed to fetch posts', err)
  } finally {
    isLoading.value = false
  }
}

let fetchTimeout: any
const triggerFetch = () => {
  clearTimeout(fetchTimeout)
  fetchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchPosts()
  }, 300)
}

watch([searchQuery, ordering], () => {
  triggerFetch()
})

onMounted(() => {
  fetchPosts()
})

const changePage = (dir: number) => {
  currentPage.value += dir
  fetchPosts()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>

<template>
  <div class="max-w-4xl mx-auto pb-20">

    <!-- ── Page Header ── -->
    <div class="pt-10 pb-6 border-b border-main/[0.08]">
      <div class="flex flex-col md:flex-row md:items-end justify-between gap-5">
        <div>
          <h1 class="text-[1.75rem] font-normal text-main leading-tight mb-1">最新資訊</h1>
          <p class="text-[13px] text-main/45">共 {{ totalPosts }} 篇文章</p>
        </div>

        <div class="flex items-center gap-2">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜尋標題、內容…"
            class="text-[13px] text-main placeholder:text-main/35 bg-transparent border border-main/[0.14] px-3 py-[7px] outline-none focus:border-primary/50 transition-colors w-48 md:w-56"
          >
          <div class="relative">
            <select
              v-model="ordering"
              class="text-[13px] text-main/70 bg-transparent border border-main/[0.14] px-3 py-[7px] pr-7 outline-none focus:border-primary/50 transition-colors cursor-pointer appearance-none"
            >
              <option value="-created_at">最新發布</option>
              <option value="created_at">最早發布</option>
              <option value="-updated_at">最近更新</option>
              <option value="updated_at">最早更新</option>
            </select>
            <svg class="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 text-main/40" width="9" height="5" viewBox="0 0 10 6" fill="none">
              <path d="M0 0l5 6 5-6z" fill="currentColor"/>
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- ── List ── -->
    <div v-if="isLoading" class="text-center py-16 text-main/45 text-[13px] font-medium">
      正在讀取文章列表...
    </div>
    <div v-else-if="posts.length === 0" class="text-center py-16 text-main/45 text-[13px] font-medium">
      找不到符合條件的文章。
    </div>
    <div v-else class="flex flex-col mt-4">
      <div
        v-for="post in posts"
        :key="post.id"
        class="group flex flex-col sm:flex-row sm:items-center justify-between gap-2 sm:gap-6 py-4 border-b border-main/[0.08] last:border-0 hover:bg-primary/[0.025] hover:-mx-4 hover:px-4 transition-colors"
      >
        <router-link
          :to="`/posts/${post.id}`"
          class="text-[15px] font-medium text-main group-hover:text-primary transition-colors no-underline block"
        >
          {{ post.title }}
        </router-link>
        <span class="font-mono text-[12.5px] text-main/45 shrink-0">
          {{ formatDate(post.created_at) }}
        </span>
      </div>

      <div class="mt-6">
        <!-- Pagination -->
        <PaginationControls
          v-if="posts.length > 0 && (hasPrev || hasNext)"
          :current-page="currentPage"
          :total-pages="totalPages"
          :has-prev="hasPrev"
          :has-next="hasNext"
          @change-page="changePage"
        />
      </div>
    </div>

  </div>
</template>
