<script setup lang="ts">
import { ref } from 'vue'

// Control spoiler protection mode
const isSpoilerProtected = ref(false)
const toggleSpoiler = () => {
  isSpoilerProtected.value = !isSpoilerProtected.value
}
</script>

<template>
  <header class="sticky top-0 z-50 bg-[#ffffff]/90 backdrop-blur-md border-b border-[#2d2016]/10 shadow-sm">
    <div class="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">

      <!-- Left: Site Name & Navigation Links -->
      <div class="flex items-center gap-8 h-full">
        <router-link to="/" class="text-lg font-bold text-[#2d2016] hover:text-[#ae5630] transition-colors">
          臺灣科幻概念資料庫
        </router-link>

        <nav class="hidden md:flex h-full gap-6">
          <router-link to="/concepts" class="inline-flex items-center px-1 border-b-2 font-medium text-base transition-colors border-transparent text-[#2d2016]/60 hover:text-[#2d2016]" active-class="!border-[#ae5630] !text-[#ae5630]">概念</router-link>
          <router-link to="/works" class="inline-flex items-center px-1 border-b-2 font-medium text-base transition-colors border-transparent text-[#2d2016]/60 hover:text-[#2d2016]" active-class="!border-[#ae5630] !text-[#ae5630]">作品</router-link>
          <router-link to="/persons" class="inline-flex items-center px-1 border-b-2 font-medium text-base transition-colors border-transparent text-[#2d2016]/60 hover:text-[#2d2016]" active-class="!border-[#ae5630] !text-[#ae5630]">人物</router-link>
          <router-link to="/about" class="inline-flex items-center px-1 border-b-2 font-medium text-base transition-colors border-transparent text-[#2d2016]/60 hover:text-[#2d2016]" active-class="!border-[#ae5630] !text-[#ae5630]">關於</router-link>
        </nav>
      </div>

      <!-- Right: Spoiler Toggle & Login -->
      <div class="flex items-center gap-5">
        <button
          @click="toggleSpoiler"
          :class="isSpoilerProtected ? 'bg-[#ae5630]/10 text-[#ae5630] border-[#ae5630]/30' : 'bg-[#ffffff] text-[#2d2016]/60 border-[#2d2016]/10 hover:bg-[#2d2016]/5 hover:text-[#2d2016]'"
          class="flex items-center gap-2 px-3 py-1.5 rounded-full border text-sm font-medium transition-all duration-200"
        >
          <span class="w-1.5 h-1.5 rounded-full" :class="isSpoilerProtected ? 'bg-[#ae5630]' : 'bg-[#2d2016]/30'"></span>
          防劇透
        </button>

        <button class="text-base font-medium text-[#2d2016]/60 hover:text-[#2d2016] transition-colors">
          登入
        </button>
      </div>
    </div>
  </header>
</template>
