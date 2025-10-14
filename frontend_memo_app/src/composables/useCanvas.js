/**
 * 캔버스 렌더링 Composable
 * 캔버스 초기화, 좌표 변환, 렌더링 로직
 */

import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import * as CanvasConstants from '../constants/canvas.js'
import { TOOL_ERASER } from '../constants/tools.js'
import { screenToCanvas, canvasToScreen } from '../utils/canvas.js'

export function useCanvas(sessionData, historyStep) {
  // Canvas 요소 참조
  const canvasRef = ref(null)
  const ctx = ref(null)

  // 뷰포트 상태
  const zoom = ref(CanvasConstants.DEFAULT_ZOOM)
  const panX = ref(0)
  const panY = ref(0)
  const canvasWidth = ref(CanvasConstants.DEFAULT_CANVAS_WIDTH)
  const canvasHeight = ref(CanvasConstants.DEFAULT_CANVAS_HEIGHT)

  // 오버레이 이미지 상태
  const overlayImages = ref([])

  // Computed
  const transformMatrix = computed(() => {
    return {
      zoom: zoom.value,
      panX: panX.value,
      panY: panY.value
    }
  })

  /**
   * 캔버스 초기화
   * @param {HTMLCanvasElement} canvas - 캔버스 엘리먼트
   */
  function initCanvas(canvas) {
    if (!canvas) return

    canvasRef.value = canvas
    ctx.value = canvas.getContext('2d')

    // 캔버스 크기 설정
    resizeCanvas()

    // 초기 렌더링
    redraw()
  }

  /**
   * 캔버스 크기 조정
   */
  function resizeCanvas() {
    if (!canvasRef.value) return

    const container = canvasRef.value.parentElement
    if (container) {
      canvasWidth.value = container.clientWidth
      canvasHeight.value = container.clientHeight
      canvasRef.value.width = canvasWidth.value
      canvasRef.value.height = canvasHeight.value
    }

    redraw()
  }

  /**
   * 스크린 좌표를 캔버스 좌표로 변환
   * @param {Event} event - 포인터 이벤트
   * @returns {object} { x, y } 캔버스 픽셀 좌표 (뷰포트 기준)
   */
  function getCoordinates(event) {
    if (!canvasRef.value) return { x: 0, y: 0 }

    const rect = canvasRef.value.getBoundingClientRect()
    let clientX, clientY

    // 터치 이벤트 처리
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

    // 단순 픽셀 좌표 반환 (zoom/pan 적용 안함)
    const x = clientX - rect.left
    const y = clientY - rect.top

    return { x, y }
  }

  /**
   * 캔버스 좌표를 스크린 좌표로 변환
   * @param {number} x - 캔버스 X 좌표
   * @param {number} y - 캔버스 Y 좌표
   * @returns {object} { x, y } 스크린 좌표
   */
  function getScreenCoordinates(x, y) {
    return canvasToScreen(x, y, zoom.value, panX.value, panY.value)
  }

  /**
   * 캔버스 전체 지우기
   */
  function clearCanvas() {
    if (!ctx.value) return

    ctx.value.clearRect(0, 0, canvasWidth.value, canvasHeight.value)
  }

  /**
   * 캔버스 전체 다시 그리기
   *
   * @param {number} scrollY - 스크롤 Y 오프셋 (절대 좌표 → 뷰포트 좌표 변환용)
   * @param {object|null} currentStroke - 현재 그리는 중인 스트로크 (실시간 렌더링용)
   */
  function redraw(scrollY = 0, currentStroke = null) {
    if (!ctx.value) return

    // 캔버스 초기화
    clearCanvas()

    // 완료된 스트로크 그리기
    drawStrokes(scrollY)

    // 현재 그리는 중인 스트로크 그리기 (실시간)
    if (currentStroke) {
      if (currentStroke.tool === TOOL_ERASER) {
        drawEraserStroke(currentStroke, scrollY)
      } else {
        drawPenStroke(currentStroke, scrollY)
      }
    }

    // 오버레이 이미지 그리기
    drawOverlayImages(scrollY)
  }

  /**
   * 스트로크 그리기
   * @param {number} scrollY - 스크롤 Y 오프셋
   */
  function drawStrokes(scrollY = 0) {
    if (!ctx.value || !sessionData.value) return

    const strokes = sessionData.value.strokes.filter(stroke => {
      // historyIndex가 없거나 현재 단계보다 큰 스트로크는 제외
      if (stroke.historyIndex === undefined) return false
      return stroke.historyIndex >= 0 && stroke.historyIndex <= historyStep.value
    })

    strokes.forEach(stroke => {
      if (stroke.tool === TOOL_ERASER) {
        drawEraserStroke(stroke, scrollY)
      } else {
        drawPenStroke(stroke, scrollY)
      }
    })
  }

  /**
   * 펜 스트로크 그리기
   * @param {object} stroke - 스트로크 데이터
   * @param {number} scrollY - 스크롤 Y 오프셋
   */
  function drawPenStroke(stroke, scrollY = 0) {
    if (!ctx.value || !stroke.points || stroke.points.length === 0) return

    ctx.value.save()

    ctx.value.strokeStyle = stroke.color
    ctx.value.lineWidth = stroke.strokeWidth
    ctx.value.lineCap = 'round'
    ctx.value.lineJoin = 'round'

    ctx.value.beginPath()

    // 첫 포인트로 이동 (절대 좌표 → 뷰포트 좌표 변환)
    const firstPoint = stroke.points[0]
    ctx.value.moveTo(firstPoint.x, firstPoint.y - scrollY)

    // 나머지 포인트 그리기
    for (let i = 1; i < stroke.points.length; i++) {
      const point = stroke.points[i]

      // 필압이 있으면 선 굵기 조정
      if (point.pressure !== null && point.pressure > 0) {
        const pressureWidth = stroke.strokeWidth * (0.5 + point.pressure * 0.5)
        ctx.value.lineWidth = pressureWidth
      }

      ctx.value.lineTo(point.x, point.y - scrollY)
    }

    ctx.value.stroke()
    ctx.value.restore()
  }

  /**
   * 지우개 스트로크 그리기
   * @param {object} stroke - 스트로크 데이터
   * @param {number} scrollY - 스크롤 Y 오프셋
   */
  function drawEraserStroke(stroke, scrollY = 0) {
    if (!ctx.value || !stroke.points || stroke.points.length === 0) return

    ctx.value.save()

    ctx.value.globalCompositeOperation = 'destination-out'
    ctx.value.lineWidth = CanvasConstants.ERASER_SIZE
    ctx.value.lineCap = 'round'
    ctx.value.lineJoin = 'round'

    ctx.value.beginPath()

    const firstPoint = stroke.points[0]
    ctx.value.moveTo(firstPoint.x, firstPoint.y - scrollY)

    for (let i = 1; i < stroke.points.length; i++) {
      const point = stroke.points[i]
      ctx.value.lineTo(point.x, point.y - scrollY)
    }

    ctx.value.stroke()
    ctx.value.restore()
  }

  /**
   * 오버레이 이미지 그리기
   * @param {number} scrollY - 스크롤 Y 오프셋
   */
  function drawOverlayImages(scrollY = 0) {
    if (!ctx.value) return

    overlayImages.value.forEach(imageData => {
      if (imageData.img && imageData.img.complete) {
        ctx.value.drawImage(
          imageData.img,
          imageData.x,
          imageData.y - scrollY,
          imageData.width,
          imageData.height
        )
      }
    })
  }

  /**
   * 오버레이 이미지 추가
   * @param {object} imageData - { src, x, y, width, height }
   */
  function addOverlayImage(imageData) {
    const img = new Image()
    img.onload = () => {
      overlayImages.value.push({
        img,
        x: imageData.x || 0,
        y: imageData.y || 0,
        width: imageData.width || img.width,
        height: imageData.height || img.height,
        id: Date.now()
      })
      redraw()
    }
    img.src = imageData.src
  }

  /**
   * 오버레이 이미지 제거
   * @param {number} id - 이미지 ID
   */
  function removeOverlayImage(id) {
    overlayImages.value = overlayImages.value.filter(img => img.id !== id)
    redraw()
  }

  /**
   * 줌 설정
   * @param {number} newZoom - 새로운 줌 레벨
   * @param {number} centerX - 줌 중심 X (스크린 좌표)
   * @param {number} centerY - 줌 중심 Y (스크린 좌표)
   */
  function setZoom(newZoom, centerX, centerY) {
    // 줌 레벨 제한
    newZoom = Math.max(CanvasConstants.MIN_ZOOM, Math.min(CanvasConstants.MAX_ZOOM, newZoom))

    if (centerX !== undefined && centerY !== undefined) {
      // 줌 중심 기준으로 pan 조정
      const oldZoom = zoom.value
      const zoomRatio = newZoom / oldZoom

      panX.value = centerX - (centerX - panX.value) * zoomRatio
      panY.value = centerY - (centerY - panY.value) * zoomRatio
    }

    zoom.value = newZoom
    redraw()
  }

  /**
   * 팬 설정
   * @param {number} dx - X 이동량
   * @param {number} dy - Y 이동량
   */
  function setPan(dx, dy) {
    panX.value += dx
    panY.value += dy
    redraw()
  }

  /**
   * 뷰포트 초기화
   */
  function resetViewport() {
    zoom.value = CanvasConstants.DEFAULT_ZOOM
    panX.value = 0
    panY.value = 0
    redraw()
  }

  /**
   * 윈도우 리사이즈 핸들러
   */
  function handleResize() {
    resizeCanvas()
  }

  // 라이프사이클: 리사이즈 이벤트 리스너 등록/해제
  onMounted(() => {
    window.addEventListener('resize', handleResize)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('resize', handleResize)
  })

  return {
    // Refs
    canvasRef,
    ctx,
    zoom,
    panX,
    panY,
    canvasWidth,
    canvasHeight,
    overlayImages,

    // Computed
    transformMatrix,

    // Methods
    initCanvas,
    resizeCanvas,
    getCoordinates,
    getScreenCoordinates,
    clearCanvas,
    redraw,
    drawStrokes,
    drawPenStroke,
    drawEraserStroke,
    drawOverlayImages,
    addOverlayImage,
    removeOverlayImage,
    setZoom,
    setPan,
    resetViewport
  }
}
