<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div class="text-center">
        <h2 class="text-3xl font-extrabold text-gray-900">忘記密碼</h2>
        <p class="mt-2 text-sm text-gray-600">我們會發送重設密碼的連結到您的電子郵件</p>
      </div>
      
      <form class="mt-8 space-y-6" @submit.prevent="handleSubmit">
        <BaseInput
          v-model="email"
          type="email"
          label="電子郵件"
          placeholder="請輸入您的電子郵件"
          required
        />

        <BaseButton
          type="submit"
          variant="primary"
          size="lg"
          :loading="isLoading"
          block
        >
          發送重設連結
        </BaseButton>

        <div class="text-center">
          <RouterLink to="/auth/login" class="text-sm text-chord-primary hover:text-blue-500">
            返回登入
          </RouterLink>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'

const email = ref('')
const isLoading = ref(false)

const handleSubmit = async () => {
  isLoading.value = true
  // TODO: 實現忘記密碼邏輯
  setTimeout(() => {
    isLoading.value = false
    alert('重設密碼連結已發送到您的電子郵件')
  }, 1000)
}
</script>