<script setup lang="ts">
/**
 * ConceptPickerModal — Dialog for rapidly searching and selecting sci-fi concepts.
 * Used for advanced filtering or navigating conceptual relationships.
 */
import { ref, computed, watch, nextTick, onUnmounted } from 'vue'
import SectionTitle from './SectionTitle.vue'
import BaseSearchInput from './BaseSearchInput.vue'
import CustomCheckbox from './CustomCheckbox.vue'
import { categoryOrder } from '../utils/constants'
import type { Concept } from '../types'

const props = defineProps<{
  modelValue: Concept[]
  allConcepts: Concept[]
  open: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Concept[]]
  close: []
}>()

const tempSelectedConcepts = ref<Concept[]>([])
const modalSearchQuery = ref('')
const searchInputRef = ref<InstanceType<typeof BaseSearchInput> | null>(null)

// Sync modal state when it opens
watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      tempSelectedConcepts.value = [...props.modelValue]
      modalSearchQuery.value = ''
      document.body.style.overflow = 'hidden' // Lock background scroll
      nextTick(() => {
        searchInputRef.value?.focus()
      })
    } else {
      document.body.style.overflow = '' // Restore background scroll
    }
  },
)

onUnmounted(() => {
  document.body.style.overflow = '' // Safety cleanup
})

const modalGroupedConcepts = computed(() => {
  const query = modalSearchQuery.value.toLowerCase()
  const filtered = props.allConcepts.filter((c) => c.name.toLowerCase().includes(query))

  // Group by the API's category_display: whatever categories arrive get a
  // group, so a future backend category shows up without frontend changes.
  const grouped: Record<string, Concept[]> = {}
  filtered.forEach((c) => {
    if (!grouped[c.category_display]) grouped[c.category_display] = []
    grouped[c.category_display].push(c)
  })

  for (const concepts of Object.values(grouped)) {
    concepts.sort((a, b) => a.name.localeCompare(b.name))
  }

  // Known categories in fixed order, unknown ones last
  return Object.fromEntries(
    Object.entries(grouped).sort(([a], [b]) => categoryOrder(a) - categoryOrder(b)),
  )
})

const toggleTempConcept = (concept: Concept) => {
  const index = tempSelectedConcepts.value.findIndex((c) => c.id === concept.id)
  if (index === -1) {
    tempSelectedConcepts.value.push(concept)
  } else {
    tempSelectedConcepts.value.splice(index, 1)
  }
}

const clearAll = () => {
  tempSelectedConcepts.value = []
}

const apply = () => {
  emit('update:modelValue', [...tempSelectedConcepts.value])
  emit('close')
}
</script>

<template>
  <div
    v-if="open"
    class="focus-visible:outline-primary/50 fixed inset-0 z-50 flex items-center justify-center p-4 outline-none focus-visible:outline-2 sm:p-6"
    tabindex="0"
    @keydown.esc="$emit('close')"
  >
    <div
      class="absolute inset-0 bg-black/50"
      @click="$emit('close')"
    ></div>
    <div
      class="bg-bg border-main/10 relative z-10 flex max-h-[88vh] w-full max-w-3xl flex-col overflow-hidden border"
    >
      <!-- Modal Header -->
      <div class="border-main/10 shrink-0 border-b px-6 pt-6 pb-5">
        <div class="mb-5 flex items-center justify-between">
          <h2 class="text-main text-xl font-normal">選取概念標籤</h2>
          <button
            class="text-main/40 border-main/10 hover:text-primary hover:border-primary/30 border px-3 py-1 text-sm transition-colors"
            @click="$emit('close')"
          >
            取消
          </button>
        </div>

        <BaseSearchInput
          ref="searchInputRef"
          v-model="modalSearchQuery"
          size="lg"
          placeholder="搜尋標籤…"
          @escape="$emit('close')"
        />

        <!-- Selected in modal -->
        <div class="mt-4 flex min-h-[28px] flex-wrap items-center gap-1.5">
          <span class="text-main/40 mr-1 shrink-0 text-sm font-medium tracking-widest uppercase">
            已選取
          </span>
          <span
            v-if="tempSelectedConcepts.length === 0"
            class="text-main/30 text-xs"
          >
            —
          </span>
          <span
            v-for="concept in tempSelectedConcepts"
            :key="concept.id"
            class="text-primary bg-primary/5 border-primary/15 inline-flex items-center gap-1 border px-2.5 py-1 text-xs"
          >
            {{ concept.name }}
            <button
              class="ml-0.5 text-sm leading-none transition-opacity hover:opacity-60"
              @click="toggleTempConcept(concept)"
            >
              &times;
            </button>
          </span>
        </div>
      </div>

      <!-- Modal Body -->
      <div class="flex-1 overflow-y-auto px-6 py-5">
        <div class="space-y-8">
          <div
            v-for="(concepts, cat) in modalGroupedConcepts"
            :key="cat"
          >
            <template v-if="concepts.length > 0">
              <SectionTitle class="mb-4">{{ cat }}</SectionTitle>
              <div class="grid grid-cols-1 gap-x-4 gap-y-1 sm:grid-cols-2 md:grid-cols-3">
                <label
                  v-for="concept in concepts"
                  :key="concept.id"
                  class="group hover:bg-primary/5 flex cursor-pointer items-center gap-2 px-2 py-1.5 transition-colors"
                >
                  <CustomCheckbox
                    name="concept"
                    :checked="tempSelectedConcepts.some((c) => c.id === concept.id)"
                    @change="toggleTempConcept(concept)"
                  />
                  <span
                    class="text-main/60 group-hover:text-primary truncate text-sm transition-colors"
                  >
                    {{ concept.name }}
                  </span>
                </label>
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="border-main/10 flex shrink-0 justify-end gap-3 border-t px-6 py-4">
        <button
          class="text-main/50 hover:text-primary px-3 py-1.5 text-xs transition-colors"
          @click="clearAll"
        >
          清除條件
        </button>
        <button
          class="text-bg bg-primary px-4 py-1.5 text-xs font-medium transition-opacity hover:opacity-85"
          @click="apply"
        >
          套用篩選
        </button>
      </div>
    </div>
  </div>
</template>
