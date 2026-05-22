<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'
import { useSpoiler } from '../composables/useSpoiler'
import ConceptTag from '../components/ConceptTag.vue'
import BackLink from '../components/BackLink.vue'
import SectionTitle from '../components/SectionTitle.vue'
import { useDocumentTitle } from '../composables/useDocumentTitle'

const route = useRoute()

const concept = ref<any>(null)
const isLoading = ref(true)

useDocumentTitle(() => concept.value?.name)

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
  return concept.value.work_concepts.filter(
    (item: any) => item.description && item.description.trim() !== '',
  )
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
watch(
  () => route.params.slug,
  (newSlug, oldSlug) => {
    if (newSlug && newSlug !== oldSlug) {
      clearRevealedSpoilers()
      fetchConceptDetail()
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  },
)

onMounted(() => {
  fetchConceptDetail()
})
</script>

<template>
  <div class="mx-auto max-w-4xl">
    <div
      v-if="isLoading"
      class="text-main/50 py-16 text-center text-sm font-medium"
    >
      正在讀取概念資料...
    </div>

    <template v-else-if="concept">
      <!-- Back Link -->
      <div class="mb-9 pt-6 md:pt-10">
        <BackLink
          to="/concepts"
          text="返回概念探索"
        />
      </div>

      <div class="flex flex-col items-start gap-10 pb-20 md:flex-row lg:gap-16">
        <!-- ── Main Column ── -->
        <div class="flex w-full flex-col md:w-7/12 lg:w-8/12">
          <!-- Concept Info -->
          <section>
            <h1 class="text-main mb-6 text-2xl leading-snug font-normal md:text-3xl">
              {{ concept.name }}
            </h1>

            <p class="text-main/80 mb-5 text-base leading-relaxed whitespace-pre-wrap">
              {{ concept.description || '目前暫無關於此概念的詳細描述。' }}
            </p>

            <!-- External Links -->
            <div
              v-if="concept.links && concept.links.length > 0"
              class="flex flex-wrap gap-4"
            >
              <a
                v-for="link in concept.links"
                :key="link.id"
                :href="link.url"
                target="_blank"
                rel="noopener noreferrer"
                class="text-primary text-base no-underline transition-opacity hover:opacity-70"
              >
                ↗ {{ link.title }}
              </a>
            </div>
          </section>

          <!-- ── Application Examples ── -->
          <section class="mt-12">
            <SectionTitle class="mb-3">概念應用範例</SectionTitle>

            <div
              v-if="validWorkConcepts.length > 0"
              class="flex flex-col"
            >
              <div
                v-for="item in validWorkConcepts"
                :key="item.id"
                class="border-main/10 flex flex-col gap-1.5 border-b py-4 last:border-0"
              >
                <div class="flex items-baseline gap-2">
                  <router-link
                    :to="`/works/${item.work}`"
                    class="text-main hover:text-primary text-sm font-medium no-underline transition-colors"
                  >
                    {{ item.work_title || '未知作品' }}
                  </router-link>
                  <span class="text-main/35 shrink-0 text-xs">
                    {{ item.year || '-' }}
                  </span>
                </div>

                <p
                  v-if="isSpoilerProtected && !revealedSpoilers.has(item.id)"
                  class="text-main/40 cursor-pointer text-sm leading-relaxed blur-sm transition-all duration-200 select-none hover:blur-[2px]"
                  title="點擊顯示劇透內容"
                  @click="revealSpoiler(item.id)"
                >
                  {{ item.description }}
                </p>
                <p
                  v-else
                  class="text-main/55 text-sm leading-relaxed"
                >
                  {{ item.description }}
                </p>
              </div>
            </div>
            <div
              v-else
              class="text-main/40 py-3 text-sm"
            >
              目前尚無收錄此概念的應用範例。
            </div>

            <!-- Link to all works -->
            <div class="mt-7">
              <router-link
                :to="{ path: '/works', query: { concept: concept.slug } }"
                class="text-primary text-base no-underline transition-opacity hover:opacity-70"
              >
                瀏覽所有與「{{ concept.name }}」相關的作品（共 {{ concept.works_count || 0 }} 部）↗
              </router-link>
            </div>
          </section>
        </div>

        <!-- ── Sidebar ── -->
        <aside
          class="mt-6 flex w-full shrink-0 flex-col gap-8 md:sticky md:top-8 md:mt-0 md:w-5/12 lg:w-4/12"
        >
          <!-- Works count -->
          <div>
            <SectionTitle class="mb-2">收錄作品數</SectionTitle>
            <span class="text-main text-xl">{{ concept.works_count || 0 }}</span>
          </div>

          <!-- Year range -->
          <div>
            <SectionTitle class="mb-2">出現年份</SectionTitle>
            <div class="flex items-baseline gap-2">
              <span class="text-main text-base">{{ earliestYear }}</span>
              <span class="text-main/30 text-xs">—</span>
              <span class="text-main text-base">{{ latestYear }}</span>
            </div>
          </div>

          <!-- Related Concepts -->
          <div>
            <SectionTitle class="mb-3">相關概念</SectionTitle>

            <div
              v-if="concept.related_concepts && concept.related_concepts.length > 0"
              class="flex flex-wrap gap-1.5"
            >
              <ConceptTag
                v-for="related in concept.related_concepts"
                :key="related.slug"
                :concept="related"
              />
            </div>
            <div
              v-else
              class="text-main/40 text-sm"
            >
              尚未與任何概念建立關聯。
            </div>
          </div>
        </aside>
      </div>
    </template>
  </div>
</template>
