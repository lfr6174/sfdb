<script setup lang="ts">
defineProps<{
  modelValue: string
  options: { value: string; label: string }[]
  selectClass?: string
}>()

defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()
</script>

<template>
  <div class="relative">
    <select
      :value="modelValue"
      :class="
        selectClass ||
        'text-main/70 border-main/20 focus:border-primary/50 cursor-pointer appearance-none border-b bg-transparent py-1 pr-6 pl-0 text-sm transition-colors outline-none focus-visible:outline-2 focus-visible:outline-primary/50'
      "
      @change="$emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
    >
      <option
        v-for="option in options"
        :key="option.value"
        :value="option.value"
      >
        {{ option.label }}
      </option>
    </select>
    <svg
      class="text-main/40 pointer-events-none absolute top-1/2 right-2 -translate-y-1/2"
      width="9"
      height="5"
      viewBox="0 0 10 6"
      fill="none"
    >
      <path
        d="M0 0l5 6 5-6z"
        fill="currentColor"
      />
    </svg>
  </div>
</template>
