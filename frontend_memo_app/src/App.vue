<template>
  <div class="app">
    <!-- 네비게이션 바 -->
    <Sidebar
      v-model:isOpen="sidebarOpen"
      @selectProblem="handleProblemSelect"
    />

    <!-- 메인 콘텐츠 영역 -->
    <div class="main-content" :class="{ 'sidebar-open': sidebarOpen }">
      <!-- 헤더 -->
      <Header
        v-model:sidebarOpen="sidebarOpen"
        :selectedCategory="selectedCategory"
        :selectedQuestion="selectedQuestion"
        :timerRunning="timerRunning"
        :penCapabilities="penCapabilities"
      />

      <!-- 가로뷰 콘텐츠 영역 -->
      <div class="content-area" ref="contentAreaRef">
        <!-- 문제 영역 -->
        <div class="problem-section" :style="{ flexBasis: problemWidthPercent }">
          <ProblemArea
            ref="problemArea"
            :problem="currentProblem"
            :selectedCategory="selectedCategory"
            :selectedQuestion="selectedQuestion"
            @openSidebar="sidebarOpen = true"
            @addImageToCanvas="handleAddImageToCanvas"
          />

          <!-- 리사이즈 핸들 -->
          <ResizeHandle
            :isResizing="isResizing"
            @resize-start="handleResizeStart"
          />
        </div>

        <!-- 메모 영역 -->
        <div class="memo-section" :style="{ flexBasis: memoWidthPercent }">
          <!-- 메모 캔버스 -->
          <MemoCanvas
            ref="memoCanvas"
            @submitAnswer="handleSubmitAnswer"
          />
        </div>
      </div>
    </div>

    <!-- 치팅 여부 확인 모달 -->
    <CheatingCheckModal
      ref="cheatingModal"
      @response="handleCheatingResponse"
      @cancel="handleCheatingCancel"
    />

    <!-- 정답 결과 모달 - 문제 제목과 세션 ID 추가 -->
    <CorrectAnswerModal
      :isOpen="correctAnswerModalOpen"
      :problemTitle="correctAnswerData.problemTitle"
      :sessionId="correctAnswerData.sessionId"
      :score="correctAnswerData.score"
      :mathpixText="correctAnswerData.mathpixText"
      :aiVerification="correctAnswerData.aiVerification"
      @close="handleCorrectAnswerModalClose"
    />

    <!-- 로딩 모달 -->
    <LoadingModal
      :isOpen="isVerifying"
      title="답안 검증 중..."
      message="AI가 풀이를 분석하고 있습니다."
    />

    <!-- 토스트 메시지 -->
    <Toast
      :messages="toastMessages"
      :type="toastType"
      :duration="3000"
    />
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import Sidebar from './components/Sidebar.vue'
import Header from './components/Header.vue'
import ProblemArea from './components/ProblemArea.vue'
import MemoCanvas from './components/MemoCanvas.vue'
import CheatingCheckModal from './components/CheatingCheckModal.vue'
import CorrectAnswerModal from './components/CorrectAnswerModal.vue'
import LoadingModal from './components/LoadingModal.vue'
import ResizeHandle from './components/ResizeHandle.vue'
import Toast from './components/Toast.vue'
import { apiPost, API_ENDPOINTS } from './api/config.js'

// Pinia stores
import { useProblemStore } from './stores/problemStore.js'
import { useSessionStore } from './stores/sessionStore.js'
import { useUIStore } from './stores/uiStore.js'

// Composables
import { useResizer } from './composables/useResizer.js'

export default {
  name: 'App',
  components: {
    Sidebar,
    Header,
    ProblemArea,
    MemoCanvas,
    LoadingModal,
    CheatingCheckModal,
    CorrectAnswerModal,
    ResizeHandle,
    Toast
  },
  setup() {
    // Pinia stores 사용
    const problemStore = useProblemStore()
    const sessionStore = useSessionStore()
    const uiStore = useUIStore()

    // 컴포넌트 참조
    const memoCanvas = ref(null)
    const problemArea = ref(null)
    const cheatingModal = ref(null)
    const contentAreaRef = ref(null)

    // 토스트 상태
    const toastMessages = ref([])
    const toastType = ref('info')

    // Resizer composable
    const {
      isResizing,
      problemWidth,
      problemWidthPercent,
      memoWidthPercent,
      startResize
    } = useResizer()

    // Computed - stores에서 가져오기
    const sidebarOpen = computed({
      get: () => uiStore.sidebarOpen,
      set: (value) => {
        if (value) uiStore.openSidebar()
        else uiStore.closeSidebar()
      }
    })
    const selectedCategory = computed(() => problemStore.selectedCategory)
    const selectedQuestion = computed(() => problemStore.selectedQuestion)
    const currentProblem = computed(() => problemStore.currentProblem)
    const timerRunning = computed(() => sessionStore.timerRunning)
    const penCapabilities = computed(() => sessionStore.penCapabilities)
    const correctAnswerModalOpen = computed(() => uiStore.correctAnswerModalOpen)
    const correctAnswerData = computed(() => sessionStore.correctAnswerData)
    const isVerifying = computed(() => uiStore.isVerifying)

    // 문제 선택 핸들러
    const handleProblemSelect = async (problemData) => {
      // 이미 문제가 선택되어 있고, 다른 문제를 선택하는 경우
      if (problemStore.currentProblem && problemStore.currentProblem.id !== problemData.questionId) {
        // 사용자 확인 alert
        const confirmed = window.confirm(
          '새로운 문제를 선택하면 현재 작성 중인 내용이 모두 삭제됩니다.\n계속하시겠습니까?'
        )

        if (!confirmed) {
          // 사용자가 취소를 선택한 경우 아무 동작도 하지 않음
          return
        }

        // 사용자가 확인을 선택한 경우 - 데이터 초기화
        resetSession()
      }

      // Store에 문제 선택 정보 저장
      problemStore.selectProblem(problemData)

      // API에서 문제 상세 정보 불러오기
      await problemStore.fetchProblemDetail(problemData.questionId)

      // 사이드바 닫기
      uiStore.closeSidebar()

      // 타이머 시작
      sessionStore.startTimer()

      console.log('[App] 문제 선택됨:', problemData)
    }

    // 세션 초기화 함수
    const resetSession = () => {
      // 1. Store의 세션 초기화
      sessionStore.resetSession()

      // 2. MemoCanvas의 세션 데이터 완전 초기화
      if (memoCanvas.value && memoCanvas.value.resetSessionData) {
        memoCanvas.value.resetSessionData()
      }

      console.log('[App] 세션 초기화 완료')
    }

    // 이미지를 메모 캔버스에 추가하는 핸들러
    const handleAddImageToCanvas = (imageData) => {
      if (memoCanvas.value && memoCanvas.value.addOverlayImage) {
        memoCanvas.value.addOverlayImage(imageData)
      }
    }

    // 토스트 표시 함수
    const showToast = (messages, type = 'info') => {
      toastMessages.value = Array.isArray(messages) ? messages : [messages]
      toastType.value = type

      // 3초 후 자동으로 메시지 제거
      setTimeout(() => {
        toastMessages.value = []
      }, 3000)
    }

    // 정답 제출 핸들러 (1단계: 데이터 검증 후 치팅 확인 모달 열기)
    const handleSubmitAnswer = async () => {
      // 1. 문제가 선택되지 않았으면 경고
      if (!problemStore.currentProblem) {
        showToast(['문제를 먼저 선택해주세요'], 'error')
        return
      }

      // 2. 사용자 답안 가져오기
      const userAnswer = problemArea.value?.getUserAnswer()
      if (!userAnswer) {
        showToast(['메모 영역의 정답 상자에 답안을 작성하고 제출하세요'], 'info')
        return
      }

      // 3. 세션 데이터 가져오기 (전체 필기 기록 + 화면에 보이는 스트로크)
      const sessionData = memoCanvas.value?.getSubmissionData()
      if (!sessionData) {
        showToast(['세션 데이터를 가져올 수 없습니다'], 'error')
        return
      }

      // 4. 제출 데이터를 Store에 임시 저장
      sessionStore.setPendingSubmission({
        userAnswer,
        sessionData
      })

      // 5. 치팅 여부 확인 모달 열기
      cheatingModal.value?.open()
    }

    /**
     * 치팅 여부 확인 응답 처리
     * @param {number} label - 0: 정상 풀이, 1: 참고자료 사용 (치팅)
     */
    const handleCheatingResponse = async (label) => {
      // Store에서 대기 중인 제출 데이터 가져오기
      if (!sessionStore.pendingSubmission) {
        console.error('[App] 제출 데이터가 없습니다.')
        return
      }

      const { userAnswer, sessionData } = sessionStore.pendingSubmission

      // 로딩 시작
      uiStore.startVerification()

      try {
        // API 요청 데이터 구성
        const requestData = {
          question_id: problemStore.currentProblem.id,
          problem_name: problemStore.currentProblem.name,
          category_id: problemStore.currentProblem.categoryId,
          category_name: problemStore.currentProblem.category,
          difficulty: problemStore.currentProblem.difficulty,
          user_answer: userAnswer,
          session_data: sessionData,
          label: label
        }

        console.log('[App] 제출 데이터:', requestData)

        // API 호출
        const response = await apiPost(API_ENDPOINTS.VERIFY_SOLUTION, requestData)

        // 응답 처리
        if (response.success) {
          const verification = response.data.verification
          const actualIsCorrect = response.data.is_correct

          if (actualIsCorrect) {
            // 정답일 경우: Store에 정답 결과 저장
            sessionStore.setCorrectAnswerData({
              problemTitle: problemStore.currentProblem?.name || '문제',
              sessionId: response.data.session_id || '',
              score: verification.total_score || 0,
              mathpixText: response.data.mathpix_result || '',
              aiVerification: {
                is_correct: verification.is_correct,
                logic_score: verification.logic_score || 0,
                accuracy_score: verification.accuracy_score || 0,
                process_score: verification.process_score || 0,
                comment: verification.comment || '',
                detailed_feedback: verification.detailed_feedback || ''
              }
            })

            // 모달 열기
            uiStore.showCorrectAnswerModal()
          } else {
            // 오답일 경우 - 토스트 메시지 표시
            showToast([`오답입니다. (${verification.total_score}점)`], 'error')
          }

          console.log('[App] 검증 완료:', response.data)
        } else {
          throw new Error(response.error || 'API 응답 실패')
        }
      } catch (error) {
        console.error('[App] 제출 실패:', error)

        let errorMessage = '제출 실패'
        if (error.message.includes('500')) {
          errorMessage = '서버 오류가 발생했습니다. 관리자에게 문의해주세요.'
        } else if (error.message.includes('404')) {
          errorMessage = '문제를 찾을 수 없습니다.'
        } else if (error.message.includes('400')) {
          errorMessage = '잘못된 요청입니다. 답안을 다시 확인해주세요.'
        } else if (error.message.includes('Network') || error.message.includes('Failed to fetch')) {
          errorMessage = '네트워크 연결을 확인해주세요.'
        } else {
          errorMessage = `제출 실패: ${error.message}`
        }

        showToast([errorMessage], 'error')
      } finally{
        uiStore.stopVerification()
        sessionStore.clearPendingSubmission()
      }
    }

    /**
     * 치팅 확인 취소 처리
     */
    const handleCheatingCancel = () => {
      sessionStore.clearPendingSubmission()
      showToast(['제출이 취소되었습니다'], 'info')
      console.log('[App] 제출 취소됨')
    }

    /**
     * 정답 결과 모달 닫기 처리 (다음 문제로 이동)
     */
    const handleCorrectAnswerModalClose = () => {
      uiStore.hideCorrectAnswerModal()
      window.location.reload()
    }

    /**
     * 리사이즈 핸들 드래그 시작
     */
    const handleResizeStart = (event) => {
      if (contentAreaRef.value) {
        startResize(event, contentAreaRef.value)
      }
    }

    /**
     * MemoCanvas가 마운트된 후 펜 능력 정보 가져오기
     */
    const updatePenCapabilities = () => {
      if (memoCanvas.value && memoCanvas.value.sessionData) {
        sessionStore.updatePenCapabilities(memoCanvas.value.sessionData.capabilities)
      }
    }

    // 컴포넌트 마운트 후 펜 능력 추적 시작
    onMounted(() => {
      updatePenCapabilities()
      const intervalId = setInterval(updatePenCapabilities, 1000)
      return () => clearInterval(intervalId)
    })

    return {
      sidebarOpen,
      selectedCategory,
      selectedQuestion,
      currentProblem,
      memoCanvas,
      problemArea,
      cheatingModal,
      contentAreaRef,
      timerRunning,
      penCapabilities,
      correctAnswerModalOpen,
      correctAnswerData,
      isVerifying,
      isResizing,
      problemWidthPercent,
      memoWidthPercent,
      toastMessages,
      toastType,
      handleProblemSelect,
      handleAddImageToCanvas,
      handleSubmitAnswer,
      handleCheatingResponse,
      handleCheatingCancel,
      handleCorrectAnswerModalClose,
      handleResizeStart
    }
  }
}
</script>

<style scoped>
.app {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  display: flex;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s ease;
  overflow: hidden;
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.problem-section {
  position: relative;
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.memo-section {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 태블릿 가로뷰 중심 최적화 */
@media (min-width: 1024px) and (orientation: landscape) {
  .main-content {
    margin-left: 0;
  }

  .app {
    height: 100vh;
    overflow: hidden;
  }

  .content-area {
    flex-direction: row;
  }

  .problem-section {
    flex: 0 0 auto;
    display: flex;
    flex-direction: column;
    min-width: 0;
    border-right: none;
  }

  .memo-section {
    flex: 1 1 auto;
    display: flex;
    flex-direction: column;
    min-width: 0;
  }
}

@media (min-width: 768px) and (max-width: 1023px) {
  .main-content {
    margin-left: 0;
  }
}

@media (max-width: 767px) {
  .main-content {
    width: 100%;
  }

  .app {
    height: 100vh;
    overflow: hidden;
  }
}
</style>