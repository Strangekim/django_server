<template>
  <div v-if="isOpen" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-container" @click.stop>
      <!-- 헤더 - 문제 제목, 점수, 세션 ID 표시 -->
      <div class="modal-header">
        <div class="success-icon">✓</div>
        <h2 class="modal-title">정답입니다!</h2>

        <!-- 문제 제목 표시 -->
        <p v-if="problemTitle" class="problem-title">{{ problemTitle }}</p>

        <!-- 점수 표시 -->
        <p class="score-text">{{ score }}점</p>

        <!-- 세션 ID 표시 -->
        <p v-if="sessionId" class="session-id">세션 ID: {{ sessionId }}</p>
      </div>

      <!-- 본문 -->
      <div class="modal-body">
        <!-- Mathpix 변환 결과 -->
        <div v-if="mathpixText" class="result-section">
          <h3 class="section-title">필기 인식 결과</h3>
          <div class="result-content mathpix-content">
            {{ mathpixText }}
          </div>
        </div>

        <!-- OpenAI 검증 결과 -->
        <div v-if="aiVerification" class="result-section">
          <h3 class="section-title">AI 풀이 검증</h3>
          <div class="result-content ai-content">
            <!-- 세부 점수 -->
            <div class="score-breakdown">
              <div class="score-item">
                <span class="score-label">논리력</span>
                <span class="score-value">{{ aiVerification.logic_score }}점</span>
              </div>
              <div class="score-item">
                <span class="score-label">정확성</span>
                <span class="score-value">{{ aiVerification.accuracy_score }}점</span>
              </div>
              <div class="score-item">
                <span class="score-label">풀이과정</span>
                <span class="score-value">{{ aiVerification.process_score }}점</span>
              </div>
            </div>

            <!-- 코멘트 -->
            <div v-if="aiVerification.comment" class="verification-item">
              <span class="label">📝 총평</span>
              <div class="comment">{{ aiVerification.comment }}</div>
            </div>

            <!-- 상세 피드백 -->
            <div v-if="aiVerification.detailed_feedback" class="verification-item">
              <span class="label">💡 상세 피드백</span>
              <div class="feedback">{{ aiVerification.detailed_feedback }}</div>
            </div>
          </div>
        </div>

        <!-- 추가 정보 섹션 삭제됨 (요청사항) -->
      </div>

      <!-- 하단 버튼 -->
      <div class="modal-footer">
        <button class="btn btn-primary" @click="handleClose">
          <span class="btn-icon">🎉</span>
          다음 문제로
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CorrectAnswerModal',
  props: {
    // 모달 열림/닫힘 상태
    isOpen: {
      type: Boolean,
      default: false
    },
    // 문제 제목 (새로 추가)
    problemTitle: {
      type: String,
      default: ''
    },
    // 세션 ID (새로 추가)
    sessionId: {
      type: String,
      default: ''
    },
    // 획득 점수
    score: {
      type: Number,
      default: 0
    },
    // Mathpix 필기 인식 결과
    mathpixText: {
      type: String,
      default: ''
    },
    // OpenAI 검증 결과
    aiVerification: {
      type: Object,
      default: null
    }
    // additionalInfo prop 삭제됨 (요청사항)
  },
  emits: ['close'],
  methods: {
    // 모달 닫기 이벤트 발생
    handleClose() {
      this.$emit('close')
    },
    // 오버레이 클릭 시 처리 (현재는 비활성화)
    handleOverlayClick() {
      // 오버레이 클릭 시 모달 닫기 (선택사항)
      // this.handleClose()
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 20px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 600px;
  width: 100%;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.4s ease;
  overflow: hidden;
}

@keyframes slideUp {
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  padding: 32px 24px;
  text-align: center;
  position: relative;
}

.success-icon {
  width: 64px;
  height: 64px;
  background: white;
  color: #10b981;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  font-weight: bold;
  margin: 0 auto 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  animation: bounce 0.6s ease;
}

@keyframes bounce {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.modal-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 12px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 문제 제목 스타일 (새로 추가) */
.problem-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 12px 0;
  opacity: 0.9;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  backdrop-filter: blur(10px);
}

.score-text {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 8px 0;
  opacity: 0.95;
}

/* 세션 ID 스타일 (새로 추가) */
.session-id {
  font-size: 13px;
  font-weight: 500;
  margin: 0;
  opacity: 0.8;
  font-family: 'Courier New', monospace;
  letter-spacing: 0.5px;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.result-section {
  margin-bottom: 24px;
}

.result-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title::before {
  content: '';
  width: 4px;
  height: 16px;
  background: #10b981;
  border-radius: 2px;
}

.result-content {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
}

.mathpix-content {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #1f2937;
  white-space: pre-wrap;
  word-break: break-word;
}

.ai-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.verification-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.verification-item .label {
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
}

.verification-item .value {
  font-size: 14px;
  color: #1f2937;
  font-weight: 500;
}

.verification-item .value.correct {
  color: #10b981;
  font-weight: 600;
}

/* 점수 분석 */
.score-breakdown {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.score-item {
  background: white;
  border: 2px solid #10b981;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.score-label {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
}

.score-value {
  font-size: 20px;
  font-weight: 700;
  color: #10b981;
}

.comment,
.feedback {
  font-size: 14px;
  line-height: 1.8;
  color: #374151;
  padding: 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
  white-space: pre-wrap;
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item {
  display: flex;
  gap: 8px;
  font-size: 14px;
}

.info-item .label {
  font-weight: 600;
  color: #6b7280;
  min-width: 100px;
}

.info-item .value {
  color: #1f2937;
  flex: 1;
  word-break: break-word;
}

.modal-footer {
  padding: 20px 24px;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.btn {
  width: 100%;
  padding: 14px 24px;
  font-size: 16px;
  font-weight: 600;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-primary:hover {
  background: linear-gradient(135deg, #059669, #047857);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
  transform: translateY(-1px);
}

.btn-primary:active {
  transform: translateY(0);
}

.btn-icon {
  font-size: 20px;
}

/* 스크롤바 스타일링 */
.modal-body::-webkit-scrollbar {
  width: 8px;
}

.modal-body::-webkit-scrollbar-track {
  background: transparent;
}

.modal-body::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 4px;
}

.modal-body::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

/* 반응형 */
@media (max-width: 640px) {
  .modal-container {
    max-height: 90vh;
  }

  .modal-header {
    padding: 24px 20px;
  }

  .success-icon {
    width: 56px;
    height: 56px;
    font-size: 32px;
  }

  .modal-title {
    font-size: 24px;
  }

  .score-text {
    font-size: 18px;
  }

  .modal-body {
    padding: 20px;
  }

  .section-title {
    font-size: 15px;
  }

  .result-content {
    padding: 12px;
  }
}
</style>
