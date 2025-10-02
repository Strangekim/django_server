<template>
  <div v-if="isOpen" class="loading-overlay">
    <div class="loading-container">
      <!-- 로딩 스피너 -->
      <div class="spinner-container">
        <div class="spinner"></div>
      </div>

      <!-- 로딩 메시지 -->
      <h3 class="loading-title">{{ title }}</h3>
      <p class="loading-message">{{ message }}</p>

      <!-- 진행 단계 표시 -->
      <div class="progress-steps">
        <div class="step" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">
          <div class="step-icon">✓</div>
          <div class="step-label">필기 분석 중</div>
        </div>
        <div class="step" :class="{ active: currentStep >= 2, completed: currentStep > 2 }">
          <div class="step-icon">✓</div>
          <div class="step-label">AI 검증 중</div>
        </div>
        <div class="step" :class="{ active: currentStep >= 3 }">
          <div class="step-icon">✓</div>
          <div class="step-label">결과 생성 중</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'LoadingModal',
  props: {
    isOpen: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: '답안 검증 중...'
    },
    message: {
      type: String,
      default: '잠시만 기다려주세요.'
    }
  },
  setup(props) {
    const currentStep = ref(0)
    let stepInterval = null

    // 로딩 상태가 열리면 단계별로 진행
    watch(() => props.isOpen, (isOpen) => {
      if (isOpen) {
        currentStep.value = 0
        // 단계별 진행 시뮬레이션
        stepInterval = setInterval(() => {
          if (currentStep.value < 3) {
            currentStep.value++
          }
        }, 2000) // 2초마다 다음 단계
      } else {
        // 닫힐 때 정리
        currentStep.value = 0
        if (stepInterval) {
          clearInterval(stepInterval)
          stepInterval = null
        }
      }
    })

    return {
      currentStep
    }
  }
}
</script>

<style scoped>
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 20000; /* 다른 모달보다 위에 */
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

.loading-container {
  background: white;
  border-radius: 20px;
  padding: 48px 40px;
  max-width: 500px;
  width: 90%;
  text-align: center;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.4s ease;
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

.spinner-container {
  margin-bottom: 24px;
}

.spinner {
  width: 60px;
  height: 60px;
  border: 4px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  margin: 0 auto;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-title {
  font-size: 22px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.loading-message {
  font-size: 15px;
  color: #6b7280;
  margin: 0 0 32px 0;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-top: 32px;
}

.step {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  opacity: 0.3;
  transition: all 0.4s ease;
}

.step.active {
  opacity: 1;
}

.step.completed {
  opacity: 0.6;
}

.step-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #e5e7eb;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
  transition: all 0.4s ease;
}

.step.active .step-icon {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  animation: pulse 1.5s ease infinite;
}

.step.completed .step-icon {
  background: #10b981;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 0 0 8px rgba(59, 130, 246, 0);
  }
}

.step-label {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  text-align: center;
}

.step.active .step-label {
  color: #3b82f6;
}

.step.completed .step-label {
  color: #10b981;
}

/* 반응형 */
@media (max-width: 640px) {
  .loading-container {
    padding: 36px 24px;
  }

  .loading-title {
    font-size: 20px;
  }

  .loading-message {
    font-size: 14px;
  }

  .progress-steps {
    gap: 8px;
  }

  .step-icon {
    width: 32px;
    height: 32px;
    font-size: 16px;
  }

  .step-label {
    font-size: 11px;
  }
}
</style>
