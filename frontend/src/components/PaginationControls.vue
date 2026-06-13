<script setup lang="ts">
/**
 * PaginationControls — Paginator for long list views (Works, Concepts).
 * Disables boundaries dynamically based on DRF's total page count.
 */
defineProps<{
  currentPage: number
  totalPages: number
  hasPrev?: boolean
  hasNext?: boolean
}>()

const emit = defineEmits<{
  (e: 'changePage', direction: number): void
}>()
</script>

<template>
  <div class="border-main/5 mt-6 flex items-center justify-center gap-4 border-t pt-6 pb-4">
    <button
      :disabled="!hasPrev"
      class="rounded-none border px-6 py-2 text-base font-medium transition-colors"
      :class="
        hasPrev
          ? 'border-main/20 text-main/70 hover:bg-hover hover:text-primary bg-bg'
          : 'border-main/10 text-main/30 cursor-not-allowed bg-transparent'
      "
      @click="emit('changePage', -1)"
    >
      上一頁
    </button>
    <span class="text-main/50 text-base">
      第
      <span class="text-main font-bold">{{ currentPage }}</span>
      /
      <span class="text-main font-bold">{{ totalPages }}</span>
      頁
    </span>
    <button
      :disabled="!hasNext"
      class="rounded-none border px-6 py-2 text-base font-medium transition-colors"
      :class="
        hasNext
          ? 'border-main/20 text-main/70 hover:bg-hover hover:text-primary bg-bg'
          : 'border-main/10 text-main/30 cursor-not-allowed bg-transparent'
      "
      @click="emit('changePage', 1)"
    >
      下一頁
    </button>
  </div>
</template>
