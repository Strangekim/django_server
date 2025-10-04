<template>
  <div class="memo-canvas-container">
    <!-- 도구 모음 -->
    <div class="toolbar">
      <div class="toolbar-section">
        <!-- 그리기 도구 -->
        <button
          class="tool-btn icon-btn"
          :class="{ active: currentTool === 'pen' }"
          @click="setTool('pen')"
          aria-label="펜 도구"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M17 3C17.5304 3 18.0391 3.21071 18.4142 3.58579C18.7893 3.96086 19 4.46957 19 5C19 5.53043 18.7893 6.03914 18.4142 6.41421L10.5 14.3L7.70711 11.5071C7.31658 11.1166 7.31658 10.4834 7.70711 10.0929L15.5858 2.20711C15.9609 1.83204 16.4696 1.62132 17 1.62132C17.5304 1.62132 18.0391 1.83204 18.4142 2.20711L21.7929 5.58579C22.1834 5.97631 22.1834 6.60948 21.7929 7L14.3 14.5L12 21L6.2 15.2C5.4 14.4 5.4 13.1 6.2 12.3L14.1 4.4C14.5 4 15 3.8 15.5 3.8C16 3.8 16.5 4 16.9 4.4L17 3Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>

        <button
          class="tool-btn icon-btn"
          :class="{ active: currentTool === 'eraser' }"
          @click="setTool('eraser')"
          aria-label="지우개"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M20 20H8L2.6 14.6C2.4 14.4 2.4 14.1 2.6 13.9L8.9 7.6C9.1 7.4 9.4 7.4 9.6 7.6L16.4 14.4C16.6 14.6 16.6 14.9 16.4 15.1L11 20.5H20V20Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>

        <button
          class="tool-btn icon-btn"
          :class="{ active: currentTool === 'hand' }"
          @click="setTool('hand')"
          aria-label="손도구"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 11V6C18 5.46957 17.7893 4.96086 17.4142 4.58579C17.0391 4.21071 16.5304 4 16 4C15.4696 4 14.9609 4.21071 14.5858 4.58579C14.2107 4.96086 14 5.46957 14 6V7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M14 7V4C14 3.46957 13.7893 2.96086 13.4142 2.58579C13.0391 2.21071 12.5304 2 12 2C11.4696 2 10.9609 2.21071 10.5858 2.58579C10.2107 2.96086 10 3.46957 10 4V7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M10 7V4C10 3.46957 9.78929 2.96086 9.41421 2.58579C9.03914 2.21071 8.53043 2 8 2C7.46957 2 6.96086 2.21071 6.58579 2.58579C6.21071 2.96086 6 3.46957 6 4V10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M6 10V16C6 17.0609 6.42143 18.0783 7.17157 18.8284C7.92172 19.5786 8.93913 20 10 20H16C17.0609 20 18.0783 19.5786 18.8284 18.8284C19.5786 18.0783 20 17.0609 20 16V11C20 10.4696 19.7893 9.96086 19.4142 9.58579C19.0391 9.21071 18.5304 9 18 9C17.4696 9 16.9609 9.21071 16.5858 9.58579C16.2107 9.96086 16 10.4696 16 11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>

        <!-- 선 굵기 -->
        <div class="stroke-width-control">
          <label class="control-label">굵기</label>
          <input
            type="range"
            v-model.number="strokeWidth"
            min="1"
            max="20"
            class="stroke-slider"
            @input="updateStrokeWidth(parseInt($event.target.value, 10))"
          />
          <span class="stroke-value">{{ strokeWidth }}</span>
        </div>
      </div>

      <div class="toolbar-section">
        <!-- 색상 팔레트 -->
        <div class="color-palette">
          <div class="color-grid">
            <button
              v-for="color in colors"
              :key="color"
              class="color-btn"
              :class="{ active: currentColor === color }"
              :style="{ backgroundColor: color }"
              @click="setColor(color)"
              :aria-label="`색상: ${color}`"
            ></button>
          </div>

          <!-- 커스텀 색상 선택기 -->
          <div class="custom-color">
            <input
              type="color"
              v-model="customColor"
              @change="setColor(customColor)"
              class="color-picker"
              aria-label="커스텀 색상"
            />
          </div>
        </div>
      </div>

      <div class="toolbar-section">
        <!-- 확대/축소 -->
        <button
          class="action-btn icon-btn"
          @click="zoomIn"
          aria-label="확대"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
            <path d="M21 21L16.65 16.65" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="11" y1="8" x2="11" y2="14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <line x1="8" y1="11" x2="14" y2="11" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>

        <button
          class="action-btn icon-btn"
          @click="zoomOut"
          aria-label="축소"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
            <path d="M21 21L16.65 16.65" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="8" y1="11" x2="14" y2="11" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>

      </div>

      <div class="toolbar-section">
        <!-- 실행 취소/다시 실행 -->
        <button
          class="action-btn icon-btn"
          @click="undo"
          :disabled="!canUndo"
          aria-label="실행 취소"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 7V3H7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M21 13C21 17.9706 16.9706 22 12 22C8.6863 22 5.81726 20.2404 4.23891 17.6011" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M3.05115 6.39892C4.62949 3.75965 7.49854 2 11 2C15.9706 2 20 6.02944 20 11V13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>

        <button
          class="action-btn icon-btn"
          @click="redo"
          :disabled="!canRedo"
          aria-label="다시 실행"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 7V3H17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M3 11C3 6.02944 7.02944 2 12 2C15.3137 2 18.1827 3.75965 19.7611 6.39892" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M20.9489 17.6011C19.3705 20.2404 16.5015 22 13 22C8.02944 22 4 17.9706 4 13V11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>

        <!-- 전체 지우기 -->
        <button
          class="action-btn icon-btn clear-all"
          @click="clearAll"
          aria-label="전체 지우기"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 6H5H21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6H19Z" stroke="currentColor" stroke-width="2"/>
            <path d="M10 11V17" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M14 11V17" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
      </div>

      <!-- 데이터 수집 통계 및 JSON 다운로드 섹션 제거됨 (요청사항) -->
      <!-- 백엔드로 전송되는 JSON 데이터는 그대로 유지됨 -->
    </div>

    <!-- 캔버스 영역 -->
    <div class="canvas-container" ref="canvasContainer" :class="{ 'eraser-cursor': currentTool === 'eraser' }" :style="eraserCursorStyle">
      <!-- 가이드 라인 -->
      <div class="guide-lines">
        <!-- 수평선들 -->
        <div
          v-for="i in horizontalLines"
          :key="'h' + i"
          class="guide-line horizontal"
          :style="{ top: (i * 40) + 'px' }"
        ></div>

        <!-- 수직선들 -->
        <div
          v-for="i in verticalLines"
          :key="'v' + i"
          class="guide-line vertical"
          :style="{ left: (i * 40) + 'px' }"
        ></div>
      </div>

      <canvas
        ref="canvas"
        class="memo-canvas"
        :data-tool="currentTool"
        @pointerdown="handlePointerDown"
        @pointermove="handlePointerMove"
        @pointerup="handlePointerUp"
        @pointercancel="handlePointerUp"
        @touchstart="handleTouchStart"
        @touchmove="handleTouchMove"
        @touchend="handleTouchEnd"
        @mousedown="startDrawing"
        @mousemove="handleMouseMove"
        @mouseup="stopDrawing"
      ></canvas>

      <!-- 캔버스 안내 텍스트 -->
      <div v-if="!hasDrawn" class="canvas-guide">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M17 3C17.5304 3 18.0391 3.21071 18.4142 3.58579C18.7893 3.96086 19 4.46957 19 5C19 5.53043 18.7893 6.03914 18.4142 6.41421L10.5 14.3L7.70711 11.5071C7.31658 11.1166 7.31658 10.4834 7.70711 10.0929L15.5858 2.20711C15.9609 1.83204 16.4696 1.62132 17 1.62132C17.5304 1.62132 18.0391 1.83204 18.4142 2.20711L21.7929 5.58579C22.1834 5.97631 22.1834 6.60948 21.7929 7L14.3 14.5L12 21L6.2 15.2C5.4 14.4 5.4 13.1 6.2 12.3L14.1 4.4C14.5 4 15 3.8 15.5 3.8C16 3.8 16.5 4 16.9 4.4L17 3Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <p>여기서 자유롭게 메모하고 계산해보세요</p>
        <p class="guide-subtitle">손글씨나 도형을 그려서 문제를 풀어보세요</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick, watch, computed } from 'vue'

export default {
  name: 'MemoCanvas',
  setup() {
    // 캔버스 관련 ref
    const canvas = ref(null)
    const canvasContainer = ref(null)

    // 그리기 상태
    const isDrawing = ref(false)
    const hasDrawn = ref(false)

    // 오버레이 이미지 상태
    const overlayImage = ref(null)
    const overlayImageData = ref(null)
    const overlayImagePosition = ref({ x: 20, y: 20 })
    const overlayImageSize = ref({ width: 0, height: 0 })

    // 캔버스 변환 상태
    const zoom = ref(1)
    const panX = ref(0)
    const panY = ref(0)

    // 손도구 상태
    const isDragging = ref(false)
    const isImageDragging = ref(false)
    const dragStart = ref({ x: 0, y: 0 })
    const dragTarget = ref(null) // 'canvas' or 'image'

    // 드래그 성능 최적화를 위한 requestAnimationFrame 관리
    let rafId = null // requestAnimationFrame ID
    let pendingPanUpdate = false // 렌더링 대기 중 플래그

    // 터치 제스처 상태 (개선된 버전)
    const isTouching = ref(false)
    const touchCount = ref(0)
    const lastTouchDistance = ref(0)
    const touchCenter = ref({ x: 0, y: 0 })
    const initialZoom = ref(1)
    const initialPan = ref({ x: 0, y: 0 })
    const gestureStartTime = ref(0)
    const gestureThreshold = 10 // 최소 이동 거리 (px)
    const zoomThreshold = 20 // 최소 핀치 거리 (px)
    const touchStartPositions = ref([])
    const lastGestureTime = ref(0)
    const gestureDebounce = 16 // 60fps 제한

    // 현재 도구 및 설정
    const currentTool = ref('pen')
    const currentColor = ref('#000000')
    const customColor = ref('#000000')
    const strokeWidth = ref(3)

    // 지우개 전용 설정 (고정 값)
    const eraserSize = 20 // 고정 사이즈 20px

    // UUID 생성 함수 (브라우저 호환성)
    const generateUUID = () => {
      if (typeof crypto !== 'undefined' && crypto.randomUUID) {
        return crypto.randomUUID()
      }
      // 폴리필: 간단한 UUID v4 생성
      return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0
        const v = c == 'x' ? r : (r & 0x3 | 0x8)
        return v.toString(16)
      })
    }

    // 간단한 데이터 수집
    const sessionData = ref({
      sessionId: generateUUID(),
      startTime: Date.now(),
      strokes: [],
      events: [],
      capabilities: {
        pressure: false,
        tilt: false,
        twist: false
      },
      stats: {
        undoCount: 0,
        redoCount: 0,
        eraserCount: 0,
        zoomCount: 0,
        panCount: 0,
        toolChanges: 0,
        colorChanges: 0,
        strokeWidthChanges: 0
      }
    })

    // 색상 팔레트 (압축된 필수 색상만)
    const colors = ref([
      '#000000', '#ff0000', '#0000ff', '#00ff00',
      '#ffff00', '#ff8000', '#800080', '#ffffff'
    ])

    // 히스토리 관리
    const history = ref([])
    const historyStep = ref(-1)

    // 가이드 라인 계산
    const horizontalLines = ref([])
    const verticalLines = ref([])

    // 캔버스 컨텍스트
    let ctx = null
    let rect = null

    // 이전 좌표
    let lastX = 0
    let lastY = 0

    // 지우개 커서 스타일 (고정 크기)
    const eraserCursorStyle = computed(() => {
      if (currentTool.value !== 'eraser') return {}

      return {
        '--eraser-size': `${eraserSize}px`
      }
    })

    // 가이드 라인 계산
    const calculateGuideLines = () => {
      if (!canvasContainer.value) return

      const container = canvasContainer.value
      const rect = container.getBoundingClientRect()

      // 수평선 계산 (40px 간격)
      const hLines = []
      for (let i = 1; i * 40 < rect.height - 40; i++) {
        hLines.push(i)
      }
      horizontalLines.value = hLines

      // 수직선 계산 (40px 간격)
      const vLines = []
      for (let i = 1; i * 40 < rect.width - 40; i++) {
        vLines.push(i)
      }
      verticalLines.value = vLines
    }

    // 캔버스 초기화
    const initCanvas = () => {
      if (!canvas.value || !canvasContainer.value) return

      const container = canvasContainer.value
      const canvasEl = canvas.value

      // 캔버스 크기 설정 (고해상도 지원)
      const devicePixelRatio = window.devicePixelRatio || 1
      const rect = container.getBoundingClientRect()

      canvasEl.width = rect.width * devicePixelRatio
      canvasEl.height = rect.height * devicePixelRatio

      canvasEl.style.width = rect.width + 'px'
      canvasEl.style.height = rect.height + 'px'

      ctx = canvasEl.getContext('2d')
      ctx.scale(devicePixelRatio, devicePixelRatio)

      // 캔버스 스타일 설정
      ctx.lineCap = 'round'
      ctx.lineJoin = 'round'
      ctx.imageSmoothingEnabled = true

      // 가이드 라인 계산
      calculateGuideLines()

      // 초기 렌더링 (overlayImage 포함)
      redrawCanvas()

      // 초기 히스토리 저장
      saveToHistory()
    }

    // drawOverlayImage 함수 제거됨 - redrawCanvas()에 통합되어 처리됨

    // 좌표 계산 (마우스/터치 이벤트) - 줌/패닝 역변환 적용
    const getCoordinates = (event) => {
      const canvasEl = canvas.value
      const rect = canvasEl.getBoundingClientRect()

      let x, y
      if (event.touches && event.touches.length > 0) {
        // 터치 이벤트
        x = event.touches[0].clientX - rect.left
        y = event.touches[0].clientY - rect.top
      } else {
        // 마우스 이벤트
        x = event.clientX - rect.left
        y = event.clientY - rect.top
      }

      // 줌/패닝 역변환: 화면 좌표 → 논리적 캔버스 좌표
      // 올바른 역변환 공식: (screen / zoom) - (pan / zoom)
      const logicalX = x / zoom.value - panX.value / zoom.value
      const logicalY = y / zoom.value - panY.value / zoom.value

      return { x: logicalX, y: logicalY }
    }

    // 화면 좌표 계산 (드래그/제스처용)
    const getScreenCoordinates = (event) => {
      const canvasEl = canvas.value
      const rect = canvasEl.getBoundingClientRect()

      let x, y
      if (event.touches && event.touches.length > 0) {
        x = event.touches[0].clientX - rect.left
        y = event.touches[0].clientY - rect.top
      } else {
        x = event.clientX - rect.left
        y = event.clientY - rect.top
      }

      return { x, y }
    }

    // 입력 방식 감지 함수 (pen.html 로직 참고)
    const detectInputType = (event) => {
      // 1. Pointer Events가 가장 정확하므로 우선 처리
      if ('pointerType' in event && event.pointerType) {
        return event.pointerType; // 'pen' | 'touch' | 'mouse'
      }

      // 2. Touch 폴백 (iOS)
      if ('changedTouches' in event && event.changedTouches?.length) {
        const touch = event.changedTouches[0]

        // iOS WebKit: Apple Pencil이면 'stylus'가 올 수 있음
        if ('touchType' in touch && touch.touchType === 'stylus') {
          return 'pen'
        }

        // 압력이나 각도 정보가 있으면 펜
        const hasForce = typeof touch.force === 'number' && touch.force > 0.1
        const hasTilt = typeof touch.altitudeAngle === 'number' || typeof touch.azimuthAngle === 'number'
        const hasPressure = typeof touch.pressure === 'number' && touch.pressure > 0.1

        if (hasForce || hasTilt || hasPressure) {
          return 'pen'
        }

        return 'finger'
      }

      // 3. 단일 터치 이벤트 처리 (touches 배열 사용)
      if (event.type.includes('touch') && event.touches?.length) {
        // 다중 터치는 항상 손가락
        if (event.touches.length > 1) {
          return 'finger'
        }

        const touch = event.touches[0]

        // iOS WebKit 지원
        if ('touchType' in touch && touch.touchType === 'stylus') {
          return 'pen'
        }

        // 압력/각도 기반 감지
        const hasForce = typeof touch.force === 'number' && touch.force > 0.1
        const hasTilt = typeof touch.altitudeAngle === 'number' || typeof touch.azimuthAngle === 'number'

        if (hasForce || hasTilt) {
          return 'pen'
        }

        return 'finger'
      }

      // 4. Mouse 폴백
      if (event.type === 'mousedown' || event.type === 'mousemove' || event.type === 'mouseup') {
        return 'mouse'
      }

      return 'unknown'
    }

    // 이벤트에서 기본 데이터 추출
    const extractEventData = (event) => {
      const coords = getCoordinates(event)
      const timestamp = Date.now() - sessionData.value.startTime
      const inputType = detectInputType(event)

      // 포인터 이벤트에서 압력, 기울기, 비틀기 정보 추출
      let pressure = null // 기본값을 null로 설정
      let tiltX = 0
      let tiltY = 0
      let twist = 0

      // 실제 압력 센서가 있는 경우만 값 설정
      if (event.pressure !== undefined && inputType === 'pen') {
        pressure = event.pressure
        sessionData.value.capabilities.pressure = true
      } else if (inputType === 'mouse' || inputType === 'touch') {
        // 마우스나 터치는 pressure를 null로 유지
        pressure = null
      }
      if (event.tiltX !== undefined) {
        tiltX = event.tiltX
        sessionData.value.capabilities.tilt = true
      }
      if (event.tiltY !== undefined) {
        tiltY = event.tiltY
        sessionData.value.capabilities.tilt = true
      }
      if (event.twist !== undefined) {
        twist = event.twist
        sessionData.value.capabilities.twist = true
      }

      return {
        timestamp,
        x: coords.x,
        y: coords.y,
        pressure,
        tiltX,
        tiltY,
        twist,
        eventType: event.type,
        inputType,
        tool: currentTool.value,
        color: currentColor.value,
        strokeWidth: strokeWidth.value
      }
    }

    // 현재 스트로크 데이터
    let currentStroke = null

    // 이벤트 로깅 헬퍼 함수
    const logEvent = (eventType, data = {}) => {
      const timestamp = Date.now() - sessionData.value.startTime
      const event = {
        timestamp,
        type: eventType,
        ...data
      }
      sessionData.value.events.push(event)
    }

    // 터치 이벤트 유틸리티 함수들
    const getTouchDistance = (touches) => {
      if (touches.length < 2) return 0
      const touch1 = touches[0]
      const touch2 = touches[1]
      const dx = touch1.clientX - touch2.clientX
      const dy = touch1.clientY - touch2.clientY
      return Math.sqrt(dx * dx + dy * dy)
    }

    const getTouchCenter = (touches) => {
      if (touches.length === 0) return { x: 0, y: 0 }
      let x = 0
      let y = 0
      for (let i = 0; i < touches.length; i++) {
        x += touches[i].clientX
        y += touches[i].clientY
      }
      const rect = canvas.value?.getBoundingClientRect()
      if (rect) {
        return {
          x: x / touches.length - rect.left,
          y: y / touches.length - rect.top
        }
      }
      return { x: x / touches.length, y: y / touches.length }
    }

    // Pointer Events 핸들러들 (우선 처리)
    const handlePointerDown = (event) => {
      if (!canvas.value) return

      event.preventDefault()
      const inputType = detectInputType(event)

      // 펜이나 마우스만 그리기 허용
      if (inputType === 'pen' || inputType === 'mouse') {
        startDrawing(event)
      } else if (inputType === 'touch') {
        // 손가락 터치는 드래그 모드 (더 안정적)
        const now = performance.now()
        if (now - lastGestureTime.value < gestureDebounce) return

        isDragging.value = true
        const screenCoords = getScreenCoordinates(event)
        dragStart.value = { x: screenCoords.x, y: screenCoords.y }
        dragTarget.value = 'canvas'
        gestureStartTime.value = now
        lastGestureTime.value = now

        // 패닝 시작 이벤트 로깅
        sessionData.value.stats.panCount++
        logEvent('canvas_pan_start', {
          startX: screenCoords.x,
          startY: screenCoords.y,
          currentZoom: zoom.value,
          prevPanX: panX.value,
          prevPanY: panY.value
        })
      }
    }

    const handlePointerMove = (event) => {
      if (!canvas.value) return

      const inputType = detectInputType(event)

      if (inputType === 'pen' || inputType === 'mouse') {
        draw(event)
        updateEraserCursor(event)
      } else if (inputType === 'touch' && isDragging.value) {
        // 손가락 터치 드래그 (민감도 개선)
        const now = performance.now()
        if (now - lastGestureTime.value < gestureDebounce) return

        event.preventDefault()
        const screenCoords = getScreenCoordinates(event)
        const deltaX = screenCoords.x - dragStart.value.x
        const deltaY = screenCoords.y - dragStart.value.y

        // 최소 이동 거리 체크
        const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY)
        if (distance < gestureThreshold) return

        panX.value += deltaX
        panY.value += deltaY
        redrawCanvas()
        dragStart.value = screenCoords
        lastGestureTime.value = now
      }
    }

    const handlePointerUp = (event) => {
      const inputType = detectInputType(event)

      if (inputType === 'pen' || inputType === 'mouse') {
        stopDrawing(event)
      } else if (inputType === 'touch') {
        // 패닝 종료 이벤트 로깅
        if (isDragging.value) {
          logEvent('canvas_pan_end', {
            finalPanX: panX.value,
            finalPanY: panY.value,
            currentZoom: zoom.value
          })
        }

        isDragging.value = false
        dragTarget.value = null
      }
    }

    // 터치 이벤트 핸들러들 (폴백 - Pointer Events 미지원 시)
    const handleTouchStart = (event) => {
      // Pointer Events가 지원되는 경우 아무것도 하지 않음
      if ('onpointerdown' in window) return

      if (!canvas.value) return

      const touches = event.touches
      touchCount.value = touches.length
      const now = performance.now()

      // 터치 시작 위치 저장
      touchStartPositions.value = Array.from(touches).map(touch => ({
        x: touch.clientX,
        y: touch.clientY,
        identifier: touch.identifier
      }))

      if (touches.length === 1) {
        // 단일 터치 - 입력 타입 검사
        const inputType = detectInputType(event)
        if (inputType === 'pen') {
          startDrawing(event)
        } else {
          // 손가락 터치는 드래그 모드 (여전히 처리)
          if (now - lastGestureTime.value >= gestureDebounce) {
            isDragging.value = true
            const screenCoords = getScreenCoordinates(event)
            dragStart.value = { x: screenCoords.x, y: screenCoords.y }
            dragTarget.value = 'canvas'
            gestureStartTime.value = now
            lastGestureTime.value = now

            // 패닝 시작 이벤트 로깅 (터치)
            sessionData.value.stats.panCount++
            logEvent('canvas_pan_start', {
              startX: screenCoords.x,
              startY: screenCoords.y,
              currentZoom: zoom.value,
              prevPanX: panX.value,
              prevPanY: panY.value,
              inputType: 'touch'
            })
          }
        }
      } else if (touches.length === 2) {
        // 두 손가락 터치 - 핀치 준비 (개선된 버전)
        event.preventDefault()

        const distance = getTouchDistance(touches)
        const center = getTouchCenter(touches)

        // 최소 거리 체크
        if (distance > zoomThreshold) {
          isTouching.value = true
          lastTouchDistance.value = distance
          touchCenter.value = center
          initialZoom.value = zoom.value
          initialPan.value = { x: panX.value, y: panY.value }
          gestureStartTime.value = now
          lastGestureTime.value = now

          // 기존 드래잉 중단
          if (isDrawing.value) {
            stopDrawing(event)
          }
          if (isDragging.value) {
            isDragging.value = false
            dragTarget.value = null
          }
        }
      }
    }

    const handleTouchMove = (event) => {
      // Pointer Events가 지원되는 경우 아무것도 하지 않음
      if ('onpointerdown' in window) return

      if (!canvas.value) return

      const touches = event.touches
      const now = performance.now()

      // 프레임레이트 제한
      if (now - lastGestureTime.value < gestureDebounce) return

      if (touches.length === 1 && !isTouching.value) {
        // 단일 터치 - 입력 타입 검사
        const inputType = detectInputType(event)
        if (inputType === 'pen') {
          draw(event)
        } else if (isDragging.value) {
          // 손가락 드래그 (민감도 개선)
          event.preventDefault()
          const screenCoords = getScreenCoordinates(event)
          const deltaX = screenCoords.x - dragStart.value.x
          const deltaY = screenCoords.y - dragStart.value.y

          // 최소 이동 거리 체크
          const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY)
          if (distance >= gestureThreshold) {
            panX.value += deltaX
            panY.value += deltaY
            redrawCanvas()
            dragStart.value = screenCoords
            lastGestureTime.value = now
          }
        }
      } else if (touches.length === 2 && isTouching.value) {
        // 두 손가락 터치 - 핀치 제스처 (개선된 버전)
        event.preventDefault()

        const currentDistance = getTouchDistance(touches)
        const currentCenter = getTouchCenter(touches)

        if (lastTouchDistance.value > zoomThreshold && currentDistance > zoomThreshold) {
          // 확대/축소 계산 (더 안정적)
          const scale = currentDistance / lastTouchDistance.value
          const scaleChange = Math.abs(scale - 1)

          // 너무 작은 스케일 변화 무시
          if (scaleChange > 0.02) {
            const previousZoom = zoom.value
            const newZoom = Math.max(0.2, Math.min(5, initialZoom.value * scale))

            // 확대/축소 중심점 고려한 패닝 조정
            const centerOffsetX = currentCenter.x - touchCenter.value.x
            const centerOffsetY = currentCenter.y - touchCenter.value.y

            zoom.value = newZoom
            panX.value = initialPan.value.x + centerOffsetX
            panY.value = initialPan.value.y + centerOffsetY

            // 핀치 줌 이벤트 로깅
            if (previousZoom !== newZoom) {
              sessionData.value.stats.zoomCount++
              logEvent('pinch_zoom', {
                previousZoom,
                newZoom,
                scale,
                centerX: currentCenter.x,
                centerY: currentCenter.y,
                previousPanX: initialPan.value.x,
                previousPanY: initialPan.value.y,
                newPanX: panX.value,
                newPanY: panY.value,
                viewportWidth: window.innerWidth,
                viewportHeight: window.innerHeight
              })
            }

            redrawCanvas()
            lastGestureTime.value = now
          }
        }
      }
    }

    const handleTouchEnd = (event) => {
      // Pointer Events가 지원되는 경우 아무것도 하지 않음
      if ('onpointerdown' in window) return

      const touches = event.touches
      touchCount.value = touches.length

      if (touches.length === 0) {
        // 모든 터치 끝남
        if (isTouching.value) {
          isTouching.value = false
        } else {
          const inputType = detectInputType(event)
          if (inputType === 'pen') {
            stopDrawing(event)
          } else {
            // 패닝 종료 이벤트 로깅 (터치)
            if (isDragging.value) {
              logEvent('canvas_pan_end', {
                finalPanX: panX.value,
                finalPanY: panY.value,
                currentZoom: zoom.value,
                inputType: 'touch'
              })
            }

            isDragging.value = false
            dragTarget.value = null
          }
        }
      } else if (touches.length === 1 && isTouching.value) {
        // 핀치에서 단일 터치로 전환
        isTouching.value = false
        lastTouchDistance.value = 0
      }
    }


    // 이미지 영역 체크 (안정화된 버전)
    const isPointInImage = (x, y) => {
      if (!overlayImage.value || !overlayImageSize.value.width || !overlayImageSize.value.height) {
        return false
      }

      // 좌표 정규화 (디바이스 회전 대응)
      const normalizedX = Math.floor(x)
      const normalizedY = Math.floor(y)

      // 이미지 위치 계산 (안정적)
      const imageX = Math.floor(overlayImagePosition.value.x + panX.value / zoom.value)
      const imageY = Math.floor(overlayImagePosition.value.y + panY.value / zoom.value)
      const imageWidth = Math.floor(overlayImageSize.value.width)
      const imageHeight = Math.floor(overlayImageSize.value.height)

      return (
        normalizedX >= imageX &&
        normalizedX <= imageX + imageWidth &&
        normalizedY >= imageY &&
        normalizedY <= imageY + imageHeight
      )
    }

    // 지우개 커서 마우스 추적
    const updateEraserCursor = (event) => {
      if (currentTool.value === 'eraser' && canvasContainer.value) {
        const rect = canvasContainer.value.getBoundingClientRect()
        const x = event.clientX - rect.left
        const y = event.clientY - rect.top

        canvasContainer.value.style.setProperty('--cursor-x', x + 'px')
        canvasContainer.value.style.setProperty('--cursor-y', y + 'px')
      }
    }

    // 마우스 이동 통합 핸들러
    const handleMouseMove = (event) => {
      draw(event)
      updateEraserCursor(event)
    }

    // 그리기 시작
    const startDrawing = (event) => {
      if (!ctx) return

      event.preventDefault()
      const coords = getCoordinates(event)

      // 이벤트 데이터 수집 (스트로크에만 사용)
      const eventData = extractEventData(event)

      // 손가락 터치인 경우 그리기 방지 (손도구 모드가 아니어도)
      if (eventData.inputType === 'finger') {
        // 손가락은 항상 드래그 모드
        isDragging.value = true
        const screenCoords = getScreenCoordinates(event)
        dragStart.value = { x: screenCoords.x, y: screenCoords.y }
        dragTarget.value = 'canvas'

        // 패닝 시작 이벤트 로깅
        sessionData.value.stats.panCount++
        logEvent('canvas_pan_start', {
          startX: screenCoords.x,
          startY: screenCoords.y,
          currentZoom: zoom.value,
          prevPanX: panX.value,
          prevPanY: panY.value
        })

        return
      }

      if (currentTool.value === 'hand') {
        // 손도구 모드 - 항상 캔버스 전체를 이동
        isDragging.value = true
        const screenCoords = getScreenCoordinates(event)
        dragStart.value = { x: screenCoords.x, y: screenCoords.y }
        dragTarget.value = 'canvas' // 항상 캔버스 패닝만 수행

        // 패닝 시작 이벤트 로깅 (손도구)
        sessionData.value.stats.panCount++
        logEvent('canvas_pan_start', {
          startX: screenCoords.x,
          startY: screenCoords.y,
          currentZoom: zoom.value,
          prevPanX: panX.value,
          prevPanY: panY.value,
          tool: 'hand'
        })
      } else if (eventData.inputType === 'pen' || eventData.inputType === 'mouse') {
        // 펜이나 마우스만 그리기 가능
        isDrawing.value = true
        hasDrawn.value = true

        lastX = coords.x
        lastY = coords.y

        ctx.globalCompositeOperation = currentTool.value === 'eraser' ? 'destination-out' : 'source-over'
        ctx.strokeStyle = currentTool.value === 'eraser' ? 'rgba(0,0,0,1)' : currentColor.value
        ctx.lineWidth = currentTool.value === 'eraser' ? eraserSize : strokeWidth.value

        // 변환 매트릭스 적용하여 그리기 시작
        ctx.save()
        ctx.translate(panX.value, panY.value)
        ctx.scale(zoom.value, zoom.value)

        ctx.beginPath()
        ctx.moveTo(lastX, lastY)

        ctx.restore()

        // 새 스트로크 시작
        const strokeId = generateUUID()
        currentStroke = {
          id: strokeId,
          startTime: eventData.timestamp,
          tool: currentTool.value,
          color: currentColor.value,
          strokeWidth: currentTool.value === 'eraser' ? eraserSize : strokeWidth.value,
          points: [eventData],
          historyIndex: historyStep.value  // 현재 히스토리 단계 저장 (Undo 추적용)
        }

        // 스트로크 시작 이벤트 로깅
        logEvent('stroke_start', {
          strokeId,
          tool: currentTool.value,
          color: currentColor.value,
          strokeWidth: currentTool.value === 'eraser' ? eraserSize : strokeWidth.value,
          inputType: eventData.inputType,
          startX: coords.x,
          startY: coords.y
        })
      }
    }

    // 그리기
    const draw = (event) => {
      if (!isDrawing.value && !isDragging.value) return

      event.preventDefault()
      const coords = getCoordinates(event)
      const eventData = extractEventData(event)

      // 드래그 모드 (손도구 또는 손가락) - 캔버스 패닝 (성능 최적화)
      if (isDragging.value) {
        const screenCoords = getScreenCoordinates(event)
        const deltaX = screenCoords.x - dragStart.value.x
        const deltaY = screenCoords.y - dragStart.value.y

        // pan 값 즉시 업데이트
        panX.value += deltaX
        panY.value += deltaY
        dragStart.value = screenCoords

        // requestAnimationFrame을 사용하여 렌더링 최적화
        // 이미 렌더링이 예약되어 있으면 스킵 (프레임 드롭 방지)
        if (!pendingPanUpdate) {
          pendingPanUpdate = true
          rafId = requestAnimationFrame(() => {
            redrawCanvas() // 실제 렌더링은 다음 프레임에서 실행
            pendingPanUpdate = false
          })
        }
      } else if (isDrawing.value && ctx && (eventData.inputType === 'pen' || eventData.inputType === 'mouse')) {
        // 펜이나 마우스만 그리기 가능

        // 현재 스트로크에 포인트 추가
        if (currentStroke) {
          currentStroke.points.push(eventData)
        }

        // 그리기 - 변환 매트릭스 적용
        ctx.save()
        ctx.translate(panX.value, panY.value)
        ctx.scale(zoom.value, zoom.value)

        ctx.lineTo(coords.x, coords.y)
        ctx.stroke()

        ctx.restore()

        lastX = coords.x
        lastY = coords.y
      }
    }

    // 그리기 종료
    const stopDrawing = (event) => {
      if (isDrawing.value) {
        // 마지막 이벤트 데이터 수집 (스트로크에만 사용)
        const eventData = extractEventData(event)

        // 현재 스트로크 완료
        if (currentStroke) {
          currentStroke.endTime = eventData.timestamp
          currentStroke.points.push(eventData)

          // 스트로크 종료 이벤트 로깅
          const strokeDuration = currentStroke.endTime - currentStroke.startTime
          const pointCount = currentStroke.points.length

          logEvent('stroke_end', {
            strokeId: currentStroke.id,
            tool: currentStroke.tool,
            duration: strokeDuration,
            pointCount,
            endX: eventData.x,
            endY: eventData.y
          })

          sessionData.value.strokes.push(currentStroke)
          currentStroke = null
        }

        isDrawing.value = false
        saveToHistory()
      }

      // 패닝 종료 이벤트 로깅
      if (isDragging.value) {
        sessionData.value.stats.panCount++
        logEvent('canvas_pan_end', {
          finalPanX: panX.value,
          finalPanY: panY.value,
          currentZoom: zoom.value
        })
      }

      isDragging.value = false
      isImageDragging.value = false
      dragTarget.value = null
    }


    // JSON 데이터 생성
    const generateSessionData = () => {
      const now = new Date()
      const sessionDuration = Date.now() - sessionData.value.startTime

      return {
        metadata: {
          version: "1.0",
          generator: "Math Memo App",
          sessionId: sessionData.value.sessionId,
          startTime: new Date(sessionData.value.startTime).toISOString(),
          endTime: now.toISOString(),
          duration: sessionDuration,
          totalStrokes: sessionData.value.strokes.length,
          totalEvents: sessionData.value.events.length
        },
        deviceCapabilities: sessionData.value.capabilities,
        canvasData: {
          strokes: sessionData.value.strokes,
          events: sessionData.value.events
        },
        statistics: {
          ...sessionData.value.stats,
          averageStrokeLength: sessionData.value.strokes.length > 0
            ? sessionData.value.strokes.reduce((sum, stroke) => sum + stroke.points.length, 0) / sessionData.value.strokes.length
            : 0,
          sessionDuration
        }
      }
    }

    /**
     * 현재 화면에 보이는 스트로크만 반환 (Undo로 되돌린 것 제외)
     * Mathpix API 전송용으로 사용
     *
     * @returns {Array} 현재 historyStep 기준으로 유효한 스트로크 배열
     */
    const getVisibleStrokes = () => {
      // 현재 히스토리 단계 이하의 스트로크만 필터링
      // historyIndex가 현재 historyStep 이하인 스트로크만 화면에 보임
      return sessionData.value.strokes.filter(stroke => {
        // historyIndex가 없는 경우 (레거시 데이터) 모두 포함
        if (stroke.historyIndex === undefined) {
          return true
        }
        // 현재 히스토리 단계 이하인 스트로크만 포함
        return stroke.historyIndex <= historyStep.value
      })
    }

    /**
     * API 제출용 세션 데이터 생성
     * - 전체 스트로크: DB 저장용
     * - 화면에 보이는 스트로크: Mathpix 전송용
     *
     * @returns {Object} 제출용 세션 데이터 (전체 + 가시 스트로크 포함)
     */
    const getSubmissionData = () => {
      const baseData = generateSessionData()
      const visibleStrokes = getVisibleStrokes()

      // canvasData에 visibleStrokes 추가
      return {
        ...baseData,
        canvasData: {
          strokes: baseData.canvasData.strokes,  // 전체 스트로크 (DB 저장용)
          visibleStrokes: visibleStrokes,  // 화면에 보이는 스트로크만 (Mathpix 전송용)
          events: baseData.canvasData.events
        }
      }
    }

    // JSON 다운로드 함수 제거됨 (요청사항)
    // 사용자가 프론트엔드에서 JSON 다운로드를 할 수 없도록 함
    // 단, 백엔드로 전송되는 데이터는 generateSessionData()를 통해 정상적으로 생성됨

    // 도구 설정
    const setTool = (tool) => {
      const previousTool = currentTool.value
      currentTool.value = tool

      // 도구 변경 이벤트 로깅
      if (previousTool !== tool) {
        sessionData.value.stats.toolChanges++

        // 지우개로 전환할 때 지우개 카운트 증가
        if (tool === 'eraser') {
          sessionData.value.stats.eraserCount++
        }

        logEvent('tool_change', {
          previousTool,
          newTool: tool
        })
      }
    }

    const setColor = (color) => {
      const previousColor = currentColor.value
      currentColor.value = color
      if (color !== customColor.value) {
        customColor.value = color
      }

      // 색상 변경 이벤트 로깅
      if (previousColor !== color) {
        sessionData.value.stats.colorChanges++

        logEvent('color_change', {
          previousColor,
          newColor: color
        })
      }
    }

    const updateStrokeWidth = (newWidth) => {
      // 현재 값과 새 값 모두 숫자로 변환
      const previousWidth = typeof strokeWidth.value === 'string' ? parseInt(strokeWidth.value, 10) : strokeWidth.value
      const numericWidth = typeof newWidth === 'string' ? parseInt(newWidth, 10) : newWidth

      if (numericWidth !== undefined && numericWidth !== previousWidth) {
        strokeWidth.value = numericWidth
        sessionData.value.stats.strokeWidthChanges++

        logEvent('stroke_width_change', {
          previousWidth: previousWidth, // 숫자로 변환된 값
          newWidth: numericWidth        // 숫자로 변환된 값
        })
      }
    }

    // 히스토리 저장
    /**
     * 히스토리에 현재 상태 저장 (단순화됨)
     *
     * [개선 사항]
     * - 기존: canvas.toDataURL()로 Base64 이미지 저장 (메모리 많이 사용, 느림)
     * - 개선: historyStep만 증가 (sessionData.strokes에 이미 데이터 있음)
     *
     * [동작 원리]
     * - 각 스트로크는 historyIndex를 가지고 있음 (생성 시점 기록)
     * - Undo: historyStep 감소 → getVisibleStrokes()가 해당 시점 스트로크만 반환
     * - Redo: historyStep 증가 → 더 많은 스트로크 표시
     *
     * [장점]
     * - 메모리 효율: Base64 문자열 저장 불필요
     * - 성능 향상: toDataURL() 호출 제거 (동기 작업)
     */
    const saveToHistory = () => {
      // 현재 단계 이후의 히스토리 제거 (새로운 분기 생성)
      // history 배열은 더 이상 이미지를 저장하지 않고, 단순히 체크포인트 역할
      history.value = history.value.slice(0, historyStep.value + 1)

      // 빈 마커 추가 (실제 데이터는 sessionData.strokes에 있음)
      history.value.push(true) // true는 "유효한 히스토리 지점" 표시
      historyStep.value = history.value.length - 1

      // 히스토리 크기 제한 (오래된 것 삭제)
      if (history.value.length > 50) {
        history.value.shift()
        historyStep.value--

        // 오래된 스트로크도 제거 (메모리 관리)
        // historyIndex가 0인 스트로크 제거
        sessionData.value.strokes = sessionData.value.strokes.filter(
          stroke => stroke.historyIndex > 0
        )
        // 모든 스트로크의 historyIndex를 1씩 감소
        sessionData.value.strokes.forEach(stroke => {
          stroke.historyIndex--
        })
      }
    }

    /**
     * 캔버스 전체를 다시 그리는 함수 (Stroke 기반 렌더링)
     *
     * [개선 사항]
     * - 기존: history[]에서 Base64 이미지를 복원 (느림, 좌표계 불일치)
     * - 개선: sessionData.strokes에서 직접 렌더링 (빠름, 좌표계 일치)
     *
     * [장점]
     * 1. 스트로크 사라짐 문제 해결: 논리 좌표만 사용하므로 zoom/pan과 무관
     * 2. 이미지 출력 문제 해결: overlayImage도 동일한 렌더링 사이클에서 처리
     * 3. 드래그 끊김 개선: Base64 디코딩 제거로 성능 향상
     */
    const redrawCanvas = () => {
      if (!ctx || !canvas.value) return

      // 1. 캔버스 전체 클리어 (변환 매트릭스 무관)
      ctx.save()
      ctx.setTransform(1, 0, 0, 1, 0, 0) // 변환 초기화
      ctx.clearRect(0, 0, canvas.value.width, canvas.value.height)
      ctx.restore()

      // 2. 변환 매트릭스 적용 (zoom, pan)
      ctx.save()
      ctx.translate(panX.value, panY.value)
      ctx.scale(zoom.value, zoom.value)

      // 3. 오버레이 이미지 먼저 그리기 (스트로크 아래에 표시)
      if (overlayImage.value) {
        try {
          const drawX = overlayImagePosition.value.x
          const drawY = overlayImagePosition.value.y
          const drawWidth = overlayImageSize.value.width
          const drawHeight = overlayImageSize.value.height

          // 이미지 크기가 설정되지 않은 경우 자동 계산
          if (drawWidth === 0 || drawHeight === 0) {
            const maxSize = 200
            let imgWidth = overlayImage.value.naturalWidth || overlayImage.value.width
            let imgHeight = overlayImage.value.naturalHeight || overlayImage.value.height

            if (imgWidth > maxSize || imgHeight > maxSize) {
              const scale = Math.min(maxSize / imgWidth, maxSize / imgHeight)
              imgWidth = Math.floor(imgWidth * scale)
              imgHeight = Math.floor(imgHeight * scale)
            }

            overlayImageSize.value = { width: imgWidth, height: imgHeight }
          }

          // 안티앨리어싱 설정
          ctx.imageSmoothingEnabled = true
          ctx.imageSmoothingQuality = 'high'

          ctx.drawImage(
            overlayImage.value,
            Math.floor(drawX),
            Math.floor(drawY),
            Math.floor(overlayImageSize.value.width),
            Math.floor(overlayImageSize.value.height)
          )
        } catch (error) {
          console.warn('오버레이 이미지 그리기 실패:', error)
        }
      }

      // 4. 현재 historyStep 기준으로 유효한 스트로크만 렌더링
      const visibleStrokes = getVisibleStrokes()

      for (const stroke of visibleStrokes) {
        // 지우개는 그리지 않음 (이미 지워진 상태)
        if (stroke.tool === 'eraser') continue

        // 스트로크 시작
        ctx.beginPath()
        ctx.strokeStyle = stroke.color
        ctx.lineWidth = stroke.strokeWidth
        ctx.lineCap = 'round'
        ctx.lineJoin = 'round'

        // 스트로크의 모든 포인트 그리기
        const points = stroke.points
        if (points.length === 0) continue

        // 첫 포인트로 이동
        ctx.moveTo(points[0].x, points[0].y)

        // 나머지 포인트들을 연결
        for (let i = 1; i < points.length; i++) {
          ctx.lineTo(points[i].x, points[i].y)
        }

        // 실제 그리기 실행
        ctx.stroke()
      }

      // 5. 변환 매트릭스 복원
      ctx.restore()
    }

    // 실행 취소/다시 실행
    const canUndo = ref(false)
    const canRedo = ref(false)

    const undo = () => {
      if (historyStep.value > 0) {
        historyStep.value--
        redrawCanvas()
        sessionData.value.stats.undoCount++

        // Undo 이벤트 로깅
        logEvent('undo', {
          historyStep: historyStep.value,
          totalHistoryLength: history.value.length
        })
      }
    }

    const redo = () => {
      if (historyStep.value < history.value.length - 1) {
        historyStep.value++
        redrawCanvas()
        sessionData.value.stats.redoCount++

        // Redo 이벤트 로깅
        logEvent('redo', {
          historyStep: historyStep.value,
          totalHistoryLength: history.value.length
        })
      }
    }

    // 전체 지우기
    const clearAll = () => {
      if (!ctx || !canvas.value) return

      // 캔버스 클리어
      ctx.clearRect(0, 0, canvas.value.width, canvas.value.height)

      // 오버레이 이미지가 있으면 다시 그리기
      if (overlayImage.value) {
        drawOverlayImage()
      }

      hasDrawn.value = false
      saveToHistory()

      // 전체 지우기 이벤트 로깅
      logEvent('clear_all', {
        strokesCleared: sessionData.value.strokes.length
      })
    }

    // 세션 데이터 완전 초기화 (새 문제 선택 시 사용)
    const resetSessionData = () => {
      // 세션 데이터 초기화
      sessionData.value = {
        sessionId: generateUUID(),
        startTime: Date.now(),
        strokes: [],
        events: [],
        capabilities: {
          pressure: false,
          tilt: false,
          twist: false
        },
        stats: {
          undoCount: 0,
          redoCount: 0,
          eraserCount: 0,
          zoomCount: 0,
          panCount: 0,
          toolChanges: 0
        }
      }

      // 캔버스 히스토리 초기화
      history.value = []
      historyStep.value = -1

      // 캔버스 클리어
      if (ctx && canvas.value) {
        ctx.clearRect(0, 0, canvas.value.width, canvas.value.height)
      }

      // 오버레이 이미지 제거
      overlayImage.value = null

      // 줌/팬 초기화
      zoom.value = 1.0
      panX.value = 0
      panY.value = 0

      hasDrawn.value = false

      // 캔버스 다시 그리기
      redrawCanvas()

      // 새 세션 시작 이벤트 로깅
      logEvent('session_start', {
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        screenWidth: window.screen.width,
        screenHeight: window.screen.height,
        viewportWidth: window.innerWidth,
        viewportHeight: window.innerHeight,
        devicePixelRatio: window.devicePixelRatio || 1
      })

      console.log('세션 데이터 완전 초기화 완료')
    }

    // 확대/축소 기능
    const zoomIn = () => {
      const previousZoom = zoom.value
      zoom.value = Math.min(zoom.value * 1.2, 5)

      if (zoom.value !== previousZoom) {
        sessionData.value.stats.zoomCount++
        logEvent('zoom_in', {
          previousZoom,
          newZoom: zoom.value,
          centerX: window.innerWidth / 2,
          centerY: window.innerHeight / 2,
          viewportWidth: window.innerWidth,
          viewportHeight: window.innerHeight
        })
      }

      redrawCanvas()
    }

    const zoomOut = () => {
      const previousZoom = zoom.value
      zoom.value = Math.max(zoom.value / 1.2, 0.2)

      if (zoom.value !== previousZoom) {
        sessionData.value.stats.zoomCount++
        logEvent('zoom_out', {
          previousZoom,
          newZoom: zoom.value,
          centerX: window.innerWidth / 2,
          centerY: window.innerHeight / 2,
          viewportWidth: window.innerWidth,
          viewportHeight: window.innerHeight
        })
      }

      redrawCanvas()
    }

    const resetZoom = () => {
      const previousZoom = zoom.value
      const previousPanX = panX.value
      const previousPanY = panY.value

      zoom.value = 1
      panX.value = 0
      panY.value = 0

      if (previousZoom !== 1 || previousPanX !== 0 || previousPanY !== 0) {
        sessionData.value.stats.zoomCount++
        logEvent('zoom_reset', {
          previousZoom,
          newZoom: 1,
          previousPanX,
          previousPanY,
          newPanX: 0,
          newPanY: 0,
          centerX: window.innerWidth / 2,
          centerY: window.innerHeight / 2,
          viewportWidth: window.innerWidth,
          viewportHeight: window.innerHeight
        })
      }

      redrawCanvas()
    }

    /**
     * 오버레이 이미지 추가 (개선 버전)
     *
     * [개선 사항]
     * - 이미지 추가 후 redrawCanvas() 호출하여 히스토리 통합
     * - 이미지가 다른 작업 후에도 유지되도록 보장
     */
    const addOverlayImage = (imageData) => {
      if (!imageData || !imageData.src) {
        console.warn('잘못된 이미지 데이터:', imageData)
        return
      }

      // 기존 이미지 정리
      if (overlayImage.value) {
        overlayImage.value = null
        overlayImageData.value = null
      }

      const img = new Image()

      img.onload = () => {
        try {
          overlayImage.value = img
          overlayImageData.value = imageData

          // 안전한 초기 위치 설정 (논리 좌표)
          const safeX = Math.max(10, Math.min(100, 20))
          const safeY = Math.max(10, Math.min(100, 20))

          overlayImagePosition.value = { x: safeX, y: safeY }
          overlayImageSize.value = { width: 0, height: 0 } // redrawCanvas에서 자동 계산

          // 전체 캔버스 다시 그리기 (이미지 포함)
          if (ctx && canvas.value) {
            redrawCanvas() // drawOverlayImage 대신 redrawCanvas 호출
            hasDrawn.value = true
          }

          console.log('오버레이 이미지 로드 완료:', {
            width: img.naturalWidth || img.width,
            height: img.naturalHeight || img.height
          })
        } catch (error) {
          console.error('이미지 처리 오류:', error)
          overlayImage.value = null
          overlayImageData.value = null
        }
      }

      img.onerror = (error) => {
        console.error('이미지 로드 실패:', error)
        overlayImage.value = null
        overlayImageData.value = null
      }

      // CORS 예방 대용
      img.crossOrigin = 'anonymous'
      img.src = imageData.src
    }


    // 히스토리 상태 업데이트
    watch([historyStep, history], () => {
      canUndo.value = historyStep.value > 0
      canRedo.value = historyStep.value < history.value.length - 1
    }, { deep: true })

    // 디바이스 회전/리사이즈 대응 (안정화된 버전)
    const handleResize = () => {
      if (!canvas.value || !canvasContainer.value) return

      // 디바운스 처리
      clearTimeout(handleResize.timeout)
      handleResize.timeout = setTimeout(() => {
        performResize()
      }, 100)
    }

    const performResize = () => {
      if (!canvas.value || !canvasContainer.value) return

      try {
        // 상태 저장 (더 안전하게)
        const savedState = {
          overlayImage: overlayImage.value,
          overlayImageData: overlayImageData.value ? { ...overlayImageData.value } : null,
          overlayPosition: overlayImagePosition.value ? { ...overlayImagePosition.value } : { x: 20, y: 20 },
          overlaySize: overlayImageSize.value ? { ...overlayImageSize.value } : { width: 0, height: 0 },
          currentZoom: zoom.value,
          currentPanX: panX.value,
          currentPanY: panY.value,
          historyData: history.value[historyStep.value] || null,
          wasDrawn: hasDrawn.value
        }

        // 리사이즈 수행
        nextTick(() => {
          try {
            // 캔버스 재초기화
            initCanvas()

            // 상태 복원
            if (savedState.historyData && savedState.wasDrawn) {
              const img = new Image()
              img.onload = () => {
                try {
                  if (ctx && canvas.value) {
                    ctx.drawImage(img, 0, 0)
                  }
                  restoreOverlayImage(savedState)
                } catch (error) {
                  console.warn('히스토리 복원 실패:', error)
                  restoreOverlayImage(savedState)
                }
              }
              img.onerror = () => {
                console.warn('히스토리 이미지 로드 실패')
                restoreOverlayImage(savedState)
              }
              img.src = savedState.historyData
            } else {
              restoreOverlayImage(savedState)
            }

            // 줄 및 확대/축소 상태 복원
            zoom.value = savedState.currentZoom
            panX.value = savedState.currentPanX
            panY.value = savedState.currentPanY

          } catch (error) {
            console.error('리사이즈 수행 오류:', error)
          }
        })
      } catch (error) {
        console.error('리사이즈 준비 오류:', error)
      }
    }

    const restoreOverlayImage = (savedState) => {
      if (savedState.overlayImage && savedState.overlayImageData) {
        try {
          overlayImage.value = savedState.overlayImage
          overlayImageData.value = savedState.overlayImageData
          overlayImagePosition.value = savedState.overlayPosition
          overlayImageSize.value = savedState.overlaySize

          if (ctx && canvas.value) {
            drawOverlayImage()
          }
        } catch (error) {
          console.warn('오버레이 이미진 복원 실패:', error)
        }
      }
    }

    // 컴포넌트 마운트 시 초기화 (강화된 버전)
    onMounted(() => {
      nextTick(() => {
        initCanvas()

        // 세션 시작 이벤트 로깅
        logEvent('session_start', {
          userAgent: navigator.userAgent,
          platform: navigator.platform,
          screenWidth: window.screen.width,
          screenHeight: window.screen.height,
          viewportWidth: window.innerWidth,
          viewportHeight: window.innerHeight,
          devicePixelRatio: window.devicePixelRatio || 1
        })

        // 리사이즈 이벤트 등록
        window.addEventListener('resize', handleResize, { passive: true })

        // 디바이스 회전 이벤트 등록
        window.addEventListener('orientationchange', () => {
          // 회전 완료 후 지연 처리
          setTimeout(handleResize, 200)
        }, { passive: true })

        // 비쥬얼 뷰포트 지원 (모바일 브라우저)
        if (window.visualViewport) {
          window.visualViewport.addEventListener('resize', handleResize, { passive: true })
        }
      })
    })

    // 컴포넌트 언마운트 시 정리
    onUnmounted(() => {
      // 모든 이벤트 리스너 제거
      window.removeEventListener('resize', handleResize)
      window.removeEventListener('orientationchange', handleResize)

      if (window.visualViewport) {
        window.visualViewport.removeEventListener('resize', handleResize)
      }

      // 타이머 정리
      if (handleResize.timeout) {
        clearTimeout(handleResize.timeout)
      }
    })

    return {
      canvas,
      canvasContainer,
      isDrawing,
      hasDrawn,
      currentTool,
      currentColor,
      customColor,
      strokeWidth,
      colors,
      canUndo,
      canRedo,
      horizontalLines,
      verticalLines,
      startDrawing,
      draw,
      stopDrawing,
      handleMouseMove,
      setTool,
      setColor,
      updateStrokeWidth,
      undo,
      redo,
      clearAll,
      resetSessionData,
      addOverlayImage,
      zoomIn,
      zoomOut,
      resetZoom,
      zoom,
      redrawCanvas,
      sessionData,
      // downloadSessionData 제거됨 (요청사항 - 사용자가 JSON을 다운로드하지 못하도록)
      generateSessionData,
      getVisibleStrokes,  // 화면에 보이는 스트로크만 반환
      getSubmissionData,  // API 제출용 데이터 (전체 + 가시 스트로크)
      eraserCursorStyle,
      updateEraserCursor,
      handlePointerDown,
      handlePointerMove,
      handlePointerUp,
      handleTouchStart,
      handleTouchMove,
      handleTouchEnd
    }
  }
}
</script>

<style scoped>
.memo-canvas-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--background-color);
  overflow: hidden;
}

.toolbar {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: rgba(255, 251, 245, 0.95);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  flex-wrap: nowrap;
  gap: 8px;
  z-index: 10;
  transition: all 0.2s ease;
}

.toolbar-section {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tool-btn {
  color: var(--text-secondary);
}

.tool-btn.active {
  background: var(--primary-color);
  color: white;
}

.stroke-width-control {
  display: flex;
  align-items: center;
  gap: 4px;
}

.control-label {
  font-size: 10px;
  color: var(--text-secondary);
  font-weight: 500;
  white-space: nowrap;
}

.stroke-slider {
  width: 60px;
  height: 3px;
  background: var(--border-color);
  border-radius: 2px;
  outline: none;
  cursor: pointer;
}

.stroke-slider::-webkit-slider-thumb {
  width: 14px;
  height: 14px;
  background: var(--primary-color);
  border-radius: 50%;
  cursor: pointer;
  -webkit-appearance: none;
}

.stroke-value {
  font-size: 10px;
  color: var(--text-primary);
  font-weight: 500;
  min-width: 16px;
  text-align: center;
}

.color-palette {
  display: flex;
  align-items: center;
  gap: 6px;
}

.color-grid {
  display: grid;
  grid-template-columns: repeat(4, 20px);
  grid-template-rows: repeat(2, 20px);
  gap: 2px;
}

.color-btn {
  width: 20px;
  height: 20px;
  border: 2px solid transparent;
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.15s ease;
  position: relative;
}

.color-btn.active {
  border-color: var(--primary-color);
  transform: scale(1.1);
  box-shadow: 0 2px 4px rgba(217, 119, 6, 0.3);
}

.color-btn:hover {
  transform: scale(1.05);
}

.custom-color {
  position: relative;
}

.color-picker {
  width: 20px;
  height: 20px;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  background: transparent;
}

.action-btn {
  color: var(--text-secondary);
}

.action-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.action-btn:hover:not(:disabled) {
  color: var(--primary-color);
}

.clear-all:hover:not(:disabled) {
  color: #dc2626;
}

.data-collection-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 6px 8px;
  background: rgba(217, 119, 6, 0.05);
  border: 1px solid rgba(217, 119, 6, 0.2);
  border-radius: 8px;
  font-size: 11px;
}

.data-stats {
  display: flex;
  gap: 8px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 2px;
}

.stat-label {
  color: var(--text-secondary);
  font-weight: 500;
}

.stat-value {
  color: var(--primary-color);
  font-weight: 600;
  font-family: 'Courier New', monospace;
}

.capabilities {
  display: flex;
  gap: 4px;
}

.capability {
  padding: 2px 4px;
  border-radius: 4px;
  background: rgba(107, 114, 128, 0.1);
  color: var(--text-secondary);
  font-size: 10px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.capability.active {
  background: var(--primary-color);
  color: white;
}

.download-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.2s ease;
}

.download-btn:hover {
  background: #ea580c;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(217, 119, 6, 0.3);
}

.download-text {
  font-size: 12px;
}

.canvas-container {
  flex: 1;
  position: relative;
  background: var(--surface-color);
  margin: 16px;
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  overflow: hidden;
}

/* 지우개 커서 */
.canvas-container.eraser-cursor {
  cursor: none;
}

.canvas-container.eraser-cursor::before {
  content: '';
  position: absolute;
  pointer-events: none;
  z-index: 1000;
  border-radius: 50%;
  border: 2px solid #dc2626;
  background: rgba(220, 38, 38, 0.1);
  width: var(--eraser-size, 20px);
  height: var(--eraser-size, 20px);
  left: var(--cursor-x, -100px);
  top: var(--cursor-y, -100px);
  transform: translate(-50%, -50%);
  transition: width 0.2s ease, height 0.2s ease;
  opacity: 0;
}

.canvas-container.eraser-cursor:hover::before {
  opacity: 1;
}

.guide-lines {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 1;
}

.guide-line {
  position: absolute;
  background: #e2e8f0;
  opacity: 0.3;
}

.guide-line.horizontal {
  width: 100%;
  height: 1px;
}

.guide-line.vertical {
  height: 100%;
  width: 1px;
}

.memo-canvas {
  position: relative;
  width: 100%;
  height: 100%;
  touch-action: none;
  z-index: 3;
}

.memo-canvas[data-tool="pen"] {
  cursor: crosshair;
}

.memo-canvas[data-tool="eraser"] {
  cursor: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8" stroke="black" stroke-width="1" fill="none"/></svg>') 12 12, auto;
}

.memo-canvas[data-tool="hand"] {
  cursor: grab;
}

.memo-canvas[data-tool="hand"]:active {
  cursor: grabbing;
}

.canvas-guide {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: var(--text-secondary);
  pointer-events: none;
  opacity: 0.6;
}

.canvas-guide svg {
  margin-bottom: 12px;
  opacity: 0.5;
}

.canvas-guide p {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 4px;
}

.guide-subtitle {
  font-size: 14px !important;
  font-weight: 400 !important;
  opacity: 0.8;
}

/* 태블릿 가로뷰 우선 반응형 */
@media (min-width: 1024px) and (orientation: landscape) {
  .memo-canvas-container {
    height: 100%;
  }

  .toolbar {
    padding: 6px 12px;
    gap: 8px;
  }

  .toolbar-section {
    gap: 6px;
  }

  .tool-btn, .action-btn {
    width: 32px;
    height: 32px;
  }

  .color-grid {
    grid-template-columns: repeat(4, 18px);
    grid-template-rows: repeat(2, 18px);
    gap: 2px;
  }

  .color-btn {
    width: 18px;
    height: 18px;
  }

  .color-picker {
    width: 18px;
    height: 18px;
  }

  .stroke-slider {
    width: 60px;
  }

  .control-label {
    font-size: 10px;
  }

  .canvas-container {
    margin: 8px;
  }

}

@media (min-width: 768px) and (max-width: 1023px) {
  .toolbar {
    padding: 6px 12px;
    gap: 8px;
  }

  .toolbar-section {
    gap: 6px;
  }

  .tool-btn, .action-btn {
    width: 32px;
    height: 32px;
  }

  .color-grid {
    grid-template-columns: repeat(4, 17px);
    grid-template-rows: repeat(2, 17px);
    gap: 2px;
  }

  .color-btn {
    width: 17px;
    height: 17px;
  }

  .color-picker {
    width: 17px;
    height: 17px;
  }

  .stroke-slider {
    width: 50px;
  }

  .control-label {
    font-size: 10px;
  }

}

@media (max-width: 767px) {
  .toolbar {
    padding: 6px 8px;
    gap: 4px;
    flex-wrap: wrap;
  }

  .toolbar-section {
    gap: 4px;
    flex-wrap: wrap;
  }

  .toolbar-section:first-child {
    order: 1;
  }

  .toolbar-section:last-child {
    order: 3;
  }

  .toolbar-section:nth-child(2) {
    order: 2;
    flex: 1;
    justify-content: center;
  }

  .tool-btn, .action-btn {
    width: 28px;
    height: 28px;
  }

  .color-grid {
    grid-template-columns: repeat(4, 16px);
    grid-template-rows: repeat(2, 16px);
    gap: 1px;
  }

  .color-btn {
    width: 16px;
    height: 16px;
  }

  .color-picker {
    width: 16px;
    height: 16px;
  }

  .stroke-width-control {
    gap: 4px;
  }

  .stroke-slider {
    width: 40px;
  }

  .color-palette {
    gap: 4px;
  }

  .data-collection-info {
    display: none;
  }

  .download-btn {
    padding: 6px 8px;
  }

  .download-text {
    display: none;
  }

  .canvas-container {
    margin: 8px;
  }

  .guide-line.horizontal {
    opacity: 0.15;
  }

  .guide-line.vertical {
    opacity: 0.15;
  }

  .answer-zone {
    width: 180px;
    height: 70px;
    bottom: 8px;
    right: 8px;
  }

  .canvas-guide p {
    font-size: 14px;
  }

  .guide-subtitle {
    font-size: 12px !important;
  }

  .memo-canvas {
    cursor: pointer;
  }
}

/* 고해상도 디스플레이 지원 */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
  .memo-canvas {
    image-rendering: pixelated;
    image-rendering: -moz-crisp-edges;
    image-rendering: crisp-edges;
  }
}
</style>