<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Navbar from './components/Navbar.vue'
import api from './api/axios'

// Control banner visibility
const showBanner = ref(false)
const globalAnnouncement = ref('')

onMounted(async () => {
  try {
    const response = await api.get('/posts/active-pinned/')
    if (response.status === 200 && response.data) {
      globalAnnouncement.value = response.data.title
      showBanner.value = true
    }
  } catch (error) {
    console.error('Failed to fetch active pinned post:', error)
  }
})
</script>

<template>
  <!-- Editorial theme: Deep beige outer bg, warm black text -->
  <div class="bg-bg text-main flex min-h-screen flex-col font-sans">
    <!-- Global Announcement Banner -->
    <div
      v-if="showBanner && globalAnnouncement"
      class="border-primary/20 bg-primary/10 relative flex items-center justify-center border-b px-4 py-2.5"
    >
      <span class="text-primary text-xs font-medium">
        {{ globalAnnouncement }}
      </span>
      <button
        class="text-primary/70 hover:text-primary absolute right-4 transition-colors"
        aria-label="關閉公告"
        @click="showBanner = false"
      >
        <!-- Close Icon (X) -->
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            fill-rule="evenodd"
            d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
            clip-rule="evenodd"
          />
        </svg>
      </button>
    </div>

    <!-- Injected Global Navbar Component -->
    <Navbar />

    <!-- Main Content Area: dynamically rendered by Vue Router -->
    <main class="flex-grow p-4 md:py-8">
      <router-view></router-view>
    </main>
  </div>
</template>
