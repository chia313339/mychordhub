<template>
  <div class="song-card" @click="handleClick">
    <!-- 歌曲標題和難度標籤 -->
    <div class="song-header">
      <h3 class="song-title">{{ song.title }}</h3>
      <div class="difficulty-badge" :class="getDifficultyClass(song.difficulty)">
        {{ getDifficultyText(song.difficulty) }}
      </div>
    </div>
    
    <!-- 歌手名稱 -->
    <p class="song-artist">{{ song.artist }}</p>
    
    <!-- 歌曲詳細信息 -->
    <div class="song-details">
      <div class="key-info">
        <span class="key-label">Key:</span>
        <span class="key-value">{{ song.key_signature }}</span>
        <span v-if="song.capo_position > 0" class="capo-info">
          (Capo {{ song.capo_position }})
        </span>
      </div>
      
      <div class="genre-tag">{{ getGenreText(song.genre) }}</div>
    </div>
    
    <!-- 評分和統計 -->
    <div class="song-stats">
      <div class="rating-section">
        <div class="stars">
          <span 
            v-for="star in 5" 
            :key="star" 
            class="star" 
            :class="{ filled: star <= Math.round(song.average_rating) }"
          >★</span>
        </div>
        <span class="rating-value">{{ song.average_rating.toFixed(1) }}</span>
        <span class="rating-count">({{ song.rating_count }})</span>
      </div>
      
      <div class="view-count">
        {{ formatViewCount(song.view_count) }} 次瀏覽
      </div>
    </div>
    
    <!-- 歌曲元信息 -->
    <div class="song-meta">
      <div class="meta-left">
        <span class="created-date">{{ formatDate(song.created_at) }}</span>
      </div>
      
      <div class="meta-right">
        <span v-if="song.author" class="author">
          {{ song.author.display_name }}
        </span>
      </div>
    </div>
    
    <!-- 操作按鈕（可選） -->
    <div v-if="showActions" class="card-actions" @click.stop>
      <button 
        v-if="canEdit" 
        @click="$emit('edit', song)"
        class="action-btn edit-btn"
        title="編輯歌曲"
      >
        <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
        </svg>
      </button>
      
      <button 
        @click="$emit('favorite', song)"
        class="action-btn favorite-btn"
        :class="{ active: isFavorited }"
        :title="isFavorited ? '取消收藏' : '加入收藏'"
      >
        <svg class="btn-icon" fill="currentColor" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
        </svg>
      </button>
      
      <button 
        @click="$emit('share', song)"
        class="action-btn share-btn"
        title="分享歌曲"
      >
        <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z"></path>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Song, Difficulty, Genre } from '@/types'

interface Props {
  song: Song
  showActions?: boolean
  isFavorited?: boolean
  canEdit?: boolean
  clickable?: boolean
}

interface Emits {
  (e: 'click', song: Song): void
  (e: 'edit', song: Song): void
  (e: 'favorite', song: Song): void
  (e: 'share', song: Song): void
}

const props = withDefaults(defineProps<Props>(), {
  showActions: false,
  isFavorited: false,
  canEdit: false,
  clickable: true
})

const emit = defineEmits<Emits>()

// 格式化方法
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

const formatViewCount = (count: number) => {
  if (count >= 1000000) {
    return (count / 1000000).toFixed(1) + 'M'
  } else if (count >= 1000) {
    return (count / 1000).toFixed(1) + 'K'
  }
  return count.toString()
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24))
  
  if (diffInDays === 0) {
    return '今天'
  } else if (diffInDays === 1) {
    return '昨天'
  } else if (diffInDays < 7) {
    return `${diffInDays}天前`
  } else if (diffInDays < 30) {
    return `${Math.floor(diffInDays / 7)}週前`
  } else if (diffInDays < 365) {
    return `${Math.floor(diffInDays / 30)}月前`
  } else {
    return date.toLocaleDateString('zh-TW', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }
}

// 事件處理
const handleClick = () => {
  if (props.clickable) {
    emit('click', props.song)
  }
}
</script>

<style scoped>
.song-card {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  position: relative;
  border: 1px solid var(--color-gray-200);
}

.song-card:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06);
  transform: translateY(-2px);
  border-color: var(--color-chord-primary);
}

/* 歌曲標題區域 */
.song-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
  gap: 0.75rem;
}

.song-title {
  font-weight: 700;
  font-size: 1.125rem;
  color: var(--color-gray-900);
  line-height: 1.4;
  margin: 0;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.difficulty-badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  white-space: nowrap;
  flex-shrink: 0;
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

/* 歌手名稱 */
.song-artist {
  color: var(--color-gray-600);
  font-size: 0.9rem;
  margin: 0 0 1rem 0;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 歌曲詳細信息 */
.song-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  gap: 0.5rem;
}

.key-info {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.875rem;
}

.key-label {
  color: var(--color-gray-500);
  font-weight: 500;
}

.key-value {
  background-color: var(--color-chord-primary);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-weight: 700;
  font-size: 0.75rem;
}

.capo-info {
  color: var(--color-gray-500);
  font-size: 0.75rem;
  font-weight: 500;
}

.genre-tag {
  background-color: var(--color-gray-100);
  color: var(--color-gray-700);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

/* 評分和統計 */
.song-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  gap: 0.5rem;
}

.rating-section {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.stars {
  display: flex;
  gap: 0.125rem;
}

.star {
  color: var(--color-gray-300);
  font-size: 0.875rem;
  transition: color 0.2s;
}

.star.filled {
  color: var(--color-yellow-400);
}

.rating-value {
  font-weight: 600;
  color: var(--color-gray-800);
  font-size: 0.875rem;
}

.rating-count {
  color: var(--color-gray-500);
  font-size: 0.75rem;
}

.view-count {
  font-size: 0.75rem;
  color: var(--color-gray-500);
  font-weight: 500;
}

/* 歌曲元信息 */
.song-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-gray-100);
  font-size: 0.75rem;
  color: var(--color-gray-400);
}

.meta-left {
  flex: 1;
}

.meta-right {
  flex-shrink: 0;
}

.created-date {
  font-weight: 500;
}

.author {
  font-weight: 600;
  color: var(--color-gray-600);
}

/* 操作按鈕 */
.card-actions {
  position: absolute;
  top: 1rem;
  right: 1rem;
  display: flex;
  gap: 0.5rem;
  opacity: 0;
  transform: translateY(-0.25rem);
  transition: all 0.2s ease-in-out;
}

.song-card:hover .card-actions {
  opacity: 1;
  transform: translateY(0);
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
  background-color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn-icon {
  width: 1rem;
  height: 1rem;
}

.edit-btn {
  color: var(--color-chord-accent);
}

.edit-btn:hover {
  background-color: var(--color-chord-accent);
  color: white;
}

.favorite-btn {
  color: var(--color-gray-400);
}

.favorite-btn:hover {
  color: #ef4444;
}

.favorite-btn.active {
  color: #ef4444;
  background-color: #fef2f2;
}

.share-btn {
  color: var(--color-gray-500);
}

.share-btn:hover {
  background-color: var(--color-chord-primary);
  color: white;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .song-card {
    padding: 1.25rem;
  }
  
  .song-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .song-details {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .song-stats {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .card-actions {
    position: static;
    opacity: 1;
    transform: none;
    justify-content: flex-end;
    margin-top: 0.75rem;
    padding-top: 0.75rem;
    border-top: 1px solid var(--color-gray-100);
  }
}

/* 不可點擊狀態 */
.song-card:not([clickable]) {
  cursor: default;
}

.song-card:not([clickable]):hover {
  transform: none;
  border-color: var(--color-gray-200);
}

/* 緊湊模式 */
.song-card.compact {
  padding: 1rem;
}

.song-card.compact .song-title {
  font-size: 1rem;
  -webkit-line-clamp: 1;
}

.song-card.compact .song-artist {
  margin-bottom: 0.5rem;
}

.song-card.compact .song-details,
.song-card.compact .song-stats {
  margin-bottom: 0.5rem;
}
</style>