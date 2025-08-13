<template>
  <div class="home-page">
    <!-- 英雄區域 -->
    <section class="hero-section">
      <div class="container">
        <h1 class="hero-title">
          MyChordHub
        </h1>
        <p class="hero-subtitle">
          發現、創作、分享吉他譜 - 讓音樂觸手可及
        </p>
        
        <!-- 搜索區域 -->
        <div class="search-container">
          <SearchBar />
        </div>
        
        <!-- 快速統計 -->
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-number">{{ stats.songCount.toLocaleString() }}+</div>
            <div class="stat-label">首歌曲</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.userCount.toLocaleString() }}+</div>
            <div class="stat-label">位用戶</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.chordCount.toLocaleString() }}+</div>
            <div class="stat-label">個和絃</div>
          </div>
        </div>
      </div>
    </section>

    <!-- 主要內容區域 -->
    <main class="main-content">
      <!-- 熱門歌曲區域 -->
      <section class="songs-section">
        <div class="section-header">
          <h2 class="section-title">熱門歌曲</h2>
          <router-link to="/browse" class="view-all-link">
            查看全部 →
          </router-link>
        </div>
        
        <div v-if="isLoadingPopular" class="loading-container">
          <LoadingOverlay :show="true" message="載入熱門歌曲中..." />
        </div>
        
        <div v-else-if="popularSongs.length > 0" class="songs-grid">
          <SongCard
            v-for="song in popularSongs"
            :key="song.id"
            :song="song"
            @click="goToSong"
          />
        </div>
        
        <div v-else class="empty-state">
          暫無熱門歌曲
        </div>
      </section>

      <!-- 最新歌曲區域 -->
      <section class="songs-section">
        <div class="section-header">
          <h2 class="section-title">最新歌曲</h2>
          <router-link to="/browse?sort=created_at&order=desc" class="view-all-link">
            查看全部 →
          </router-link>
        </div>
        
        <div v-if="isLoadingLatest" class="loading-container">
          <LoadingOverlay :show="true" message="載入最新歌曲中..." />
        </div>
        
        <div v-else-if="latestSongs.length > 0" class="songs-grid">
          <SongCard
            v-for="song in latestSongs"
            :key="song.id"
            :song="song"
            @click="goToSong"
          />
        </div>
        
        <div v-else class="empty-state">
          暫無最新歌曲
        </div>
      </section>

      <!-- 功能介紹區域 -->
      <section class="features-section">
        <div class="features-header">
          <h2 class="features-title">為什麼選擇 MyChordHub？</h2>
          <p class="features-subtitle">專為吉他愛好者打造的全方位譜曲平台</p>
        </div>
        
        <div class="features-grid">
          <div class="feature-item">
            <div class="feature-icon">
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"></path>
              </svg>
            </div>
            <h3 class="feature-title">豐富樂譜庫</h3>
            <p class="feature-description">擁有數萬首歌曲的和絃譜，涵蓋各種音樂風格</p>
          </div>
          
          <div class="feature-item">
            <div class="feature-icon">
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path>
              </svg>
            </div>
            <h3 class="feature-title">簡易編輯器</h3>
            <p class="feature-description">直觀的編輯界面，輕鬆創作和分享您的音樂作品</p>
          </div>
          
          <div class="feature-item">
            <div class="feature-icon">
              <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
              </svg>
            </div>
            <h3 class="feature-title">智能轉調</h3>
            <p class="feature-description">一鍵轉調功能，支援 Capo 計算，適應不同演奏需求</p>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import SearchBar from '@/components/features/SearchBar.vue'
import SongCard from '@/components/features/SongCard.vue'
import LoadingOverlay from '@/components/ui/LoadingOverlay.vue'
import { songsService } from '@/services/songs'
import type { Song } from '@/types'

const router = useRouter()

// 狀態管理
const popularSongs = ref<Song[]>([])
const latestSongs = ref<Song[]>([])
const isLoadingPopular = ref(false)
const isLoadingLatest = ref(false)

// 統計數據（將來可以從 API 獲取）
const stats = ref({
  songCount: 15000,
  userCount: 5000,
  chordCount: 1200
})

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// 導航到歌曲詳情頁
const goToSong = (song: Song) => {
  router.push(`/songs/${song.id}`)
}

// 載入熱門歌曲
const loadPopularSongs = async () => {
  try {
    isLoadingPopular.value = true
    popularSongs.value = await songsService.getPopularSongs(6)
  } catch (error) {
    console.error('Failed to load popular songs:', error)
  } finally {
    isLoadingPopular.value = false
  }
}

// 載入最新歌曲
const loadLatestSongs = async () => {
  try {
    isLoadingLatest.value = true
    latestSongs.value = await songsService.getLatestSongs(6)
  } catch (error) {
    console.error('Failed to load latest songs:', error)
  } finally {
    isLoadingLatest.value = false
  }
}

// 頁面初始化
onMounted(() => {
  loadPopularSongs()
  loadLatestSongs()
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background-color: var(--color-gray-50);
}

/* 英雄區域樣式 */
.hero-section {
  background: linear-gradient(to bottom, var(--color-chord-primary), var(--color-chord-primary-dark));
  color: white;
  padding: 5rem 0;
  text-align: center;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: bold;
  margin-bottom: 1.5rem;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
}

.hero-subtitle {
  font-size: 1.25rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

@media (max-width: 768px) {
  .hero-subtitle {
    font-size: 1rem;
  }
}

.search-container {
  max-width: 42rem;
  margin: 0 auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-top: 3rem;
  max-width: 28rem;
  margin-left: auto;
  margin-right: auto;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: bold;
}

.stat-label {
  font-size: 0.875rem;
  opacity: 0.75;
}

/* 主要內容樣式 */
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem 1rem;
}

.songs-section {
  margin-bottom: 3rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--color-gray-900);
}

.view-all-link {
  color: var(--color-chord-primary);
  font-weight: 500;
  text-decoration: none;
  transition: color 0.2s;
}

.view-all-link:hover {
  color: var(--color-chord-primary-dark);
}

.loading-container {
  text-align: center;
  padding: 2rem 0;
}

.songs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.song-card {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  cursor: pointer;
  transition: box-shadow 0.2s;
}

.song-card:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.song-title {
  font-weight: bold;
  font-size: 1.125rem;
  margin-bottom: 0.5rem;
  color: var(--color-gray-900);
}

.song-artist {
  color: var(--color-gray-600);
  margin-bottom: 0.5rem;
}

.song-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  color: var(--color-gray-500);
  margin-bottom: 0.5rem;
}

.song-rating {
  display: flex;
  align-items: center;
}

.stars {
  color: var(--color-yellow-400);
  margin-right: 0.5rem;
}

.rating-value {
  font-size: 0.875rem;
  color: var(--color-gray-600);
}

.empty-state {
  text-align: center;
  padding: 2rem 0;
  color: var(--color-gray-500);
}

/* 功能介紹區域樣式 */
.features-section {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 4rem 2rem;
  margin-top: 2rem;
}

.features-header {
  text-align: center;
  margin-bottom: 3rem;
}

.features-title {
  font-size: 1.875rem;
  font-weight: bold;
  color: var(--color-gray-900);
  margin-bottom: 1rem;
}

.features-subtitle {
  font-size: 1.125rem;
  color: var(--color-gray-600);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.feature-item {
  text-align: center;
}

.feature-icon {
  width: 4rem;
  height: 4rem;
  background-color: var(--color-chord-primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem auto;
}

.icon {
  width: 2rem;
  height: 2rem;
  color: white;
}

.feature-title {
  font-size: 1.25rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  color: var(--color-gray-900);
}

.feature-description {
  color: var(--color-gray-600);
}
</style>
