<script setup lang="ts">
/**
 * AgentInline — A 、-separated inline run of byline/credit agents. Persons
 * link to their detail page; organizations render as plain text.
 *
 * Pass :linked="false" where links must not render — e.g. inside a
 * HoverListItem that is itself an <a> (nested links are invalid HTML).
 */
import type { BylineEntry } from '../types'

withDefaults(
  defineProps<{
    agents: BylineEntry[]
    linked?: boolean
  }>(),
  { linked: true },
)
</script>

<template>
  <template
    v-for="(agent, idx) in agents"
    :key="idx"
  >
    <router-link
      v-if="linked && agent.id && agent.agent_type === 'person'"
      :to="`/persons/${agent.id}`"
      class="hover:text-primary no-underline transition-colors"
    >
      {{ agent.text }}
    </router-link>
    <span v-else>{{ agent.text }}</span>
    <span v-if="idx < agents.length - 1">、</span>
  </template>
</template>
