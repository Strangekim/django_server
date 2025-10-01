<template>
  <!-- 사이드바 오버레이 (모바일) -->
  <div
    v-if="isOpen"
    class="sidebar-overlay"
    @click="closeSidebar"
  ></div>

  <!-- 사이드바 -->
  <div class="sidebar" :class="{ 'is-open': isOpen }">
    <div class="sidebar-header">
      <h2 class="sidebar-title">문제 선택</h2>
      <button
        class="close-btn icon-btn"
        @click="closeSidebar"
        aria-label="사이드바 닫기"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          <path d="M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </button>
    </div>

    <div class="sidebar-content">
      <!-- 로딩 상태 -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>문제 목록을 불러오는 중...</p>
      </div>

      <!-- 에러 상태 -->
      <div v-else-if="error" class="error-state">
        <p>{{ error }}</p>
        <button @click="fetchQuestions" class="retry-btn">다시 시도</button>
      </div>

      <!-- 카테고리별 메뉴 -->
      <div
        v-else
        v-for="category in categories"
        :key="category.category_id"
        class="category-section"
      >
        <button
          class="category-button"
          :class="{ 'expanded': expandedCategory === category.category_id }"
          @click="toggleCategory(category.category_id)"
        >
          <span class="category-title">{{ category.category_name }}</span>
          <div class="category-info">
            <span class="question-count">{{ category.question_count }}문제</span>
            <svg
              class="chevron-icon"
              :class="{ 'rotated': expandedCategory === category.category_id }"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </button>

        <!-- 문제 목록 -->
        <div
          class="question-list"
          :class="{ 'expanded': expandedCategory === category.category_id }"
        >
          <button
            v-for="question in category.questions"
            :key="question.id"
            class="question-button"
            @click="selectQuestion(category, question)"
          >
            <span class="question-name">{{ question.name }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { apiGet, API_ENDPOINTS } from '../api/config.js'

export default {
  name: 'Sidebar',
  props: {
    isOpen: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:isOpen', 'selectProblem'],
  setup(props, { emit }) {
    // 현재 펼쳐진 카테고리
    const expandedCategory = ref(null)

    // 카테고리 데이터 (API 응답 형식에 맞춤)
    const categories = ref([])

    // 로딩 상태
    const loading = ref(false)
    const error = ref(null)

    // API에서 문제 목록 불러오기
    const fetchQuestions = async () => {
      loading.value = true
      error.value = null

      try {
        const response = await apiGet(API_ENDPOINTS.QUESTIONS_LIST)

        if (response.success) {
          categories.value = response.data.categories
          console.log('문제 목록 로드 완료:', response.data.total_count, '개 문제')
        } else {
          throw new Error('API 응답 실패')
        }
      } catch (err) {
        console.error('문제 목록 로드 실패:', err)
        error.value = '문제 목록을 불러오는데 실패했습니다.'
      } finally {
        loading.value = false
      }
    }

    // 컴포넌트 마운트 시 문제 목록 불러오기
    onMounted(() => {
      fetchQuestions()
    })

    // 사이드바 닫기
    const closeSidebar = () => {
      emit('update:isOpen', false)
    }

    // 카테고리 펼치기/접기 토글
    const toggleCategory = (categoryId) => {
      expandedCategory.value = expandedCategory.value === categoryId ? null : categoryId
    }

    // 문제 선택
    const selectQuestion = (category, question) => {
      const problemData = {
        categoryId: category.category_id,
        categoryName: category.category_name,
        questionId: question.id,
        questionName: question.name
      }

      emit('selectProblem', problemData)
      console.log(`문제 선택: ${category.category_name} - ${question.name}`)
    }

    return {
      expandedCategory,
      categories,
      loading,
      error,
      closeSidebar,
      toggleCategory,
      selectQuestion,
      fetchQuestions
    }
  }
}
</script>

<style scoped>
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 200;
}

.sidebar {
  position: fixed;
  top: 0;
  left: -320px;
  width: 320px;
  height: 100vh;
  background: var(--surface-color);
  box-shadow: var(--shadow-lg);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 300;
  display: flex;
  flex-direction: column;
  will-change: transform;
}

.sidebar.is-open {
  transform: translateX(320px);
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
  background: var(--background-color);
}

.sidebar-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  color: var(--text-secondary);
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.category-section {
  border-bottom: 1px solid var(--border-color);
}

.category-button {
  width: 100%;
  padding: 14px 16px;
  border: none;
  background: none;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  transition: background-color 0.2s ease;
  font-size: 15px;
}

.category-button:hover {
  background-color: var(--background-color);
}

.category-button.expanded {
  background-color: var(--background-color);
}

.category-title {
  font-weight: 600;
  color: var(--text-primary);
  flex: 1;
  text-align: left;
}

.category-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.question-count {
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 500;
}

.chevron-icon {
  color: var(--text-secondary);
  transition: transform 0.2s ease;
}

.chevron-icon.rotated {
  transform: rotate(90deg);
}

.question-list {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease;
  background: var(--background-color);
}

.question-list.expanded {
  max-height: 600px;
}

.question-button {
  width: 100%;
  padding: 12px 24px 12px 32px;
  border: none;
  background: none;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: background-color 0.2s ease;
  font-size: 14px;
}

.question-button:hover {
  background-color: var(--surface-color);
}

.question-name {
  color: var(--text-primary);
  font-weight: 400;
  text-align: left;
}

/* 로딩 상태 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--text-secondary);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  font-size: 14px;
}

/* 에러 상태 */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--error-color, #ef4444);
}

.error-state p {
  font-size: 14px;
  margin-bottom: 16px;
  text-align: center;
}

.retry-btn {
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  background: var(--surface-color);
  color: var(--text-primary);
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.retry-btn:hover {
  background: var(--background-color);
  border-color: var(--primary-color);
}

/* 태블릿 가로뷰 중심 최적화 */
@media (min-width: 1024px) and (orientation: landscape) {
  .sidebar {
    width: 320px;
    left: -320px;
  }

  .sidebar.is-open {
    transform: translateX(320px);
  }

  .sidebar-title {
    font-size: 18px;
  }

  .category-button {
    padding: 14px 16px;
    font-size: 15px;
  }

  .question-button {
    padding: 12px 24px 12px 32px;
    font-size: 14px;
  }
}

@media (min-width: 768px) and (max-width: 1023px) {
  .sidebar {
    width: 300px;
    left: -300px;
  }

  .sidebar.is-open {
    transform: translateX(300px);
  }

  .sidebar-title {
    font-size: 17px;
  }

  .category-button {
    padding: 13px 15px;
    font-size: 14px;
  }

  .question-button {
    padding: 11px 22px 11px 30px;
    font-size: 13px;
  }
}

@media (max-width: 767px) {
  .sidebar {
    width: 280px;
    left: -280px;
  }

  .sidebar.is-open {
    transform: translateX(280px);
  }

  .sidebar-title {
    font-size: 16px;
  }

  .category-button {
    padding: 12px 14px;
    font-size: 14px;
  }

  .question-button {
    padding: 10px 20px 10px 28px;
    font-size: 13px;
  }
}
</style>