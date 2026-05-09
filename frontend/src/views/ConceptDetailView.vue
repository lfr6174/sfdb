<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'
import { useSpoiler } from '../composables/useSpoiler'
import ConceptTag from '../components/ConceptTag.vue'

const route = useRoute()

const concept = ref<any>(null)
const isLoading = ref(true)

const { isSpoilerProtected, revealedSpoilers, revealSpoiler, clearRevealedSpoilers } = useSpoiler()

const fetchConceptDetail = async () => {
  isLoading.value = true
  try {
    const response = await api.get(`/concepts/${route.params.slug}/`)
    concept.value = response.data
  } catch (error) {
    console.error('Failed to fetch concept details:', error)
  } finally {
    isLoading.value = false
  }
}

const validWorkConcepts = computed(() => {
  if (!concept.value?.work_concepts) return []
  return concept.value.work_concepts.filter((item: any) => item.description && item.description.trim() !== '')
})

const earliestYear = computed(() => {
  if (!concept.value?.work_concepts || concept.value.work_concepts.length === 0) return '—'
  const years = concept.value.work_concepts
    .map((w: any) => parseInt(w.year))
    .filter((y: number) => !isNaN(y))
  if (years.length === 0) return '—'
  return Math.min(...years)
})

const latestYear = computed(() => {
  if (!concept.value?.work_concepts || concept.value.work_concepts.length === 0) return '—'
  const years = concept.value.work_concepts
    .map((w: any) => parseInt(w.year))
    .filter((y: number) => !isNaN(y))
  if (years.length === 0) return '—'
  return Math.max(...years)
})

// Refetch data to handle same-route navigation
watch(() => route.params.slug, (newSlug, oldSlug) => {
  if (newSlug && newSlug !== oldSlug) {
    clearRevealedSpoilers()
    fetchConceptDetail()
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
})

onMounted(() => {
  fetchConceptDetail()
})
</script>

<template>
  <div class="max-w-4xl mx-auto">

    <div v-if="isLoading" class="text-center py-16 text-main/50 text-sm font-medium">
      正在讀取概念資料...
    </div>

    <template v-else-if="concept">

      <!-- Back Link -->
      <div class="pt-10 mb-9">
        <router-link
          to="/concepts"
          class="inline-flex items-center gap-1.5 text-xs font-medium tracking-widest uppercase text-main/40 hover:text-primary transition-colors group no-underline"
        >
          <svg width="13" height="13" viewBox="0 0 14 14" fill="none" class="transition-transform group-hover:-translate-x-0.5">
            <path d="M9 2L4 7L9 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          返回概念探索
        </router-link>
      </div>

      <div class="flex flex-col md:flex-row gap-10 lg:gap-16 items-start pb-20">

        <!-- ── Main Column ── -->
        <div class="w-full md:w-7/12 lg:w-8/12 flex flex-col">

          <!-- Concept Info -->
          <section>
            <h1 class="text-3xl md:text-4xl font-normal leading-snug text-main mb-5">
              {{ concept.name }}
            </h1>

            <p class="text-sm text-main/70 leading-loose whitespace-pre-wrap mb-5">
              {{ concept.description || '目前暫無關於此概念的詳細描述。' }}
            </p>

            <!-- External Links -->
            <div v-if="concept.links && concept.links.length > 0" class="flex flex-wrap gap-4">
              <a
                v-for="link in concept.links"
                :key="link.id"
                :href="link.url"
                target="_blank"
                rel="noopener noreferrer"
                class="text-sm text-primary hover:opacity-70 transition-opacity no-underline"
              >
                ↗ {{ link.title }}
              </a>
            </div>
          </section>

          <!-- ── Application Examples ── -->
          <section class="mt-12">
            <div class="flex items-center gap-3 mb-5">
              <span class="text-xs font-medium tracking-widest uppercase text-main/40 whitespace-nowrap">概念應用範例</span>
              <div class="flex-1 border-t border-main/10"></div>
            </div>

            <div v-if="validWorkConcepts.length > 0" class="flex flex-col">
              <div
                v-for="item in validWorkConcepts"
                :key="item.id"
                class="flex items-start gap-4 py-4 border-b border-main/10 last:border-0"
              >
                <span class="font-mono text-xs text-main/50 w-10 shrink-0 pt-0.5">{{ item.year || '-' }}</span>

                <div class="flex-1 min-w-0 flex flex-col gap-2">
                  <router-link
                    :to="`/works/${item.work}`"
                    class="text-sm font-medium text-main hover:text-primary transition-colors no-underline w-fit"
                  >
                    {{ item.work_title || '未知作品' }}
                  </router-link>

                  <p
                    v-if="isSpoilerProtected && !revealedSpoilers.has(item.id)"
                    @click="revealSpoiler(item.id)"
                    class="text-sm leading-relaxed blur-sm hover:blur-[2px] transition-all duration-200 text-main/40 cursor-pointer select-none"
                    title="點擊顯示劇透內容"
                  >
                    {{ item.description }}
                  </p>
                  <p v-else class="text-sm leading-relaxed text-main/70">
                    {{ item.description }}
                  </p>
                </div>
              </div>
            </div>
            <div v-else class="text-sm text-main/40 py-3">目前尚無收錄此概念的應用範例。</div>

            <!-- Link to all works -->
            <div class="mt-7">
              <router-link
                :to="{ path: '/works', query: { concept: concept.slug } }"
                class="text-sm text-primary hover:opacity-70 transition-opacity no-underline"
              >
                瀏覽所有與「{{ concept.name }}」相關的作品（共 {{ concept.works_count || 0 }} 部）↗
              </router-link>
            </div>
          </section>

        </div>

        <!-- ── Sidebar ── -->
        <aside class="w-full md:w-5/12 lg:w-4/12 shrink-0 flex flex-col gap-8 md:sticky md:top-8 mt-6 md:mt-0">

          <!-- Works count -->
          <div>
            <div class="flex items-center gap-3 mb-2">
              <span class="text-xs font-medium tracking-widest uppercase text-main/40 whitespace-nowrap">收錄作品數</span>
              <div class="flex-1 border-t border-main/10"></div>
            </div>
            <span class="font-mono text-base text-main">{{ concept.works_count || 0 }}</span>
          </div>

          <!-- Year range -->
          <div>
            <div class="flex items-center gap-3 mb-2">
              <span class="text-xs font-medium tracking-widest uppercase text-main/40 whitespace-nowrap">出現年份</span>
              <div class="flex-1 border-t border-main/10"></div>
            </div>
            <div class="flex items-baseline gap-2">
              <span class="font-mono text-sm text-main">{{ earliestYear }}</span>
              <span class="text-xs text-main/30">—</span>
              <span class="font-mono text-sm text-main">{{ latestYear }}</span>
            </div>
          </div>

          <!-- Related Concepts -->
          <div>
            <div class="flex items-center gap-3 mb-3">
              <span class="text-xs font-medium tracking-widest uppercase text-main/40 whitespace-nowrap">相關概念</span>
              <div class="flex-1 border-t border-main/10"></div>
            </div>

            <div v-if="concept.related_concepts && concept.related_concepts.length > 0" class="flex flex-wrap gap-1.5">
              <ConceptTag
                v-for="related in concept.related_concepts"
                :key="related.slug"
                :concept="related"
              />
            </div>
            <div v-else class="text-sm text-main/40">尚未與任何概念建立關聯。</div>
          </div>

        </aside>

      </div>
    </template>

  </div>
</template>
