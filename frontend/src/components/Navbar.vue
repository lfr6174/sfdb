<script setup lang="ts">
import { useSpoiler } from '../composables/useSpoiler'

const { isSpoilerProtected, toggleSpoiler } = useSpoiler()
</script>

<template>
  <header class="bg-bg/90 border-main/10 sticky top-0 z-50 border-b backdrop-blur-md">
    <div class="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
      <div class="flex h-full items-center gap-8">
        <router-link
          to="/"
          class="text-main hover:text-primary text-lg font-bold transition-colors"
        >
          臺灣科幻概念資料庫
        </router-link>

        <nav class="hidden h-full gap-6 md:flex">
          <router-link
            to="/concepts"
            class="text-main/60 hover:text-primary inline-flex items-center border-b-2 border-transparent px-1 text-base font-medium transition-colors"
            active-class="!border-primary !text-primary"
          >
            概念
          </router-link>
          <router-link
            to="/works"
            class="text-main/60 hover:text-primary inline-flex items-center border-b-2 border-transparent px-1 text-base font-medium transition-colors"
            active-class="!border-primary !text-primary"
          >
            作品
          </router-link>
          <router-link
            to="/persons"
            class="text-main/60 hover:text-primary inline-flex items-center border-b-2 border-transparent px-1 text-base font-medium transition-colors"
            active-class="!border-primary !text-primary"
          >
            人物
          </router-link>
          <router-link
            to="/pages/about"
            class="text-main/60 hover:text-primary inline-flex items-center border-b-2 border-transparent px-1 text-base font-medium transition-colors"
            active-class="!border-primary !text-primary"
          >
            關於
          </router-link>
        </nav>
      </div>

      <div class="flex items-center gap-5">
        <button
          :class="
            isSpoilerProtected
              ? 'border-primary/30 text-primary bg-bg'
              : 'bg-bg text-main/60 border-main/10 hover:border-primary/30 hover:text-primary'
          "
          class="flex items-center gap-2 border px-3 py-1.5 text-sm font-medium transition-all duration-200"
          @click="toggleSpoiler"
        >
          <span
            class="h-1.5 w-1.5 rounded-full"
            :class="isSpoilerProtected ? 'bg-primary' : 'bg-main/30'"
          ></span>
          防劇透
        </button>
      </div>
    </div>
  </header>
</template>
