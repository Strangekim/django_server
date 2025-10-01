<template>
  <div v-if="show" class="keyboard-overlay" @click="$emit('close')">
    <div class="keyboard-container" @click.stop>
      <div class="keyboard-header">
        <h3 class="keyboard-title">정답 입력</h3>
        <button class="close-btn" @click="$emit('close')" aria-label="닫기">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
      </div>

      <div class="display-area">
        <input
          ref="answerInput"
          type="text"
          :value="modelValue"
          readonly
          class="answer-display"
          placeholder="숫자를 입력하세요"
        />
      </div>

      <div class="keyboard-grid">
        <button
          v-for="key in keys"
          :key="key"
          class="key-btn"
          :class="{ 'special': ['←', '확인'].includes(key) }"
          @click="handleKeyPress(key)"
        >
          {{ key === '←' ? '←' : key }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'NumericKeyboard',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    modelValue: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue', 'close', 'submit'],
  setup(props, { emit }) {
    const answerInput = ref(null)

    const keys = [
      '7', '8', '9',
      '4', '5', '6',
      '1', '2', '3',
      '.', '0', '←',
      '확인'
    ]

    const handleKeyPress = (key) => {
      let newValue = props.modelValue

      if (key === '←') {
        // 백스페이스
        newValue = newValue.slice(0, -1)
      } else if (key === '확인') {
        // 확인 버튼
        emit('submit', props.modelValue)
        emit('close')
      } else if (key === '.') {
        // 소수점 - 이미 있으면 추가 안함
        if (!newValue.includes('.')) {
          newValue += key
        }
      } else {
        // 숫자
        newValue += key
      }

      emit('update:modelValue', newValue)
    }

    // 키보드가 열릴 때 포커스
    watch(() => props.show, (newVal) => {
      if (newVal && answerInput.value) {
        answerInput.value.focus()
      }
    })

    return {
      answerInput,
      keys,
      handleKeyPress
    }
  }
}
</script>

<style scoped>
.keyboard-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.keyboard-container {
  width: 100%;
  max-width: 500px;
  background: var(--surface-color);
  border-radius: 16px 16px 0 0;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.15);
  padding: 20px;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

.keyboard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.keyboard-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: color 0.2s ease;
}

.close-btn:hover {
  color: var(--text-primary);
}

.display-area {
  margin-bottom: 16px;
}

.answer-display {
  width: 100%;
  padding: 16px;
  font-size: 24px;
  font-weight: 600;
  text-align: center;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  background: var(--background-color);
  color: var(--text-primary);
  outline: none;
  caret-color: var(--primary-color);
}

.answer-display:focus {
  border-color: var(--primary-color);
}

.keyboard-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.key-btn {
  padding: 20px;
  font-size: 20px;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  background: var(--background-color);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  -webkit-tap-highlight-color: transparent;
}

.key-btn:hover {
  background: var(--border-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.key-btn:active {
  transform: translateY(0);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.key-btn.special {
  background: var(--primary-color);
  color: white;
}

.key-btn.special:hover {
  background: #1e40af;
}

.key-btn:nth-last-child(1) {
  grid-column: span 3;
}

/* 태블릿 최적화 */
@media (min-width: 768px) {
  .keyboard-container {
    max-width: 600px;
    padding: 24px;
  }

  .keyboard-title {
    font-size: 20px;
  }

  .answer-display {
    font-size: 28px;
    padding: 18px;
  }

  .key-btn {
    padding: 24px;
    font-size: 22px;
  }
}

/* 모바일 최적화 */
@media (max-width: 767px) {
  .keyboard-container {
    padding: 16px;
  }

  .keyboard-title {
    font-size: 16px;
  }

  .answer-display {
    font-size: 20px;
    padding: 14px;
  }

  .key-btn {
    padding: 16px;
    font-size: 18px;
  }
}
</style>
