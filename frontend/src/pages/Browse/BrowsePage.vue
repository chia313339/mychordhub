<template>
  <div class="browse-page">
    <!-- 搜索與篩選區域 -->
    <div class="search-section">
      <div class="container">
        <h1 class="page-title">瀏覽歌曲</h1>
        
        <!-- 搜索框 -->
        <div class="search-container">
          <SearchBar />
        </div>
        
        <!-- 篩選器 -->
        <div class="filters-container">
          <div class="filters-row">
            <!-- Key 篩選 -->
            <div class="filter-group">
              <label class="filter-label">調性</label>
              <select v-model="filters.key_signature" @change="applyFilters" class="filter-select">
                <option value="">全部</option>
                <option v-for="key in availableKeys" :key="key" :value="key">
                  {{ key }}
                </option>
              </select>
            </div>
            
            <!-- 難度篩選 -->
            <div class="filter-group">
              <label class="filter-label">難度</label>
              <select v-model="filters.difficulty" @change="applyFilters" class="filter-select">
                <option value="">全部</option>
                <option value="beginner">初學</option>
                <option value="intermediate">中級</option>
                <option value="advanced">進階</option>
                <option value="expert">專家</option>
              </select>
            </div>
            
            <!-- 風格篩選 -->
            <div class="filter-group">
              <label class="filter-label">風格</label>
              <select v-model="filters.genre" @change="applyFilters" class="filter-select">
                <option value="">全部</option>
                <option value="pop">流行</option>
                <option value="rock">搖滾</option>
                <option value="folk">民謠</option>
                <option value="country">鄉村</option>
                <option value="jazz">爵士</option>
                <option value="blues">藍調</option>
                <option value="classical">古典</option>
                <option value="other">其他</option>
              </select>
            </div>
            
            <!-- 排序選項 -->
            <div class="filter-group">
              <label class="filter-label">排序</label>
              <select v-model="sortOption" @change="applySorting" class="filter-select">
                <option value="popular">熱門程度</option>
                <option value="latest">最新發布</option>
                <option value="rating">評分</option>
                <option value="title">標題</option>
                <option value="view_count">瀏覽次數</option>
              </select>
            </div>
            
            <!-- 清除篩選器 -->
            <button @click="clearFilters" class="clear-filters-btn">
              清除篩選
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 歌曲列表區域 -->
    <div class="songs-section">
      <div class="container">
        <!-- 結果統計 -->
        <div class="results-info">
          <span v-if="searchQuery" class="search-result">
            「{{ searchQuery }}」的搜索結果：
          </span>
          <span class="total-count">
            共 {{ pagination.total }} 首歌曲
          </span>
        </div>
        
        <!-- 載入中 -->
        <div v-if="isLoading && songs.length === 0" class="loading-container">
          <LoadingOverlay :show="true" message="載入歌曲中..." />
        </div>
        
        <!-- 歌曲列表 -->
        <div v-else-if="songs.length > 0" class="songs-grid">
          <SongCard
            v-for="song in songs"
            :key="song.id"
            :song="song"
            @click="goToSong"
          />
        </div>
        
        <!-- 空狀態 -->
        <div v-else class="empty-state">
          <div class="empty-icon">🎵</div>
          <h3 class="empty-title">
            {{ searchQuery ? '沒有找到相符的歌曲' : '暫無歌曲' }}
          </h3>
          <p class="empty-description">
            {{ searchQuery ? '試試調整搜索關鍵字或篩選條件' : '快來創建第一首歌曲吧！' }}
          </p>
          <router-link v-if="!searchQuery" to="/edit" class="create-song-btn">
            創建歌曲
          </router-link>
        </div>
        
        <!-- 載入更多 -->
        <div v-if="hasMore && !isLoading" class="load-more-container">
          <button @click="loadMore" class="load-more-btn" :disabled="isLoading">
            載入更多
          </button>
        </div>
        
        <!-- 載入更多中 -->
        <div v-if="isLoading && songs.length > 0" class="loading-more">
          載入更多歌曲中...
        </div>
        
        <!-- 分頁信息 -->
        <div v-if="songs.length > 0" class="pagination-info">
          顯示第 {{ (pagination.page - 1) * pagination.size + 1 }} - 
          {{ Math.min(pagination.page * pagination.size, pagination.total) }} 首，
          共 {{ pagination.total }} 首歌曲
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSongsStore } from '@/stores/songs'
import SearchBar from '@/components/features/SearchBar.vue'
import SongCard from '@/components/features/SongCard.vue'
import LoadingOverlay from '@/components/ui/LoadingOverlay.vue'
import type { SongSearchFilters, Note, Difficulty, Genre, Song } from '@/types'

const router = useRouter()
const route = useRoute()
const songsStore = useSongsStore()

// 響應式數據
const filters = ref<SongSearchFilters>({})
const sortOption = ref('popular')
const searchQuery = ref('')

// 可用選項
const availableKeys: Note[] = [
  'C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 
  'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B'
]

// 計算屬性
const songs = computed(() => songsStore.filteredSongs)
const isLoading = computed(() => songsStore.isLoading)
const hasMore = computed(() => songsStore.hasMore)
const pagination = computed(() => songsStore.pagination)

// 方法
const getDifficultyClass = (difficulty: Difficulty) => {
  const classes = {
    beginner: 'difficulty-beginner',
    intermediate: 'difficulty-intermediate', 
    advanced: 'difficulty-advanced',
    expert: 'difficulty-expert'
  }
  return classes[difficulty] || 'difficulty-beginner'
}

const getDifficultyText = (difficulty: Difficulty) => {
  const texts = {
    beginner: '初學',
    intermediate: '中級',
    advanced: '進階',
    expert: '專家'
  }
  return texts[difficulty] || '初學'
}

const getGenreText = (genre: Genre) => {
  const texts = {
    pop: '流行',
    rock: '搖滾',
    folk: '民謠',
    country: '鄉村',
    jazz: '爵士',
    blues: '藍調',
    classical: '古典',
    other: '其他'
  }
  return texts[genre] || '其他'
}

const formatNumber = (num: number) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const goToSong = (song: Song) => {
  router.push(`/songs/${song.id}`)
}

const applyFilters = () => {
  loadSongs(true)
}

const applySorting = () => {
  const [sort, order] = getSortParams()
  loadSongs(true, { sort, order })
}

const getSortParams = (): [string, 'asc' | 'desc'] => {
  switch (sortOption.value) {
    case 'latest':
      return ['created_at', 'desc']
    case 'rating':
      return ['average_rating', 'desc']
    case 'title':
      return ['title', 'asc']
    case 'view_count':
      return ['view_count', 'desc']
    default:
      return ['view_count', 'desc'] // 默認按瀏覽量排序（熱門程度）
  }
}

const loadSongs = async (reset = false, extraParams = {}) => {
  const [sort, order] = getSortParams()
  
  const params = {
    query: searchQuery.value,
    filters: filters.value,
    sort,
    order,
    page: reset ? 1 : undefined,
    ...extraParams
  }
  
  if (searchQuery.value || Object.keys(filters.value).length > 0) {
    await songsStore.searchSongs(params.query, params.filters)
  } else {
    await songsStore.fetchSongs(params)
  }
}

const loadMore = async () => {
  await songsStore.loadMoreSongs()
}

const clearFilters = () => {
  filters.value = {}
  searchQuery.value = ''
  sortOption.value = 'popular'
  songsStore.clearSearch()
  loadSongs(true)
}

// 初始化
onMounted(async () => {
  // 從 URL 查詢參數獲取搜索關鍵字
  const query = route.query.q as string
  if (query) {
    searchQuery.value = query
  }
  
  // 從 URL 獲取其他參數
  if (route.query.sort) {
    sortOption.value = route.query.sort as string
  }
  
  await loadSongs(true)
})

// 監聽路由變化
watch(() => route.query, (newQuery) => {
  if (newQuery.q !== searchQuery.value) {
    searchQuery.value = (newQuery.q as string) || ''
    loadSongs(true)
  }
})
</script>

<style scoped>
.browse-page {
  min-height: 100vh;
  background-color: var(--color-gray-50);
}

/* 搜索與篩選區域 */
.search-section {
  background: white;
  border-bottom: 1px solid var(--color-gray-200);
  padding: 2rem 0;
}

.page-title {
  font-size: 2rem;
  font-weight: bold;
  color: var(--color-gray-900);
  margin-bottom: 1.5rem;
  text-align: center;
}

.search-container {
  max-width: 600px;
  margin: 0 auto 2rem auto;
}

.filters-container {
  max-width: 1200px;
  margin: 0 auto;
}

.filters-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  min-width: 120px;
}

.filter-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-gray-700);
  margin-bottom: 0.25rem;
}

.filter-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-gray-300);
  border-radius: 0.375rem;
  background: white;
  font-size: 0.875rem;
  color: var(--color-gray-900);
}

.filter-select:focus {
  outline: none;
  border-color: var(--color-chord-primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.clear-filters-btn {
  padding: 0.5rem 1rem;
  background-color: var(--color-gray-200);
  color: var(--color-gray-700);
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.clear-filters-btn:hover {
  background-color: var(--color-gray-300);
}

/* 歌曲列表區域 */
.songs-section {
  padding: 2rem 0;
}

.results-info {
  margin-bottom: 1.5rem;
  color: var(--color-gray-600);
}

.search-result {
  font-weight: 500;
  margin-right: 0.5rem;
}

.total-count {
  font-size: 0.875rem;
}

.loading-container {
  text-align: center;
  padding: 4rem 0;
}

.songs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

/* 歌曲卡片樣式 */
.song-card {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.song-card:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.song-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 0.5rem;
}

.song-title {
  font-weight: bold;
  font-size: 1.125rem;
  color: var(--color-gray-900);
  margin-right: 0.5rem;
}

.song-badge {
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  white-space: nowrap;
}

.difficulty-beginner {
  background-color: #dcfce7;
  color: #166534;
}

.difficulty-intermediate {
  background-color: #fef3c7;
  color: #92400e;
}

.difficulty-advanced {
  background-color: #fed7c3;
  color: #c2410c;
}

.difficulty-expert {
  background-color: #fecaca;
  color: #dc2626;
}

.song-artist {
  color: var(--color-gray-600);
  margin-bottom: 0.75rem;
  font-size: 0.9rem;
}

.song-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
}

.song-key {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.key-label {
  color: var(--color-gray-500);
}

.key-value {
  font-weight: 600;
  color: var(--color-chord-primary);
}

.capo-info {
  color: var(--color-gray-500);
  font-size: 0.75rem;
}

.song-genre {
  color: var(--color-gray-500);
  font-size: 0.75rem;
  background-color: var(--color-gray-100);
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
}

.song-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.rating {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.stars {
  color: var(--color-yellow-400);
  font-size: 0.875rem;
}

.rating-value {
  font-weight: 500;
  color: var(--color-gray-700);
  font-size: 0.875rem;
}

.rating-count {
  color: var(--color-gray-500);
  font-size: 0.75rem;
}

.view-count {
  font-size: 0.75rem;
  color: var(--color-gray-500);
}

.song-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.75rem;
  color: var(--color-gray-400);
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-gray-100);
}

.created-date {
}

.author {
  font-weight: 500;
}

/* 空狀態 */
.empty-state {
  text-align: center;
  padding: 4rem 0;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-title {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--color-gray-900);
  margin-bottom: 0.5rem;
}

.empty-description {
  color: var(--color-gray-600);
  margin-bottom: 2rem;
}

.create-song-btn {
  display: inline-block;
  background-color: var(--color-chord-primary);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  text-decoration: none;
  font-weight: 500;
  transition: background-color 0.2s;
}

.create-song-btn:hover {
  background-color: var(--color-chord-primary-dark);
}

/* 載入更多 */
.load-more-container {
  text-align: center;
  margin-top: 2rem;
}

.load-more-btn {
  background-color: var(--color-gray-200);
  color: var(--color-gray-700);
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.load-more-btn:hover:not(:disabled) {
  background-color: var(--color-gray-300);
}

.load-more-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-more {
  text-align: center;
  padding: 1rem 0;
  color: var(--color-gray-500);
  font-size: 0.875rem;
}

.pagination-info {
  text-align: center;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-gray-200);
  color: var(--color-gray-500);
  font-size: 0.875rem;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .filters-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    min-width: unset;
  }
  
  .songs-grid {
    grid-template-columns: 1fr;
  }
  
  .song-header {
    flex-direction: column;
    align-items: start;
    gap: 0.5rem;
  }
  
  .song-details {
    flex-direction: column;
    align-items: start;
    gap: 0.25rem;
  }
  
  .song-stats {
    flex-direction: column;
    align-items: start;
    gap: 0.25rem;
  }
}
</style>