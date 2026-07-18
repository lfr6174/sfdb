<script setup lang="ts">
/**
 * WorkListItem — one row in the works list: title, byline/meta on the left,
 * concept tags on the right. Pure presentation, everything comes from `work`.
 */
import type { Work } from '../types'
import HoverListItem from './HoverListItem.vue'
import AgentInline from './AgentInline.vue'
import ConceptTag from './ConceptTag.vue'

defineProps<{ work: Work }>()
</script>

<template>
  <HoverListItem
    tag="div"
    class="flex flex-col justify-between gap-3 py-4 md:flex-row md:items-start"
  >
    <!-- Left: title + meta -->
    <div class="min-w-0 flex-1">
      <router-link
        :to="`/works/${work.id}`"
        class="text-main/80 group-hover:text-primary mb-1.5 block text-base font-medium no-underline transition-colors"
      >
        {{ work.title }}
      </router-link>

      <div class="text-main/50 flex flex-wrap items-center gap-x-1.5 gap-y-0.5 text-sm">
        <span
          v-if="work.byline && work.byline.length"
          class="flex flex-wrap items-center gap-x-0.5"
        >
          <AgentInline :agents="work.byline" />
        </span>
        <span v-else>佚名</span>

        <span class="text-main/20">·</span>
        <span>{{ work.year || '未知' }}</span>
        <template v-if="[work.work_length_display, work.genre_display].filter(Boolean).length">
          <span class="text-main/20">·</span>
          <span>
            {{ [work.work_length_display, work.genre_display].filter(Boolean).join('') }}
          </span>
        </template>
      </div>
    </div>

    <!-- Right: concept tags -->
    <div
      v-if="work.work_concepts && work.work_concepts.length"
      class="flex flex-wrap gap-1.5 md:max-w-[45%] md:justify-end"
    >
      <ConceptTag
        v-for="wc in work.work_concepts"
        :key="wc.concept.slug"
        :concept="wc.concept"
      />
    </div>
  </HoverListItem>
</template>
