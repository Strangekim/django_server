/**
 * 상하 무한 스크롤 Composable
 * 메모장 스타일의 상하 스크롤 기능 (좌우 이동 제거)
 */

import { ref, computed } from 'vue'
import * as EventTypes from '../constants/events.js'

export function useScroll(sessionData, logEvent) {
  // 스크롤 상태
  const scrollY = ref(0)
  const canvasHeight = ref(0)
  const viewportHeight = ref(0)

  // 관성 스크롤 상태
  const isScrolling = ref(false)
  const velocity = ref(0)
  const lastTouchY = ref(0)
  const lastTouchTime = ref(0)

  // Computed
  const scrollProgress = computed(() => {
    if (canvasHeight.value === 0) return 0
    return scrollY.value / canvasHeight.value
  })

  const canScrollUp = computed(() => scrollY.value > 0)
  const canScrollDown = computed(() => scrollY.value < canvasHeight.value - viewportHeight.value)

  /**
   * 스크롤 시작
   * @param {number} y - 시작 Y 좌표
   * @param {number} timestamp - 타임스탬프
   */
  function startScroll(y, timestamp) {
    isScrolling.value = true
    lastTouchY.value = y
    lastTouchTime.value = timestamp
    velocity.value = 0
  }

  /**
   * 스크롤 이동
   * @param {number} y - 현재 Y 좌표
   * @param {number} timestamp - 타임스탬프
   */
  function moveScroll(y, timestamp) {
    if (!isScrolling.value) return

    const deltaY = lastTouchY.value - y
    const deltaTime = timestamp - lastTouchTime.value

    // 스크롤 위치 업데이트
    scrollY.value = Math.max(0, Math.min(
      scrollY.value + deltaY,
      canvasHeight.value - viewportHeight.value
    ))

    // 속도 계산 (관성 스크롤용)
    if (deltaTime > 0) {
      velocity.value = deltaY / deltaTime
    }

    lastTouchY.value = y
    lastTouchTime.value = timestamp
  }

  /**
   * 스크롤 종료 (관성 스크롤 적용)
   */
  function endScroll() {
    if (!isScrolling.value) return

    isScrolling.value = false

    // 관성 스크롤 적용
    if (Math.abs(velocity.value) > 0.5) {
      applyMomentum()
    }

    // 스크롤 이벤트 로깅
    if (logEvent) {
      logEvent(EventTypes.EVENT_CANVAS_PAN, {
        scrollY: scrollY.value,
        scrollProgress: scrollProgress.value
      })
    }

    // 통계 증가
    if (sessionData && sessionData.value) {
      sessionData.value.stats.panCount = (sessionData.value.stats.panCount || 0) + 1
    }
  }

  /**
   * 관성 스크롤 적용
   */
  function applyMomentum() {
    const friction = 0.95 // 마찰 계수
    const minVelocity = 0.1 // 최소 속도 (이하면 정지)

    const animate = () => {
      velocity.value *= friction

      if (Math.abs(velocity.value) < minVelocity) {
        velocity.value = 0
        return
      }

      // 스크롤 위치 업데이트
      scrollY.value = Math.max(0, Math.min(
        scrollY.value + velocity.value * 16, // 16ms 기준 (60fps)
        canvasHeight.value - viewportHeight.value
      ))

      requestAnimationFrame(animate)
    }

    requestAnimationFrame(animate)
  }

  /**
   * 마우스 휠 스크롤 처리
   * @param {WheelEvent} event - 휠 이벤트
   */
  function handleWheel(event) {
    event.preventDefault()

    const delta = event.deltaY

    // 스크롤 위치 업데이트
    scrollY.value = Math.max(0, Math.min(
      scrollY.value + delta,
      canvasHeight.value - viewportHeight.value
    ))

    // 스크롤 이벤트 로깅 (throttle 적용)
    if (logEvent && Math.abs(delta) > 10) {
      logEvent(EventTypes.EVENT_CANVAS_PAN, {
        scrollY: scrollY.value,
        deltaY: delta,
        scrollProgress: scrollProgress.value
      })
    }
  }

  /**
   * 특정 Y 위치로 스크롤
   * @param {number} targetY - 목표 Y 위치
   * @param {boolean} smooth - 부드러운 애니메이션 여부
   */
  function scrollTo(targetY, smooth = true) {
    targetY = Math.max(0, Math.min(targetY, canvasHeight.value - viewportHeight.value))

    if (!smooth) {
      scrollY.value = targetY
      return
    }

    // 부드러운 스크롤 애니메이션
    const startY = scrollY.value
    const distance = targetY - startY
    const duration = 600 // ms
    const startTime = performance.now()

    const animate = (currentTime) => {
      const elapsed = currentTime - startTime
      const progress = Math.min(elapsed / duration, 1)

      // Ease-out cubic
      const easeProgress = 1 - Math.pow(1 - progress, 3)

      scrollY.value = startY + distance * easeProgress

      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }

    requestAnimationFrame(animate)
  }

  /**
   * 캔버스 높이 설정
   * @param {number} height - 캔버스 높이
   */
  function setCanvasHeight(height) {
    canvasHeight.value = height
  }

  /**
   * 뷰포트 높이 설정
   * @param {number} height - 뷰포트 높이
   */
  function setViewportHeight(height) {
    viewportHeight.value = height
  }

  /**
   * 스크롤 리셋
   */
  function resetScroll() {
    scrollY.value = 0
    velocity.value = 0
    isScrolling.value = false
  }

  /**
   * 현재 스크롤 위치 가져오기
   * @returns {number} 스크롤 Y 위치
   */
  function getScrollY() {
    return scrollY.value
  }

  /**
   * 스크롤 변환 적용 (캔버스 좌표 → 스크린 좌표)
   * @param {number} canvasY - 캔버스 Y 좌표
   * @returns {number} 스크린 Y 좌표
   */
  function applyScrollTransform(canvasY) {
    return canvasY - scrollY.value
  }

  /**
   * 스크롤 역변환 적용 (스크린 좌표 → 캔버스 좌표)
   * @param {number} screenY - 스크린 Y 좌표
   * @returns {number} 캔버스 Y 좌표
   */
  function reverseScrollTransform(screenY) {
    return screenY + scrollY.value
  }

  return {
    // State
    scrollY,
    canvasHeight,
    viewportHeight,
    isScrolling,
    velocity,

    // Computed
    scrollProgress,
    canScrollUp,
    canScrollDown,

    // Methods
    startScroll,
    moveScroll,
    endScroll,
    handleWheel,
    scrollTo,
    setCanvasHeight,
    setViewportHeight,
    resetScroll,
    getScrollY,
    applyScrollTransform,
    reverseScrollTransform
  }
}
