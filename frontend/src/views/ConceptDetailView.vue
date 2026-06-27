<script setup lang="ts">
import { ref, computed } from 'vue'
import { useSpoiler } from '../composables/useSpoiler'
import ConceptTag from '../components/ConceptTag.vue'
import BackLink from '../components/BackLink.vue'
import HoverListItem from '../components/HoverListItem.vue'
import SectionTitle from '../components/SectionTitle.vue'
import ListState from '../components/ListState.vue'
import { useDocumentMeta } from '../composables/useDocumentTitle'
import { fetchConceptDetail } from '../api/concepts'
import { useApiDetail } from '../composables/useApiDetail'
import { getYearRange } from '../utils/formatters'

const { isSpoilerProtected, revealedSpoilers, revealSpoiler, clearRevealedSpoilers } = useSpoiler()
const isExamplesExpanded = ref(false)

const {
  data: concept,
  isLoading,
  hasError,
} = useApiDetail((params) => fetchConceptDetail(params.slug as string), {
  onRefetch: () => {
    isExamplesExpanded.value = false
    clearRevealedSpoilers()
  },
})

useDocumentMeta(
  () => concept.value?.name,
  () => concept.value?.description?.slice(0, 160),
)

const activeFilter = ref<'all' | 'original' | 'licensed'>('all')

const validWorkConcepts = computed(() => {
  if (!concept.value?.work_concepts) return []
  return concept.value.work_concepts.filter(
    (item) =>
      item.description &&
      item.description.trim() !== '' &&
      (activeFilter.value === 'all' || item.provenance === activeFilter.value),
  )
})

const yearRange = computed(() => getYearRange(concept.value?.work_concepts || []))
</script>

<template>
  <div class="mx-auto max-w-4xl">
    <ListState
      :loading="isLoading"
      :error="hasError"
      size="sm"
      loading-text="正在讀取概念資料..."
    />

    <template v-if="concept">
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
              {{ concept.description || '暫無此概念的簡介。' }}
            </p>

          </section>

          <!-- ── Application Examples ── -->
          <section class="mt-12">
            <SectionTitle class="mb-3">
              概念範例
              <template #action>
                <div class="flex items-center gap-2 text-sm">
                  <button
                    class="transition-colors"
                    :class="
                      activeFilter === 'all'
                        ? 'text-primary font-medium'
                        : 'text-main/50 hover:text-main'
                    "
                    @click="activeFilter = 'all'"
                  >
                    全部
                  </button>
                  <span class="text-main/20">/</span>
                  <button
                    class="transition-colors"
                    :class="
                      activeFilter === 'original'
                        ? 'text-primary font-medium'
                        : 'text-main/50 hover:text-main'
                    "
                    @click="activeFilter = 'original'"
                  >
                    原創
                  </button>
                  <span class="text-main/20">/</span>
                  <button
                    class="transition-colors"
                    :class="
                      activeFilter === 'licensed'
                        ? 'text-primary font-medium'
                        : 'text-main/50 hover:text-main'
                    "
                    @click="activeFilter = 'licensed'"
                  >
                    代理
                  </button>
                </div>
              </template>
            </SectionTitle>

            <div
              v-if="validWorkConcepts.length > 0"
              class="flex flex-col"
            >
              <div
                v-for="(item, index) in validWorkConcepts"
                v-show="index < 5 || isExamplesExpanded"
                :key="item.id"
                class="border-main/10 flex flex-col gap-1.5 border-b py-4 last:border-0"
              >
                <div class="flex items-baseline justify-between gap-2">
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
                  <span
                    v-if="item.provenance === 'original' || item.provenance === 'licensed'"
                    class="text-main/40 shrink-0 text-xs"
                  >
                    {{ item.provenance === 'original' ? '原創' : '代理' }}
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

              <!-- Expand Button -->
              <button
                v-if="validWorkConcepts.length > 5 && !isExamplesExpanded"
                class="bg-main/3 hover:bg-primary/3 hover:text-primary text-main/60 w-full py-3 text-center text-sm transition-colors"
                @click="isExamplesExpanded = true"
              >
                ↓ 展開其餘 {{ validWorkConcepts.length - 5 }} 個範例
              </button>
            </div>
            <div
              v-else
              class="flex flex-col items-center gap-2 py-10 text-center"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.2"
                stroke="currentColor"
                class="text-main/15 h-10 w-10"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M3.75 9.776c.112-.017.227-.026.344-.026h15.812c.117 0 .232.009.344.026m-16.5 0a2.25 2.25 0 0 0-1.883 2.542l.857 6a2.25 2.25 0 0 0 2.227 1.932H19.05a2.25 2.25 0 0 0 2.227-1.932l.857-6a2.25 2.25 0 0 0-1.883-2.542m-16.5 0V6A2.25 2.25 0 0 1 6 3.75h3.879a1.5 1.5 0 0 1 1.06.44l2.122 2.12a1.5 1.5 0 0 0 1.06.44H18A2.25 2.25 0 0 1 20.25 9v.776"
                />
              </svg>
              <span class="text-main/35 text-sm">目前未收錄此概念範例。</span>
            </div>

            <!-- Link to all works -->
            <div class="mt-6">
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
          class="mt-6 flex w-full shrink-0 flex-col gap-8 md:sticky md:top-24 md:mt-0 md:w-5/12 lg:w-4/12"
        >
          <!-- Aliases -->
          <div v-if="concept.aliases && concept.aliases.length > 0">
            <SectionTitle class="mb-2">概念別稱</SectionTitle>
            <div class="text-main/70 text-sm leading-relaxed">
              {{ concept.aliases.map((a) => a.name).join(' / ') }}
            </div>
          </div>
          <!-- Year range -->
          <div>
            <SectionTitle class="mb-2">出現年份</SectionTitle>
            <div class="flex items-baseline gap-2">
              <span class="text-main/70 text-sm">{{ yearRange.min ?? '—' }}</span>
              <span class="text-main/30 text-xs">—</span>
              <span class="text-main/70 text-sm">{{ yearRange.max ?? '—' }}</span>
            </div>
          </div>

          <!-- Related Concepts -->
          <div v-if="concept.related_concepts && concept.related_concepts.length > 0">
            <SectionTitle class="mb-3">相關概念</SectionTitle>
            <div class="flex flex-wrap gap-1.5">
              <ConceptTag
                v-for="related in concept.related_concepts"
                :key="related.slug"
                :concept="related"
              />
            </div>
          </div>

          <!-- External Links -->
          <div v-if="concept.links && concept.links.length > 0">
            <SectionTitle class="mb-2">參考連結</SectionTitle>
            <div>
              <HoverListItem
                v-for="link in concept.links"
                :key="link.id"
                tag="a"
                :href="link.url"
                target="_blank"
                rel="noopener noreferrer"
                class="block no-underline"
              >
                <div class="flex items-center justify-between gap-2 py-2.5">
                  <span class="text-main/70 group-hover:text-primary text-sm transition-colors">{{ link.title }}</span>
                  <span class="text-main/40 group-hover:text-primary shrink-0 text-sm transition-colors">↗</span>
                </div>
              </HoverListItem>
            </div>
          </div>
        </aside>
      </div>
    </template>
  </div>
</template>
