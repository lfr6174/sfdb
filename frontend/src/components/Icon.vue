<script setup lang="ts">
/**
 * Icon — Single source of truth for inline SVG icons.
 *
 * Every icon shares a 24×24 viewBox and inherits its color and size from the
 * parent via class, e.g. <Icon name="box" class="h-10 w-10 text-main/15" />.
 * To add an icon: paste its <path> "d" string into ICONS below and use its key.
 */
const ICONS = {
  // Open box — "no records" empty states
  box: 'M3.75 9.776c.112-.017.227-.026.344-.026h15.812c.117 0 .232.009.344.026m-16.5 0a2.25 2.25 0 0 0-1.883 2.542l.857 6a2.25 2.25 0 0 0 2.227 1.932H19.05a2.25 2.25 0 0 0 2.227-1.932l.857-6a2.25 2.25 0 0 0-1.883-2.542m-16.5 0V6A2.25 2.25 0 0 1 6 3.75h3.879a1.5 1.5 0 0 1 1.06.44l2.122 2.12a1.5 1.5 0 0 0 1.06.44H18A2.25 2.25 0 0 1 20.25 9v.776',
  // Bell with slash — "no announcements" empty state
  'bell-off':
    'M9.143 17.082a24.248 24.248 0 0 0 3.844.148m-3.844-.148a23.856 23.856 0 0 1-5.455-1.31 8.964 8.964 0 0 0 2.3-5.542m3.155 6.852a3 3 0 0 0 5.667 1.97m1.965-2.277L21 21m-4.225-4.225a23.81 23.81 0 0 0 .498-2.242M3 3l4.241 4.241m0 0A23.94 23.94 0 0 1 12 6c2.57 0 5.026.4 7.334 1.15m-7.078 7.078L3 3',
  // Circular arrows — "shuffle / refresh"
  refresh:
    'M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99',
  // X — close / dismiss
  close: 'M18 6 6 18M6 6l12 12',
  // Chevron pointing up — "back to top"
  'chevron-up': 'm18 15-6-6-6 6',
} as const

withDefaults(
  defineProps<{
    name: keyof typeof ICONS
    strokeWidth?: number
  }>(),
  { strokeWidth: 1.5 },
)
</script>

<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    :stroke-width="strokeWidth"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <path :d="ICONS[name]" />
  </svg>
</template>
