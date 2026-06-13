<script setup lang="ts">
/**
 * FilterChip — Toggleable UI chip for refining search results in the database.
 * Used for filtering works by genre, era, or origin (e.g., Original vs. Licensed).
 */
defineProps<{ label: string }>()
defineEmits<{ remove: [] }>()
</script>
<template>
  <span
    class="text-primary bg-primary/5 border-primary/15 inline-flex items-center gap-1 border px-2.5 py-1 text-xs"
  >
    {{ label }}
    <button
      class="ml-0.5 text-sm leading-none transition-opacity hover:opacity-60"
      @click.stop="$emit('remove')"
    >
      &times;
    </button>
  </span>
</template>
