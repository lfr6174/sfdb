<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'
import { useSpoiler } from '../composables/useSpoiler'

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
  <div class="max-w-4xl mx-auto space-y-4">

    <div v-if="isLoading" class="card text-center py-16 text-main/50 text-sm font-medium">
      正在讀取作品資料...
    </div>

    <template v-else-if="work">
      <div class="mb-9">
        <!-- Back Link -->
        <router-link to="/works" class="inline-flex items-center gap-1.5 text-xs font-medium tracking-wide uppercase text-main/40 hover:text-primary transition-colors group no-underline">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" class="inline-block transform transition-transform group-hover:-translate-x-0.5"><path d="M9 2L4 7L9 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
          返回作品列表
        </router-link>
      </div>

      <div class="flex flex-col md:flex-row gap-8 lg:gap-14 items-start pb-16">

        <!-- Main Column -->
        <div class="w-full md:w-7/12 lg:w-8/12 flex flex-col">

          <!-- Header Info & Synopsis Section -->
          <section class="relative">

            <!-- Media type and work length -->
            <div v-if="work.work_length_display || work.media_type_display" class="mb-4 flex flex-wrap gap-2">
              <span class="font-mono text-xs tracking-wider text-main/40 border border-main/10 rounded-sm px-2 py-1 inline-block">
                {{ work.work_length_display || '' }}{{ work.media_type_display || '' }}
              </span>
            </div>

            <h1 class="font-serif text-2xl md:text-3xl font-normal leading-snug text-main mb-4">
              <span>{{ work.title }}</span>
            </h1>

            <!-- Metadata List -->
            <div class="flex flex-wrap items-center gap-x-2.5 gap-y-1.5 text-sm text-main/60 pb-5 mb-5 border-b border-main/10">
              <span v-if="work.credit && work.credit.length" class="flex flex-wrap items-center gap-x-0.5">
                <template v-for="(group, gIdx) in work.credit" :key="gIdx">
                  <template v-for="(agent, aIdx) in group.agents" :key="aIdx">
                    <router-link v-if="agent.id" :to="`/agents/${agent.id}`" class="text-primary hover:opacity-70 transition-opacity">{{ agent.text }}</router-link>
                    <span v-else class="text-main">{{ agent.text }}</span>
                    <span v-if="aIdx < group.agents.length - 1">、</span>
                  </template>
                  <span v-if="group.role" class="text-main/40 ml-1">{{ group.role }}</span>
                  <span v-if="gIdx < work.credit.length - 1" class="ml-1 mr-0.5">；</span>
                </template>
              </span>
              <span v-else>-</span>

              <span class="text-main/20">·</span>
              <span>{{ work.year || '未知年份' }}</span>

              <!-- Series -->
              <template v-if="work.series">
                <span class="text-main/20">·</span>
                <span>{{ work.series.title }}</span>
              </template>
            </div>

            <!-- Synopsis -->
            <p class="text-sm text-main leading-relaxed whitespace-pre-wrap mb-7">{{ work.description || '暫無簡述提供。' }}</p>

            <!-- Concept Tags List -->
            <div v-if="work.work_concepts && work.work_concepts.length > 0" class="flex flex-wrap gap-1.5 mb-2">
              <router-link
                v-for="wc in displayedConcepts"
                :key="wc.concept.slug"
                :to="`/concepts/${wc.concept.slug}`"
                class="inline-flex items-center text-xs text-main/60 border border-main/15 rounded-sm px-2.5 py-1 hover:text-primary hover:bg-primary/5 hover:border-primary/25 transition-all whitespace-nowrap"
              >
                <span>{{ wc.concept.name }}</span>
              </router-link>

              <button v-if="hiddenConceptsCount > 0 && !isConceptsExpanded" @click="isConceptsExpanded = true" class="inline-flex items-center text-xs text-primary border border-primary/30 border-dashed rounded-sm px-2.5 py-1 hover:bg-primary/5 transition-all whitespace-nowrap">
                + {{ hiddenConceptsCount }} 更多
              </button>
              <button v-if="isConceptsExpanded" @click="isConceptsExpanded = false" class="inline-flex items-center text-xs text-primary border border-primary/30 border-dashed rounded-sm px-2.5 py-1 hover:bg-primary/5 transition-all whitespace-nowrap">
                - 收合
              </button>
            </div>
          </section>

          <!-- Concepts Section -->
          <section v-if="conceptDescriptions.length > 0" class="mt-10 pt-10 border-t border-main/10 relative">
            <div class="text-xs font-medium tracking-widest uppercase text-main/40 pb-2.5 border-b border-main/10 mb-5">
              概念應用詳述
            </div>
            <div class="flex flex-col">
              <div v-for="wc in conceptDescriptions" :key="wc.id" class="grid grid-cols-1 md:grid-cols-[8rem_1fr] gap-4 md:gap-5 py-3.5 border-b border-main/10 last:border-0 hover:bg-primary/5 hover:-mx-3 hover:px-3 rounded transition-colors group">
                <div class="pt-0.5">
                  <router-link :to="`/concepts/${wc.concept.slug}`" class="inline-flex items-center text-xs font-medium text-main/60 border border-main/15 rounded-sm px-2.5 py-1 hover:text-primary hover:border-primary/30 hover:bg-primary/5 transition-all">
                    {{ wc.concept.name }}
                  </router-link>
                </div>
                <p
                  :class="['text-sm leading-relaxed', { 'spoiler': isSpoilerProtected && !revealedSpoilers.has(wc.id), 'text-main': !isSpoilerProtected || revealedSpoilers.has(wc.id) }]"
                  @click="isSpoilerProtected && !revealedSpoilers.has(wc.id) && revealSpoiler(wc.id)"
                  :title="isSpoilerProtected && !revealedSpoilers.has(wc.id) ? '點擊顯示劇透內容' : ''"
                >
                  {{ wc.description }}
                </p>
              </div>
            </div>
          </section>
        </div>

        <!-- Sidebar Column (Pubs & Catalogues) -->
        <aside class="w-full md:w-5/12 lg:w-4/12 shrink-0 flex flex-col gap-10 md:sticky md:top-8 mt-8 md:mt-0">

          <!-- Publications -->
          <section v-if="work.publications && work.publications.length > 0">
            <div class="text-xs font-medium tracking-widest uppercase text-main/40 pb-2.5 border-b border-main/10 mb-5">
              出版與發行
            </div>
            <div class="flex flex-col">
              <div
                v-for="pub in work.publications"
                :key="pub.manifestation_id || pub.id"
                class="group flex items-start gap-3.5 py-3 border-b border-main/10 last:border-0 cursor-pointer hover:bg-primary/5 hover:-mx-3 hover:pl-3 hover:pr-1 rounded transition-colors relative"
                @click="toggleIsbn(pub.manifestation_id || pub.id)"
              >
                <!-- Left accent line on hover -->
                <div class="absolute -left-3 top-0 bottom-0 w-0.5 bg-transparent group-hover:bg-primary transition-colors"></div>

                <!-- Left Column: Year & Media Tag -->
                <div class="flex flex-col shrink-0 items-start gap-1.5 pt-0.5 w-14">
                  <span class="font-mono text-xs text-main/50">{{ pub.year || '-' }}</span>
                  <span v-if="pub.media_display" class="inline-block text-xs border border-main/10 rounded-sm px-1.5 py-0.5 text-main/50 text-center whitespace-nowrap">
                    {{ pub.media_display }}
                  </span>
                </div>

                <div class="flex-1 min-w-0 flex flex-col items-start">
                  <!-- Line 1：書名 -->
                  <span class="text-sm font-medium text-main mb-0.5">{{ pub.title }}</span>

                  <!-- Line 2：Credit · 出版社 -->
                  <div
                    v-if="(pub.credit && pub.credit.length) || pub.publisher?.name"
                    class="text-xs text-main/60 flex items-center flex-wrap gap-x-1 mt-0.5"
                  >
                    <template v-if="pub.credit && pub.credit.length">
                      <template v-for="(group, gIdx) in pub.credit" :key="gIdx">
                        <template v-for="(agent, aIdx) in group.agents" :key="aIdx">
                          {{ agent.text }}<span v-if="aIdx < group.agents.length - 1">、</span>
                        </template>
                        <span v-if="group.role">{{ group.role }}</span>
                        <span v-if="gIdx < pub.credit.length - 1">；</span>
                      </template>
                      <span v-if="pub.publisher?.name" class="text-main/30 px-0.5">/</span>
                    </template>
                    <span v-if="pub.publisher?.name">{{ pub.publisher.name }}</span>
                  </div>

                  <!-- Line 3：manifestation 副標（單一版本才顯示） -->
                  <div
                    v-if="pub.manifestations?.length === 1 && pub.manifestation_display_name && pub.manifestation_display_name !== pub.title"
                    class="text-xs text-primary/90 mt-0.5"
                  >
                    ↳ {{ pub.manifestation_display_name }}
                  </div>

                  <!-- Line 4：ISBN（點擊顯示） -->
                  <div
                    v-if="visibleIsbns.has(pub.manifestation_id || pub.id) && pub.isbn"
                    class="font-mono text-xs text-main/50 mt-1.5 selection:bg-primary/20"
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
            <div class="text-xs font-medium tracking-widest uppercase text-main/40 pb-2.5 border-b border-main/10 mb-5">
              收錄與獲獎
            </div>
            <div class="flex flex-col">
              <div v-for="entry in work.work_catalogues" :key="entry.id" class="group flex items-start gap-3.5 py-3 border-b border-main/10 last:border-0 cursor-pointer hover:bg-primary/5 hover:-mx-3 hover:pl-3 hover:pr-1 rounded transition-colors relative">
                <!-- Left accent line on hover -->
                <div class="absolute -left-3 top-0 bottom-0 w-0.5 bg-transparent group-hover:bg-primary transition-colors"></div>

                <!-- Left Column: Year & Type Tag -->
                <div class="flex flex-col shrink-0 items-start gap-1.5 pt-0.5 w-14">
                  <span class="font-mono text-xs text-main/50">{{ entry.catalogue.year || '-' }}</span>
                  <span v-if="entry.catalogue.catalogue_type_display" class="inline-block text-xs border border-main/10 rounded-sm px-1.5 py-0.5 text-main/50 text-center whitespace-nowrap">
                    {{ entry.catalogue.catalogue_type_display }}
                  </span>
                </div>

                <div class="flex-1 min-w-0 flex flex-col items-start">
                  <router-link v-if="entry.catalogue.id" :to="`/catalogues/${entry.catalogue.id}`" class="text-sm font-medium text-main hover:text-primary transition-colors block mb-0.5">{{ entry.catalogue.title }}</router-link>
                  <span v-else class="text-sm font-medium text-main block mb-0.5">{{ entry.catalogue.title }}</span>

                  <div v-if="entry.category || entry.status_display || entry.note" class="text-xs text-main/60 mt-0.5 flex items-center flex-wrap gap-x-1.5">
                    <span v-if="entry.category" class="font-medium text-main">{{ entry.category }}</span>
                    <span v-if="entry.category && entry.status_display" class="text-main/20 mx-1">·</span>
                    <span v-if="entry.status_display" :class="entry.status_display === '得獎' || entry.status_display === '首獎' || entry.status_display === '入選' ? 'text-primary' : 'text-main/40'">{{ entry.status_display }}</span>
                    <span v-if="entry.note" class="text-main/50 ml-1">({{ entry.note }})</span>
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
