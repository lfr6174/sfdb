<script setup lang="ts">
withDefaults(
  defineProps<{
    concept: {
      name: string
      slug: string
      works_count?: number
    }
    size?: 'sm' | 'md'
  }>(),
  {
    size: 'sm', // Default to 'sm' for sidebars or inline lists
  },
)
</script>

<template>
  <router-link
    :to="`/concepts/${concept.slug}`"
    :class="[
      'border-main/12 hover:text-primary hover:bg-primary/3 hover:border-primary/20 inline-flex items-center border whitespace-nowrap no-underline transition-all',
      size === 'md'
        ? 'text-main/50 gap-2 px-3 py-1.5 text-sm'
        : 'text-main/50 gap-1.5 px-2.5 py-1 text-xs',
    ]"
  >
    <span>{{ concept.name }}</span>
    <span
      v-if="concept.works_count !== undefined"
      class="text-main/40 font-mono text-[10px]"
    >
      {{ concept.works_count }}
    </span>
  </router-link>
</template>
