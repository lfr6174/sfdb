<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'

const route = useRoute()

const person = ref<any>(null)
const isLoading = ref(true)
const isConceptsExpanded = ref(false)

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

// Manage displayed concepts for the "show more" functionality
const DISPLAY_LIMIT = 10
const displayedConcepts = computed(() => {
  if (!person.value?.concept_stats) return []
  if (isConceptsExpanded.value) return person.value.concept_stats
  return person.value.concept_stats.slice(0, DISPLAY_LIMIT)
})

const hiddenConceptsCount = computed(() => {
  if (!person.value?.concept_stats) return 0
  return Math.max(0, person.value.concept_stats.length - DISPLAY_LIMIT)
})
</script>

<template>
  <div class="max-w-5xl mx-auto space-y-6">

    <div v-if="isLoading" class="text-center py-16 text-[#2d2016]/50 font-medium bg-[#ffffff] rounded-lg border border-[#2d2016]/10">
      正在讀取人物資料...
    </div>

    <template v-else-if="person">
      <!-- Back Link -->
      <router-link to="/persons" class="inline-flex items-center text-sm font-medium text-[#2d2016]/50 hover:text-[#ae5630] transition-colors mb-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        返回人物列表
      </router-link>

      <!-- Header Info Section -->
      <section class="bg-[#ffffff] rounded-lg p-6 md:p-8 shadow-sm border border-[#2d2016]/10 relative">
        <h1 class="text-3xl md:text-4xl font-bold text-[#2d2016] tracking-tight mb-4 flex items-baseline gap-3 flex-wrap">
          <span>{{ person.name }}</span>
          <span v-if="person.aliases && person.aliases.length > 0" class="text-sm md:text-2xl font-normal text-[#2d2016]/40">
            {{ person.aliases.map((a: any) => a.name).join(' 、 ') }}
          </span>
        </h1>

        <p class="text-lg text-[#2d2016]/80 leading-relaxed whitespace-pre-wrap">{{ person.bio || '暫無簡歷提供。' }}</p>

        <!-- Links -->
        <div v-if="person.links && person.links.length > 0" class="flex flex-wrap gap-4 mt-5">
          <a
            v-for="link in person.links"
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

      <!-- Concept Tags Section -->
      <section class="bg-[#ffffff] rounded-lg p-6 md:p-8 shadow-sm border border-[#2d2016]/10">
        <div class="flex items-baseline gap-3 mb-5 border-b border-[#2d2016]/5 pb-3">
          <h2 class="text-xl md:text-2xl font-bold text-[#2d2016] tracking-tight">作品概念</h2>
          <span class="text-sm text-[#2d2016]/50 font-mono">{{ person.concept_stats?.length || 0 }}</span>
        </div>

        <div v-if="person.concept_stats && person.concept_stats.length > 0" class="flex flex-wrap gap-2.5 md:gap-3">
          <router-link
            v-for="concept in displayedConcepts"
            :key="concept.slug"
            :to="`/concepts/${concept.slug}`"
            class="group flex items-center gap-1.5 px-3 py-1.5 bg-transparent border border-[#2d2016]/10 text-[#2d2016]/70 text-base font-medium rounded-lg hover:bg-[#f5f0e8]/50 hover:border-[#ae5630]/30 hover:text-[#ae5630] transition-all duration-200"
          >
            <span>{{ concept.name }}</span>
            <span class="text-[13px] font-mono text-[#2d2016]/40 group-hover:text-[#ae5630]/60 transition-colors">{{ concept.count }}</span>
          </router-link>

          <!-- Show More Bubble -->
          <button
            v-if="hiddenConceptsCount > 0 && !isConceptsExpanded"
            @click="isConceptsExpanded = true"
            class="flex items-center px-3 py-1.5 bg-transparent border border-dashed border-[#ae5630]/40 text-[#ae5630] text-sm font-medium rounded-lg hover:bg-[#ae5630]/5 hover:border-[#ae5630]/60 transition-all duration-200"
          >
            + {{ hiddenConceptsCount }} 更多
          </button>
          <button
            v-if="isConceptsExpanded"
            @click="isConceptsExpanded = false"
            class="flex items-center px-3 py-1.5 bg-transparent border border-dashed border-[#ae5630]/40 text-[#ae5630] text-sm font-medium rounded-lg hover:bg-[#ae5630]/5 hover:border-[#ae5630]/60 transition-all duration-200"
          >
            - 收合
          </button>
        </div>
        <div v-else class="text-[#2d2016]/40 py-2">該人物尚未與任何概念建立關聯。</div>
      </section>

      <!-- Participated Works Section (Table-like) -->
      <section class="bg-[#ffffff] rounded-lg p-6 md:p-8 shadow-sm border border-[#2d2016]/10 overflow-hidden">
        <div class="flex items-baseline gap-3 mb-5 border-b border-[#2d2016]/5 pb-3">
          <h2 class="text-xl md:text-2xl font-bold text-[#2d2016] tracking-tight">歷年作品</h2>
          <span class="text-sm text-[#2d2016]/50 font-mono">{{ person.participated_works?.length || 0 }}</span>
        </div>

        <div v-if="person.participated_works && person.participated_works.length > 0" class="overflow-x-auto -mx-6 md:mx-0 px-6 md:px-0">
          <table class="w-full text-left border-collapse min-w-[700px]">
            <thead>
              <tr class="border-b border-[#2d2016]/10 text-[#2d2016]/60 text-base font-medium tracking-wide">
                <th class="pb-3 pr-4 font-normal w-20">年份</th>
                <th class="pb-3 pr-4 font-normal">標題</th>
                <th class="pb-3 pr-4 font-normal w-32">類型</th>
                <th class="pb-3 pr-4 font-normal w-32">參與</th>
                <th class="pb-3 font-normal w-64">概念</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#2d2016]/5 text-[#2d2016]/80 text-[17px]">
              <tr v-for="work in person.participated_works" :key="work.id" class="hover:bg-[#f5f0e8]/30 transition-colors group">
                <td class="py-4 pr-4 font-mono text-[#2d2016]/50 align-top">{{ work.year || '-' }}</td>
                <td class="py-4 pr-4 align-top">
                  <router-link :to="`/works/${work.id}`" class="text-lg font-medium group-hover:text-[#ae5630] transition-colors block">{{ work.title }}</router-link>
                  <div v-if="work.title_en" class="text-base text-[#2d2016]/40 mt-0.5">{{ work.title_en }}</div>
                </td>
                <td class="py-4 pr-4 text-[#2d2016]/60 align-top">
                  {{ work.work_length || '-' }} / {{ work.media_type || '-' }}
                </td>
                <td class="py-4 pr-4 align-top leading-snug">{{ work.roles.join('、') }}</td>
                <td class="py-4 align-top">
                  <div class="flex flex-wrap gap-2">
                    <router-link v-for="concept in work.concepts" :key="concept.slug" :to="`/concepts/${concept.slug}`" class="px-2 py-1 bg-[#2d2016]/5 hover:bg-[#ae5630]/10 text-[#2d2016]/70 hover:text-[#ae5630] text-sm font-medium rounded transition-colors cursor-pointer">{{ concept.name }}</router-link>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-[#2d2016]/40 py-2">尚無關聯的作品。</div>
      </section>
    </template>

  </div>
</template>
