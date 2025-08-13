<template>
  <div class="space-y-1">
    <label v-if="label" :for="inputId" class="block text-sm font-medium text-gray-700">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>

    <div class="relative">
      <!-- 前綴圖標 -->
      <div
        v-if="prefixIcon"
        class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"
      >
        <component :is="prefixIcon" class="h-5 w-5 text-gray-400" />
      </div>

      <!-- 輸入框 -->
      <input
        :id="inputId"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :autocomplete="autocomplete"
        :class="inputClasses"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
        @keydown="handleKeydown"
      />

      <!-- 後綴圖標 -->
      <div
        v-if="suffixIcon"
        class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none"
      >
        <component :is="suffixIcon" class="h-5 w-5 text-gray-400" />
      </div>

      <!-- 密碼顯示/隱藏按鈕 -->
      <button
        v-if="type === 'password' && showPasswordToggle"
        type="button"
        class="absolute inset-y-0 right-0 pr-3 flex items-center"
        @click="togglePasswordVisibility"
      >
        <EyeIcon v-if="isPasswordVisible" class="h-5 w-5 text-gray-400" />
        <EyeOffIcon v-else class="h-5 w-5 text-gray-400" />
      </button>
    </div>

    <!-- 幫助文字 -->
    <p v-if="helpText && !errorMessage" class="text-sm text-gray-500">
      {{ helpText }}
    </p>

    <!-- 錯誤訊息 -->
    <p v-if="errorMessage" class="text-sm text-red-600">
      {{ errorMessage }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, useId } from 'vue'
import { EyeIcon, EyeOffIcon } from 'lucide-vue-next'

interface Props {
  modelValue?: string | number
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search'
  label?: string
  placeholder?: string
  helpText?: string
  errorMessage?: string
  disabled?: boolean
  readonly?: boolean
  required?: boolean
  autocomplete?: string
  size?: 'sm' | 'md' | 'lg'
  prefixIcon?: any
  suffixIcon?: any
  showPasswordToggle?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  size: 'md',
  showPasswordToggle: true,
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
  blur: [event: FocusEvent]
  focus: [event: FocusEvent]
  keydown: [event: KeyboardEvent]
}>()

const inputId = useId()
const isPasswordVisible = ref(false)

const actualType = computed(() => {
  if (props.type === 'password' && isPasswordVisible.value) {
    return 'text'
  }
  return props.type
})

const inputClasses = computed(() => {
  const baseClasses = [
    'block w-full rounded-lg border border-gray-300 transition-colors',
    'focus:ring-2 focus:ring-chord-primary focus:border-transparent',
    'disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed',
    'placeholder-gray-400',
  ]

  // 尺寸樣式
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-3 py-2 text-base',
    lg: 'px-4 py-3 text-lg',
  }

  // 圖標間距
  const iconPadding = []
  if (props.prefixIcon) {
    iconPadding.push('pl-10')
  }
  if (props.suffixIcon || (props.type === 'password' && props.showPasswordToggle)) {
    iconPadding.push('pr-10')
  }

  // 錯誤狀態
  const errorClasses = props.errorMessage
    ? 'border-red-300 focus:ring-red-500 focus:border-red-500'
    : ''

  return [...baseClasses, sizeClasses[props.size], ...iconPadding, errorClasses].join(' ')
})

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  let value: string | number = target.value

  if (props.type === 'number') {
    value = parseFloat(value) || 0
  }

  emit('update:modelValue', value)
}

const handleBlur = (event: FocusEvent) => {
  emit('blur', event)
}

const handleFocus = (event: FocusEvent) => {
  emit('focus', event)
}

const handleKeydown = (event: KeyboardEvent) => {
  emit('keydown', event)
}

const togglePasswordVisibility = () => {
  isPasswordVisible.value = !isPasswordVisible.value
}
</script>
