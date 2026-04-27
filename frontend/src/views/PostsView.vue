<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import api from '../api/axios'

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

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return dateStr.split('T')[0].replace(/-/g, '/')
}
</script>

<template>
  <div class="max-w-4xl mx-auto pb-12">
    <!-- Single Card Layout -->
    <section class="bg-[#ffffff] rounded-lg p-6 md:p-8 shadow-sm border border-[#2d2016]/10">
      <!-- Top Control Bar -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 pb-4 border-b border-[#2d2016]/10">
        <div>
          <h1 class="text-2xl font-bold text-[#2d2016] tracking-tight mb-1">全部資訊</h1>
          <p class="text-[#2d2016]/50 text-sm font-medium">共 {{ totalPosts }} 篇</p>
        </div>
        <div class="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
          <input v-model="searchQuery" type="text" placeholder="搜尋標題、內容..." class="w-full sm:w-64 h-10 px-3 border border-[#2d2016]/20 rounded bg-[#ffffff] focus:outline-none focus:border-[#ae5630] focus:ring-1 focus:ring-[#ae5630] transition-colors text-[#2d2016] placeholder-[#2d2016]/40" />
          <select v-model="ordering" class="w-full sm:w-40 h-10 px-3 border border-[#2d2016]/20 rounded bg-[#ffffff] focus:outline-none focus:border-[#ae5630] text-[15px] text-[#2d2016] cursor-pointer">
            <option value="-created_at">最新發布</option>
            <option value="created_at">最早發布</option>
            <option value="-updated_at">最近更新</option>
            <option value="updated_at">最早更新</option>
          </select>
        </div>
      </div>

        <div v-if="isLoading" class="py-12 text-center text-[#2d2016]/50 font-medium">
          讀取中...
        </div>
        <div v-else-if="posts.length === 0" class="py-12 text-center text-[#2d2016]/50 font-medium">
          找不到符合條件的文章。
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>

            </thead>
            <tbody class="divide-y divide-[#2d2016]/5">
              <tr v-for="post in posts" :key="post.id" class="group hover:bg-[#f5f0e8]/30 transition-colors">
                <td class="py-3.5 pr-4 align-middle">
                  <router-link :to="`/posts/${post.id}`" class="text-[17px] font-medium text-[#2d2016] group-hover:text-[#ae5630] transition-colors block">
                    {{ post.title }}
                  </router-link>
                </td>
                <td class="py-3.5 align-middle text-right font-mono text-[15px] text-[#2d2016]/60">
                  {{ formatDate(post.created_at) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="posts.length > 0 && (hasPrev || hasNext)" class="flex items-center justify-center gap-4 mt-8 pt-6 border-t border-[#2d2016]/5">
          <button :disabled="!hasPrev" @click="changePage(-1)" class="px-5 py-2 rounded-lg font-medium transition-colors border border-[#2d2016]/20" :class="hasPrev ? 'bg-[#ffffff] text-[#2d2016] hover:bg-[#ede8dc]' : 'bg-[#f5f0e8] text-[#2d2016]/30 cursor-not-allowed'">
            上一頁
          </button>
          <span class="text-sm text-[#2d2016]/60 font-medium tabular-nums">
            第 <span class="text-[#2d2016] font-bold">{{ currentPage }}</span> / <span class="text-[#2d2016] font-bold">{{ totalPages }}</span> 頁
          </span>
          <button :disabled="!hasNext" @click="changePage(1)" class="px-5 py-2 rounded-lg font-medium transition-colors border border-[#2d2016]/20" :class="hasNext ? 'bg-[#ffffff] text-[#2d2016] hover:bg-[#ede8dc]' : 'bg-[#f5f0e8] text-[#2d2016]/30 cursor-not-allowed'">
            下一頁
          </button>
        </div>
      </section>
  </div>
</template>
