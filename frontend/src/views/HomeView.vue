<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../api/axios'

const works = ref<any[]>([])
const isLoading = ref(true)

const stats = ref({ works: 0, concepts: 0 })
const currentConcept = ref<any>({})
const recentConcepts = ref<Record<string, {name: string, slug: string}[]>>({})
const announcements = ref<any[]>([])

// 共用的日期格式化函式
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return dateStr.split('T')[0].replace(/-/g, '/')
}

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
  <div class="max-w-5xl mx-auto space-y-4">

    <!-- Hero Section (Statement & Statistics) - Left Aligned -->
    <section class="bg-[#ffffff] rounded-lg p-6 md:p-8 shadow-sm border border-[#2d2016]/10">
      <div class="max-w-4xl">
        <p class="text-xl md:text-2xl font-medium text-[#2d2016] mb-1 tracking-tight leading-relaxed">
          以「概念」為核心的科幻作品資料庫
        </p>
        <p class="text-xl md:text-2xl font-medium text-[#2d2016] mb-6 tracking-tight leading-relaxed">
          目前共收錄 <span class="font-semibold text-[#ae5630]">{{ stats.works }}</span> 件台灣原創科幻作品與 <span class="font-semibold text-[#ae5630]">{{ stats.concepts }}</span> 個核心概念。
        </p>
        <div class="flex flex-wrap gap-4">
          <router-link to="/works" class="px-6 py-2 bg-[#ae5630] text-[#ffffff] text-base font-medium rounded hover:bg-[#ae5630]/90 transition-colors shadow-sm">
            瀏覽作品
          </router-link>
          <router-link to="/concepts" class="px-6 py-2 bg-[#ffffff] text-[#2d2016]/80 border border-[#2d2016]/20 text-base font-medium rounded hover:bg-[#ede8dc] hover:text-[#2d2016] transition-colors shadow-sm">
            探索概念
          </router-link>
        </div>
      </div>
    </section>

    <!-- Two Column Layout: 5/12 for Works, 7/12 for Concepts -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-4 md:gap-5">

      <!-- Left Column: Random Concept Works (Narrower) -->
      <section class="lg:col-span-5 bg-[#ffffff] rounded-lg p-5 shadow-sm border border-[#2d2016]/10">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg md:text-xl font-bold text-[#2d2016] tracking-tight">
            與 <router-link :to="`/concepts/${currentConcept.slug}`" class="text-[#ae5630] underline decoration-[#ae5630]/40 underline-offset-4 cursor-pointer hover:text-[#ae5630]/80">
              {{ currentConcept.name }}
            </router-link> 相關的作品
          </h2>
          <button @click="refreshRandomConcept" class="text-sm md:text-base px-2.5 py-1 text-[#2d2016]/70 border border-[#2d2016]/20 rounded hover:bg-[#ede8dc] hover:text-[#2d2016] transition-colors">
            換一個
          </button>
        </div>

        <div v-if="isLoading" class="text-[#2d2016]/50 py-4">讀取作品中...</div>
        <div v-else-if="works.length > 0" class="space-y-1">
          <!-- Works List -->
          <router-link v-for="work in works" :key="work.id" :to="`/works/${work.id}`" class="group flex flex-col py-2.5 border-b border-[#2d2016]/5 last:border-0 hover:bg-[#ede8dc] px-2 -mx-2 rounded transition-colors cursor-pointer">
            <h3 class="text-lg font-medium text-[#2d2016] group-hover:text-[#ae5630] transition-colors">
              {{ work.title }}
            </h3>
            <p class="text-sm md:text-base text-[#2d2016]/60 mt-0.5">
              <template v-if="work.byline && work.byline.length">
                <template v-for="(agent, idx) in work.byline" :key="idx">
                  <span>{{ agent.text }}</span><span v-if="idx < work.byline.length - 1">、</span>
                </template>
              </template>
              <span v-else>佚名</span>
              · {{ work.year || '未知年份' }} · {{ work.media_type_display || '未知媒體' }} · {{ work.work_length_display || '未知篇幅' }}
            </p>
          </router-link>
        </div>
        <div v-else class="text-[#2d2016]/50 py-4">
          目前該概念下暫無作品。
        </div>
      </section>

      <!-- Right Column: Recent Concepts (Wider) -->
      <section class="lg:col-span-7 bg-[#ffffff] rounded-lg p-5 shadow-sm border border-[#2d2016]/10">
        <h2 class="text-lg md:text-xl font-bold text-[#2d2016] tracking-tight mb-4">近期新增概念</h2>

        <div class="space-y-3">
          <div v-for="(tags, category) in recentConcepts" :key="category">
            <h3 class="text-sm font-bold tracking-widest text-[#2d2016]/50 uppercase mb-2">{{ category }}</h3>
            <div class="flex flex-wrap gap-2">
              <router-link v-for="tag in tags" :key="tag.slug" :to="`/concepts/${tag.slug}`" class="px-2.5 py-1 bg-transparent border border-[#2d2016]/10 text-[#2d2016]/60 text-base font-medium rounded-md cursor-pointer hover:bg-[#ae5630]/10 hover:border-[#ae5630]/30 hover:text-[#ae5630] transition-all duration-200">
                {{ tag.name }}
              </router-link>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Footer Section: Announcements -->
    <section class="bg-[#ffffff] rounded-lg p-5 shadow-sm border border-[#2d2016]/10">
      <div class="flex items-center justify-between mb-3 border-b border-[#2d2016]/5 pb-2">
        <h2 class="text-lg md:text-xl font-bold text-[#2d2016] tracking-tight">最新資訊</h2>
        <router-link to="/posts" class="text-sm font-medium text-[#ae5630] hover:underline underline-offset-4 transition-colors">
          查看全部
        </router-link>
      </div>
      <ul class="space-y-2">
        <li v-for="ann in announcements" :key="ann.id" class="border-b border-[#2d2016]/5 last:border-0">
          <router-link :to="`/posts/${ann.id}`" class="flex flex-col sm:flex-row sm:items-baseline gap-2 sm:gap-6 py-1.5 group cursor-pointer w-full">
            <span class="text-base font-mono text-[#2d2016]/50 min-w-[110px] group-hover:text-[#ae5630]/70 transition-colors">{{ formatDate(ann.created_at) }}</span>
            <span class="text-base text-[#2d2016]/80 group-hover:text-[#ae5630] transition-colors leading-relaxed">{{ ann.title }}</span>
          </router-link>
        </li>
      </ul>
    </section>

  </div>
</template>
