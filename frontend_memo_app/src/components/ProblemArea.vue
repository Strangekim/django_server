<template>
  <div class="problem-area">
    <!-- 문제 표시 영역 -->
    <div class="problem-container">
      <div v-if="problem" class="problem-content">
        <!-- 문제 헤더 -->
        <div class="problem-header">
          <div class="problem-meta">
            <span class="problem-badge">문제</span>
            <span class="problem-grade">{{ selectedGrade }}</span>
            <span class="problem-category">{{ selectedCategory }}</span>
          </div>
          <div class="problem-difficulty">
            <DifficultyBadge :difficulty="problem.difficulty_1_to_100" />
          </div>
        </div>

        <!-- 문제 카테고리 태그 -->
        <div class="problem-tags">
          <span class="category-tag">{{ problem.category }}</span>
        </div>

        <!-- 문제 텍스트 (MathJax로 수식 렌더링) -->
        <div class="problem-text">
          <MathContent :content="problem.problem_text" />
        </div>

        <!-- 문제 이미지 -->
        <div v-if="problem.image" class="problem-image">
          <img
            :src="problem.image"
            :alt="problem.image_alt || '문제 이미지'"
            class="problem-diagram"
            @click="addImageToCanvas"
          />
          <p class="image-hint">이미지를 클릭하면 메모 영역에 표시됩니다</p>
        </div>

        <!-- 객관식 보기 -->
        <div v-if="problem.choices && problem.choices.length > 0" class="choices-container">
          <h4 class="choices-title">보기</h4>
          <div class="choices-list">
            <div
              v-for="(choice, index) in problem.choices"
              :key="index"
              class="choice-item"
              :class="{ selected: selectedChoice === index }"
              @click="selectChoice(index)"
            >
              <div class="choice-number">{{ getChoiceLabel(index) }}</div>
              <!-- 객관식 보기도 MathJax로 렌더링 -->
              <div class="choice-text">
                <MathContent :content="choice" />
              </div>
            </div>
          </div>
        </div>

        <!-- 주관식 정답 입력 -->
        <div v-else class="subjective-answer-container">
          <h4 class="answer-title">정답 입력</h4>
          <div class="answer-input-wrapper" @click="showKeyboard = true">
            <input
              type="text"
              v-model="subjectiveAnswer"
              readonly
              class="answer-input"
              placeholder="여기를 터치하여 정답을 입력하세요"
            />
            <div class="keyboard-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="2" y="6" width="20" height="12" rx="2" stroke="currentColor" stroke-width="2"/>
                <path d="M6 10H6.01M10 10H10.01M14 10H14.01M18 10H18.01M6 14H18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- 문제가 선택되지 않았을 때는 빈 영역 -->
      <div v-else class="problem-placeholder"></div>
    </div>

    <!-- 가상 키보드 -->
    <NumericKeyboard
      v-model="subjectiveAnswer"
      :show="showKeyboard"
      @close="showKeyboard = false"
      @submit="submitAnswer"
    />
  </div>
</template>

<script>
import { ref } from 'vue'
import DifficultyBadge from './DifficultyBadge.vue'
import NumericKeyboard from './NumericKeyboard.vue'
// MathJax 수식 렌더링 컴포넌트 import
import MathContent from './MathContent.vue'

export default {
  name: 'ProblemArea',
  components: {
    DifficultyBadge,
    NumericKeyboard,
    MathContent  // MathContent 컴포넌트 등록
  },
  props: {
    problem: {
      type: Object,
      default: null
    },
    selectedGrade: {
      type: String,
      default: ''
    },
    selectedCategory: {
      type: String,
      default: ''
    }
  },
  emits: ['openSidebar', 'addImageToCanvas'],
  setup(props, { emit }) {
    // 선택된 보기
    const selectedChoice = ref(null)

    // 주관식 답안
    const subjectiveAnswer = ref('')

    // 키보드 표시 여부
    const showKeyboard = ref(false)

    // 사이드바 열기 함수
    const openSidebar = () => {
      emit('openSidebar')
    }

    // 보기 선택 함수
    const selectChoice = (index) => {
      selectedChoice.value = index
      console.log(`선택된 보기: ${getChoiceLabel(index)} - ${props.problem.choices[index]}`)
    }

    // 보기 라벨 생성 (①, ②, ③, ④, ⑤)
    const getChoiceLabel = (index) => {
      const labels = ['①', '②', '③', '④', '⑤']
      return labels[index] || `${index + 1}`
    }

    // 주관식 답안 제출
    const submitAnswer = (answer) => {
      console.log('제출된 답안:', answer)
      // TODO: API로 답안 전송
    }

    // 이미지를 메모 캔버스에 추가
    const addImageToCanvas = () => {
      if (props.problem && props.problem.image) {
        const imageData = {
          src: props.problem.image,
          alt: props.problem.image_alt || '문제 이미지'
        }
        emit('addImageToCanvas', imageData)
        console.log('이미지를 메모 캔버스에 추가:', imageData)
      }
    }

    // 사용자가 입력한 답안 반환 (외부에서 접근용)
    const getUserAnswer = () => {
      // 객관식인 경우 (choices가 있고 선택된 보기가 있음)
      if (props.problem && props.problem.choices && props.problem.choices.length > 0) {
        if (selectedChoice.value !== null) {
          return {
            type: 'multiple_choice',
            selectedIndex: selectedChoice.value,
            selectedValue: props.problem.choices[selectedChoice.value]
          }
        }
        return null // 아직 선택 안 함
      }

      // 주관식인 경우
      if (subjectiveAnswer.value) {
        return {
          type: 'subjective',
          answer: subjectiveAnswer.value
        }
      }

      return null // 답안 없음
    }

    return {
      selectedChoice,
      subjectiveAnswer,
      showKeyboard,
      openSidebar,
      selectChoice,
      getChoiceLabel,
      submitAnswer,
      addImageToCanvas,
      getUserAnswer
    }
  }
}
</script>

<style scoped>
.problem-area {
  background: var(--background-color);
  border-bottom: 1px solid var(--border-color);
  min-height: 200px;
  max-height: 400px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.problem-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.problem-content {
  padding: 20px;
  background: var(--surface-color);
  margin: 16px;
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  flex: 1;
  overflow-y: auto;
}

.problem-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.problem-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.problem-badge {
  background: var(--primary-color);
  color: white;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.problem-grade {
  background: rgba(217, 119, 6, 0.1);
  color: var(--primary-color);
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.problem-category {
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
}

.problem-difficulty {
  display: flex;
  align-items: center;
}

.problem-tags {
  margin-bottom: 16px;
}

.category-tag {
  background: linear-gradient(135deg, #fed7aa, #fdba74);
  color: #92400e;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(217, 119, 6, 0.2);
}

.problem-text {
  font-size: 17px;
  line-height: 1.7;
  color: var(--text-primary);
  margin-bottom: 20px;
  padding: 16px;
  background: rgba(254, 247, 237, 0.5);
  border-radius: 8px;
  border-left: 4px solid var(--primary-color);
  font-weight: 500;
}

.problem-image {
  margin-bottom: 24px;
  text-align: center;
  padding: 16px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.problem-diagram {
  max-width: 100%;
  height: auto;
  max-height: 200px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.problem-diagram:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 16px rgba(217, 119, 6, 0.3);
  border: 2px solid var(--primary-color);
}

.image-hint {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 8px;
  opacity: 0.8;
  font-style: italic;
}

.choices-container {
  margin-top: 20px;
}

.choices-title {
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.choices-title::before {
  content: '';
  width: 4px;
  height: 16px;
  background: var(--primary-color);
  border-radius: 2px;
}

.choices-list {
  display: grid;
  gap: 8px;
}

.choice-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.8);
  border: 2px solid var(--border-color);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.choice-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 0;
  height: 100%;
  background: linear-gradient(135deg, rgba(217, 119, 6, 0.1), rgba(234, 88, 12, 0.1));
  transition: width 0.3s ease;
}

.choice-item:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 8px rgba(217, 119, 6, 0.15);
  transform: translateY(-1px);
}

.choice-item:hover::before {
  width: 100%;
}

.choice-item.selected {
  border-color: var(--primary-color);
  background: linear-gradient(135deg, rgba(217, 119, 6, 0.1), rgba(234, 88, 12, 0.05));
  box-shadow: 0 4px 12px rgba(217, 119, 6, 0.25);
}

.choice-item.selected::before {
  width: 100%;
}

.choice-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--primary-color), #ea580c);
  color: white;
  border-radius: 50%;
  font-size: 16px;
  font-weight: 600;
  flex-shrink: 0;
  position: relative;
  z-index: 2;
}

.choice-item.selected .choice-number {
  background: linear-gradient(135deg, #059669, #10b981);
  box-shadow: 0 2px 6px rgba(5, 150, 105, 0.4);
}

.choice-text {
  flex: 1;
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
  position: relative;
  z-index: 2;
}

/* 주관식 답안 입력 */
.subjective-answer-container {
  margin-top: 20px;
}

.answer-title {
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.answer-title::before {
  content: '';
  width: 4px;
  height: 16px;
  background: var(--primary-color);
  border-radius: 2px;
}

.answer-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  cursor: pointer;
}

.answer-input {
  width: 100%;
  padding: 16px 50px 16px 20px;
  font-size: 18px;
  font-weight: 600;
  border: 2px solid var(--border-color);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.9);
  color: var(--text-primary);
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.answer-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 4px rgba(217, 119, 6, 0.1);
}

.answer-input::placeholder {
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 14px;
}

.keyboard-icon {
  position: absolute;
  right: 16px;
  color: var(--text-secondary);
  pointer-events: none;
  transition: color 0.2s ease;
}

.answer-input-wrapper:hover .answer-input {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(217, 119, 6, 0.15);
}

.answer-input-wrapper:hover .keyboard-icon {
  color: var(--primary-color);
}

.problem-placeholder {
  height: 100%;
}

/* 태블릿 가로뷰 중심 반응형 */
@media (min-width: 1024px) and (orientation: landscape) {
  .problem-area {
    min-height: auto;
    max-height: none;
    height: 100%;
    border-bottom: none;
    border-right: 1px solid var(--border-color);
  }

  .problem-container {
    height: 100%;
    max-height: 100%;
  }

  .problem-content {
    padding: 16px;
    margin: 12px;
    height: calc(100% - 24px);
    max-height: none;
  }

  .problem-text {
    font-size: 16px;
    padding: 16px;
  }

  .choices-list {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .choice-item {
    padding: 10px 14px;
  }

  .choice-text {
    font-size: 14px;
  }
}

@media (min-width: 768px) and (max-width: 1023px) {
  .problem-area {
    min-height: 180px;
    max-height: 380px;
  }

  .problem-content {
    padding: 20px;
    margin: 16px;
  }

  .problem-text {
    font-size: 16px;
    padding: 16px;
  }

  .choices-list {
    gap: 10px;
  }

  .choice-item {
    padding: 12px 16px;
  }

  .choice-text {
    font-size: 15px;
  }
}

@media (max-width: 767px) {
  .problem-area {
    min-height: 160px;
    max-height: 320px;
  }

  .problem-content {
    padding: 16px;
    margin: 12px;
  }

  .problem-text {
    font-size: 15px;
    padding: 12px;
  }

  .choices-list {
    gap: 8px;
  }

  .choice-item {
    padding: 10px 14px;
  }

  .choice-number {
    width: 28px;
    height: 28px;
    font-size: 14px;
  }

  .choice-text {
    font-size: 14px;
  }
}

/* 스크롤바 스타일링 */
.problem-content::-webkit-scrollbar {
  width: 6px;
}

.problem-content::-webkit-scrollbar-track {
  background: transparent;
}

.problem-content::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
}

.problem-content::-webkit-scrollbar-thumb:hover {
  background: var(--secondary-color);
}
</style>