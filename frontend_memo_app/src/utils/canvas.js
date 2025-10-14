/**
 * 캔버스 관련 유틸리티 함수
 */

/**
 * 두 점 사이의 유클리드 거리 계산
 * @param {number} x1 - 첫 번째 점의 x 좌표
 * @param {number} y1 - 첫 번째 점의 y 좌표
 * @param {number} x2 - 두 번째 점의 x 좌표
 * @param {number} y2 - 두 번째 점의 y 좌표
 * @returns {number} 두 점 사이의 거리
 */
export function calculateDistance(x1, y1, x2, y2) {
  const dx = x2 - x1
  const dy = y2 - y1
  return Math.sqrt(dx * dx + dy * dy)
}

/**
 * 포인트 배열로부터 바운딩 박스 계산
 * @param {Array} points - 포인트 배열 [{x, y}, ...]
 * @returns {Array<number>} [minX, minY, maxX, maxY]
 */
export function calculateBoundingBox(points) {
  if (!points || points.length === 0) {
    return [0, 0, 0, 0]
  }

  let minX = Infinity
  let minY = Infinity
  let maxX = -Infinity
  let maxY = -Infinity

  for (const point of points) {
    minX = Math.min(minX, point.x)
    minY = Math.min(minY, point.y)
    maxX = Math.max(maxX, point.x)
    maxY = Math.max(maxY, point.y)
  }

  return [minX, minY, maxX, maxY]
}

/**
 * 화면 좌표를 캔버스 좌표로 변환 (줌/팬 고려)
 * @param {number} screenX - 화면 x 좌표
 * @param {number} screenY - 화면 y 좌표
 * @param {number} zoom - 확대 비율
 * @param {number} panX - 패닝 x 오프셋
 * @param {number} panY - 패닝 y 오프셋
 * @returns {{x: number, y: number}} 캔버스 좌표
 */
export function screenToCanvas(screenX, screenY, zoom, panX, panY) {
  return {
    x: (screenX - panX) / zoom,
    y: (screenY - panY) / zoom
  }
}

/**
 * 캔버스 좌표를 화면 좌표로 변환 (줌/팬 고려)
 * @param {number} canvasX - 캔버스 x 좌표
 * @param {number} canvasY - 캔버스 y 좌표
 * @param {number} zoom - 확대 비율
 * @param {number} panX - 패닝 x 오프셋
 * @param {number} panY - 패닝 y 오프셋
 * @returns {{x: number, y: number}} 화면 좌표
 */
export function canvasToScreen(canvasX, canvasY, zoom, panX, panY) {
  return {
    x: canvasX * zoom + panX,
    y: canvasY * zoom + panY
  }
}

/**
 * 캔버스 컨텍스트에 변환 적용 (줌/팬)
 * @param {CanvasRenderingContext2D} ctx - 캔버스 컨텍스트
 * @param {number} zoom - 확대 비율
 * @param {number} panX - 패닝 x 오프셋
 * @param {number} panY - 패닝 y 오프셋
 */
export function applyCanvasTransform(ctx, zoom, panX, panY) {
  ctx.setTransform(zoom, 0, 0, zoom, panX, panY)
}

/**
 * 캔버스를 완전히 지움
 * @param {HTMLCanvasElement} canvas - 캔버스 엘리먼트
 * @param {CanvasRenderingContext2D} ctx - 캔버스 컨텍스트
 */
export function clearCanvas(canvas, ctx) {
  ctx.save()
  ctx.setTransform(1, 0, 0, 1, 0, 0)
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  ctx.restore()
}
