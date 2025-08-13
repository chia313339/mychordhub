<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 頂部導航 -->
    <AppHeader />

    <!-- 主要內容區域 -->
    <main class="container mx-auto px-4 py-6">
      <RouterView />
    </main>

    <!-- 頁腳 -->
    <AppFooter />

    <!-- 全局通知 -->
    <NotificationContainer />

    <!-- 全局加載指示器 -->
    <LoadingOverlay v-if="isGlobalLoading" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppHeader from './AppHeader.vue'
import AppFooter from './AppFooter.vue'
import NotificationContainer from '@/components/ui/NotificationContainer.vue'
import LoadingOverlay from '@/components/ui/LoadingOverlay.vue'

const authStore = useAuthStore()

const isGlobalLoading = computed(() => {
  // 可以根據需要添加其他全局加載狀態
  return authStore.isLoading
})
</script>
