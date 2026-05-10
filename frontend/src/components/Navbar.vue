<script setup lang="ts">
import { useSpoiler } from '../composables/useSpoiler'

const { isSpoilerProtected, toggleSpoiler } = useSpoiler()
</script>

<template>
  <header class="sticky top-0 z-50 bg-bg/90 backdrop-blur-md border-b border-main/10 shadow-sm">
    <div class="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">

      <div class="flex items-center gap-8 h-full">
        <router-link to="/" class="text-lg font-bold text-main hover:text-primary transition-colors">
          臺灣科幻概念資料庫
        </router-link>

        <nav class="hidden md:flex h-full gap-6">
          <router-link to="/concepts" class="inline-flex items-center px-1 border-b-2 font-medium text-base transition-colors border-transparent text-main/60 hover:text-main" active-class="!border-primary !text-primary">概念</router-link>
          <router-link to="/works" class="inline-flex items-center px-1 border-b-2 font-medium text-base transition-colors border-transparent text-main/60 hover:text-main" active-class="!border-primary !text-primary">作品</router-link>
          <router-link to="/persons" class="inline-flex items-center px-1 border-b-2 font-medium text-base transition-colors border-transparent text-main/60 hover:text-main" active-class="!border-primary !text-primary">人物</router-link>
          <router-link to="/pages/about" class="inline-flex items-center px-1 border-b-2 font-medium text-base transition-colors border-transparent text-main/60 hover:text-main" active-class="!border-primary !text-primary">關於</router-link>
        </nav>
      </div>

      <div class="flex items-center gap-5">
        <button
          @click="toggleSpoiler"
          :class="isSpoilerProtected ? 'bg-primary/10 text-primary border-primary/30' : 'bg-bg text-main/60 border-main/10 hover:bg-main/5 hover:text-main'"
          class="flex items-center gap-2 px-3 py-1.5 rounded-full border text-sm font-medium transition-all duration-200"
        >
          <span class="w-1.5 h-1.5 rounded-full" :class="isSpoilerProtected ? 'bg-primary' : 'bg-main/30'"></span>
          防劇透
        </button>

        <button class="text-base font-medium text-main/60 hover:text-main transition-colors">
          登入
        </button>
      </div>
    </div>
  </header>
</template>
