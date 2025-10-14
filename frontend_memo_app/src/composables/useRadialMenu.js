/**
 * Radial Menu Composable
 * 원형 도구 선택 메뉴 관리
 */

import { ref, computed } from 'vue'
import { TOOL_PEN, TOOL_ERASER } from '../constants/tools.js'
import { COLORS } from '../constants/colors.js'

export function useRadialMenu() {
  // 상태
  const isOpen = ref(false)
  const selectedTool = ref(TOOL_PEN)
  const selectedColor = ref(COLORS[0])
  const strokeWidth = ref(2)

  // 메뉴 아이템 정의 (8방향)
  const menuItems = computed(() => [
    {
      id: 'pen',
      label: '펜',
      icon: 'pen',
      angle: 0, // 12시 방향
      action: () => setTool(TOOL_PEN)
    },
    {
      id: 'eraser',
      label: '지우개',
      icon: 'eraser',
      angle: 45, // 1시 30분 방향
      action: () => setTool(TOOL_ERASER)
    },
    {
      id: 'color',
      label: '색상',
      icon: 'palette',
      angle: 90, // 3시 방향
      action: () => openColorPalette()
    },
    {
      id: 'width',
      label: '굵기',
      icon: 'width',
      angle: 135, // 4시 30분 방향
      action: () => openStrokeWidthSelector()
    },
    {
      id: 'undo',
      label: '실행 취소',
      icon: 'undo',
      angle: 180, // 6시 방향
      action: () => emit('undo')
    },
    {
      id: 'redo',
      label: '다시 실행',
      icon: 'redo',
      angle: 225, // 7시 30분 방향
      action: () => emit('redo')
    },
    {
      id: 'clear',
      label: '전체 지우기',
      icon: 'trash',
      angle: 270, // 9시 방향
      action: () => emit('clear')
    },
    {
      id: 'close',
      label: '닫기',
      icon: 'close',
      angle: 315, // 10시 30분 방향
      action: () => toggle()
    }
  ])

  // 서브 메뉴 상태
  const showColorPalette = ref(false)
  const showStrokeWidthSelector = ref(false)

  // Computed
  const currentToolIcon = computed(() => {
    const item = menuItems.value.find(i => i.id === selectedTool.value)
    return item ? item.icon : 'pen'
  })

  const currentToolLabel = computed(() => {
    const item = menuItems.value.find(i => i.id === selectedTool.value)
    return item ? item.label : '펜'
  })

  // 이벤트 에미터 (외부에서 주입)
  let emit = null

  /**
   * 이벤트 에미터 설정
   * @param {Function} emitFn - emit 함수
   */
  function setEmit(emitFn) {
    emit = emitFn
  }

  /**
   * 메뉴 열기/닫기 토글
   */
  function toggle() {
    isOpen.value = !isOpen.value

    // 서브 메뉴 닫기
    if (!isOpen.value) {
      closeSubMenus()
    }
  }

  /**
   * 메뉴 열기
   */
  function open() {
    isOpen.value = true
  }

  /**
   * 메뉴 닫기
   */
  function close() {
    isOpen.value = false
    closeSubMenus()
  }

  /**
   * 도구 설정
   * @param {string} tool - 도구 이름
   */
  function setTool(tool) {
    selectedTool.value = tool
    if (emit) {
      emit('tool-change', tool)
    }
    close()
  }

  /**
   * 색상 설정
   * @param {string} color - 색상 코드
   */
  function setColor(color) {
    selectedColor.value = color
    if (emit) {
      emit('color-change', color)
    }
    closeSubMenus()
  }

  /**
   * 선 굵기 설정
   * @param {number} width - 선 굵기
   */
  function setStrokeWidth(width) {
    strokeWidth.value = width
    if (emit) {
      emit('stroke-width-change', width)
    }
    closeSubMenus()
  }

  /**
   * 색상 팔레트 열기
   */
  function openColorPalette() {
    showColorPalette.value = true
    showStrokeWidthSelector.value = false
  }

  /**
   * 선 굵기 선택기 열기
   */
  function openStrokeWidthSelector() {
    showStrokeWidthSelector.value = true
    showColorPalette.value = false
  }

  /**
   * 서브 메뉴 닫기
   */
  function closeSubMenus() {
    showColorPalette.value = false
    showStrokeWidthSelector.value = false
  }

  /**
   * 메뉴 아이템 위치 계산
   * @param {number} angle - 각도 (0-360)
   * @param {number} radius - 반지름 (px)
   * @returns {object} { x, y } 위치
   */
  function calculatePosition(angle, radius) {
    const radians = (angle - 90) * (Math.PI / 180) // -90도: 12시 방향을 0도로
    return {
      x: Math.cos(radians) * radius,
      y: Math.sin(radians) * radius
    }
  }

  /**
   * 메뉴 아이템 스타일 계산
   * @param {object} item - 메뉴 아이템
   * @param {number} radius - 반지름
   * @param {number} index - 인덱스 (stagger 애니메이션용)
   * @returns {object} 스타일 객체
   */
  function getItemStyle(item, radius, index) {
    const position = calculatePosition(item.angle, radius)
    return {
      transform: `translate(${position.x}px, ${position.y}px)`,
      transitionDelay: `${index * 50}ms` // Stagger animation
    }
  }

  /**
   * 색상 팔레트 가져오기
   * @returns {Array} 색상 배열
   */
  function getColorPalette() {
    return COLORS
  }

  /**
   * 선 굵기 옵션 가져오기
   * @returns {Array} 선 굵기 배열
   */
  function getStrokeWidthOptions() {
    return [1, 2, 3, 5, 8, 12, 16, 20]
  }

  return {
    // State
    isOpen,
    selectedTool,
    selectedColor,
    strokeWidth,
    showColorPalette,
    showStrokeWidthSelector,

    // Computed
    menuItems,
    currentToolIcon,
    currentToolLabel,

    // Methods
    setEmit,
    toggle,
    open,
    close,
    setTool,
    setColor,
    setStrokeWidth,
    openColorPalette,
    openStrokeWidthSelector,
    closeSubMenus,
    calculatePosition,
    getItemStyle,
    getColorPalette,
    getStrokeWidthOptions
  }
}
