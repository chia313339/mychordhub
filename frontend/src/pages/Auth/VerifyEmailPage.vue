<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="max-w-md w-full">
      <h2 class="text-3xl font-extrabold text-gray-900 text-center mb-8">驗證郵箱</h2>
      <p class="text-center text-gray-600 mb-8">功能開發中...</p>
      <div class="text-center">
        <RouterLink to="/">
          <BaseButton variant="primary">返回首頁</BaseButton>
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import BaseButton from '@/components/ui/BaseButton.vue'
</script>