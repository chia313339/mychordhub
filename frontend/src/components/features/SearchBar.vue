<template>
  <div class="relative">
    <div class="relative">
      <SearchIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
      <input
        v-model="searchQuery"
        type="search"
        placeholder="搜索歌曲、藝人或和絃..."
        class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-chord-primary focus:border-transparent"
        @keydown.enter="handleSearch"
        @input="handleInput"
      />
    </div>
    
    <!-- 搜索建議下拉選單 -->
    <div
      v-if="showSuggestions && suggestions.length > 0"
      class="absolute top-full left-0 right-0 mt-1 bg-white rounded-lg shadow-lg border border-gray-200 max-h-64 overflow-y-auto z-50"
    >
      <div
        v-for="(suggestion, index) in suggestions"
        :key="index"
        class="px-4 py-2 hover:bg-gray-50 cursor-pointer text-sm"
        @click="selectSuggestion(suggestion)"
      >
        {{ suggestion }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { SearchIcon } from 'lucide-vue-next'
import { songsService } from '@/services/songs'
import { useDebounceFn } from '@vueuse/core'

const router = useRouter()

const searchQuery = ref('')
const suggestions = ref<string[]>([])
const showSuggestions = ref(false)
const isLoading = ref(false)

// 防抖搜索建議
const debouncedGetSuggestions = useDebounceFn(async (query: string) => {
  if (query.length < 2) {
    suggestions.value = []
    showSuggestions.value = false
    return
  }

  try {
    isLoading.value = true
    const results = await songsService.getSearchSuggestions(query)
    suggestions.value = results
    showSuggestions.value = true
  } catch (error) {
    console.error('Failed to get suggestions:', error)
    suggestions.value = []
    showSuggestions.value = false
  } finally {
    isLoading.value = false
  }
}, 300)

const handleInput = () => {
  debouncedGetSuggestions(searchQuery.value)
}

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    showSuggestions.value = false
    router.push({
      name: 'browse',
      query: { q: searchQuery.value.trim() }
    })
  }
}

const selectSuggestion = (suggestion: string) => {
  searchQuery.value = suggestion
  showSuggestions.value = false
  handleSearch()
}

// 點擊外部關閉建議
watch(showSuggestions, (newValue) => {
  if (newValue) {
    document.addEventListener('click', closeSuggestions)
  } else {
    document.removeEventListener('click', closeSuggestions)
  }
})

const closeSuggestions = (event: Event) => {
  const target = event.target as HTMLElement
  if (!target.closest('.relative')) {
    showSuggestions.value = false
  }
}
</script>