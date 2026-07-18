<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import Navbar from './components/Navbar.vue'
import Icon from './components/Icon.vue'
import api from './api/axios'

// Control banner visibility
const showBanner = ref(false)
const globalAnnouncement = ref('')

// Global settings
const siteSettings = ref<Record<string, string>>({})

// Scroll-to-top logic
const showScrollTop = ref(false)

const handleScroll = () => {
  showScrollTop.value = window.scrollY > 400
}

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

onMounted(async () => {
  window.addEventListener('scroll', handleScroll, { passive: true })

  // Fetch banner
  try {
    const response = await api.get('/posts/active-pinned/')
    if (response.status === 200 && response.data) {
      globalAnnouncement.value = response.data.title
      showBanner.value = true
    }
  } catch (error) {
    console.error('Failed to fetch active pinned post:', error)
  }

  try {
    const response = await api.get('/settings/')
    if (response.status === 200 && response.data?.results) {
      const settingsMap: Record<string, string> = {}
      response.data.results.forEach((s: { key: string; value: string }) => {
        settingsMap[s.key] = s.value
      })
      siteSettings.value = settingsMap
    }
  } catch (error) {
    console.error('Failed to fetch site settings:', error)
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
        aria-label="Close announcement"
        @click="showBanner = false"
      >
        <Icon
          name="close"
          class="h-5 w-5"
          :stroke-width="2"
        />
      </button>
    </div>

    <!-- Injected Global Navbar Component -->
    <Navbar />

    <main class="flex-grow px-5 py-4 md:px-8 md:py-8">
      <router-view v-slot="{ Component }">
        <transition
          name="fade"
          mode="out-in"
        >
          <component
            :is="Component"
            :key="$route.path"
          />
        </transition>
      </router-view>
    </main>

    <!-- Scroll-to-top Button: sticky, so it rests above the footer instead of covering it -->
    <button
      v-show="showScrollTop"
      aria-label="回到頂部"
      class="bg-main/10 text-main/50 hover:bg-primary hover:text-bg sticky bottom-8 z-40 mr-8 mb-4 flex h-10 w-10 items-center justify-center self-end rounded-full shadow-sm transition-all duration-200"
      @click="scrollToTop"
    >
      <Icon
        name="chevron-up"
        class="h-5 w-5"
        :stroke-width="2"
      />
    </button>

    <!-- Footer -->
    <footer class="border-main/10 mt-auto border-t py-8">
      <div
        class="text-main/60 mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 text-sm sm:flex-row"
      >
        <!-- Left: Creative Commons Declaration -->
        <div>
          本站內容採用
          <a
            href="https://creativecommons.org/licenses/by/4.0/deed.zh-Hant"
            target="_blank"
            rel="noopener noreferrer"
            class="text-primary hover:text-primary/80 decoration-primary/30 font-medium underline underline-offset-4 transition-colors"
          >
            CC BY 4.0 授權條款
          </a>
        </div>

        <!-- Right: Page Links -->
        <div class="flex gap-6">
          <a
            v-if="siteSettings['submit_data_url']"
            :href="siteSettings['submit_data_url']"
            target="_blank"
            rel="noopener noreferrer"
            class="hover:text-main transition-colors"
          >
            貢獻資料
          </a>
          <a
            v-if="siteSettings['feedback_url']"
            :href="siteSettings['feedback_url']"
            target="_blank"
            rel="noopener noreferrer"
            class="hover:text-main transition-colors"
          >
            問題回報
          </a>
          <router-link
            to="/pages/about"
            class="hover:text-main transition-colors"
          >
            關於我們
          </router-link>
          <router-link
            to="/pages/privacy"
            class="hover:text-main transition-colors"
          >
            隱私政策
          </router-link>
        </div>
      </div>
    </footer>
  </div>
</template>
