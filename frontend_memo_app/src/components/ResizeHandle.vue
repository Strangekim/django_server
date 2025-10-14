<template>
  <div
    class="resize-handle"
    :class="{ resizing: isResizing }"
    @mousedown="handleMouseDown"
    @touchstart="handleTouchStart"
  >
    <div class="handle-line"></div>
    <div class="handle-grip">
      <span class="grip-dot"></span>
      <span class="grip-dot"></span>
      <span class="grip-dot"></span>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  isResizing: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['resize-start'])

function handleMouseDown(event) {
  emit('resize-start', event)
}

function handleTouchStart(event) {
  emit('resize-start', event)
}
</script>

<style scoped>
.resize-handle {
  position: absolute;
  top: 0;
  right: 0;
  width: 6px;
  height: 100%;
  cursor: col-resize;
  z-index: 100;
  transition: background-color var(--duration-small) var(--ease-smooth);
  display: flex;
  align-items: center;
  justify-content: center;
}

.resize-handle:hover,
.resize-handle.resizing {
  background-color: rgba(0, 0, 0, 0.05);
}

.handle-line {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 2px;
  height: 100%;
  background: var(--border-color);
  transition: background-color var(--duration-small) var(--ease-smooth);
}

.resize-handle:hover .handle-line,
.resize-handle.resizing .handle-line {
  background: var(--primary-color);
}

.handle-grip {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  gap: 3px;
  padding: 8px 0;
  opacity: 0;
  transition: opacity var(--duration-small) var(--ease-smooth);
}

.resize-handle:hover .handle-grip,
.resize-handle.resizing .handle-grip {
  opacity: 1;
}

.grip-dot {
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: var(--text-secondary);
}

.resize-handle:hover .grip-dot,
.resize-handle.resizing .grip-dot {
  background: var(--primary-color);
}

/* 태블릿 최적화 */
@media (min-width: 1024px) and (orientation: landscape) {
  .resize-handle {
    width: 8px;
  }
}

@media (max-width: 767px) {
  .resize-handle {
    width: 10px;
  }

  .handle-grip {
    gap: 4px;
  }

  .grip-dot {
    width: 4px;
    height: 4px;
  }
}
</style>
