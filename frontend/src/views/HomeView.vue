<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../api/axios'
import { formatDate } from '../utils/formatters'

const works = ref<any[]>([])
const isLoading = ref(true)

const stats = ref({ works: 0, concepts: 0 })
const currentConcept = ref<any>({})
const recentConcepts = ref<Record<string, {name: string, slug: string}[]>>({})
const announcements = ref<any[]>([])

const refreshRandomConcept = async () => {
  isLoading.value = true
  try {
    const response = await api.get('/concepts/random/')
    if (response.status === 200 && response.data) {
      currentConcept.value = response.data
      works.value = response.data.random_works || []
    }
  } catch (error) {
    console.error('Failed to fetch random spotlight concept:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  try {
    // Send four independent RESTful requests in parallel using Promise.allSettled
    const [worksRes, conceptsRes, postsRes, randomRes] = await Promise.allSettled([
      api.get('/works/'),
      api.get('/concepts/', { params: { ordering: '-updated_at' } }), // Fetch genuinely "recently added" concepts by sorting
      api.get('/posts/'),
      api.get('/concepts/random/') // Fetch a random concept on initial load
    ])

    // 1. Statistics
    if (worksRes.status === 'fulfilled') {
      stats.value.works = worksRes.value.data.count || 0
    }
    if (conceptsRes.status === 'fulfilled') {
      stats.value.concepts = conceptsRes.value.data.count || 0

      // 2. Concept processing
      const allConcepts = conceptsRes.value.data.results || []

      // Group recent concepts by category
      const recent: Record<string, {name: string, slug: string}[]> = {}
      allConcepts.forEach((c: any) => {
        const catName = c.category || '未分類' // If DRF returns category_display, consider using c.category_display instead
        if (!recent[catName]) recent[catName] = []
        if (recent[catName].length < 5) recent[catName].push({ name: c.name, slug: c.slug })
      })
      recentConcepts.value = recent
    }

    // 3. Announcement processing
    if (postsRes.status === 'fulfilled') {
      const fetchedPosts = postsRes.value.data.results || []
      announcements.value = fetchedPosts.slice(0, 5) // 統一：直接儲存原始資料
    }

    // 4. Set initial random concept
    if (randomRes.status === 'fulfilled' && randomRes.value.status === 200 && randomRes.value.data) {
      currentConcept.value = randomRes.value.data
      works.value = randomRes.value.data.random_works || []
    }
  } catch (error) {
    console.error('RESTful API fetch failed:', error)
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div class="max-w-4xl mx-auto space-y-4">

    <!-- Hero Section (Statement & Statistics) - Left Aligned -->
    <section class="card">
      <div class="max-w-4xl">
        <h1 class="text-2xl font-medium text-main mb-4">
          以「概念」為核心的科幻作品資料庫
        </h1>
        <p class="text-sm text-main mb-6">
          目前共收錄 <span class="font-semibold text-primary">{{ stats.works }}</span> 件台灣原創科幻作品與 <span class="font-semibold text-primary">{{ stats.concepts }}</span> 個核心概念。
        </p>
        <div class="flex flex-wrap gap-4">
          <router-link to="/works" class="btn-primary">
            瀏覽作品
          </router-link>
          <router-link to="/concepts" class="tag">
            探索概念
          </router-link>
        </div>
      </div>
    </section>

    <!-- Two Column Layout: 5/12 for Works, 7/12 for Concepts -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-4 md:gap-5">

      <!-- Left Column: Random Concept Works (Narrower) -->
      <section class="lg:col-span-5 card">
        <div class="section-label">
          <span>
            與 <router-link :to="`/concepts/${currentConcept.slug}`" class="text-primary hover:text-primary/70">
              {{ currentConcept.name }}
            </router-link> 相關的作品
          </span>
          <button @click="refreshRandomConcept" class="flex items-center gap-1 text-xs font-medium text-main/50 hover:text-primary transition-colors ml-4 pb-1">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-3.5 h-3.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
            </svg>
              換一個
          </button>
        </div>

        <div v-if="isLoading" class="text-sm text-main/50 py-3">讀取作品中...</div>
        <div v-else-if="works.length > 0" class="flex flex-col">
          <!-- Works List -->
          <router-link v-for="work in works" :key="work.id" :to="`/works/${work.id}`" class="list-row group !flex-col !gap-1 cursor-pointer">
            <h3 class="text-base font-medium text-main group-hover:text-primary transition-colors">
              {{ work.title }}
            </h3>
            <p class="text-sm text-main/50 mt-1">
              <template v-if="work.byline && work.byline.length">
                <template v-for="(agent, idx) in work.byline" :key="idx">
                  <span>{{ agent.text }}</span><span v-if="idx < work.byline.length - 1">、</span>
                </template>
              </template>
              <span v-else>佚名</span>
              · {{ work.year || '未知年份' }} · {{ work.work_length_display || '未知篇幅' }}{{ work.media_type_display || '未知媒體' }}
            </p>
          </router-link>
        </div>

        <div v-else class="text-sm text-main/50 py-3">
          目前該概念下暫無作品。
        </div>
      </section>

      <!-- Right Column: Recent Concepts (Wider) -->
      <section class="lg:col-span-7 card">
        <h2 class="section-label">近期新增概念</h2>

        <div class="space-y-5">
          <div v-for="(tags, category) in recentConcepts" :key="category">
            <h3 class="text-xs font-bold tracking-wider text-main/40 uppercase mb-3">{{ category }}</h3>
            <div class="flex flex-wrap gap-2.5">
              <router-link v-for="tag in tags" :key="tag.slug" :to="`/concepts/${tag.slug}`" class="tag !text-xs !py-1">
                {{ tag.name }}
              </router-link>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Footer Section: Announcements -->
    <section class="card">
      <div class="section-label">
        <span>最新資訊</span>
        <router-link to="/posts" class="text-xs font-medium text-main/50 hover:text-primary transition-colors pb-1">
          查看全部
        </router-link>
      </div>
      <ul class="flex flex-col">
        <li v-for="ann in announcements" :key="ann.id">
          <router-link :to="`/posts/${ann.id}`" class="list-row group cursor-pointer w-full !gap-2 sm:!gap-6 sm:items-center">
            <span class="text-sm font-mono text-main/50 min-w-[110px]">{{ formatDate(ann.created_at) }}</span>
            <span class="text-base text-main group-hover:text-primary transition-colors leading-relaxed">{{ ann.title }}</span>
          </router-link>
        </li>
      </ul>
    </section>

  </div>
</template>
