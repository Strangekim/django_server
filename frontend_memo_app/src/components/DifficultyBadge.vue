<template>
  <div class="difficulty-badge" :class="difficultyClass">
    <div class="difficulty-icon">
      <svg v-if="level === 'easy'" width="16" height="16" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="9" fill="currentColor"/>
      </svg>
      <svg v-else-if="level === 'normal'" width="16" height="16" viewBox="0 0 24 24" fill="none">
        <polygon points="12 2 22 20 2 20" fill="currentColor"/>
      </svg>
      <svg v-else-if="level === 'hard'" width="16" height="16" viewBox="0 0 24 24" fill="none">
        <polygon points="12 2 2 7 10 12.5 2 18 12 22 22 18 14 12.5 22 7" fill="currentColor"/>
      </svg>
      <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none">
        <polygon points="12 2 15.09 8.26 22 9 17 14.74 18.18 22 12 18.27 5.82 22 7 14.74 2 9 8.91 8.26" fill="currentColor"/>
      </svg>
    </div>
    <span class="difficulty-text">{{ levelText }}</span>
    <div class="difficulty-bars">
      <div
        v-for="i in 5"
        :key="i"
        class="difficulty-bar"
        :class="{ active: i <= barCount }"
      ></div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DifficultyBadge',
  props: {
    difficulty: {
      type: Number,
      required: true,
      validator: (value) => value >= 1 && value <= 100
    }
  },
  computed: {
    level() {
      if (this.difficulty <= 25) return 'easy'
      if (this.difficulty <= 50) return 'normal'
      if (this.difficulty <= 75) return 'hard'
      return 'expert'
    },
    levelText() {
      const texts = {
        easy: '쉬움',
        normal: '보통',
        hard: '어려움',
        expert: '매우어려움'
      }
      return texts[this.level]
    },
    difficultyClass() {
      return `difficulty-${this.level}`
    },
    barCount() {
      return Math.ceil(this.difficulty / 20)
    }
  }
}
</script>

<style scoped>
.difficulty-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.2s ease;
}

.difficulty-easy {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
}

.difficulty-normal {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  box-shadow: 0 2px 4px rgba(245, 158, 11, 0.3);
}

.difficulty-hard {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
}

.difficulty-expert {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  color: white;
  box-shadow: 0 2px 4px rgba(139, 92, 246, 0.3);
}

.difficulty-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
}

.difficulty-text {
  font-size: 11px;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.difficulty-bars {
  display: flex;
  gap: 2px;
  align-items: center;
}

.difficulty-bar {
  width: 3px;
  height: 12px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  transition: all 0.2s ease;
}

.difficulty-bar.active {
  background: rgba(255, 255, 255, 0.9);
  transform: scaleY(1.1);
}

/* 호버 효과 */
.difficulty-badge:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.difficulty-easy:hover {
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.4);
}

.difficulty-normal:hover {
  box-shadow: 0 4px 8px rgba(245, 158, 11, 0.4);
}

.difficulty-hard:hover {
  box-shadow: 0 4px 8px rgba(239, 68, 68, 0.4);
}

.difficulty-expert:hover {
  box-shadow: 0 4px 8px rgba(139, 92, 246, 0.4);
}

/* 태블릿 반응형 */
@media (max-width: 767px) {
  .difficulty-badge {
    padding: 4px 8px;
    gap: 4px;
  }

  .difficulty-text {
    font-size: 10px;
  }

  .difficulty-bar {
    width: 2px;
    height: 10px;
  }
}
</style>