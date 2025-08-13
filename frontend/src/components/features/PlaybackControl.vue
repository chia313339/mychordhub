<template>
  <div class="playback-control" :class="{ compact, vertical: layout === 'vertical' }">
    <!-- 播放控制標題 -->
    <div v-if="showTitle" class="control-header">
      <h3 class="control-title">播放控制</h3>
      <div class="control-status">
        <span class="status-indicator" :class="playbackStatus">
          {{ getStatusText() }}
        </span>
        <span v-if="currentTime > 0" class="time-display">
          {{ formatTime(currentTime) }} / {{ formatTime(totalTime) }}
        </span>
      </div>
    </div>

    <!-- 主控制面板 -->
    <div class="control-panel">
      <!-- 播放按鈕組 -->
      <div class="playback-buttons">
        <!-- 播放/暫停按鈕 -->
        <button
          @click="togglePlayback"
          :disabled="disabled"
          class="play-btn"
          :class="{ playing: isPlaying }"
          :title="isPlaying ? '暫停' : '播放'"
        >
          <svg v-if="!isPlaying" class="play-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h1m4 0h1m-6 4h8a2 2 0 002-2V8a2 2 0 00-2-2H8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
          </svg>
          
          <svg v-else class="pause-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </button>

        <!-- 停止按鈕 -->
        <button
          @click="stopPlayback"
          :disabled="disabled || !isPlaying"
          class="control-btn stop-btn"
          title="停止"
        >
          <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10h6v4H9z"/>
          </svg>
        </button>

        <!-- 重播按鈕 -->
        <button
          @click="restartPlayback"
          :disabled="disabled"
          class="control-btn restart-btn"
          title="重新開始"
        >
          <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
          </svg>
        </button>
      </div>

      <!-- 進度控制 -->
      <div v-if="showProgress" class="progress-section">
        <div class="progress-header">
          <span class="progress-label">播放進度</span>
          <span class="progress-percentage">{{ Math.round(progressPercentage) }}%</span>
        </div>
        
        <div class="progress-bar-container">
          <input
            v-model="progressValue"
            @input="handleProgressChange"
            type="range"
            min="0"
            max="100"
            step="1"
            class="progress-bar"
            :disabled="disabled || !hasContent"
          />
          
          <!-- 進度標記 -->
          <div v-if="showMarkers" class="progress-markers">
            <div
              v-for="marker in progressMarkers"
              :key="marker.id"
              class="progress-marker"
              :style="{ left: `${marker.position}%` }"
              :title="marker.label"
            >
              <div class="marker-dot"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 滾動控制面板 -->
    <div class="scroll-controls">
      <div class="control-group">
        <label class="control-label">
          <input
            v-model="autoScrollEnabled"
            @change="handleAutoScrollToggle"
            type="checkbox"
            class="control-checkbox"
            :disabled="disabled"
          />
          自動滾動
        </label>
      </div>

      <div class="control-group">
        <label class="control-label">滾動速度</label>
        <div class="speed-control">
          <button
            @click="decreaseSpeed"
            :disabled="disabled || !autoScrollEnabled || scrollSpeed <= minSpeed"
            class="speed-btn"
            title="減速"
          >
            <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4"/>
            </svg>
          </button>
          
          <div class="speed-display">
            <span class="speed-value">{{ scrollSpeed.toFixed(1) }}x</span>
            <input
              v-model.number="scrollSpeed"
              @input="handleSpeedChange"
              type="range"
              :min="minSpeed"
              :max="maxSpeed"
              step="0.1"
              class="speed-slider"
              :disabled="disabled || !autoScrollEnabled"
            />
          </div>
          
          <button
            @click="increaseSpeed"
            :disabled="disabled || !autoScrollEnabled || scrollSpeed >= maxSpeed"
            class="speed-btn"
            title="加速"
          >
            <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- BPM 控制 -->
      <div v-if="showBpmControl" class="control-group">
        <label class="control-label">節拍速度 (BPM)</label>
        <div class="bpm-control">
          <input
            v-model.number="currentBpm"
            @input="handleBpmChange"
            type="number"
            min="60"
            max="200"
            step="5"
            class="bpm-input"
            :disabled="disabled"
          />
          <span class="bpm-unit">BPM</span>
        </div>
      </div>
    </div>

    <!-- 高級控制選項 -->
    <div v-if="showAdvancedControls" class="advanced-controls">
      <div class="advanced-header">
        <button
          @click="showAdvanced = !showAdvanced"
          class="advanced-toggle"
          :class="{ expanded: showAdvanced }"
        >
          <span>進階選項</span>
          <svg class="toggle-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
          </svg>
        </button>
      </div>

      <div v-show="showAdvanced" class="advanced-panel">
        <div class="advanced-grid">
          <div class="control-group">
            <label class="control-label">
              <input
                v-model="loopMode"
                type="checkbox"
                class="control-checkbox"
                :disabled="disabled"
              />
              循環播放
            </label>
          </div>

          <div class="control-group">
            <label class="control-label">
              <input
                v-model="smoothScroll"
                type="checkbox"
                class="control-checkbox"
                :disabled="disabled"
              />
              平滑滾動
            </label>
          </div>

          <div class="control-group">
            <label class="control-label">
              <input
                v-model="highlightCurrentLine"
                type="checkbox"
                class="control-checkbox"
                :disabled="disabled"
              />
              高亮當前行
            </label>
          </div>

          <div class="control-group">
            <label class="control-label">
              <input
                v-model="pauseOnChordChange"
                type="checkbox"
                class="control-checkbox"
                :disabled="disabled"
              />
              和絃轉換時暫停
            </label>
          </div>
        </div>

        <!-- 預設速度按鈕 -->
        <div class="preset-speeds">
          <span class="preset-label">快速設定:</span>
          <button
            v-for="preset in speedPresets"
            :key="preset.value"
            @click="setPresetSpeed(preset.value)"
            :class="['preset-btn', { active: scrollSpeed === preset.value }]"
            :disabled="disabled || !autoScrollEnabled"
          >
            {{ preset.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- 狀態指示器 -->
    <div v-if="showStatusBar" class="status-bar">
      <div class="status-left">
        <div class="status-item">
          <span class="status-label">狀態:</span>
          <span class="status-value" :class="playbackStatus">
            {{ getStatusText() }}
          </span>
        </div>
        
        <div v-if="scrollPosition > 0" class="status-item">
          <span class="status-label">位置:</span>
          <span class="status-value">{{ scrollPosition }}px</span>
        </div>
      </div>

      <div class="status-right">
        <div v-if="estimatedDuration > 0" class="status-item">
          <span class="status-label">預估時長:</span>
          <span class="status-value">{{ formatTime(estimatedDuration) }}</span>
        </div>
      </div>
    </div>

    <!-- 錯誤提示 -->
    <div v-if="error" class="error-alert">
      <span class="error-icon">⚠️</span>
      <span class="error-text">{{ error }}</span>
      <button @click="clearError" class="error-dismiss">×</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

interface SpeedPreset {
  label: string
  value: number
}

interface ProgressMarker {
  id: string
  position: number
  label: string
  type: 'verse' | 'chorus' | 'bridge'
}

interface Props {
  layout?: 'horizontal' | 'vertical'
  compact?: boolean
  showTitle?: boolean
  showProgress?: boolean
  showMarkers?: boolean
  showBpmControl?: boolean
  showAdvancedControls?: boolean
  showStatusBar?: boolean
  disabled?: boolean
  hasContent?: boolean
  contentHeight?: number
  initialBpm?: number
  autoStart?: boolean
}

interface Emits {
  (e: 'play'): void
  (e: 'pause'): void
  (e: 'stop'): void
  (e: 'restart'): void
  (e: 'progress-change', progress: number): void
  (e: 'scroll-change', position: number): void
  (e: 'speed-change', speed: number): void
  (e: 'bpm-change', bpm: number): void
  (e: 'setting-change', settings: any): void
}

const props = withDefaults(defineProps<Props>(), {
  layout: 'horizontal',
  compact: false,
  showTitle: true,
  showProgress: true,
  showMarkers: false,
  showBpmControl: true,
  showAdvancedControls: true,
  showStatusBar: false,
  disabled: false,
  hasContent: true,
  contentHeight: 1000,
  initialBpm: 120,
  autoStart: false
})

const emit = defineEmits<Emits>()

// 響應式狀態
const isPlaying = ref(false)
const autoScrollEnabled = ref(false)
const scrollSpeed = ref(1.0)
const scrollPosition = ref(0)
const currentTime = ref(0)
const totalTime = ref(0)
const currentBpm = ref(props.initialBpm)
const progressValue = ref(0)
const showAdvanced = ref(false)
const error = ref('')

// 進階選項
const loopMode = ref(false)
const smoothScroll = ref(true)
const highlightCurrentLine = ref(false)
const pauseOnChordChange = ref(false)

// 播放狀態
const playbackStatus = ref<'stopped' | 'playing' | 'paused'>('stopped')

// 常數
const minSpeed = 0.1
const maxSpeed = 3.0
const speedStep = 0.1

// 速度預設
const speedPresets: SpeedPreset[] = [
  { label: '慢', value: 0.5 },
  { label: '正常', value: 1.0 },
  { label: '快', value: 1.5 },
  { label: '很快', value: 2.0 }
]

// 進度標記（示例）
const progressMarkers = ref<ProgressMarker[]>([
  { id: '1', position: 25, label: '第一段', type: 'verse' },
  { id: '2', position: 50, label: '副歌', type: 'chorus' },
  { id: '3', position: 75, label: '第二段', type: 'verse' }
])

// 計時器
let scrollTimer: number | null = null
let progressTimer: number | null = null

// 計算屬性
const progressPercentage = computed(() => {
  if (totalTime.value === 0) return 0
  return (currentTime.value / totalTime.value) * 100
})

const estimatedDuration = computed(() => {
  if (!props.contentHeight || scrollSpeed.value === 0) return 0
  // 根據內容高度和滾動速度估算播放時間
  return (props.contentHeight / (scrollSpeed.value * 50)) * 60 // 假設每秒滾動50px
})

// 方法
const togglePlayback = () => {
  if (isPlaying.value) {
    pausePlayback()
  } else {
    startPlayback()
  }
}

const startPlayback = () => {
  if (!props.hasContent) {
    error.value = '沒有內容可播放'
    return
  }

  isPlaying.value = true
  playbackStatus.value = 'playing'
  
  if (autoScrollEnabled.value) {
    startAutoScroll()
  }
  
  startProgressTimer()
  emit('play')
}

const pausePlayback = () => {
  isPlaying.value = false
  playbackStatus.value = 'paused'
  
  stopAutoScroll()
  stopProgressTimer()
  emit('pause')
}

const stopPlayback = () => {
  isPlaying.value = false
  playbackStatus.value = 'stopped'
  currentTime.value = 0
  progressValue.value = 0
  scrollPosition.value = 0
  
  stopAutoScroll()
  stopProgressTimer()
  emit('stop')
}

const restartPlayback = () => {
  stopPlayback()
  setTimeout(() => {
    startPlayback()
  }, 100)
  emit('restart')
}

const startAutoScroll = () => {
  if (!autoScrollEnabled.value || scrollTimer) return
  
  const scrollStep = smoothScroll.value ? 1 : 5
  const interval = smoothScroll.value ? 50 : 100
  
  scrollTimer = window.setInterval(() => {
    if (!isPlaying.value) return
    
    const increment = (scrollSpeed.value * scrollStep)
    scrollPosition.value += increment
    
    // 檢查是否到達底部
    if (scrollPosition.value >= (props.contentHeight || 1000)) {
      if (loopMode.value) {
        scrollPosition.value = 0
      } else {
        stopPlayback()
        return
      }
    }
    
    emit('scroll-change', scrollPosition.value)
  }, interval / scrollSpeed.value)
}

const stopAutoScroll = () => {
  if (scrollTimer) {
    clearInterval(scrollTimer)
    scrollTimer = null
  }
}

const startProgressTimer = () => {
  if (progressTimer) return
  
  progressTimer = window.setInterval(() => {
    if (!isPlaying.value) return
    
    currentTime.value += 0.1
    totalTime.value = estimatedDuration.value
    
    const percentage = (currentTime.value / totalTime.value) * 100
    progressValue.value = Math.min(percentage, 100)
    
    if (progressValue.value >= 100 && !loopMode.value) {
      stopPlayback()
    }
  }, 100)
}

const stopProgressTimer = () => {
  if (progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
  }
}

const handleAutoScrollToggle = () => {
  emit('setting-change', { autoScrollEnabled: autoScrollEnabled.value })
  
  if (isPlaying.value) {
    if (autoScrollEnabled.value) {
      startAutoScroll()
    } else {
      stopAutoScroll()
    }
  }
}

const handleSpeedChange = () => {
  emit('speed-change', scrollSpeed.value)
  emit('setting-change', { scrollSpeed: scrollSpeed.value })
  
  // 重新啟動自動滾動以應用新速度
  if (isPlaying.value && autoScrollEnabled.value) {
    stopAutoScroll()
    startAutoScroll()
  }
}

const handleProgressChange = () => {
  const newTime = (progressValue.value / 100) * totalTime.value
  currentTime.value = newTime
  
  // 根據進度計算滾動位置
  const newScrollPosition = (progressValue.value / 100) * (props.contentHeight || 1000)
  scrollPosition.value = newScrollPosition
  
  emit('progress-change', progressValue.value)
  emit('scroll-change', scrollPosition.value)
}

const handleBpmChange = () => {
  emit('bpm-change', currentBpm.value)
  emit('setting-change', { bpm: currentBpm.value })
}

const increaseSpeed = () => {
  if (scrollSpeed.value < maxSpeed) {
    scrollSpeed.value = Math.min(maxSpeed, scrollSpeed.value + speedStep)
    handleSpeedChange()
  }
}

const decreaseSpeed = () => {
  if (scrollSpeed.value > minSpeed) {
    scrollSpeed.value = Math.max(minSpeed, scrollSpeed.value - speedStep)
    handleSpeedChange()
  }
}

const setPresetSpeed = (speed: number) => {
  scrollSpeed.value = speed
  handleSpeedChange()
}

const getStatusText = () => {
  switch (playbackStatus.value) {
    case 'playing': return '播放中'
    case 'paused': return '已暫停'
    case 'stopped': return '已停止'
    default: return '就緒'
  }
}

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const clearError = () => {
  error.value = ''
}

// 監聽器
watch(() => props.contentHeight, () => {
  // 內容高度變化時重新計算總時間
  totalTime.value = estimatedDuration.value
})

// 生命週期
onMounted(() => {
  if (props.autoStart && props.hasContent) {
    setTimeout(() => {
      autoScrollEnabled.value = true
      startPlayback()
    }, 500)
  }
})

onUnmounted(() => {
  stopAutoScroll()
  stopProgressTimer()
})

// 快捷鍵支持
const handleKeyPress = (event: KeyboardEvent) => {
  if (props.disabled) return
  
  switch (event.code) {
    case 'Space':
      event.preventDefault()
      togglePlayback()
      break
    case 'ArrowUp':
      event.preventDefault()
      increaseSpeed()
      break
    case 'ArrowDown':
      event.preventDefault()
      decreaseSpeed()
      break
    case 'Escape':
      event.preventDefault()
      stopPlayback()
      break
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeyPress)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyPress)
})
</script>

<style scoped>
.playback-control {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  padding: 1.5rem;
  border: 1px solid var(--color-gray-200);
  user-select: none;
}

.playback-control.compact {
  padding: 1rem;
}

.playback-control.vertical {
  display: flex;
  flex-direction: column;
}

/* 控制標題 */
.control-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--color-gray-200);
}

.control-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-gray-900);
  margin: 0;
}

.control-status {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
  font-size: 0.75rem;
}

.status-indicator {
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.status-indicator.playing {
  background-color: #dcfce7;
  color: #166534;
}

.status-indicator.paused {
  background-color: #fef3c7;
  color: #92400e;
}

.status-indicator.stopped {
  background-color: var(--color-gray-100);
  color: var(--color-gray-600);
}

.time-display {
  color: var(--color-gray-500);
  font-family: monospace;
}

/* 控制面板 */
.control-panel {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.playback-buttons {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  justify-content: center;
}

.play-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 4rem;
  height: 4rem;
  border: none;
  border-radius: 50%;
  background-color: var(--color-chord-primary);
  color: white;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.play-btn:hover:not(:disabled) {
  background-color: var(--color-chord-primary-dark);
  transform: scale(1.05);
}

.play-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.play-btn.playing {
  background-color: #f59e0b;
}

.play-icon,
.pause-icon {
  width: 1.5rem;
  height: 1.5rem;
}

.control-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border: 1px solid var(--color-gray-300);
  border-radius: 50%;
  background: white;
  color: var(--color-gray-600);
  cursor: pointer;
  transition: all 0.2s;
}

.control-btn:hover:not(:disabled) {
  border-color: var(--color-chord-primary);
  color: var(--color-chord-primary);
  background-color: var(--color-gray-50);
}

.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon {
  width: 1rem;
  height: 1rem;
}

/* 進度控制 */
.progress-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
}

.progress-label {
  color: var(--color-gray-700);
  font-weight: 500;
}

.progress-percentage {
  color: var(--color-chord-primary);
  font-weight: 600;
  font-family: monospace;
}

.progress-bar-container {
  position: relative;
  display: flex;
  align-items: center;
}

.progress-bar {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: var(--color-gray-200);
  outline: none;
  cursor: pointer;
  -webkit-appearance: none;
  appearance: none;
}

.progress-bar::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--color-chord-primary);
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
}

.progress-bar::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--color-chord-primary);
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  border: none;
}

.progress-markers {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 6px;
  pointer-events: none;
}

.progress-marker {
  position: absolute;
  top: -2px;
  transform: translateX(-50%);
}

.marker-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: var(--color-chord-accent);
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* 滾動控制 */
.scroll-controls {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  background-color: var(--color-gray-50);
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.control-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-gray-700);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.control-checkbox {
  width: 1rem;
  height: 1rem;
}

.speed-control {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.speed-btn {
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
}

.speed-btn:hover:not(:disabled) {
  border-color: var(--color-chord-primary);
  color: var(--color-chord-primary);
}

.speed-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.speed-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.speed-value {
  font-weight: 600;
  color: var(--color-chord-primary);
  font-family: monospace;
  font-size: 0.875rem;
}

.speed-slider {
  width: 100%;
  height: 4px;
  border-radius: 2px;
  background: var(--color-gray-200);
  outline: none;
  cursor: pointer;
  -webkit-appearance: none;
  appearance: none;
}

.speed-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--color-chord-primary);
  cursor: pointer;
}

.speed-slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--color-chord-primary);
  cursor: pointer;
  border: none;
}

.bpm-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.bpm-input {
  width: 80px;
  padding: 0.5rem;
  border: 1px solid var(--color-gray-300);
  border-radius: 0.25rem;
  font-size: 0.875rem;
  text-align: center;
}

.bpm-input:focus {
  outline: none;
  border-color: var(--color-chord-primary);
}

.bpm-unit {
  font-size: 0.75rem;
  color: var(--color-gray-500);
  font-weight: 500;
}

/* 進階控制 */
.advanced-controls {
  border-top: 1px solid var(--color-gray-200);
  padding-top: 1rem;
}

.advanced-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: 0.5rem;
  background: var(--color-gray-100);
  color: var(--color-gray-700);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.advanced-toggle:hover {
  background: var(--color-gray-200);
}

.advanced-toggle.expanded {
  background: var(--color-chord-primary);
  color: white;
}

.toggle-icon {
  width: 1rem;
  height: 1rem;
  transform: rotate(0deg);
  transition: transform 0.2s;
}

.advanced-toggle.expanded .toggle-icon {
  transform: rotate(180deg);
}

.advanced-panel {
  padding: 1rem 0;
}

.advanced-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.preset-speeds {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.preset-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-gray-700);
}

.preset-btn {
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

.preset-btn:hover:not(:disabled) {
  border-color: var(--color-chord-primary);
  color: var(--color-chord-primary);
}

.preset-btn.active {
  background: var(--color-chord-primary);
  color: white;
  border-color: var(--color-chord-primary);
}

.preset-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 狀態列 */
.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: var(--color-gray-50);
  border-radius: 0.375rem;
  font-size: 0.75rem;
  color: var(--color-gray-600);
}

.status-left,
.status-right {
  display: flex;
  gap: 1rem;
}

.status-item {
  display: flex;
  gap: 0.25rem;
}

.status-label {
  font-weight: 500;
}

.status-value {
  font-weight: 600;
  font-family: monospace;
}

/* 錯誤提示 */
.error-alert {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #fef2f2;
  color: #dc2626;
  padding: 0.75rem;
  border-radius: 0.375rem;
  border: 1px solid #fecaca;
  font-size: 0.875rem;
  margin-top: 1rem;
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
  .playback-control {
    padding: 1rem;
  }
  
  .control-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
  
  .playback-buttons {
    gap: 0.5rem;
  }
  
  .play-btn {
    width: 3.5rem;
    height: 3.5rem;
  }
  
  .control-btn {
    width: 2rem;
    height: 2rem;
  }
  
  .scroll-controls {
    gap: 0.75rem;
  }
  
  .speed-control {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }
  
  .advanced-grid {
    grid-template-columns: 1fr;
  }
  
  .preset-speeds {
    justify-content: center;
  }
  
  .status-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }
  
  .status-left,
  .status-right {
    justify-content: space-between;
  }
}

/* 動畫效果 */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.status-indicator.playing {
  animation: pulse 2s ease-in-out infinite;
}

/* 禁用狀態 */
.playback-control[disabled] {
  opacity: 0.6;
  pointer-events: none;
}
</style>