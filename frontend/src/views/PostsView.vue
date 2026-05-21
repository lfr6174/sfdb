<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import api from '../api/axios'
import PaginationControls from '../components/PaginationControls.vue'
import { formatDate } from '../utils/formatters'
import { useDebounceFn } from '../composables/useDebounce'

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

const triggerFetch = useDebounceFn(() => {
  currentPage.value = 1
  fetchPosts()
}, 300)

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
  <div class="mx-auto max-w-4xl pb-20">
    <!-- ── Controls ── -->
    <div class="flex flex-col justify-between gap-4 pt-10 pb-8 md:flex-row md:items-center">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="搜尋標題、內容…"
        class="text-main placeholder:text-main/35 border-main/20 focus:border-main/50 w-full border-b bg-transparent px-0 py-1.5 text-sm transition-colors outline-none md:w-56"
      />
      <div class="relative shrink-0">
        <select
          v-model="ordering"
          class="text-main/60 border-main/20 focus:border-main/50 w-28 cursor-pointer appearance-none border-b bg-transparent py-1.5 pr-6 pl-1 text-sm transition-colors outline-none"
        >
          <option value="-created_at">最新發布</option>
          <option value="created_at">最早發布</option>
          <option value="-updated_at">最近更新</option>
          <option value="updated_at">最早更新</option>
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

    <!-- ── List ── -->
    <div
      v-if="isLoading"
      class="text-main/50 py-16 text-center text-base font-medium"
    >
      正在讀取文章列表...
    </div>
    <div
      v-else-if="posts.length === 0"
      class="text-main/50 py-16 text-center text-base font-medium"
    >
      找不到符合條件的文章。
    </div>
    <div
      v-else
      class="flex flex-col"
    >
      <!-- Count -->
      <p
        v-if="totalPosts > 0"
        class="text-main/45 mb-1 text-sm tracking-wide"
      >
        共 {{ totalPosts }} 篇文章
      </p>

      <router-link
        v-for="post in posts"
        :key="post.id"
        :to="`/posts/${post.id}`"
        class="group border-main/10 relative z-0 flex flex-col gap-1 border-b py-4 no-underline transition-colors last:border-0"
      >
        <!-- Hover Background Overlay -->
        <div
          class="pointer-events-none absolute -inset-x-3 inset-y-0 -z-10 rounded-sm bg-transparent transition-colors group-hover:bg-white/5"
        ></div>

        <!-- Accent line -->
        <div
          class="group-hover:bg-primary pointer-events-none absolute top-0 bottom-0 -left-3 w-0.5 bg-transparent transition-colors"
        ></div>

        <span class="text-main/40 text-xs">
          {{ formatDate(post.created_at) }}
        </span>
        <span class="text-main group-hover:text-primary block text-lg font-medium transition-colors">
          {{ post.title }}
        </span>
      </router-link>

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
