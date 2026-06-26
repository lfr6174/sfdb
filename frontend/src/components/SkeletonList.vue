<script setup lang="ts">
/**
 * SkeletonList — Placeholder shown while a list is loading.
 *
 *   variant="rows" (default) renders stacked title/subtitle bars for row lists.
 *   variant="tags" renders a cloud of pill shapes for the concept explorer.
 *
 * Purely decorative, so it is hidden from assistive tech.
 */
withDefaults(
  defineProps<{
    variant?: 'rows' | 'tags'
    rows?: number
    tags?: number
  }>(),
  { variant: 'rows', rows: 6, tags: 12 },
)
</script>

<template>
  <div
    class="animate-pulse"
    aria-hidden="true"
  >
    <div
      v-if="variant === 'rows'"
      class="flex flex-col"
    >
      <div
        v-for="n in rows"
        :key="n"
        class="border-main/5 flex flex-col gap-2.5 border-b py-4 last:border-0"
      >
        <div class="bg-main/10 h-4 w-1/3 rounded"></div>
        <div class="bg-main/10 h-3 w-2/3 rounded"></div>
      </div>
    </div>

    <div
      v-else
      class="flex flex-wrap gap-2 py-4"
    >
      <div
        v-for="n in tags"
        :key="n"
        class="bg-main/10 h-7 rounded"
        :style="{ width: `${48 + (n % 4) * 24}px` }"
      ></div>
    </div>
  </div>
</template>
