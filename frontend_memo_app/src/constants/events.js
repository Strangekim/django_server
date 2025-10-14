/**
 * 이벤트 타입 상수
 */

// 스트로크 이벤트
export const EVENT_STROKE_START = 'stroke_start'
export const EVENT_STROKE_END = 'stroke_end'

// 도구 변경 이벤트
export const EVENT_TOOL_CHANGE = 'tool_change'
export const EVENT_COLOR_CHANGE = 'color_change'
export const EVENT_STROKE_WIDTH_CHANGE = 'stroke_width_change'

// 편집 이벤트
export const EVENT_UNDO = 'undo'
export const EVENT_REDO = 'redo'
export const EVENT_CLEAR_ALL = 'clear_all'

// 화면 조작 이벤트
export const EVENT_ZOOM_IN = 'zoom_in'
export const EVENT_ZOOM_OUT = 'zoom_out'
export const EVENT_PINCH_ZOOM = 'pinch_zoom'
export const EVENT_CANVAS_PAN = 'canvas_pan'
export const EVENT_IMAGE_DRAG = 'image_drag'

// 세션 이벤트
export const EVENT_SESSION_START = 'session_start'
export const EVENT_SESSION_END = 'session_end'
export const EVENT_WINDOW_FOCUS = 'window_focus'
export const EVENT_WINDOW_BLUR = 'window_blur'
