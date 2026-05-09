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
  <div class="max-w-4xl mx-auto space-y-0 pb-20">

    <!-- Hero Section (Statement & Statistics) - Left Aligned -->
    <section class="pt-10 pb-12 md:pb-16">
      <div class="max-w-3xl">
        <p class="text-base text-main/70 mb-4">
          目前共收錄 <span class="font-medium text-primary">{{ stats.works }}</span> 件台灣原創科幻作品與 <span class="font-medium text-primary">{{ stats.concepts }}</span> 個核心概念。
        </p>
        <h1 class="text-4xl md:text-5xl font-normal leading-snug text-main mb-8">
          以「概念」為核心的<br class="hidden md:block">科幻作品資料庫
        </h1>
        <div class="flex flex-wrap gap-3">
          <router-link to="/works" class="text-base font-medium text-bg bg-primary px-6 py-3 hover:opacity-85 transition-opacity no-underline inline-block">
            瀏覽作品
          </router-link>
          <router-link to="/concepts" class="text-base text-main/60 border border-main/15 px-6 py-3 hover:text-primary hover:border-primary/30 hover:bg-primary/5 transition-all no-underline inline-block">
            探索概念
          </router-link>
        </div>
      </div>
    </section>

    <!-- Two Column Layout -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-10 lg:gap-14 pb-16">

      <!-- Left Column: Random Concept Works -->
      <section class="flex flex-col">
        <div class="flex items-center gap-3 mb-5">
          <span class="text-sm font-medium tracking-widest uppercase text-main/40 whitespace-nowrap">
            與 <router-link :to="`/concepts/${currentConcept.slug}`" class="text-primary hover:text-primary/70 transition-colors no-underline">
              {{ currentConcept.name }}
            </router-link> 相關的作品
          </span>
          <div class="flex-1 border-t border-main/10"></div>
          <button @click="refreshRandomConcept" class="flex items-center gap-1 text-sm text-main/40 hover:text-primary transition-colors whitespace-nowrap">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="w-3.5 h-3.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
            </svg>
              換一個
          </button>
        </div>

        <div v-if="isLoading" class="text-base text-main/50 py-3 text-center">正在讀取作品...</div>
        <div v-else-if="works.length > 0" class="flex flex-col">
          <!-- Works List -->
          <router-link
            v-for="work in works"
            :key="work.id"
            :to="`/works/${work.id}`"
            class="group flex flex-col gap-1 py-3.5 border-b border-main/10 last:border-0 hover:bg-primary/5 hover:-mx-4 hover:px-4 transition-colors no-underline"
          >
            <div class="flex items-start justify-between gap-4 w-full">
              <span class="text-base font-medium text-main group-hover:text-primary transition-colors block mb-1">
                {{ work.title }}
              </span>
              <span class="font-mono text-xs tracking-wide text-main/50 bg-main/5 px-1.5 py-0.5 shrink-0 mt-0.5">
                {{ [work.work_length_display, work.media_type_display].filter(Boolean).join('') || '-' }}
              </span>
            </div>
            <div class="text-sm text-main/50">
              <template v-if="work.byline && work.byline.length">
                <template v-for="(agent, idx) in work.byline" :key="idx">
                  <span>{{ agent.text }}</span><span v-if="idx < work.byline.length - 1">、</span>
                </template>
              </template>
              <span v-else>佚名</span>
              <span class="text-main/20 mx-1.5">·</span>
              <span>{{ work.year || '未知年份' }}</span>
            </div>
          </router-link>
        </div>

        <div v-else class="text-base text-main/50 py-3 text-center">
          目前該概念下暫無作品。
        </div>
      </section>

      <!-- Right Column: Recent Concepts -->
      <section class="flex flex-col lg:pl-10 lg:border-l border-main/10">
        <div class="flex items-center gap-3 mb-5">
          <span class="text-sm font-medium tracking-widest uppercase text-main/40 whitespace-nowrap">近期新增概念</span>
          <div class="flex-1 border-t border-main/10"></div>
        </div>

        <div class="space-y-7">
          <div v-for="(tags, category) in recentConcepts" :key="category">
            <h3 class="text-sm font-medium tracking-widest uppercase text-main/40 mb-3">{{ category }}</h3>
            <div class="flex flex-wrap gap-1.5">
              <router-link
                v-for="tag in tags"
                :key="tag.slug"
                :to="`/concepts/${tag.slug}`"
                class="inline-flex items-center text-xs text-main/60 border border-main/15 px-2.5 py-1 hover:text-primary hover:bg-primary/5 hover:border-primary/30 transition-all whitespace-nowrap no-underline"
              >
                {{ tag.name }}
              </router-link>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Footer Section: Announcements -->
    <section class="">
      <div class="flex items-center gap-3 mb-5">
        <span class="text-sm font-medium tracking-widest uppercase text-main/40 whitespace-nowrap">最新資訊</span>
        <div class="flex-1 border-t border-main/10"></div>
        <router-link to="/posts" class="text-sm text-main/40 hover:text-primary transition-colors no-underline">
          查看全部
        </router-link>
      </div>
      <ul class="flex flex-col">
        <li v-for="ann in announcements" :key="ann.id">
          <router-link :to="`/posts/${ann.id}`" class="flex flex-col sm:flex-row sm:items-baseline gap-2 sm:gap-6 py-3.5 border-b border-main/10 last:border-0 group cursor-pointer hover:bg-primary/5 hover:-mx-4 hover:px-4 transition-colors no-underline">
            <span class="text-sm font-mono text-main/50 shrink-0 sm:w-28">{{ formatDate(ann.created_at) }}</span>
            <span class="text-base font-medium text-main group-hover:text-primary transition-colors leading-relaxed">{{ ann.title }}</span>
          </router-link>
        </li>
      </ul>
    </section>

  </div>
</template>
