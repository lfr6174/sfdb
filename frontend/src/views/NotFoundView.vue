<script setup lang="ts">
import { useDocumentMeta } from '../composables/useDocumentTitle'

useDocumentMeta('404 找不到頁面', '')
</script>

<template>
  <div
    class="mx-auto flex max-w-4xl flex-col items-center justify-center py-20 text-center md:py-32"
  >
    <!-- Large subtle 404 watermark -->
    <div
      class="text-main/10 absolute -z-10 text-[10rem] leading-none font-bold tracking-tighter select-none md:text-[16rem]"
    >
      404
    </div>

    <h1 class="text-main mt-8 mb-4 text-2xl font-medium md:text-3xl">找不到頁面</h1>
    <p class="text-main/60 mb-10 max-w-md px-6 text-base leading-relaxed">
      您尋找的頁面可能已被移除，或者網址有誤。
    </p>

    <div class="flex items-center gap-6">
      <router-link
        to="/"
        class="text-main hover:text-primary border-main/20 hover:border-primary/50 border-b pb-0.5 text-base transition-colors"
      >
        返回首頁
      </router-link>
      <router-link
        to="/concepts"
        class="text-main hover:text-primary border-main/20 hover:border-primary/50 border-b pb-0.5 text-base transition-colors"
      >
        前往概念探索
      </router-link>
    </div>
  </div>
</template>
