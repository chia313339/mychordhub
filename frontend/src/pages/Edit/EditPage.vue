<template>
  <div class="song-edit-page">
    <!-- 頁面標題欄 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">
            {{ isNewSong ? '創建新歌曲' : '編輯歌曲' }}
          </h1>
          <div class="breadcrumb">
            <router-link to="/" class="breadcrumb-link">首頁</router-link>
            <span class="breadcrumb-separator">/</span>
            <router-link to="/browse" class="breadcrumb-link">瀏覽</router-link>
            <span class="breadcrumb-separator">/</span>
            <span class="breadcrumb-current">{{ isNewSong ? '創建' : '編輯' }}</span>
          </div>
        </div>
        
        <div class="header-actions">
          <button
            @click="previewSong"
            :disabled="!isFormValid || saving"
            class="action-btn secondary"
          >
            預覽
          </button>
          
          <button
            @click="saveSong"
            :disabled="!isFormValid || saving"
            class="action-btn primary"
          >
            <span v-if="saving" class="loading-spinner"></span>
            {{ saving ? '儲存中...' : (isNewSong ? '創建歌曲' : '儲存變更') }}
          </button>
        </div>
      </div>
    </div>

    <!-- 編輯表單 -->
    <div class="edit-form-container">
      <form @submit.prevent="saveSong" class="song-form">
        <!-- 基本信息區塊 -->
        <div class="form-section">
          <div class="section-header">
            <h2 class="section-title">基本信息</h2>
            <p class="section-description">設定歌曲的基本資料</p>
          </div>
          
          <div class="form-grid">
            <div class="form-group col-span-2">
              <label class="form-label" for="title">
                歌曲標題 <span class="required">*</span>
              </label>
              <input
                id="title"
                v-model="songData.title"
                type="text"
                class="form-input"
                :class="{ 'error': errors.title }"
                placeholder="輸入歌曲標題"
                required
              />
              <span v-if="errors.title" class="error-message">{{ errors.title }}</span>
            </div>
            
            <div class="form-group col-span-2">
              <label class="form-label" for="artist">
                歌手/創作者 <span class="required">*</span>
              </label>
              <input
                id="artist"
                v-model="songData.artist"
                type="text"
                class="form-input"
                :class="{ 'error': errors.artist }"
                placeholder="輸入歌手或創作者名稱"
                required
              />
              <span v-if="errors.artist" class="error-message">{{ errors.artist }}</span>
            </div>
            
            <div class="form-group">
              <label class="form-label" for="genre">曲風</label>
              <select
                id="genre"
                v-model="songData.genre"
                class="form-select"
              >
                <option value="">請選擇曲風</option>
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
            
            <div class="form-group">
              <label class="form-label" for="difficulty">難度</label>
              <select
                id="difficulty"
                v-model="songData.difficulty"
                class="form-select"
              >
                <option value="">請選擇難度</option>
                <option value="beginner">初學</option>
                <option value="intermediate">中級</option>
                <option value="advanced">進階</option>
                <option value="expert">專家</option>
              </select>
            </div>
            
            <div class="form-group">
              <label class="form-label" for="bpm">節拍 (BPM)</label>
              <input
                id="bpm"
                v-model.number="songData.bpm"
                type="number"
                min="30"
                max="200"
                class="form-input"
                placeholder="120"
              />
            </div>
            
            <div class="form-group">
              <label class="form-label">
                <input
                  v-model="songData.is_public"
                  type="checkbox"
                  class="form-checkbox"
                />
                公開歌曲
              </label>
              <p class="form-help">勾選後其他用戶可以瀏覽此歌曲</p>
            </div>
            
            <div class="form-group col-span-2">
              <label class="form-label" for="description">歌曲描述</label>
              <textarea
                id="description"
                v-model="songData.description"
                rows="3"
                class="form-textarea"
                placeholder="簡短描述這首歌曲的特色或背景..."
              ></textarea>
            </div>
          </div>
        </div>

        <!-- 調性設定區塊 -->
        <div class="form-section">
          <div class="section-header">
            <h2 class="section-title">調性設定</h2>
            <p class="section-description">設定歌曲的調性和變調夾位置</p>
          </div>
          
          <KeyCapoSelector
            v-model:model-key="songData.key_signature"
            v-model:model-capo="songData.capo_position"
            :show-title="false"
            :show-preview="true"
            :show-chord-preview="true"
            @change="handleKeyCapoChange"
          />
        </div>

        <!-- 歌詞編輯區塊 -->
        <div class="form-section">
          <div class="section-header">
            <h2 class="section-title">歌詞與和絃</h2>
            <p class="section-description">編輯歌詞並插入和絃標記</p>
          </div>
          
          <LyricsEditor
            v-model="lyricsContent"
            v-model:chord-positions="chordPositions"
            :auto-save="true"
            @content-change="handleLyricsChange"
            @chord-change="handleChordChange"
          />
        </div>

        <!-- 和絃管理區塊 -->
        <div v-if="detectedChords.length > 0" class="form-section">
          <div class="section-header">
            <h2 class="section-title">和絃管理</h2>
            <p class="section-description">管理歌曲中使用的和絃</p>
          </div>
          
          <div class="chord-management">
            <div class="chord-list">
              <h3 class="chord-list-title">已使用的和絃 ({{ detectedChords.length }})</h3>
              <div class="chord-grid">
                <div
                  v-for="chord in detectedChords"
                  :key="chord"
                  class="chord-item"
                >
                  <ChordDisplay
                    :chord-symbol="chord"
                    :compact="true"
                    :display-mode="chordDisplayMode"
                    @chord-click="selectChord(chord)"
                  />
                </div>
              </div>
            </div>
            
            <div class="chord-tools">
              <h3 class="tools-title">和絃工具</h3>
              
              <!-- 和絃轉調器 -->
              <ChordTransposer
                :chords="detectedChords"
                :original-key="songData.key_signature"
                :compact="true"
                :auto-apply="false"
                @transpose="handleChordTranspose"
              />
            </div>
          </div>
        </div>

        <!-- 預覽區塊 -->
        <div v-if="showPreview" class="form-section">
          <div class="section-header">
            <h2 class="section-title">歌曲預覽</h2>
            <p class="section-description">預覽最終效果</p>
          </div>
          
          <div class="song-preview">
            <div class="preview-header">
              <div class="preview-info">
                <h3 class="preview-title">{{ songData.title || '未命名歌曲' }}</h3>
                <p class="preview-artist">{{ songData.artist || '未知歌手' }}</p>
                <div class="preview-meta">
                  <span v-if="songData.key_signature" class="meta-item">
                    Key: {{ songData.key_signature }}
                  </span>
                  <span v-if="songData.capo_position" class="meta-item">
                    Capo: {{ songData.capo_position }}
                  </span>
                  <span v-if="songData.bpm" class="meta-item">
                    BPM: {{ songData.bpm }}
                  </span>
                </div>
              </div>
            </div>
            
            <div class="preview-content">
              <div class="lyrics-display">
                <!-- 這裡會顯示格式化的歌詞和和絃 -->
                <div
                  v-for="(line, index) in previewLines"
                  :key="index"
                  class="preview-line"
                >
                  <div v-if="line.chords.length > 0" class="chord-line">
                    <span
                      v-for="chord in line.chords"
                      :key="chord.id"
                      class="chord-marker"
                      :style="{ left: `${chord.position * 0.6}ch` }"
                    >
                      {{ chord.symbol }}
                    </span>
                  </div>
                  <div class="lyric-text">{{ line.text }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </form>
    </div>

    <!-- 錯誤提示 -->
    <div v-if="error" class="error-toast">
      <span class="error-icon">⚠️</span>
      <span class="error-text">{{ error }}</span>
      <button @click="clearError" class="error-dismiss">×</button>
    </div>

    <!-- 成功提示 -->
    <div v-if="successMessage" class="success-toast">
      <span class="success-icon">✅</span>
      <span class="success-text">{{ successMessage }}</span>
      <button @click="clearSuccess" class="success-dismiss">×</button>
    </div>

    <!-- 載入遮罩 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner large"></div>
        <span class="loading-text">{{ loadingText }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import type { CreateSongData, UpdateSongData, ChordPosition, Note } from '@/types/music'
import KeyCapoSelector from '@/components/features/KeyCapoSelector.vue'
import LyricsEditor from '@/components/features/LyricsEditor.vue'
import ChordDisplay from '@/components/features/ChordDisplay.vue'
import ChordTransposer from '@/components/features/ChordTransposer.vue'

interface Props {
  id?: string
}

const props = defineProps<Props>()
const router = useRouter()

// 響應式狀態
const songData = ref<CreateSongData>({
  title: '',
  artist: '',
  key_signature: 'C',
  capo_position: 0,
  bpm: 120,
  difficulty: 'beginner',
  genre: 'pop',
  description: '',
  is_public: true
})

const lyricsContent = ref('')
const chordPositions = ref<ChordPosition[]>([])
const detectedChords = ref<string[]>([])
const chordDisplayMode = ref<'text' | 'diagram'>('text')
const showPreview = ref(false)
const loading = ref(false)
const saving = ref(false)
const loadingText = ref('')
const error = ref('')
const successMessage = ref('')

// 表單驗證錯誤
const errors = ref<Record<string, string>>({})

// 計算屬性
const isNewSong = computed(() => !props.id)

const isFormValid = computed(() => {
  return songData.value.title.trim() !== '' && 
         songData.value.artist.trim() !== '' &&
         Object.keys(errors.value).length === 0
})

const previewLines = computed(() => {
  const lines = lyricsContent.value.split('\n')
  return lines.map(line => {
    const chords: Array<{ symbol: string; position: number; id: string }> = []
    let cleanText = line
    
    // 提取和絃
    const chordMatches = Array.from(line.matchAll(/\[([^\]]+)\]/g))
    
    for (let i = chordMatches.length - 1; i >= 0; i--) {
      const match = chordMatches[i]
      const chordSymbol = match[1]
      const position = match.index || 0
      
      chords.unshift({
        symbol: chordSymbol,
        position: position,
        id: `preview-chord-${Math.random().toString(36).substr(2, 9)}`
      })
      
      cleanText = cleanText.substring(0, position) + cleanText.substring(position + match[0].length)
    }
    
    return {
      text: cleanText,
      chords: chords.sort((a, b) => a.position - b.position)
    }
  })
})

// 方法
const validateForm = () => {
  const newErrors: Record<string, string> = {}
  
  if (!songData.value.title.trim()) {
    newErrors.title = '歌曲標題為必填項目'
  } else if (songData.value.title.length > 100) {
    newErrors.title = '歌曲標題不能超過100個字元'
  }
  
  if (!songData.value.artist.trim()) {
    newErrors.artist = '歌手名稱為必填項目'
  } else if (songData.value.artist.length > 50) {
    newErrors.artist = '歌手名稱不能超過50個字元'
  }
  
  errors.value = newErrors
  return Object.keys(newErrors).length === 0
}

const handleKeyCapoChange = (data: { key: Note; capo: number; effectiveKey: Note }) => {
  songData.value.key_signature = data.key
  songData.value.capo_position = data.capo
}

const handleLyricsChange = (data: { lyrics: string; chords: ChordPosition[] }) => {
  lyricsContent.value = data.lyrics
  chordPositions.value = data.chords
}

const handleChordChange = (chords: string[]) => {
  detectedChords.value = chords
}

const handleChordTranspose = (data: { semitones: number; chords: any[]; targetKey: Note }) => {
  // 更新歌曲調性
  songData.value.key_signature = data.targetKey
  
  // 更新歌詞中的和絃
  let newLyrics = lyricsContent.value
  
  data.chords.forEach(chordMapping => {
    if (!chordMapping.error) {
      const oldPattern = new RegExp(`\\[${chordMapping.original}\\]`, 'g')
      newLyrics = newLyrics.replace(oldPattern, `[${chordMapping.transposed}]`)
    }
  })
  
  lyricsContent.value = newLyrics
}

const selectChord = (chord: string) => {
  // 選擇和絃的邏輯，可以用於編輯或顯示詳細信息
  console.log('Selected chord:', chord)
}

const previewSong = () => {
  if (!validateForm()) {
    error.value = '請先修正表單錯誤'
    return
  }
  
  showPreview.value = !showPreview.value
}

const saveSong = async () => {
  if (!validateForm()) {
    error.value = '請先修正表單錯誤'
    return
  }
  
  saving.value = true
  error.value = ''
  
  try {
    const songPayload = {
      ...songData.value,
      lyrics: lyricsContent.value,
      chord_positions: chordPositions.value
    }
    
    if (isNewSong.value) {
      loadingText.value = '創建歌曲中...'
      // 創建新歌曲的 API 調用
      await createSong(songPayload)
      successMessage.value = '歌曲創建成功！'
      
      // 跳轉到歌曲詳細頁面
      setTimeout(() => {
        router.push('/browse') // 或跳轉到新創建的歌曲頁面
      }, 2000)
    } else {
      loadingText.value = '儲存變更中...'
      // 更新現有歌曲的 API 調用
      await updateSong(props.id!, songPayload)
      successMessage.value = '歌曲更新成功！'
    }
    
  } catch (err) {
    error.value = err instanceof Error ? err.message : '儲存失敗，請稍後再試'
  } finally {
    saving.value = false
    loading.value = false
  }
}

const createSong = async (data: any) => {
  // 模擬 API 調用
  await new Promise(resolve => setTimeout(resolve, 1500))
  console.log('Creating song:', data)
}

const updateSong = async (id: string, data: any) => {
  // 模擬 API 調用
  await new Promise(resolve => setTimeout(resolve, 1500))
  console.log('Updating song:', id, data)
}

const loadExistingSong = async (id: string) => {
  loading.value = true
  loadingText.value = '載入歌曲資料...'
  
  try {
    // 模擬 API 調用載入現有歌曲
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 這裡應該從 API 載入歌曲資料
    const mockSong = {
      title: '測試歌曲',
      artist: '測試歌手',
      key_signature: 'G' as Note,
      capo_position: 2,
      bpm: 120,
      difficulty: 'intermediate' as any,
      genre: 'pop' as any,
      description: '這是一首測試歌曲',
      is_public: true
    }
    
    songData.value = mockSong
    lyricsContent.value = '[G]今天天氣真好 [Am]陽光普照\n[C]讓我們一起 [D]唱首歌吧\n\n[G]這是副歌部分 [Em]很簡單\n[Am]大家一起來 [D]跟著唱 [G]'
    
  } catch (err) {
    error.value = '載入歌曲失敗，請稍後再試'
  } finally {
    loading.value = false
  }
}

const clearError = () => {
  error.value = ''
}

const clearSuccess = () => {
  successMessage.value = ''
}

// 監聽器
watch(() => songData.value.title, () => {
  if (errors.value.title && songData.value.title.trim()) {
    delete errors.value.title
  }
})

watch(() => songData.value.artist, () => {
  if (errors.value.artist && songData.value.artist.trim()) {
    delete errors.value.artist
  }
})

// 生命週期
onMounted(() => {
  if (!isNewSong.value && props.id) {
    loadExistingSong(props.id)
  }
})
</script>

<style scoped>
.song-edit-page {
  min-height: 100vh;
  background-color: var(--color-gray-50);
}

/* 頁面標題欄 */
.page-header {
  background: white;
  border-bottom: 1px solid var(--color-gray-200);
  padding: 1.5rem 0;
  position: sticky;
  top: 0;
  z-index: 50;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
}

.header-left {
  flex: 1;
}

.page-title {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--color-gray-900);
  margin: 0 0 0.5rem 0;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.breadcrumb-link {
  color: var(--color-chord-primary);
  text-decoration: none;
  transition: color 0.2s;
}

.breadcrumb-link:hover {
  color: var(--color-chord-primary-dark);
}

.breadcrumb-separator {
  color: var(--color-gray-400);
}

.breadcrumb-current {
  color: var(--color-gray-600);
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  flex-shrink: 0;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  white-space: nowrap;
}

.action-btn.primary {
  background-color: var(--color-chord-primary);
  color: white;
}

.action-btn.primary:hover:not(:disabled) {
  background-color: var(--color-chord-primary-dark);
}

.action-btn.secondary {
  background-color: var(--color-gray-100);
  color: var(--color-gray-700);
  border: 1px solid var(--color-gray-300);
}

.action-btn.secondary:hover:not(:disabled) {
  background-color: var(--color-gray-200);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* 編輯表單容器 */
.edit-form-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.song-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* 表單區塊 */
.form-section {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  border: 1px solid var(--color-gray-200);
  overflow: hidden;
}

.section-header {
  padding: 1.5rem 1.5rem 1rem 1.5rem;
  border-bottom: 1px solid var(--color-gray-100);
}

.section-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-gray-900);
  margin: 0 0 0.5rem 0;
}

.section-description {
  font-size: 0.875rem;
  color: var(--color-gray-600);
  margin: 0;
  line-height: 1.5;
}

/* 表單網格 */
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  padding: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group.col-span-2 {
  grid-column: span 2;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-gray-700);
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.required {
  color: #dc2626;
}

.form-input,
.form-select,
.form-textarea {
  padding: 0.75rem;
  border: 2px solid var(--color-gray-200);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: border-color 0.2s;
  background: white;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--color-chord-primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-input.error,
.form-select.error,
.form-textarea.error {
  border-color: #dc2626;
}

.form-checkbox {
  margin-right: 0.5rem;
}

.form-help {
  font-size: 0.75rem;
  color: var(--color-gray-500);
  margin: 0.25rem 0 0 0;
}

.error-message {
  font-size: 0.75rem;
  color: #dc2626;
  margin-top: 0.25rem;
}

/* 和絃管理 */
.chord-management {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  padding: 1.5rem;
}

.chord-list-title,
.tools-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-gray-800);
  margin: 0 0 1rem 0;
}

.chord-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.chord-item {
  border: 1px solid var(--color-gray-200);
  border-radius: 0.5rem;
  overflow: hidden;
}

/* 歌曲預覽 */
.song-preview {
  background-color: var(--color-gray-50);
  border-radius: 0.5rem;
  margin: 1.5rem;
  overflow: hidden;
}

.preview-header {
  background: white;
  padding: 1.5rem;
  border-bottom: 1px solid var(--color-gray-200);
}

.preview-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-gray-900);
  margin: 0 0 0.5rem 0;
}

.preview-artist {
  font-size: 1.125rem;
  color: var(--color-gray-600);
  margin: 0 0 1rem 0;
}

.preview-meta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.meta-item {
  background-color: var(--color-chord-primary);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.preview-content {
  padding: 1.5rem;
}

.lyrics-display {
  background: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  border: 1px solid var(--color-gray-200);
}

.preview-line {
  position: relative;
  margin-bottom: 1.5rem;
  min-height: 2rem;
}

.chord-line {
  position: relative;
  height: 1.5rem;
  margin-bottom: 0.25rem;
}

.chord-marker {
  position: absolute;
  background-color: var(--color-chord-primary);
  color: white;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  transform: translateX(-50%);
  white-space: nowrap;
  z-index: 1;
}

.lyric-text {
  font-size: 0.875rem;
  line-height: 1.6;
  color: var(--color-gray-900);
  white-space: pre-wrap;
}

/* 提示訊息 */
.error-toast,
.success-toast {
  position: fixed;
  top: 1rem;
  right: 1rem;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 0.75rem;
  z-index: 100;
  max-width: 400px;
  animation: slideIn 0.3s ease-out;
}

.error-toast {
  background-color: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.success-toast {
  background-color: #f0fdf4;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.error-icon,
.success-icon {
  flex-shrink: 0;
  font-size: 1.25rem;
}

.error-text,
.success-text {
  flex: 1;
  font-size: 0.875rem;
  font-weight: 500;
}

.error-dismiss,
.success-dismiss {
  background: none;
  border: none;
  color: currentColor;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0;
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.error-dismiss:hover,
.success-dismiss:hover {
  opacity: 1;
}

/* 載入遮罩 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  background: white;
  padding: 2rem;
  border-radius: 0.75rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.loading-spinner.large {
  width: 3rem;
  height: 3rem;
  border: 4px solid var(--color-gray-200);
  border-top: 4px solid var(--color-chord-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  font-size: 0.875rem;
  color: var(--color-gray-600);
  font-weight: 500;
}

/* 動畫 */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 響應式設計 */
@media (max-width: 1024px) {
  .chord-management {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 1rem 0;
  }
  
  .header-content {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .header-actions {
    justify-content: stretch;
  }
  
  .action-btn {
    flex: 1;
    justify-content: center;
  }
  
  .edit-form-container {
    padding: 1rem;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
    padding: 1rem;
  }
  
  .form-group.col-span-2 {
    grid-column: span 1;
  }
  
  .section-header {
    padding: 1rem;
  }
  
  .chord-grid {
    grid-template-columns: 1fr;
  }
  
  .preview-meta {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .error-toast,
  .success-toast {
    top: auto;
    bottom: 1rem;
    left: 1rem;
    right: 1rem;
    max-width: none;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.5rem;
  }
  
  .breadcrumb {
    font-size: 0.75rem;
  }
  
  .form-grid {
    padding: 0.75rem;
  }
  
  .preview-content,
  .lyrics-display {
    padding: 1rem;
  }
}
</style>