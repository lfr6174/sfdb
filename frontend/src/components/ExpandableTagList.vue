<script setup lang="ts">
import { ref, computed } from 'vue'
import ConceptTag from './ConceptTag.vue'

const props = withDefaults(
  defineProps<{
    concepts: { name: string; slug: string; works_count?: number }[]
    limit?: number
  }>(),
  {
    limit: 10,
  },
)

const isExpanded = ref(false)

const displayedConcepts = computed(() => {
  if (isExpanded.value) return props.concepts
  return props.concepts.slice(0, props.limit)
})

const hiddenCount = computed(() => Math.max(0, props.concepts.length - props.limit))
</script>

<template>
  <div class="flex flex-wrap gap-1.5">
    <ConceptTag
      v-for="concept in displayedConcepts"
      :key="concept.slug || concept.id"
      :concept="concept"
    />

    <button
      v-if="hiddenCount > 0"
      class="text-primary border-primary/30 hover:bg-primary/5 inline-flex items-center border border-dashed px-2.5 py-1 text-xs whitespace-nowrap transition-all"
      @click="isExpanded = !isExpanded"
    >
      {{ isExpanded ? '− 收合' : `+ ${hiddenCount} 更多` }}
    </button>
  </div>
</template>
