<template>
  <header class="bg-white shadow-sm border-b border-gray-200">
    <div class="container mx-auto px-4">
      <div class="flex items-center justify-between h-16">
        <!-- Logo 和品牌 -->
        <div class="flex items-center">
          <RouterLink to="/" class="flex items-center space-x-2">
            <div class="w-8 h-8 bg-chord-primary rounded-lg flex items-center justify-center">
              <span class="text-white font-bold text-lg">M</span>
            </div>
            <span class="text-xl font-bold text-gray-900">MyChordHub</span>
          </RouterLink>
        </div>

        <!-- 桌面導航選單 -->
        <nav class="hidden md:flex items-center space-x-8">
          <RouterLink
            to="/browse"
            class="text-gray-600 hover:text-chord-primary transition-colors"
            active-class="text-chord-primary font-medium"
          >
            瀏覽歌曲
          </RouterLink>

          <RouterLink
            v-if="authStore.isAuthenticated"
            to="/edit"
            class="text-gray-600 hover:text-chord-primary transition-colors"
            active-class="text-chord-primary font-medium"
          >
            創作歌曲
          </RouterLink>
        </nav>

        <!-- 用戶操作區域 -->
        <div class="flex items-center space-x-4">
          <!-- 搜索按鈕（手機版） -->
          <button
            class="md:hidden p-2 text-gray-600 hover:text-chord-primary"
            @click="toggleMobileSearch"
          >
            <SearchIcon class="w-5 h-5" />
          </button>

          <!-- 已登入用戶選單 -->
          <div v-if="authStore.isAuthenticated" class="relative">
            <button
              @click="toggleUserMenu"
              class="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <img
                v-if="authStore.user?.avatar_url"
                :src="authStore.user.avatar_url"
                :alt="authStore.user.display_name"
                class="w-8 h-8 rounded-full object-cover"
              />
              <div
                v-else
                class="w-8 h-8 bg-chord-secondary rounded-full flex items-center justify-center"
              >
                <span class="text-white text-sm font-medium">
                  {{ getInitials(authStore.user?.display_name) }}
                </span>
              </div>
              <ChevronDownIcon class="w-4 h-4 text-gray-500" />
            </button>

            <!-- 用戶下拉選單 -->
            <Transition
              enter-active-class="transition duration-200 ease-out"
              enter-from-class="transform scale-95 opacity-0"
              enter-to-class="transform scale-100 opacity-100"
              leave-active-class="transition duration-75 ease-in"
              leave-from-class="transform scale-100 opacity-100"
              leave-to-class="transform scale-95 opacity-0"
            >
              <div
                v-if="showUserMenu"
                class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50"
                @click.away="showUserMenu = false"
              >
                <RouterLink
                  to="/profile"
                  class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  @click="showUserMenu = false"
                >
                  個人資料
                </RouterLink>
                <RouterLink
                  to="/profile/songs"
                  class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  @click="showUserMenu = false"
                >
                  我的歌曲
                </RouterLink>
                <RouterLink
                  to="/profile/collections"
                  class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  @click="showUserMenu = false"
                >
                  我的收藏
                </RouterLink>
                <hr class="my-1 border-gray-200" />
                <button
                  @click="handleLogout"
                  class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  登出
                </button>
              </div>
            </Transition>
          </div>

          <!-- 未登入用戶按鈕 -->
          <div v-else class="flex items-center space-x-2">
            <RouterLink to="/auth/login">
              <BaseButton variant="ghost" size="sm"> 登入 </BaseButton>
            </RouterLink>
            <RouterLink to="/auth/register">
              <BaseButton variant="primary" size="sm"> 註冊 </BaseButton>
            </RouterLink>
          </div>

          <!-- 手機選單按鈕 -->
          <button
            class="md:hidden p-2 text-gray-600 hover:text-chord-primary"
            @click="toggleMobileMenu"
          >
            <MenuIcon v-if="!showMobileMenu" class="w-6 h-6" />
            <XIcon v-else class="w-6 h-6" />
          </button>
        </div>
      </div>

      <!-- 手機搜索欄 -->
      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="transform -translate-y-2 opacity-0"
        enter-to-class="transform translate-y-0 opacity-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="transform translate-y-0 opacity-100"
        leave-to-class="transform -translate-y-2 opacity-0"
      >
        <div v-if="showMobileSearch" class="md:hidden py-4 border-t border-gray-200">
          <SearchBar />
        </div>
      </Transition>

      <!-- 手機導航選單 -->
      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="transform -translate-y-2 opacity-0"
        enter-to-class="transform translate-y-0 opacity-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="transform translate-y-0 opacity-100"
        leave-to-class="transform -translate-y-2 opacity-0"
      >
        <nav v-if="showMobileMenu" class="md:hidden py-4 border-t border-gray-200">
          <div class="space-y-2">
            <RouterLink
              to="/browse"
              class="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              @click="showMobileMenu = false"
            >
              瀏覽歌曲
            </RouterLink>
            <RouterLink
              v-if="authStore.isAuthenticated"
              to="/edit"
              class="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
              @click="showMobileMenu = false"
            >
              創作歌曲
            </RouterLink>
          </div>
        </nav>
      </Transition>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { SearchIcon, MenuIcon, XIcon, ChevronDownIcon } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import BaseButton from '@/components/ui/BaseButton.vue'
import SearchBar from '@/components/features/SearchBar.vue'

const router = useRouter()
const authStore = useAuthStore()

const showMobileMenu = ref(false)
const showMobileSearch = ref(false)
const showUserMenu = ref(false)

const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value
  showMobileSearch.value = false
}

const toggleMobileSearch = () => {
  showMobileSearch.value = !showMobileSearch.value
  showMobileMenu.value = false
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const getInitials = (name?: string) => {
  if (!name) return '?'
  return name
    .split(' ')
    .map((word) => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    showUserMenu.value = false
    router.push('/')
  } catch (error) {
    console.error('Logout failed:', error)
  }
}
</script>
