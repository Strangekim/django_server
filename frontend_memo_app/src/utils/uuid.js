/**
 * UUID 생성 유틸리티
 * 브라우저 네이티브 API 사용, 폴백으로 간단한 UUID v4 구현
 */

/**
 * UUID v4 생성
 * @returns {string} UUID 문자열
 */
export function generateUUID() {
  // 브라우저가 crypto.randomUUID를 지원하는 경우 (최신 브라우저)
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID()
  }

  // 폴백: 간단한 UUID v4 생성 구현
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0
    const v = c === 'x' ? r : (r & 0x3 | 0x8)
    return v.toString(16)
  })
}
