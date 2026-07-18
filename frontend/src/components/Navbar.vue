<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useSpoiler } from '../composables/useSpoiler'

const { isSpoilerProtected, toggleSpoiler } = useSpoiler()
const route = useRoute()
const isMobileMenuOpen = ref(false)

watch(
  () => route.path,
  () => {
    isMobileMenuOpen.value = false
  },
)
</script>

<template>
  <header class="bg-bg/90 border-main/10 sticky top-0 z-50 border-b backdrop-blur-md">
    <div class="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
      <div class="flex h-full items-center gap-8">
        <router-link
          to="/"
          class="text-main hover:text-primary text-lg font-medium transition-colors"
        >
          臺灣科幻概念資料庫
        </router-link>

        <nav class="hidden h-full gap-6 md:flex">
          <router-link
            to="/concepts"
            :class="[
              'hover:text-primary inline-flex items-center border-b-2 px-1 text-base font-medium transition-colors',
              route.path.startsWith('/concepts')
                ? 'border-primary text-primary'
                : 'text-main/60 border-transparent',
            ]"
          >
            概念
          </router-link>
          <router-link
            to="/works"
            :class="[
              'hover:text-primary inline-flex items-center border-b-2 px-1 text-base font-medium transition-colors',
              route.path.startsWith('/works')
                ? 'border-primary text-primary'
                : 'text-main/60 border-transparent',
            ]"
          >
            作品
          </router-link>
          <router-link
            to="/persons"
            :class="[
              'hover:text-primary inline-flex items-center border-b-2 px-1 text-base font-medium transition-colors',
              route.path.startsWith('/persons')
                ? 'border-primary text-primary'
                : 'text-main/60 border-transparent',
            ]"
          >
            人物
          </router-link>
          <router-link
            to="/pages/about"
            :class="[
              'hover:text-primary inline-flex items-center border-b-2 px-1 text-base font-medium transition-colors',
              route.path.startsWith('/pages/about')
                ? 'border-primary text-primary'
                : 'text-main/60 border-transparent',
            ]"
          >
            關於
          </router-link>
        </nav>
      </div>

      <!-- Desktop Spoiler Button -->
      <div class="hidden items-center gap-5 md:flex">
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

      <!-- Mobile Menu Toggle -->
      <div class="flex items-center md:hidden">
        <button
          class="text-main/60 hover:text-primary p-2 transition-colors"
          aria-label="Toggle mobile menu"
          @click="isMobileMenuOpen = !isMobileMenuOpen"
        >
          <svg
            v-if="!isMobileMenuOpen"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            class="h-6 w-6"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5"
            />
          </svg>
          <svg
            v-else
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            class="h-6 w-6"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>
    </div>

    <!-- Mobile Menu Backdrop -->
    <div
      v-if="isMobileMenuOpen"
      class="fixed inset-0 top-16 -z-10 bg-black/5 md:hidden"
      @click="isMobileMenuOpen = false"
    ></div>

    <!-- Mobile Menu Panel -->
    <div
      v-if="isMobileMenuOpen"
      class="bg-bg border-main/10 absolute inset-x-0 top-16 border-b px-6 py-8 md:hidden"
    >
      <nav class="flex flex-col gap-6">
        <router-link
          to="/concepts"
          :class="[
            'hover:text-primary text-lg font-medium transition-colors',
            route.path.startsWith('/concepts') ? 'text-primary' : 'text-main/70',
          ]"
        >
          概念
        </router-link>
        <router-link
          to="/works"
          :class="[
            'hover:text-primary text-lg font-medium transition-colors',
            route.path.startsWith('/works') ? 'text-primary' : 'text-main/70',
          ]"
        >
          作品
        </router-link>
        <router-link
          to="/persons"
          :class="[
            'hover:text-primary text-lg font-medium transition-colors',
            route.path.startsWith('/persons') ? 'text-primary' : 'text-main/70',
          ]"
        >
          人物
        </router-link>
        <router-link
          to="/pages/about"
          :class="[
            'hover:text-primary text-lg font-medium transition-colors',
            route.path.startsWith('/pages/about') ? 'text-primary' : 'text-main/70',
          ]"
        >
          關於
        </router-link>

        <div class="border-main/10 my-2 border-t"></div>

        <button
          :class="
            isSpoilerProtected
              ? 'border-primary/30 text-primary bg-bg'
              : 'bg-bg text-main/60 border-main/10 hover:border-primary/30 hover:text-primary'
          "
          class="flex w-full items-center justify-center gap-2 border px-4 py-3 text-base font-medium transition-all duration-200"
          @click="toggleSpoiler"
        >
          <span
            class="h-1.5 w-1.5 rounded-full"
            :class="isSpoilerProtected ? 'bg-primary' : 'bg-main/30'"
          ></span>
          防劇透
        </button>
      </nav>
    </div>
  </header>
</template>
