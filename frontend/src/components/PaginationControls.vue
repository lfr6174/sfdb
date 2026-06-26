<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  currentPage: number
  totalPages: number
}>()

const emit = defineEmits<{
  changePage: [page: number]
}>()

const pages = computed<(number | '...')[]>(() => {
  const { currentPage: cur, totalPages: total } = props
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)

  const result: (number | '...')[] = [1]

  if (cur > 3) result.push('...')

  const start = Math.max(2, cur - 1)
  const end = Math.min(total - 1, cur + 1)
  for (let i = start; i <= end; i++) result.push(i)

  if (cur < total - 2) result.push('...')

  result.push(total)
  return result
})

const cellBase =
  'flex h-9 min-w-[36px] items-center justify-center border text-sm transition-colors'
const cellActive = 'bg-primary border-primary text-bg cursor-default'
const cellNormal =
  'border-main/20 text-main/70 hover:border-primary/40 hover:bg-hover hover:text-primary cursor-pointer'
const cellDisabled = 'border-main/10 text-main/25 cursor-not-allowed'
</script>

<template>
  <div class="border-main/5 mt-6 flex items-center justify-center gap-1 border-t pt-6 pb-4">
    <button
      :disabled="currentPage === 1"
      :class="[cellBase, currentPage > 1 ? cellNormal : cellDisabled]"
      @click="currentPage > 1 && emit('changePage', currentPage - 1)"
    >
      ←
    </button>

    <!-- Mobile: stable current/total indicator -->
    <span :class="[cellBase, 'border-main/20 text-main/70 px-3 tabular-nums sm:hidden']">
      {{ currentPage }} / {{ totalPages }}
    </span>

    <!-- Desktop: full numbered pagination -->
    <template
      v-for="(p, i) in pages"
      :key="i"
    >
      <span
        v-if="p === '...'"
        class="text-main/30 hidden h-9 min-w-[36px] items-center justify-center text-sm sm:flex"
      >
        …
      </span>
      <button
        v-else
        :disabled="p === currentPage"
        :class="[cellBase, 'hidden sm:flex', p === currentPage ? cellActive : cellNormal]"
        @click="p !== currentPage && emit('changePage', p as number)"
      >
        {{ p }}
      </button>
    </template>

    <button
      :disabled="currentPage === totalPages"
      :class="[cellBase, currentPage < totalPages ? cellNormal : cellDisabled]"
      @click="currentPage < totalPages && emit('changePage', currentPage + 1)"
    >
      →
    </button>
  </div>
</template>
