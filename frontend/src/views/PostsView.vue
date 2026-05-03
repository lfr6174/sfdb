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
  <div class="max-w-4xl mx-auto pb-12">
    <!-- Single Card Layout -->
    <section class="card !p-6 md:!p-8">
      <!-- Top Control Bar -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 pb-4 border-b border-main/10">
        <div>
          <h1 class="text-2xl font-bold text-main tracking-tight mb-1">全部資訊</h1>
          <p class="text-main/50 text-sm font-medium">共 {{ totalPosts }} 篇</p>
        </div>
        <div class="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
          <input v-model="searchQuery" type="text" placeholder="搜尋標題、內容..." class="w-full sm:w-64 h-10 px-3 border border-main/20 rounded bg-bg focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors text-main placeholder-main/40" />
          <select v-model="ordering" class="w-full sm:w-40 h-10 px-3 border border-main/20 rounded bg-bg focus:outline-none focus:border-primary text-[15px] text-main cursor-pointer">
            <option value="-created_at">最新發布</option>
            <option value="created_at">最早發布</option>
            <option value="-updated_at">最近更新</option>
            <option value="updated_at">最早更新</option>
          </select>
        </div>
      </div>

        <div v-if="isLoading" class="py-12 text-center text-main/50 font-medium">
          讀取中...
        </div>
        <div v-else-if="posts.length === 0" class="py-12 text-center text-main/50 font-medium">
          找不到符合條件的文章。
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <tbody class="divide-y divide-main/5">
              <tr v-for="post in posts" :key="post.id" class="group hover:bg-hover/30 transition-colors">
                <td class="py-3.5 pr-4 align-middle">
                  <router-link :to="`/posts/${post.id}`" class="text-[17px] font-medium text-main group-hover:text-primary transition-colors block">
                    {{ post.title }}
                  </router-link>
                </td>
                <td class="py-3.5 align-middle text-right font-mono text-[15px] text-main/60">
                  {{ formatDate(post.created_at) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <PaginationControls
          v-if="posts.length > 0 && (hasPrev || hasNext)"
          :current-page="currentPage"
          :total-pages="totalPages"
          :has-prev="hasPrev"
          :has-next="hasNext"
          @change-page="changePage"
        />
      </section>
  </div>
</template>
