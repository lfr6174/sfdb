<script setup lang="ts">
defineProps<{
  checked: boolean
  name?: string
  value?: string
}>()

defineEmits<{ change: [event: Event] }>()
</script>

<template>
  <input
    type="checkbox"
    :name="name"
    :value="value"
    :checked="checked"
    class="custom-checkbox border-main/30 ring-offset-bg hover:border-primary/50 checked:border-primary checked:bg-primary peer focus-visible:ring-primary/30 h-[14px] w-[14px] shrink-0 cursor-pointer appearance-none rounded-[2px] border transition-all outline-none focus-visible:ring-2 focus-visible:ring-offset-1"
    @change="$emit('change', $event)"
  />
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
