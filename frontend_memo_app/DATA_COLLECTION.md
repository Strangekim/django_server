# 📊 데이터 수집 시스템 - Math Memo App

이 문서는 Math Memo App에서 부정행위 탐지 모델 학습을 위해 수집하는 데이터에 대한 상세한 설명입니다.

## 🎯 수집 목적

부정행위(치팅) 탐지를 위한 머신러닝 모델 학습용 데이터 수집:
- 자연스러운 필기 패턴 vs 인위적 조작 구분
- 정상적인 문제 해결 과정 vs 비정상적 행동 패턴
- 집중도 및 사고 과정 분석

## 📋 수집 데이터 상세

### 🖊️ **1. 스트로크 데이터 (Stroke Data)**

각 펜/지우개 스트로크마다 수집되는 데이터:

#### 기본 정보
- `strokeId`: 스트로크 고유 ID
- `tool`: 사용 도구 ('pen' | 'eraser')
- `color`: 사용된 색상 (hex code)
- `strokeWidth`: 선 굵기 (1-20px)
- `startTime`: 스트로크 시작 시각 (세션 시작 기준 ms)
- `endTime`: 스트로크 종료 시각 (세션 시작 기준 ms)
- `totalDistance`: 총 이동 거리 (픽셀)
- `averageSpeed`: 평균 속도 (px/s)
- `averagePressure`: 평균 필압 (0.0-1.0, 지원 시)
- `bbox`: 바운딩 박스 [minX, minY, maxX, maxY]

#### 포인트 데이터 (각 스트로크 내 모든 포인트)
- `timestamp`: 포인트 시각 (스트로크 시작 기준 ms)
- `x, y`: 좌표 (픽셀)
- `pressure`: 필압 (0.0-1.0, null if 미지원)
- `tiltX, tiltY`: 펜 기울기 (-90 ~ 90도, null if 미지원)
- `twist`: 펜 회전 각도 (0-359도, null if 미지원)
- `pointerType`: 포인터 타입 ('pen' | 'touch' | 'mouse')
- `pointerId`: 포인터 ID (멀티터치 구분)
- `buttons`: 버튼 상태 (비트마스크)
- `width, height`: 접촉 영역 크기 (픽셀, null if 미지원)
- `distance`: 이전 포인트로부터의 거리 (픽셀)
- `speed`: 순간 속도 (px/s)
- `coalesced`: 고주파수 이벤트 여부 (boolean)

### 📱 **2. 상호작용 이벤트 (Interaction Events)**

사용자의 모든 상호작용을 시간순으로 기록:

#### 스트로크 관련
- `stroke_start`: 스트로크 시작
- `stroke_end`: 스트로크 종료

#### 도구 변경
- `tool_change`: 펜/지우개/손도구 변경
- `color_change`: 색상 변경
- `stroke_width_change`: 선 굵기 변경

#### 편집 행위
- `undo`: 실행 취소
- `redo`: 다시 실행
- `clear_all`: 전체 지우기

#### 화면 조작
- `zoom_in`: 확대
- `zoom_out`: 축소
- `zoom_reset`: 확대/축소 초기화
- `canvas_pan_start/end`: 캔버스 이동 시작/종료
- `image_drag_start/end`: 이미지 드래그 시작/종료

#### 세션 관리
- `session_start`: 세션 시작
- `session_end`: 세션 종료
- `window_focus`: 창 포커스 획득
- `window_blur`: 창 포커스 상실
- `overlay_image_added`: 문제 이미지 추가
- `data_download`: 데이터 다운로드

### 📊 **3. 세션 통계 (Session Statistics)**

세션 전체에 대한 집계 데이터:

- `sessionDuration`: 총 세션 시간 (ms)
- `strokeCount`: 총 스트로크 수
- `totalDistance`: 총 이동 거리 (픽셀)
- `averageStrokeLength`: 평균 스트로크 길이 (픽셀)
- `undoCount`: Undo 사용 횟수
- `redoCount`: Redo 사용 횟수
- `eraserCount`: 지우개 사용 횟수
- `zoomCount`: 확대/축소 사용 횟수
- `panCount`: 캔버스 이동 횟수

### 🔧 **4. 기기 및 환경 정보**

#### 기기 정보
- `userAgent`: 브라우저 User Agent
- `platform`: 운영체제 플랫폼
- `pixelRatio`: 화면 픽셀 비율
- `screenSize`: 화면 크기 { width, height }

#### 포인터 기능 지원
- `pressure`: 필압 감지 지원 여부
- `tilt`: 기울기 감지 지원 여부
- `twist`: 회전 감지 지원 여부
- `coalesced`: 고주파수 이벤트 지원 여부

#### 캔버스 정보
- `logicalSize`: 캔버스 논리적 크기
- `cssSize`: 캔버스 CSS 크기
- `transform`: 현재 변환 상태 (zoom, pan)

## 🔒 개인정보 보호

### 수집하지 않는 데이터
- 개인 식별 정보
- 실제 답안 내용
- 텍스트 입력 내용
- 네트워크 주소

### 익명화 처리
- 세션 ID는 랜덤 UUID 사용
- 절대 시간 대신 상대 시간 사용
- 개인 식별 불가능한 기기 정보만 수집

## 📁 데이터 형식

### JSON 구조 예시

```json
{
  "sessionInfo": {
    "sessionId": "123e4567-e89b-12d3-a456-426614174000",
    "startTime": "2024-03-20T10:30:00.000Z",
    "endTime": "2024-03-20T10:45:30.123Z",
    "duration": 930123,
    "deviceInfo": {
      "userAgent": "Mozilla/5.0...",
      "platform": "Win32",
      "pixelRatio": 1.5,
      "screenSize": { "width": 1920, "height": 1080 }
    }
  },
  "capabilities": {
    "pressure": true,
    "tilt": true,
    "twist": false,
    "coalesced": true
  },
  "canvasInfo": {
    "logicalSize": { "width": 1200, "height": 520 },
    "cssSize": { "width": 800, "height": 400 },
    "transform": { "zoom": 1.2, "panX": 10, "panY": -5 }
  },
  "strokes": [
    {
      "strokeId": 1,
      "tool": "pen",
      "color": "#000000",
      "strokeWidth": 3,
      "startTime": 1234,
      "endTime": 2345,
      "totalDistance": 156.7,
      "averageSpeed": 89.2,
      "averagePressure": 0.72,
      "bbox": [100, 50, 200, 150],
      "points": [
        {
          "timestamp": 0,
          "x": 100,
          "y": 50,
          "pressure": 0.65,
          "tiltX": -5,
          "tiltY": 12,
          "twist": null,
          "pointerType": "pen",
          "pointerId": 1,
          "buttons": 1,
          "width": 2,
          "height": 2,
          "distance": 0,
          "speed": 0,
          "coalesced": false
        }
        // ... 더 많은 포인트들
      ]
    }
    // ... 더 많은 스트로크들
  ],
  "events": [
    {
      "timestamp": 0,
      "type": "session_start"
    },
    {
      "timestamp": 1234,
      "type": "stroke_start",
      "strokeId": 1,
      "tool": "pen"
    }
    // ... 더 많은 이벤트들
  ],
  "statistics": {
    "sessionDuration": 930123,
    "strokeCount": 25,
    "totalDistance": 3421.5,
    "averageStrokeLength": 136.9,
    "undoCount": 3,
    "redoCount": 1,
    "eraserCount": 2,
    "zoomCount": 5,
    "panCount": 8
  }
}
```

## 🧠 부정행위 탐지 활용 방안

### 분석 가능한 패턴

#### 1. **필기 자연스러움**
- 압력 변화의 자연스러움
- 속도 일관성
- 기울기 안정성
- 좌표 이동의 부드러움

#### 2. **행동 패턴**
- 사고 중단 시간 (스트로크 간 간격)
- Undo/Redo 사용 빈도
- 화면 조작 패턴
- 문제 이미지 참조 빈도

#### 3. **집중도 분석**
- 창 포커스 이탈 빈도
- 화면 확대/축소 패턴
- 작업 영역 이동 패턴

#### 4. **이상 징후**
- 비정상적으로 빠른 속도
- 일정한 압력/속도 (기계적 입력)
- 불규칙한 포커스 패턴
- 과도한 편집 행위

## 📈 모델 학습 고려사항

### 피처 엔지니어링
- 시계열 데이터 처리
- 통계적 특성 추출
- 패턴 인식을 위한 변환

### 라벨링 기준
- 정상 행위 vs 부정행위
- 집중도 레벨
- 난이도별 행동 패턴

### 데이터 증강
- 시간 축 변형
- 노이즈 추가
- 패턴 변형

## 🔧 기술 구현

### PointerEvent API 활용
```javascript
// 고정밀도 포인터 데이터 수집
const extractPointerData = (event) => {
  return {
    pressure: event.pressure,
    tiltX: event.tiltX,
    tiltY: event.tiltY,
    twist: event.twist,
    pointerType: event.pointerType,
    // Coalesced events 처리
    coalescedEvents: event.getCoalescedEvents?.() || []
  }
}
```

### 실시간 분석
- 스트로크별 즉시 통계 계산
- 이상 패턴 실시간 감지
- 메모리 효율적 데이터 관리

## 📝 사용법

1. **데이터 수집 시작**: 문제 풀이 시작과 함께 자동으로 수집 시작
2. **실시간 모니터링**: 툴바에서 수집 상태 확인
3. **데이터 다운로드**: "JSON 다운로드" 버튼 클릭
4. **분석 도구 연동**: 다운로드된 JSON을 분석 파이프라인에 입력

## 🔮 향후 확장 계획

- WebGL 기반 고성능 렌더링
- 음성 입력 패턴 분석
- 눈동자 추적 (WebRTC)
- 실시간 AI 분석 피드백