<template>
  <!-- MathJax로 수식을 렌더링할 컨테이너 -->
  <div ref="mathContainer" class="math-content"></div>
</template>

<script>
import { ref, onMounted, watch, nextTick } from 'vue'

export default {
  name: 'MathContent',
  props: {
    // 렌더링할 텍스트 (LaTeX 수식 포함 가능)
    content: {
      type: String,
      default: ''
    }
  },
  setup(props) {
    // MathJax가 렌더링할 DOM 요소 참조
    const mathContainer = ref(null)

    /**
     * MathJax를 사용하여 수식을 렌더링하는 함수
     * LaTeX 수식이 포함된 텍스트를 수학 기호로 변환
     */
    const renderMath = async () => {
      // DOM 요소가 없으면 종료
      if (!mathContainer.value) return

      // 텍스트 내용을 DOM에 설정
      mathContainer.value.innerHTML = props.content

      // MathJax 라이브러리가 로드되었는지 확인
      if (window.MathJax && window.MathJax.typesetPromise) {
        try {
          // 이전 렌더링 초기화 (캐시 제거)
          if (window.MathJax.typesetClear) {
            window.MathJax.typesetClear([mathContainer.value])
          }

          // MathJax를 사용하여 현재 컨테이너 내의 수식 렌더링
          // typesetPromise는 비동기로 수식을 변환
          await window.MathJax.typesetPromise([mathContainer.value])
        } catch (error) {
          // 렌더링 중 에러 발생 시 콘솔에 출력
          console.error('MathJax 렌더링 오류:', error)
        }
      } else {
        // MathJax가 아직 로드되지 않은 경우
        console.warn('MathJax가 아직 로드되지 않았습니다.')

        // MathJax 라이브러리 동적 로드
        loadMathJax()
      }
    }

    /**
     * MathJax 라이브러리를 동적으로 로드하는 함수
     * CDN에서 MathJax 스크립트를 가져와서 페이지에 추가
     */
    const loadMathJax = () => {
      // 이미 로드 중이거나 로드된 경우 중복 방지
      if (document.getElementById('mathjax-script')) return

      // script 태그 생성
      const script = document.createElement('script')
      script.id = 'mathjax-script'
      script.async = true
      script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js'

      // MathJax 로드 완료 후 렌더링 실행
      script.onload = () => {
        console.log('MathJax 로드 완료')
        // 로드 후 약간의 지연을 두고 렌더링
        setTimeout(renderMath, 100)
      }

      // 스크립트를 문서 head에 추가
      document.head.appendChild(script)
    }

    // 컴포넌트가 마운트되면 MathJax 렌더링 시작
    onMounted(() => {
      // DOM이 완전히 업데이트된 후 렌더링
      nextTick(() => {
        renderMath()
      })
    })

    // content prop이 변경될 때마다 다시 렌더링
    watch(
      () => props.content,
      () => {
        // DOM 업데이트 후 렌더링
        nextTick(() => {
          renderMath()
        })
      }
    )

    return {
      mathContainer
    }
  }
}
</script>

<style scoped>
/* 수식 렌더링 컨테이너 스타일 */
.math-content {
  font-size: inherit; /* 부모로부터 폰트 크기 상속 */
  line-height: inherit; /* 부모로부터 줄 높이 상속 */
  color: inherit; /* 부모로부터 색상 상속 */
  word-wrap: break-word; /* 긴 수식이 컨테이너를 벗어나지 않도록 줄바꿈 */
  overflow-wrap: break-word; /* 단어 단위로 줄바꿈 */
}

/* MathJax SVG 요소 스타일 조정 */
.math-content :deep(mjx-container) {
  display: inline-block; /* 인라인 블록으로 표시 */
  margin: 0 2px; /* 좌우 약간의 여백 */
}

/* 블록 수식 (display math) 스타일 */
.math-content :deep(mjx-container[display="block"]) {
  display: block; /* 블록으로 표시 */
  margin: 1em 0; /* 상하 여백 */
  text-align: center; /* 중앙 정렬 */
}
</style>
