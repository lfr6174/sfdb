<script setup lang="ts">
/**
 * WorkAdvancedSearch — the full-width advanced search form for the works
 * list. All filter state is owned by WorksView (URL-backed refs) and bound
 * here via named v-models; this component only renders and forwards changes.
 */
import type { CatalogueOption } from '../api/works'
import type { Concept } from '../types'
import SectionTitle from './SectionTitle.vue'
import FormRow from './FormRow.vue'
import CheckboxGroup from './CheckboxGroup.vue'
import EncodingLevelRing from './EncodingLevelRing.vue'
import {
  GENRE_OPTIONS,
  LENGTH_OPTIONS,
  PROVENANCE_OPTIONS,
  LANGUAGE_OPTIONS,
  ENCODING_LEVEL_OPTIONS,
} from '../utils/constants'

defineProps<{
  /** Catalogues grouped by type label, for the <optgroup> select. */
  cataloguesByType: Map<string, CatalogueOption[]>
  /** Concepts currently active as filters, shown as removable chips. */
  selectedConcepts: Concept[]
  /** Current result count for the「查看結果」button. */
  totalWorks: number
}>()

const searchQuery = defineModel<string>('search', { required: true })
const isAdvancedMode = defineModel<boolean>('advancedMode', { required: true })
const yearMin = defineModel<number | ''>('yearMin', { required: true })
const yearMax = defineModel<number | ''>('yearMax', { required: true })
const selectedGenres = defineModel<string[]>('genres', { required: true })
const selectedLengths = defineModel<string[]>('lengths', { required: true })
const selectedProvenances = defineModel<string[]>('provenances', { required: true })
const selectedLanguages = defineModel<string[]>('languages', { required: true })
const selectedEncodingLevels = defineModel<string[]>('encodingLevels', { required: true })
const selectedCatalogueTitle = defineModel<string>('catalogueTitle', { required: true })

defineEmits<{ toggleConcept: [concept: Concept]; openModal: []; clearAll: [] }>()

/** Full option entry (level + description) for an encoding level value. */
const encodingOption = (value: string) => ENCODING_LEVEL_OPTIONS.find((o) => o.value === value)
</script>

<template>
  <section class="border-main/10 mb-8 border-b pb-10">
    <SectionTitle class="mb-4">
      進階搜尋
      <template #action>
        <button
          class="text-main/50 border-main/10 hover:text-primary hover:border-primary/30 border px-3 py-1 text-xs transition-colors"
          @click="isAdvancedMode = false"
        >
          返回結果列表
        </button>
      </template>
    </SectionTitle>

    <!-- Definition-list style form: each row = label (left) + content (right) -->
    <dl class="divide-main/10 divide-y">
      <FormRow label="關鍵字">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="標題、作者、筆名等"
          class="text-main placeholder:text-main/30 border-main/20 focus:border-primary/50 w-full border-b bg-transparent pb-2 text-base transition-colors outline-none"
        />
      </FormRow>

      <FormRow label="發表年份">
        <div
          class="search-input border-main/20 focus-within:border-primary/50 inline-flex items-center border-b transition-colors"
        >
          <input
            v-model="yearMin"
            type="number"
            placeholder="YYYY"
            class="text-main placeholder:text-main/30 w-20 bg-transparent py-2 text-center font-mono text-base outline-none"
          />
          <span class="text-main/30 px-3 font-mono">—</span>
          <input
            v-model="yearMax"
            type="number"
            placeholder="YYYY"
            class="text-main placeholder:text-main/30 w-20 bg-transparent py-2 text-center font-mono text-base outline-none"
          />
        </div>
      </FormRow>

      <FormRow label="作品體裁">
        <CheckboxGroup
          v-model="selectedGenres"
          :options="GENRE_OPTIONS"
          layout-class="flex flex-wrap gap-x-6 gap-y-2"
        />
      </FormRow>

      <FormRow label="作品篇幅">
        <CheckboxGroup
          v-model="selectedLengths"
          :options="LENGTH_OPTIONS"
          layout-class="flex flex-wrap gap-x-6 gap-y-2"
        />
      </FormRow>

      <FormRow label="作品來源">
        <CheckboxGroup
          v-model="selectedProvenances"
          :options="PROVENANCE_OPTIONS"
          layout-class="flex flex-wrap gap-x-6 gap-y-2"
        />
      </FormRow>

      <FormRow label="原始語言">
        <CheckboxGroup
          v-model="selectedLanguages"
          :options="LANGUAGE_OPTIONS"
          layout-class="flex flex-wrap gap-x-6 gap-y-2"
        />
      </FormRow>

      <FormRow label="著錄層次">
        <CheckboxGroup
          v-model="selectedEncodingLevels"
          :options="ENCODING_LEVEL_OPTIONS"
          layout-class="flex flex-wrap gap-x-6 gap-y-2"
        >
          <template #label="{ option }">
            <span
              class="inline-flex items-center gap-1.5"
              :title="encodingOption(option.value)?.description"
            >
              <EncodingLevelRing
                :level="encodingOption(option.value)?.level ?? 0"
                class="h-3.5 w-3.5"
              />
              {{ option.label }}
            </span>
          </template>
        </CheckboxGroup>
      </FormRow>

      <FormRow label="精選／獎項">
        <div class="relative">
          <select
            v-model="selectedCatalogueTitle"
            class="text-main/70 border-main/20 focus:border-primary/50 focus-visible:outline-primary/50 w-full cursor-pointer appearance-none border-b bg-transparent py-1 pr-6 pl-0 text-sm transition-colors outline-none focus-visible:outline-2"
          >
            <option value="">（不限）</option>
            <template
              v-for="[type, items] in cataloguesByType"
              :key="type"
            >
              <optgroup :label="type">
                <option
                  v-for="c in items"
                  :key="c.id"
                  :value="c.title"
                >
                  {{ c.title }}
                </option>
              </optgroup>
            </template>
          </select>
          <svg
            class="text-main/40 pointer-events-none absolute top-1/2 right-2 -translate-y-1/2"
            width="9"
            height="5"
            viewBox="0 0 10 6"
            fill="none"
          >
            <path
              d="M0 0l5 6 5-6z"
              fill="currentColor"
            />
          </svg>
        </div>
      </FormRow>

      <FormRow
        label="概念標籤"
        align="top"
      >
        <button
          class="text-main/70 hover:text-primary decoration-main/20 hover:decoration-primary/50 text-left text-base underline underline-offset-4 transition-colors"
          @click="$emit('openModal')"
        >
          + 點擊選取概念標籤
        </button>
        <div
          v-if="selectedConcepts.length > 0"
          class="mt-3 flex flex-wrap gap-1.5"
        >
          <span
            v-for="concept in selectedConcepts"
            :key="concept.id"
            class="text-primary bg-primary/5 border-primary/15 inline-flex items-center gap-1 border px-2.5 py-1 text-xs"
          >
            {{ concept.name }}
            <button
              class="hover:text-primary/60 ml-0.5 text-sm leading-none transition-colors"
              :aria-label="`移除 ${concept.name}`"
              @click.stop="$emit('toggleConcept', concept)"
            >
              &times;
            </button>
          </span>
        </div>
      </FormRow>
    </dl>

    <!-- Footer Actions -->
    <div class="border-main/10 mt-10 flex justify-end gap-3 border-t pt-6">
      <button
        class="text-main/50 hover:text-primary px-3 py-1.5 text-sm transition-colors"
        @click="$emit('clearAll')"
      >
        清除條件
      </button>
      <button
        class="bg-primary text-bg px-4 py-1.5 text-sm font-medium transition-opacity hover:opacity-85"
        @click="isAdvancedMode = false"
      >
        查看結果 ({{ totalWorks }})
      </button>
    </div>
  </section>
</template>

<style scoped>
/* 移除 input number 的上下箭頭 */
input[type='number']::-webkit-inner-spin-button,
input[type='number']::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
input[type='number'] {
  -moz-appearance: textfield;
  appearance: textfield;
}

/* Custom focus state */
.search-input:focus-within {
  border-color: rgba(194, 113, 78, 0.5); /* primary/50 */
}
</style>
