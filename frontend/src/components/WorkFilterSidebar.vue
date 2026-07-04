<script setup lang="ts">
/**
 * WorkFilterSidebar — desktop-only filter column for the works list.
 * All filter state is owned by WorksView (URL-backed refs) and bound here
 * via named v-models; this component only renders and forwards changes.
 */
import type { Concept } from '../types'
import BaseSearchInput from './BaseSearchInput.vue'
import SectionTitle from './SectionTitle.vue'
import CheckboxGroup from './CheckboxGroup.vue'
import CustomCheckbox from './CustomCheckbox.vue'
import { GENRE_OPTIONS, LENGTH_OPTIONS, PROVENANCE_OPTIONS } from '../utils/constants'

defineProps<{
  /** Concepts currently active as filters (checked, shown on top). */
  selectedConcepts: Concept[]
  /** Featured concepts offered as quick picks below the selected ones. */
  featuredConcepts: Concept[]
}>()

const searchQuery = defineModel<string>('search', { required: true })
const isAdvancedMode = defineModel<boolean>('advancedMode', { required: true })
const selectedGenres = defineModel<string[]>('genres', { required: true })
const selectedLengths = defineModel<string[]>('lengths', { required: true })
const selectedProvenances = defineModel<string[]>('provenances', { required: true })

defineEmits<{ toggleConcept: [concept: Concept]; openModal: [] }>()
</script>

<template>
  <aside
    class="lg:border-main/10 hidden shrink-0 pt-6 md:pt-10 lg:block lg:w-56 lg:border-r lg:pr-8 lg:pb-20"
  >
    <!-- Search (Desktop) -->
    <div class="mb-7 hidden lg:block">
      <BaseSearchInput
        v-model="searchQuery"
        size="lg"
        placeholder="搜尋標題、作者…"
      />
      <div class="mt-2 flex justify-start">
        <button
          class="text-main/50 hover:text-primary decoration-main/20 hover:decoration-primary/50 text-sm font-medium tracking-wide underline underline-offset-4 transition-colors"
          @click="isAdvancedMode = !isAdvancedMode"
        >
          {{ isAdvancedMode ? '返回一般結果' : '進階搜索' }}
        </button>
      </div>
    </div>

    <!-- Genre Type -->
    <div class="mb-6">
      <SectionTitle class="mb-3">作品體裁</SectionTitle>
      <CheckboxGroup
        v-model="selectedGenres"
        :options="GENRE_OPTIONS"
      />
    </div>

    <!-- Work Length -->
    <div class="mb-6">
      <SectionTitle class="mb-3">作品篇幅</SectionTitle>
      <CheckboxGroup
        v-model="selectedLengths"
        :options="LENGTH_OPTIONS"
      />
    </div>

    <!-- Provenance -->
    <div class="mb-6">
      <SectionTitle class="mb-3">作品來源</SectionTitle>
      <CheckboxGroup
        v-model="selectedProvenances"
        :options="PROVENANCE_OPTIONS"
      />
    </div>

    <!-- Concept Tags -->
    <div>
      <SectionTitle class="mb-3">概念標籤</SectionTitle>

      <!-- Selected tags -->
      <div
        v-if="selectedConcepts.length > 0"
        class="mb-4"
      >
        <div class="flex flex-col gap-2">
          <label
            v-for="concept in selectedConcepts"
            :key="concept.id"
            class="group flex cursor-pointer items-center gap-2"
          >
            <CustomCheckbox
              name="selected-concept"
              :checked="true"
              @change="$emit('toggleConcept', concept)"
            />
            <span class="text-primary text-sm font-medium">{{ concept.name }}</span>
          </label>
        </div>
        <div class="border-main/10 mt-3 mb-3 border-t"></div>
      </div>

      <!-- Featured concepts -->
      <div class="space-y-4">
        <div class="flex flex-col gap-2">
          <label
            v-for="concept in featuredConcepts"
            :key="concept.id"
            class="group flex cursor-pointer items-center gap-2"
          >
            <CustomCheckbox
              name="featured-concept"
              :checked="false"
              @change="$emit('toggleConcept', concept)"
            />
            <span class="text-main/60 group-hover:text-primary text-sm transition-colors">
              {{ concept.name }}
            </span>
          </label>
        </div>
      </div>

      <button
        class="text-main/70 hover:text-primary decoration-main/20 hover:decoration-primary/50 mt-5 w-full text-left text-sm underline underline-offset-4 transition-colors"
        @click="$emit('openModal')"
      >
        展開所有標籤
      </button>
    </div>
  </aside>
</template>
