<script setup lang="ts">
/**
 * SidebarRow — One row in a WorkDetailView sidebar section (publications,
 * catalogues, relations). Renders a fixed-width left column — a label (a year
 * or a relation type) with an optional gray badge below it — and a content slot.
 *
 * Pass `to` to make the whole row a hover-highlighted link (used by relations);
 * omit it for rows whose content carries its own links (publications, awards).
 */
import HoverListItem from './HoverListItem.vue'

defineProps<{
  label?: string | number | null
  badge?: string
  to?: string | object
}>()
</script>

<template>
  <component
    :is="to ? HoverListItem : 'div'"
    :to="to"
    :class="to ? 'block' : 'border-main/10 border-b last:border-0'"
  >
    <div class="flex items-start gap-3 py-3">
      <div class="flex w-14 shrink-0 flex-col items-start gap-1.5 pt-0.5">
        <span class="text-main/50 text-xs">{{ label ?? '-' }}</span>
        <span
          v-if="badge"
          class="text-main/50 bg-main/5 px-1.5 py-0.5 font-mono text-xs tracking-wide whitespace-nowrap"
        >
          {{ badge }}
        </span>
      </div>
      <div class="min-w-0 flex-1">
        <slot />
      </div>
    </div>
  </component>
</template>
