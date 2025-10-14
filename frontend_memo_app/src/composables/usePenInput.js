/**
 * 펜 입력 감지 Composable
 * 포인터/터치 이벤트에서 입력 타입 감지 및 펜 데이터 추출
 */

import { ref } from 'vue'

export function usePenInput(sessionData) {
  // 디버그 모드 (URL 파라미터 ?debug=pen 으로 활성화)
  const isDebugMode = ref(false)
  if (typeof window !== 'undefined') {
    const urlParams = new URLSearchParams(window.location.search)
    isDebugMode.value = urlParams.get('debug') === 'pen'
    if (isDebugMode.value) {
      console.log('🔍 [PEN DEBUG] 디버그 모드 활성화됨')
    }
  }

  /**
   * 입력 방식 감지 함수 (다층 폴백)
   * @param {Event} event - 이벤트 객체
   * @returns {string} 'pen' | 'touch' | 'mouse' | 'finger' | 'unknown'
   */
  function detectInputType(event) {
    // 1. Pointer Events가 가장 정확하므로 우선 처리
    if ('pointerType' in event && event.pointerType) {
      const type = event.pointerType // 'pen' | 'touch' | 'mouse'
      if (isDebugMode.value) {
        console.log(`🔍 [PEN DEBUG] pointerType 감지: ${type}`)
      }
      return type
    }

    // 2. 압력 데이터로 펜 감지
    if (event.pressure !== undefined && event.pressure !== null) {
      if (event.pressure > 0 && event.pressure !== 0.5) {
        if (isDebugMode.value) {
          console.log(`🔍 [PEN DEBUG] pressure로 펜 감지: ${event.pressure}`)
        }
        return 'pen'
      } else if (event.pressure === 0.5) {
        return 'mouse'
      }
    }

    // 3. 기울기 정보가 있으면 펜 (0 값도 유효)
    if (event.tiltX !== undefined || event.tiltY !== undefined) {
      if (isDebugMode.value) {
        console.log(`🔍 [PEN DEBUG] tilt로 펜 감지: tiltX=${event.tiltX}, tiltY=${event.tiltY}`)
      }
      return 'pen'
    }

    // 4. Touch 폴백 (iOS)
    if ('changedTouches' in event && event.changedTouches?.length) {
      const touch = event.changedTouches[0]

      // iOS WebKit: Apple Pencil이면 'stylus'가 올 수 있음
      if ('touchType' in touch && touch.touchType === 'stylus') {
        return 'pen'
      }

      // 압력이나 각도 정보가 있으면 펜
      const hasForce = typeof touch.force === 'number' && touch.force > 0.1
      const hasTilt = typeof touch.altitudeAngle === 'number' || typeof touch.azimuthAngle === 'number'
      const hasPressure = typeof touch.pressure === 'number' && touch.pressure > 0.1

      if (hasForce || hasTilt || hasPressure) {
        return 'pen'
      }

      return 'finger'
    }

    // 5. 단일 터치 이벤트 처리 (touches 배열 사용)
    if (event.type.includes('touch') && event.touches?.length) {
      // 다중 터치는 항상 손가락
      if (event.touches.length > 1) {
        return 'finger'
      }

      const touch = event.touches[0]

      // iOS WebKit 지원
      if ('touchType' in touch && touch.touchType === 'stylus') {
        return 'pen'
      }

      // 압력/각도 기반 감지
      const hasForce = typeof touch.force === 'number' && touch.force > 0.1
      const hasTilt = typeof touch.altitudeAngle === 'number' || typeof touch.azimuthAngle === 'number'

      if (hasForce || hasTilt) {
        return 'pen'
      }

      return 'finger'
    }

    // 6. Mouse 폴백
    if (event.type === 'mousedown' || event.type === 'mousemove' || event.type === 'mouseup') {
      return 'mouse'
    }

    return 'unknown'
  }

  /**
   * 이벤트에서 펜 데이터 추출
   * @param {Event} event - 이벤트 객체
   * @param {Function} getCoordinates - 좌표 변환 함수
   * @param {string} currentTool - 현재 도구
   * @param {string} currentColor - 현재 색상
   * @param {number} strokeWidth - 현재 선 굵기
   * @returns {object} 추출된 펜 데이터
   */
  function extractEventData(event, getCoordinates, currentTool, currentColor, strokeWidth) {
    const coords = getCoordinates(event)
    const timestamp = Date.now() - sessionData.value.startTime
    const inputType = detectInputType(event)

    // 포인터 이벤트에서 압력, 기울기, 비틀기 정보 추출
    let pressure = null
    let tiltX = 0
    let tiltY = 0
    let twist = 0

    // 압력 센서 데이터 수집 (조건 완화 - inputType 체크 제거)
    if (event.pressure !== undefined && event.pressure !== null) {
      if (event.pressure > 0) {
        pressure = event.pressure
        sessionData.value.capabilities.pressure = true
      }
    }

    // 틸트 데이터 수집 (개선됨 - 0 값도 유효)
    if (event.tiltX !== undefined && event.tiltX !== null) {
      tiltX = event.tiltX
      sessionData.value.capabilities.tilt = true
    }
    if (event.tiltY !== undefined && event.tiltY !== null) {
      tiltY = event.tiltY
      sessionData.value.capabilities.tilt = true
    }

    // Twist 데이터 수집
    if (event.twist !== undefined && event.twist !== null) {
      twist = event.twist
      sessionData.value.capabilities.twist = true
    }

    // 디버그 모드: 포인터 데이터 출력
    if (isDebugMode.value && (inputType === 'pen' || pressure > 0)) {
      console.log(`🔍 [PEN DEBUG] inputType=${inputType}, pressure=${pressure}, tiltX=${tiltX}, tiltY=${tiltY}, twist=${twist}`)
    }

    return {
      timestamp,
      x: coords.x,
      y: coords.y,
      pressure,
      tiltX,
      tiltY,
      twist,
      eventType: event.type,
      inputType,
      tool: currentTool,
      color: currentColor,
      strokeWidth
    }
  }

  /**
   * Coalesced Events 추출 함수 (고주파수 데이터 수집)
   * @param {Event} event - 포인터 이벤트
   * @param {Function} getCoordinates - 좌표 변환 함수
   * @param {string} currentTool - 현재 도구
   * @param {string} currentColor - 현재 색상
   * @param {number} strokeWidth - 현재 선 굵기
   * @returns {Array|null} 추출된 coalesced events 배열 또는 null
   */
  function extractCoalescedEvents(event, getCoordinates, currentTool, currentColor, strokeWidth) {
    // getCoalescedEvents() 지원 확인
    if (!event.getCoalescedEvents || typeof event.getCoalescedEvents !== 'function') {
      return null
    }

    try {
      const coalescedEvents = event.getCoalescedEvents()

      // coalesced events가 있으면 capabilities 업데이트
      if (coalescedEvents && coalescedEvents.length > 0) {
        sessionData.value.capabilities.coalesced = true

        if (isDebugMode.value) {
          console.log(`🔍 [PEN DEBUG] Coalesced events: ${coalescedEvents.length}개`)
        }

        // 각 coalesced event에서 데이터 추출
        return coalescedEvents.map(e => extractEventData(e, getCoordinates, currentTool, currentColor, strokeWidth))
      }
    } catch (err) {
      if (isDebugMode.value) {
        console.warn(`⚠️ [PEN DEBUG] Coalesced events 추출 실패:`, err)
      }
    }

    return null
  }

  return {
    isDebugMode,
    detectInputType,
    extractEventData,
    extractCoalescedEvents
  }
}
