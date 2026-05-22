<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../api/axios'
import { formatDate } from '../utils/formatters'
import SectionTitle from '../components/SectionTitle.vue'
import ConceptTag from '../components/ConceptTag.vue'
import { useDocumentTitle } from '../composables/useDocumentTitle'

useDocumentTitle(null)

const works = ref<any[]>([])
const isLoading = ref(true)

const stats = ref({ works: 0, concepts: 0 })
const currentConcept = ref<any>({})
const recentConcepts = ref<Record<string, { name: string; slug: string }[]>>({})
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
      api.get('/works/', { params: { limit: 1 } }), // 優化：只為獲取總數，避免回傳整頁笨重資料
      api.get('/concepts/', { params: { ordering: '-updated_at' } }), // Fetch genuinely "recently added" concepts by sorting
      api.get('/posts/'),
      api.get('/concepts/random/'), // Fetch a random concept on initial load
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
      const recent: Record<string, { name: string; slug: string }[]> = {}
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
      announcements.value = fetchedPosts.slice(0, 5)
    }

    // 4. Set initial random concept
    if (
      randomRes.status === 'fulfilled' &&
      randomRes.value.status === 200 &&
      randomRes.value.data
    ) {
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
  <div class="mx-auto max-w-4xl space-y-0 pb-20">
    <!-- Hero -->
    <section class="pt-6 pb-14 md:pt-10">
      <h1 class="text-main mb-2 text-2xl font-normal">能依概念檢索的科幻書目資料庫</h1>
      <p class="text-main/40 mb-7 text-sm">
        收錄 {{ stats.works }} 件台灣原創作品與 {{ stats.concepts }} 種概念
      </p>
      <div class="flex items-center gap-5">
        <router-link
          to="/works"
          class="text-bg bg-primary px-4 py-2 text-sm font-medium no-underline transition-opacity hover:opacity-85"
        >
          瀏覽作品
        </router-link>
        <router-link
          to="/concepts"
          class="text-main/40 hover:text-primary text-sm no-underline transition-colors"
        >
          探索概念 →
        </router-link>
      </div>
    </section>

    <!-- Two Column Layout -->
    <div class="grid grid-cols-1 gap-10 pb-16 lg:grid-cols-2 lg:gap-14">
      <!-- Left Column: Random Concept Works -->
      <section class="flex flex-col">
        <SectionTitle class="mb-5">
          與
          <router-link
            :to="`/concepts/${currentConcept.slug}`"
            class="text-primary/70 hover:text-primary no-underline transition-colors"
          >
            {{ currentConcept.name }}
          </router-link>
          相關的作品
          <template #action>
            <button
              class="text-main/40 hover:text-primary flex items-center gap-1 text-sm whitespace-nowrap transition-colors"
              @click="refreshRandomConcept"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.8"
                stroke="currentColor"
                class="h-3.5 w-3.5"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99"
                />
              </svg>
              換一個
            </button>
          </template>
        </SectionTitle>

        <div
          v-if="isLoading"
          class="text-main/50 py-3 text-center text-base"
        >
          正在讀取作品...
        </div>
        <div
          v-else-if="works.length > 0"
          class="flex flex-col"
        >
          <!-- Works List -->
          <router-link
            v-for="work in works"
            :key="work.id"
            :to="`/works/${work.id}`"
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

            <div class="flex w-full items-start justify-between gap-4">
              <span
                class="text-main group-hover:text-primary mb-1 block text-base font-medium transition-colors"
              >
                {{ work.title }}
              </span>
            </div>
            <div class="text-main/50 text-sm">
              <template v-if="work.byline && work.byline.length">
                <template
                  v-for="(agent, idx) in work.byline"
                  :key="idx"
                >
                  <span>{{ agent.text }}</span>
                  <span v-if="idx < work.byline.length - 1">、</span>
                </template>
              </template>
              <span v-else>佚名</span>
              <span class="text-main/20 mx-1.5">·</span>
              <span>{{ work.year || '未知年份' }}</span>
              <template
                v-if="[work.work_length_display, work.media_type_display].filter(Boolean).length"
              >
                <span class="text-main/20 mx-1.5">·</span>
                <span>
                  {{ [work.work_length_display, work.media_type_display].filter(Boolean).join('') }}
                </span>
              </template>
            </div>
          </router-link>
        </div>

        <div
          v-else
          class="text-main/50 py-3 text-center text-base"
        >
          目前該概念下暫無作品。
        </div>
      </section>

      <!-- Right Column: Recent Concepts -->
      <section class="border-main/10 flex flex-col lg:border-l lg:pl-10">
        <SectionTitle class="mb-5">近期新增概念</SectionTitle>

        <div class="space-y-7">
          <div
            v-for="(tags, category) in recentConcepts"
            :key="category"
          >
            <h3 class="text-main/40 mb-3 text-sm font-medium tracking-widest uppercase">
              {{ category }}
            </h3>
            <div class="flex flex-wrap gap-1.5">
              <ConceptTag
                v-for="tag in tags"
                :key="tag.slug"
                :concept="tag"
              />
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Footer Section: Announcements -->
    <section class="">
      <SectionTitle class="mb-5">
        最新資訊
        <template #action>
          <router-link
            to="/posts"
            class="text-main/40 hover:text-primary text-sm no-underline transition-colors"
          >
            查看全部
          </router-link>
        </template>
      </SectionTitle>
      <ul class="flex flex-col">
        <li
          v-for="ann in announcements"
          :key="ann.id"
        >
          <router-link
            :to="`/posts/${ann.id}`"
            class="group border-main/10 relative z-0 flex cursor-pointer flex-col gap-2 border-b py-4 no-underline transition-colors last:border-0 sm:flex-row sm:items-baseline sm:gap-6"
          >
            <!-- Hover Background Overlay -->
            <div
              class="pointer-events-none absolute -inset-x-3 inset-y-0 -z-10 rounded-sm bg-transparent transition-colors group-hover:bg-white/5"
            ></div>

            <!-- Accent line -->
            <div
              class="group-hover:bg-primary pointer-events-none absolute top-0 bottom-0 -left-3 w-0.5 bg-transparent transition-colors"
            ></div>

            <span class="text-main/50 shrink-0 text-sm sm:w-28">
              {{ formatDate(ann.created_at) }}
            </span>
            <span
              class="text-main group-hover:text-primary text-base leading-relaxed font-medium transition-colors"
            >
              {{ ann.title }}
            </span>
          </router-link>
        </li>
      </ul>
    </section>
  </div>
</template>
