<script setup lang="ts">
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
  <div class="flex items-center justify-center gap-4 mt-6 pt-6 pb-4 border-t border-main/5">
    <button
      :disabled="!hasPrev"
      @click="emit('changePage', -1)"
      class="px-6 py-2 rounded-none text-base font-medium transition-colors border"
      :class="hasPrev ? 'border-main/20 text-main/70 hover:bg-hover hover:text-main bg-bg' : 'border-main/10 text-main/30 cursor-not-allowed bg-transparent'">
      上一頁
    </button>
    <span class="text-base font-mono text-main/50">
      第 <span class="text-main font-bold">{{ currentPage }}</span> / <span class="text-main font-bold">{{ totalPages }}</span> 頁
    </span>
    <button
      :disabled="!hasNext"
      @click="emit('changePage', 1)"
      class="px-6 py-2 rounded-none text-base font-medium transition-colors border"
      :class="hasNext ? 'border-main/20 text-main/70 hover:bg-hover hover:text-main bg-bg' : 'border-main/10 text-main/30 cursor-not-allowed bg-transparent'">
      下一頁
    </button>
  </div>
</template>
