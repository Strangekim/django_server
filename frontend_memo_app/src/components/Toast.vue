<template>
  <Transition name="toast-fade">
    <div v-if="visible" class="toast-container" :class="type">
      <div class="toast-content">
        <div class="toast-icon">
          <svg v-if="type === 'info'" width="24" height="24" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/>
            <path d="M12 7V13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M12 17H12.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="toast-messages">
          <div v-for="(msg, index) in messages" :key="index" class="toast-message">
            {{ msg }}
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  messages: {
    type: Array,
    default: () => []
  },
  type: {
    type: String,
    default: 'info',
    validator: (value) => ['info', 'success', 'error'].includes(value)
  },
  duration: {
    type: Number,
    default: 3000
  }
})

const visible = ref(false)
let timer = null

// messages가 변경될 때마다 토스트 표시
watch(() => props.messages, (newMessages) => {
  if (newMessages && newMessages.length > 0) {
    showToast()
  } else {
    hideToast()
  }
}, { immediate: true })

function showToast() {
  visible.value = true

  // 기존 타이머 제거
  if (timer) {
    clearTimeout(timer)
  }

  // duration 후 자동 숨김
  timer = setTimeout(() => {
    hideToast()
  }, props.duration)
}

function hideToast() {
  visible.value = false
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 9999;
  max-width: 80vw;
  min-width: 300px;
}

.toast-content {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  display: flex;
  gap: 16px;
  align-items: start;
  border: 2px solid #e5e7eb;
}

.toast-container.info .toast-content {
  border-color: #3b82f6;
  background: linear-gradient(135deg, #eff6ff, #dbeafe);
}

.toast-container.success .toast-content {
  border-color: #10b981;
  background: linear-gradient(135deg, #f0fdf4, #dcfce7);
}

.toast-container.error .toast-content {
  border-color: #ef4444;
  background: linear-gradient(135deg, #fef2f2, #fee2e2);
}

.toast-icon {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.toast-container.info .toast-icon {
  background: #3b82f6;
  color: white;
}

.toast-container.success .toast-icon {
  background: #10b981;
  color: white;
}

.toast-container.error .toast-icon {
  background: #ef4444;
  color: white;
}

.toast-messages {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.toast-message {
  font-size: 16px;
  font-weight: 500;
  line-height: 1.5;
}

.toast-container.info .toast-message {
  color: #1e40af;
}

.toast-container.success .toast-message {
  color: #065f46;
}

.toast-container.error .toast-message {
  color: #991b1b;
}

/* Transition */
.toast-fade-enter-active,
.toast-fade-leave-active {
  transition: all 0.3s ease;
}

.toast-fade-enter-from {
  opacity: 0;
  transform: translate(-50%, -60%);
}

.toast-fade-leave-to {
  opacity: 0;
  transform: translate(-50%, -40%);
}

/* 반응형 */
@media (max-width: 767px) {
  .toast-container {
    min-width: 260px;
    max-width: 90vw;
  }

  .toast-content {
    padding: 20px;
    gap: 12px;
  }

  .toast-icon {
    width: 28px;
    height: 28px;
  }

  .toast-message {
    font-size: 14px;
  }
}
</style>
