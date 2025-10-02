<template>
  <div v-if="isOpen" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-container" @click.stop>
      <!-- 모달 헤더 -->
      <div class="modal-header">
        <h3>풀이 방식 확인</h3>
      </div>

      <!-- 모달 본문 -->
      <div class="modal-body">
        <p class="question-text">
          이 문제를 어떻게 풀이하셨나요?
        </p>
        <p class="description-text">
          정확한 학습 데이터 수집을 위해 정직하게 답변해주세요.
        </p>
      </div>

      <!-- 모달 버튼 -->
      <div class="modal-actions">
        <button
          class="btn btn-honest"
          @click="handleResponse(0)"
        >
          <span class="btn-icon">✍️</span>
          직접 풀었습니다
        </button>
        <button
          class="btn btn-cheating"
          @click="handleResponse(1)"
        >
          <span class="btn-icon">📱</span>
          참고자료를 사용했습니다
        </button>
      </div>

      <!-- 취소 버튼 -->
      <div class="modal-footer">
        <button class="btn-cancel" @click="handleCancel">
          취소
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'CheatingCheckModal',
  emits: ['response', 'cancel'],
  setup(props, { emit }) {
    // 모달 열림/닫힘 상태
    const isOpen = ref(false)

    /**
     * 모달 열기
     */
    const open = () => {
      isOpen.value = true
    }

    /**
     * 모달 닫기
     */
    const close = () => {
      isOpen.value = false
    }

    /**
     * 사용자 응답 처리
     * @param {number} label - 0: 정상 풀이, 1: 참고자료 사용 (치팅)
     */
    const handleResponse = (label) => {
      // 즉시 모달 닫기 (로딩 모달이 바로 보이도록)
      close()
      // 응답 이벤트 발생
      emit('response', label)
    }

    /**
     * 취소 버튼 클릭 처리
     */
    const handleCancel = () => {
      emit('cancel')
      close()
    }

    /**
     * 모달 배경 클릭 처리 (모달 외부 클릭 시 취소)
     */
    const handleOverlayClick = () => {
      handleCancel()
    }

    return {
      isOpen,
      open,
      close,
      handleResponse,
      handleCancel,
      handleOverlayClick
    }
  }
}
</script>

<style scoped>
/* 모달 오버레이 (배경) */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.15s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 모달 컨테이너 */
.modal-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  max-width: 480px;
  width: 90%;
  padding: 0;
  animation: slideUp 0.2s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* 모달 헤더 */
.modal-header {
  padding: 24px 24px 16px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
}

/* 모달 본문 */
.modal-body {
  padding: 24px;
}

.question-text {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin: 0 0 12px 0;
}

.description-text {
  font-size: 14px;
  color: #666;
  margin: 0;
  line-height: 1.5;
}

/* 모달 액션 버튼 영역 */
.modal-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 0 24px 16px 24px;
}

/* 공통 버튼 스타일 */
.btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 20px;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-icon {
  font-size: 20px;
}

/* 직접 풀이 버튼 (정상) */
.btn-honest {
  background: #4CAF50;
  color: white;
}

.btn-honest:hover {
  background: #45a049;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.btn-honest:active {
  transform: translateY(0);
}

/* 참고자료 사용 버튼 (치팅) */
.btn-cheating {
  background: #FF9800;
  color: white;
}

.btn-cheating:hover {
  background: #f57c00;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 152, 0, 0.3);
}

.btn-cheating:active {
  transform: translateY(0);
}

/* 모달 푸터 */
.modal-footer {
  padding: 12px 24px 24px 24px;
  display: flex;
  justify-content: center;
}

/* 취소 버튼 */
.btn-cancel {
  background: none;
  border: none;
  color: #999;
  font-size: 14px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.btn-cancel:hover {
  background: #f5f5f5;
  color: #666;
}
</style>
