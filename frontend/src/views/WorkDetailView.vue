<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'

const route = useRoute()
const work = ref<any>(null)
const isLoading = ref(true)
const isConceptsExpanded = ref(false)

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

const isSpoilerProtected = ref(localStorage.getItem('spoiler') !== 'false')
const revealedSpoilers = ref<Set<number>>(new Set())

const handleSpoilerToggle = (e: any) => {
  isSpoilerProtected.value = e.detail
}

const revealSpoiler = (itemId: number) => {
  revealedSpoilers.value.add(itemId)
}

onMounted(() => {
  fetchWorkDetail()
  window.addEventListener('spoiler-toggle', handleSpoilerToggle)
})

onUnmounted(() => {
  window.removeEventListener('spoiler-toggle', handleSpoilerToggle)
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

const groupedWorkCredits = computed(() => {
  if (!work.value?.credits) return []
  const groups: Record<string, any[]> = {}
  work.value.credits.forEach((c: any) => {
    if (!groups[c.role]) groups[c.role] = []
    groups[c.role].push(c)
  })

  const result = []
  const authors = [...(groups['author'] || []), ...(groups['co_author'] || [])]
  if (authors.length) result.push({ label: '', credits: authors })
  if (groups['story']) result.push({ label: '原作', credits: groups['story'] })
  if (groups['art']) result.push({ label: '作畫', credits: groups['art'] })
  return result
})

const getGroupedPubCredits = (credits: any[]) => {
  if (!credits || !credits.length) return []

  const filteredCredits = credits.filter((c: any) => {
    // 核心作者群如果沒有填寫專屬的 display_name，就不要顯示在出版品列表上
    if (['author', 'co_author', 'story', 'art'].includes(c.role)) {
      return !!c.display_name
    }
    return true // 譯者、繪者、編輯則一律顯示
  })

  const groups: Record<string, any[]> = {}
  filteredCredits.forEach((c: any) => {
    if (!groups[c.role]) groups[c.role] = []
    groups[c.role].push(c)
  })

  const result = []
  const authors = [...(groups['author'] || []), ...(groups['co_author'] || [])]

  if (authors.length) result.push({ label: '著', credits: authors })
  if (groups['story']) result.push({ label: '原作', credits: groups['story'] })
  if (groups['art']) result.push({ label: '作畫', credits: groups['art'] })

  if (groups['translator']) result.push({ label: '譯', credits: groups['translator'] })
  if (groups['illustrator']) result.push({ label: '繪', credits: groups['illustrator'] })
  if (groups['editor']) result.push({ label: '編', credits: groups['editor'] })
  return result
}
</script>

<template>
  <div class="max-w-5xl mx-auto space-y-6 pb-12">

    <div v-if="isLoading" class="text-center py-16 text-[#2d2016]/50 font-medium bg-[#ffffff] rounded-lg border border-[#2d2016]/10">
      正在讀取作品資料...
    </div>

    <template v-else-if="work">
      <!-- Back Link -->
      <router-link to="/works" class="inline-flex items-center text-sm font-medium text-[#2d2016]/50 hover:text-[#ae5630] transition-colors mb-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        返回作品列表
      </router-link>

      <!-- Header Info & Synopsis Section -->
      <section class="bg-[#ffffff] rounded-lg p-6 md:p-8 shadow-sm border border-[#2d2016]/10 relative">
        <h1 class="text-3xl md:text-4xl font-bold text-[#2d2016] tracking-tight mb-4 flex items-baseline gap-3 flex-wrap">
          <span>{{ work.title }}</span>
        </h1>

        <!-- Metadata List -->
        <div class="flex flex-wrap items-center gap-2 text-base text-[#2d2016]/70 mb-6 font-medium">
          <span v-if="groupedWorkCredits.length > 0" class="flex flex-wrap items-center">
            <span v-for="(group, gIdx) in groupedWorkCredits" :key="gIdx" class="flex flex-wrap items-center">
              <span v-for="(credit, cIdx) in group.credits" :key="credit.id">
                <router-link :to="`/agents/${credit.agent_detail.id}`" class="text-[#ae5630] hover:text-[#ae5630]/70 transition-colors">
                  {{ credit.agent_detail.name }}
                </router-link>
                <span v-if="cIdx < group.credits.length - 1" class="text-[#2d2016]/80 mx-0.5">、</span>
              </span>
              <span v-if="group.label" class="text-[#2d2016]/80 ml-1">({{ group.label }})</span>
              <span v-if="gIdx < groupedWorkCredits.length - 1" class="text-[#2d2016]/80 mx-1">，</span>
            </span>
          </span>
          <span v-else>佚名</span>
          <span class="text-[#2d2016]/30">·</span>
          <span>{{ work.year || '未知年份' }}</span>
          <span class="text-[#2d2016]/30">·</span>
          <span>{{ work.work_length_display || '未知篇幅' }}</span>
          <span class="text-[#2d2016]/30">·</span>
          <span>{{ work.media_type_display || '未知媒體' }}</span>
        </div>

        <!-- Synopsis -->
        <div>
          <p class="text-lg text-[#2d2016]/80 leading-relaxed whitespace-pre-wrap">{{ work.description || '暫無簡述提供。' }}</p>
        </div>
      </section>

      <!-- Concept Tags Section -->
      <section class="bg-[#ffffff] rounded-lg p-6 md:p-8 shadow-sm border border-[#2d2016]/10">
        <div class="flex items-baseline gap-3 mb-5 border-b border-[#2d2016]/5 pb-3">
          <h2 class="text-xl md:text-2xl font-bold text-[#2d2016] tracking-tight">相關概念</h2>
        </div>

        <div v-if="work.work_concepts && work.work_concepts.length > 0" class="flex flex-wrap gap-2.5 md:gap-3">
          <router-link
            v-for="wc in displayedConcepts"
            :key="wc.concept_detail.slug"
            :to="`/concepts/${wc.concept_detail.slug}`"
            class="group flex items-center gap-1.5 px-3 py-1.5 bg-transparent border border-[#2d2016]/10 text-[#2d2016]/70 text-base font-medium rounded-lg hover:bg-[#f5f0e8]/50 hover:border-[#ae5630]/30 hover:text-[#ae5630] transition-all duration-200"
          >
            <span>{{ wc.concept_detail.name }}</span>
          </router-link>

          <button v-if="hiddenConceptsCount > 0 && !isConceptsExpanded" @click="isConceptsExpanded = true" class="flex items-center px-3 py-1.5 bg-transparent border border-dashed border-[#ae5630]/40 text-[#ae5630] text-sm font-medium rounded-lg hover:bg-[#ae5630]/5 hover:border-[#ae5630]/60 transition-all duration-200">
            + {{ hiddenConceptsCount }} 更多
          </button>
          <button v-if="isConceptsExpanded" @click="isConceptsExpanded = false" class="flex items-center px-3 py-1.5 bg-transparent border border-dashed border-[#ae5630]/40 text-[#ae5630] text-sm font-medium rounded-lg hover:bg-[#ae5630]/5 hover:border-[#ae5630]/60 transition-all duration-200">
            - 收合
          </button>
        </div>
        <div v-else class="text-[#2d2016]/40 py-2">尚無標註任何概念。</div>
      </section>

      <!-- Concept Descriptions (Spoilers) Section -->
      <section v-if="conceptDescriptions.length > 0" class="bg-[#ffffff] rounded-lg p-6 md:p-8 shadow-sm border border-[#2d2016]/10">
        <h2 class="text-xl md:text-2xl font-bold text-[#2d2016] tracking-tight mb-5 border-b border-[#2d2016]/5 pb-3">概念應用詳述</h2>
        <div class="space-y-6">
          <div v-for="wc in conceptDescriptions" :key="wc.id" class="flex flex-col md:flex-row gap-2 md:gap-6 pt-4 first:pt-0 border-t border-[#2d2016]/5 first:border-0">
            <div class="md:w-1/5 flex-shrink-0">
              <router-link
                :to="`/concepts/${wc.concept_detail.slug}`"
                class="group inline-flex items-center gap-1.5 px-3 py-1.5 bg-transparent border border-[#2d2016]/10 text-[#2d2016]/70 text-base font-medium rounded-lg hover:bg-[#f5f0e8]/50 hover:border-[#ae5630]/30 hover:text-[#ae5630] transition-all duration-200"
              >
                <span>{{ wc.concept_detail.name }}</span>
              </router-link>
            </div>
            <div class="md:w-4/5">
              <span
                v-if="isSpoilerProtected && !revealedSpoilers.has(wc.id)"
                @click="revealSpoiler(wc.id)"
                class="cursor-pointer text-[#2d2016]/5 hover:text-[#2d2016]/60 transition-all duration-300 select-none block text-[17px] leading-relaxed whitespace-pre-wrap"
                title="點擊顯示劇透內容"
              >
                {{ wc.description }}
              </span>
              <span v-else class="block text-[17px] text-[#2d2016]/80 leading-relaxed whitespace-pre-wrap">
                {{ wc.description }}
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- Publications / Releases Section -->
      <section class="bg-[#ffffff] rounded-lg p-6 md:p-8 shadow-sm border border-[#2d2016]/10 overflow-hidden">
        <h2 class="text-xl md:text-2xl font-bold text-[#2d2016] tracking-tight mb-5 border-b border-[#2d2016]/5 pb-3">出版與發行</h2>
        <div v-if="work.publications && work.publications.length > 0" class="overflow-x-auto -mx-6 md:mx-0 px-6 md:px-0">
          <table class="w-full text-left border-collapse min-w-[900px]">
            <thead>
              <tr class="border-b border-[#2d2016]/10 text-[#2d2016]/60 text-base font-medium tracking-wide">
                <th class="pb-3 pr-4 font-normal w-48">名稱</th>
                <th class="pb-3 pr-4 font-normal w-24">形式</th>
                <th class="pb-3 pr-4 font-normal w-20">年份</th>
                <th class="pb-3 pr-4 font-normal w-32">出版商</th>
                <th class="pb-3 pr-4 font-normal w-40">參與</th>
                <th class="pb-3 pr-4 font-normal w-32">ISBN</th>
                <th class="pb-3 font-normal">備註</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#2d2016]/5 text-[#2d2016]/80 text-[16px]">
              <tr v-for="pub in work.publications" :key="pub.id" class="hover:bg-[#f5f0e8]/30 transition-colors">
                <td class="py-3.5 pr-4 align-top font-medium">{{ pub.title }}</td>
                <td class="py-3.5 pr-4 align-top"><span class="px-2 py-0.5 rounded bg-[#2d2016]/5 text-sm">{{ pub.media_display || '-' }}</span></td>
                <td class="py-3.5 pr-4 align-top font-mono text-[#2d2016]/60">{{ pub.year || '-' }}</td>
                <td class="py-3.5 pr-4 align-top">{{ pub.publisher_detail?.name || '-' }}</td>
                <td class="py-3.5 pr-4 align-top text-sm">
                  <template v-if="pub.credits.length > 0">
                    <span v-for="(group, gIdx) in getGroupedPubCredits(pub.credits)" :key="gIdx">
                      <span v-for="(c, cIdx) in group.credits" :key="c.id">
                        <router-link :to="`/agents/${c.agent_detail.id}`" class="hover:text-[#ae5630] transition-colors">
                          {{ c.display_name || c.agent_detail.name }}
                        </router-link><span v-if="cIdx < group.credits.length - 1">、</span>
                      </span>
                      <span class="text-[#2d2016]/60 ml-0.5">{{ group.label }}</span>
                      <span v-if="gIdx < getGroupedPubCredits(pub.credits).length - 1">；</span>
                    </span>
                  </template>
                  <span v-else>-</span>
                </td>
                <td class="py-3.5 pr-4 align-top font-mono text-sm text-[#2d2016]/60">{{ pub.isbn || '-' }}</td>
                <td class="py-3.5 align-top text-[#2d2016]/60">{{ pub.note || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-[#2d2016]/40 py-2">無出版或發行紀錄。</div>
      </section>

      <!-- Catalogues Section -->
      <section class="bg-[#ffffff] rounded-lg p-6 md:p-8 shadow-sm border border-[#2d2016]/10 overflow-hidden">
        <h2 class="text-xl md:text-2xl font-bold text-[#2d2016] tracking-tight mb-5 border-b border-[#2d2016]/5 pb-3">收錄與獲獎目錄</h2>
        <div v-if="work.catalogue_entries && work.catalogue_entries.length > 0" class="overflow-x-auto -mx-6 md:mx-0 px-6 md:px-0">
          <table class="w-full text-left border-collapse min-w-[700px]">
            <thead>
              <tr class="border-b border-[#2d2016]/10 text-[#2d2016]/60 text-base font-medium tracking-wide">
                <th class="pb-3 pr-4 font-normal w-24">類型</th>
                <th class="pb-3 pr-4 font-normal w-48">名稱</th>
                <th class="pb-3 pr-4 font-normal w-20">年份</th>
                <th class="pb-3 pr-4 font-normal w-32">維護者</th>
                <th class="pb-3 font-normal">備註</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#2d2016]/5 text-[#2d2016]/80 text-[16px]">
              <tr v-for="entry in work.catalogue_entries" :key="entry.id" class="hover:bg-[#f5f0e8]/30 transition-colors">
                <td class="py-3.5 pr-4 align-top"><span class="px-2 py-0.5 rounded bg-[#2d2016]/5 text-sm">{{ entry.catalogue_detail.catalogue_type_display }}</span></td>
                <td class="py-3.5 pr-4 align-top font-medium">{{ entry.catalogue_detail.title }}</td>
                <td class="py-3.5 pr-4 align-top font-mono text-[#2d2016]/60">{{ entry.catalogue_detail.year || '-' }}</td>
                <td class="py-3.5 pr-4 align-top">
                  <router-link v-if="entry.catalogue_detail.curator_detail" :to="`/agents/${entry.catalogue_detail.curator_detail.id}`" class="hover:text-[#ae5630] transition-colors">{{ entry.catalogue_detail.curator_detail.name }}</router-link>
                  <span v-else>-</span>
                </td>
                <td class="py-3.5 align-top text-[#2d2016]/60">{{ entry.note || '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-[#2d2016]/40 py-2">無收錄與獲獎紀錄。</div>
      </section>
    </template>
  </div>
</template>
