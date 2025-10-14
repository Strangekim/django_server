<template>
  <transition name="radial-menu-fade">
    <div v-if="isOpen" class="radial-menu-overlay" @click="handleOverlayClick">
      <div class="radial-menu-container">
        <!-- 메뉴 아이템들 -->
        <div
          v-for="(item, index) in menuItems"
          :key="item.id"
          class="radial-menu-item"
          :class="{ active: isItemActive(item) }"
          :style="getItemStyle(item, index)"
          @click.stop="handleItemClick(item)"
        >
          <div class="item-button">
            <component :is="getIconComponent(item.icon)" />
          </div>
          <div class="item-label">{{ item.label }}</div>
        </div>

        <!-- 색상 팔레트 서브 메뉴 -->
        <transition name="submenu-fade">
          <div v-if="showColorPalette" class="submenu-container color-palette-submenu">
            <h4 class="submenu-title">색상 선택</h4>
            <div class="color-grid">
              <button
                v-for="color in colors"
                :key="color"
                class="color-button"
                :class="{ active: selectedColor === color }"
                :style="{ backgroundColor: color }"
                @click="handleColorSelect(color)"
                :aria-label="`색상: ${color}`"
              ></button>
            </div>
            <button class="close-submenu" @click="closeSubmenus">닫기</button>
          </div>
        </transition>

        <!-- 선 굵기 서브 메뉴 -->
        <transition name="submenu-fade">
          <div v-if="showStrokeWidthSelector" class="submenu-container stroke-width-submenu">
            <h4 class="submenu-title">선 굵기</h4>
            <div class="stroke-width-list">
              <button
                v-for="width in strokeWidthOptions"
                :key="width"
                class="stroke-width-button"
                :class="{ active: strokeWidth === width }"
                @click="handleStrokeWidthSelect(width)"
              >
                <div class="width-preview" :style="{ height: `${width}px`, backgroundColor: selectedColor }"></div>
                <span class="width-label">{{ width }}px</span>
              </button>
            </div>
            <button class="close-submenu" @click="closeSubmenus">닫기</button>
          </div>
        </transition>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { computed, defineProps, defineEmits } from 'vue'
import { COLORS } from '../constants/colors.js'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  currentTool: {
    type: String,
    default: 'pen'
  },
  selectedColor: {
    type: String,
    default: '#000000'
  },
  strokeWidth: {
    type: Number,
    default: 2
  },
  showColorPalette: {
    type: Boolean,
    default: false
  },
  showStrokeWidthSelector: {
    type: Boolean,
    default: false
  },
  canUndo: {
    type: Boolean,
    default: false
  },
  canRedo: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'select-tool',
  'select-color',
  'select-stroke-width',
  'open-color-palette',
  'open-stroke-width-selector',
  'close-submenus',
  'close',
  'undo',
  'redo',
  'clear-all'
])

// 메뉴 아이템 정의
const menuItems = computed(() => [
  {
    id: 'pen',
    label: '펜',
    icon: 'pen',
    angle: 0,
    action: () => emit('select-tool', 'pen')
  },
  {
    id: 'eraser',
    label: '지우개',
    icon: 'eraser',
    angle: 45,
    action: () => emit('select-tool', 'eraser')
  },
  {
    id: 'color',
    label: '색상',
    icon: 'palette',
    angle: 90,
    action: () => emit('open-color-palette')
  },
  {
    id: 'width',
    label: '굵기',
    icon: 'width',
    angle: 135,
    action: () => emit('open-stroke-width-selector')
  },
  {
    id: 'undo',
    label: '실행 취소',
    icon: 'undo',
    angle: 180,
    action: () => emit('undo'),
    disabled: !props.canUndo
  },
  {
    id: 'redo',
    label: '다시 실행',
    icon: 'redo',
    angle: 225,
    action: () => emit('redo'),
    disabled: !props.canRedo
  },
  {
    id: 'clear',
    label: '전체 지우기',
    icon: 'trash',
    angle: 270,
    action: () => emit('clear-all')
  },
  {
    id: 'close',
    label: '닫기',
    icon: 'close',
    angle: 315,
    action: () => emit('close')
  }
])

const colors = COLORS
const strokeWidthOptions = [1, 2, 3, 5, 8, 12, 16, 20]

// 아이템 위치 계산
function getItemStyle(item, index) {
  const radius = 110 // px (FAB 주변 배치)
  const radians = ((item.angle - 90) * Math.PI) / 180
  const x = Math.cos(radians) * radius
  const y = Math.sin(radians) * radius

  return {
    '--item-x': `${x}px`,
    '--item-y': `${y}px`,
    transitionDelay: `${index * 60}ms`
  }
}

// 아이템 활성 상태
function isItemActive(item) {
  if (item.id === 'pen' || item.id === 'eraser') {
    return props.currentTool === item.id
  }
  return false
}

// 아이템 클릭 핸들러
function handleItemClick(item) {
  if (item.disabled) return
  if (item.action) {
    item.action()
  }
}

// 오버레이 클릭 핸들러
function handleOverlayClick() {
  emit('close')
}

// 색상 선택 핸들러
function handleColorSelect(color) {
  emit('select-color', color)
  emit('close-submenus')
}

// 선 굵기 선택 핸들러
function handleStrokeWidthSelect(width) {
  emit('select-stroke-width', width)
  emit('close-submenus')
}

// 서브 메뉴 닫기
function closeSubmenus() {
  emit('close-submenus')
}

// 아이콘 컴포넌트 반환
function getIconComponent(iconName) {
  // SVG를 직접 반환하는 함수형 컴포넌트
  const icons = {
    pen: () => `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M17 3C17.5304 3 18.0391 3.21071 18.4142 3.58579C18.7893 3.96086 19 4.46957 19 5C19 5.53043 18.7893 6.03914 18.4142 6.41421L10.5 14.3L7.70711 11.5071C7.31658 11.1166 7.31658 10.4834 7.70711 10.0929L15.5858 2.20711C15.9609 1.83204 16.4696 1.62132 17 1.62132C17.5304 1.62132 18.0391 1.83204 18.4142 2.20711L21.7929 5.58579C22.1834 5.97631 22.1834 6.60948 21.7929 7L14.3 14.5L12 21L6.2 15.2C5.4 14.4 5.4 13.1 6.2 12.3L14.1 4.4C14.5 4 15 3.8 15.5 3.8C16 3.8 16.5 4 16.9 4.4L17 3Z" stroke="currentColor" stroke-width="2"/>
    </svg>`,
    eraser: () => `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M20 20H8L2.6 14.6C2.4 14.4 2.4 14.1 2.6 13.9L8.9 7.6C9.1 7.4 9.4 7.4 9.6 7.6L16.4 14.4C16.6 14.6 16.6 14.9 16.4 15.1L11 20.5H20V20Z" stroke="currentColor" stroke-width="2"/>
    </svg>`,
    palette: () => `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2C6.49 2 2 6.49 2 12C2 17.51 6.49 22 12 22C12.55 22 13 21.55 13 21V20.5C13 20.11 12.89 19.74 12.71 19.43C12.53 19.13 12.5 18.76 12.66 18.43C12.82 18.1 13.14 17.89 13.5 17.89H15C18.31 17.89 21 15.2 21 11.89C21 6.43 16.73 2 12 2ZM6.5 12C5.67 12 5 11.33 5 10.5C5 9.67 5.67 9 6.5 9C7.33 9 8 9.67 8 10.5C8 11.33 7.33 12 6.5 12ZM9.5 8C8.67 8 8 7.33 8 6.5C8 5.67 8.67 5 9.5 5C10.33 5 11 5.67 11 6.5C11 7.33 10.33 8 9.5 8ZM14.5 8C13.67 8 13 7.33 13 6.5C13 5.67 13.67 5 14.5 5C15.33 5 16 5.67 16 6.5C16 7.33 15.33 8 14.5 8ZM17.5 12C16.67 12 16 11.33 16 10.5C16 9.67 16.67 9 17.5 9C18.33 9 19 9.67 19 10.5C19 11.33 18.33 12 17.5 12Z" fill="currentColor"/>
    </svg>`,
    width: () => `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <line x1="4" y1="6" x2="20" y2="6" stroke="currentColor" stroke-width="1"/>
      <line x1="4" y1="10" x2="20" y2="10" stroke="currentColor" stroke-width="2"/>
      <line x1="4" y1="15" x2="20" y2="15" stroke="currentColor" stroke-width="4"/>
    </svg>`,
    undo: () => `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 7V3H7" stroke="currentColor" stroke-width="2"/>
      <path d="M3.05115 6.39892C4.62949 3.75965 7.49854 2 11 2C15.9706 2 20 6.02944 20 11V13" stroke="currentColor" stroke-width="2"/>
    </svg>`,
    redo: () => `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M21 7V3H17" stroke="currentColor" stroke-width="2"/>
      <path d="M20.9489 6.39892C19.3705 3.75965 16.5015 2 13 2C8.02944 2 4 6.02944 4 11V13" stroke="currentColor" stroke-width="2"/>
    </svg>`,
    trash: () => `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 6H5H21" stroke="currentColor" stroke-width="2"/>
      <path d="M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6H19Z" stroke="currentColor" stroke-width="2"/>
    </svg>`,
    close: () => `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2"/>
    </svg>`
  }

  return {
    template: icons[iconName] ? icons[iconName]() : icons.pen()
  }
}
</script>

<style scoped>
.radial-menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(2px);
  z-index: 999;
  pointer-events: auto;
}

.radial-menu-container {
  position: fixed;
  right: 60px;
  top: 50%;
  transform: translateY(-50%);
  width: 280px;
  height: 280px;
  pointer-events: none;
  z-index: 1001;
}

.radial-menu-item {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(calc(-50% + var(--item-x, 0px)), calc(-50% + var(--item-y, 0px))) scale(0) rotate(180deg);
  opacity: 0;
  transition: all var(--duration-medium) var(--ease-spring);
  pointer-events: auto;
}

.radial-menu-overlay .radial-menu-item {
  opacity: 1;
  transform: translate(calc(-50% + var(--item-x, 0px)), calc(-50% + var(--item-y, 0px))) scale(1) rotate(0deg);
}

.item-button {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: white;
  color: var(--text-primary);
  border: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--duration-small) var(--ease-smooth);
  box-shadow: var(--shadow-md);
  pointer-events: auto;
}

.item-button:hover {
  transform: scale(1.15);
  box-shadow: var(--shadow-lg);
  border-color: var(--primary-color);
}

.radial-menu-item.active .item-button {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.item-label {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-top: 8px;
  font-size: 11px;
  font-weight: 500;
  color: white;
  white-space: nowrap;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

/* 서브 메뉴 */
.submenu-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: var(--shadow-xl);
  min-width: 280px;
  max-width: 90vw;
  z-index: 10;
}

.submenu-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--text-primary);
}

.color-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 8px;
  margin-bottom: 16px;
}

.color-button {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all var(--duration-small) var(--ease-smooth);
}

.color-button:hover {
  transform: scale(1.1);
  box-shadow: var(--shadow-md);
}

.color-button.active {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px white, 0 0 0 4px var(--primary-color);
}

.stroke-width-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.stroke-width-button {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all var(--duration-small) var(--ease-smooth);
}

.stroke-width-button:hover {
  border-color: var(--primary-color);
  background: var(--surface-color);
}

.stroke-width-button.active {
  border-color: var(--primary-color);
  background: var(--surface-color);
}

.width-preview {
  width: 60px;
  border-radius: 2px;
}

.width-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.close-submenu {
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 8px;
  background: var(--surface-color);
  color: var(--text-primary);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--duration-small) var(--ease-smooth);
}

.close-submenu:hover {
  background: var(--border-color);
}

/* 애니메이션 */
.radial-menu-fade-enter-active,
.radial-menu-fade-leave-active {
  transition: opacity var(--duration-small) var(--ease-smooth);
}

.radial-menu-fade-enter-from,
.radial-menu-fade-leave-to {
  opacity: 0;
}

.submenu-fade-enter-active,
.submenu-fade-leave-active {
  transition: all var(--duration-small) var(--ease-smooth);
}

.submenu-fade-enter-from,
.submenu-fade-leave-to {
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.9);
}
</style>
