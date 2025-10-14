<template>
  <div class="fab-container">
    <button
      class="fab"
      :class="{ active: isMenuOpen }"
      @click="handleClick"
      aria-label="도구 메뉴"
    >
      <div class="fab-icon" :class="{ rotated: isMenuOpen }">
        <svg v-if="!isMenuOpen" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M17 3C17.5304 3 18.0391 3.21071 18.4142 3.58579C18.7893 3.96086 19 4.46957 19 5C19 5.53043 18.7893 6.03914 18.4142 6.41421L10.5 14.3L7.70711 11.5071C7.31658 11.1166 7.31658 10.4834 7.70711 10.0929L15.5858 2.20711C15.9609 1.83204 16.4696 1.62132 17 1.62132C17.5304 1.62132 18.0391 1.83204 18.4142 2.20711L21.7929 5.58579C22.1834 5.97631 22.1834 6.60948 21.7929 7L14.3 14.5L12 21L6.2 15.2C5.4 14.4 5.4 13.1 6.2 12.3L14.1 4.4C14.5 4 15 3.8 15.5 3.8C16 3.8 16.5 4 16.9 4.4L17 3Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
    </button>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  isMenuOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click'])

function handleClick() {
  emit('click')
}
</script>

<style scoped>
.fab-container {
  position: fixed;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  z-index: 1000;
}

.fab {
  width: 48px;
  height: 48px;
  border-radius: 24px 0 0 24px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-right: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.15);
  transition: all var(--duration-small) var(--ease-smooth);
  position: relative;
  overflow: visible;
}

.fab::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  transform: translate(-50%, -50%);
  transition: width var(--duration-medium) var(--ease-smooth),
              height var(--duration-medium) var(--ease-smooth);
}

.fab:hover {
  width: 56px;
  padding-left: 8px;
  box-shadow: -4px 0 12px rgba(0, 0, 0, 0.2);
}

.fab:hover::before {
  width: 80px;
  height: 80px;
}

.fab:active {
  transform: translateY(-50%) scale(0.95);
}

.fab.active {
  background: var(--secondary-color);
  width: 56px;
}

.fab-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform var(--duration-small) var(--ease-smooth);
  position: relative;
  z-index: 2;
}

.fab-icon.rotated {
  transform: rotate(90deg);
}

/* 태블릿 최적화 */
@media (min-width: 1024px) and (orientation: landscape) {
  .fab {
    width: 52px;
    height: 52px;
  }

  .fab:hover {
    width: 60px;
  }
}

@media (max-width: 767px) {
  .fab {
    width: 44px;
    height: 44px;
  }

  .fab:hover {
    width: 50px;
  }

  .fab-icon svg {
    width: 20px;
    height: 20px;
  }
}
</style>
