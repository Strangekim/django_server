/**
 * 히스토리 관리 Composable (Undo/Redo)
 * 스트로크 히스토리 및 실행 취소/다시 실행 기능
 */

import { ref, computed } from 'vue'
import * as EventTypes from '../constants/events.js'

export function useHistory(sessionData, logEvent) {
  // 히스토리 상태
  const history = ref([])
  const historyStep = ref(-1)

  // Computed
  const canUndo = computed(() => historyStep.value > 0)
  const canRedo = computed(() => historyStep.value < history.value.length - 1)

  /**
   * 히스토리에 현재 상태 저장
   * - historyStep만 증가 (sessionData.strokes에 이미 데이터 있음)
   * - 각 스트로크는 historyIndex를 가지고 있음 (생성 시점 기록)
   */
  function saveToHistory() {
    // Redo 분기 처리: 현재 단계 이후의 스트로크 무효화
    if (historyStep.value < history.value.length - 1) {
      // Redo 가능한 스트로크들을 제거 (새로운 분기 생성)
      sessionData.value.strokes = sessionData.value.strokes.filter(
        stroke => stroke.historyIndex === undefined || stroke.historyIndex <= historyStep.value
      )
    }

    // 히스토리 트리밍
    history.value = history.value.slice(0, historyStep.value + 1)

    // 새로운 히스토리 스냅샷 추가
    history.value.push(true)
    historyStep.value = history.value.length - 1

    // 방금 추가된 스트로크에 현재 historyStep 할당
    // historyIndex가 없는 스트로크 = 가장 최근에 추가된 스트로크
    sessionData.value.strokes.forEach(stroke => {
      if (stroke.historyIndex === undefined) {
        stroke.historyIndex = historyStep.value
      }
    })

    // 히스토리 길이 제한 (50개)
    if (history.value.length > 50) {
      history.value.shift()
      historyStep.value--

      // 히스토리 인덱스 0인 스트로크 제거
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
   * 실행 취소 (Undo)
   */
  function undo() {
    if (historyStep.value > 0) {
      historyStep.value--

      // 통계 증가
      sessionData.value.stats.undoCount++

      // Undo 이벤트 로깅
      logEvent(EventTypes.EVENT_UNDO, {
        historyStep: historyStep.value,
        totalHistoryLength: history.value.length
      })

      return true
    }
    return false
  }

  /**
   * 다시 실행 (Redo)
   */
  function redo() {
    if (historyStep.value < history.value.length - 1) {
      historyStep.value++

      // 통계 증가
      sessionData.value.stats.redoCount++

      // Redo 이벤트 로깅
      logEvent(EventTypes.EVENT_REDO, {
        historyStep: historyStep.value,
        totalHistoryLength: history.value.length
      })

      return true
    }
    return false
  }

  /**
   * 전체 지우기
   */
  function clearAll() {
    // Undo 이후의 스트로크는 이미 제거되었거나 무효화됨
    // 현재 유효한 스트로크만 무효화 (historyIndex = -1)
    sessionData.value.strokes = sessionData.value.strokes.filter(
      stroke => stroke.historyIndex === undefined || stroke.historyIndex > historyStep.value
    )

    // Clear all 이벤트 로깅
    logEvent(EventTypes.EVENT_CLEAR_ALL, {})

    // 히스토리에 저장
    saveToHistory()

    return true
  }

  /**
   * 히스토리 초기화
   */
  function resetHistory() {
    history.value = []
    historyStep.value = -1
  }

  /**
   * 현재 히스토리 단계 가져오기
   */
  function getCurrentStep() {
    return historyStep.value
  }

  return {
    // State
    history,
    historyStep,

    // Computed
    canUndo,
    canRedo,

    // Methods
    saveToHistory,
    undo,
    redo,
    clearAll,
    resetHistory,
    getCurrentStep
  }
}
