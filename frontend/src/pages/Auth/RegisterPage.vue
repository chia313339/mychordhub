<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <div class="mx-auto h-12 w-12 bg-chord-primary rounded-lg flex items-center justify-center">
          <span class="text-white font-bold text-xl">M</span>
        </div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          建立新帳戶
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          已有帳戶？
          <RouterLink to="/auth/login" class="font-medium text-chord-primary hover:text-blue-500">
            立即登入
          </RouterLink>
        </p>
      </div>
      
      <form class="mt-8 space-y-6" @submit.prevent="handleSubmit">
        <div class="space-y-4">
          <BaseInput
            v-model="form.display_name"
            type="text"
            label="顯示名稱"
            placeholder="請輸入您的顯示名稱"
            required
            :error-message="errors.display_name"
          />
          
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
            placeholder="請輸入密碼（至少8位）"
            required
            :error-message="errors.password"
            help-text="密碼需至少8個字符，包含大小寫字母和數字"
          />
          
          <BaseInput
            v-model="form.confirm_password"
            type="password"
            label="確認密碼"
            placeholder="請再次輸入密碼"
            required
            :error-message="errors.confirm_password"
          />
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
            註冊
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
import { ref, computed, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  email: '',
  password: '',
  confirm_password: '',
  display_name: ''
})

const errors = ref({
  email: '',
  password: '',
  confirm_password: '',
  display_name: ''
})

const isLoading = ref(false)
const error = ref('')

const isFormValid = computed(() => {
  return form.value.email && 
         form.value.password && 
         form.value.confirm_password && 
         form.value.display_name &&
         form.value.password === form.value.confirm_password
})

// 密碼確認驗證
watch(() => form.value.confirm_password, (newValue) => {
  if (newValue && form.value.password && newValue !== form.value.password) {
    errors.value.confirm_password = '密碼不一致'
  } else {
    errors.value.confirm_password = ''
  }
})

const handleSubmit = async () => {
  try {
    isLoading.value = true
    error.value = ''
    errors.value = { email: '', password: '', confirm_password: '', display_name: '' }

    await authStore.register(form.value)

    // 註冊成功後重導向
    router.push('/')
  } catch (err: any) {
    error.value = err.message || '註冊失敗'
  } finally {
    isLoading.value = false
  }
}
</script>