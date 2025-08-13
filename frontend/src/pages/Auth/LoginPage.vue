<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <div class="mx-auto h-12 w-12 bg-chord-primary rounded-lg flex items-center justify-center">
          <span class="text-white font-bold text-xl">M</span>
        </div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          登入您的帳戶
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          還沒有帳戶？
          <RouterLink to="/auth/register" class="font-medium text-chord-primary hover:text-blue-500">
            立即註冊
          </RouterLink>
        </p>
      </div>
      
      <form class="mt-8 space-y-6" @submit.prevent="handleSubmit">
        <div class="space-y-4">
          <BaseInput
            v-model="form.email"
            type="email"
            label="電子郵件"
            placeholder="請輸入您的電子郵件"
            required
            :error-message="errors.email"
          />
          
          <BaseInput
            v-model="form.password"
            type="password"
            label="密碼"
            placeholder="請輸入您的密碼"
            required
            :error-message="errors.password"
          />
        </div>

        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <input
              id="remember-me"
              v-model="form.remember_me"
              name="remember-me"
              type="checkbox"
              class="h-4 w-4 text-chord-primary focus:ring-chord-primary border-gray-300 rounded"
            />
            <label for="remember-me" class="ml-2 block text-sm text-gray-900">
              記住我
            </label>
          </div>

          <div class="text-sm">
            <RouterLink to="/auth/forgot-password" class="font-medium text-chord-primary hover:text-blue-500">
              忘記密碼？
            </RouterLink>
          </div>
        </div>

        <div>
          <BaseButton
            type="submit"
            variant="primary"
            size="lg"
            :loading="isLoading"
            :disabled="!isFormValid"
            block
          >
            登入
          </BaseButton>
        </div>

        <div v-if="error" class="text-center text-sm text-red-600">
          {{ error }}
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const form = ref({
  email: '',
  password: '',
  remember_me: false
})

const errors = ref({
  email: '',
  password: ''
})

const isLoading = ref(false)
const error = ref('')

const isFormValid = computed(() => {
  return form.value.email && form.value.password
})

const handleSubmit = async () => {
  try {
    isLoading.value = true
    error.value = ''
    errors.value = { email: '', password: '' }

    await authStore.login(form.value)

    // 登入成功後重導向
    const redirectPath = route.query.redirect as string || '/'
    router.push(redirectPath)
  } catch (err: any) {
    error.value = err.message || '登入失敗'
  } finally {
    isLoading.value = false
  }
}
</script>