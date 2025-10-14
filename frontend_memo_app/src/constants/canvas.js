/**
 * 캔버스 관련 상수
 */

// 줌 설정
export const MIN_ZOOM = 0.2
export const MAX_ZOOM = 5
export const DEFAULT_ZOOM = 1
export const ZOOM_STEP = 0.2

// 제스처 임계값
export const GESTURE_THRESHOLD = 10 // 최소 이동 거리 (px)
export const ZOOM_THRESHOLD = 20 // 최소 핀치 거리 (px)
export const GESTURE_DEBOUNCE = 16 // 60fps 제한 (ms)

// 지우개 설정
export const ERASER_SIZE = 20 // 고정 지우개 크기 (px)

// 스트로크 기본값
export const DEFAULT_STROKE_WIDTH = 3
export const MIN_STROKE_WIDTH = 1
export const MAX_STROKE_WIDTH = 20

// 캔버스 크기
export const DEFAULT_CANVAS_WIDTH = 1200
export const DEFAULT_CANVAS_HEIGHT = 800

// 캔버스 기본 색상
export const DEFAULT_COLOR = '#000000'
export const CANVAS_BACKGROUND = '#ffffff'
