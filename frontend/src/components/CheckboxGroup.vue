<script setup lang="ts">
/**
 * CheckboxGroup — Multi-select input for complex database filters (e.g., Work Genres).
 * Synchronizes selected arrays directly with URL search parameters.
 */
import CustomCheckbox from './CustomCheckbox.vue'

withDefaults(
  defineProps<{
    options: { value: string; label: string }[]
    modelValue: string[]
    layoutClass?: string
  }>(),
  {
    layoutClass: 'flex flex-col gap-2',
  },
)

defineEmits<{ 'update:modelValue': [val: string[]] }>()
</script>

<template>
  <div :class="layoutClass">
    <label
      v-for="opt in options"
      :key="opt.value"
      class="group flex cursor-pointer items-start gap-2"
    >
      <CustomCheckbox
        :name="opt.value"
        :value="opt.value"
        :checked="modelValue.includes(opt.value)"
        @change="
          $emit(
            'update:modelValue',
            modelValue.includes(opt.value)
              ? modelValue.filter((v) => v !== opt.value)
              : [...modelValue, opt.value],
          )
        "
      />
      <span
        class="text-main/60 group-hover:text-main peer-checked:text-main text-sm transition-colors peer-checked:font-medium"
      >
        {{ opt.label }}
      </span>
    </label>
  </div>
</template>
