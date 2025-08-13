<template>
  <div class="key-capo-selector" :class="{ compact, vertical: layout === 'vertical' }">
    <!-- 標題 -->
    <div v-if="showTitle" class="selector-header">
      <h3 class="selector-title">調性與變調夾</h3>
      <p v-if="showDescription" class="selector-description">
        選擇歌曲的原始調性和變調夾位置，系統會自動計算有效調性
      </p>
    </div>

    <!-- 選擇器容器 -->
    <div class="selectors-container">
      <!-- Key 選擇器 -->
      <div class="selector-group">
        <label class="selector-label">
          <span class="label-text">調性 (Key)</span>
          <span v-if="showHelp" class="help-icon" title="歌曲的原始調性">?</span>
        </label>
        
        <div class="key-selector">
          <!-- 按鈕模式 -->
          <div v-if="keyDisplayMode === 'buttons'" class="key-buttons">
            <button
              v-for="key in availableKeys"
              :key="key.note"
              :class="['key-btn', { 
                active: selectedKey === key.note,
                'is-sharp': key.note.includes('#'),
                'is-flat': key.note.includes('b')
              }]"
              @click="handleKeyChange(key.note)"
              :title="`${key.note} ${key.name}`"
            >
              {{ key.note }}
            </button>
          </div>

          <!-- 下拉選單模式 -->
          <select
            v-else
            v-model="selectedKey"
            @change="handleKeyChange($event.target.value)"
            class="key-select"
          >
            <option value="">請選擇調性</option>
            <option
              v-for="key in availableKeys"
              :key="key.note"
              :value="key.note"
            >
              {{ key.note }} - {{ key.name }}
            </option>
          </select>
        </div>
      </div>

      <!-- Capo 選擇器 -->
      <div class="selector-group">
        <label class="selector-label">
          <span class="label-text">變調夾 (Capo)</span>
          <span v-if="showHelp" class="help-icon" title="變調夾的品位，0表示不使用變調夾">?</span>
        </label>
        
        <div class="capo-selector">
          <!-- 滑桿模式 -->
          <div v-if="capoDisplayMode === 'slider'" class="capo-slider-container">
            <input
              v-model.number="selectedCapo"
              @input="handleCapoChange($event.target.value)"
              type="range"
              min="0"
              max="12"
              step="1"
              class="capo-slider"
            />
            <div class="capo-value">{{ selectedCapo }} 品</div>
            <div class="capo-marks">
              <span
                v-for="mark in capoMarks"
                :key="mark"
                class="capo-mark"
                :class="{ active: selectedCapo === mark }"
              >
                {{ mark }}
              </span>
            </div>
          </div>

          <!-- 按鈕模式 -->
          <div v-else-if="capoDisplayMode === 'buttons'" class="capo-buttons">
            <button
              v-for="capo in 13"
              :key="capo - 1"
              :class="['capo-btn', { active: selectedCapo === capo - 1 }]"
              @click="handleCapoChange(capo - 1)"
              :title="`${capo - 1 === 0 ? '無變調夾' : `第 ${capo - 1} 品`}`"
            >
              {{ capo - 1 === 0 ? 'Open' : capo - 1 }}
            </button>
          </div>

          <!-- 下拉選單模式 -->
          <select
            v-else
            v-model.number="selectedCapo"
            @change="handleCapoChange($event.target.value)"
            class="capo-select"
          >
            <option value="0">無變調夾 (Open)</option>
            <option
              v-for="capo in 12"
              :key="capo"
              :value="capo"
            >
              第 {{ capo }} 品
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- 效果預覽 -->
    <div v-if="showPreview && selectedKey" class="effect-preview">
      <div class="preview-header">
        <h4 class="preview-title">轉調效果預覽</h4>
      </div>
      
      <div class="preview-content">
        <div class="preview-row">
          <span class="preview-label">原始調性:</span>
          <span class="preview-value original">{{ selectedKey }}</span>
        </div>
        
        <div class="preview-row">
          <span class="preview-label">變調夾:</span>
          <span class="preview-value capo">
            {{ selectedCapo === 0 ? '無' : `第 ${selectedCapo} 品` }}
          </span>
        </div>
        
        <div class="preview-row highlight">
          <span class="preview-label">有效調性:</span>
          <span class="preview-value effective">{{ effectiveKey }}</span>
        </div>
        
        <div v-if="selectedCapo > 0" class="preview-row">
          <span class="preview-label">半音變化:</span>
          <span class="preview-value semitones">
            +{{ selectedCapo }} 半音
          </span>
        </div>
      </div>

      <!-- 和絃轉換預覽 -->
      <div v-if="showChordPreview && commonChords.length" class="chord-preview">
        <h5 class="chord-preview-title">常用和絃轉換</h5>
        <div class="chord-conversions">
          <div
            v-for="chord in commonChords"
            :key="chord.original"
            class="chord-conversion"
          >
            <span class="chord-original">{{ chord.original }}</span>
            <span class="chord-arrow">→</span>
            <span class="chord-converted">{{ chord.converted }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 快速設定 -->
    <div v-if="showQuickSettings" class="quick-settings">
      <h4 class="quick-settings-title">常用設定</h4>
      <div class="quick-presets">
        <button
          v-for="preset in quickPresets"
          :key="`${preset.key}-${preset.capo}`"
          @click="applyPreset(preset)"
          class="preset-btn"
          :class="{ active: isPresetActive(preset) }"
          :title="preset.description"
        >
          {{ preset.name }}
        </button>
      </div>
    </div>

    <!-- 錯誤提示 -->
    <div v-if="error" class="error-message">
      <span class="error-icon">⚠️</span>
      <span class="error-text">{{ error }}</span>
      <button @click="clearError" class="error-dismiss">×</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { Note } from '@/types/music'

interface KeyInfo {
  note: Note
  name: string
  sharps?: number
  flats?: number
}

interface QuickPreset {
  name: string
  key: Note
  capo: number
  description: string
}

interface ChordConversion {
  original: string
  converted: string
}

interface Props {
  modelKey?: Note | null
  modelCapo?: number
  keyDisplayMode?: 'buttons' | 'select'
  capoDisplayMode?: 'slider' | 'buttons' | 'select'
  layout?: 'horizontal' | 'vertical'
  compact?: boolean
  showTitle?: boolean
  showDescription?: boolean
  showHelp?: boolean
  showPreview?: boolean
  showChordPreview?: boolean
  showQuickSettings?: boolean
  disabled?: boolean
}

interface Emits {
  (e: 'update:modelKey', key: Note): void
  (e: 'update:modelCapo', capo: number): void
  (e: 'change', data: { key: Note; capo: number; effectiveKey: Note }): void
  (e: 'key-change', key: Note): void
  (e: 'capo-change', capo: number): void
}

const props = withDefaults(defineProps<Props>(), {
  modelKey: null,
  modelCapo: 0,
  keyDisplayMode: 'buttons',
  capoDisplayMode: 'slider',
  layout: 'horizontal',
  compact: false,
  showTitle: true,
  showDescription: false,
  showHelp: true,
  showPreview: true,
  showChordPreview: false,
  showQuickSettings: false,
  disabled: false
})

const emit = defineEmits<Emits>()

// 響應式狀態
const selectedKey = ref<Note | null>(props.modelKey)
const selectedCapo = ref(props.modelCapo)
const error = ref('')

// 可用調性
const availableKeys: KeyInfo[] = [
  { note: 'C', name: '大調' },
  { note: 'C#', name: '大調 (升C)' },
  { note: 'Db', name: '大調 (降D)' },
  { note: 'D', name: '大調' },
  { note: 'D#', name: '大調 (升D)' },
  { note: 'Eb', name: '大調 (降E)' },
  { note: 'E', name: '大調' },
  { note: 'F', name: '大調' },
  { note: 'F#', name: '大調 (升F)' },
  { note: 'Gb', name: '大調 (降G)' },
  { note: 'G', name: '大調' },
  { note: 'G#', name: '大調 (升G)' },
  { note: 'Ab', name: '大調 (降A)' },
  { note: 'A', name: '大調' },
  { note: 'A#', name: '大調 (升A)' },
  { note: 'Bb', name: '大調 (降B)' },
  { note: 'B', name: '大調' }
]

// Capo 標記
const capoMarks = [0, 2, 4, 5, 7, 9, 12]

// 快速設定預設
const quickPresets: QuickPreset[] = [
  { name: 'C Open', key: 'C', capo: 0, description: 'C大調，無變調夾' },
  { name: 'G Open', key: 'G', capo: 0, description: 'G大調，無變調夾' },
  { name: 'D Open', key: 'D', capo: 0, description: 'D大調，無變調夾' },
  { name: 'C → D', key: 'C', capo: 2, description: 'C指法彈D調' },
  { name: 'G → A', key: 'G', capo: 2, description: 'G指法彈A調' },
  { name: 'D → E', key: 'D', capo: 2, description: 'D指法彈E調' },
  { name: 'C → E', key: 'C', capo: 4, description: 'C指法彈E調' },
  { name: 'G → B', key: 'G', capo: 4, description: 'G指法彈B調' }
]

// 計算屬性
const effectiveKey = computed((): Note => {
  if (!selectedKey.value) return 'C'
  return transposeNote(selectedKey.value, selectedCapo.value)
})

const commonChords = computed((): ChordConversion[] => {
  if (!selectedKey.value || selectedCapo.value === 0) return []
  
  const baseChords = getCommonChordsForKey(selectedKey.value)
  return baseChords.map(chord => ({
    original: chord,
    converted: transposeChord(chord, selectedCapo.value)
  }))
})

// 方法
const transposeNote = (note: Note, semitones: number): Note => {
  const notes: Note[] = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
  const noteIndex = notes.indexOf(note)
  if (noteIndex === -1) return note
  
  const newIndex = (noteIndex + semitones) % 12
  return notes[newIndex]
}

const transposeChord = (chord: string, semitones: number): string => {
  // 簡化的和絃轉調邏輯
  const notePattern = /^([A-G][b#]?)/
  const match = chord.match(notePattern)
  if (!match) return chord
  
  const rootNote = match[1] as Note
  const transposedRoot = transposeNote(rootNote, semitones)
  return chord.replace(notePattern, transposedRoot)
}

const getCommonChordsForKey = (key: Note): string[] => {
  // 根據調性返回常用和絃
  const keyChords: Record<Note, string[]> = {
    'C': ['C', 'Dm', 'Em', 'F', 'G', 'Am'],
    'G': ['G', 'Am', 'Bm', 'C', 'D', 'Em'],
    'D': ['D', 'Em', 'F#m', 'G', 'A', 'Bm'],
    'A': ['A', 'Bm', 'C#m', 'D', 'E', 'F#m'],
    'E': ['E', 'F#m', 'G#m', 'A', 'B', 'C#m'],
    'F': ['F', 'Gm', 'Am', 'Bb', 'C', 'Dm']
  } as any
  
  return keyChords[key] || ['C', 'F', 'G']
}

const handleKeyChange = (key: Note) => {
  if (props.disabled) return
  
  selectedKey.value = key
  emit('update:modelKey', key)
  emit('key-change', key)
  emitChange()
}

const handleCapoChange = (capo: number | string) => {
  if (props.disabled) return
  
  const capoNum = typeof capo === 'string' ? parseInt(capo) : capo
  
  if (isNaN(capoNum) || capoNum < 0 || capoNum > 12) {
    error.value = '變調夾位置必須在 0-12 品之間'
    return
  }
  
  selectedCapo.value = capoNum
  emit('update:modelCapo', capoNum)
  emit('capo-change', capoNum)
  emitChange()
}

const emitChange = () => {
  if (selectedKey.value) {
    emit('change', {
      key: selectedKey.value,
      capo: selectedCapo.value,
      effectiveKey: effectiveKey.value
    })
  }
}

const applyPreset = (preset: QuickPreset) => {
  if (props.disabled) return
  
  selectedKey.value = preset.key
  selectedCapo.value = preset.capo
  
  emit('update:modelKey', preset.key)
  emit('update:modelCapo', preset.capo)
  emit('key-change', preset.key)
  emit('capo-change', preset.capo)
  emitChange()
}

const isPresetActive = (preset: QuickPreset): boolean => {
  return selectedKey.value === preset.key && selectedCapo.value === preset.capo
}

const clearError = () => {
  error.value = ''
}

// 監聽器
watch(() => props.modelKey, (newKey) => {
  selectedKey.value = newKey
})

watch(() => props.modelCapo, (newCapo) => {
  selectedCapo.value = newCapo
})
</script>

<style scoped>
.key-capo-selector {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  padding: 1.5rem;
  border: 1px solid var(--color-gray-200);
}

.key-capo-selector.compact {
  padding: 1rem;
}

.key-capo-selector.vertical .selectors-container {
  flex-direction: column;
}

/* 標題區域 */
.selector-header {
  margin-bottom: 1.5rem;
}

.selector-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-gray-900);
  margin: 0 0 0.5rem 0;
}

.selector-description {
  font-size: 0.875rem;
  color: var(--color-gray-600);
  margin: 0;
  line-height: 1.5;
}

/* 選擇器容器 */
.selectors-container {
  display: flex;
  gap: 2rem;
  margin-bottom: 1.5rem;
}

.selector-group {
  flex: 1;
  min-width: 0;
}

.selector-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-gray-700);
}

.help-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1rem;
  height: 1rem;
  background-color: var(--color-gray-400);
  color: white;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: bold;
  cursor: help;
}

/* Key 選擇器 */
.key-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(2.5rem, 1fr));
  gap: 0.5rem;
}

.key-btn {
  padding: 0.75rem 0.5rem;
  border: 2px solid var(--color-gray-200);
  border-radius: 0.375rem;
  background: white;
  color: var(--color-gray-700);
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.key-btn:hover {
  border-color: var(--color-chord-primary);
  background-color: var(--color-gray-50);
}

.key-btn.active {
  background-color: var(--color-chord-primary);
  border-color: var(--color-chord-primary);
  color: white;
}

.key-btn.is-sharp {
  background-color: var(--color-gray-800);
  color: white;
  border-color: var(--color-gray-800);
}

.key-btn.is-sharp:hover {
  background-color: var(--color-gray-700);
  border-color: var(--color-gray-700);
}

.key-btn.is-sharp.active {
  background-color: var(--color-chord-primary);
  border-color: var(--color-chord-primary);
}

.key-select {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid var(--color-gray-200);
  border-radius: 0.375rem;
  background: white;
  font-size: 0.875rem;
  cursor: pointer;
}

.key-select:focus {
  outline: none;
  border-color: var(--color-chord-primary);
}

/* Capo 選擇器 */
.capo-slider-container {
  position: relative;
}

.capo-slider {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: var(--color-gray-200);
  outline: none;
  cursor: pointer;
  -webkit-appearance: none;
  appearance: none;
}

.capo-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--color-chord-primary);
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
}

.capo-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--color-chord-primary);
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  border: none;
}

.capo-value {
  text-align: center;
  margin: 0.75rem 0;
  font-weight: 600;
  color: var(--color-chord-primary);
}

.capo-marks {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: var(--color-gray-500);
}

.capo-mark {
  transition: color 0.2s;
}

.capo-mark.active {
  color: var(--color-chord-primary);
  font-weight: 600;
}

.capo-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(3rem, 1fr));
  gap: 0.375rem;
  max-height: 120px;
  overflow-y: auto;
}

.capo-btn {
  padding: 0.5rem 0.25rem;
  border: 2px solid var(--color-gray-200);
  border-radius: 0.25rem;
  background: white;
  color: var(--color-gray-700);
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.capo-btn:hover {
  border-color: var(--color-chord-primary);
  background-color: var(--color-gray-50);
}

.capo-btn.active {
  background-color: var(--color-chord-primary);
  border-color: var(--color-chord-primary);
  color: white;
}

.capo-select {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid var(--color-gray-200);
  border-radius: 0.375rem;
  background: white;
  font-size: 0.875rem;
  cursor: pointer;
}

.capo-select:focus {
  outline: none;
  border-color: var(--color-chord-primary);
}

/* 效果預覽 */
.effect-preview {
  background-color: var(--color-gray-50);
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.preview-header {
  margin-bottom: 0.75rem;
}

.preview-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-gray-800);
  margin: 0;
}

.preview-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.preview-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.375rem 0;
}

.preview-row.highlight {
  background-color: var(--color-chord-primary);
  color: white;
  border-radius: 0.25rem;
  padding: 0.5rem 0.75rem;
  margin: 0.25rem 0;
}

.preview-label {
  font-size: 0.875rem;
  font-weight: 500;
}

.preview-value {
  font-weight: 700;
  font-size: 0.875rem;
}

.preview-value.effective {
  font-size: 1rem;
}

/* 和絃預覽 */
.chord-preview {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-gray-200);
}

.chord-preview-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-gray-700);
  margin: 0 0 0.75rem 0;
}

.chord-conversions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
  gap: 0.5rem;
}

.chord-conversion {
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 0.25rem;
  padding: 0.375rem;
  font-size: 0.75rem;
  border: 1px solid var(--color-gray-200);
}

.chord-original {
  color: var(--color-gray-600);
  font-weight: 500;
}

.chord-arrow {
  margin: 0 0.25rem;
  color: var(--color-gray-400);
}

.chord-converted {
  color: var(--color-chord-primary);
  font-weight: 700;
}

/* 快速設定 */
.quick-settings {
  margin-bottom: 1rem;
}

.quick-settings-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-gray-800);
  margin: 0 0 0.75rem 0;
}

.quick-presets {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 0.5rem;
}

.preset-btn {
  padding: 0.5rem 0.75rem;
  border: 2px solid var(--color-gray-200);
  border-radius: 0.375rem;
  background: white;
  color: var(--color-gray-700);
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.preset-btn:hover {
  border-color: var(--color-chord-primary);
  background-color: var(--color-gray-50);
}

.preset-btn.active {
  background-color: var(--color-chord-primary);
  border-color: var(--color-chord-primary);
  color: white;
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
  .selectors-container {
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .key-buttons {
    grid-template-columns: repeat(4, 1fr);
  }
  
  .capo-buttons {
    grid-template-columns: repeat(4, 1fr);
  }
  
  .quick-presets {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .chord-conversions {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 禁用狀態 */
.key-capo-selector[disabled] {
  opacity: 0.6;
  pointer-events: none;
}
</style>