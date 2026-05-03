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
      <div class="mb-4">
        <!-- Back Link -->
        <router-link to="/works" class="back-link">
          ← 返回作品列表
        </router-link>
      </div>

      <div class="flex flex-col md:flex-row gap-4 md:gap-5 items-start pb-12">

        <!-- Main Column -->
        <div class="w-full md:w-7/12 lg:w-8/12 flex flex-col gap-4 md:gap-5">

          <!-- Header Info & Synopsis Section -->
          <section class="card relative">

            <!-- Media type and work length -->
            <div v-if="work.work_length_display || work.media_type_display" class="mb-2 flex flex-wrap gap-2">
              <span class="pill">
                {{ work.work_length_display || '' }}{{ work.media_type_display || '' }}
              </span>
            </div>

            <h1 class="font-serif text-[21px] md:text-2xl font-medium text-main mb-3">
              <span>{{ work.title }}</span>
            </h1>

            <!-- Metadata List -->
            <div class="flex flex-wrap items-center gap-x-2.5 gap-y-1.5 text-[13px] text-main/60 pb-3 mb-4 border-b border-main/10">
              <span v-if="work.credit && work.credit.length" class="flex flex-wrap items-center gap-x-[2px]">
                <template v-for="(group, gIdx) in work.credit" :key="gIdx">
                  <template v-for="(agent, aIdx) in group.agents" :key="aIdx">
                    <router-link v-if="agent.id" :to="`/agents/${agent.id}`" class="text-primary hover:text-primary/70 transition-colors">{{ agent.text }}</router-link>
                    <span v-else class="text-main">{{ agent.text }}</span>
                    <span v-if="aIdx < group.agents.length - 1">、</span>
                  </template>
                  <span v-if="group.role" class="text-main/25">{{ group.role }}</span>
                  <span v-if="gIdx < work.credit.length - 1" class="ml-1 mr-0.5">；</span>
                </template>
              </span>
              <span v-else>-</span>

              <span class="text-main/25">·</span>
              <span>{{ work.year || '未知年份' }}</span>

              <!-- Series -->
              <template v-if="work.series">
                <span class="text-main/25">·</span>
                <span>{{ work.series.title }}</span>
              </template>
            </div>

            <!-- Synopsis -->
            <div>
              <p class="text-[14px] text-main leading-[1.8] whitespace-pre-wrap">{{ work.description || '暫無簡述提供。' }}</p>
            </div>

            <!-- Concept Tags List -->
            <div v-if="work.work_concepts && work.work_concepts.length > 0" class="mt-5 flex flex-wrap gap-2">
              <router-link
                v-for="wc in displayedConcepts"
                :key="wc.concept.slug"
                :to="`/concepts/${wc.concept.slug}`"
                class="tag"
              >
                <span>{{ wc.concept.name }}</span>
              </router-link>

              <button v-if="hiddenConceptsCount > 0 && !isConceptsExpanded" @click="isConceptsExpanded = true" class="tag !border-dashed !text-primary hover:!bg-hover">
                + {{ hiddenConceptsCount }} 更多
              </button>
              <button v-if="isConceptsExpanded" @click="isConceptsExpanded = false" class="tag !border-dashed !text-primary hover:!bg-hover">
                - 收合
              </button>
            </div>
          </section>

          <!-- Concepts Section -->
          <section v-if="conceptDescriptions.length > 0" class="card relative">
            <h2 class="section-label">概念應用詳述</h2>
            <div class="flex flex-col">
              <div v-for="wc in conceptDescriptions" :key="wc.id" class="concept-row">
                <div class="concept-row-label">
                  <router-link :to="`/concepts/${wc.concept.slug}`" class="tag">
                    {{ wc.concept.name }}
                  </router-link>
                </div>
                <p
                  :class="['concept-row-desc', { 'spoiler': isSpoilerProtected && !revealedSpoilers.has(wc.id), 'text-main': !isSpoilerProtected || revealedSpoilers.has(wc.id) }]"
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
        <aside class="w-full md:w-5/12 lg:w-4/12 shrink-0 flex flex-col gap-4 md:sticky md:top-4">

          <!-- Publications -->
          <section v-if="work.publications && work.publications.length > 0" class="card-sm">
            <h2 class="section-label">出版與發行</h2>
            <div class="flex flex-col">
              <div
                v-for="pub in work.publications"
                :key="pub.manifestation_id || pub.id"
                class="flat-row items-start"
                @click="toggleIsbn(pub.manifestation_id || pub.id)"
              >
                <!-- Left Column: Year & Media Tag -->
                <div class="flex flex-col shrink-0 items-start gap-1 pt-[1px]">
                  <span class="flat-year">{{ pub.year || '-' }}</span>
                  <span v-if="pub.media_display" class="text-[10px] text-main/40 border border-main/15 rounded px-1 py-0.5 leading-none whitespace-nowrap">
                    {{ pub.media_display }}
                  </span>
                </div>

                <div class="flat-body">
                  <!-- Line 1：書名 -->
                  <div class="mb-[2px]">
                    <span class="flat-title">{{ pub.title }}</span>
                  </div>

                  <!-- Line 2：Credit · 出版社 -->
                  <div
                    v-if="(pub.credit && pub.credit.length) || pub.publisher?.name"
                    class="flat-sub flex items-center flex-wrap gap-x-1 mt-[2px]"
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
                    class="text-[12px] text-primary/90 mt-[2px]"
                  >
                    ↳ {{ pub.manifestation_display_name }}
                  </div>

                  <!-- Line 4：ISBN（點擊顯示） -->
                  <div
                    v-if="visibleIsbns.has(pub.manifestation_id || pub.id) && pub.isbn"
                    class="font-mono text-[12px] text-main/60 mt-1 selection:bg-primary/20"
                    @click.stop
                  >
                    ISBN {{ pub.isbn }}
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- Catalogues -->
          <section v-if="work.catalogue_entries && work.catalogue_entries.length > 0" class="card-sm">
            <h2 class="section-label">收錄與獲獎</h2>
            <div class="flex flex-col">
              <div v-for="entry in work.catalogue_entries" :key="entry.id" class="flat-row items-start">
                <!-- Left Column: Year & Type Tag -->
                <div class="flex flex-col shrink-0 items-start gap-1 pt-[1px]">
                  <span class="flat-year">{{ entry.catalogue.year || '-' }}</span>
                  <span v-if="entry.catalogue.catalogue_type_display" class="text-[10px] text-main/40 border border-main/15 rounded px-1 py-0.5 leading-none whitespace-nowrap">
                    {{ entry.catalogue.catalogue_type_display }}
                  </span>
                </div>

                <div class="flat-body">
                  <div class="mb-[2px]">
                    <router-link v-if="entry.catalogue.id" :to="`/catalogues/${entry.catalogue.id}`" class="flat-title hover:text-primary transition-colors">{{ entry.catalogue.title }}</router-link>
                    <span v-else class="flat-title">{{ entry.catalogue.title }}</span>
                  </div>
                  <div v-if="entry.note" class="flat-sub mt-[2px] flex items-center flex-wrap gap-x-1.5">
                    <span v-if="entry.note">{{ entry.note }}</span>
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
