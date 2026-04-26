<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'

const route = useRoute()

const concept = ref<any>(null)
const isLoading = ref(true)

const isSpoilerProtected = ref(localStorage.getItem('spoiler') !== 'false')
const revealedSpoilers = ref<Set<number>>(new Set())

const handleSpoilerToggle = (e: any) => {
  isSpoilerProtected.value = e.detail
}

const fetchConceptDetail = async () => {
  isLoading.value = true
  try {
    const response = await api.get(`/concepts/${route.params.slug}/`)
    concept.value = response.data
  } catch (error) {
    console.error('Failed to fetch concept details:', error)
  } finally {
    isLoading.value = false
  }
}

const revealSpoiler = (itemId: number) => {
  revealedSpoilers.value.add(itemId)
}

const validWorkConcepts = computed(() => {
  if (!concept.value?.work_concepts) return []
  return concept.value.work_concepts.filter((item: any) => item.description && item.description.trim() !== '')
})

// Refetch data to handle same-route navigation
watch(() => route.params.slug, (newSlug, oldSlug) => {
  if (newSlug && newSlug !== oldSlug) {
    revealedSpoilers.value.clear()
    fetchConceptDetail()
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
})

onMounted(() => {
  fetchConceptDetail()
  window.addEventListener('spoiler-toggle', handleSpoilerToggle)
})

onUnmounted(() => {
  window.removeEventListener('spoiler-toggle', handleSpoilerToggle)
})
</script>

<template>
  <div class="max-w-5xl mx-auto space-y-6">

    <div v-if="isLoading" class="text-center py-16 text-[#2d2016]/50 font-medium bg-[#ffffff] rounded-lg border border-[#2d2016]/10">
      正在讀取概念資料...
    </div>

    <template v-else-if="concept">
      <router-link to="/concepts" class="inline-flex items-center text-sm font-medium text-[#2d2016]/50 hover:text-[#ae5630] transition-colors mb-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        返回概念探索
      </router-link>

      <section class="bg-[#ffffff] rounded-lg p-6 md:p-8 shadow-sm border border-[#2d2016]/10 relative">
        <h1 class="text-3xl md:text-4xl font-bold text-[#2d2016] tracking-tight mb-4 flex items-baseline gap-3 flex-wrap">
          <span>{{ concept.name }}</span>
        </h1>

        <p class="text-lg text-[#2d2016]/80 leading-relaxed whitespace-pre-wrap">{{ concept.description || '目前暫無關於此概念的詳細描述。' }}</p>

        <div v-if="concept.links && concept.links.length > 0" class="flex flex-wrap gap-4 mt-6 pt-5 border-t border-[#2d2016]/5">
          <a
            v-for="link in concept.links"
            :key="link.id"
            :href="link.url"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center text-base font-medium text-[#ae5630] hover:text-[#ae5630]/70 transition-colors gap-1.5"
          >
            ↗ {{ link.title }}
          </a>
        </div>
      </section>

      <section v-if="concept.related_concepts_detail && concept.related_concepts_detail.length > 0" class="bg-[#ffffff] rounded-lg p-6 md:p-8 shadow-sm border border-[#2d2016]/10">
        <div class="flex items-baseline gap-3 mb-5 border-b border-[#2d2016]/5 pb-3">
          <h2 class="text-xl md:text-2xl font-bold text-[#2d2016] tracking-tight">相關概念</h2>
        </div>

        <div class="flex flex-wrap gap-2.5 md:gap-3">
          <router-link
            v-for="related in concept.related_concepts_detail"
            :key="related.slug"
            :to="`/concepts/${related.slug}`"
            class="group flex items-center gap-1.5 px-3 py-1.5 bg-transparent border border-[#2d2016]/10 text-[#2d2016]/70 text-base font-medium rounded-lg hover:bg-[#f5f0e8]/50 hover:border-[#ae5630]/30 hover:text-[#ae5630] transition-all duration-200"
          >
            <span>{{ related.name }}</span>
          </router-link>
        </div>
      </section>

      <section class="bg-[#ffffff] rounded-lg p-6 md:p-8 shadow-sm border border-[#2d2016]/10 overflow-hidden">
        <div class="flex items-baseline gap-3 mb-5 border-b border-[#2d2016]/5 pb-3">
          <h2 class="text-xl md:text-2xl font-bold text-[#2d2016] tracking-tight">概念應用範例</h2>
        </div>

        <div v-if="validWorkConcepts.length > 0" class="overflow-x-auto -mx-6 md:mx-0 px-6 md:px-0">
          <table class="w-full text-left border-collapse min-w-[600px]">
            <thead>
              <tr class="border-b border-[#2d2016]/10 text-[#2d2016]/60 text-base font-medium tracking-wide">
                <th class="pb-3 pr-4 font-normal w-1/4">作品標題</th>
                <th class="pb-3 font-normal w-3/4">概念在作品中如何運作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#2d2016]/5 text-[#2d2016]/80 text-[17px]">
              <tr v-for="item in validWorkConcepts" :key="item.id" class="hover:bg-[#f5f0e8]/30 transition-colors group">
                <td class="py-4 pr-4 align-top">
                  <!-- Support varied API response structures -->
                  <router-link :to="`/works/${item.work_detail?.id || item.work}`" class="text-lg font-medium group-hover:text-[#ae5630] transition-colors block">
                    {{ item.work_detail?.title || item.work_title || '未知作品' }}
                  </router-link>
                </td>
                <td class="py-4 align-top leading-relaxed">
                  <span
                    v-if="isSpoilerProtected && !revealedSpoilers.has(item.id)"
                    @click="revealSpoiler(item.id)"
                    class="cursor-pointer text-[#2d2016]/5 hover:text-[#2d2016]/60 transition-all duration-300 select-none block"
                    title="點擊顯示劇透內容"
                  >
                    {{ item.description }}
                  </span>
                  <span v-else class="block">
                    {{ item.description }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-[#2d2016]/40 py-2">目前尚無收錄此概念的應用範例。</div>
      </section>

      <div class="pt-4 pb-12 text-left">
        <router-link :to="{ path: '/works', query: { concept: concept.slug } }" class="inline-flex items-center text-base font-medium text-[#ae5630] hover:text-[#ae5630]/70 transition-colors">
          瀏覽所有與「{{ concept.name }}」相關的作品（共 {{ concept.works_count }} 部） ↗
        </router-link>
      </div>
    </template>

  </div>
</template>
