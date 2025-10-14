/**
 * 세션 상태 관리 Store
 * 타이머, 펜 입력 능력, 제출 상태 등 세션 관련 상태 관리
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useSessionStore = defineStore('session', () => {
  // 타이머 상태
  const timerRunning = ref(false)
  const timerStartTime = ref(null)
  const timerElapsed = ref(0)

  // 펜 입력 능력 상태
  const penCapabilities = ref(null)

  // 제출 관련 상태
  const pendingSubmission = ref(null)
  const correctAnswerData = ref({
    problemTitle: '',
    sessionId: '',
    score: 0,
    mathpixText: '',
    aiVerification: null
  })

  // Computed
  const hasTimer = computed(() => timerRunning.value)
  const hasPendingSubmission = computed(() => pendingSubmission.value !== null)

  // Actions
  /**
   * 타이머 시작
   */
  function startTimer() {
    timerRunning.value = true
    timerStartTime.value = Date.now()
    console.log('[SessionStore] 타이머 시작')
  }

  /**
   * 타이머 중지
   */
  function stopTimer() {
    timerRunning.value = false
    timerElapsed.value = Date.now() - (timerStartTime.value || Date.now())
    console.log('[SessionStore] 타이머 중지:', timerElapsed.value, 'ms')
  }

  /**
   * 타이머 리셋
   */
  function resetTimer() {
    timerRunning.value = false
    timerStartTime.value = null
    timerElapsed.value = 0
    console.log('[SessionStore] 타이머 리셋')
  }

  /**
   * 펜 능력 업데이트
   * @param {object} capabilities - 펜 입력 능력 (pressure, tilt, coalesced)
   */
  function updatePenCapabilities(capabilities) {
    penCapabilities.value = capabilities
  }

  /**
   * 제출 데이터 저장
   * @param {object} data - 제출 데이터 (userAnswer, sessionData)
   */
  function setPendingSubmission(data) {
    pendingSubmission.value = data
    console.log('[SessionStore] 제출 데이터 저장됨')
  }

  /**
   * 제출 데이터 초기화
   */
  function clearPendingSubmission() {
    pendingSubmission.value = null
    console.log('[SessionStore] 제출 데이터 초기화')
  }

  /**
   * 정답 결과 데이터 설정
   * @param {object} data - 정답 결과 데이터
   */
  function setCorrectAnswerData(data) {
    correctAnswerData.value = {
      problemTitle: data.problemTitle || '',
      sessionId: data.sessionId || '',
      score: data.score || 0,
      mathpixText: data.mathpixText || '',
      aiVerification: data.aiVerification || null
    }
    console.log('[SessionStore] 정답 결과 데이터 설정:', data)
  }

  /**
   * 정답 결과 데이터 초기화
   */
  function clearCorrectAnswerData() {
    correctAnswerData.value = {
      problemTitle: '',
      sessionId: '',
      score: 0,
      mathpixText: '',
      aiVerification: null
    }
  }

  /**
   * 전체 세션 초기화
   */
  function resetSession() {
    stopTimer()
    resetTimer()
    penCapabilities.value = null
    clearPendingSubmission()
    clearCorrectAnswerData()
    console.log('[SessionStore] 전체 세션 초기화 완료')
  }

  return {
    // State
    timerRunning,
    timerStartTime,
    timerElapsed,
    penCapabilities,
    pendingSubmission,
    correctAnswerData,
    // Computed
    hasTimer,
    hasPendingSubmission,
    // Actions
    startTimer,
    stopTimer,
    resetTimer,
    updatePenCapabilities,
    setPendingSubmission,
    clearPendingSubmission,
    setCorrectAnswerData,
    clearCorrectAnswerData,
    resetSession
  }
})
