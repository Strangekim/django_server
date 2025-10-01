<template>
  <svg
    width="512"
    height="512"
    viewBox="0 0 512 512"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <!-- 배경 -->
    <rect width="512" height="512" rx="96" fill="#fef7ed"/>

    <!-- 메인 원형 배경 -->
    <circle cx="256" cy="256" r="200" fill="#fed7aa" opacity="0.5"/>

    <!-- 펜 아이콘 -->
    <path
      d="M320 160L352 192L240 304L208 272L320 160Z"
      fill="#d97706"
      stroke="#a16207"
      stroke-width="4"
    />
    <path
      d="M352 192L368 208L256 320L240 304L352 192Z"
      fill="#ea580c"
    />

    <!-- 수학 기호들 -->
    <text x="180" y="400" font-family="serif" font-size="48" fill="#a16207" font-weight="bold">∑</text>
    <text x="320" y="400" font-family="serif" font-size="40" fill="#a16207">π</text>
    <text x="140" y="180" font-family="serif" font-size="36" fill="#a16207">∫</text>
    <text x="360" y="180" font-family="serif" font-size="32" fill="#a16207">√</text>

    <!-- 격자 라인 (희미하게) -->
    <g opacity="0.2" stroke="#d97706" stroke-width="1">
      <line x1="120" y1="140" x2="390" y2="140"/>
      <line x1="120" y1="180" x2="390" y2="180"/>
      <line x1="120" y1="220" x2="390" y2="220"/>
      <line x1="140" y1="120" x2="140" y2="240"/>
      <line x1="180" y1="120" x2="180" y2="240"/>
      <line x1="220" y1="120" x2="220" y2="240"/>
    </g>
  </svg>
</template>

<script>
export default {
  name: 'AppIcon'
}
</script>