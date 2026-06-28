<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fetchWorks as fetchWorksApi } from '../api/works'
import {
  fetchConcepts as fetchConceptsApi,
  fetchRandomConcept as fetchRandomConceptApi,
} from '../api/concepts'
import { fetchPosts as fetchPostsApi } from '../api/posts'
import type { Concept, Post } from '../types'

// The homepage spotlight list holds a concept's random_works (a trimmed work shape).
type SpotlightWork = NonNullable<Concept['random_works']>[number]
import { formatDate } from '../utils/formatters'
import SectionTitle from '../components/SectionTitle.vue'
import ConceptTag from '../components/ConceptTag.vue'
import HoverListItem from '../components/HoverListItem.vue'
import Icon from '../components/Icon.vue'
import { useDocumentMeta } from '../composables/useDocumentTitle'

useDocumentMeta(null, '')

const works = ref<SpotlightWork[]>([])
const isLoading = ref(true)
const hasError = ref(false)

const stats = ref({ works: 0, concepts: 0 })
const currentConcept = ref<Concept | null>(null)
const recentConcepts = ref<Concept[]>([])
const announcements = ref<Post[]>([])

const refreshRandomConcept = async () => {
  isLoading.value = true
  try {
    const response = await fetchRandomConceptApi()
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
  isLoading.value = true
  hasError.value = false
  try {
    const [worksRes, conceptsRes, postsRes, randomRes] = await Promise.allSettled([
      fetchWorksApi({ limit: 1 }),
      fetchConceptsApi({ ordering: '-updated_at' }),
      fetchPostsApi(),
      fetchRandomConceptApi(),
    ])

    if (worksRes.status === 'fulfilled') {
      stats.value.works = worksRes.value.data.count || 0
    }
    if (conceptsRes.status === 'fulfilled') {
      stats.value.concepts = conceptsRes.value.data.count || 0
      const allConcepts = conceptsRes.value.data.results || []
      recentConcepts.value = allConcepts.slice(0, 8)
    }
    if (postsRes.status === 'fulfilled') {
      announcements.value = (postsRes.value.data.results || []).slice(0, 5)
    }
    if (
      randomRes.status === 'fulfilled' &&
      randomRes.value.status === 200 &&
      randomRes.value.data
    ) {
      currentConcept.value = randomRes.value.data
      works.value = randomRes.value.data.random_works || []
    }

    if (
      worksRes.status === 'rejected' &&
      conceptsRes.status === 'rejected' &&
      postsRes.status === 'rejected'
    ) {
      hasError.value = true
    }
  } catch (error) {
    console.error('RESTful API fetch failed:', error)
    hasError.value = true
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div class="mx-auto max-w-4xl pb-20">
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

    <!-- Error State -->
    <div
      v-if="hasError"
      class="text-main/50 py-16 text-center text-base font-medium"
    >
      資料讀取發生問題，請稍後再試。
    </div>

    <!-- Two Column Layout: 60/40 -->
    <div
      v-else
      class="grid grid-cols-1 gap-10 lg:grid-cols-[3fr_2fr] lg:gap-14"
    >
      <!-- Left Column: Random Concept Works -->
      <section class="flex flex-col">
        <SectionTitle
          v-if="currentConcept"
          class="mb-4"
        >
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
              <Icon
                name="refresh"
                :stroke-width="1.8"
                class="h-3.5 w-3.5"
              />
              換一個
            </button>
          </template>
        </SectionTitle>

        <div
          v-if="isLoading"
          class="text-main/50 animate-pulse py-3 text-sm"
        >
          正在讀取作品...
        </div>

        <div
          v-else-if="works.length > 0"
          class="flex flex-col"
        >
          <HoverListItem
            v-for="work in works"
            :key="work.id"
            :to="`/works/${work.id}`"
            class="flex items-baseline gap-4 py-3 no-underline"
          >
            <!-- Year -->
            <span class="text-main/50 w-10 shrink-0 text-sm">
              {{ work.year || '-' }}
            </span>

            <!-- Title -->
            <div class="flex min-w-0 flex-1 items-baseline">
              <span
                class="text-main group-hover:text-primary text-base font-medium transition-colors"
              >
                {{ work.title }}
              </span>
            </div>

            <!-- Author + Meta -->
            <div class="shrink-0 text-right">
              <span class="text-main/50 text-sm">
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
              </span>
              <span
                v-if="[work.work_length_display, work.genre_display].filter(Boolean).length"
                class="text-main/45 ml-2 text-sm"
              >
                {{ [work.work_length_display, work.genre_display].filter(Boolean).join('') }}
              </span>
            </div>
          </HoverListItem>
        </div>

        <div
          v-else
          class="flex flex-col items-center gap-2 py-10 text-center"
        >
          <Icon
            name="box"
            :stroke-width="1.2"
            class="text-main/15 h-10 w-10"
          />
          <span class="text-main/35 text-sm">目前該概念下暫無作品。</span>
        </div>
      </section>

      <!-- Right Column -->
      <aside class="lg:border-main/10 flex flex-col gap-10 lg:border-l lg:pl-10">
        <!-- Latest news -->
        <section>
          <SectionTitle class="mb-4">
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

          <!-- Loading state -->
          <div
            v-if="isLoading"
            class="text-main/50 animate-pulse py-3 text-sm"
          >
            正在讀取公告...
          </div>

          <!-- Empty state -->
          <div
            v-else-if="announcements.length === 0"
            class="flex flex-col items-center gap-2 py-6 text-center"
          >
            <Icon
              name="bell-off"
              :stroke-width="1.2"
              class="text-main/20 h-8 w-8"
            />
            <span class="text-main/30 text-sm">目前尚無最新公告</span>
          </div>

          <!-- Announcements list -->
          <ul
            v-else
            class="flex flex-col"
          >
            <li
              v-for="ann in announcements"
              :key="ann.id"
            >
              <HoverListItem
                :to="`/posts/${ann.id}`"
                class="flex flex-col gap-0.5 py-3 no-underline"
              >
                <span class="text-main/40 text-xs">{{ formatDate(ann.created_at) }}</span>
                <span
                  class="text-main group-hover:text-primary text-sm leading-snug font-medium transition-colors"
                >
                  {{ ann.title }}
                </span>
              </HoverListItem>
            </li>
          </ul>
        </section>

        <!-- Recently added concepts -->
        <section>
          <SectionTitle class="mb-4">近期新增概念</SectionTitle>
          <div
            v-if="isLoading"
            class="text-main/50 animate-pulse py-3 text-sm"
          >
            正在讀取概念...
          </div>
          <div
            v-else-if="recentConcepts.length > 0"
            class="flex flex-wrap gap-1.5"
          >
            <ConceptTag
              v-for="concept in recentConcepts"
              :key="concept.slug"
              :concept="concept"
            />
          </div>
          <p
            v-else
            class="text-main/30 text-sm"
          >
            尚無概念資料。
          </p>
        </section>
      </aside>
    </div>
  </div>
</template>
