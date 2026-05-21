<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'
import BackLink from '../components/BackLink.vue'
import SectionTitle from '../components/SectionTitle.vue'
import ExpandableTagList from '../components/ExpandableTagList.vue'
import { useDocumentTitle } from '../composables/useDocumentTitle'

const route = useRoute()

const person = ref<any>(null)
useDocumentTitle(() => person.value?.name)
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
        if (!awardsMap.has(award.title)) {
          awardsMap.set(award.title, {
            id: award.title,
            title: award.title,
            count: 0,
          })
        }
        awardsMap.get(award.title).count += 1
      })
    }
  })

  return Array.from(awardsMap.values()).sort((a, b) => b.count - a.count)
})
</script>

<template>
  <div class="mx-auto max-w-4xl">
    <div
      v-if="isLoading"
      class="text-main/50 py-16 text-center text-sm font-medium"
    >
      正在讀取人物資料...
    </div>

    <template v-else-if="person">
      <!-- Back Link -->
      <div class="mb-9 pt-10">
        <BackLink
          to="/persons"
          text="返回人物列表"
        />
      </div>

      <div class="flex flex-col items-start gap-10 pb-20 md:flex-row lg:gap-16">
        <!-- ── Main Column ── -->
        <div class="flex w-full flex-col md:w-7/12 lg:w-8/12">
          <!-- Personal Info -->
          <section>
            <h1 class="text-main mb-4 text-2xl leading-snug font-normal md:text-3xl">
              {{ person.name }}
            </h1>

            <div
              v-if="person.aliases && person.aliases.length > 0"
              class="text-main/40 mb-5 text-base"
            >
              {{ person.aliases.map((a) => a.name).join(' · ') }}
            </div>

            <p class="text-main/80 mb-5 text-base leading-relaxed whitespace-pre-wrap">
              {{ person.about || '暫無簡歷提供。' }}
            </p>

            <!-- External Links -->
            <div
              v-if="person.links && person.links.length > 0"
              class="flex flex-wrap gap-4"
            >
              <a
                v-for="link in person.links"
                :key="link.id"
                :href="link.url"
                target="_blank"
                rel="noopener noreferrer"
                class="text-primary text-base no-underline transition-opacity hover:opacity-70"
              >
                ↗ {{ link.label }}
              </a>
            </div>
          </section>

          <!-- ── Participated Works ── -->
          <section class="mt-10">
            <SectionTitle class="mb-2">歷年作品</SectionTitle>

            <div
              v-if="person.participated_works && person.participated_works.length > 0"
              class="flex flex-col"
            >
              <router-link
                v-for="work in person.participated_works"
                :key="work.id"
                :to="`/works/${work.id}`"
                class="group border-main/10 relative z-0 flex items-baseline gap-4 border-b py-3 no-underline transition-colors last:border-0"
              >
                <!-- Hover Background Overlay -->
                <div
                  class="pointer-events-none absolute -inset-x-3 inset-y-0 -z-10 rounded-sm bg-transparent transition-colors group-hover:bg-white/5"
                ></div>

                <!-- Accent line -->
                <div
                  class="group-hover:bg-primary pointer-events-none absolute top-0 bottom-0 -left-3 w-0.5 bg-transparent transition-colors"
                ></div>

                <span class="text-main/50 w-10 shrink-0 text-sm">
                  {{ work.year || '-' }}
                </span>

                <div class="flex min-w-0 flex-1 flex-wrap items-baseline gap-x-2 gap-y-1">
                  <span
                    class="text-main group-hover:text-primary text-base font-medium transition-colors"
                  >
                    {{ work.title }}
                  </span>
                </div>
                <div>
                  <span class="text-main/50 pr-3 text-sm">
                    {{ [work.work_length, work.media_type].filter(Boolean).join('') }}
                  </span>
                  <span class="text-primary shrink-0 text-right text-sm font-medium">
                    {{ work.roles.join('、') }}
                  </span>
                </div>
              </router-link>
            </div>
            <div
              v-else
              class="text-main/40 py-3 text-base"
            >
              尚無關聯的歷年作品。
            </div>
          </section>

          <!-- ── Participated Publications ── -->
          <section
            v-if="person.participated_publications && person.participated_publications.length > 0"
            class="mt-10"
          >
            <SectionTitle class="mb-2">出版與其他參與</SectionTitle>

            <div class="flex flex-col">
              <div
                v-for="pub in person.participated_publications"
                :key="pub.id"
                class="border-main/10 flex items-baseline gap-4 border-b py-3 last:border-0"
              >
                <span class="text-main/50 w-10 shrink-0 text-sm">
                  {{ pub.year || '-' }}
                </span>

                <div class="flex min-w-0 flex-1 flex-wrap items-baseline gap-x-2 gap-y-1">
                  <span class="text-main text-base font-medium">{{ pub.title }}</span>
                </div>
                <div>
                  <span
                    v-if="pub.publisher"
                    class="text-main/50 pr-3 text-sm"
                  >
                    {{ pub.publisher }}
                  </span>
                  <span class="text-primary shrink-0 text-right text-sm font-medium">
                    {{ pub.roles.join('、') }}
                  </span>
                </div>
              </div>
            </div>
          </section>
        </div>

        <!-- ── Sidebar ── -->
        <aside
          class="mt-6 flex w-full shrink-0 flex-col gap-8 md:sticky md:top-8 md:mt-0 md:w-5/12 lg:w-4/12"
        >
          <!-- Work count -->
          <div>
            <SectionTitle class="mb-2">作品總數</SectionTitle>
            <span class="text-main text-xl">{{ totalWorksCount }}</span>
          </div>

          <!-- Active years -->
          <div>
            <SectionTitle class="mb-2">活躍年份</SectionTitle>
            <span class="text-main text-base">{{ activeYears }}</span>
          </div>

          <!-- Top Concepts -->
          <div>
            <SectionTitle class="mb-3">常見標籤</SectionTitle>

            <div v-if="person.concepts && person.concepts.length > 0">
              <ExpandableTagList
                :concepts="person.concepts"
                :limit="7"
              />
            </div>
            <div
              v-else
              class="text-main/40 text-sm"
            >
              尚未與任何概念建立關聯。
            </div>
          </div>

          <!-- Awards -->
          <div v-if="personAwards.length > 0">
            <SectionTitle class="mb-3">相關獎項</SectionTitle>
            <div class="flex flex-wrap gap-1.5">
              <span
                v-for="award in personAwards"
                :key="award.id"
                class="text-main/60 border-main/15 inline-flex cursor-default items-center gap-1.5 border px-2.5 py-1 text-xs whitespace-nowrap"
              >
                <span>{{ award.title }}</span>
                <span
                  v-if="award.count > 1"
                  class="text-main/40 font-mono text-[10px]"
                >
                  {{ award.count }}
                </span>
              </span>
            </div>
          </div>
        </aside>
      </div>
    </template>
  </div>
</template>
