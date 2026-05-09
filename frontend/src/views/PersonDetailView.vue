<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'
import ConceptTag from '../components/ConceptTag.vue'

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
  <div class="max-w-4xl mx-auto">

    <div v-if="isLoading" class="text-center py-16 text-main/50 text-sm font-medium">
      正在讀取人物資料...
    </div>

    <template v-else-if="agent">

      <!-- Back Link -->
      <div class="pt-10 mb-9">
        <router-link
          to="/agents"
          class="inline-flex items-center gap-1.5 text-sm font-medium tracking-widest uppercase text-main/40 hover:text-primary transition-colors group no-underline"
        >
          <svg width="13" height="13" viewBox="0 0 14 14" fill="none" class="transition-transform group-hover:-translate-x-0.5">
            <path d="M9 2L4 7L9 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          返回人物列表
        </router-link>
      </div>

      <div class="flex flex-col md:flex-row gap-10 lg:gap-16 items-start pb-20">

        <!-- ── Main Column ── -->
        <div class="w-full md:w-7/12 lg:w-8/12 flex flex-col">

          <!-- Personal Info -->
          <section>
            <h1 class="text-3xl md:text-4xl font-normal leading-snug text-main mb-2">
              {{ agent.name }}
            </h1>

            <div v-if="agent.aliases && agent.aliases.length > 0" class="text-base text-main/40 mb-5">
              {{ agent.aliases.map((a) => a.name).join(' · ') }}
            </div>

            <p class="text-base text-main/80 leading-relaxed whitespace-pre-wrap mb-5">
              {{ agent.about || '暫無簡歷提供。' }}
            </p>

            <!-- External Links -->
            <div v-if="agent.links && agent.links.length > 0" class="flex flex-wrap gap-4">
              <a
                v-for="link in agent.links"
                :key="link.id"
                :href="link.url"
                target="_blank"
                rel="noopener noreferrer"
                class="text-base text-primary hover:opacity-70 transition-opacity no-underline"
              >
                ↗ {{ link.label }}
              </a>
            </div>
          </section>

          <!-- ── Participated Works ── -->
          <section class="mt-12">
            <div class="flex items-center gap-3 mb-5">
              <span class="text-sm font-medium tracking-widest uppercase text-main/40 whitespace-nowrap">歷年作品</span>
              <div class="flex-1 border-t border-main/10"></div>
            </div>

            <div v-if="agent.participated_works && agent.participated_works.length > 0" class="flex flex-col">
              <router-link
                v-for="work in agent.participated_works"
                :key="work.id"
                :to="`/works/${work.id}`"
                class="group flex items-start gap-4 py-4 border-b border-main/10 last:border-0 hover:bg-primary/5 hover:-mx-3 hover:px-3 transition-colors no-underline"
              >
                <span class="font-mono text-xs text-main/50 w-10 shrink-0 pt-0.5">{{ work.year || '-' }}</span>

                <div class="flex-1 min-w-0">
                  <span class="text-base font-medium text-main group-hover:text-primary transition-colors block mb-0.5">
                    {{ work.title }}
                  </span>
                  <span v-if="work.title_en" class="text-xs text-main/40 block mb-1">{{ work.title_en }}</span>
                  <!-- Gray badge for media metadata -->
                  <span class="font-mono text-[10px] tracking-wide text-main/50 bg-main/5 px-1.5 py-0.5">
                    {{ [work.work_length, work.media_type].filter(Boolean).join(' · ') || '-' }}
                  </span>
                </div>

                <span class="shrink-0 pt-0.5 text-xs font-medium text-primary">
                  {{ work.roles.join('、') }}
                </span>
              </router-link>
            </div>
            <div v-else class="text-base text-main/40 py-3">尚無關聯的歷年作品。</div>
          </section>

          <!-- ── Participated Publications ── -->
          <section v-if="agent.participated_publications && agent.participated_publications.length > 0" class="mt-10">
            <div class="flex items-center gap-3 mb-5">
              <span class="text-sm font-medium tracking-widest uppercase text-main/40 whitespace-nowrap">出版與其他參與</span>
              <div class="flex-1 border-t border-main/10"></div>
            </div>

            <div class="flex flex-col">
              <div
                v-for="pub in agent.participated_publications"
                :key="pub.id"
                class="group flex items-start gap-4 py-4 border-b border-main/10 last:border-0"
              >
                <span class="font-mono text-xs text-main/50 w-10 shrink-0 pt-0.5">{{ pub.year || '-' }}</span>

                <div class="flex-1 min-w-0">
                  <span class="text-base font-medium text-main block mb-0.5">{{ pub.title }}</span>
                  <span class="text-xs text-main/50">{{ pub.publisher || '-' }}</span>
                </div>

                <span class="shrink-0 pt-0.5 text-xs font-medium text-primary">
                  {{ pub.roles.join('、') }}
                </span>
              </div>
            </div>
          </section>

        </div>

        <!-- ── Sidebar ── -->
        <aside class="w-full md:w-5/12 lg:w-4/12 shrink-0 flex flex-col gap-8 md:sticky md:top-8 mt-6 md:mt-0">

          <!-- Work count -->
          <div>
            <div class="flex items-center gap-3 mb-2">
              <span class="text-sm font-medium tracking-widest uppercase text-main/40 whitespace-nowrap">作品總數</span>
              <div class="flex-1 border-t border-main/10"></div>
            </div>
            <span class="font-mono text-xl text-main">{{ totalWorksCount }}</span>
          </div>

          <!-- Active years -->
          <div>
            <div class="flex items-center gap-3 mb-2">
              <span class="text-sm font-medium tracking-widest uppercase text-main/40 whitespace-nowrap">活躍年份</span>
              <div class="flex-1 border-t border-main/10"></div>
            </div>
            <span class="font-mono text-base text-main">{{ activeYears }}</span>
          </div>

          <!-- Top Concepts -->
          <div>
            <div class="flex items-center gap-3 mb-3">
              <span class="text-sm font-medium tracking-widest uppercase text-main/40 whitespace-nowrap">常見標籤</span>
              <div class="flex-1 border-t border-main/10"></div>
            </div>

            <div v-if="agent.top_concepts && agent.top_concepts.length > 0" class="flex flex-wrap gap-1.5">
              <ConceptTag
                v-for="concept in displayedConcepts"
                :key="concept.slug"
                :concept="concept"
              />

              <button
                v-if="hiddenConceptsCount > 0 && !isConceptsExpanded"
                @click="isConceptsExpanded = true"
                class="inline-flex items-center text-xs text-primary border border-dashed border-primary/30 px-2.5 py-1 hover:bg-primary/5 transition-all whitespace-nowrap"
              >
                + {{ hiddenConceptsCount }} 更多
              </button>
              <button
                v-if="isConceptsExpanded"
                @click="isConceptsExpanded = false"
                class="inline-flex items-center text-xs text-primary border border-dashed border-primary/30 px-2.5 py-1 hover:bg-primary/5 transition-all whitespace-nowrap"
              >
                − 收合
              </button>
            </div>
            <div v-else class="text-sm text-main/40">尚未與任何概念建立關聯。</div>
          </div>

          <!-- Awards -->
          <div v-if="personAwards.length > 0">
            <div class="flex items-center gap-3 mb-3">
              <span class="text-sm font-medium tracking-widest uppercase text-main/40 whitespace-nowrap">相關獎項</span>
              <div class="flex-1 border-t border-main/10"></div>
            </div>
            <div class="flex flex-wrap gap-1.5">
              <span
                v-for="award in personAwards"
                :key="award.id"
                class="inline-flex items-center gap-1.5 text-xs text-main/60 border border-main/15 px-2.5 py-1 whitespace-nowrap cursor-default"
              >
                <span>{{ award.title }}</span>
                <span v-if="award.count > 1" class="font-mono text-[10px] text-main/40">{{ award.count }}</span>
              </span>
            </div>
          </div>

        </aside>
      </div>
    </template>

  </div>
</template>
