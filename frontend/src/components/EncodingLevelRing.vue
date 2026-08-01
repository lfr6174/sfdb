<script setup lang="ts">
/**
 * EncodingLevelRing — four-segment ring pictogram for the work encoding
 * level (著錄層次). Lit segments = level (1–4), clockwise from the top;
 * unlit segments stay faint so the "out of four" denominator reads at a
 * glance. Follows Icon.vue conventions: 24×24 viewBox, color and size
 * inherited from the parent via class.
 */

// Four 70° arcs (r=9, centre 12,12) with 20° gaps, clockwise from 12 o'clock.
const SEGMENTS = [
  'M13.56 3.14A9 9 0 0 1 20.86 10.44',
  'M20.86 13.56A9 9 0 0 1 13.56 20.86',
  'M10.44 20.86A9 9 0 0 1 3.14 13.56',
  'M3.14 10.44A9 9 0 0 1 10.44 3.14',
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
