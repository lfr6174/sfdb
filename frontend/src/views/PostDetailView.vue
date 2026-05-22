<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/axios'
import { formatDate } from '../utils/formatters'
import BackLink from '../components/BackLink.vue'
import { useDocumentTitle } from '../composables/useDocumentTitle'

const route = useRoute()
const post = ref<any>(null)
useDocumentTitle(() => post.value?.title)
const isLoading = ref(true)

const fetchPostDetail = async () => {
  isLoading.value = true
  try {
    const response = await api.get(`/posts/${route.params.id}/`)
    post.value = response.data
  } catch (error) {
    console.error('Failed to fetch post details:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchPostDetail()
})
</script>

<template>
  <div class="mx-auto max-w-4xl pb-20">
    <div
      v-if="isLoading"
      class="text-main/50 py-16 text-center text-sm font-medium"
    >
      正在讀取文章資料...
    </div>

    <template v-else-if="post">
      <!-- Back Link -->
      <div class="mb-9 pt-6 md:pt-10">
        <BackLink
          to="/posts"
          text="返回文章列表"
        />
      </div>

      <article class="flex flex-col">
        <h1 class="text-main mb-6 text-2xl font-medium md:text-3xl">
          {{ post.title }}
        </h1>

        <div class="text-main/50 mb-8 flex items-center gap-2 text-base">
          <span>{{ post.author_name || '管理員' }}</span>
          <span class="text-main/20">·</span>
          <time>{{ formatDate(post.created_at) }}</time>
        </div>

        <!-- content -->
        <div class="text-main/80 max-w-none text-base leading-loose whitespace-pre-wrap lg:text-lg">
          {{ post.body || '無內容' }}
        </div>

        <div class="border-main/10 mt-16 flex justify-end border-t pt-6">
          <span class="text-main/40 text-xs">最後更新於 {{ formatDate(post.updated_at) }}</span>
        </div>
      </article>
    </template>
  </div>
</template>
