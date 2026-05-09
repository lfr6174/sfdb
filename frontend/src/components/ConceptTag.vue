<script setup lang="ts">
withDefaults(defineProps<{
  concept: {
    name: string;
    slug: string;
    works_count?: number;
  };
  size?: 'sm' | 'md';
}>(), {
  size: 'sm' // 預設為小尺寸，符合大多數的 sidebar 或 inline list 需求
})
</script>

<template>
  <router-link
    :to="`/concepts/${concept.slug}`"
    :class="[
      'inline-flex items-center border border-main/15 hover:text-primary hover:bg-primary/5 hover:border-primary/30 transition-all whitespace-nowrap no-underline',
      size === 'md' ? 'gap-2 text-sm text-main/60 px-3 py-1.5' : 'gap-1.5 text-xs text-main/60 px-2.5 py-1'
    ]"
  >
    <span>{{ concept.name }}</span>
    <span v-if="concept.works_count !== undefined" class="font-mono text-[10px] text-main/40">{{ concept.works_count }}</span>
  </router-link>
</template>
