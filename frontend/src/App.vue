<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AppLayout from '@/components/layout/AppLayout.vue'

const authStore = useAuthStore()

// 應用初始化
onMounted(async () => {
  // 嘗試從 localStorage 恢復認證狀態
  await authStore.initializeAuth()
})
</script>

<template>
  <AppLayout />
</template>
