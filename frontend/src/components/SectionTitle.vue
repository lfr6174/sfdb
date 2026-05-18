<script setup lang="ts">
// Fallthrough attributes (e.g., class="mb-5") automatically bind to the root div
</script>

<template>
  <div class="flex items-center gap-3">
    <span class="text-main/40 text-sm font-medium tracking-widest whitespace-nowrap uppercase">
      <slot></slot>
    </span>
    <div class="border-main/10 flex-1 border-t"></div>
    <!-- Optional right-side actions -->
    <slot name="action"></slot>
  </div>
</template>
