<script setup lang="ts">
/**
 * CheckboxGroup — Multi-select input for complex database filters (e.g., Work Genres).
 * Synchronizes selected arrays directly with URL search parameters.
 */
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
      <input
        type="checkbox"
        :name="opt.value"
        :value="opt.value"
        :checked="modelValue.includes(opt.value)"
        class="border-main/30 ring-offset-bg hover:border-primary/50 focus-visible:ring-primary/30 checked:border-primary checked:bg-primary custom-checkbox peer h-[14px] w-[14px] shrink-0 cursor-pointer appearance-none rounded-[2px] border transition-all outline-none focus-visible:ring-2 focus-visible:ring-offset-1"
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

<style scoped>
.custom-checkbox {
  position: relative;
  margin-top: 2px;
}
.custom-checkbox:checked::after {
  content: '';
  position: absolute;
  top: 1.5px;
  left: 4.5px;
  width: 3.5px;
  height: 7.5px;
  border: solid #f8f8f6;
  border-width: 0 1.5px 1.5px 0;
  transform: rotate(45deg);
}
</style>
