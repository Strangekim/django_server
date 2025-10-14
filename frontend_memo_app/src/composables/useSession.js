/**
 * 세션 데이터 관리 Composable
 * 세션 ID, 스트로크, 이벤트, 통계 등 세션 관련 데이터 관리
 */

import { ref } from 'vue'
import { generateUUID } from '../utils/uuid.js'
import * as EventTypes from '../constants/events.js'

export function useSession() {
  // 세션 데이터 구조
  const sessionData = ref({
    sessionId: generateUUID(),
    startTime: Date.now(),
    strokes: [],
    events: [],
    capabilities: {
      pressure: false,
      tilt: false,
      twist: false,
      coalesced: false
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

  /**
   * 이벤트 로깅
   * @param {string} eventType - 이벤트 타입 (EVENT_* 상수 사용)
   * @param {object} data - 이벤트 데이터
   */
  function logEvent(eventType, data = {}) {
    const event = {
      type: eventType,
      timestamp: Date.now() - sessionData.value.startTime,
      data
    }
    sessionData.value.events.push(event)
  }

  /**
   * 스트로크 추가
   * @param {object} stroke - 스트로크 데이터
   */
  function addStroke(stroke) {
    sessionData.value.strokes.push(stroke)
  }

  /**
   * 스트로크 업데이트 (마지막 스트로크)
   * @param {object} updates - 업데이트할 필드
   */
  function updateLastStroke(updates) {
    const lastIndex = sessionData.value.strokes.length - 1
    if (lastIndex >= 0) {
      Object.assign(sessionData.value.strokes[lastIndex], updates)
    }
  }

  /**
   * 세션 데이터 생성 (API 제출용)
   * @returns {object} 제출용 세션 데이터
   */
  function generateSessionData() {
    const now = Date.now()
    const sessionDuration = now - sessionData.value.startTime

    return {
      sessionId: sessionData.value.sessionId,
      sessionInfo: {
        startTime: new Date(sessionData.value.startTime).toISOString(),
        endTime: new Date(now).toISOString(),
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
   * 가시 스트로크 필터링 (Undo로 되돌린 것 제외)
   * @param {number} historyStep - 현재 히스토리 단계
   * @returns {Array} 가시 스트로크 배열
   */
  function getVisibleStrokes(historyStep) {
    return sessionData.value.strokes.filter(stroke => {
      if (stroke.historyIndex === undefined) {
        return false
      }
      return stroke.historyIndex >= 0 && stroke.historyIndex <= historyStep
    })
  }

  /**
   * API 제출용 세션 데이터 생성 (가시 스트로크 포함)
   * @param {number} historyStep - 현재 히스토리 단계
   * @returns {object} 제출용 세션 데이터
   */
  function getSubmissionData(historyStep) {
    const baseData = generateSessionData()
    const visibleStrokes = getVisibleStrokes(historyStep)

    return {
      ...baseData,
      canvasData: {
        strokes: baseData.canvasData.strokes,  // 전체 스트로크 (DB 저장용)
        visibleStrokes: visibleStrokes,  // 화면에 보이는 스트로크만 (Mathpix 전송용)
        events: baseData.canvasData.events
      }
    }
  }

  /**
   * 세션 초기화
   */
  function resetSession() {
    sessionData.value = {
      sessionId: generateUUID(),
      startTime: Date.now(),
      strokes: [],
      events: [],
      capabilities: {
        pressure: false,
        tilt: false,
        twist: false,
        coalesced: false
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
    }

    // 세션 시작 이벤트 로깅
    logEvent(EventTypes.EVENT_SESSION_START, {
      sessionId: sessionData.value.sessionId,
      timestamp: sessionData.value.startTime
    })
  }

  /**
   * 통계 증가
   * @param {string} statName - 통계 항목 이름
   * @param {number} amount - 증가량 (기본 1)
   */
  function incrementStat(statName, amount = 1) {
    if (statName in sessionData.value.stats) {
      sessionData.value.stats[statName] += amount
    }
  }

  return {
    // State
    sessionData,

    // Methods
    logEvent,
    addStroke,
    updateLastStroke,
    generateSessionData,
    getVisibleStrokes,
    getSubmissionData,
    resetSession,
    incrementStat
  }
}
