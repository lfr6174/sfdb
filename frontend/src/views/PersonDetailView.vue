<script setup lang="ts">
import { computed } from 'vue'
import BackLink from '../components/BackLink.vue'
import SectionTitle from '../components/SectionTitle.vue'
import ListState from '../components/ListState.vue'
import ExpandableTagList from '../components/ExpandableTagList.vue'
import HoverListItem from '../components/HoverListItem.vue'
import { useDocumentMeta } from '../composables/useDocumentTitle'
import { fetchPersonDetail } from '../api/persons'
import { useApiDetail } from '../composables/useApiDetail'
import { getYearRange } from '../utils/formatters'

const {
  data: person,
  isLoading,
  hasError,
} = useApiDetail((params) => fetchPersonDetail(params.id as string))
useDocumentMeta(
  () => person.value?.name,
  () => person.value?.about?.slice(0, 160),
)

const totalWorksCount = computed(() => {
  return person.value?.participated_works?.length || 0
})

const totalPublicationsCount = computed(() => {
  return person.value?.participated_publications?.length || 0
})

// Publication-only participants (e.g. cover illustrators) get their publication
// count instead of a misleading zero works count
const participationStat = computed(() =>
  totalWorksCount.value > 0 || totalPublicationsCount.value === 0
    ? { label: '作品總數', value: totalWorksCount.value }
    : { label: '出版參與', value: totalPublicationsCount.value },
)

const activeYears = computed(() => {
  const range = getYearRange([
    ...(person.value?.participated_works || []),
    ...(person.value?.participated_publications || []),
  ])
  if (range.min === null) return '—'
  return range.min === range.max ? `${range.min}` : `${range.min} — ${range.max}`
})

const personAwards = computed(() => {
  if (!person.value?.participated_works) return []
  const awardsMap = new Map<string, { id: string; title: string; count: number }>()

  person.value.participated_works.forEach((w) => {
    if (w.awards && w.awards.length > 0) {
      w.awards.forEach((award) => {
        if (!awardsMap.has(award.title)) {
          awardsMap.set(award.title, {
            id: award.title,
            title: award.title,
            count: 0,
          })
        }
        awardsMap.get(award.title)!.count += 1
      })
    }
  })

  return Array.from(awardsMap.values()).sort((a, b) => b.count - a.count)
})
</script>

<template>
  <div class="mx-auto max-w-4xl">
    <ListState
      :loading="isLoading"
      :error="hasError"
      size="sm"
      loading-text="正在讀取人物資料..."
    />

    <template v-if="person">
      <!-- Back Link -->
      <div class="mb-9 pt-6 md:pt-10">
        <BackLink
          to="/persons"
          text="返回人物列表"
        />
      </div>

      <div class="flex flex-col items-start gap-10 pb-20 md:flex-row lg:gap-16">
        <!-- Main Column -->
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

          <!-- Participated Works (hidden for publication-only participants) -->
          <section
            v-if="totalWorksCount > 0 || totalPublicationsCount === 0"
            class="mt-12"
          >
            <SectionTitle class="mb-4">歷年作品</SectionTitle>

            <div
              v-if="person.participated_works && person.participated_works.length > 0"
              class="flex flex-col"
            >
              <HoverListItem
                v-for="work in person.participated_works"
                :key="work.id"
                :to="`/works/${work.id}`"
                class="flex items-baseline gap-4 py-3 no-underline"
              >
                <span class="text-main/50 w-10 shrink-0 text-sm">
                  {{ work.year || '-' }}
                </span>

                <div class="flex min-w-0 flex-1 flex-wrap items-baseline gap-x-2 gap-y-1">
                  <span
                    class="text-main/80 group-hover:text-primary text-base font-medium transition-colors"
                  >
                    {{ work.title }}
                  </span>
                </div>
                <div>
                  <span class="text-main/50 pr-3 text-sm">
                    {{ [work.work_length, work.genre].filter(Boolean).join('') }}
                  </span>
                  <span class="text-primary shrink-0 text-right text-sm font-medium">
                    {{ work.roles.join('、') }}
                  </span>
                </div>
              </HoverListItem>
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
              <span class="text-main/35 text-sm">暫無作品收錄。</span>
            </div>
          </section>

          <!-- Participated Publications -->
          <section
            v-if="person.participated_publications && person.participated_publications.length > 0"
            class="mt-12"
          >
            <SectionTitle class="mb-4">出版與其他參與</SectionTitle>

            <div class="flex flex-col">
              <div
                v-for="pub in person.participated_publications"
                :key="pub.ids[0]"
                class="border-main/10 flex items-baseline gap-4 border-b py-3 last:border-0"
              >
                <span class="text-main/50 w-10 shrink-0 text-sm">
                  {{ pub.year || '-' }}
                </span>

                <div class="flex min-w-0 flex-1 flex-wrap items-baseline gap-x-2 gap-y-1">
                  <router-link
                    :to="{
                      path: '/works',
                      query: { publication: pub.ids.join(','), publication_title: pub.title },
                    }"
                    class="text-main/80 hover:text-primary text-base font-medium no-underline transition-colors"
                  >
                    {{ pub.title }}
                  </router-link>
                  <span
                    v-if="pub.media.length"
                    class="text-main/40 text-xs"
                  >
                    {{ pub.media.join('・') }}
                  </span>
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

        <!-- Sidebar -->
        <aside
          class="mt-6 flex w-full shrink-0 flex-col gap-8 md:sticky md:top-24 md:mt-0 md:w-5/12 lg:w-4/12"
        >
          <!-- Participation count -->
          <div>
            <SectionTitle class="mb-3">{{ participationStat.label }}</SectionTitle>
            <span class="text-main text-xl">{{ participationStat.value }}</span>
          </div>

          <!-- Active years -->
          <div>
            <SectionTitle class="mb-3">活躍年份</SectionTitle>
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
              尚無常見的作品標籤。
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
                  class="text-main/40 font-mono text-xs"
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
