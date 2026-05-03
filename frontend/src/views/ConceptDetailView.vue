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

const earliestYear = computed(() => {
  if (!concept.value?.work_concepts || concept.value.work_concepts.length === 0) return '—'
  const years = concept.value.work_concepts
    .map((w: any) => parseInt(w.year))
    .filter((y: number) => !isNaN(y))
  if (years.length === 0) return '—'
  return Math.min(...years)
})

const latestYear = computed(() => {
  if (!concept.value?.work_concepts || concept.value.work_concepts.length === 0) return '—'
  const years = concept.value.work_concepts
    .map((w: any) => parseInt(w.year))
    .filter((y: number) => !isNaN(y))
  if (years.length === 0) return '—'
  return Math.max(...years)
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
  <div class="max-w-4xl mx-auto space-y-4">

    <div v-if="isLoading" class="card text-center py-16 text-main/50 text-sm font-medium">
      正在讀取概念資料...
    </div>

    <template v-else-if="concept">
      <div class="mb-4">
        <router-link to="/concepts" class="back-link">
          ← 返回概念探索
        </router-link>
      </div>

      <div class="flex flex-col md:flex-row gap-4 items-start pb-12">

        <!-- Left: Main Content -->
        <div class="w-full md:w-7/12 lg:w-8/12 flex flex-col gap-5 md:gap-6">

          <!-- Personal Info -->
          <section class="card relative">
            <h1 class="text-2xl font-medium text-main mb-4">
              <span>{{ concept.name }}</span>
            </h1>

            <p class="text-sm text-main leading-relaxed whitespace-pre-wrap">{{ concept.description || '目前暫無關於此概念的詳細描述。' }}</p>

            <!-- Links -->
            <div v-if="concept.links && concept.links.length > 0" class="flex flex-wrap gap-4 mt-4">
              <a
                v-for="link in concept.links"
                :key="link.id"
                :href="link.url"
                target="_blank"
                rel="noopener noreferrer"
                class="text-sm text-primary hover:text-primary/70 transition-colors"
              >
                ↗ {{ link.title }}
              </a>
            </div>
          </section>

          <!-- Concept Application Examples -->
          <section class="card relative">
            <h2 class="section-label">概念應用範例</h2>

            <div v-if="validWorkConcepts.length > 0" class="flex flex-col">
              <div
                v-for="item in validWorkConcepts" :key="item.id"
                class="list-row group"
              >
                <span class="font-mono text-sm text-main/50 w-12 shrink-0 pt-0.5">{{ item.year || '-' }}</span>
                <div class="flex-1 min-w-0 flex flex-col gap-1.5">
                  <router-link :to="`/works/${item.work}`" class="text-base font-medium text-main group-hover:text-primary transition-colors w-fit block">
                    {{ item.work_title || '未知作品' }}
                  </router-link>
                  <span
                    v-if="isSpoilerProtected && !revealedSpoilers.has(item.id)"
                    @click="revealSpoiler(item.id)"
                    class="cursor-pointer text-main/40 hover:text-main/70 transition-all select-none block text-sm leading-relaxed whitespace-pre-wrap"
                    title="點擊顯示劇透內容"
                  >
                    {{ item.description }}
                  </span>
                  <span v-else class="block text-sm text-main/70 leading-relaxed whitespace-pre-wrap">
                    {{ item.description }}
                  </span>
                </div>
              </div>
            </div>
            <div v-else class="text-sm text-main/50 py-3">目前尚無收錄此概念的應用範例。</div>

            <!-- Link to all works -->
            <div class="mt-6 text-left">
              <router-link :to="{ path: '/works', query: { concept: concept.slug } }" class="text-sm font-medium text-primary hover:text-primary/70 transition-colors">
                瀏覽所有與「{{ concept.name }}」相關的作品（共 {{ concept.works_count || 0 }} 部） ↗
              </router-link>
            </div>
          </section>

        </div>

        <!-- Right: Sidebar -->
        <aside class="w-full md:w-5/12 lg:w-4/12 card shrink-0 md:sticky md:top-4 flex flex-col divide-y divide-main/10">

          <div class="py-4 first:pt-0 flex flex-col gap-1.5">
            <span class="text-xs font-medium tracking-widest uppercase text-main/40">收錄作品數</span>
            <span class="text-sm text-main">{{ concept.works_count || 0 }}</span>
          </div>

          <div class="py-4 flex flex-col gap-1.5">
            <span class="text-xs font-medium tracking-widest uppercase text-main/40">最早出現</span>
            <span class="font-mono text-sm text-main">{{ earliestYear }}</span>
          </div>

          <div class="py-4 flex flex-col gap-1.5">
            <span class="text-xs font-medium tracking-widest uppercase text-main/40">最近出現</span>
            <span class="font-mono text-sm text-main">{{ latestYear }}</span>
          </div>

          <div class="py-4 last:pb-0 flex flex-col gap-3">
            <div class="text-xs font-medium tracking-widest uppercase text-main/40 flex items-center justify-between">
              相關概念
              <span v-if="concept.related_concepts?.length > 0" class="badge !py-0 !px-1.5 text-xs font-mono">{{ concept.related_concepts.length }}</span>
            </div>

            <div v-if="concept.related_concepts && concept.related_concepts.length > 0" class="flex flex-wrap gap-2">
              <router-link
                v-for="related in concept.related_concepts"
                :key="related.slug"
                :to="`/concepts/${related.slug}`"
                class="tag"
              >
                {{ related.name }}
              </router-link>
            </div>
            <div v-else class="text-sm text-main/50 mt-2">尚未與任何概念建立關聯。</div>
          </div>

        </aside>

      </div>
    </template>

  </div>
</template>
