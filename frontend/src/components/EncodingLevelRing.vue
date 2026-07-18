<script setup lang="ts">
/**
 * EncodingLevelRing — three-segment ring pictogram for the work encoding
 * level (著錄層次). Lit segments = level (1–3), clockwise from the top;
 * unlit segments stay faint so the "out of three" denominator reads at a
 * glance. Follows Icon.vue conventions: 24×24 viewBox, color and size
 * inherited from the parent via class.
 */

// Three 100° arcs (r=9, centre 12,12) with 20° gaps, clockwise from 12 o'clock.
const SEGMENTS = [
  'M13.56 3.14A9 9 0 0 1 20.46 15.08',
  'M18.89 17.78A9 9 0 0 1 5.11 17.78',
  'M3.54 15.08A9 9 0 0 1 10.44 3.14',
]

defineProps<{ level: number }>()
</script>

<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2.5"
    stroke-linecap="round"
    aria-hidden="true"
  >
    <path
      v-for="(d, i) in SEGMENTS"
      :key="i"
      :d="d"
      :opacity="i < level ? 1 : 0.25"
    />
  </svg>
</template>
