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
      />

      <!-- 가로뷰 콘텐츠 영역 -->
      <div class="content-area">
        <!-- 문제 영역 -->
        <div class="problem-section">
          <ProblemArea
            ref="problemArea"
            :problem="currentProblem"
            :selectedCategory="selectedCategory"
            :selectedQuestion="selectedQuestion"
            @openSidebar="sidebarOpen = true"
            @addImageToCanvas="handleAddImageToCanvas"
          />
        </div>

        <!-- 메모 및 정답 영역 -->
        <div class="memo-section">
          <!-- 메모 캔버스 -->
          <MemoCanvas ref="memoCanvas" />

          <!-- 정답란 -->
          <AnswerArea
            ref="answerArea"
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

    <!-- 정답 결과 모달 -->
    <CorrectAnswerModal
      :isOpen="correctAnswerModalOpen"
      :score="correctAnswerData.score"
      :mathpixText="correctAnswerData.mathpixText"
      :aiVerification="correctAnswerData.aiVerification"
      :additionalInfo="correctAnswerData.additionalInfo"
      @close="handleCorrectAnswerModalClose"
    />

    <!-- 로딩 모달 -->
    <LoadingModal
      :isOpen="isVerifying"
      title="답안 검증 중..."
      message="AI가 풀이를 분석하고 있습니다."
    />
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import Sidebar from './components/Sidebar.vue'
import Header from './components/Header.vue'
import ProblemArea from './components/ProblemArea.vue'
import MemoCanvas from './components/MemoCanvas.vue'
import AnswerArea from './components/AnswerArea.vue'
import CheatingCheckModal from './components/CheatingCheckModal.vue'
import CorrectAnswerModal from './components/CorrectAnswerModal.vue'
import LoadingModal from './components/LoadingModal.vue'
import { apiGet, apiPost, API_ENDPOINTS } from './api/config.js'

export default {
  name: 'App',
  components: {
    Sidebar,
    Header,
    ProblemArea,
    MemoCanvas,
    AnswerArea,
    LoadingModal,
    CheatingCheckModal,
    CorrectAnswerModal
  },
  setup() {
    // 사이드바 상태
    const sidebarOpen = ref(false)

    // 선택된 문제 정보
    const selectedCategory = ref('')
    const selectedQuestion = ref('')
    const currentProblem = ref(null)

    // 컴포넌트 참조
    const memoCanvas = ref(null)
    const problemArea = ref(null)
    const answerArea = ref(null)
    const cheatingModal = ref(null)

    // 타이머 상태
    const timerRunning = ref(false)

    // 로딩 상태
    const loadingProblem = ref(false)

    // 제출 대기 중인 데이터 (치팅 확인 후 사용)
    const pendingSubmission = ref(null)

    // 정답 결과 모달 상태
    const correctAnswerModalOpen = ref(false)
    const correctAnswerData = reactive({
      score: 0,
      mathpixText: '',
      aiVerification: null,
      additionalInfo: null
    })

    // 로딩 상태
    const isVerifying = ref(false)

    // API에서 문제 상세 정보 불러오기
    const fetchProblemDetail = async (questionId) => {
      loadingProblem.value = true

      try {
        const response = await apiGet(API_ENDPOINTS.QUESTION_DETAIL(questionId))

        if (response.success) {
          const data = response.data

          // API 응답을 ProblemArea가 기대하는 형식으로 변환
          currentProblem.value = {
            id: data.id,
            name: data.name,
            category: data.category.name,
            categoryId: data.category.id,
            difficulty: data.difficulty,
            difficulty_1_to_100: data.difficulty, // ProblemArea에서 사용
            problem_text: data.problem,
            choices: data.choices,
            description: data.description,
            image: data.separate_img,
            image_alt: `${data.name} 문제 이미지`
          }

          console.log('문제 상세 정보 로드 완료:', data.name)
        } else {
          throw new Error('API 응답 실패')
        }
      } catch (error) {
        console.error('문제 상세 정보 로드 실패:', error)
        alert('문제를 불러오는데 실패했습니다.')
      } finally {
        loadingProblem.value = false
      }
    }

    // 문제 선택 핸들러
    const handleProblemSelect = async (problemData) => {
      // 이미 문제가 선택되어 있고, 다른 문제를 선택하는 경우
      if (currentProblem.value && currentProblem.value.id !== problemData.questionId) {
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

      selectedCategory.value = problemData.categoryName
      selectedQuestion.value = problemData.questionName

      // API에서 문제 상세 정보 불러오기
      await fetchProblemDetail(problemData.questionId)

      sidebarOpen.value = false // 문제 선택 후 사이드바 닫기

      // 타이머 시작
      timerRunning.value = true

      console.log('문제 선택됨:', problemData)
    }

    // 세션 초기화 함수
    const resetSession = () => {
      // 1. 타이머 중지 및 초기화 (다음 문제 선택 시 다시 시작됨)
      timerRunning.value = false

      // 2. MemoCanvas의 세션 데이터 완전 초기화
      // - 캔버스 클리어
      // - strokes, events, statistics 모두 초기화
      // - 새로운 sessionId 생성
      // - 히스토리 초기화
      // - 오버레이 이미지 제거
      // - 줌/팬 초기화
      if (memoCanvas.value && memoCanvas.value.resetSessionData) {
        memoCanvas.value.resetSessionData()
      }

      // 3. ProblemArea의 답안 초기화는 새 문제 로드 시 자동으로 리셋됨
      // (selectedChoice와 subjectiveAnswer는 내부 ref이므로 새 문제가 로드되면 초기 상태가 됨)

      console.log('세션 초기화 완료')
    }

    // 이미지를 메모 캔버스에 추가하는 핸들러
    const handleAddImageToCanvas = (imageData) => {
      if (memoCanvas.value && memoCanvas.value.addOverlayImage) {
        memoCanvas.value.addOverlayImage(imageData)
      }
    }

    // 정답 제출 핸들러 (1단계: 데이터 검증 후 치팅 확인 모달 열기)
    const handleSubmitAnswer = async () => {
      // 1. 문제가 선택되지 않았으면 경고
      if (!currentProblem.value) {
        answerArea.value?.setSubmissionStatus('error', '문제를 먼저 선택해주세요.')
        return
      }

      // 2. 사용자 답안 가져오기
      const userAnswer = problemArea.value?.getUserAnswer()
      if (!userAnswer) {
        answerArea.value?.setSubmissionStatus('error', '답안을 입력해주세요.')
        return
      }

      // 3. 세션 데이터 가져오기 (전체 필기 기록 + 화면에 보이는 스트로크)
      const sessionData = memoCanvas.value?.getSubmissionData()
      if (!sessionData) {
        answerArea.value?.setSubmissionStatus('error', '세션 데이터를 가져올 수 없습니다.')
        return
      }

      // 4. 제출 데이터를 임시 저장
      pendingSubmission.value = {
        userAnswer,
        sessionData
      }

      // 5. 로딩 상태 즉시 시작 (사용자에게 즉각적인 피드백 제공)
      isVerifying.value = true
      answerArea.value?.setSubmissionStatus('info', '답안을 제출하는 중입니다...')

      // 6. 치팅 여부 확인 모달 열기
      cheatingModal.value?.open()
    }

    /**
     * 치팅 여부 확인 응답 처리
     * @param {number} label - 0: 정상 풀이, 1: 참고자료 사용 (치팅)
     */
    const handleCheatingResponse = async (label) => {
      // 대기 중인 제출 데이터가 없으면 무시
      if (!pendingSubmission.value) {
        console.error('제출 데이터가 없습니다.')
        return
      }

      const { userAnswer, sessionData } = pendingSubmission.value

      // 로딩 상태 메시지 업데이트 (이미 로딩 중이므로 메시지만 변경)
      answerArea.value?.setSubmissionStatus('info', 'AI가 답안을 검증하는 중입니다...')

      try {
        // API 요청 데이터 구성
        const requestData = {
          // 문제 메타데이터
          question_id: currentProblem.value.id,
          problem_name: currentProblem.value.name,
          category_id: currentProblem.value.categoryId,
          category_name: currentProblem.value.category,
          difficulty: currentProblem.value.difficulty,

          // 사용자 답안
          user_answer: userAnswer,

          // 전체 세션 데이터 (필기 기록, 이벤트, 통계 등)
          session_data: sessionData,

          // 치팅 여부 라벨 (0: 정상, 1: 치팅)
          label: label
        }

        console.log('제출 데이터:', requestData)

        // API 호출
        const response = await apiPost(API_ENDPOINTS.VERIFY_SOLUTION, requestData)

        // 응답 처리
        if (response.success) {
          const verification = response.data.verification

          // 정답 여부에 따라 메시지 표시
          if (verification.is_correct) {
            // 정답일 경우: 결과 모달 표시
            correctAnswerData.score = verification.total_score || 0
            correctAnswerData.mathpixText = response.data.mathpix_result || ''
            correctAnswerData.aiVerification = {
              is_correct: verification.is_correct,
              logic_score: verification.logic_score || 0,
              accuracy_score: verification.accuracy_score || 0,
              process_score: verification.process_score || 0,
              comment: verification.comment || '',
              detailed_feedback: verification.detailed_feedback || ''
            }
            correctAnswerData.additionalInfo = {
              session_id: response.data.session_id,
              s3_url: response.data.s3_url
            }

            // 모달 열기
            correctAnswerModalOpen.value = true

            // AnswerArea에도 성공 메시지 표시 (모달 닫을 때까지 유지)
            answerArea.value?.setSubmissionStatus(
              'success',
              `정답입니다! (${verification.total_score}점)`
            )
          } else {
            // 오답일 경우: 기존대로 상세 결과 표시
            answerArea.value?.setSubmissionStatus(
              'error',
              `오답입니다. (${verification.total_score}점)`
            )
            answerArea.value?.showVerificationResult(response.data)
          }

          console.log('검증 완료:', response.data)
        } else {
          throw new Error(response.error || 'API 응답 실패')
        }
      } catch (error) {
        console.error('제출 실패:', error)

        // 에러 메시지 상세화
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

        answerArea.value?.setSubmissionStatus('error', errorMessage)
      } finally {
        // 로딩 종료
        isVerifying.value = false
        // 제출 완료 후 임시 데이터 초기화
        pendingSubmission.value = null
      }
    }

    /**
     * 치팅 확인 취소 처리
     */
    const handleCheatingCancel = () => {
      // 로딩 상태 종료 (제출 취소)
      isVerifying.value = false

      // 임시 저장된 제출 데이터 삭제
      pendingSubmission.value = null

      // 사용자에게 취소 메시지 표시
      answerArea.value?.setSubmissionStatus('info', '제출이 취소되었습니다.')

      console.log('제출 취소됨')
    }

    /**
     * 정답 결과 모달 닫기 처리 (다음 문제로 이동)
     */
    const handleCorrectAnswerModalClose = () => {
      // 모달 닫기
      correctAnswerModalOpen.value = false

      // 페이지 새로고침으로 완전히 초기화 (모든 상태와 캔버스 리셋)
      window.location.reload()
    }

    return {
      sidebarOpen,
      selectedCategory,
      selectedQuestion,
      currentProblem,
      memoCanvas,
      problemArea,
      answerArea,
      cheatingModal,
      timerRunning,
      loadingProblem,
      pendingSubmission,
      correctAnswerModalOpen,
      correctAnswerData,
      handleProblemSelect,
      handleAddImageToCanvas,
      handleSubmitAnswer,
      handleCheatingResponse,
      handleCheatingCancel,
      handleCorrectAnswerModalClose
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
  flex: none;
}

.memo-section {
  flex: 1;
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
    flex: 3;
    display: flex;
    flex-direction: column;
    min-width: 0;
    border-right: 1px solid var(--border-color);
  }

  .memo-section {
    flex: 7;
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