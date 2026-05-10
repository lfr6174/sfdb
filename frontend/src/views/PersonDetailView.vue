<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'
import ConceptTag from '../components/ConceptTag.vue'
import BackLink from '../components/BackLink.vue'
import SectionTitle from '../components/SectionTitle.vue'
import ExpandableTagList from '../components/ExpandableTagList.vue'

const route = useRoute()

const person = ref<any>(null)
const isLoading = ref(true)

const fetchPersonDetail = async () => {
  isLoading.value = true
  try {
    const response = await api.get(`/persons/${route.params.id}/`)
    person.value = response.data
  } catch (error) {
    console.error('Failed to fetch person details:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchPersonDetail()
})


const totalWorksCount = computed(() => {
  return person.value?.participated_works?.length || 0
})

const activeYears = computed(() => {
  if (!person.value?.participated_works || person.value.participated_works.length === 0) return '—'
  const years = person.value.participated_works
    .map((w: any) => parseInt(w.year))
    .filter((y: number) => !isNaN(y))
  if (years.length === 0) return '—'
  const min = Math.min(...years)
  const max = Math.max(...years)
  return min === max ? `${min}` : `${min} — ${max}`
})

const personAwards = computed(() => {
  if (!person.value?.participated_works) return []
  const awardsMap = new Map<number, any>()

  person.value.participated_works.forEach((w: any) => {
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

    <template v-else-if="person">

      <!-- Back Link -->
      <div class="pt-10 mb-9">
        <BackLink to="/persons" text="返回人物列表" />
      </div>

      <div class="flex flex-col md:flex-row gap-10 lg:gap-16 items-start pb-20">

        <!-- ── Main Column ── -->
        <div class="w-full md:w-7/12 lg:w-8/12 flex flex-col">

          <!-- Personal Info -->
          <section>
            <h1 class="text-3xl md:text-4xl font-normal leading-snug text-main mb-2">
              {{ person.name }}
            </h1>

            <div v-if="person.aliases && person.aliases.length > 0" class="text-base text-main/40 mb-5">
              {{ person.aliases.map((a) => a.name).join(' · ') }}
            </div>

            <p class="text-base text-main/80 leading-relaxed whitespace-pre-wrap mb-5">
              {{ person.about || '暫無簡歷提供。' }}
            </p>

            <!-- External Links -->
            <div v-if="person.links && person.links.length > 0" class="flex flex-wrap gap-4">
              <a
                v-for="link in person.links"
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
            <SectionTitle class="mb-5">歷年作品</SectionTitle>

          <div v-if="person.participated_works && person.participated_works.length > 0" class="flex flex-col">
              <router-link
              v-for="work in person.participated_works"
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
          <section v-if="person.participated_publications && person.participated_publications.length > 0" class="mt-10">
            <SectionTitle class="mb-5">出版與其他參與</SectionTitle>

            <div class="flex flex-col">
              <div
                v-for="pub in person.participated_publications"
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
            <SectionTitle class="mb-2">作品總數</SectionTitle>
            <span class="font-mono text-xl text-main">{{ totalWorksCount }}</span>
          </div>

          <!-- Active years -->
          <div>
            <SectionTitle class="mb-2">活躍年份</SectionTitle>
            <span class="font-mono text-base text-main">{{ activeYears }}</span>
          </div>

          <!-- Top Concepts -->
          <div>
            <SectionTitle class="mb-3">常見標籤</SectionTitle>

            <div v-if="person.top_concepts && person.top_concepts.length > 0">
              <ExpandableTagList :concepts="person.top_concepts" :limit="10" />
            </div>
            <div v-else class="text-sm text-main/40">尚未與任何概念建立關聯。</div>
          </div>

          <!-- Awards -->
          <div v-if="personAwards.length > 0">
            <SectionTitle class="mb-3">相關獎項</SectionTitle>
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
