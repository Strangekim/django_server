/**
 * API 설정 파일
 * 백엔드 API 서버와의 통신을 위한 공통 설정
 */

// API 기본 URL
// 개발 환경: localhost, 프로덕션 환경: EC2 서버
export const API_BASE_URL = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : 'http://54.180.150.130'

// API 엔드포인트
export const API_ENDPOINTS = {
  // 헬스체크
  HEALTH: '/api/health/',

  // 문제 관련
  QUESTIONS_LIST: '/api/questions/',
  QUESTION_DETAIL: (id) => `/api/questions/${id}/`,

  // 문제 풀이 검증
  VERIFY_SOLUTION: '/api/verify-solution/'
}

// HTTP 요청 헬퍼 함수
export const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`

  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  }

  try {
    const response = await fetch(url, defaultOptions)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('API 요청 실패:', error)
    throw error
  }
}

// GET 요청
export const apiGet = (endpoint) => {
  return apiRequest(endpoint, { method: 'GET' })
}

// POST 요청
export const apiPost = (endpoint, body) => {
  return apiRequest(endpoint, {
    method: 'POST',
    body: JSON.stringify(body)
  })
}
