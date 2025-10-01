<template>
  <div v-if="isOpen" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-container" @click.stop>
      <!-- 헤더 -->
      <div class="modal-header">
        <div class="success-icon">✓</div>
        <h2 class="modal-title">정답입니다!</h2>
        <p class="score-text">{{ score }}점</p>
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
            <div class="verification-item">
              <span class="label">정답 여부:</span>
              <span class="value" :class="{ correct: aiVerification.is_correct }">
                {{ aiVerification.is_correct ? '정답' : '오답' }}
              </span>
            </div>
            <div v-if="aiVerification.explanation" class="verification-item">
              <span class="label">설명:</span>
              <div class="explanation">{{ aiVerification.explanation }}</div>
            </div>
            <div v-if="aiVerification.feedback" class="verification-item">
              <span class="label">피드백:</span>
              <div class="feedback">{{ aiVerification.feedback }}</div>
            </div>
          </div>
        </div>

        <!-- 추가 정보 -->
        <div v-if="additionalInfo" class="result-section">
          <h3 class="section-title">추가 정보</h3>
          <div class="result-content info-content">
            <div v-for="(value, key) in additionalInfo" :key="key" class="info-item">
              <span class="label">{{ formatKey(key) }}:</span>
              <span class="value">{{ formatValue(value) }}</span>
            </div>
          </div>
        </div>
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
    isOpen: {
      type: Boolean,
      default: false
    },
    score: {
      type: Number,
      default: 0
    },
    mathpixText: {
      type: String,
      default: ''
    },
    aiVerification: {
      type: Object,
      default: null
    },
    additionalInfo: {
      type: Object,
      default: null
    }
  },
  emits: ['close'],
  methods: {
    handleClose() {
      this.$emit('close')
    },
    handleOverlayClick() {
      // 오버레이 클릭 시 모달 닫기 (선택사항)
      // this.handleClose()
    },
    formatKey(key) {
      // 키 이름을 사람이 읽기 쉽게 변환
      const keyMap = {
        total_score: '총점',
        step_scores: '단계별 점수',
        reasoning: '추론 과정',
        confidence: '신뢰도'
      }
      return keyMap[key] || key
    },
    formatValue(value) {
      if (typeof value === 'object') {
        return JSON.stringify(value, null, 2)
      }
      return value
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
  margin: 0 0 8px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.score-text {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  opacity: 0.95;
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

.explanation,
.feedback {
  font-size: 14px;
  line-height: 1.6;
  color: #374151;
  padding: 8px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
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
