<template>
  <div class="chord-diagram-container">
    <svg
      :width="options.width"
      :height="options.height"
      :viewBox="`0 0 ${options.width} ${options.height}`"
      class="chord-diagram-svg"
    >
      <!-- 琴格背景 -->
      <g class="fretboard">
        <!-- 垂直線 (弦) -->
        <g class="strings">
          <line
            v-for="string in 6"
            :key="`string-${string}`"
            :x1="stringSpacing * (string - 1) + marginLeft"
            :y1="marginTop"
            :x2="stringSpacing * (string - 1) + marginLeft"
            :y2="marginTop + fretboardHeight"
            stroke="#666"
            :stroke-width="string === 1 || string === 6 ? 2 : 1.5"
            class="string-line"
          />
        </g>

        <!-- 水平線 (品) -->
        <g class="frets">
          <line
            v-for="fret in options.frets + 1"
            :key="`fret-${fret}`"
            :x1="marginLeft"
            :y1="fretSpacing * (fret - 1) + marginTop"
            :x2="marginLeft + fretboardWidth"
            :y2="fretSpacing * (fret - 1) + marginTop"
            stroke="#333"
            :stroke-width="fret === 1 ? 4 : 2"
            class="fret-line"
          />
        </g>

        <!-- 品位數字 -->
        <g v-if="options.showFretNumbers" class="fret-numbers">
          <text
            v-for="fret in options.frets"
            :key="`fret-num-${fret}`"
            :x="marginLeft + fretboardWidth + 10"
            :y="fretSpacing * (fret - 0.5) + marginTop + 4"
            font-family="sans-serif"
            font-size="12"
            fill="#666"
            class="fret-number"
          >
            {{ fret }}
          </text>
        </g>
      </g>

      <!-- 弦名 -->
      <g v-if="options.showStringNames" class="string-names">
        <text
          v-for="(stringName, index) in stringNames"
          :key="`string-name-${index}`"
          :x="stringSpacing * index + marginLeft"
          :y="marginTop - 8"
          font-family="sans-serif"
          font-size="12"
          font-weight="600"
          fill="#333"
          text-anchor="middle"
          class="string-name"
        >
          {{ stringName }}
        </text>
      </g>

      <!-- 手指按壓點 -->
      <g class="finger-positions">
        <g
          v-for="(fret, stringIndex) in fingering.frets"
          :key="`finger-${stringIndex}`"
        >
          <!-- 按壓點圓圈 -->
          <circle
            v-if="fret > 0"
            :cx="stringSpacing * stringIndex + marginLeft"
            :cy="fretSpacing * (fret - 0.5) + marginTop"
            :r="fingerDotRadius"
            :fill="getFingerColor(fingering.fingers[stringIndex])"
            stroke="white"
            stroke-width="2"
            class="finger-dot"
          />
          
          <!-- 開放弦標記 -->
          <circle
            v-else-if="fret === 0"
            :cx="stringSpacing * stringIndex + marginLeft"
            :cy="marginTop - 20"
            r="6"
            fill="none"
            stroke="#28a745"
            stroke-width="2"
            class="open-string"
          />
          
          <!-- 不彈弦標記 -->
          <g v-else-if="fret === -1">
            <line
              :x1="stringSpacing * stringIndex + marginLeft - 4"
              :y1="marginTop - 16"
              :x2="stringSpacing * stringIndex + marginLeft + 4"
              :y2="marginTop - 24"
              stroke="#dc3545"
              stroke-width="2"
              class="muted-string"
            />
            <line
              :x1="stringSpacing * stringIndex + marginLeft - 4"
              :y1="marginTop - 24"
              :x2="stringSpacing * stringIndex + marginLeft + 4"
              :y2="marginTop - 16"
              stroke="#dc3545"
              stroke-width="2"
              class="muted-string"
            />
          </g>
        </g>
      </g>

      <!-- 手指編號 -->
      <g v-if="options.showFingers" class="finger-numbers">
        <text
          v-for="(finger, stringIndex) in fingering.fingers"
          :key="`finger-num-${stringIndex}`"
          v-show="finger > 0 && fingering.frets[stringIndex] > 0"
          :x="stringSpacing * stringIndex + marginLeft"
          :y="fretSpacing * (fingering.frets[stringIndex] - 0.5) + marginTop + 4"
          font-family="sans-serif"
          font-size="12"
          font-weight="bold"
          fill="white"
          text-anchor="middle"
          class="finger-number"
        >
          {{ finger }}
        </text>
      </g>

      <!-- 封閉和絃線 -->
      <g class="barre-lines">
        <line
          v-for="barre in barreLines"
          :key="`barre-${barre.fret}-${barre.startString}-${barre.endString}`"
          :x1="stringSpacing * barre.startString + marginLeft"
          :y1="fretSpacing * (barre.fret - 0.5) + marginTop"
          :x2="stringSpacing * barre.endString + marginLeft"
          :y2="fretSpacing * (barre.fret - 0.5) + marginTop"
          stroke="#333"
          stroke-width="6"
          stroke-linecap="round"
          opacity="0.7"
          class="barre-line"
        />
      </g>

      <!-- 起始品位標記 -->
      <g v-if="startingFret > 1" class="starting-fret">
        <text
          :x="marginLeft - 20"
          :y="marginTop + fretSpacing * 0.5 + 4"
          font-family="sans-serif"
          font-size="14"
          font-weight="bold"
          fill="#333"
          text-anchor="middle"
          class="starting-fret-number"
        >
          {{ startingFret }}fr
        </text>
      </g>
    </svg>

    <!-- 圖例說明 -->
    <div v-if="showLegend" class="diagram-legend">
      <div class="legend-item">
        <div class="legend-symbol open-circle"></div>
        <span>開放弦</span>
      </div>
      <div class="legend-item">
        <div class="legend-symbol muted-x">×</div>
        <span>不彈</span>
      </div>
      <div class="legend-item">
        <div class="legend-symbol finger-dot"></div>
        <span>按壓</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { FingeringPattern, TabRenderOptions } from '@/types/music'

interface Props {
  fingering: FingeringPattern | null
  options?: TabRenderOptions
  showLegend?: boolean
}

interface Emits {
  (e: 'fingering-change', fingering: FingeringPattern): void
}

const props = withDefaults(defineProps<Props>(), {
  options: () => ({
    frets: 5,
    showFretNumbers: true,
    showFingers: true,
    showStringNames: true,
    width: 160,
    height: 200
  }),
  showLegend: false
})

const emit = defineEmits<Emits>()

// 常數
const stringNames = ['E', 'A', 'D', 'G', 'B', 'E']
const fingerColors = ['#666', '#e74c3c', '#f39c12', '#2ecc71', '#3498db', '#9b59b6']

// 計算佈局尺寸
const marginLeft = computed(() => 30)
const marginTop = computed(() => 40)
const marginRight = computed(() => 30)
const marginBottom = computed(() => 20)

const fretboardWidth = computed(() => 
  (props.options?.width || 160) - marginLeft.value - marginRight.value
)

const fretboardHeight = computed(() => 
  (props.options?.height || 200) - marginTop.value - marginBottom.value
)

const stringSpacing = computed(() => fretboardWidth.value / 5)
const fretSpacing = computed(() => fretboardHeight.value / (props.options?.frets || 5))
const fingerDotRadius = computed(() => Math.min(stringSpacing.value * 0.3, 12))

// 計算起始品位
const startingFret = computed(() => {
  if (!props.fingering) return 1
  const validFrets = props.fingering.frets.filter(f => f > 0)
  if (validFrets.length === 0) return 1
  return Math.min(...validFrets)
})

// 計算封閉和絃線
const barreLines = computed(() => {
  if (!props.fingering) return []
  
  const lines = []
  const { frets, fingers } = props.fingering
  
  // 檢查每個手指是否形成封閉
  for (let finger = 1; finger <= 4; finger++) {
    const fingerPositions = fingers
      .map((f, i) => ({ finger: f, string: i, fret: frets[i] }))
      .filter(pos => pos.finger === finger && pos.fret > 0)
    
    if (fingerPositions.length >= 2) {
      // 檢查是否在同一品位
      const sameFret = fingerPositions.every(pos => pos.fret === fingerPositions[0].fret)
      
      if (sameFret) {
        const startString = Math.min(...fingerPositions.map(pos => pos.string))
        const endString = Math.max(...fingerPositions.map(pos => pos.string))
        
        // 檢查中間是否有其他手指阻擋
        let isBarre = true
        for (let string = startString + 1; string < endString; string++) {
          if (fingers[string] > 0 && fingers[string] !== finger && frets[string] < fingerPositions[0].fret) {
            isBarre = false
            break
          }
        }
        
        if (isBarre && endString - startString >= 2) {
          lines.push({
            fret: fingerPositions[0].fret,
            startString,
            endString
          })
        }
      }
    }
  }
  
  return lines
})

// 方法
const getFingerColor = (fingerNumber: number): string => {
  return fingerColors[fingerNumber] || fingerColors[0]
}
</script>

<style scoped>
.chord-diagram-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.chord-diagram-svg {
  background-color: #fafafa;
  border-radius: 0.5rem;
  border: 1px solid var(--color-gray-200);
}

/* SVG 元素樣式 */
.string-line {
  transition: stroke 0.2s;
}

.string-line:hover {
  stroke: var(--color-chord-primary);
}

.fret-line {
  transition: stroke 0.2s;
}

.finger-dot {
  transition: all 0.2s;
  cursor: pointer;
}

.finger-dot:hover {
  transform: scale(1.1);
  filter: brightness(1.1);
}

.open-string {
  transition: all 0.2s;
}

.muted-string {
  transition: stroke 0.2s;
}

.finger-number {
  pointer-events: none;
  user-select: none;
}

.string-name {
  font-weight: 600;
  transition: fill 0.2s;
}

.fret-number {
  transition: fill 0.2s;
}

.starting-fret-number {
  font-weight: bold;
  transition: fill 0.2s;
}

.barre-line {
  transition: all 0.2s;
}

/* 圖例樣式 */
.diagram-legend {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: var(--color-gray-600);
  justify-content: center;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.legend-symbol {
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.legend-symbol.open-circle {
  border: 2px solid #28a745;
  border-radius: 50%;
  background: white;
}

.legend-symbol.muted-x {
  color: #dc3545;
  font-size: 14px;
  font-weight: bold;
}

.legend-symbol.finger-dot {
  background: #333;
  border-radius: 50%;
  border: 2px solid white;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .diagram-legend {
    font-size: 0.7rem;
    gap: 0.75rem;
  }
  
  .legend-item {
    gap: 0.25rem;
  }
  
  .legend-symbol {
    width: 14px;
    height: 14px;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .chord-diagram-svg {
    background-color: #2a2a2a;
    border-color: #404040;
  }
  
  .string-name,
  .fret-number,
  .starting-fret-number {
    fill: #e0e0e0;
  }
  
  .string-line {
    stroke: #888;
  }
  
  .fret-line {
    stroke: #bbb;
  }
}

/* 動畫效果 */
@keyframes fingerPress {
  0% { transform: scale(1); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

.finger-dot.animate {
  animation: fingerPress 0.3s ease-in-out;
}

/* 互動式效果 */
.chord-diagram-svg:hover .string-line {
  opacity: 0.8;
}

.chord-diagram-svg:hover .fret-line {
  opacity: 0.8;
}

/* 可訪問性 */
.chord-diagram-svg {
  outline: none;
}

.chord-diagram-svg:focus {
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.3);
}

/* 列印樣式 */
@media print {
  .chord-diagram-svg {
    background-color: white;
    border: 1px solid black;
  }
  
  .string-line,
  .fret-line {
    stroke: black;
  }
  
  .finger-dot {
    fill: black;
    stroke: white;
  }
}
</style>