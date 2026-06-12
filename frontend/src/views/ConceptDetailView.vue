<script setup lang="ts">
import { ref, computed } from 'vue'
import { useSpoiler } from '../composables/useSpoiler'
import ConceptTag from '../components/ConceptTag.vue'
import BackLink from '../components/BackLink.vue'
import SectionTitle from '../components/SectionTitle.vue'
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

const validWorkConcepts = computed(() => {
  if (!concept.value?.work_concepts) return []
  return concept.value.work_concepts.filter(
    (item) => item.description && item.description.trim() !== '',
  )
})

const yearRange = computed(() => getYearRange(concept.value?.work_concepts || []))
</script>

<template>
  <div class="mx-auto max-w-4xl">
    <div
      v-if="isLoading"
      class="text-main/50 animate-pulse py-16 text-center text-sm font-medium"
    >
      正在讀取概念資料...
    </div>

    <div
      v-else-if="hasError"
      class="text-main/50 py-16 text-center text-sm font-medium"
    >
      資料讀取發生問題，請稍後再試。
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
                v-for="(item, index) in validWorkConcepts"
                v-show="index < 5 || isExamplesExpanded"
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

              <!-- Expand Button -->
              <button
                v-if="validWorkConcepts.length > 5 && !isExamplesExpanded"
                class="bg-main/3 hover:bg-primary/3 hover:text-primary text-main/60 w-full py-3 text-center text-sm transition-colors"
                @click="isExamplesExpanded = true"
              >
                ↓ 展開其餘 {{ validWorkConcepts.length - 5 }} 個應用範例
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
              <span class="text-main/35 text-sm">目前尚無收錄此概念的應用範例。</span>
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
          <!-- Works count -->
          <div>
            <SectionTitle class="mb-2">收錄作品數</SectionTitle>
            <span class="text-main text-xl">{{ concept.works_count || 0 }}</span>
          </div>

          <!-- Year range -->
          <div>
            <SectionTitle class="mb-2">出現年份</SectionTitle>
            <div class="flex items-baseline gap-2">
              <span class="text-main text-base">{{ yearRange.min ?? '—' }}</span>
              <span class="text-main/30 text-xs">—</span>
              <span class="text-main text-base">{{ yearRange.max ?? '—' }}</span>
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
