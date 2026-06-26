<script setup lang="ts">
/**
 * ListState — Renders the shared loading / error / empty placeholders for any
 * list or detail view, falling back to the default slot (the real content) once
 * data is ready.
 *
 *   <ListState :loading="isLoading" :error="hasError" :empty="items.length === 0">
 *     <!-- results -->
 *   </ListState>
 *
 * Detail views pass only :loading/:error and keep their content in a sibling
 * guarded by v-if, since there is no "empty" state (a 404 redirects instead).
 */
import Icon from './Icon.vue'

withDefaults(
  defineProps<{
    loading?: boolean
    error?: boolean
    empty?: boolean
    loadingText?: string
    errorText?: string
    emptyText?: string
    size?: 'sm' | 'base'
  }>(),
  {
    loading: false,
    error: false,
    empty: false,
    loadingText: '正在讀取資料...',
    errorText: '資料讀取發生問題，請稍後再試。',
    emptyText: '找不到符合條件的資料。',
    size: 'base',
  },
)
</script>

<template>
  <div
    v-if="loading"
    class="text-main/50 animate-pulse py-16 text-center font-medium"
    :class="size === 'sm' ? 'text-sm' : 'text-base'"
  >
    {{ loadingText }}
  </div>
  <div
    v-else-if="error"
    class="text-main/50 py-16 text-center font-medium"
    :class="size === 'sm' ? 'text-sm' : 'text-base'"
  >
    {{ errorText }}
  </div>
  <div
    v-else-if="empty"
    class="flex flex-col items-center gap-2 py-16 text-center"
  >
    <Icon
      name="box"
      :stroke-width="1.2"
      class="text-main/15 h-10 w-10"
    />
    <span class="text-main/35 text-sm">{{ emptyText }}</span>
  </div>
  <slot v-else />
</template>
