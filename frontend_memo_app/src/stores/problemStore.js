/**
 * 문제 상태 관리 Store
 * 현재 문제, 카테고리, 문제 목록 등 문제 관련 상태 관리
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiGet, API_ENDPOINTS } from '../api/config.js'

export const useProblemStore = defineStore('problem', () => {
  // 현재 선택된 문제 정보
  const currentProblem = ref(null)
  const selectedCategory = ref('')
  const selectedQuestion = ref('')

  // 문제 목록 (사이드바용)
  const categories = ref([])

  // 로딩 상태
  const loading = ref(false)
  const error = ref(null)

  // Computed
  const hasProblem = computed(() => currentProblem.value !== null)
  const problemId = computed(() => currentProblem.value?.id || null)

  // Actions
  /**
   * 문제 목록 불러오기 (API 호출)
   */
  async function fetchCategories() {
    loading.value = true
    error.value = null

    try {
      const response = await apiGet(API_ENDPOINTS.QUESTIONS_LIST)

      if (response.success) {
        categories.value = response.data.categories
        console.log('[ProblemStore] 문제 목록 로드 완료:', response.data.total_count, '개 문제')
        return true
      } else {
        throw new Error('API 응답 실패')
      }
    } catch (err) {
      console.error('[ProblemStore] 문제 목록 로드 실패:', err)
      error.value = '문제 목록을 불러오는데 실패했습니다.'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 문제 상세 정보 불러오기 (API 호출)
   * @param {number} questionId - 문제 ID
   */
  async function fetchProblemDetail(questionId) {
    loading.value = true
    error.value = null

    try {
      const response = await apiGet(API_ENDPOINTS.QUESTION_DETAIL(questionId))

      if (response.success) {
        const data = response.data

        // API 응답을 ProblemArea가 기대하는 형식으로 변환
        currentProblem.value = {
          id: data.id,
          name: data.name,
          category: data.category.name,
          categoryId: data.category.id,
          difficulty: data.difficulty,
          difficulty_1_to_100: data.difficulty, // ProblemArea에서 사용
          problem_text: data.problem,
          choices: data.choices,
          description: data.description,
          image: data.separate_img,
          image_alt: `${data.name} 문제 이미지`
        }

        console.log('[ProblemStore] 문제 상세 정보 로드 완료:', data.name)
        return true
      } else {
        throw new Error('API 응답 실패')
      }
    } catch (err) {
      console.error('[ProblemStore] 문제 상세 정보 로드 실패:', err)
      error.value = '문제를 불러오는데 실패했습니다.'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 문제 선택
   * @param {object} problemData - 문제 선택 데이터 (categoryId, categoryName, questionId, questionName)
   */
  function selectProblem(problemData) {
    selectedCategory.value = problemData.categoryName
    selectedQuestion.value = problemData.questionName
    console.log('[ProblemStore] 문제 선택됨:', problemData)
  }

  /**
   * 현재 문제 초기화
   */
  function resetProblem() {
    currentProblem.value = null
    selectedCategory.value = ''
    selectedQuestion.value = ''
    console.log('[ProblemStore] 문제 초기화 완료')
  }

  return {
    // State
    currentProblem,
    selectedCategory,
    selectedQuestion,
    categories,
    loading,
    error,
    // Computed
    hasProblem,
    problemId,
    // Actions
    fetchCategories,
    fetchProblemDetail,
    selectProblem,
    resetProblem
  }
})
