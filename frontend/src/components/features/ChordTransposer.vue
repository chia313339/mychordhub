<template>
  <div class="chord-transposer" :class="{ compact, vertical: layout === 'vertical' }">
    <!-- 標題區域 -->
    <div v-if="showTitle" class="transposer-header">
      <h3 class="transposer-title">和絃轉調器</h3>
      <p v-if="showDescription" class="transposer-description">
        自動轉換歌曲中的所有和絃到指定調性
      </p>
    </div>

    <!-- 轉調控制區域 -->
    <div class="transpose-controls">
      <!-- 轉調方向按鈕 -->
      <div class="transpose-buttons">
        <button
          @click="transposeDown"
          :disabled="disabled || loading"
          class="transpose-btn down"
          title="降低半音"
        >
          <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"/>
          </svg>
          <span>降調</span>
        </button>

        <!-- 轉調顯示 -->
        <div class="transpose-display">
          <div class="semitone-indicator">
            <span class="semitone-value">{{ semitoneOffset >= 0 ? '+' : '' }}{{ semitoneOffset }}</span>
            <span class="semitone-unit">半音</span>
          </div>
          <div v-if="originalKey && targetKey" class="key-display">
            <span class="original-key">{{ originalKey }}</span>
            <span class="arrow">→</span>
            <span class="target-key">{{ targetKey }}</span>
          </div>
        </div>

        <button
          @click="transposeUp"
          :disabled="disabled || loading"
          class="transpose-btn up"
          title="升高半音"
        >
          <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"/>
          </svg>
          <span>升調</span>
        </button>
      </div>

      <!-- 精確轉調控制 -->
      <div v-if="showAdvancedControls" class="advanced-controls">
        <div class="control-group">
          <label class="control-label">目標調性:</label>
          <select 
            v-model="selectedTargetKey"
            @change="transposeToKey"
            class="key-select"
            :disabled="disabled || loading"
          >
            <option value="">選擇調性</option>
            <option
              v-for="key in availableKeys"
              :key="key"
              :value="key"
            >
              {{ key }}
            </option>
          </select>
        </div>

        <div class="control-group">
          <label class="control-label">半音偏移:</label>
          <input
            v-model.number="semitoneInput"
            @change="transposeToSemitones"
            type="number"
            min="-11"
            max="11"
            class="semitone-input"
            :disabled="disabled || loading"
          />
        </div>

        <button
          @click="resetTransposition"
          :disabled="disabled || loading || semitoneOffset === 0"
          class="reset-btn"
        >
          重置
        </button>
      </div>
    </div>

    <!-- 和絃轉換預覽 -->
    <div v-if="showPreview && chordMappings.length" class="chord-preview">
      <h4 class="preview-title">和絃轉換預覽</h4>
      
      <div class="chord-mappings">
        <div
          v-for="mapping in chordMappings"
          :key="mapping.original"
          class="chord-mapping"
          :class="{ 
            'is-complex': mapping.isComplex,
            'has-error': mapping.error 
          }"
        >
          <div class="chord-original">
            {{ mapping.original }}
          </div>
          
          <div class="chord-arrow">
            <svg class="arrow-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
            </svg>
          </div>
          
          <div class="chord-transposed">
            {{ mapping.error ? '?' : mapping.transposed }}
          </div>
          
          <div v-if="mapping.error" class="chord-error" :title="mapping.error">
            ⚠️
          </div>
        </div>
      </div>

      <!-- 統計信息 -->
      <div class="transpose-stats">
        <div class="stat-item">
          <span class="stat-label">總和絃:</span>
          <span class="stat-value">{{ chordMappings.length }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">成功轉換:</span>
          <span class="stat-value success">{{ successfulTranspositions }}</span>
        </div>
        <div v-if="failedTranspositions > 0" class="stat-item">
          <span class="stat-label">轉換失敗:</span>
          <span class="stat-value error">{{ failedTranspositions }}</span>
        </div>
      </div>
    </div>

    <!-- 操作按鈕 -->
    <div v-if="showActions" class="action-buttons">
      <button
        @click="applyTransposition"
        :disabled="disabled || loading || semitoneOffset === 0"
        class="action-btn primary"
      >
        <span v-if="loading" class="loading-spinner"></span>
        {{ loading ? '轉調中...' : '套用轉調' }}
      </button>
      
      <button
        @click="previewTransposition"
        :disabled="disabled || loading"
        class="action-btn secondary"
      >
        預覽
      </button>
      
      <button
        v-if="canUndo"
        @click="undoTransposition"
        :disabled="disabled || loading"
        class="action-btn secondary"
      >
        復原
      </button>
    </div>

    <!-- 錯誤提示 -->
    <div v-if="error" class="error-message">
      <span class="error-icon">⚠️</span>
      <span class="error-text">{{ error }}</span>
      <button @click="clearError" class="error-dismiss">×</button>
    </div>

    <!-- 載入狀態 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner large"></div>
        <span class="loading-text">{{ loadingText }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { Note } from '@/types/music'

interface ChordMapping {
  original: string
  transposed: string
  isComplex: boolean
  error?: string
}

interface TransposeHistory {
  semitones: number
  chords: ChordMapping[]
  timestamp: number
}

interface Props {
  chords?: string[]
  originalKey?: Note
  layout?: 'horizontal' | 'vertical'
  compact?: boolean
  showTitle?: boolean
  showDescription?: boolean
  showAdvancedControls?: boolean
  showPreview?: boolean
  showActions?: boolean
  disabled?: boolean
  autoApply?: boolean
}

interface Emits {
  (e: 'transpose', data: { semitones: number; chords: ChordMapping[]; targetKey: Note }): void
  (e: 'chord-change', chords: string[]): void
  (e: 'key-change', key: Note): void
  (e: 'error', error: string): void
}

const props = withDefaults(defineProps<Props>(), {
  chords: () => [],
  layout: 'horizontal',
  compact: false,
  showTitle: true,
  showDescription: false,
  showAdvancedControls: true,
  showPreview: true,
  showActions: true,
  disabled: false,
  autoApply: false
})

const emit = defineEmits<Emits>()

// 響應式狀態
const semitoneOffset = ref(0)
const semitoneInput = ref(0)
const selectedTargetKey = ref<Note | ''>('')
const chordMappings = ref<ChordMapping[]>([])
const loading = ref(false)
const error = ref('')
const loadingText = ref('轉調中...')
const history = ref<TransposeHistory[]>([])

// 可用調性
const availableKeys: Note[] = [
  'C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 
  'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B'
]

// 音階映射
const noteToSemitone: Record<Note, number> = {
  'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
  'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
  'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
}

const semitoneToNote: Note[] = [
  'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'
]

// 計算屬性
const targetKey = computed((): Note => {
  if (!props.originalKey) return 'C'
  return transposeNote(props.originalKey, semitoneOffset.value)
})

const successfulTranspositions = computed(() => 
  chordMappings.value.filter(m => !m.error).length
)

const failedTranspositions = computed(() => 
  chordMappings.value.filter(m => m.error).length
)

const canUndo = computed(() => history.value.length > 0)

// 方法
const transposeNote = (note: Note, semitones: number): Note => {
  const noteIndex = noteToSemitone[note]
  const newIndex = (noteIndex + semitones + 12) % 12
  return semitoneToNote[newIndex]
}

const parseChord = (chord: string) => {
  // 和絃解析正則表達式
  const chordPattern = /^([A-G][b#]?)([^\/]*)(\/([A-G][b#]?))?$/
  const match = chord.match(chordPattern)
  
  if (!match) {
    return null
  }
  
  const [, root, quality, , bass] = match
  return {
    root: root as Note,
    quality: quality || '',
    bass: bass as Note | undefined
  }
}

const transposeChord = (chord: string, semitones: number): ChordMapping => {
  try {
    const parsed = parseChord(chord)
    
    if (!parsed) {
      return {
        original: chord,
        transposed: chord,
        isComplex: false,
        error: '無法解析的和絃格式'
      }
    }
    
    // 轉調根音
    const newRoot = transposeNote(parsed.root, semitones)
    
    // 轉調低音 (如果存在)
    let newBass = ''
    if (parsed.bass) {
      const transposedBass = transposeNote(parsed.bass, semitones)
      newBass = `/${transposedBass}`
    }
    
    // 組合新和絃
    const transposed = `${newRoot}${parsed.quality}${newBass}`
    
    // 檢查是否為複雜和絃
    const isComplex = parsed.quality.length > 3 || 
                      parsed.quality.includes('maj') ||
                      parsed.quality.includes('dim') ||
                      parsed.quality.includes('aug') ||
                      /\d/.test(parsed.quality)
    
    return {
      original: chord,
      transposed,
      isComplex,
      error: undefined
    }
  } catch (err) {
    return {
      original: chord,
      transposed: chord,
      isComplex: false,
      error: err instanceof Error ? err.message : '轉調失敗'
    }
  }
}

const updateChordMappings = () => {
  if (!props.chords || props.chords.length === 0) {
    chordMappings.value = []
    return
  }
  
  // 去重並轉調
  const uniqueChords = [...new Set(props.chords)]
  chordMappings.value = uniqueChords.map(chord => 
    transposeChord(chord, semitoneOffset.value)
  )
}

const transposeUp = () => {
  if (semitoneOffset.value < 11) {
    semitoneOffset.value++
    semitoneInput.value = semitoneOffset.value
    updateChordMappings()
    
    if (props.autoApply) {
      applyTransposition()
    }
  }
}

const transposeDown = () => {
  if (semitoneOffset.value > -11) {
    semitoneOffset.value--
    semitoneInput.value = semitoneOffset.value
    updateChordMappings()
    
    if (props.autoApply) {
      applyTransposition()
    }
  }
}

const transposeToKey = () => {
  if (!selectedTargetKey.value || !props.originalKey) return
  
  const originalSemitone = noteToSemitone[props.originalKey]
  const targetSemitone = noteToSemitone[selectedTargetKey.value as Note]
  
  let newOffset = targetSemitone - originalSemitone
  
  // 確保在 -11 到 11 範圍內
  if (newOffset > 6) newOffset -= 12
  if (newOffset < -6) newOffset += 12
  
  semitoneOffset.value = newOffset
  semitoneInput.value = newOffset
  updateChordMappings()
  
  if (props.autoApply) {
    applyTransposition()
  }
}

const transposeToSemitones = () => {
  const value = Math.max(-11, Math.min(11, semitoneInput.value || 0))
  semitoneOffset.value = value
  semitoneInput.value = value
  
  // 更新目標調性選擇
  if (props.originalKey) {
    selectedTargetKey.value = transposeNote(props.originalKey, value)
  }
  
  updateChordMappings()
  
  if (props.autoApply) {
    applyTransposition()
  }
}

const resetTransposition = () => {
  semitoneOffset.value = 0
  semitoneInput.value = 0
  selectedTargetKey.value = props.originalKey || ''
  updateChordMappings()
  
  if (props.autoApply) {
    applyTransposition()
  }
}

const previewTransposition = () => {
  updateChordMappings()
}

const applyTransposition = async () => {
  if (semitoneOffset.value === 0) return
  
  loading.value = true
  loadingText.value = '正在套用轉調...'
  error.value = ''
  
  try {
    // 保存到歷史
    const historyEntry: TransposeHistory = {
      semitones: semitoneOffset.value,
      chords: [...chordMappings.value],
      timestamp: Date.now()
    }
    history.value.push(historyEntry)
    
    // 限制歷史記錄數量
    if (history.value.length > 10) {
      history.value.shift()
    }
    
    // 模擬處理延遲
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 發出事件
    const transposedChords = chordMappings.value
      .filter(m => !m.error)
      .map(m => m.transposed)
    
    emit('transpose', {
      semitones: semitoneOffset.value,
      chords: chordMappings.value,
      targetKey: targetKey.value
    })
    
    emit('chord-change', transposedChords)
    emit('key-change', targetKey.value)
    
  } catch (err) {
    error.value = err instanceof Error ? err.message : '轉調失敗'
    emit('error', error.value)
  } finally {
    loading.value = false
  }
}

const undoTransposition = () => {
  if (history.value.length === 0) return
  
  const lastEntry = history.value.pop()
  if (lastEntry) {
    // 還原到上一個狀態
    semitoneOffset.value = -lastEntry.semitones
    semitoneInput.value = semitoneOffset.value
    
    if (props.originalKey) {
      selectedTargetKey.value = transposeNote(props.originalKey, semitoneOffset.value)
    }
    
    updateChordMappings()
    
    if (props.autoApply) {
      applyTransposition()
    }
  }
}

const clearError = () => {
  error.value = ''
}

// 監聽器
watch(() => props.chords, () => {
  updateChordMappings()
}, { deep: true })

watch(() => props.originalKey, (newKey) => {
  if (newKey && selectedTargetKey.value === '') {
    selectedTargetKey.value = newKey
  }
})

// 初始化
updateChordMappings()
</script>

<style scoped>
.chord-transposer {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  padding: 1.5rem;
  border: 1px solid var(--color-gray-200);
  position: relative;
}

.chord-transposer.compact {
  padding: 1rem;
}

.chord-transposer.vertical .transpose-controls {
  flex-direction: column;
}

/* 標題區域 */
.transposer-header {
  margin-bottom: 1.5rem;
}

.transposer-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-gray-900);
  margin: 0 0 0.5rem 0;
}

.transposer-description {
  font-size: 0.875rem;
  color: var(--color-gray-600);
  margin: 0;
  line-height: 1.5;
}

/* 轉調控制 */
.transpose-controls {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.transpose-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.transpose-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  border: 2px solid var(--color-gray-200);
  border-radius: 0.5rem;
  background: white;
  color: var(--color-gray-700);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 80px;
}

.transpose-btn:hover:not(:disabled) {
  border-color: var(--color-chord-primary);
  background-color: var(--color-gray-50);
}

.transpose-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.transpose-btn.down {
  color: #dc2626;
}

.transpose-btn.up {
  color: #059669;
}

.btn-icon {
  width: 1.5rem;
  height: 1.5rem;
}

.transpose-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background-color: var(--color-gray-50);
  border-radius: 0.5rem;
  border: 2px solid var(--color-gray-200);
  min-width: 120px;
}

.semitone-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.semitone-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-chord-primary);
}

.semitone-unit {
  font-size: 0.75rem;
  color: var(--color-gray-600);
}

.key-display {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.original-key {
  color: var(--color-gray-600);
  font-weight: 500;
}

.arrow {
  color: var(--color-gray-400);
}

.target-key {
  color: var(--color-chord-primary);
  font-weight: 700;
}

/* 進階控制 */
.advanced-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: flex-end;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  min-width: 120px;
}

.control-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-gray-700);
}

.key-select,
.semitone-input {
  padding: 0.5rem 0.75rem;
  border: 2px solid var(--color-gray-200);
  border-radius: 0.375rem;
  background: white;
  font-size: 0.875rem;
}

.key-select:focus,
.semitone-input:focus {
  outline: none;
  border-color: var(--color-chord-primary);
}

.semitone-input {
  width: 80px;
  text-align: center;
}

.reset-btn {
  padding: 0.5rem 1rem;
  border: 2px solid var(--color-gray-300);
  border-radius: 0.375rem;
  background: white;
  color: var(--color-gray-700);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.reset-btn:hover:not(:disabled) {
  border-color: var(--color-chord-primary);
  background-color: var(--color-gray-50);
}

.reset-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 和絃預覽 */
.chord-preview {
  background-color: var(--color-gray-50);
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.preview-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-gray-800);
  margin: 0 0 1rem 0;
}

.chord-mappings {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.chord-mapping {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: white;
  border-radius: 0.375rem;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-gray-200);
  transition: all 0.2s;
}

.chord-mapping.is-complex {
  border-color: var(--color-chord-accent);
  background-color: #fffbeb;
}

.chord-mapping.has-error {
  border-color: #dc2626;
  background-color: #fef2f2;
}

.chord-original {
  font-weight: 500;
  color: var(--color-gray-600);
  font-size: 0.875rem;
}

.arrow-icon {
  width: 1rem;
  height: 1rem;
  color: var(--color-gray-400);
}

.chord-transposed {
  font-weight: 700;
  color: var(--color-chord-primary);
  font-size: 0.875rem;
}

.chord-error {
  color: #dc2626;
  font-size: 0.75rem;
  cursor: help;
}

.transpose-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-gray-200);
}

.stat-item {
  display: flex;
  gap: 0.375rem;
}

.stat-label {
  color: var(--color-gray-600);
}

.stat-value {
  font-weight: 600;
}

.stat-value.success {
  color: #059669;
}

.stat-value.error {
  color: #dc2626;
}

/* 操作按鈕 */
.action-buttons {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
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

/* 載入狀態 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.75rem;
  z-index: 10;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.loading-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid var(--color-gray-200);
  border-top: 2px solid var(--color-chord-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-spinner.large {
  width: 2rem;
  height: 2rem;
  border-width: 3px;
}

.loading-text {
  font-size: 0.875rem;
  color: var(--color-gray-600);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 錯誤提示 */
.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #fef2f2;
  color: #dc2626;
  padding: 0.75rem;
  border-radius: 0.375rem;
  border: 1px solid #fecaca;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.error-icon {
  flex-shrink: 0;
}

.error-text {
  flex: 1;
}

.error-dismiss {
  background: none;
  border: none;
  color: #dc2626;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0;
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .transpose-buttons {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .advanced-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .control-group {
    min-width: auto;
  }
  
  .chord-mappings {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .action-btn {
    justify-content: center;
  }
}
</style>