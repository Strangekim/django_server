/**
 * 드로잉 로직 Composable
 * 펜/지우개 스트로크 생성 및 관리
 */

import { ref } from 'vue'
import { generateUUID } from '../utils/uuid.js'
import { calculateDistance } from '../utils/canvas.js'
import { TOOL_PEN, TOOL_ERASER } from '../constants/tools.js'
import * as EventTypes from '../constants/events.js'

export function useDrawing(sessionData, penInput, historyComposable, logEvent) {
  // 현재 스트로크 상태
  const currentStroke = ref(null)
  const isDrawing = ref(false)

  /**
   * 스트로크 시작
   * @param {object} eventData - 이벤트 데이터 (extractEventData에서 반환)
   * @param {string} tool - 현재 도구
   * @param {string} color - 현재 색상
   * @param {number} strokeWidth - 선 굵기
   */
  function startStroke(eventData, tool, color, strokeWidth) {
    isDrawing.value = true

    // 새로운 스트로크 객체 생성
    currentStroke.value = {
      id: generateUUID(),
      tool: tool,
      color: color,
      strokeWidth: strokeWidth,
      points: [],
      startTime: Date.now() - sessionData.value.startTime,
      endTime: null,
      totalDistance: 0,
      averageSpeed: 0,
      averagePressure: 0,
      boundingBox: null,
      historyIndex: undefined // 히스토리에 저장될 때 설정됨
    }

    // 첫 포인트 추가
    addPoint(eventData)

    // 스트로크 시작 이벤트 로깅
    if (logEvent) {
      logEvent(EventTypes.EVENT_STROKE_START, {
        strokeId: currentStroke.value.id,
        tool: tool,
        color: color,
        strokeWidth: strokeWidth,
        inputType: eventData.inputType,
        timestamp: currentStroke.value.startTime
      })
    }
  }

  /**
   * 포인트 추가
   * @param {object} eventData - 이벤트 데이터
   */
  function addPoint(eventData) {
    if (!currentStroke.value) return

    const point = {
      x: eventData.x,
      y: eventData.y,
      t_ms: eventData.timestamp - currentStroke.value.startTime,
      pressure: eventData.pressure,
      tiltX: eventData.tiltX,
      tiltY: eventData.tiltY,
      twist: eventData.twist,
      inputType: eventData.inputType,
      width: eventData.width || null,
      height: eventData.height || null
    }

    currentStroke.value.points.push(point)

    // 거리 계산 (이전 포인트와의 거리)
    if (currentStroke.value.points.length > 1) {
      const prevPoint = currentStroke.value.points[currentStroke.value.points.length - 2]
      const distance = calculateDistance(prevPoint.x, prevPoint.y, point.x, point.y)
      currentStroke.value.totalDistance += distance
    }
  }

  /**
   * Coalesced Events 처리
   * @param {Array} coalescedEvents - getCoalescedEvents로 가져온 이벤트 배열
   */
  function addCoalescedPoints(coalescedEvents) {
    if (!currentStroke.value || !coalescedEvents || coalescedEvents.length === 0) return

    coalescedEvents.forEach(eventData => {
      addPoint(eventData)
    })
  }

  /**
   * 스트로크 종료
   */
  function endStroke() {
    if (!currentStroke.value) return

    isDrawing.value = false

    // 종료 시간 설정
    currentStroke.value.endTime = Date.now() - sessionData.value.startTime

    // 통계 계산
    calculateStrokeStats()

    // 바운딩 박스 계산
    currentStroke.value.boundingBox = calculateBoundingBox()

    // 세션 데이터에 스트로크 추가
    if (sessionData && sessionData.value) {
      sessionData.value.strokes.push(currentStroke.value)
    }

    // 히스토리에 저장
    if (historyComposable && historyComposable.saveToHistory) {
      historyComposable.saveToHistory()
    }

    // 스트로크 종료 이벤트 로깅
    if (logEvent) {
      logEvent(EventTypes.EVENT_STROKE_END, {
        strokeId: currentStroke.value.id,
        pointCount: currentStroke.value.points.length,
        totalDistance: currentStroke.value.totalDistance,
        averageSpeed: currentStroke.value.averageSpeed,
        averagePressure: currentStroke.value.averagePressure,
        duration: currentStroke.value.endTime - currentStroke.value.startTime
      })
    }

    // 통계 업데이트
    if (currentStroke.value.tool === TOOL_ERASER && sessionData.value) {
      sessionData.value.stats.eraserCount = (sessionData.value.stats.eraserCount || 0) + 1
    }

    // 현재 스트로크 초기화
    currentStroke.value = null
  }

  /**
   * 스트로크 통계 계산
   */
  function calculateStrokeStats() {
    if (!currentStroke.value || currentStroke.value.points.length === 0) return

    const duration = currentStroke.value.endTime - currentStroke.value.startTime

    // 평균 속도 계산 (px/ms)
    if (duration > 0) {
      currentStroke.value.averageSpeed = currentStroke.value.totalDistance / duration
    } else {
      currentStroke.value.averageSpeed = 0
    }

    // 평균 필압 계산
    const pressureValues = currentStroke.value.points
      .map(p => p.pressure)
      .filter(p => p !== null && p > 0)

    if (pressureValues.length > 0) {
      const sum = pressureValues.reduce((acc, val) => acc + val, 0)
      currentStroke.value.averagePressure = sum / pressureValues.length
    } else {
      currentStroke.value.averagePressure = 0
    }
  }

  /**
   * 바운딩 박스 계산
   * @returns {Array} [minX, minY, maxX, maxY]
   */
  function calculateBoundingBox() {
    if (!currentStroke.value || currentStroke.value.points.length === 0) {
      return [0, 0, 0, 0]
    }

    let minX = Infinity
    let minY = Infinity
    let maxX = -Infinity
    let maxY = -Infinity

    currentStroke.value.points.forEach(point => {
      minX = Math.min(minX, point.x)
      minY = Math.min(minY, point.y)
      maxX = Math.max(maxX, point.x)
      maxY = Math.max(maxY, point.y)
    })

    return [minX, minY, maxX, maxY]
  }

  /**
   * 드로잉 취소 (스트로크 버리기)
   */
  function cancelStroke() {
    if (currentStroke.value) {
      currentStroke.value = null
      isDrawing.value = false
    }
  }

  /**
   * 현재 드로잉 중인지 확인
   * @returns {boolean}
   */
  function getIsDrawing() {
    return isDrawing.value
  }

  /**
   * 현재 스트로크 가져오기
   * @returns {object|null}
   */
  function getCurrentStroke() {
    return currentStroke.value
  }

  /**
   * 특정 영역의 스트로크 찾기 (지우개용)
   * @param {number} x - X 좌표
   * @param {number} y - Y 좌표
   * @param {number} radius - 반경
   * @param {number} historyStep - 현재 히스토리 단계
   * @returns {Array} 해당 영역의 스트로크 ID 배열
   */
  function findStrokesInArea(x, y, radius, historyStep) {
    if (!sessionData || !sessionData.value) return []

    const foundStrokes = []

    sessionData.value.strokes.forEach(stroke => {
      // 현재 히스토리 단계에서 보이는 스트로크만 검사
      if (stroke.historyIndex === undefined || stroke.historyIndex > historyStep) {
        return
      }

      // 지우개 스트로크는 제외
      if (stroke.tool === TOOL_ERASER) {
        return
      }

      // 바운딩 박스 빠른 검사
      if (stroke.boundingBox) {
        const [minX, minY, maxX, maxY] = stroke.boundingBox
        if (x + radius < minX || x - radius > maxX || y + radius < minY || y - radius > maxY) {
          return
        }
      }

      // 포인트별 상세 검사
      for (const point of stroke.points) {
        const distance = calculateDistance(x, y, point.x, point.y)
        if (distance <= radius) {
          foundStrokes.push(stroke.id)
          break
        }
      }
    })

    return foundStrokes
  }

  /**
   * 스트로크 무효화 (히스토리 인덱스 -1로 설정)
   * @param {Array} strokeIds - 무효화할 스트로크 ID 배열
   */
  function invalidateStrokes(strokeIds) {
    if (!sessionData || !sessionData.value) return

    sessionData.value.strokes.forEach(stroke => {
      if (strokeIds.includes(stroke.id)) {
        stroke.historyIndex = -1
      }
    })
  }

  return {
    // State
    currentStroke,
    isDrawing,

    // Methods
    startStroke,
    addPoint,
    addCoalescedPoints,
    endStroke,
    calculateStrokeStats,
    calculateBoundingBox,
    cancelStroke,
    getIsDrawing,
    getCurrentStroke,
    findStrokesInArea,
    invalidateStrokes
  }
}
