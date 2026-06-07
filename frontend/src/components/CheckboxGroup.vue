<script setup lang="ts">
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
      class="group flex cursor-pointer items-center gap-2"
    >
      <input
        type="checkbox"
        :value="opt.value"
        :checked="modelValue.includes(opt.value)"
        class="text-primary border-main/25 h-4 w-4 shrink-0 cursor-pointer rounded-none focus:ring-0 focus:ring-offset-0"
        @change="
          $emit(
            'update:modelValue',
            modelValue.includes(opt.value)
              ? modelValue.filter((v) => v !== opt.value)
              : [...modelValue, opt.value],
          )
        "
      />
      <span class="text-main/60 group-hover:text-primary text-sm transition-colors">
        {{ opt.label }}
      </span>
    </label>
  </div>
</template>
