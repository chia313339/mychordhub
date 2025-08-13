<template>
  <div class="lyrics-editor" :class="{ compact, fullscreen: isFullscreen }">
    <!-- 編輯器標題欄 -->
    <div class="editor-header">
      <div class="header-left">
        <h3 class="editor-title">歌詞編輯器</h3>
        <div class="editor-stats">
          <span class="stat-item">{{ lineCount }} 行</span>
          <span class="stat-item">{{ chordCount }} 個和絃</span>
          <span class="stat-item">{{ wordCount }} 字</span>
        </div>
      </div>
      
      <div class="header-right">
        <!-- 顯示模式切換 -->
        <div class="view-mode-toggle">
          <button
            :class="{ active: viewMode === 'edit' }"
            @click="setViewMode('edit')"
            class="mode-btn"
            title="編輯模式"
          >
            編輯
          </button>
          <button
            :class="{ active: viewMode === 'preview' }"
            @click="setViewMode('preview')"
            class="mode-btn"
            title="預覽模式"
          >
            預覽
          </button>
          <button
            :class="{ active: viewMode === 'split' }"
            @click="setViewMode('split')"
            class="mode-btn"
            title="分割視圖"
          >
            分割
          </button>
        </div>
        
        <!-- 工具按鈕 -->
        <div class="toolbar-buttons">
          <button
            @click="toggleFullscreen"
            class="tool-btn"
            :title="isFullscreen ? '退出全螢幕' : '進入全螢幕'"
          >
            <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="!isFullscreen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"/>
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 9V4.5M9 9H4.5M9 9L3.5 3.5M15 9h4.5M15 9V4.5M15 9l5.5-5.5M9 15v4.5M9 15H4.5M9 15l-5.5 5.5M15 15h4.5M15 15v4.5m0 0l5.5 5.5"/>
            </svg>
          </button>
          
          <button
            @click="showChordPalette = !showChordPalette"
            class="tool-btn"
            :class="{ active: showChordPalette }"
            title="和絃選擇器"
          >
            🎸
          </button>
          
          <button
            @click="showHelp = !showHelp"
            class="tool-btn"
            title="說明"
          >
            ?
          </button>
        </div>
      </div>
    </div>

    <!-- 編輯器主體 -->
    <div class="editor-body" :class="{ 'split-view': viewMode === 'split' }">
      <!-- 編輯區域 -->
      <div v-if="viewMode === 'edit' || viewMode === 'split'" class="edit-panel">
        <div class="edit-container">
          <!-- 工具欄 -->
          <div class="editor-toolbar">
            <button
              @click="insertChord"
              class="toolbar-btn primary"
              :disabled="!selectedText && cursorPosition === -1"
            >
              插入和絃
            </button>
            
            <button @click="formatLyrics" class="toolbar-btn">
              格式化
            </button>
            
            <button @click="clearAllChords" class="toolbar-btn danger">
              清除和絃
            </button>
            
            <div class="toolbar-divider"></div>
            
            <button @click="undo" :disabled="!canUndo" class="toolbar-btn">
              復原
            </button>
            
            <button @click="redo" :disabled="!canRedo" class="toolbar-btn">
              重做
            </button>
          </div>

          <!-- 文字編輯區 -->
          <div class="text-editor-container">
            <textarea
              ref="textareaRef"
              v-model="lyricsContent"
              @input="handleInput"
              @keydown="handleKeyDown"
              @select="handleSelection"
              @click="handleCursorPosition"
              class="lyrics-textarea"
              :placeholder="placeholder"
              spellcheck="false"
            ></textarea>
            
            <!-- 行號 -->
            <div class="line-numbers">
              <div
                v-for="line in lineCount"
                :key="line"
                class="line-number"
              >
                {{ line }}
              </div>
            </div>
            
            <!-- 游標位置指示器 -->
            <div v-if="showCursorInfo" class="cursor-info">
              行 {{ cursorLine }}，列 {{ cursorColumn }}
            </div>
          </div>
        </div>
      </div>

      <!-- 預覽區域 -->
      <div v-if="viewMode === 'preview' || viewMode === 'split'" class="preview-panel">
        <div class="preview-container">
          <div class="preview-header">
            <h4 class="preview-title">預覽</h4>
            <div class="preview-controls">
              <label class="checkbox-label">
                <input v-model="showChordDiagrams" type="checkbox" />
                顯示和絃圖
              </label>
            </div>
          </div>
          
          <div class="lyrics-preview">
            <div
              v-for="(line, index) in parsedLyrics"
              :key="index"
              class="lyrics-line"
            >
              <!-- 和絃行 -->
              <div v-if="line.chords.length > 0" class="chord-line">
                <span
                  v-for="(chord, chordIndex) in line.chords"
                  :key="chordIndex"
                  class="chord-marker"
                  :style="{ left: `${chord.position * 0.6}ch` }"
                  @click="editChord(chord, index)"
                >
                  {{ chord.symbol }}
                </span>
              </div>
              
              <!-- 歌詞行 -->
              <div class="lyric-text">{{ line.text }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 和絃選擇器面板 -->
    <div v-if="showChordPalette" class="chord-palette-panel">
      <div class="palette-header">
        <h4 class="palette-title">常用和絃</h4>
        <button @click="showChordPalette = false" class="close-btn">×</button>
      </div>
      
      <div class="chord-categories">
        <button
          v-for="category in chordCategories"
          :key="category.name"
          @click="selectedCategory = category.name"
          :class="['category-btn', { active: selectedCategory === category.name }]"
        >
          {{ category.name }}
        </button>
      </div>
      
      <div class="chord-grid">
        <button
          v-for="chord in currentCategoryChords"
          :key="chord"
          @click="insertChordAtCursor(chord)"
          class="chord-btn"
        >
          {{ chord }}
        </button>
      </div>
    </div>

    <!-- 和絃編輯對話框 -->
    <div v-if="editingChord" class="chord-edit-modal">
      <div class="modal-content">
        <div class="modal-header">
          <h4 class="modal-title">編輯和絃</h4>
          <button @click="closeChordEdit" class="close-btn">×</button>
        </div>
        
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">和絃符號:</label>
            <input
              v-model="editingChordSymbol"
              type="text"
              class="form-input"
              placeholder="例如: C, Dm, G7"
              @keyup.enter="saveChordEdit"
            />
          </div>
          
          <div class="form-actions">
            <button @click="saveChordEdit" class="action-btn primary">
              儲存
            </button>
            <button @click="deleteChord" class="action-btn danger">
              刪除
            </button>
            <button @click="closeChordEdit" class="action-btn secondary">
              取消
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 說明面板 -->
    <div v-if="showHelp" class="help-panel">
      <div class="help-content">
        <h4 class="help-title">使用說明</h4>
        
        <div class="help-section">
          <h5>插入和絃:</h5>
          <ul>
            <li>選擇文字後點擊「插入和絃」按鈕</li>
            <li>或在游標位置直接輸入 [C] 格式</li>
            <li>使用和絃選擇器快速插入常用和絃</li>
          </ul>
        </div>
        
        <div class="help-section">
          <h5>快捷鍵:</h5>
          <ul>
            <li><kbd>Ctrl+Z</kbd> 復原</li>
            <li><kbd>Ctrl+Y</kbd> 重做</li>
            <li><kbd>F11</kbd> 全螢幕切換</li>
            <li><kbd>Ctrl+/</kbd> 插入和絃</li>
          </ul>
        </div>
        
        <div class="help-section">
          <h5>格式說明:</h5>
          <ul>
            <li>和絃使用 [和絃名稱] 格式，例如 [C]、[Dm]、[G7]</li>
            <li>可以在歌詞的任何位置插入和絃</li>
            <li>點擊預覽中的和絃可以編輯</li>
          </ul>
        </div>
        
        <button @click="showHelp = false" class="close-help-btn">
          關閉說明
        </button>
      </div>
    </div>

    <!-- 錯誤提示 -->
    <div v-if="error" class="error-toast">
      <span class="error-icon">⚠️</span>
      <span class="error-text">{{ error }}</span>
      <button @click="clearError" class="error-dismiss">×</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import type { ChordPosition } from '@/types/music'

interface ParsedLyricLine {
  text: string
  chords: Array<{
    symbol: string
    position: number
    id: string
  }>
}

interface ChordCategory {
  name: string
  chords: string[]
}

interface Props {
  modelValue?: string
  chordPositions?: ChordPosition[]
  compact?: boolean
  placeholder?: string
  showLineNumbers?: boolean
  showCursorInfo?: boolean
  autoSave?: boolean
  maxLines?: number
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'update:chordPositions', positions: ChordPosition[]): void
  (e: 'chord-change', chords: string[]): void
  (e: 'content-change', data: { lyrics: string; chords: ChordPosition[] }): void
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  chordPositions: () => [],
  compact: false,
  placeholder: '在此輸入歌詞...\n\n可以使用 [C] [Dm] [G] 格式插入和絃',
  showLineNumbers: true,
  showCursorInfo: true,
  autoSave: false,
  maxLines: 100
})

const emit = defineEmits<Emits>()

// 響應式狀態
const lyricsContent = ref(props.modelValue)
const viewMode = ref<'edit' | 'preview' | 'split'>('edit')
const isFullscreen = ref(false)
const showChordPalette = ref(false)
const showHelp = ref(false)
const showChordDiagrams = ref(false)
const selectedCategory = ref('基本')
const cursorPosition = ref(-1)
const cursorLine = ref(1)
const cursorColumn = ref(1)
const selectedText = ref('')
const textareaRef = ref<HTMLTextAreaElement>()
const error = ref('')

// 編輯狀態
const editingChord = ref<any>(null)
const editingChordSymbol = ref('')
const history = ref<string[]>([])
const historyIndex = ref(-1)
const maxHistory = 50

// 和絃分類
const chordCategories: ChordCategory[] = [
  {
    name: '基本',
    chords: ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'Dm', 'Em', 'Am']
  },
  {
    name: '七和絃',
    chords: ['C7', 'D7', 'E7', 'F7', 'G7', 'A7', 'B7', 'Cmaj7', 'Dmaj7', 'Emaj7']
  },
  {
    name: '小調',
    chords: ['Cm', 'Dm', 'Em', 'Fm', 'Gm', 'Am', 'Bm', 'Cm7', 'Dm7', 'Em7']
  },
  {
    name: '其他',
    chords: ['Csus2', 'Csus4', 'C6', 'C9', 'Cadd9', 'Cdim', 'Caug', 'C/E', 'C/G']
  }
]

// 計算屬性
const lineCount = computed(() => {
  return lyricsContent.value.split('\n').length
})

const wordCount = computed(() => {
  return lyricsContent.value.replace(/\[.*?\]/g, '').trim().length
})

const chordCount = computed(() => {
  const matches = lyricsContent.value.match(/\[([^\]]+)\]/g)
  return matches ? matches.length : 0
})

const currentCategoryChords = computed(() => {
  const category = chordCategories.find(c => c.name === selectedCategory.value)
  return category ? category.chords : []
})

const parsedLyrics = computed((): ParsedLyricLine[] => {
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
        id: `chord-${Math.random().toString(36).substr(2, 9)}`
      })
      
      // 從文字中移除和絃標記
      cleanText = cleanText.substring(0, position) + cleanText.substring(position + match[0].length)
    }
    
    return {
      text: cleanText,
      chords: chords.sort((a, b) => a.position - b.position)
    }
  })
})

const canUndo = computed(() => historyIndex.value > 0)
const canRedo = computed(() => historyIndex.value < history.value.length - 1)

// 方法
const setViewMode = (mode: 'edit' | 'preview' | 'split') => {
  viewMode.value = mode
}

const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
}

const handleInput = () => {
  saveToHistory()
  emit('update:modelValue', lyricsContent.value)
  updateChordPositions()
  
  if (props.autoSave) {
    // 自動儲存邏輯
    debounceAutoSave()
  }
}

const handleKeyDown = (event: KeyboardEvent) => {
  if (event.ctrlKey) {
    switch (event.key) {
      case 'z':
        event.preventDefault()
        undo()
        break
      case 'y':
        event.preventDefault()
        redo()
        break
      case '/':
        event.preventDefault()
        insertChord()
        break
    }
  } else if (event.key === 'F11') {
    event.preventDefault()
    toggleFullscreen()
  }
}

const handleSelection = () => {
  if (!textareaRef.value) return
  
  const start = textareaRef.value.selectionStart
  const end = textareaRef.value.selectionEnd
  
  if (start !== end) {
    selectedText.value = lyricsContent.value.substring(start, end)
  } else {
    selectedText.value = ''
  }
}

const handleCursorPosition = () => {
  if (!textareaRef.value) return
  
  cursorPosition.value = textareaRef.value.selectionStart
  
  // 計算行列號
  const textBeforeCursor = lyricsContent.value.substring(0, cursorPosition.value)
  const lines = textBeforeCursor.split('\n')
  cursorLine.value = lines.length
  cursorColumn.value = lines[lines.length - 1].length + 1
}

const insertChord = () => {
  if (!textareaRef.value) return
  
  const chordSymbol = prompt('請輸入和絃符號 (例如: C, Dm, G7):')
  if (!chordSymbol) return
  
  insertChordAtCursor(chordSymbol)
}

const insertChordAtCursor = (chordSymbol: string) => {
  if (!textareaRef.value) return
  
  const start = textareaRef.value.selectionStart
  const end = textareaRef.value.selectionEnd
  const chordText = `[${chordSymbol}]`
  
  const newContent = 
    lyricsContent.value.substring(0, start) +
    chordText +
    lyricsContent.value.substring(end)
  
  lyricsContent.value = newContent
  
  // 設置游標位置
  nextTick(() => {
    if (textareaRef.value) {
      const newCursorPos = start + chordText.length
      textareaRef.value.setSelectionRange(newCursorPos, newCursorPos)
      textareaRef.value.focus()
    }
  })
  
  handleInput()
}

const formatLyrics = () => {
  // 基本格式化：移除多餘空行，統一和絃格式
  let formatted = lyricsContent.value
  
  // 統一和絃格式
  formatted = formatted.replace(/\[\s*([^\]]+)\s*\]/g, '[$1]')
  
  // 移除多餘空行
  formatted = formatted.replace(/\n{3,}/g, '\n\n')
  
  // 首尾去空
  formatted = formatted.trim()
  
  lyricsContent.value = formatted
  handleInput()
}

const clearAllChords = () => {
  if (confirm('確定要清除所有和絃嗎？')) {
    lyricsContent.value = lyricsContent.value.replace(/\[([^\]]+)\]/g, '')
    handleInput()
  }
}

const editChord = (chord: any, lineIndex: number) => {
  editingChord.value = { ...chord, lineIndex }
  editingChordSymbol.value = chord.symbol
}

const saveChordEdit = () => {
  if (!editingChord.value) return
  
  // 在歌詞中找到並替換和絃
  const lines = lyricsContent.value.split('\n')
  const lineIndex = editingChord.value.lineIndex
  
  if (lineIndex < lines.length) {
    const line = lines[lineIndex]
    const oldChordPattern = `[${editingChord.value.symbol}]`
    const newChordPattern = `[${editingChordSymbol.value}]`
    
    lines[lineIndex] = line.replace(oldChordPattern, newChordPattern)
    lyricsContent.value = lines.join('\n')
    handleInput()
  }
  
  closeChordEdit()
}

const deleteChord = () => {
  if (!editingChord.value) return
  
  const lines = lyricsContent.value.split('\n')
  const lineIndex = editingChord.value.lineIndex
  
  if (lineIndex < lines.length) {
    const line = lines[lineIndex]
    const chordPattern = `[${editingChord.value.symbol}]`
    lines[lineIndex] = line.replace(chordPattern, '')
    lyricsContent.value = lines.join('\n')
    handleInput()
  }
  
  closeChordEdit()
}

const closeChordEdit = () => {
  editingChord.value = null
  editingChordSymbol.value = ''
}

const saveToHistory = () => {
  // 移除當前位置之後的歷史
  history.value = history.value.slice(0, historyIndex.value + 1)
  
  // 添加新狀態
  history.value.push(lyricsContent.value)
  
  // 限制歷史記錄數量
  if (history.value.length > maxHistory) {
    history.value.shift()
  } else {
    historyIndex.value++
  }
}

const undo = () => {
  if (canUndo.value) {
    historyIndex.value--
    lyricsContent.value = history.value[historyIndex.value]
    emit('update:modelValue', lyricsContent.value)
    updateChordPositions()
  }
}

const redo = () => {
  if (canRedo.value) {
    historyIndex.value++
    lyricsContent.value = history.value[historyIndex.value]
    emit('update:modelValue', lyricsContent.value)
    updateChordPositions()
  }
}

const updateChordPositions = () => {
  const positions: ChordPosition[] = []
  const lines = lyricsContent.value.split('\n')
  
  lines.forEach((line, lineIndex) => {
    const chordMatches = Array.from(line.matchAll(/\[([^\]]+)\]/g))
    
    chordMatches.forEach(match => {
      positions.push({
        line: lineIndex,
        position: match.index || 0,
        chord: match[1]
      })
    })
  })
  
  emit('update:chordPositions', positions)
  
  // 提取唯一和絃
  const uniqueChords = [...new Set(positions.map(p => p.chord))]
  emit('chord-change', uniqueChords)
  
  emit('content-change', {
    lyrics: lyricsContent.value,
    chords: positions
  })
}

let autoSaveTimer: number | null = null

const debounceAutoSave = () => {
  if (autoSaveTimer) {
    clearTimeout(autoSaveTimer)
  }
  
  autoSaveTimer = window.setTimeout(() => {
    // 自動儲存邏輯
    console.log('Auto saving...')
  }, 2000)
}

const clearError = () => {
  error.value = ''
}

// 全螢幕事件監聽
const handleFullscreenChange = () => {
  isFullscreen.value = document.fullscreenElement !== null
}

// 監聽器
watch(() => props.modelValue, (newValue) => {
  if (newValue !== lyricsContent.value) {
    lyricsContent.value = newValue
  }
})

// 生命週期
onMounted(() => {
  // 初始化歷史記錄
  history.value = [lyricsContent.value]
  historyIndex.value = 0
  
  // 添加全螢幕事件監聽
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  
  // 更新和絃位置
  updateChordPositions()
})

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  
  if (autoSaveTimer) {
    clearTimeout(autoSaveTimer)
  }
})
</script>

<style scoped>
.lyrics-editor {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  border: 1px solid var(--color-gray-200);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 600px;
  position: relative;
}

.lyrics-editor.compact {
  height: 400px;
}

.lyrics-editor.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  border-radius: 0;
  height: 100vh;
}

/* 標題欄 */
.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--color-gray-200);
  background-color: var(--color-gray-50);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.editor-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-gray-900);
  margin: 0;
}

.editor-stats {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: var(--color-gray-600);
}

.stat-item {
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.view-mode-toggle {
  display: flex;
  background-color: var(--color-gray-100);
  border-radius: 0.375rem;
  padding: 0.25rem;
}

.mode-btn {
  padding: 0.375rem 0.75rem;
  border: none;
  border-radius: 0.25rem;
  background: transparent;
  color: var(--color-gray-600);
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.mode-btn:hover {
  background-color: var(--color-gray-200);
}

.mode-btn.active {
  background-color: var(--color-chord-primary);
  color: white;
}

.toolbar-buttons {
  display: flex;
  gap: 0.5rem;
}

.tool-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border: 1px solid var(--color-gray-300);
  border-radius: 0.25rem;
  background: white;
  color: var(--color-gray-600);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
}

.tool-btn:hover {
  background-color: var(--color-gray-50);
  border-color: var(--color-chord-primary);
}

.tool-btn.active {
  background-color: var(--color-chord-primary);
  color: white;
  border-color: var(--color-chord-primary);
}

.btn-icon {
  width: 1rem;
  height: 1rem;
}

/* 編輯器主體 */
.editor-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.editor-body.split-view .edit-panel,
.editor-body.split-view .preview-panel {
  flex: 1;
  border-right: 1px solid var(--color-gray-200);
}

.editor-body.split-view .preview-panel {
  border-right: none;
}

.edit-panel,
.preview-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 編輯區域 */
.edit-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-gray-200);
  background-color: var(--color-gray-50);
  flex-shrink: 0;
}

.toolbar-btn {
  padding: 0.375rem 0.75rem;
  border: 1px solid var(--color-gray-300);
  border-radius: 0.25rem;
  background: white;
  color: var(--color-gray-700);
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.toolbar-btn:hover:not(:disabled) {
  background-color: var(--color-gray-50);
  border-color: var(--color-chord-primary);
}

.toolbar-btn.primary {
  background-color: var(--color-chord-primary);
  color: white;
  border-color: var(--color-chord-primary);
}

.toolbar-btn.primary:hover:not(:disabled) {
  background-color: var(--color-chord-primary-dark);
}

.toolbar-btn.danger {
  color: #dc2626;
  border-color: #fecaca;
}

.toolbar-btn.danger:hover:not(:disabled) {
  background-color: #fef2f2;
  border-color: #dc2626;
}

.toolbar-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.toolbar-divider {
  width: 1px;
  height: 1.5rem;
  background-color: var(--color-gray-300);
  margin: 0 0.5rem;
}

.text-editor-container {
  position: relative;
  flex: 1;
  display: flex;
}

.lyrics-textarea {
  flex: 1;
  padding: 1rem;
  padding-left: 3rem;
  border: none;
  outline: none;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  line-height: 1.6;
  resize: none;
  background: transparent;
  color: var(--color-gray-900);
}

.line-numbers {
  position: absolute;
  left: 0;
  top: 0;
  width: 2.5rem;
  padding: 1rem 0.5rem;
  background-color: var(--color-gray-50);
  border-right: 1px solid var(--color-gray-200);
  font-family: 'Courier New', monospace;
  font-size: 0.75rem;
  line-height: 1.6;
  color: var(--color-gray-500);
  text-align: right;
  user-select: none;
  overflow: hidden;
}

.line-number {
  height: 1.4em;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.cursor-info {
  position: absolute;
  bottom: 0.5rem;
  right: 0.5rem;
  background-color: var(--color-gray-800);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-family: monospace;
}

/* 預覽區域 */
.preview-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-gray-200);
  background-color: var(--color-gray-50);
  flex-shrink: 0;
}

.preview-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-gray-800);
  margin: 0;
}

.preview-controls {
  display: flex;
  gap: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: var(--color-gray-600);
  cursor: pointer;
}

.lyrics-preview {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  background: white;
}

.lyrics-line {
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
  cursor: pointer;
  transform: translateX(-50%);
  white-space: nowrap;
  z-index: 1;
}

.chord-marker:hover {
  background-color: var(--color-chord-primary-dark);
}

.lyric-text {
  font-size: 0.875rem;
  line-height: 1.6;
  color: var(--color-gray-900);
  white-space: pre-wrap;
}

/* 和絃選擇器面板 */
.chord-palette-panel {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid var(--color-gray-200);
  border-top: none;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 100;
  max-height: 300px;
  overflow-y: auto;
}

.palette-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-gray-200);
  background-color: var(--color-gray-50);
}

.palette-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-gray-800);
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  color: var(--color-gray-500);
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0;
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chord-categories {
  display: flex;
  padding: 0.5rem 1rem;
  gap: 0.5rem;
  border-bottom: 1px solid var(--color-gray-200);
}

.category-btn {
  padding: 0.25rem 0.75rem;
  border: 1px solid var(--color-gray-300);
  border-radius: 0.25rem;
  background: white;
  color: var(--color-gray-700);
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.category-btn:hover {
  background-color: var(--color-gray-50);
}

.category-btn.active {
  background-color: var(--color-chord-primary);
  color: white;
  border-color: var(--color-chord-primary);
}

.chord-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(3rem, 1fr));
  gap: 0.5rem;
  padding: 1rem;
}

.chord-btn {
  padding: 0.5rem;
  border: 1px solid var(--color-gray-300);
  border-radius: 0.25rem;
  background: white;
  color: var(--color-gray-700);
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.chord-btn:hover {
  background-color: var(--color-chord-primary);
  color: white;
  border-color: var(--color-chord-primary);
}

/* 和絃編輯對話框 */
.chord-edit-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.modal-content {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  max-width: 400px;
  width: 90%;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--color-gray-200);
}

.modal-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-gray-800);
  margin: 0;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-gray-700);
  margin-bottom: 0.375rem;
}

.form-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 2px solid var(--color-gray-200);
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-chord-primary);
}

.form-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.action-btn {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
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

.action-btn.primary:hover {
  background-color: var(--color-chord-primary-dark);
}

.action-btn.danger {
  background-color: #dc2626;
  color: white;
}

.action-btn.danger:hover {
  background-color: #b91c1c;
}

.action-btn.secondary {
  background-color: var(--color-gray-100);
  color: var(--color-gray-700);
  border: 1px solid var(--color-gray-300);
}

.action-btn.secondary:hover {
  background-color: var(--color-gray-200);
}

/* 說明面板 */
.help-panel {
  position: absolute;
  top: 100%;
  right: 0;
  width: 300px;
  background: white;
  border: 1px solid var(--color-gray-200);
  border-top: none;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.help-content {
  padding: 1rem;
}

.help-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-gray-800);
  margin: 0 0 1rem 0;
}

.help-section {
  margin-bottom: 1rem;
}

.help-section h5 {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-gray-700);
  margin: 0 0 0.5rem 0;
}

.help-section ul {
  margin: 0;
  padding-left: 1.25rem;
  font-size: 0.75rem;
  color: var(--color-gray-600);
  line-height: 1.5;
}

.help-section li {
  margin-bottom: 0.25rem;
}

kbd {
  background-color: var(--color-gray-100);
  border: 1px solid var(--color-gray-300);
  border-radius: 0.25rem;
  padding: 0.125rem 0.25rem;
  font-family: monospace;
  font-size: 0.75rem;
}

.close-help-btn {
  width: 100%;
  padding: 0.5rem;
  background-color: var(--color-chord-primary);
  color: white;
  border: none;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
}

/* 錯誤提示 */
.error-toast {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background-color: #fef2f2;
  color: #dc2626;
  padding: 0.75rem;
  border-radius: 0.375rem;
  border: 1px solid #fecaca;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  z-index: 150;
  max-width: 300px;
}

.error-icon {
  flex-shrink: 0;
}

.error-text {
  flex: 1;
  font-size: 0.875rem;
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
  .lyrics-editor {
    height: 500px;
  }
  
  .editor-header {
    flex-direction: column;
    gap: 0.75rem;
    padding: 1rem;
  }
  
  .header-left,
  .header-right {
    width: 100%;
  }
  
  .header-right {
    justify-content: space-between;
  }
  
  .editor-body.split-view {
    flex-direction: column;
  }
  
  .editor-body.split-view .edit-panel,
  .editor-body.split-view .preview-panel {
    border-right: none;
    border-bottom: 1px solid var(--color-gray-200);
  }
  
  .editor-body.split-view .preview-panel {
    border-bottom: none;
  }
  
  .help-panel {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 90%;
    max-width: 400px;
  }
  
  .chord-palette-panel {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 90%;
    max-width: 400px;
    max-height: 70vh;
  }
}
</style>