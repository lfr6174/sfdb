<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'
import { useSpoiler } from '../composables/useSpoiler'
import ConceptTag from '../components/ConceptTag.vue'

const route = useRoute()
const work = ref<any>(null)
const isLoading = ref(true)
const isConceptsExpanded = ref(false)

const { isSpoilerProtected, revealedSpoilers, revealSpoiler } = useSpoiler()

const fetchWorkDetail = async () => {
  isLoading.value = true
  try {
    const response = await api.get(`/works/${route.params.id}/`)
    work.value = response.data
  } catch (error) {
    console.error('Failed to fetch work details:', error)
  } finally {
    isLoading.value = false
  }
}

const visibleIsbns = ref<Set<number>>(new Set())
const toggleIsbn = (id: number) => {
  if (visibleIsbns.value.has(id)) {
    visibleIsbns.value.delete(id)
  } else {
    visibleIsbns.value.add(id)
  }
}

onMounted(() => {
  fetchWorkDetail()
})

// Manage displayed concepts for the "show more" functionality
const DISPLAY_LIMIT = 15
const displayedConcepts = computed(() => {
  if (!work.value?.work_concepts) return []
  if (isConceptsExpanded.value) return work.value.work_concepts
  return work.value.work_concepts.slice(0, DISPLAY_LIMIT)
})

const hiddenConceptsCount = computed(() => {
  if (!work.value?.work_concepts) return 0
  return Math.max(0, work.value.work_concepts.length - DISPLAY_LIMIT)
})

const conceptDescriptions = computed(() => {
  if (!work.value?.work_concepts) return []
  return work.value.work_concepts.filter((wc: any) => !!wc.description)
})

</script>

<template>
  <div class="max-w-4xl mx-auto">

    <div v-if="isLoading" class="text-center py-16 text-main/50 text-sm font-medium">
      正在讀取作品資料...
    </div>

    <template v-else-if="work">

      <!-- Back Link -->
      <div class="pt-10 mb-9">
        <router-link
          to="/works"
          class="inline-flex items-center gap-1.5 text-sm font-medium tracking-widest uppercase text-main/40 hover:text-primary transition-colors group no-underline"
        >
          <svg width="13" height="13" viewBox="0 0 14 14" fill="none" class="transition-transform group-hover:-translate-x-0.5">
            <path d="M9 2L4 7L9 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          返回作品列表
        </router-link>
      </div>

      <div class="flex flex-col md:flex-row gap-10 lg:gap-16 items-start pb-20">

        <!-- ── Main Column ── -->
        <div class="w-full md:w-7/12 lg:w-8/12 flex flex-col">
          <section>

            <!-- Media type pill (gray filled badge, not a tag) -->
            <div v-if="work.work_length_display || work.media_type_display" class="mb-4">
              <span class="font-mono text-xs tracking-wider uppercase text-main/50 bg-main/5 px-2 py-1 inline-block">
                {{ work.work_length_display || '' }}{{ work.media_type_display || '' }}
              </span>
            </div>

            <!-- Title -->
            <h1 class="text-3xl md:text-4xl font-normal leading-snug text-main mb-4">
              {{ work.title }}
            </h1>

            <!-- Meta row -->
            <div class="flex flex-wrap items-center gap-x-2 gap-y-1 text-base text-main/70 mb-6">
              <span v-if="work.credit && work.credit.length" class="flex flex-wrap items-center gap-x-0.5">
                <template v-for="(group, gIdx) in work.credit" :key="gIdx">
                  <template v-for="(agent, aIdx) in group.agents" :key="aIdx">
                    <router-link v-if="agent.id" :to="`/agents/${agent.id}`" class="text-primary hover:opacity-70 transition-opacity">{{ agent.text }}</router-link>
                    <span v-else class="text-main/80">{{ agent.text }}</span>
                    <span v-if="aIdx < group.agents.length - 1">、</span>
                  </template>
                  <span v-if="group.role" class="text-main/40 ml-0.5">{{ group.role }}</span>
                  <span v-if="gIdx < work.credit.length - 1" class="ml-1 mr-0.5">；</span>
                </template>
              </span>
              <span v-else class="text-main/35">-</span>

              <span class="text-main/20">·</span>
              <span>{{ work.year || '未知年份' }}</span>

              <template v-if="work.series">
                <span class="text-main/20">·</span>
                <span>{{ work.series.title }}</span>
              </template>
            </div>

            <!-- Synopsis -->
            <p class="text-base text-main/80 leading-relaxed whitespace-pre-wrap mb-8">
              {{ work.description || '暫無簡述提供。' }}
            </p>

            <!-- Concept Tags -->
            <div v-if="work.work_concepts && work.work_concepts.length > 0" class="flex flex-wrap gap-1.5">
              <ConceptTag
                v-for="wc in displayedConcepts"
                :key="wc.concept.slug"
                :concept="wc.concept"
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
          </section>

          <!-- ── Concept Descriptions ── -->
          <section v-if="conceptDescriptions.length > 0" class="mt-12 pt-2">

            <!-- Section eyebrow: label inline with rule -->
            <div class="flex items-center gap-3 mb-5">
              <span class="text-sm font-medium tracking-widest uppercase text-main/40 whitespace-nowrap">概念應用詳述</span>
              <div class="flex-1 border-t border-main/10"></div>
            </div>

            <div class="flex flex-col">
              <div
                v-for="wc in conceptDescriptions"
                :key="wc.id"
                class="grid grid-cols-1 md:grid-cols-[7.5rem_1fr] gap-3 md:gap-5 py-4 border-b border-main/10 last:border-0 hover:bg-primary/5 hover:-mx-3 hover:px-3 transition-colors"
              >
                <div class="pt-0.5">
                  <ConceptTag :concept="wc.concept" />
                </div>
                <p
                  :class="[
                    'text-base leading-relaxed',
                    isSpoilerProtected && !revealedSpoilers.has(wc.id)
                      ? 'blur-sm hover:blur-[2px] transition-all duration-200 text-main/40 cursor-pointer'
                      : 'text-main/75'
                  ]"
                  @click="isSpoilerProtected && !revealedSpoilers.has(wc.id) && revealSpoiler(wc.id)"
                  :title="isSpoilerProtected && !revealedSpoilers.has(wc.id) ? '點擊顯示劇透內容' : ''"
                >
                  {{ wc.description }}
                </p>
              </div>
            </div>
          </section>
        </div>

        <!-- ── Sidebar ── -->
        <aside class="w-full md:w-5/12 lg:w-4/12 shrink-0 flex flex-col gap-10 md:sticky md:top-8 mt-6 md:mt-0">

          <!-- Publications -->
          <section v-if="work.publications && work.publications.length > 0">
            <div class="flex items-center gap-3 mb-4">
              <span class="text-sm font-medium tracking-widest uppercase text-main/40 whitespace-nowrap">出版與發行</span>
              <div class="flex-1 border-t border-main/10"></div>
            </div>

            <div class="flex flex-col">
              <div
                v-for="pub in work.publications"
                :key="pub.manifestation_id || pub.id"
                class="group flex items-start gap-3 py-3 border-b border-main/10 last:border-0 cursor-pointer hover:bg-primary/5 hover:-mx-3 hover:pl-3 hover:pr-1 transition-colors relative"
                @click="toggleIsbn(pub.manifestation_id || pub.id)"
              >
                <!-- Accent line -->
                <div class="absolute -left-3 top-0 bottom-0 w-[2px] bg-transparent group-hover:bg-primary transition-colors"></div>

                <!-- Left: year + media badge -->
                <div class="flex flex-col shrink-0 items-start gap-1.5 pt-0.5 w-11">
                  <span class="font-mono text-xs text-main/50">{{ pub.year || '-' }}</span>
                  <!-- Gray filled badge — visually distinct from concept tags -->
                  <span
                    v-if="pub.media_display"
                    class="font-mono text-[10px] tracking-wide text-main/50 bg-main/5 px-1.5 py-0.5 whitespace-nowrap"
                  >
                    {{ pub.media_display }}
                  </span>
                </div>

                <div class="flex-1 min-w-0">
                  <span class="text-base font-medium text-main block mb-0.5">{{ pub.title }}</span>

                  <div
                    v-if="(pub.credit && pub.credit.length) || pub.publisher?.name"
                    class="text-xs text-main/50 flex flex-wrap gap-x-1 mt-0.5"
                  >
                    <template v-if="pub.credit && pub.credit.length">
                      <template v-for="(group, gIdx) in pub.credit" :key="gIdx">
                        <template v-for="(agent, aIdx) in group.agents" :key="aIdx">
                          {{ agent.text }}<span v-if="aIdx < group.agents.length - 1">、</span>
                        </template>
                        <span v-if="group.role">{{ group.role }}</span>
                        <span v-if="gIdx < pub.credit.length - 1">；</span>
                      </template>
                      <span v-if="pub.publisher?.name" class="text-main/25 px-0.5">/</span>
                    </template>
                    <span v-if="pub.publisher?.name">{{ pub.publisher.name }}</span>
                  </div>

                  <div
                    v-if="pub.manifestations?.length === 1 && pub.manifestation_display_name && pub.manifestation_display_name !== pub.title"
                    class="text-xs text-primary/80 mt-0.5"
                  >
                    ↳ {{ pub.manifestation_display_name }}
                  </div>

                  <div
                    v-if="visibleIsbns.has(pub.manifestation_id || pub.id) && pub.isbn"
                    class="font-mono text-xs text-main/40 mt-2 selection:bg-primary/20"
                    @click.stop
                  >
                    ISBN {{ pub.isbn }}
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- Catalogues -->
          <section v-if="work.work_catalogues && work.work_catalogues.length > 0">
            <div class="flex items-center gap-3 mb-4">
              <span class="text-sm font-medium tracking-widest uppercase text-main/40 whitespace-nowrap">收錄與獲獎</span>
              <div class="flex-1 border-t border-main/10"></div>
            </div>

            <div class="flex flex-col">
              <div
                v-for="entry in work.work_catalogues"
                :key="entry.id"
                class="group flex items-start gap-3 py-3 border-b border-main/10 last:border-0 cursor-pointer hover:bg-primary/5 hover:-mx-3 hover:pl-3 hover:pr-1 transition-colors relative"
              >
                <div class="absolute -left-3 top-0 bottom-0 w-[2px] bg-transparent group-hover:bg-primary transition-colors"></div>

                <div class="flex flex-col shrink-0 items-start gap-1.5 pt-0.5 w-11">
                  <span class="font-mono text-xs text-main/50">{{ entry.catalogue.year || '-' }}</span>
                  <span
                    v-if="entry.catalogue.catalogue_type_display"
                    class="font-mono text-[10px] tracking-wide text-main/50 bg-main/5 px-1.5 py-0.5 whitespace-nowrap"
                  >
                    {{ entry.catalogue.catalogue_type_display }}
                  </span>
                </div>

                <div class="flex-1 min-w-0">
                  <router-link
                    v-if="entry.catalogue.id"
                    :to="`/catalogues/${entry.catalogue.id}`"
                    class="text-base font-medium text-main hover:text-primary transition-colors block mb-0.5 no-underline"
                  >
                    {{ entry.catalogue.title }}
                  </router-link>
                  <span v-else class="text-base font-medium text-main block mb-0.5">
                    {{ entry.catalogue.title }}
                  </span>

                  <div
                    v-if="entry.category || entry.status_display || entry.note"
                    class="text-xs text-main/50 mt-0.5 flex flex-wrap items-center gap-x-1.5"
                  >
                    <span v-if="entry.category" class="font-medium text-main/65">{{ entry.category }}</span>
                    <span v-if="entry.category && entry.status_display" class="text-main/20">·</span>
                    <span
                      v-if="entry.status_display"
                      :class="['得獎','首獎','入選'].includes(entry.status_display) ? 'text-primary' : 'text-main/35'"
                    >
                      {{ entry.status_display }}
                    </span>
                    <span v-if="entry.note" class="text-main/40">({{ entry.note }})</span>
                  </div>
                </div>
              </div>
            </div>
          </section>

        </aside>
      </div>
    </template>
  </div>
</template>
