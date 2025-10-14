<template>
  <header class="header">
    <div class="header-left">
      <!-- 메뉴 버튼 -->
      <button
        class="menu-btn icon-btn"
        @click="toggleSidebar"
        aria-label="메뉴 열기/닫기"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M3 12H21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M3 6H21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M3 18H21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </button>
    </div>

    <div class="header-right">
      <!-- 타이머 -->
      <div v-if="timerRunning" class="timer-display">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="timer-icon">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
          <polyline points="12,6 12,12 16,14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span class="timer-text">{{ formattedTime }}</span>
      </div>
    </div>
  </header>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

export default {
  name: 'Header',
  props: {
    sidebarOpen: {
      type: Boolean,
      default: false
    },
    selectedGrade: {
      type: String,
      default: ''
    },
    selectedCategory: {
      type: String,
      default: ''
    },
    timerRunning: {
      type: Boolean,
      default: false
    },
    penCapabilities: {
      type: Object,
      default: null
    }
  },
  emits: ['update:sidebarOpen'],
  setup(props, { emit }) {
    // 타이머 상태
    const startTime = ref(null)
    const elapsedTime = ref(0)
    let intervalId = null

    // 타이머 시작
    const startTimer = () => {
      if (!intervalId) {
        startTime.value = Date.now() - elapsedTime.value
        intervalId = setInterval(() => {
          elapsedTime.value = Date.now() - startTime.value
        }, 100) // 100ms마다 업데이트
      }
    }

    // 타이머 정지
    const stopTimer = () => {
      if (intervalId) {
        clearInterval(intervalId)
        intervalId = null
      }
    }

    // 타이머 리셋
    const resetTimer = () => {
      stopTimer()
      elapsedTime.value = 0
      startTime.value = null
    }

    // 시간 포맷팅 (MM:SS)
    const formattedTime = computed(() => {
      const totalSeconds = Math.floor(elapsedTime.value / 1000)
      const minutes = Math.floor(totalSeconds / 60)
      const seconds = totalSeconds % 60
      return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
    })

    // 타이머 실행 상태 감시
    watch(() => props.timerRunning, (running) => {
      if (running) {
        resetTimer()
        startTimer()
      } else {
        stopTimer()
      }
    }, { immediate: true })

    // 사이드바 토글 함수
    const toggleSidebar = () => {
      emit('update:sidebarOpen', !props.sidebarOpen)
    }

    // 문제 새로고침 함수
    const refreshProblem = () => {
      // TODO: 백엔드 연결 시 새로운 문제를 요청하는 로직 구현
      console.log('새 문제 요청:', props.selectedGrade, props.selectedCategory)
    }

    // 컴포넌트 언마운트 시 타이머 정리
    onUnmounted(() => {
      stopTimer()
    })

    return {
      toggleSidebar,
      refreshProblem,
      formattedTime
    }
  }
}
</script>

<style scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0;
  height: 48px;
  background: var(--background-color);
  border-bottom: 1px solid var(--border-color);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  position: relative;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0;
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
}

.menu-btn {
  color: var(--text-primary);
  margin: 0;
  border-radius: 0;
  padding: 16px;
  width: auto;
  height: auto;
  box-shadow: none;
  border-right: 1px solid var(--border-color);
  transition: background-color 0.2s ease, transform 0.2s ease;
}

.menu-btn:hover {
  background-color: var(--background-color);
  transform: none;
  box-shadow: none;
}


.timer-display {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: 24px;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 14px;
  box-shadow: var(--shadow-sm);
}

.timer-icon {
  color: var(--text-secondary);
}

.timer-text {
  font-family: 'Courier New', monospace;
  letter-spacing: 1px;
}

/* 태블릿 가로뷰 중심 반응형 */
@media (min-width: 1024px) and (orientation: landscape) {
  .header-right {
    padding: 12px 20px;
  }

  .menu-btn {
    padding: 16px 20px;
  }
}

@media (min-width: 768px) and (max-width: 1023px) {
  .header-right {
    padding: 10px 16px;
  }

  .menu-btn {
    padding: 14px 16px;
  }
}

@media (max-width: 767px) {
  .header-right {
    padding: 8px 12px;
  }

  .menu-btn {
    padding: 12px;
  }
}
</style>