<script setup lang="ts">
/**
 * BaseSearchInput — Primary search bar for filtering concepts or works.
 * Features an integrated clear button (Escape) and delegates debouncing to the parent.
 */
import { ref } from 'vue'

const { size = 'sm' } = defineProps<{
  /** sm: compact list-page style; lg: prominent style (works filters, modal) */
  size?: 'sm' | 'lg'
}>()

const model = defineModel<string>({ default: '' })
const inputRef = ref<HTMLInputElement | null>(null)

const sizeClasses = {
  sm: 'placeholder:text-main/35 focus:border-main/50 py-1.5 text-sm',
  lg: 'placeholder:text-main/40 focus:border-primary/50 py-2 text-base',
}

const emit = defineEmits<{ escape: [] }>()

defineExpose({
  focus: () => inputRef.value?.focus(),
})

const handleEscape = () => {
  if (model.value) {
    model.value = ''
  } else {
    emit('escape')
  }
}
</script>

<script lang="ts">
export default {
  inheritAttrs: false,
}
</script>

<template>
  <div class="relative w-full">
    <svg
      class="text-main/30 pointer-events-none absolute top-1/2 left-0 -translate-y-1/2"
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <circle
        cx="11"
        cy="11"
        r="8"
      />
      <path d="m21 21-4.3-4.3" />
    </svg>
    <input
      ref="inputRef"
      v-model="model"
      type="text"
      name="search"
      class="text-main border-main/20 focus-visible:outline-primary/50 w-full border-b bg-transparent pr-8 pl-6 transition-colors outline-none focus-visible:outline-2"
      :class="sizeClasses[size]"
      v-bind="$attrs"
      @keydown.esc.stop="handleEscape"
    />
    <button
      v-if="model"
      class="text-main/30 hover:text-primary absolute top-1/2 right-0 -translate-y-1/2 p-1 transition-colors"
      aria-label="清除搜尋"
      @click="model = ''"
    >
      <svg
        width="12"
        height="12"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2.5"
      >
        <path d="M18 6 6 18M6 6l12 12" />
      </svg>
    </button>
  </div>
</template>
