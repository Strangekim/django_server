<template>
  <div class="memo-canvas">
    <!-- 최상단 헤더 표시 -->
    <div class="page-header" :class="{ visible: scrollY < 50 }">
      <div class="header-line"></div>
    </div>

    <!-- 노트북 배경 (전체 스크롤 영역) -->
    <div class="notebook-background" :style="{
      height: canvasHeight + 'px',
      transform: `translateY(${-scrollY}px)`
    }"></div>

    <!-- 캔버스 -->
    <canvas
      ref="canvasRef"
      class="drawing-canvas"
      :class="{ 'eraser-cursor': currentTool === 'eraser' }"
      @pointerdown="handlePointerDown"
      @pointermove="handlePointerMove"
      @pointerup="handlePointerUp"
      @pointercancel="handlePointerUp"
    ></canvas>

    <!-- 캔버스 가이드 -->
    <div v-if="strokes.length === 0 && !isDrawing" class="canvas-guide">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
        <path d="M17 3C17.5304 3 18.0391 3.21071 18.4142 3.58579C18.7893 3.96086 19 4.46957 19 5C19 5.53043 18.7893 6.03914 18.4142 6.41421L10.5 14.3L7.70711 11.5071C7.31658 11.1166 7.31658 10.4834 7.70711 10.0929L15.5858 2.20711C15.9609 1.83204 16.4696 1.62132 17 1.62132C17.5304 1.62132 18.0391 1.83204 18.4142 2.20711L21.7929 5.58579C22.1834 5.97631 22.1834 6.60948 21.7929 7L14.3 14.5L12 21L6.2 15.2C5.4 14.4 5.4 13.1 6.2 12.3L14.1 4.4C14.5 4 15 3.8 15.5 3.8C16 3.8 16.5 4 16.9 4.4L17 3Z" stroke="currentColor" stroke-width="2"/>
      </svg>
      <p>여기서 자유롭게 메모하고 계산해보세요</p>
    </div>

    <!-- 스크롤 위치 인디케이터 (우측) -->
    <div class="scroll-indicator">
      <div class="scroll-track">
        <div
          class="scroll-thumb"
          :style="{
            height: scrollThumbHeight + '%',
            top: scrollThumbPosition + '%'
          }"
        ></div>
      </div>
      <div class="scroll-label">{{ scrollPercentage }}%</div>
    </div>

    <!-- 우하단 정답 제출 버튼 -->
    <button class="submit-button" @click="handleSubmit" title="정답 제출">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2"/>
      </svg>
      <span>정답 제출</span>
    </button>

    <!-- 하단 툴바 -->
    <div class="toolbar">
      <!-- 도구 선택 -->
      <div class="tool-group">
        <button
          class="tool-button"
          :class="{ active: currentTool === 'pen' }"
          @click="selectTool('pen')"
          title="펜"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path d="M17 3C17.5304 3 18.0391 3.21071 18.4142 3.58579C18.7893 3.96086 19 4.46957 19 5C19 5.53043 18.7893 6.03914 18.4142 6.41421L10.5 14.3L7.70711 11.5071C7.31658 11.1166 7.31658 10.4834 7.70711 10.0929L15.5858 2.20711C15.9609 1.83204 16.4696 1.62132 17 1.62132C17.5304 1.62132 18.0391 1.83204 18.4142 2.20711L21.7929 5.58579C22.1834 5.97631 22.1834 6.60948 21.7929 7L14.3 14.5L12 21L6.2 15.2C5.4 14.4 5.4 13.1 6.2 12.3L14.1 4.4C14.5 4 15 3.8 15.5 3.8C16 3.8 16.5 4 16.9 4.4L17 3Z" stroke="currentColor" stroke-width="2"/>
          </svg>
        </button>
        <button
          class="tool-button"
          :class="{ active: currentTool === 'eraser' }"
          @click="selectTool('eraser')"
          title="지우개"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path d="M20 20H8L2.6 14.6C2.4 14.4 2.4 14.1 2.6 13.9L8.9 7.6C9.1 7.4 9.4 7.4 9.6 7.6L16.4 14.4C16.6 14.6 16.6 14.9 16.4 15.1L11 20.5H20V20Z" stroke="currentColor" stroke-width="2"/>
          </svg>
        </button>
      </div>

      <!-- 색상 선택 -->
      <div class="tool-group">
        <input
          type="color"
          v-model="currentColor"
          class="color-picker"
          title="색상"
        >
        <div class="color-presets">
          <button
            v-for="color in colorPresets"
            :key="color"
            class="color-preset"
            :style="{ backgroundColor: color }"
            :class="{ active: currentColor === color }"
            @click="currentColor = color"
          ></button>
        </div>
      </div>

      <!-- 선 굵기 -->
      <div class="tool-group">
        <input
          type="range"
          v-model.number="strokeWidth"
          min="1"
          max="20"
          class="stroke-width-slider"
          title="선 굵기"
        >
        <span class="stroke-width-label">{{ strokeWidth }}px</span>
      </div>

      <!-- 편집 버튼 -->
      <div class="tool-group">
        <button
          class="tool-button"
          :disabled="!canUndo"
          @click="undo"
          title="실행 취소"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path d="M3 7V3H7" stroke="currentColor" stroke-width="2"/>
            <path d="M3.05115 6.39892C4.62949 3.75965 7.49854 2 11 2C15.9706 2 20 6.02944 20 11V13" stroke="currentColor" stroke-width="2"/>
          </svg>
        </button>
        <button
          class="tool-button"
          :disabled="!canRedo"
          @click="redo"
          title="다시 실행"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path d="M21 7V3H17" stroke="currentColor" stroke-width="2"/>
            <path d="M20.9489 6.39892C19.3705 3.75965 16.5015 2 13 2C8.02944 2 4 6.02944 4 11V13" stroke="currentColor" stroke-width="2"/>
          </svg>
        </button>
        <button
          class="tool-button"
          @click="clearAll"
          title="전체 지우기"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path d="M3 6H5H21" stroke="currentColor" stroke-width="2"/>
            <path d="M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6H19Z" stroke="currentColor" stroke-width="2"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, defineExpose, defineEmits } from 'vue'

// Emit 정의
const emit = defineEmits(['submitAnswer'])

// ============================================
// State
// ============================================

const canvasRef = ref(null)
const ctx = ref(null)

// 도구 및 설정
const currentTool = ref('pen')
const currentColor = ref('#000000')
const strokeWidth = ref(2)

const colorPresets = ['#000000', '#FF0000', '#0000FF', '#00AA00', '#FF6600', '#9900FF']

// 그리기 상태
const isDrawing = ref(false)
const strokes = ref([])
const currentStroke = ref(null)

// 스크롤 상태
const scrollY = ref(0)
const canvasHeight = ref(5000) // 가상 캔버스 높이 (스크롤 가능 영역) - 증가

// 히스토리
const history = ref([])
const historyIndex = ref(-1)

// 세션 정보
const sessionStartTime = ref(Date.now())
const sessionId = ref(crypto.randomUUID())

// Computed
const canUndo = computed(() => historyIndex.value > 0)
const canRedo = computed(() => historyIndex.value < history.value.length - 1)

// 스크롤 인디케이터 computed
const scrollPercentage = computed(() => {
  const canvas = canvasRef.value
  if (!canvas) return 0
  const maxScroll = canvasHeight.value - canvas.height
  if (maxScroll <= 0) return 0
  return Math.round((scrollY.value / maxScroll) * 100)
})

const scrollThumbHeight = computed(() => {
  const canvas = canvasRef.value
  if (!canvas) return 100
  return Math.max(10, (canvas.height / canvasHeight.value) * 100)
})

const scrollThumbPosition = computed(() => {
  const canvas = canvasRef.value
  if (!canvas) return 0
  const maxScroll = canvasHeight.value - canvas.height
  if (maxScroll <= 0) return 0
  const maxThumbPosition = 100 - scrollThumbHeight.value
  return (scrollY.value / maxScroll) * maxThumbPosition
})

// ============================================
// Canvas 초기화
// ============================================

onMounted(() => {
  if (!canvasRef.value) return

  const canvas = canvasRef.value
  ctx.value = canvas.getContext('2d', { willReadFrequently: true })

  // 캔버스 크기 설정
  resizeCanvas()

  // 윈도우 리사이즈 이벤트
  window.addEventListener('resize', resizeCanvas)

  // 휠 이벤트 (스크롤)
  canvas.addEventListener('wheel', handleWheel, { passive: false })

  // 초기 히스토리 저장
  saveHistory()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCanvas)
  if (canvasRef.value) {
    canvasRef.value.removeEventListener('wheel', handleWheel)
  }
})

function resizeCanvas() {
  const canvas = canvasRef.value
  if (!canvas) return

  const container = canvas.parentElement
  canvas.width = container.clientWidth
  canvas.height = container.clientHeight

  render()
}

// ============================================
// 스크롤 처리
// ============================================

function handleWheel(event) {
  event.preventDefault()

  // 스크롤 양 계산 (deltaY 사용)
  const delta = event.deltaY

  // 스크롤 업데이트 (상하만 허용)
  scrollY.value += delta

  // 스크롤 범위 제한
  const canvas = canvasRef.value
  const maxScroll = canvasHeight.value - canvas.height
  scrollY.value = Math.max(0, Math.min(scrollY.value, maxScroll))

  // 배경 스크롤 업데이트
  updateBackgroundScroll()

  // 재렌더링
  render()
}

function updateBackgroundScroll() {
  // Vue의 반응형 바인딩으로 자동 업데이트됨
}

// ============================================
// 좌표 계산
// ============================================

function getCoordinates(event) {
  const canvas = canvasRef.value
  const rect = canvas.getBoundingClientRect()

  let clientX, clientY

  if (event.touches && event.touches.length > 0) {
    clientX = event.touches[0].clientX
    clientY = event.touches[0].clientY
  } else if (event.changedTouches && event.changedTouches.length > 0) {
    clientX = event.changedTouches[0].clientX
    clientY = event.changedTouches[0].clientY
  } else {
    clientX = event.clientX
    clientY = event.clientY
  }

  // 스크린 좌표를 캔버스 좌표로 변환
  // CSS 크기와 실제 캔버스 크기의 비율 계산
  const scaleX = canvas.width / rect.width
  const scaleY = canvas.height / rect.height

  const x = (clientX - rect.left) * scaleX
  const y = (clientY - rect.top) * scaleY + scrollY.value // 스크롤 오프셋 추가

  return {
    x: x,
    y: y,
    pressure: event.pressure || 0.5,
    tiltX: event.tiltX || 0,
    tiltY: event.tiltY || 0,
    twist: event.twist || 0,
    pointerType: event.pointerType || 'mouse'
  }
}

// ============================================
// 그리기 이벤트
// ============================================

function handlePointerDown(event) {
  event.preventDefault()

  isDrawing.value = true

  const point = getCoordinates(event)
  currentStroke.value = {
    id: crypto.randomUUID(),
    tool: currentTool.value,
    color: currentColor.value,
    strokeWidth: strokeWidth.value,
    points: [point],
    startTime: Date.now() - sessionStartTime.value
  }

  // Pointer capture
  if (canvasRef.value && event.pointerId !== undefined) {
    try {
      canvasRef.value.setPointerCapture(event.pointerId)
    } catch (e) {
      console.warn('setPointerCapture failed:', e)
    }
  }

  render()
}

function handlePointerMove(event) {
  if (!isDrawing.value) return

  event.preventDefault()

  // Coalesced events 처리 (고주파수 데이터)
  const coalescedEvents = event.getCoalescedEvents ? event.getCoalescedEvents() : [event]

  coalescedEvents.forEach(evt => {
    const point = getCoordinates(evt)
    currentStroke.value.points.push(point)
  })

  // 즉시 렌더링
  requestAnimationFrame(render)
}

function handlePointerUp(event) {
  if (!isDrawing.value) return

  event.preventDefault()

  // 스트로크 종료
  currentStroke.value.endTime = Date.now() - sessionStartTime.value

  // 통계 계산
  calculateStrokeStats(currentStroke.value)

  // 스트로크 저장
  strokes.value.push(currentStroke.value)

  // 히스토리 저장
  saveHistory()

  // Pointer release
  if (canvasRef.value && event.pointerId !== undefined) {
    try {
      canvasRef.value.releasePointerCapture(event.pointerId)
    } catch (e) {
      // Ignore
    }
  }

  currentStroke.value = null
  isDrawing.value = false

  render()
}

// ============================================
// 통계 계산
// ============================================

function calculateStrokeStats(stroke) {
  if (!stroke || stroke.points.length === 0) return

  let totalDistance = 0
  for (let i = 1; i < stroke.points.length; i++) {
    const p1 = stroke.points[i - 1]
    const p2 = stroke.points[i]
    const dx = p2.x - p1.x
    const dy = p2.y - p1.y
    totalDistance += Math.sqrt(dx * dx + dy * dy)
  }

  const duration = stroke.endTime - stroke.startTime
  const averageSpeed = duration > 0 ? totalDistance / duration : 0

  const pressureValues = stroke.points.map(p => p.pressure).filter(p => p > 0)
  const averagePressure = pressureValues.length > 0
    ? pressureValues.reduce((a, b) => a + b, 0) / pressureValues.length
    : 0

  stroke.totalDistance = totalDistance
  stroke.averageSpeed = averageSpeed
  stroke.averagePressure = averagePressure

  // Bounding box
  const xs = stroke.points.map(p => p.x)
  const ys = stroke.points.map(p => p.y)
  stroke.boundingBox = [
    Math.min(...xs),
    Math.min(...ys),
    Math.max(...xs),
    Math.max(...ys)
  ]
}

// ============================================
// 렌더링
// ============================================

function render() {
  const canvas = canvasRef.value
  if (!canvas || !ctx.value) return

  // 캔버스 초기화
  ctx.value.clearRect(0, 0, canvas.width, canvas.height)

  // 완료된 스트로크 그리기
  strokes.value.forEach(drawStroke)

  // 현재 그리는 중인 스트로크 그리기
  if (currentStroke.value) {
    drawStroke(currentStroke.value)
  }
}

function drawStroke(stroke) {
  if (!stroke || !stroke.points || stroke.points.length === 0) return

  ctx.value.save()

  if (stroke.tool === 'eraser') {
    ctx.value.globalCompositeOperation = 'destination-out'
    ctx.value.lineWidth = 20
  } else {
    ctx.value.strokeStyle = stroke.color
    ctx.value.lineWidth = stroke.strokeWidth
  }

  ctx.value.lineCap = 'round'
  ctx.value.lineJoin = 'round'
  ctx.value.beginPath()

  const firstPoint = stroke.points[0]
  // 스크롤 오프셋을 빼서 화면 좌표로 변환
  ctx.value.moveTo(firstPoint.x, firstPoint.y - scrollY.value)

  stroke.points.forEach((point, index) => {
    if (index > 0) {
      // 필압 적용
      if (point.pressure > 0 && stroke.tool !== 'eraser') {
        const pressureWidth = stroke.strokeWidth * (0.5 + point.pressure * 0.5)
        ctx.value.lineWidth = pressureWidth
      }

      // 스크롤 오프셋을 빼서 화면 좌표로 변환
      ctx.value.lineTo(point.x, point.y - scrollY.value)
    }
  })

  ctx.value.stroke()
  ctx.value.restore()
}

// ============================================
// 도구 선택
// ============================================

function selectTool(tool) {
  currentTool.value = tool
}

// ============================================
// 히스토리 (Undo/Redo)
// ============================================

function saveHistory() {
  // 현재 위치 이후의 히스토리 제거
  history.value = history.value.slice(0, historyIndex.value + 1)

  // 현재 상태 저장 (deep copy)
  history.value.push(JSON.parse(JSON.stringify(strokes.value)))
  historyIndex.value++

  // 히스토리 길이 제한 (50개)
  if (history.value.length > 50) {
    history.value.shift()
    historyIndex.value--
  }
}

function undo() {
  if (historyIndex.value > 0) {
    historyIndex.value--
    strokes.value = JSON.parse(JSON.stringify(history.value[historyIndex.value]))
    render()
  }
}

function redo() {
  if (historyIndex.value < history.value.length - 1) {
    historyIndex.value++
    strokes.value = JSON.parse(JSON.stringify(history.value[historyIndex.value]))
    render()
  }
}

function clearAll() {
  if (confirm('전체 내용을 지우시겠습니까?')) {
    strokes.value = []
    saveHistory()
    render()
  }
}

// ============================================
// 백엔드 전송용 데이터
// ============================================

function getSubmissionData() {
  return {
    sessionId: sessionId.value,
    startTime: sessionStartTime.value,
    strokes: strokes.value,
    stats: {
      strokeCount: strokes.value.length,
      totalDistance: strokes.value.reduce((sum, s) => sum + (s.totalDistance || 0), 0),
      averageStrokeLength: strokes.value.length > 0
        ? strokes.value.reduce((sum, s) => sum + (s.totalDistance || 0), 0) / strokes.value.length
        : 0
    },
    capabilities: {
      pressure: strokes.value.some(s => s.points.some(p => p.pressure > 0)),
      tilt: strokes.value.some(s => s.points.some(p => p.tiltX !== 0 || p.tiltY !== 0)),
      twist: strokes.value.some(s => s.points.some(p => p.twist !== 0))
    }
  }
}

// ============================================
// 정답 제출
// ============================================

function handleSubmit() {
  emit('submitAnswer')
}

// Expose
defineExpose({
  getSubmissionData,
  clearAll
})
</script>

<style scoped>
.memo-canvas {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: #ffffff;
}

/* 최상단 헤더 */
.page-header {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
  z-index: 10;
}

.page-header.visible {
  opacity: 1;
}

.header-line {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent 0%, #3b82f6 20%, #3b82f6 80%, transparent 100%);
}

/* 노트북 배경 */
.notebook-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  /* height는 Vue에서 동적으로 설정됨 */
  background-image:
    /* 좌측 여백 선 */
    linear-gradient(90deg, transparent 59px, #e5e7eb 59px, #e5e7eb 60px, transparent 60px),
    /* 우측 여백 선 */
    linear-gradient(90deg, transparent calc(100% - 60px), #e5e7eb calc(100% - 60px), #e5e7eb calc(100% - 59px), transparent calc(100% - 59px)),
    /* 가로줄 (좌우 여백 60px) */
    repeating-linear-gradient(
      transparent,
      transparent 44px,
      #e5e7eb 44px,
      #e5e7eb 45px
    );
  background-size: 100% 100%, 100% 100%, 100% 45px;
  background-position: 0 0, 0 0, 60px 0;
  pointer-events: none;
  z-index: 0;
}

/* 캔버스 */
.drawing-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  cursor: crosshair;
  touch-action: none;
  z-index: 1;
}

.drawing-canvas.eraser-cursor {
  cursor: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="none" stroke="black" stroke-width="2"/></svg>') 12 12, auto;
}

/* 캔버스 가이드 */
.canvas-guide {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  pointer-events: none;
  color: #9ca3af;
  opacity: 0.6;
  z-index: 2;
}

.canvas-guide svg {
  margin-bottom: 16px;
  opacity: 0.5;
}

.canvas-guide p {
  font-size: 16px;
  font-weight: 500;
}

/* 스크롤 위치 인디케이터 */
.scroll-indicator {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  z-index: 100;
}

.scroll-track {
  width: 6px;
  height: 200px;
  background: rgba(0, 0, 0, 0.08);
  border-radius: 3px;
  position: relative;
  overflow: hidden;
}

.scroll-thumb {
  position: absolute;
  left: 0;
  width: 100%;
  background: linear-gradient(180deg, #3b82f6, #2563eb);
  border-radius: 3px;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
}

.scroll-label {
  font-size: 10px;
  font-weight: 600;
  color: #3b82f6;
  background: white;
  padding: 3px 6px;
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  min-width: 35px;
  text-align: center;
}

/* 정답 제출 버튼 (우하단) */
.submit-button {
  position: absolute;
  bottom: 12px;
  right: 12px;
  background: linear-gradient(135deg, #d97706, #ea580c);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 18px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 2px 12px rgba(217, 119, 6, 0.3);
  transition: all 0.3s ease;
  z-index: 1001;
}

.submit-button svg {
  width: 20px;
  height: 20px;
}

.submit-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 30px rgba(217, 119, 6, 0.4);
  background: linear-gradient(135deg, #ea580c, #c2410c);
}

.submit-button:active {
  transform: translateY(0);
}

/* 툴바 */
.toolbar {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  padding: 8px 12px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.12);
  display: flex;
  gap: 10px;
  align-items: center;
  z-index: 1000;
}

.tool-group {
  display: flex;
  gap: 6px;
  align-items: center;
  padding: 0 6px;
  border-right: 1px solid #e5e7eb;
}

.tool-group:last-child {
  border-right: none;
}

.tool-button {
  width: 32px;
  height: 32px;
  border: 1.5px solid #e5e7eb;
  border-radius: 6px;
  background: white;
  color: #6b7280;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.tool-button svg {
  width: 16px;
  height: 16px;
}

.tool-button:hover:not(:disabled) {
  border-color: #3b82f6;
  background: #eff6ff;
  color: #3b82f6;
}

.tool-button.active {
  border-color: #3b82f6;
  background: #3b82f6;
  color: white;
}

.tool-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.color-picker {
  width: 32px;
  height: 32px;
  border: 1.5px solid #e5e7eb;
  border-radius: 6px;
  cursor: pointer;
}

.color-presets {
  display: flex;
  gap: 3px;
}

.color-preset {
  width: 20px;
  height: 20px;
  border: 1.5px solid transparent;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s;
}

.color-preset:hover {
  transform: scale(1.1);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
}

.color-preset.active {
  border-color: #3b82f6;
  box-shadow: 0 0 0 1.5px white, 0 0 0 3px #3b82f6;
}

.stroke-width-slider {
  width: 80px;
}

.stroke-width-label {
  font-size: 11px;
  color: #6b7280;
  min-width: 30px;
}

/* 반응형 */
@media (max-width: 767px) {
  .submit-button {
    bottom: 8px;
    right: 8px;
    padding: 8px 14px;
    font-size: 13px;
  }

  .submit-button svg {
    width: 18px;
    height: 18px;
  }

  .toolbar {
    bottom: 8px;
    padding: 6px 10px;
    gap: 8px;
    flex-wrap: wrap;
    max-width: 90%;
  }

  .tool-group {
    padding: 0 4px;
    gap: 4px;
  }

  .tool-button {
    width: 28px;
    height: 28px;
  }

  .tool-button svg {
    width: 14px;
    height: 14px;
  }

  .color-picker {
    width: 28px;
    height: 28px;
  }

  .color-preset {
    width: 18px;
    height: 18px;
  }

  .stroke-width-slider {
    width: 60px;
  }

  .stroke-width-label {
    font-size: 10px;
  }
}
</style>
