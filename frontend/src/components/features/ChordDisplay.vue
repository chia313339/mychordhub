<template>
  <div class="chord-display" :class="{ compact }">
    <!-- 和絃名稱標題 -->
    <div class="chord-header">
      <h3 class="chord-name">{{ chordSymbol }}</h3>
      
      <!-- 顯示模式切換按鈕 -->
      <div class="display-mode-toggle">
        <button
          :class="{ active: displayMode === 'text' }"
          @click="setDisplayMode('text')"
          class="mode-btn"
          title="文字模式"
        >
          文字
        </button>
        <button
          :class="{ active: displayMode === 'diagram' }"
          @click="setDisplayMode('diagram')"
          class="mode-btn"
          title="六線譜模式"
        >
          圖示
        </button>
      </div>
    </div>

    <!-- 和絃內容顯示 -->
    <div class="chord-content">
      <!-- 文字模式 -->
      <div v-if="displayMode === 'text'" class="text-mode">
        <div class="chord-info">
          <div class="chord-detail">
            <span class="label">根音:</span>
            <span class="value">{{ chordInfo?.root || 'N/A' }}</span>
          </div>
          
          <div class="chord-detail">
            <span class="label">類型:</span>
            <span class="value">{{ getChordQualityText(chordInfo?.quality) }}</span>
          </div>
          
          <div v-if="chordInfo?.extension" class="chord-detail">
            <span class="label">延伸:</span>
            <span class="value">{{ chordInfo.extension }}</span>
          </div>
          
          <div v-if="chordInfo?.bass" class="chord-detail">
            <span class="label">低音:</span>
            <span class="value">{{ chordInfo.bass }}</span>
          </div>
        </div>

        <!-- 音符組成 -->
        <div v-if="noteComposition" class="note-composition">
          <h4 class="composition-title">音符組成</h4>
          <div class="notes-grid">
            <span 
              v-for="note in compositionNotes" 
              :key="note.role"
              class="note-item"
              :title="note.role"
            >
              {{ note.note }}
            </span>
          </div>
        </div>
      </div>

      <!-- 六線譜圖示模式 -->
      <div v-if="displayMode === 'diagram'" class="diagram-mode">
        <div class="chord-diagram" ref="chordDiagramRef">
          <!-- 六線譜圖形將在這裡渲染 -->
          <ChordDiagramSvg
            :fingering="selectedFingering"
            :options="diagramOptions"
            @fingering-change="handleFingeringChange"
          />
        </div>

        <!-- 指法選擇器 -->
        <div v-if="fingeringPatterns && fingeringPatterns.length > 1" class="fingering-selector">
          <label class="selector-label">指法選擇:</label>
          <select 
            v-model="selectedFingeringId" 
            @change="handleFingeringChange"
            class="fingering-select"
          >
            <option
              v-for="pattern in fingeringPatterns"
              :key="pattern.id"
              :value="pattern.id"
            >
              {{ pattern.name }} ({{ getDifficultyText(pattern.difficulty) }})
            </option>
          </select>
        </div>

        <!-- 指法詳細信息 -->
        <div v-if="selectedFingering" class="fingering-details">
          <div class="fingering-info">
            <div class="info-item">
              <span class="info-label">品位:</span>
              <span class="info-value">{{ selectedFingering.frets.join('-') }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">手指:</span>
              <span class="info-value">{{ selectedFingering.fingers.join('-') }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">難度:</span>
              <span class="info-value difficulty-badge" :class="getDifficultyClass(selectedFingering.difficulty)">
                {{ getDifficultyText(selectedFingering.difficulty) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 載入狀態 -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <span>載入和絃資料...</span>
      </div>

      <!-- 錯誤狀態 -->
      <div v-if="error" class="error-state">
        <div class="error-icon">⚠️</div>
        <span class="error-message">{{ error }}</span>
        <button @click="retry" class="retry-btn">重試</button>
      </div>

      <!-- 無資料狀態 -->
      <div v-if="!loading && !error && !chordInfo && !fingeringPatterns?.length" class="empty-state">
        <div class="empty-icon">🎸</div>
        <span class="empty-message">無法找到和絃 "{{ chordSymbol }}" 的資料</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import type { ChordInfo, FingeringPattern, NoteComposition, ChordQuality, TabRenderOptions } from '@/types/music'
import ChordDiagramSvg from './ChordDiagramSvg.vue'

interface Props {
  chordSymbol: string
  displayMode?: 'text' | 'diagram'
  compact?: boolean
  interactive?: boolean
  size?: 'small' | 'medium' | 'large'
}

interface Emits {
  (e: 'mode-change', mode: 'text' | 'diagram'): void
  (e: 'fingering-change', fingering: FingeringPattern): void
  (e: 'chord-click', chord: string): void
}

const props = withDefaults(defineProps<Props>(), {
  displayMode: 'text',
  compact: false,
  interactive: true,
  size: 'medium'
})

const emit = defineEmits<Emits>()

// 響應式狀態
const currentDisplayMode = ref(props.displayMode)
const loading = ref(false)
const error = ref<string>('')
const chordInfo = ref<ChordInfo | null>(null)
const fingeringPatterns = ref<FingeringPattern[]>([])
const noteComposition = ref<NoteComposition | null>(null)
const selectedFingeringId = ref<string>('')
const chordDiagramRef = ref<HTMLElement>()

// 計算屬性
const displayMode = computed({
  get: () => currentDisplayMode.value,
  set: (value) => {
    currentDisplayMode.value = value
    emit('mode-change', value)
  }
})

const selectedFingering = computed(() => {
  if (!fingeringPatterns.value || !selectedFingeringId.value) return null
  return fingeringPatterns.value.find(p => p.id === selectedFingeringId.value) || fingeringPatterns.value[0]
})

const compositionNotes = computed(() => {
  if (!noteComposition.value) return []
  
  const notes = []
  if (noteComposition.value.root) notes.push({ note: noteComposition.value.root, role: '根音' })
  if (noteComposition.value.third) notes.push({ note: noteComposition.value.third, role: '三音' })
  if (noteComposition.value.fifth) notes.push({ note: noteComposition.value.fifth, role: '五音' })
  if (noteComposition.value.seventh) notes.push({ note: noteComposition.value.seventh, role: '七音' })
  if (noteComposition.value.ninth) notes.push({ note: noteComposition.value.ninth, role: '九音' })
  if (noteComposition.value.eleventh) notes.push({ note: noteComposition.value.eleventh, role: '十一音' })
  if (noteComposition.value.thirteenth) notes.push({ note: noteComposition.value.thirteenth, role: '十三音' })
  
  return notes
})

const diagramOptions = computed((): TabRenderOptions => ({
  frets: 5,
  showFretNumbers: true,
  showFingers: true,
  showStringNames: true,
  width: props.size === 'small' ? 120 : props.size === 'large' ? 200 : 160,
  height: props.size === 'small' ? 150 : props.size === 'large' ? 250 : 200
}))

// 方法
const setDisplayMode = (mode: 'text' | 'diagram') => {
  displayMode.value = mode
}

const parseChordSymbol = (symbol: string): ChordInfo | null => {
  try {
    // 簡單的和絃解析邏輯
    const chordPattern = /^([A-G][b#]?)([^\/]*)(\/([A-G][b#]?))?$/
    const match = symbol.match(chordPattern)
    
    if (!match) return null

    const [, root, qualityExt, , bass] = match
    
    // 解析和絃品質和延伸
    let quality: ChordQuality = 'maj'
    let extension = ''
    
    if (qualityExt) {
      if (qualityExt.includes('m') && !qualityExt.includes('maj')) {
        quality = 'min'
        extension = qualityExt.replace('m', '')
      } else if (qualityExt.includes('dim')) {
        quality = 'dim'
        extension = qualityExt.replace('dim', '')
      } else if (qualityExt.includes('aug')) {
        quality = 'aug'
        extension = qualityExt.replace('aug', '')
      } else if (qualityExt.includes('sus2')) {
        quality = 'sus2'
        extension = qualityExt.replace('sus2', '')
      } else if (qualityExt.includes('sus4')) {
        quality = 'sus4'
        extension = qualityExt.replace('sus4', '')
      } else if (qualityExt.includes('maj7')) {
        quality = 'maj7'
        extension = qualityExt.replace('maj7', '')
      } else if (qualityExt.includes('7')) {
        quality = '7'
        extension = qualityExt.replace('7', '')
      }
    }

    return {
      symbol,
      root: root as any,
      quality,
      extension: extension || undefined,
      bass: bass as any || undefined
    }
  } catch (err) {
    console.error('Error parsing chord symbol:', err)
    return null
  }
}

const loadChordData = async () => {
  if (!props.chordSymbol) return

  loading.value = true
  error.value = ''

  try {
    // 解析和絃符號
    const parsed = parseChordSymbol(props.chordSymbol)
    if (parsed) {
      chordInfo.value = parsed
    }

    // 這裡應該調用 API 獲取和絃數據
    // 暫時使用模擬數據
    await new Promise(resolve => setTimeout(resolve, 300))
    
    // 模擬指法數據
    fingeringPatterns.value = generateMockFingeringPatterns(props.chordSymbol)
    
    // 模擬音符組成數據
    noteComposition.value = generateMockNoteComposition(chordInfo.value)

    // 設置預設指法
    if (fingeringPatterns.value.length > 0) {
      const defaultPattern = fingeringPatterns.value.find(p => p.is_default) || fingeringPatterns.value[0]
      selectedFingeringId.value = defaultPattern.id
    }

  } catch (err) {
    error.value = err instanceof Error ? err.message : '載入和絃資料時發生錯誤'
  } finally {
    loading.value = false
  }
}

const generateMockFingeringPatterns = (symbol: string): FingeringPattern[] => {
  // 基本模擬指法數據
  const patterns = [
    {
      id: `${symbol}-1`,
      name: '開放位置',
      frets: [3, 2, 0, 1, 0, 0],
      fingers: [3, 2, 0, 1, 0, 0],
      difficulty: 1,
      is_default: true
    },
    {
      id: `${symbol}-2`,
      name: '封閉位置',
      frets: [3, 5, 5, 4, 3, 3],
      fingers: [1, 3, 4, 2, 1, 1],
      difficulty: 3,
      is_default: false
    }
  ]
  
  return patterns
}

const generateMockNoteComposition = (chord: ChordInfo | null): NoteComposition | null => {
  if (!chord) return null
  
  return {
    root: chord.root,
    third: chord.quality === 'min' ? 'Eb' as any : 'E' as any,
    fifth: 'G' as any,
    seventh: chord.quality === 'maj7' || chord.quality === '7' ? 'B' as any : undefined
  }
}

const getChordQualityText = (quality?: ChordQuality) => {
  const qualityTexts = {
    maj: '大三和絃',
    min: '小三和絃',
    dim: '減三和絃',
    aug: '增三和絃',
    sus2: '掛二和絃',
    sus4: '掛四和絃',
    '7': '屬七和絃',
    maj7: '大七和絃',
    min7: '小七和絃',
    dim7: '減七和絃',
    aug7: '增七和絃',
    '9': '九和絃',
    '11': '十一和絃',
    '13': '十三和絃'
  }
  return qualityTexts[quality || 'maj'] || '未知'
}

const getDifficultyText = (difficulty: number) => {
  if (difficulty <= 1) return '簡單'
  if (difficulty <= 2) return '普通'
  if (difficulty <= 3) return '困難'
  return '專家'
}

const getDifficultyClass = (difficulty: number) => {
  if (difficulty <= 1) return 'easy'
  if (difficulty <= 2) return 'medium'
  if (difficulty <= 3) return 'hard'
  return 'expert'
}

const handleFingeringChange = () => {
  if (selectedFingering.value) {
    emit('fingering-change', selectedFingering.value)
  }
}

const retry = () => {
  loadChordData()
}

// 監聽器
watch(() => props.chordSymbol, () => {
  loadChordData()
}, { immediate: true })

watch(() => props.displayMode, (newMode) => {
  currentDisplayMode.value = newMode
})

// 生命週期
onMounted(() => {
  loadChordData()
})
</script>

<style scoped>
.chord-display {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  padding: 1.5rem;
  border: 1px solid var(--color-gray-200);
  transition: all 0.2s ease-in-out;
}

.chord-display:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06);
}

.chord-display.compact {
  padding: 1rem;
}

/* 和絃標題區域 */
.chord-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  gap: 1rem;
}

.chord-name {
  font-weight: 700;
  font-size: 1.5rem;
  color: var(--color-chord-primary);
  margin: 0;
  flex: 1;
}

.display-mode-toggle {
  display: flex;
  background-color: var(--color-gray-100);
  border-radius: 0.5rem;
  padding: 0.25rem;
  gap: 0.25rem;
}

.mode-btn {
  padding: 0.5rem 0.75rem;
  border: none;
  border-radius: 0.375rem;
  background: transparent;
  color: var(--color-gray-600);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.mode-btn:hover {
  background-color: var(--color-gray-200);
}

.mode-btn.active {
  background-color: var(--color-chord-primary);
  color: white;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* 和絃內容區域 */
.chord-content {
  min-height: 200px;
  position: relative;
}

/* 文字模式樣式 */
.text-mode {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.chord-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.chord-detail {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.chord-detail .label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-gray-600);
}

.chord-detail .value {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-gray-900);
  background-color: var(--color-gray-50);
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
  border: 1px solid var(--color-gray-200);
}

.note-composition {
  background-color: var(--color-gray-50);
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid var(--color-gray-200);
}

.composition-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-gray-800);
  margin: 0 0 0.75rem 0;
}

.notes-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.note-item {
  background-color: var(--color-chord-primary);
  color: white;
  padding: 0.375rem 0.75rem;
  border-radius: 0.25rem;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: help;
}

/* 六線譜模式樣式 */
.diagram-mode {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
}

.chord-diagram {
  display: flex;
  justify-content: center;
  min-height: 200px;
  align-items: center;
}

.fingering-selector {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  max-width: 300px;
}

.selector-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-gray-700);
  white-space: nowrap;
}

.fingering-select {
  flex: 1;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-gray-300);
  border-radius: 0.375rem;
  background-color: white;
  font-size: 0.875rem;
  cursor: pointer;
}

.fingering-select:focus {
  outline: none;
  border-color: var(--color-chord-primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.fingering-details {
  background-color: var(--color-gray-50);
  padding: 1rem;
  border-radius: 0.5rem;
  width: 100%;
  max-width: 400px;
}

.fingering-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-gray-600);
}

.info-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-gray-900);
  font-family: monospace;
}

.difficulty-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  font-family: sans-serif;
}

.difficulty-badge.easy {
  background-color: #dcfce7;
  color: #166534;
}

.difficulty-badge.medium {
  background-color: #fef3c7;
  color: #92400e;
}

.difficulty-badge.hard {
  background-color: #fed7c3;
  color: #c2410c;
}

.difficulty-badge.expert {
  background-color: #fecaca;
  color: #dc2626;
}

/* 載入狀態 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: var(--color-gray-600);
  gap: 1rem;
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid var(--color-gray-200);
  border-top: 3px solid var(--color-chord-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 錯誤狀態 */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 1rem;
}

.error-icon {
  font-size: 2rem;
}

.error-message {
  color: var(--color-gray-600);
  text-align: center;
  font-size: 0.875rem;
}

.retry-btn {
  padding: 0.5rem 1rem;
  background-color: var(--color-chord-primary);
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.retry-btn:hover {
  background-color: var(--color-chord-primary-dark);
}

/* 空狀態 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 1rem;
}

.empty-icon {
  font-size: 2rem;
  opacity: 0.6;
}

.empty-message {
  color: var(--color-gray-500);
  text-align: center;
  font-size: 0.875rem;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .chord-display {
    padding: 1.25rem;
  }
  
  .chord-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
  
  .chord-name {
    font-size: 1.25rem;
  }
  
  .chord-info {
    grid-template-columns: 1fr;
  }
  
  .fingering-selector {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .selector-label {
    white-space: normal;
  }
  
  .fingering-select {
    width: 100%;
  }
}

/* 緊湊模式調整 */
.chord-display.compact .chord-header {
  margin-bottom: 1rem;
}

.chord-display.compact .chord-name {
  font-size: 1.25rem;
}

.chord-display.compact .chord-content {
  min-height: 150px;
}

.chord-display.compact .text-mode {
  gap: 1rem;
}
</style>