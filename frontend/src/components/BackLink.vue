<script setup lang="ts">
/**
 * BackLink — Standardized return navigation for detail pages (Works, Concepts, Posts).
 * Ensures visual consistency when returning to master lists.
 */
defineProps<{
  to: string | object
  text: string
}>()
</script>

<template>
  <router-link
    :to="to"
    class="text-main/40 hover:text-primary group inline-flex items-center gap-1.5 text-sm font-medium tracking-widest uppercase no-underline transition-colors"
  >
    <svg
      width="13"
      height="13"
      viewBox="0 0 14 14"
      fill="none"
      class="transition-transform group-hover:-translate-x-0.5"
    >
      <path
        d="M9 2L4 7L9 12"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
    {{ text }}
  </router-link>
</template>
