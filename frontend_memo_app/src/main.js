import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import './assets/styles/global.css'

// MathJax 설정 및 초기화
// MathJax가 수식을 렌더링할 때 사용할 전역 설정
window.MathJax = {
  // TeX 입력 설정 (LaTeX 수식 지원)
  tex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']],  // 인라인 수식: $수식$ 또는 \(수식\)
    displayMath: [['$$', '$$'], ['\\[', '\\]']], // 블록 수식: $$수식$$ 또는 \[수식\]
    processEscapes: true,  // 역슬래시 이스케이프 처리 활성화
    processEnvironments: true  // LaTeX 환경 처리 활성화
  },
  // SVG 출력 설정 (수식을 SVG로 렌더링)
  svg: {
    fontCache: 'global'  // 폰트 캐시를 전역으로 설정하여 성능 향상
  },
  // MathJax 시작 설정
  startup: {
    // 페이지 로드 시 자동으로 수식 렌더링하지 않음 (Vue 컴포넌트에서 수동으로 제어)
    typeset: false
  }
}

// Vue 앱 생성 및 마운트
const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.mount('#app')