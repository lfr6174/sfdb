<script setup lang="ts">
import { ref } from 'vue'

const model = defineModel<string>({ default: '' })
const inputRef = ref<HTMLInputElement | null>(null)

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
