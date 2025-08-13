<template>
  <footer class="bg-white border-t border-gray-200 mt-auto">
    <div class="container mx-auto px-4 py-8">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
        <!-- 品牌區域 -->
        <div class="col-span-1 md:col-span-2">
          <div class="flex items-center space-x-2 mb-4">
            <div class="w-8 h-8 bg-chord-primary rounded-lg flex items-center justify-center">
              <span class="text-white font-bold text-lg">M</span>
            </div>
            <span class="text-xl font-bold text-gray-900">MyChordHub</span>
          </div>
          <p class="text-gray-600 text-sm mb-4 max-w-md">
            專業的線上吉他譜編輯平台，提供直觀易用的和絃譜瀏覽與編輯功能。
          </p>
          <div class="flex space-x-4">
            <!-- 社交媒體連結可以在這裡添加 -->
          </div>
        </div>

        <!-- 快速連結 -->
        <div>
          <h3 class="font-semibold text-gray-900 mb-4">快速連結</h3>
          <ul class="space-y-2 text-sm">
            <li>
              <RouterLink to="/browse" class="text-gray-600 hover:text-chord-primary transition-colors">
                瀏覽歌曲
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/edit" class="text-gray-600 hover:text-chord-primary transition-colors">
                創作歌曲
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/about" class="text-gray-600 hover:text-chord-primary transition-colors">
                關於我們
              </RouterLink>
            </li>
          </ul>
        </div>

        <!-- 幫助與支援 -->
        <div>
          <h3 class="font-semibold text-gray-900 mb-4">幫助與支援</h3>
          <ul class="space-y-2 text-sm">
            <li>
              <a href="#" class="text-gray-600 hover:text-chord-primary transition-colors">
                使用說明
              </a>
            </li>
            <li>
              <a href="#" class="text-gray-600 hover:text-chord-primary transition-colors">
                常見問題
              </a>
            </li>
            <li>
              <a href="#" class="text-gray-600 hover:text-chord-primary transition-colors">
                聯絡我們
              </a>
            </li>
          </ul>
        </div>
      </div>

      <!-- 版權資訊 -->
      <div class="border-t border-gray-200 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
        <p class="text-gray-500 text-sm">
          © {{ currentYear }} MyChordHub. 保留所有權利。
        </p>
        <div class="flex space-x-6 text-sm text-gray-500 mt-4 md:mt-0">
          <a href="#" class="hover:text-chord-primary transition-colors">隱私政策</a>
          <a href="#" class="hover:text-chord-primary transition-colors">服務條款</a>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const currentYear = computed(() => new Date().getFullYear())
</script>