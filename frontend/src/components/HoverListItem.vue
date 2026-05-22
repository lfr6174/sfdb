<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const props = defineProps<{
  to?: string | object
  tag?: string
}>()

const resolvedTag = computed(() => {
  if (props.tag) return props.tag
  return props.to ? RouterLink : 'div'
})
</script>

<template>
  <component
    :is="resolvedTag"
    :to="to"
    class="group border-main/10 relative z-0 block border-b py-4 transition-colors last:border-0"
  >
    <!-- Hover Background Overlay -->
    <div
      class="pointer-events-none absolute -inset-x-3 inset-y-0 -z-10 rounded-sm bg-transparent transition-colors group-hover:bg-white/5"
    ></div>

    <!-- Accent line -->
    <div
      class="group-hover:bg-primary pointer-events-none absolute top-0 bottom-0 -left-3 w-0.5 bg-transparent transition-colors"
    ></div>

    <slot />
  </component>
</template>
