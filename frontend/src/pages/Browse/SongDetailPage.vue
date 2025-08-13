<template>
  <div class="song-detail-page">
    <!-- 載入中 -->
    <div v-if="isLoading && !song" class="loading-container">
      <LoadingOverlay :show="true" message="載入歌曲中..." />
    </div>
    
    <!-- 歌曲不存在 -->
    <div v-else-if="!song && !isLoading" class="error-container">
      <div class="error-content">
        <h1 class="error-title">歌曲不存在</h1>
        <p class="error-message">您要查看的歌曲可能已被刪除或不存在。</p>
        <router-link to="/browse" class="back-btn">
          返回瀏覽頁面
        </router-link>
      </div>
    </div>
    
    <!-- 歌曲內容 -->
    <div v-else-if="song" class="song-content">
      <!-- 歌曲標題區域 -->
      <div class="song-header">
        <div class="container">
          <div class="header-content">
            <div class="song-info">
              <h1 class="song-title">{{ song.title }}</h1>
              <p class="song-artist">{{ song.artist }}</p>
              
              <div class="song-meta">
                <div class="meta-item">
                  <span class="meta-label">調性:</span>
                  <span class="meta-value key-display">{{ song.key_signature }}</span>
                  <span v-if="song.capo_position > 0" class="capo-info">
                    (Capo {{ song.capo_position }})
                  </span>
                </div>
                
                <div class="meta-item">
                  <span class="meta-label">BPM:</span>
                  <span class="meta-value">{{ song.bpm }}</span>
                </div>
                
                <div class="meta-item">
                  <span class="meta-label">難度:</span>
                  <span class="meta-value difficulty-badge" :class="getDifficultyClass(song.difficulty)">
                    {{ getDifficultyText(song.difficulty) }}
                  </span>
                </div>
                
                <div class="meta-item">
                  <span class="meta-label">風格:</span>
                  <span class="meta-value">{{ getGenreText(song.genre) }}</span>
                </div>
              </div>
              
              <div class="song-stats">
                <div class="rating">
                  <div class="stars">★★★★☆</div>
                  <span class="rating-value">{{ song.average_rating.toFixed(1) }}</span>
                  <span class="rating-count">({{ song.rating_count }} 評價)</span>
                </div>
                
                <div class="view-count">
                  {{ formatNumber(song.view_count) }} 次瀏覽
                </div>
                
                <div v-if="song.author" class="author-info">
                  作者：{{ song.author.display_name }}
                </div>
              </div>
            </div>
            
            <!-- 操作按鈕 -->
            <div class="action-buttons">
              <button @click="togglePlayback" class="play-btn" :class="{ active: isPlaying }">
                <svg v-if="!isPlaying" class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1M9 16v-6a1 1 0 011-1h4a1 1 0 011 1v6M12 7V3"></path>
                </svg>
                <svg v-else class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                {{ isPlaying ? '停止播放' : '自動播放' }}
              </button>
              
              <button @click="toggleTranspose" class="transpose-btn">
                <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                轉調
              </button>
              
              <button v-if="canEdit" @click="editSong" class="edit-btn">
                <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                </svg>
                編輯
              </button>
              
              <button @click="shareSong" class="share-btn">
                <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z"></path>
                </svg>
                分享
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 轉調控制面板（可收起） -->
      <div v-if="showTranspose" class="transpose-panel">
        <div class="container">
          <div class="transpose-content">
            <h3 class="transpose-title">轉調設定</h3>
            
            <div class="transpose-controls">
              <div class="control-group">
                <label class="control-label">原調:</label>
                <span class="original-key">{{ song?.key_signature }}</span>
              </div>
              
              <div class="control-group">
                <label class="control-label">轉調:</label>
                <select v-model="targetKey" @change="applyTranspose" class="key-select">
                  <option v-for="key in availableKeys" :key="key" :value="key">
                    {{ key }}
                  </option>
                </select>
              </div>
              
              <div class="control-group">
                <label class="control-label">Capo:</label>
                <input 
                  v-model.number="capoPosition" 
                  @change="applyTranspose"
                  type="range" 
                  min="0" 
                  max="12" 
                  class="capo-slider"
                />
                <span class="capo-value">{{ capoPosition }}</span>
              </div>
              
              <button @click="resetTranspose" class="reset-btn">
                重設
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 歌詞和絃顯示區域 -->
      <div class="lyrics-section">
        <div class="container">
          <!-- 播放控制區域 -->
          <div v-if="isPlaying" class="playback-controls">
            <div class="playback-info">
              <span class="tempo-display">速度: {{ currentTempo }} BPM</span>
              <div class="tempo-controls">
                <button @click="adjustTempo(-10)" class="tempo-btn">-</button>
                <input 
                  v-model.number="currentTempo" 
                  type="range" 
                  min="60" 
                  max="200" 
                  class="tempo-slider"
                />
                <button @click="adjustTempo(10)" class="tempo-btn">+</button>
              </div>
            </div>
            
            <div class="scroll-controls">
              <label class="control-label">
                <input v-model="autoScroll" type="checkbox" />
                自動滾動
              </label>
              <div v-if="autoScroll" class="scroll-speed-control">
                <span class="speed-label">滾動速度:</span>
                <input 
                  v-model.number="scrollSpeed" 
                  type="range" 
                  min="1" 
                  max="10" 
                  class="speed-slider"
                />
              </div>
            </div>
          </div>
          
          <!-- 歌詞內容 -->
          <div v-if="songContent" class="lyrics-container" ref="lyricsContainer">
            <div class="lyrics-content" :class="{ 'auto-scrolling': isPlaying && autoScroll }">
              <!-- 這裡將使用 LyricsDisplay 組件來顯示帶和絃的歌詞 -->
              <div v-html="formattedLyrics" class="lyrics-text"></div>
            </div>
          </div>
          
          <!-- 載入歌詞中 -->
          <div v-else-if="isLoadingContent" class="loading-lyrics">
            <LoadingOverlay :show="true" message="載入歌詞中..." />
          </div>
          
          <!-- 沒有歌詞 -->
          <div v-else class="no-lyrics">
            <p class="no-lyrics-text">此歌曲尚未添加歌詞和絃</p>
            <button v-if="canEdit" @click="editSong" class="add-lyrics-btn">
              添加歌詞
            </button>
          </div>
        </div>
      </div>
      
      <!-- 歌曲信息和評論區域 -->
      <div class="info-section">
        <div class="container">
          <div class="info-grid">
            <!-- 歌曲描述 -->
            <div v-if="song?.description" class="description-card">
              <h3 class="card-title">歌曲介紹</h3>
              <p class="description-text">{{ song.description }}</p>
            </div>
            
            <!-- 歌曲結構 -->
            <div v-if="songContent?.structure_metadata" class="structure-card">
              <h3 class="card-title">歌曲結構</h3>
              <div class="structure-items">
                <div v-if="songContent.structure_metadata.intro" class="structure-item">
                  <span class="structure-label">前奏</span>
                </div>
                <div v-if="songContent.structure_metadata.verse1" class="structure-item">
                  <span class="structure-label">第一段</span>
                </div>
                <div v-if="songContent.structure_metadata.chorus" class="structure-item">
                  <span class="structure-label">副歌</span>
                </div>
                <div v-if="songContent.structure_metadata.verse2" class="structure-item">
                  <span class="structure-label">第二段</span>
                </div>
                <div v-if="songContent.structure_metadata.bridge" class="structure-item">
                  <span class="structure-label">橋段</span>
                </div>
                <div v-if="songContent.structure_metadata.outro" class="structure-item">
                  <span class="structure-label">尾奏</span>
                </div>
              </div>
            </div>
            
            <!-- 統計信息 -->
            <div class="stats-card">
              <h3 class="card-title">統計信息</h3>
              <div class="stats-items">
                <div class="stat-item">
                  <span class="stat-label">創建時間</span>
                  <span class="stat-value">{{ song ? formatDate(song.created_at) : '' }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">最後更新</span>
                  <span class="stat-value">{{ song ? formatDate(song.updated_at) : '' }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">瀏覽次數</span>
                  <span class="stat-value">{{ song ? formatNumber(song.view_count) : '' }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">評價數量</span>
                  <span class="stat-value">{{ song?.rating_count || 0 }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useSongsStore } from '@/stores/songs'
import { useAuthStore } from '@/stores/auth'
import LoadingOverlay from '@/components/ui/LoadingOverlay.vue'
import type { Song, SongContent, Note, Difficulty, Genre } from '@/types'

interface Props {
  id: string
}

const props = defineProps<Props>()
const router = useRouter()
const songsStore = useSongsStore()
const authStore = useAuthStore()

// 響應式數據
const isLoadingContent = ref(false)
const showTranspose = ref(false)
const isPlaying = ref(false)
const autoScroll = ref(false)
const scrollSpeed = ref(5)
const currentTempo = ref(120)
const targetKey = ref<Note>('C')
const capoPosition = ref(0)
const transposedChords = ref<Record<string, string>>({})
const lyricsContainer = ref<HTMLElement>()

// 自動滾動相關
let scrollInterval: number | null = null

// 計算屬性
const song = computed(() => songsStore.currentSong)
const songContent = computed(() => songsStore.currentSongContent)
const isLoading = computed(() => songsStore.isLoading)
const canEdit = computed(() => {
  if (!authStore.isAuthenticated || !song.value) return false
  return authStore.user?.id === song.value.author_id
})

// 可用調性
const availableKeys: Note[] = [
  'C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 
  'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B'
]

// 格式化歌詞（包含和絃）
const formattedLyrics = computed(() => {
  if (!songContent.value) return ''
  
  let lyrics = songContent.value.lyrics
  const chordPositions = songContent.value.chord_positions
  
  // 按位置倒序排列，避免插入和絃時位置偏移
  const sortedChords = [...chordPositions].sort((a, b) => b.position - a.position)
  
  // 按行分割歌詞
  const lines = lyrics.split('\n')
  
  // 處理每一行的和絃
  sortedChords.forEach(chordPos => {
    if (chordPos.line < lines.length) {
      const line = lines[chordPos.line]
      const chord = transposedChords.value[chordPos.chord] || chordPos.chord
      
      // 在指定位置插入和絃標記
      const before = line.substring(0, chordPos.position)
      const after = line.substring(chordPos.position)
      lines[chordPos.line] = `${before}<span class="chord">${chord}</span>${after}`
    }
  })
  
  return lines.join('\n').replace(/\n/g, '<br>')
})

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
    month: 'long',
    day: 'numeric'
  })
}

const togglePlayback = () => {
  isPlaying.value = !isPlaying.value
  
  if (isPlaying.value) {
    currentTempo.value = song.value?.bpm || 120
    if (autoScroll.value) {
      startAutoScroll()
    }
  } else {
    stopAutoScroll()
  }
}

const toggleTranspose = () => {
  showTranspose.value = !showTranspose.value
  if (showTranspose.value && song.value) {
    targetKey.value = song.value.key_signature
    capoPosition.value = song.value.capo_position
  }
}

const applyTranspose = () => {
  // 這裡實作和絃轉調邏輯
  // 暫時使用簡單的映射，之後可以使用 music theory 庫
  console.log('轉調:', { from: song.value?.key_signature, to: targetKey.value, capo: capoPosition.value })
}

const resetTranspose = () => {
  if (song.value) {
    targetKey.value = song.value.key_signature
    capoPosition.value = song.value.capo_position
    transposedChords.value = {}
  }
}

const adjustTempo = (delta: number) => {
  currentTempo.value = Math.max(60, Math.min(200, currentTempo.value + delta))
}

const startAutoScroll = () => {
  if (scrollInterval) return
  
  scrollInterval = window.setInterval(() => {
    if (lyricsContainer.value) {
      const scrollAmount = scrollSpeed.value * 2
      lyricsContainer.value.scrollTop += scrollAmount
    }
  }, 1000) // 每秒滾動
}

const stopAutoScroll = () => {
  if (scrollInterval) {
    clearInterval(scrollInterval)
    scrollInterval = null
  }
}

const editSong = () => {
  router.push(`/edit/${props.id}`)
}

const shareSong = async () => {
  if (!song.value) return
  
  const shareData = {
    title: `${song.value.title} - ${song.value.artist}`,
    url: window.location.href
  }
  
  if (navigator.share) {
    try {
      await navigator.share(shareData)
    } catch (err) {
      console.log('分享取消或失敗')
    }
  } else {
    // Fallback: 複製到剪貼板
    await navigator.clipboard.writeText(shareData.url)
    alert('連結已複製到剪貼板')
  }
}

// 載入歌曲數據
const loadSongData = async () => {
  try {
    await songsStore.getSong(props.id)
    
    isLoadingContent.value = true
    await songsStore.getSongContent(props.id)
  } catch (error) {
    console.error('載入歌曲失敗:', error)
  } finally {
    isLoadingContent.value = false
  }
}

// 生命週期
onMounted(async () => {
  await loadSongData()
})

onUnmounted(() => {
  stopAutoScroll()
  songsStore.clearCurrentSong()
})
</script>

<style scoped>
.song-detail-page {
  min-height: 100vh;
  background-color: var(--color-gray-50);
}

/* 載入和錯誤狀態 */
.loading-container,
.error-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}

.error-content {
  text-align: center;
  padding: 2rem;
}

.error-title {
  font-size: 2rem;
  font-weight: bold;
  color: var(--color-gray-900);
  margin-bottom: 1rem;
}

.error-message {
  color: var(--color-gray-600);
  margin-bottom: 2rem;
}

.back-btn {
  display: inline-block;
  background-color: var(--color-chord-primary);
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  text-decoration: none;
  font-weight: 500;
  transition: background-color 0.2s;
}

.back-btn:hover {
  background-color: var(--color-chord-primary-dark);
}

/* 歌曲標題區域 */
.song-header {
  background: white;
  border-bottom: 1px solid var(--color-gray-200);
  padding: 2rem 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: start;
  gap: 2rem;
}

.song-info {
  flex: 1;
}

.song-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: var(--color-gray-900);
  margin-bottom: 0.5rem;
}

.song-artist {
  font-size: 1.25rem;
  color: var(--color-gray-600);
  margin-bottom: 1.5rem;
}

.song-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  margin-bottom: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.meta-label {
  color: var(--color-gray-500);
  font-size: 0.875rem;
}

.meta-value {
  font-weight: 500;
  color: var(--color-gray-900);
}

.key-display {
  background-color: var(--color-chord-primary);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-weight: bold;
}

.capo-info {
  color: var(--color-gray-500);
  font-size: 0.875rem;
}

.difficulty-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
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

.song-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  align-items: center;
}

.rating {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stars {
  color: var(--color-yellow-400);
  font-size: 1.125rem;
}

.rating-value {
  font-weight: 600;
  color: var(--color-gray-800);
}

.rating-count {
  color: var(--color-gray-500);
  font-size: 0.875rem;
}

.view-count,
.author-info {
  color: var(--color-gray-600);
  font-size: 0.875rem;
}

/* 操作按鈕 */
.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.play-btn,
.transpose-btn,
.edit-btn,
.share-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.play-btn {
  background-color: var(--color-chord-primary);
  color: white;
}

.play-btn:hover {
  background-color: var(--color-chord-primary-dark);
}

.play-btn.active {
  background-color: #dc2626;
}

.transpose-btn,
.share-btn {
  background-color: var(--color-gray-200);
  color: var(--color-gray-700);
}

.transpose-btn:hover,
.share-btn:hover {
  background-color: var(--color-gray-300);
}

.edit-btn {
  background-color: var(--color-chord-accent);
  color: white;
}

.edit-btn:hover {
  background-color: #d97706;
}

/* 轉調面板 */
.transpose-panel {
  background: var(--color-gray-100);
  border-bottom: 1px solid var(--color-gray-200);
  padding: 1.5rem 0;
}

.transpose-content {
  max-width: 800px;
  margin: 0 auto;
}

.transpose-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-gray-900);
  margin-bottom: 1rem;
}

.transpose-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  align-items: center;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.control-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-gray-700);
}

.original-key {
  background-color: var(--color-chord-primary);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-weight: bold;
}

.key-select {
  padding: 0.5rem;
  border: 1px solid var(--color-gray-300);
  border-radius: 0.25rem;
  background: white;
}

.capo-slider,
.tempo-slider,
.speed-slider {
  width: 100px;
}

.capo-value {
  font-weight: 500;
  min-width: 20px;
}

.reset-btn {
  background-color: var(--color-gray-200);
  color: var(--color-gray-700);
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.reset-btn:hover {
  background-color: var(--color-gray-300);
}

/* 歌詞區域 */
.lyrics-section {
  padding: 2rem 0;
}

.playback-controls {
  background: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.playback-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.tempo-display {
  font-weight: 500;
  color: var(--color-gray-700);
}

.tempo-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tempo-btn {
  background-color: var(--color-gray-200);
  border: none;
  border-radius: 0.25rem;
  width: 2rem;
  height: 2rem;
  cursor: pointer;
  font-weight: bold;
}

.tempo-btn:hover {
  background-color: var(--color-gray-300);
}

.scroll-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.scroll-speed-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.speed-label {
  font-size: 0.875rem;
  color: var(--color-gray-600);
}

/* 歌詞容器 */
.lyrics-container {
  background: white;
  border-radius: 0.5rem;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  max-height: 70vh;
  overflow-y: auto;
}

.lyrics-content {
  line-height: 2;
  font-size: 1.125rem;
  color: var(--color-gray-800);
}

.lyrics-text :deep(.chord) {
  background-color: var(--color-chord-primary);
  color: white;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  margin: 0 0.25rem;
  white-space: nowrap;
}

.auto-scrolling {
  scroll-behavior: smooth;
}

.loading-lyrics,
.no-lyrics {
  text-align: center;
  padding: 4rem 0;
}

.no-lyrics-text {
  color: var(--color-gray-600);
  margin-bottom: 1rem;
}

.add-lyrics-btn {
  background-color: var(--color-chord-primary);
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.add-lyrics-btn:hover {
  background-color: var(--color-chord-primary-dark);
}

/* 信息區域 */
.info-section {
  background: white;
  padding: 2rem 0;
  border-top: 1px solid var(--color-gray-200);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.description-card,
.structure-card,
.stats-card {
  background: var(--color-gray-50);
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-gray-900);
  margin-bottom: 1rem;
}

.description-text {
  color: var(--color-gray-700);
  line-height: 1.6;
}

.structure-items,
.stats-items {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.structure-item,
.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.structure-label,
.stat-label {
  color: var(--color-gray-600);
  font-size: 0.875rem;
}

.stat-value {
  font-weight: 500;
  color: var(--color-gray-800);
}

/* 響應式設計 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: stretch;
    gap: 1.5rem;
  }
  
  .song-title {
    font-size: 1.75rem;
  }
  
  .song-meta {
    flex-direction: column;
    gap: 0.75rem;
    align-items: start;
  }
  
  .action-buttons {
    flex-direction: row;
    flex-wrap: wrap;
  }
  
  .transpose-controls {
    flex-direction: column;
    align-items: start;
    gap: 1rem;
  }
  
  .playback-info,
  .scroll-controls {
    flex-direction: column;
    align-items: start;
    gap: 0.75rem;
  }
  
  .lyrics-container {
    max-height: 50vh;
    padding: 1rem;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>