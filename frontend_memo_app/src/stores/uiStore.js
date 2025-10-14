/**
 * UI 상태 관리 Store
 * 사이드바, 모달, 로딩 상태 등 UI 관련 상태 관리
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUIStore = defineStore('ui', () => {
  // 사이드바 상태
  const sidebarOpen = ref(false)

  // 모달 상태
  const correctAnswerModalOpen = ref(false)
  const loadingModalOpen = ref(false)

  // 로딩 상태
  const isVerifying = ref(false)
  const loadingProblem = ref(false)

  // Actions
  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value
  }

  function openSidebar() {
    sidebarOpen.value = true
  }

  function closeSidebar() {
    sidebarOpen.value = false
  }

  function showCorrectAnswerModal() {
    correctAnswerModalOpen.value = true
  }

  function hideCorrectAnswerModal() {
    correctAnswerModalOpen.value = false
  }

  function startVerification() {
    isVerifying.value = true
  }

  function stopVerification() {
    isVerifying.value = false
  }

  function startLoadingProblem() {
    loadingProblem.value = true
  }

  function stopLoadingProblem() {
    loadingProblem.value = false
  }

  return {
    // State
    sidebarOpen,
    correctAnswerModalOpen,
    loadingModalOpen,
    isVerifying,
    loadingProblem,
    // Actions
    toggleSidebar,
    openSidebar,
    closeSidebar,
    showCorrectAnswerModal,
    hideCorrectAnswerModal,
    startVerification,
    stopVerification,
    startLoadingProblem,
    stopLoadingProblem
  }
})
