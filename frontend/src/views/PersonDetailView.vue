<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'

const route = useRoute()

const agent = ref<any>(null)
const isLoading = ref(true)
const isConceptsExpanded = ref(false)

const fetchAgentDetail = async () => {
  isLoading.value = true
  try {
    const response = await api.get(`/agents/${route.params.id}/`)
    agent.value = response.data
  } catch (error) {
    console.error('Failed to fetch agent details:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchAgentDetail()
})

// Manage displayed concepts for the "show more" functionality
const DISPLAY_LIMIT = 10
const displayedConcepts = computed(() => {
  if (!agent.value?.top_concepts) return []
  if (isConceptsExpanded.value) return agent.value.top_concepts
  return agent.value.top_concepts.slice(0, DISPLAY_LIMIT)
})

const hiddenConceptsCount = computed(() => {
  if (!agent.value?.top_concepts) return 0
  return Math.max(0, agent.value.top_concepts.length - DISPLAY_LIMIT)
})

const totalWorksCount = computed(() => {
  return agent.value?.participated_works?.length || 0
})

const activeYears = computed(() => {
  if (!agent.value?.participated_works || agent.value.participated_works.length === 0) return '—'
  const years = agent.value.participated_works
    .map((w: any) => parseInt(w.year))
    .filter((y: number) => !isNaN(y))
  if (years.length === 0) return '—'
  const min = Math.min(...years)
  const max = Math.max(...years)
  return min === max ? `${min}` : `${min} — ${max}`
})

const personAwards = computed(() => {
  if (!agent.value?.participated_works) return []
  const awardsMap = new Map<number, any>()

  agent.value.participated_works.forEach((w: any) => {
    if (w.awards && w.awards.length > 0) {
      w.awards.forEach((award: any) => {
        if (!awardsMap.has(award.catalogue_id)) {
          awardsMap.set(award.catalogue_id, {
            id: award.catalogue_id,
            title: award.title,
            count: 0
          })
        }
        awardsMap.get(award.catalogue_id).count += 1
      })
    }
  })

  return Array.from(awardsMap.values()).sort((a, b) => b.count - a.count)
})
</script>

<template>
  <div class="max-w-4xl mx-auto space-y-4">

    <div v-if="isLoading" class="card text-center py-16 text-main/50 text-sm font-medium">
      正在讀取人物資料...
    </div>

    <template v-else-if="agent">
      <div class="mb-4">
        <!-- Back Link -->
        <router-link to="/agents" class="back-link">
          ← 返回人物列表
        </router-link>
      </div>

      <div class="flex flex-col md:flex-row gap-4 items-start pb-12">

        <!-- Left: Main Content -->
        <div class="w-full md:w-7/12 lg:w-8/12 flex flex-col gap-5 md:gap-6">

          <!-- Personal Info -->
          <section class="card relative">
            <h1 class="text-2xl font-medium text-main mb-2">
              <span>{{ agent.name }}</span>
            </h1>

            <div v-if="agent.aliases && agent.aliases.length > 0" class="text-sm text-main/50 mb-4">
              {{ agent.aliases.map((a: any) => a.name).join(' · ') }}
            </div>

            <p class="text-sm text-main leading-relaxed whitespace-pre-wrap border-t border-main/10 pt-4">{{ agent.about || '暫無簡歷提供。' }}</p>

            <!-- Links -->
            <div v-if="agent.links && agent.links.length > 0" class="flex flex-wrap gap-4 mt-4">
              <a
                v-for="link in agent.links"
                :key="link.id"
                :href="link.url"
                target="_blank"
                rel="noopener noreferrer"
                class="text-sm text-primary hover:text-primary/70 transition-colors"
              >
                ↗ {{ link.label}}
              </a>
            </div>
          </section>

          <!-- Participated Works (Flat List) -->
          <section class="card relative">
            <h2 class="section-label">歷年作品</h2>

            <div v-if="agent.participated_works && agent.participated_works.length > 0" class="flex flex-col">
              <router-link
                v-for="work in agent.participated_works" :key="work.id"
                :to="`/works/${work.id}`"
                class="list-row group cursor-pointer"
              >
                <span class="font-mono text-sm text-main/50 w-12 shrink-0 pt-0.5">{{ work.year || '-' }}</span>
                <div class="flex-1 min-w-0 flex flex-col gap-1.5">
                  <span class="text-base font-medium text-main group-hover:text-primary transition-colors">{{ work.title }}</span>
                  <span v-if="work.title_en" class="text-sm text-main/40">{{ work.title_en }}</span>
                  <span class="text-sm text-main/60">{{ work.work_length || '-' }} · {{ work.media_type || '-' }}</span>
                </div>
                <span class="shrink-0 pt-0.5 text-sm font-medium text-primary">{{ work.roles.join('、') }}</span>
              </router-link>
            </div>
            <div v-else class="text-sm text-main/50 py-3">尚無關聯的歷年作品。</div>
          </section>

          <!-- Participated Publications (Flat List) -->
          <section v-if="agent.participated_publications && agent.participated_publications.length > 0" class="card relative">
            <h2 class="section-label">出版與其他參與</h2>

            <div class="flex flex-col">
              <div
                v-for="pub in agent.participated_publications" :key="pub.id"
                class="list-row group"
              >
                <span class="font-mono text-sm text-main/50 w-12 shrink-0 pt-0.5">{{ pub.year || '-' }}</span>
                <div class="flex-1 min-w-0 flex flex-col gap-1.5">
                  <span class="text-base font-medium text-main">{{ pub.title }}</span>
                  <span class="text-sm text-main/60">{{ pub.publisher || '-' }}</span>
                </div>
                <span class="shrink-0 pt-0.5 text-sm font-medium text-primary">{{ pub.roles.join('、') }}</span>
              </div>
            </div>
          </section>

        </div>

        <!-- Right: Sidebar -->
        <aside class="w-full md:w-5/12 lg:w-4/12 card shrink-0 md:sticky md:top-4 flex flex-col divide-y divide-main/10">

          <div class="py-4 first:pt-0 flex flex-col gap-1.5">
            <span class="text-xs font-medium tracking-widest uppercase text-main/40">作品總數</span>
            <span class="text-sm text-main">{{ totalWorksCount }}</span>
          </div>

          <div class="py-4 flex flex-col gap-1.5">
            <span class="text-xs font-medium tracking-widest uppercase text-main/40">活躍年份</span>
            <span class="font-mono text-sm text-main">{{ activeYears }}</span>
          </div>

          <div class="py-4 flex flex-col gap-3">
            <div class="text-xs font-medium tracking-widest uppercase text-main/40 flex items-center justify-between">
              常見標籤
            </div>

            <div v-if="agent.top_concepts && agent.top_concepts.length > 0" class="flex flex-wrap gap-2">
              <router-link
                v-for="concept in displayedConcepts"
                :key="concept.slug"
                :to="`/concepts/${concept.slug}`"
                class="tag !gap-1.5"
              >
                <span>{{ concept.name }}</span>
                <span class="font-mono opacity-50 pt-px">{{ concept.works_count }}</span>
              </router-link>

              <!-- Show More Bubble -->
              <button
                v-if="hiddenConceptsCount > 0 && !isConceptsExpanded"
                @click="isConceptsExpanded = true"
                class="tag !border-dashed !text-primary hover:!bg-primary/5"
              >
                + {{ hiddenConceptsCount }} 更多
              </button>
              <button
                v-if="isConceptsExpanded"
                @click="isConceptsExpanded = false"
                class="tag !border-dashed !text-primary hover:!bg-primary/5"
              >
                - 收合
              </button>
            </div>
            <div v-else class="text-sm text-main/50">該人物尚未與任何概念建立關聯。</div>
          </div>

          <!-- Awards Tag Cloud -->
          <div v-if="personAwards.length > 0" class="py-4 last:pb-0 flex flex-col gap-3">
            <div class="text-xs font-medium tracking-widest uppercase text-main/40 flex items-center justify-between">
              相關獎項
            </div>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="award in personAwards"
                :key="award.id"
                class="tag !gap-1.5 cursor-default"
              >
                <span>{{ award.title }}</span>
                <span v-if="award.count > 1" class="font-mono opacity-50 pt-px">{{ award.count }}</span>
              </span>
            </div>
          </div>

        </aside>

      </div>
    </template>

  </div>
</template>
