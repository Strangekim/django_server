<template>
  <div class="notebook-lines" :style="containerStyle">
    <div
      v-for="i in lineCount"
      :key="i"
      class="notebook-line"
      :style="getLineStyle(i)"
    ></div>
  </div>
</template>

<script setup>
import { computed, defineProps } from 'vue'

const props = defineProps({
  scrollY: {
    type: Number,
    default: 0
  },
  canvasHeight: {
    type: Number,
    default: 5000
  },
  viewportHeight: {
    type: Number,
    default: 800
  },
  lineSpacing: {
    type: Number,
    default: 45 // px
  }
})

// 필요한 선의 개수 계산
const lineCount = computed(() => {
  return Math.ceil(props.canvasHeight / props.lineSpacing) + 1
})

// 컨테이너 스타일
const containerStyle = computed(() => {
  return {
    height: `${props.canvasHeight}px`,
    transform: `translateY(${-props.scrollY}px)`
  }
})

// 각 선의 위치 계산
function getLineStyle(index) {
  // 첫 번째 줄은 상단 표시를 위해 간격을 더 크게
  const y = index === 1 ? 0 : (index - 1) * props.lineSpacing + (index === 2 ? 20 : 0)
  return {
    top: `${y}px`
  }
}
</script>

<style scoped>
.notebook-lines {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  pointer-events: none;
  z-index: 0;
  transition: transform 0.05s linear;
  padding: 0 40px; /* 좌우 여백 */
}

.notebook-line {
  position: absolute;
  left: 40px;
  right: 40px;
  width: auto;
  height: 1px;
  background: var(--notebook-line-color);
}

.notebook-line:nth-child(5n) {
  background: rgba(0, 0, 0, 0.12);
}

/* 태블릿 최적화 */
@media (min-width: 1024px) and (orientation: landscape) {
  .notebook-lines {
    padding: 0 60px;
  }

  .notebook-line {
    left: 60px;
    right: 60px;
  }
}

@media (max-width: 767px) {
  .notebook-lines {
    padding: 0 24px;
  }

  .notebook-line {
    left: 24px;
    right: 24px;
  }
}
</style>
