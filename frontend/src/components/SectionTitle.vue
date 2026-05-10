<script setup lang="ts">
// Fallthrough attributes (e.g., class="mb-5") automatically bind to the root div
</script>

<template>
  <div class="flex items-center gap-3">
    <span class="text-sm font-medium tracking-widest uppercase text-main/40 whitespace-nowrap">
      <slot></slot>
    </span>
    <div class="flex-1 border-t border-main/10"></div>
    <!-- Optional right-side actions -->
    <slot name="action"></slot>
  </div>
</template>
