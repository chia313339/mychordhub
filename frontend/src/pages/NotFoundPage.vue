<template>
  <div class="min-h-[60vh] flex items-center justify-center">
    <div class="text-center">
      <h1 class="text-6xl font-bold text-gray-300 mb-4">404</h1>
      <h2 class="text-2xl font-semibold text-gray-700 mb-4">頁面不存在</h2>
      <p class="text-gray-500 mb-8">抱歉，您訪問的頁面無法找到。</p>
      <RouterLink to="/">
        <BaseButton variant="primary">
          返回首頁
        </BaseButton>
      </RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import BaseButton from '@/components/ui/BaseButton.vue'
</script>