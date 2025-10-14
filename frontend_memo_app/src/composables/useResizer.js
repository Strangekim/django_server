/**
 * 리사이즈 핸들 Composable
 * 문제 영역과 메모 영역의 크기를 동적으로 조절
 */

import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const STORAGE_KEY = 'problem-area-width'
const DEFAULT_WIDTH = 30 // percentage
const MIN_WIDTH = 20 // percentage
const MAX_WIDTH = 60 // percentage

export function useResizer() {
  // 상태
  const isResizing = ref(false)
  const problemWidth = ref(DEFAULT_WIDTH)
  const startX = ref(0)
  const startWidth = ref(0)
  const containerWidth = ref(0)

  // Computed
  const problemWidthPercent = computed(() => `${problemWidth.value}%`)
  const memoWidthPercent = computed(() => `${100 - problemWidth.value}%`)

  /**
   * localStorage에서 저장된 너비 불러오기
   */
  function loadSavedWidth() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved) {
        const width = parseFloat(saved)
        if (width >= MIN_WIDTH && width <= MAX_WIDTH) {
          problemWidth.value = width
        }
      }
    } catch (error) {
      console.warn('[useResizer] Failed to load saved width:', error)
    }
  }

  /**
   * localStorage에 현재 너비 저장
   */
  function saveWidth() {
    try {
      localStorage.setItem(STORAGE_KEY, problemWidth.value.toString())
    } catch (error) {
      console.warn('[useResizer] Failed to save width:', error)
    }
  }

  /**
   * 리사이즈 시작
   * @param {MouseEvent|TouchEvent} event - 이벤트 객체
   * @param {HTMLElement} container - 컨테이너 엘리먼트
   */
  function startResize(event, container) {
    event.preventDefault()
    isResizing.value = true

    // 컨테이너 너비 저장
    if (container) {
      containerWidth.value = container.getBoundingClientRect().width
    }

    // 시작 위치 저장
    if (event.touches) {
      startX.value = event.touches[0].clientX
    } else {
      startX.value = event.clientX
    }

    startWidth.value = problemWidth.value

    // 전역 이벤트 리스너 등록
    document.addEventListener('mousemove', onResize)
    document.addEventListener('mouseup', stopResize)
    document.addEventListener('touchmove', onResize)
    document.addEventListener('touchend', stopResize)

    // 선택 방지
    document.body.style.userSelect = 'none'
    document.body.style.cursor = 'col-resize'
  }

  /**
   * 리사이즈 중
   * @param {MouseEvent|TouchEvent} event - 이벤트 객체
   */
  function onResize(event) {
    if (!isResizing.value) return

    event.preventDefault()

    // 현재 X 위치
    let clientX
    if (event.touches) {
      clientX = event.touches[0].clientX
    } else {
      clientX = event.clientX
    }

    // 이동 거리 계산
    const deltaX = clientX - startX.value

    // 퍼센트로 변환
    const deltaPercent = (deltaX / containerWidth.value) * 100

    // 새 너비 계산
    let newWidth = startWidth.value + deltaPercent

    // 최소/최대 너비 제한
    newWidth = Math.max(MIN_WIDTH, Math.min(MAX_WIDTH, newWidth))

    problemWidth.value = newWidth
  }

  /**
   * 리사이즈 종료
   */
  function stopResize() {
    if (!isResizing.value) return

    isResizing.value = false

    // 전역 이벤트 리스너 제거
    document.removeEventListener('mousemove', onResize)
    document.removeEventListener('mouseup', stopResize)
    document.removeEventListener('touchmove', onResize)
    document.removeEventListener('touchend', stopResize)

    // 스타일 복원
    document.body.style.userSelect = ''
    document.body.style.cursor = ''

    // 너비 저장
    saveWidth()
  }

  /**
   * 너비 리셋
   */
  function resetWidth() {
    problemWidth.value = DEFAULT_WIDTH
    saveWidth()
  }

  /**
   * 특정 너비로 설정
   * @param {number} width - 설정할 너비 (퍼센트)
   */
  function setWidth(width) {
    width = Math.max(MIN_WIDTH, Math.min(MAX_WIDTH, width))
    problemWidth.value = width
    saveWidth()
  }

  // 라이프사이클: 저장된 너비 불러오기
  onMounted(() => {
    loadSavedWidth()
  })

  // 라이프사이클: 정리
  onBeforeUnmount(() => {
    if (isResizing.value) {
      stopResize()
    }
  })

  return {
    // State
    isResizing,
    problemWidth,

    // Computed
    problemWidthPercent,
    memoWidthPercent,

    // Methods
    startResize,
    onResize,
    stopResize,
    resetWidth,
    setWidth,
    loadSavedWidth,
    saveWidth
  }
}
