<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'
import { useSpoiler } from '../composables/useSpoiler'
import BackLink from '../components/BackLink.vue'
import SectionTitle from '../components/SectionTitle.vue'
import ExpandableTagList from '../components/ExpandableTagList.vue'
import { useDocumentTitle } from '../composables/useDocumentTitle'

const route = useRoute()
const work = ref<any>(null)
const isLoading = ref(true)

useDocumentTitle(() => work.value?.title)

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
  return [...work.value.work_catalogues].sort(
    (a, b) => (b.catalogue.year || 0) - (a.catalogue.year || 0),
  )
})

const sortedPublications = computed(() => {
  if (!work.value?.publications) return []
  return [...work.value.publications].sort((a, b) => (b.year || 0) - (a.year || 0))
})
</script>

<template>
  <div class="mx-auto max-w-4xl">
    <div
      v-if="isLoading"
      class="text-main/50 py-16 text-center text-sm font-medium"
    >
      正在讀取作品資料...
    </div>

    <template v-else-if="work">
      <!-- Back Link -->
      <div class="mb-9 pt-6 md:pt-10">
        <BackLink
          to="/works"
          text="返回作品列表"
        />
      </div>

      <div class="flex flex-col items-start gap-10 pb-20 md:flex-row lg:gap-16">
        <!-- ── Main Column ── -->
        <div class="flex w-full flex-col md:w-7/12 lg:w-8/12">
          <section>
            <!-- Media type pill (gray filled badge, not a tag) -->
            <div
              v-if="work.work_length_display || work.media_type_display"
              class="mb-4"
            >
              <span
                class="text-main/50 bg-main/5 inline-block px-2 py-1 font-mono text-xs tracking-wider uppercase"
              >
                {{ work.work_length_display || '' }}{{ work.media_type_display || '' }}
              </span>
            </div>

            <!-- Title -->
            <h1 class="text-main mb-6 text-2xl leading-snug font-normal md:text-3xl">
              {{ work.title }}
            </h1>

            <!-- Meta row -->
            <div class="text-main/70 mb-6 flex flex-wrap items-center gap-x-2 gap-y-1 text-base">
              <span
                v-if="work.credit && work.credit.length"
                class="flex flex-wrap items-center gap-x-0.5"
              >
                <template
                  v-for="(group, gIdx) in work.credit"
                  :key="gIdx"
                >
                  <template
                    v-for="(agent, aIdx) in group.agents"
                    :key="aIdx"
                  >
                    <router-link
                      v-if="agent.id && agent.agent_type === 'person'"
                      :to="`/persons/${agent.id}`"
                      class="text-primary transition-opacity hover:opacity-70"
                    >
                      {{ agent.text }}
                    </router-link>
                    <span
                      v-else
                      class="text-main/80"
                    >
                      {{ agent.text }}
                    </span>
                    <span v-if="aIdx < group.agents.length - 1">、</span>
                  </template>
                  <span
                    v-if="group.role"
                    class="text-main/40 ml-0.5"
                  >
                    {{ group.role }}
                  </span>
                  <span
                    v-if="gIdx < work.credit.length - 1"
                    class="mr-0.5 ml-1"
                  >
                    ；
                  </span>
                </template>
              </span>
              <span
                v-else
                class="text-main/35"
              >
                -
              </span>

              <span class="text-main/20">·</span>
              <span>{{ work.year || '未知年份' }}</span>

              <template v-if="work.cycle">
                <span class="text-main/20">·</span>
                <span>{{ work.cycle.title }}</span>
              </template>
            </div>

            <!-- Synopsis -->
            <p class="text-main/80 mb-8 text-base leading-relaxed whitespace-pre-wrap">
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
          <section
            v-if="conceptDescriptions.length > 0"
            class="mt-12"
          >
            <!-- Section eyebrow: label inline with rule -->
            <div class="mb-3 flex items-center gap-3">
              <span
                class="text-main/40 text-sm font-medium tracking-widest whitespace-nowrap uppercase"
              >
                概念應用詳述
              </span>
              <div class="border-main/10 flex-1 border-t"></div>
            </div>

            <div class="flex flex-col">
              <div
                v-for="wc in conceptDescriptions"
                :key="wc.id"
                class="border-main/10 border-b py-3 text-sm leading-relaxed last:border-0"
              >
                <router-link
                  :to="`/concepts/${wc.concept.slug}`"
                  class="text-primary/80 hover:text-primary font-medium no-underline transition-colors"
                >
                  {{ wc.concept.name }}
                </router-link>
                <span class="text-main/25 mx-2">—</span>
                <span
                  :class="[
                    isSpoilerProtected && !revealedSpoilers.has(wc.id)
                      ? 'text-main/40 cursor-pointer blur-sm transition-all duration-200 select-none hover:blur-[2px]'
                      : 'text-main/65',
                  ]"
                  @click="
                    isSpoilerProtected && !revealedSpoilers.has(wc.id) && revealSpoiler(wc.id)
                  "
                >
                  {{ wc.description }}
                </span>
              </div>
            </div>
          </section>
        </div>

        <!-- ── Sidebar ── -->
        <aside
          class="mt-6 flex w-full shrink-0 flex-col gap-10 md:sticky md:top-8 md:mt-0 md:w-5/12 lg:w-4/12"
        >
          <!-- Publications -->
          <section v-if="work.publications && work.publications.length > 0">
            <SectionTitle class="mb-4">出版與發行</SectionTitle>

            <div class="flex flex-col">
              <div
                v-for="pub in sortedPublications"
                :key="pub.manifestation_id || pub.id"
                class="border-main/10 flex items-start gap-3 border-b py-3 last:border-0"
                :class="{ 'cursor-pointer': pub.isbn }"
                @click="pub.isbn && toggleIsbn(pub.manifestation_id || pub.id)"
              >
                <!-- Left: year + media badge -->
                <div class="flex w-11 shrink-0 flex-col items-start gap-1.5 pt-0.5">
                  <span class="text-main/50 text-xs">{{ pub.year || '-' }}</span>
                  <!-- Gray filled badge — visually distinct from concept tags -->
                  <span
                    v-if="pub.media_display"
                    class="text-main/50 bg-main/5 px-1.5 py-0.5 font-mono text-[10px] tracking-wide whitespace-nowrap"
                  >
                    {{ pub.media_display }}
                  </span>
                </div>

                <div class="min-w-0 flex-1">
                  <span class="text-main mb-0.5 block text-base font-medium">{{ pub.title }}</span>

                  <div
                    v-if="(pub.credit && pub.credit.length) || pub.publisher?.name"
                    class="text-main/50 mt-0.5 flex flex-wrap gap-x-1 text-xs"
                  >
                    <template v-if="pub.credit && pub.credit.length">
                      <template
                        v-for="(group, gIdx) in pub.credit"
                        :key="gIdx"
                      >
                        <template
                          v-for="(agent, aIdx) in group.agents"
                          :key="aIdx"
                        >
                          {{ agent.text }}
                          <span v-if="aIdx < group.agents.length - 1">、</span>
                        </template>
                        <span v-if="group.role">{{ group.role }}</span>
                        <span v-if="gIdx < pub.credit.length - 1">；</span>
                      </template>
                      <span
                        v-if="pub.publisher?.name"
                        class="text-main/25 px-0.5"
                      >
                        /
                      </span>
                    </template>
                    <span v-if="pub.publisher?.name">{{ pub.publisher.name }}</span>
                  </div>

                  <div
                    v-if="
                      pub.manifestations?.length === 1 &&
                      pub.manifestation_display_name &&
                      pub.manifestation_display_name !== pub.title
                    "
                    class="text-primary/80 mt-0.5 text-xs"
                  >
                    ↳ {{ pub.manifestation_display_name }}
                  </div>

                  <div
                    v-if="visibleIsbns.has(pub.manifestation_id || pub.id) && pub.isbn"
                    class="text-main/40 selection:bg-primary/20 mt-2 font-mono text-xs"
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
                class="border-main/10 flex items-start gap-3 border-b py-3 last:border-0"
              >
                <div class="flex w-11 shrink-0 flex-col items-start gap-1.5 pt-0.5">
                  <span class="text-main/50 text-xs">
                    {{ entry.catalogue.year || '-' }}
                  </span>
                  <span
                    v-if="entry.catalogue.catalogue_type_display"
                    class="text-main/50 bg-main/5 px-1.5 py-0.5 font-mono text-[10px] tracking-wide whitespace-nowrap"
                  >
                    {{ entry.catalogue.catalogue_type_display }}
                  </span>
                </div>

                <div class="min-w-0 flex-1">
                  <span class="text-main mb-0.5 block text-base font-medium">
                    {{ entry.catalogue.title }}
                  </span>

                  <div
                    v-if="entry.category || entry.status_display || entry.note"
                    class="text-main/50 mt-0.5 flex flex-wrap items-center gap-x-1.5 text-xs"
                  >
                    <span
                      v-if="entry.category"
                      class="text-main/65 font-medium"
                    >
                      {{ entry.category }}
                    </span>
                    <span
                      v-if="entry.category && entry.status_display"
                      class="text-main/20"
                    >
                      ·
                    </span>
                    <span
                      v-if="entry.status_display"
                      :class="
                        ['得獎', '首獎', '入選'].includes(entry.status_display)
                          ? 'text-primary'
                          : 'text-main/35'
                      "
                    >
                      {{ entry.status_display }}
                    </span>
                    <span
                      v-if="entry.note"
                      class="text-main/40"
                    >
                      ({{ entry.note }})
                    </span>
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
