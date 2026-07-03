<script setup lang="ts">
/**
 * FormRow — One row of a definition-list style form (advanced search):
 * a fixed-width uppercase label (dt) on the left and a content slot (dd).
 *
 * Rows are baseline-aligned by default; pass align="top" for multi-line
 * content such as tag clouds. Meant to be a direct child of a <dl> with
 * divide-y: vertical padding collapses at the first/last row so the form
 * sits flush against whatever surrounds it.
 */
defineProps<{
  label: string
  align?: 'baseline' | 'top'
}>()
</script>

<template>
  <div
    class="py-6 first:pt-0 last:pb-0 md:flex md:gap-6"
    :class="{ 'md:items-baseline': align !== 'top' }"
  >
    <dt
      class="text-main/40 mb-2 shrink-0 text-sm font-medium tracking-widest uppercase md:mb-0 md:w-28"
      :class="{ 'pt-0.5': align === 'top' }"
    >
      {{ label }}
    </dt>
    <dd class="flex-1">
      <slot />
    </dd>
  </div>
</template>
