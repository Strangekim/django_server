/**
 * 터치 제스처 관련 유틸리티 함수
 */

/**
 * 두 터치 포인트 간의 거리 계산
 * @param {TouchList} touches - 터치 리스트
 * @returns {number} 두 터치 간의 거리
 */
export function getTouchDistance(touches) {
  if (touches.length < 2) return 0

  const dx = touches[0].clientX - touches[1].clientX
  const dy = touches[0].clientY - touches[1].clientY
  return Math.sqrt(dx * dx + dy * dy)
}

/**
 * 두 터치 포인트의 중심점 계산
 * @param {TouchList} touches - 터치 리스트
 * @returns {{x: number, y: number}} 중심점 좌표
 */
export function getTouchCenter(touches) {
  if (touches.length === 0) return { x: 0, y: 0 }
  if (touches.length === 1) {
    return {
      x: touches[0].clientX,
      y: touches[0].clientY
    }
  }

  return {
    x: (touches[0].clientX + touches[1].clientX) / 2,
    y: (touches[0].clientY + touches[1].clientY) / 2
  }
}

/**
 * 핀치 제스처 감지
 * @param {number} currentDistance - 현재 터치 거리
 * @param {number} previousDistance - 이전 터치 거리
 * @param {number} threshold - 최소 변화 임계값
 * @returns {boolean} 핀치 제스처 여부
 */
export function detectPinchGesture(currentDistance, previousDistance, threshold = 10) {
  const diff = Math.abs(currentDistance - previousDistance)
  return diff > threshold
}

/**
 * 터치 이벤트에서 좌표 추출
 * @param {TouchEvent} event - 터치 이벤트
 * @returns {{x: number, y: number}} 좌표
 */
export function getTouchCoordinates(event) {
  if (event.touches && event.touches.length > 0) {
    return {
      x: event.touches[0].clientX,
      y: event.touches[0].clientY
    }
  }
  return { x: 0, y: 0 }
}
