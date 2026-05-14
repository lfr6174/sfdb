<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'
import { useSpoiler } from '../composables/useSpoiler'
import BackLink from '../components/BackLink.vue'
import SectionTitle from '../components/SectionTitle.vue'
import ExpandableTagList from '../components/ExpandableTagList.vue'

const route = useRoute()
const work = ref<any>(null)
const isLoading = ref(true)

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

// Map relational objects to simple concept objects for the tag list component
const plainConcepts = computed(() => {
  return work.value?.work_concepts?.map((wc: any) => wc.concept) || []
})

const conceptDescriptions = computed(() => {
  if (!work.value?.work_concepts) return []
  return work.value.work_concepts.filter((wc: any) => !!wc.description)
})

const sortedCatalogues = computed(() => {
  if (!work.value?.work_catalogues) return []
  // Sort by year descending
  return [...work.value.work_catalogues].sort((a, b) => (b.catalogue.year || 0) - (a.catalogue.year || 0))
})

const sortedPublications = computed(() => {
  if (!work.value?.publications) return []
  return [...work.value.publications].sort((a, b) => (b.year || 0) - (a.year || 0))
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
        <BackLink to="/works" text="返回作品列表" />
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
                    <router-link v-if="agent.id && agent.agent_type === 'person'" :to="`/persons/${agent.id}`" class="text-primary hover:opacity-70 transition-opacity">{{ agent.text }}</router-link>
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

              <template v-if="work.cycle">
                <span class="text-main/20">·</span>
                <span>{{ work.cycle.title }}</span>
              </template>
            </div>

            <!-- Synopsis -->
            <p class="text-base text-main/80 leading-relaxed whitespace-pre-wrap mb-8">
              {{ work.description || '暫無簡述提供。' }}
            </p>

            <!-- Concept Tags -->
            <ExpandableTagList
              v-if="work.work_concepts && work.work_concepts.length > 0"
              :concepts="plainConcepts"
              :limit="6"
            />
          </section>

          <!-- ── Concept Descriptions ── -->
          <section v-if="conceptDescriptions.length > 0" class="mt-12">

            <!-- Section eyebrow: label inline with rule -->
            <div class="flex items-center gap-3 mb-3">
              <span class="text-sm font-medium tracking-widest uppercase text-main/40 whitespace-nowrap">概念應用詳述</span>
              <div class="flex-1 border-t border-main/10"></div>
            </div>

            <div class="flex flex-col">
              <div
                v-for="wc in conceptDescriptions"
                :key="wc.id"
                class="py-3 border-b border-main/10 last:border-0 text-sm leading-relaxed"
              >
                <router-link
                  :to="`/concepts/${wc.concept.slug}`"
                  class="font-medium text-primary/80 hover:text-primary transition-colors no-underline"
                >
                  {{ wc.concept.name }}
                </router-link>
                <span class="text-main/25 mx-2">—</span>
                <span
                  :class="[
                    isSpoilerProtected && !revealedSpoilers.has(wc.id)
                      ? 'blur-sm hover:blur-[2px] transition-all duration-200 text-main/40 cursor-pointer select-none'
                      : 'text-main/65'
                  ]"
                  @click="isSpoilerProtected && !revealedSpoilers.has(wc.id) && revealSpoiler(wc.id)"
                >
                  {{ wc.description }}
                </span>
              </div>
            </div>
          </section>
        </div>

        <!-- ── Sidebar ── -->
        <aside class="w-full md:w-5/12 lg:w-4/12 shrink-0 flex flex-col gap-10 md:sticky md:top-8 mt-6 md:mt-0">

          <!-- Publications -->
          <section v-if="work.publications && work.publications.length > 0">
            <SectionTitle class="mb-4">出版與發行</SectionTitle>

            <div class="flex flex-col">
              <div
                v-for="pub in sortedPublications"
                :key="pub.manifestation_id || pub.id"
                class="flex items-start gap-3 py-3 border-b border-main/10 last:border-0"
                :class="{ 'cursor-pointer': pub.isbn }"
                @click="pub.isbn && toggleIsbn(pub.manifestation_id || pub.id)"
              >
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
            <SectionTitle class="mb-4">收錄與獲獎</SectionTitle>

            <div class="flex flex-col">
              <div
                v-for="entry in sortedCatalogues"
                :key="entry.id"
                class="flex items-start gap-3 py-3 border-b border-main/10 last:border-0"
              >
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
                  <span class="text-base font-medium text-main block mb-0.5">{{ entry.catalogue.title }}</span>

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
