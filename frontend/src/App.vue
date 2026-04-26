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
  <div class="min-h-screen bg-[#F8F8F6] font-sans text-[#2d2016] flex flex-col">

    <!-- Global Announcement Banner -->
    <div v-if="showBanner && globalAnnouncement" class="bg-[#ae5630]/10 border-b border-[#ae5630]/20 px-4 py-2.5 relative flex justify-center items-center">
      <span class="text-[13px] font-medium text-[#ae5630]">
        {{ globalAnnouncement }}
      </span>
      <button @click="showBanner = false" class="absolute right-4 text-[#ae5630] hover:text-[#ae5630]/70 transition-colors">
        <!-- Close Icon (X) -->
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
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
