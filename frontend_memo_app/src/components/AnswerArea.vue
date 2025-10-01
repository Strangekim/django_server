<template>
  <div class="answer-area">
    <div class="answer-container">
      <!-- 제출 버튼 영역 -->
      <div class="submit-section">
        <div class="submit-info">
          <span class="submit-label">메모 영역의 정답 상자에 답안을 작성하고 제출하세요</span>
        </div>

        <button
          class="submit-btn btn btn-primary"
          @click="submitAnswer"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2"/>
          </svg>
          정답 제출
        </button>
      </div>

      <!-- 제출 상태 표시 -->
      <div v-if="submissionStatus" class="submission-status" :class="submissionStatus.type">
        <div class="status-content">
          <svg
            v-if="submissionStatus.type === 'success'"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2"/>
          </svg>

          <svg
            v-else-if="submissionStatus.type === 'error'"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/>
            <path d="M15 9L9 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M9 9L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>

          <svg
            v-else
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/>
            <path d="M12 7V13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M12 17H12.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>

          <span class="status-message">{{ submissionStatus.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'AnswerArea',
  emits: ['submitAnswer'],
  setup(props, { emit }) {
    // 제출 상태
    const submissionStatus = ref(null)

    // 검증 결과 상세 정보
    const verificationResult = ref(null)

    // 정답 제출 버튼 클릭
    const submitAnswer = () => {
      // App.vue의 handleSubmitAnswer로 이벤트 전달
      emit('submitAnswer')
    }

    // 제출 상태 설정 (외부에서 호출)
    const setSubmissionStatus = (type, message) => {
      submissionStatus.value = { type, message }

      // info 상태는 3초 후 자동 제거
      if (type === 'info') {
        setTimeout(() => {
          if (submissionStatus.value?.type === 'info') {
            submissionStatus.value = null
          }
        }, 3000)
      }
    }

    // 검증 결과 표시 (외부에서 호출)
    const showVerificationResult = (result) => {
      verificationResult.value = result
      console.log('검증 결과 수신:', result)
      // TODO: 상세 결과 모달이나 패널 표시
    }

    return {
      submissionStatus,
      verificationResult,
      submitAnswer,
      setSubmissionStatus,
      showVerificationResult
    }
  }
}
</script>

<style scoped>
.answer-area {
  background: var(--background-color);
  border-top: 1px solid var(--border-color);
  padding: 16px;
}

.answer-container {
  background: var(--surface-color);
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.submit-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: var(--background-color);
}

.submit-info {
  flex: 1;
}

.submit-label {
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
}

.submit-btn {
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  min-width: 140px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.submission-status {
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
}

.submission-status.success {
  background: #f0fdf4;
  color: #166534;
  border-top-color: #bbf7d0;
}

.submission-status.error {
  background: #fef2f2;
  color: #dc2626;
  border-top-color: #fecaca;
}

.submission-status.info {
  background: #eff6ff;
  color: #1d4ed8;
  border-top-color: #bfdbfe;
}

.status-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-message {
  font-size: 14px;
  font-weight: 500;
}

/* 가로뷰 최적화 */
@media (min-width: 1024px) and (orientation: landscape) {
  .answer-area {
    padding: 8px;
    border-top: 1px solid var(--border-color);
  }

  .submit-section {
    padding: 8px 12px;
    gap: 8px;
  }

  .submit-label {
    font-size: 12px;
  }

  .submit-btn {
    padding: 8px 16px;
    font-size: 13px;
    min-width: 100px;
  }

  .submission-status {
    padding: 8px 12px;
  }

  .status-message {
    font-size: 12px;
  }
}

/* 태블릿 반응형 */
@media (max-width: 767px) {
  .answer-area {
    padding: 12px;
  }

  .submit-section {
    flex-direction: column;
    gap: 12px;
    text-align: center;
    padding: 16px 12px;
  }

  .submit-label {
    font-size: 13px;
  }

  .submit-btn {
    padding: 12px 20px;
    font-size: 15px;
    min-width: 120px;
  }

  .status-message {
    font-size: 13px;
  }
}

@media (min-width: 768px) and (max-width: 1024px) {
  .submit-section {
    padding: 14px 16px;
  }

  .submit-label {
    font-size: 13px;
  }

  .submit-btn {
    padding: 10px 20px;
    font-size: 15px;
    min-width: 130px;
  }
}
</style>