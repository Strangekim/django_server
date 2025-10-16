# Math Cheating Detection System

<div align="center">

**AI 기반 부정행위 탐지를 위한 고정밀도 행동 데이터 수집 시스템**

[![Django](https://img.shields.io/badge/Django-5.2.6-092E20?style=flat&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.4-4FC08D?style=flat&logo=vue.js&logoColor=white)](https://vuejs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5--nano-412991?style=flat&logo=openai&logoColor=white)](https://openai.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Features](#-주요-기능) • [Tech Stack](#-기술-스택) • [Architecture](#-시스템-아키텍처) • [Installation](#-설치-및-실행) • [API Docs](#-api-문서) • [Demo](#-데모)

</div>

---

## 📌 프로젝트 개요

**교육 평가의 공정성을 지키는 AI 기반 부정행위 탐지 시스템**

온라인 시험 환경에서 학생들의 문제 풀이 과정을 **고정밀도로 추적·분석**하여, 부정행위 패턴을 자동으로 탐지하는 통합 솔루션입니다. 단순한 답안 제출 시스템을 넘어, **펜 입력 궤적, 필압, 기울기, 행동 패턴**까지 수집하여 ML 모델 학습을 위한 데이터를 생성합니다.

### 🎯 핵심 가치

- **📊 고정밀도 데이터 수집** - PointerEvent API를 활용한 밀리초 단위 스트로크 추적
- **🤖 AI 기반 풀이 검증** - Mathpix OCR + OpenAI로 필기 내용을 자동 채점
- **🔍 행동 패턴 분석** - 취소, 수정, 도구 변경 등 미시적 행동 로깅
- **🛡️ 개인정보 보호** - 실제 답안 내용 미수집, 익명화된 행동 데이터만 저장
- **🚀 확장 가능한 설계** - PostgreSQL 파티셔닝 지원, S3 기반 백업 아키텍처

---

## ✨ 주요 기능

### 1. 태블릿 최적화 메모 앱 (Vue.js + Capacitor)

<table>
<tr>
<td width="50%">

#### 🖊️ 고정밀도 펜 입력
- **PointerEvent API** 기반 필압/기울기/회전 감지
- **Coalesced Events** 처리로 고주파수 데이터 수집
- **Apple Pencil / S-Pen** 완벽 지원

</td>
<td width="50%">

#### 🎨 직관적인 드로잉 툴
- 펜/지우개 도구 (색상, 굵기 커스터마이징)
- 무한 Undo/Redo 히스토리
- Zoom/Pan 제스처 지원

</td>
</tr>
<tr>
<td width="50%">

#### 📐 수학 수식 렌더링
- **MathJax 3.2** 기반 LaTeX 렌더링
- 문제 이미지와 선택지 동기화
- 반응형 레이아웃 (모바일/태블릿 대응)

</td>
<td width="50%">

#### 📡 실시간 세션 추적
- 클라이언트 측 통계 계산 (스트로크 수, 거리, 속도)
- 이벤트 타임라인 자동 생성
- 백그라운드 진입/복귀 감지

</td>
</tr>
</table>

### 2. Django REST API 백엔드

#### 🗄️ 정교한 데이터베이스 설계

```
PostgreSQL Custom Schema (questions)
├── questions.category      # 수학 단원 카테고리
├── questions.list          # 문제 정보 (OCR 처리된 본문, 선택지, 정답)
├── sessions                # 세션 메타데이터 + 요약 통계 (집계 캐시)
├── strokes                 # 스트로크 메타 (도구, 색상, bbox, 평균 필압)
├── stroke_points           # 고정밀도 포인트 (좌표, 필압, 기울기, 타임스탬프)
└── events                  # 사용자 상호작용 이벤트 (undo, redo, zoom, tool_change)
```

**설계 철학:**
- **시계열 분석 최적화** - 상대 시간 기준 (밀리초 단위)으로 시계 동기화 문제 해결
- **대용량 처리** - `stroke_points` 테이블 파티셔닝 권장 (월/수집일 기준)
- **복합 인덱싱** - `(session, stroke, idx)`, `(session, ts_ms)` 복합 키로 쿼리 성능 최적화

#### 🧠 AI 기반 풀이 검증 파이프라인

```mermaid
graph LR
    A[사용자 답안 제출] --> B{정답 여부 확인}
    B -->|오답| C[즉시 응답 반환]
    B -->|정답| D[PostgreSQL 저장]
    D --> E[S3 원본 JSON 백업]
    E --> F[Mathpix OCR]
    F --> G[OpenAI 풀이 검증]
    G --> H[검증 결과 반환]
```

**검증 메트릭:**
- **logic_score** (40%) - 논리적 사고 과정의 타당성
- **accuracy_score** (40%) - 계산 및 개념 정확도
- **process_score** (20%) - 문제 해결 절차의 체계성
- **is_correct** - 총점 60점 이상 시 합격 판정

#### 📤 자동화된 문제 업로드 시스템

```python
# mathpix.py - 문제 이미지 → 구조화된 데이터
이미지 업로드 → Mathpix OCR → OpenAI 구조화 → DB 저장 → S3 업로드
```

**출력 형식:**
```json
{
  "problem": "함수 $f(x) = x^2 + 3x + 2$의 극값을 구하시오.",
  "choices": ["$x = -\\frac{3}{2}$", "$x = 0$", "$x = 1$", "$x = 2$", "$x = 3$"],
  "difficulty": 65,
  "solution_steps": [
    {"step_number": 1, "description": "$f'(x) = 2x + 3$를 계산한다."},
    {"step_number": 2, "description": "$f'(x) = 0$을 만족하는 $x = -\\frac{3}{2}$를 구한다."}
  ]
}
```

---

## 🛠 기술 스택

### Backend
- **Django 5.2.6** - REST API 프레임워크
- **PostgreSQL 15+** - ArrayField, 스키마 네임스페이스, 파티셔닝 지원
- **Gunicorn 23.0** - WSGI 프로덕션 서버
- **django-storages** + **boto3** - AWS S3 통합
- **Pydantic 2.11** - 구조화된 데이터 검증

### Frontend
- **Vue.js 3.4** - Composition API 기반 SPA
- **Pinia 2.1** - 상태 관리
- **Vite 5.0** - 빌드 도구
- **Capacitor 7.4** - 네이티브 앱 컨테이너 (Android/iOS)
- **MathJax 3.2** - 수식 렌더링 엔진

### AI/ML
- **OpenAI GPT-5-nano** - 문제 구조화 + 풀이 검증
- **Mathpix OCR API** - 필기 인식 (LaTeX 변환)

### Infrastructure
- **AWS S3** - 이미지 저장소 (CloudFront 연동 가능)
- **PostgreSQL Custom Schema** - 논리적 데이터 분리
- **GitHub Actions** - CI/CD 자동화 (issue 생성 워크플로우)

---

## 🏗 시스템 아키텍처

### 전체 구조도

```
┌──────────────────────────────────────────────────────────────┐
│                      Client Layer                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Vue.js SPA (Capacitor)                              │   │
│  │  - Canvas Drawing (PointerEvent API)                 │   │
│  │  - Real-time Session Tracking                        │   │
│  │  - MathJax Rendering                                 │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                           │ HTTPS (REST API)
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                      API Layer                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Django REST Framework                               │   │
│  │  - /api/questions/          (GET)                    │   │
│  │  - /api/verify-solution/    (POST)                   │   │
│  │  - /problems/upload/        (Admin)                  │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  PostgreSQL     │  │  AWS S3         │  │  OpenAI API     │
│  - sessions     │  │  - images/      │  │  - GPT-5-nano   │
│  - strokes      │  │  - answers/     │  │  - Mathpix OCR  │
│  - events       │  │                 │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 데이터 수집 파이프라인

```
PointerEvent → Canvas Capture → Session Store (Pinia)
                                      │
                                      ▼
                        ┌─────────────────────────┐
                        │ Submit Button Click     │
                        └─────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────┐
                        │ /api/verify-solution/   │
                        │ - sessionData           │
                        │ - strokes[]             │
                        │ - events[]              │
                        │ - visibleStrokes[]      │
                        └─────────────────────────┘
                                      │
                ┌─────────────────────┼─────────────────────┐
                ▼                     ▼                     ▼
        ┌───────────────┐   ┌──────────────┐   ┌──────────────┐
        │ PostgreSQL    │   │ S3 Backup    │   │ AI Verify    │
        │ (Relational)  │   │ (JSON.gz)    │   │ (Optional)   │
        └───────────────┘   └──────────────┘   └──────────────┘
```

### 수집 데이터 구조

#### 1. 세션 메타데이터
```javascript
{
  session_uuid: "550e8400-e29b-41d4-a716-446655440000",
  duration_ms: 125340,
  problem_id: 42,
  category: 3,

  // 기기 정보
  user_agent: "Mozilla/5.0 ...",
  platform: "Android",
  pixel_ratio: 2.625,
  screen_width: 1080,
  screen_height: 2400,

  // 요약 통계
  stroke_count: 47,
  total_distance_px: 3245.67,
  undo_count: 3,
  tool_change_count: 5
}
```

#### 2. 스트로크 데이터 (각 펜/지우개 획)
```javascript
{
  stroke_uuid: "...",
  tool: "pen",
  color: "#000000",
  stroke_width: 2,
  start_ms: 1234,
  end_ms: 1567,

  // 입력 기기
  pointer_type: "pen",  // 'pen' | 'touch' | 'mouse'

  // 통계
  total_distance_px: 123.45,
  average_speed_pxps: 67.8,
  average_pressure: 0.65,

  // 바운딩 박스
  bbox: [100, 200, 350, 450]
}
```

#### 3. 포인트 데이터 (각 스트로크의 모든 점)
```javascript
{
  idx: 0,
  t_ms: 0,              // 스트로크 시작 기준 상대 시간
  x: 150,
  y: 250,
  pressure: 0.68,       // 0.0 ~ 1.0
  tilt_x: -15,          // -90 ~ 90 (도)
  tilt_y: 5,
  twist: 0,             // 0 ~ 359 (도)
  pointer_type: "pen",
  width: 12,            // 접촉 영역 크기
  height: 12
}
```

#### 4. 이벤트 로그
```javascript
[
  { ts_ms: 0, type: "session_start", details: {} },
  { ts_ms: 1234, type: "stroke_start", details: { stroke_uuid: "..." } },
  { ts_ms: 5678, type: "tool_change", details: { from: "pen", to: "eraser" } },
  { ts_ms: 12340, type: "undo", details: { stroke_uuid: "..." } },
  { ts_ms: 15600, type: "zoom_in", details: { from: 1.0, to: 1.5 } },
  { ts_ms: 125340, type: "session_end", details: {} }
]
```

---

## 🚀 설치 및 실행

### 사전 요구사항

- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 15+**
- **AWS S3 버킷** (문제 이미지 저장용)
- **API Keys** (Mathpix, OpenAI)

### 1. 환경 변수 설정

프로젝트 루트에 `.env` 파일 생성:

```bash
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DATABASE_URL=postgres://admin:secret@127.0.0.1:5432/mydb
ALLOWED_HOSTS=127.0.0.1,localhost

# AWS S3
AWS_S3_REGION_NAME=ap-northeast-2
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name

# Mathpix OCR
MATHPIX_APP_ID=your-mathpix-app-id
MATHPIX_APP_KEY=your-mathpix-app-key

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# GitHub Issue Automation (Optional)
GITHUB_TOKEN=ghp_your_github_token
GITHUB_REPO_OWNER=your-username
GITHUB_REPO_NAME=django_server
```

### 2. 백엔드 설정

```bash
# Python 의존성 설치
pip install -r requirements.txt

# 데이터베이스 마이그레이션
python manage.py migrate

# 관리자 계정 생성
python manage.py createsuperuser

# 개발 서버 실행 (http://127.0.0.1:8000)
python manage.py runserver
```

### 3. 프론트엔드 설정

```bash
cd frontend_memo_app

# Node.js 의존성 설치
npm install

# 개발 서버 실행 (http://localhost:3000)
npm run dev

# 프로덕션 빌드
npm run build

# Android 앱 빌드 (Android Studio 필요)
npm run android

# iOS 앱 빌드 (Xcode 필요, macOS only)
npm run ios
```

### 4. PostgreSQL 초기 데이터

```bash
# 데이터베이스 접속
PGPASSWORD=secret psql -h 127.0.0.1 -U admin -d mydb

# 카테고리 추가 예시
INSERT INTO questions.category (name) VALUES
  ('미적분학'),
  ('확률과 통계'),
  ('기하학');

# 문제 조회
SELECT id, answer, choices FROM questions.list WHERE id = 11;
```

---

## 📚 API 문서

### 엔드포인트 개요

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/health/` | 서버 상태 확인 | ❌ |
| `GET` | `/api/questions/` | 전체 문제 목록 (카테고리별 그룹화) | ❌ |
| `GET` | `/api/questions/<id>/` | 문제 상세 정보 (정답 제외) | ❌ |
| `POST` | `/api/verify-solution/` | 답안 제출 + 세션 데이터 저장 | ❌ |
| `GET` | `/problems/upload/` | 문제 업로드 폼 (관리자 전용) | ✅ |

### API 상세

#### 1. 문제 목록 조회

```bash
curl http://127.0.0.1:8000/api/questions/
```

**Response:**
```json
{
  "1": [  // category_id
    {
      "id": 1,
      "name": "미적분-극한-001",
      "problem": "함수 $f(x)=\\frac{x^2-4}{x-2}$의 $x \\to 2$일 때의 극한값은?",
      "choices": [
        "$0$",
        "$2$",
        "$4$",
        "$\\infty$",
        "극한값이 존재하지 않는다"
      ],
      "difficulty": 45,
      "category": 1,
      "original_img": "https://s3.amazonaws.com/bucket/images/problem1.jpg",
      "separate_img": null
    }
  ],
  "2": [...]
}
```

#### 2. 답안 제출 및 검증

```bash
curl -X POST http://127.0.0.1:8000/api/verify-solution/ \
  -H "Content-Type: application/json" \
  -d '{
    "question_id": 1,
    "user_answer": {
      "selectedIndex": 2
    },
    "session_data": {
      "sessionUuid": "550e8400-e29b-41d4-a716-446655440000",
      "startTime": "2025-10-16T10:30:00Z",
      "endTime": "2025-10-16T10:35:00Z",
      "durationMs": 300000,
      "problemId": 1,
      "category": 1,
      "device": {
        "userAgent": "...",
        "platform": "Android",
        "pixelRatio": 2.625
      },
      "canvas": {
        "logicalWidth": 800,
        "logicalHeight": 600
      },
      "statistics": {
        "strokeCount": 25,
        "totalDistance": 1234.56,
        "undoCount": 2
      },
      "strokes": [...],
      "events": [...],
      "visibleStrokes": [...]
    }
  }'
```

**Response (정답 + 풀이 데이터 있음):**
```json
{
  "is_correct": true,
  "correct_answer": "3",
  "user_answer": "3",
  "session_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "s3_url": "https://s3.amazonaws.com/bucket/answers/1_550e8400.json.gz",
  "verification": {
    "logic_score": 85,
    "accuracy_score": 90,
    "process_score": 80,
    "total_score": 86.0,
    "is_correct": true,
    "comment": "논리적이고 정확한 풀이입니다.",
    "detailed_feedback": [
      {
        "step": 1,
        "feedback": "극한의 정의를 올바르게 적용했습니다.",
        "score": 95
      }
    ]
  }
}
```

**Response (오답):**
```json
{
  "is_correct": false,
  "correct_answer": "3",
  "user_answer": "1",
  "session_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "s3_url": "https://s3.amazonaws.com/bucket/answers/1_550e8400.json.gz",
  "verification": null
}
```

#### 3. 문제 업로드 (관리자 전용)

Django 관리자 로그인 필요 → `/problems/upload/` 접속

**처리 흐름:**
1. 이미지 업로드 (JPEG/PNG)
2. Mathpix OCR로 텍스트 추출
3. OpenAI로 데이터 구조화 (난이도, 선택지, 풀이 단계)
4. PostgreSQL 저장
5. S3에 원본 + 분리 이미지 업로드
6. DB에 S3 URL 업데이트

---

## 🔍 핵심 구현 디테일

### 1. 타임스탬프 설계 철학

**문제:** 클라이언트와 서버의 시계가 다를 수 있음

**해결책:** 상대 시간 기준 사용

```javascript
// Frontend - 세션 시작 시각을 기준으로 저장
const sessionStartTime = Date.now();

// 스트로크 시작
const strokeStartTime = Date.now() - sessionStartTime; // 예: 1234ms

// 포인트 기록 (스트로크 시작 기준)
const point = {
  t_ms: Date.now() - strokeStartTime  // 예: 567ms
};
```

**장점:**
- 시계 동기화 불필요
- 정확한 상대적 시간 분석 가능
- 타임존 문제 없음

### 2. 선택지 형식 통일

**문제:** 프론트엔드는 0-based index, 백엔드는 1-based string

**해결책:**
```python
# api/views.py
def verify_solution(request):
    selected_index = request.data['user_answer']['selectedIndex']
    user_answer_str = str(selected_index + 1)  # 0→"1", 1→"2", ...

    correct_answer = question.answer  # DB에 "1", "2", ... 로 저장됨
    is_correct = (user_answer_str == correct_answer)
```

### 3. 가시 스트로크 vs 전체 스트로크

**개인정보 보호 전략:**

```javascript
// Frontend
const sessionData = {
  strokes: [...],           // 지워진 것 포함 (DB 저장용)
  visibleStrokes: [...]     // 화면에 보이는 것만 (Mathpix 전송용)
};
```

```python
# Backend
# DB에는 전체 스트로크 저장
for stroke in session_data.get('strokes', []):
    Stroke.objects.create(...)

# Mathpix로는 가시 스트로크만 전송
visible_strokes = session_data.get('visibleStrokes', session_data.get('strokes', []))
mathpix_result = send_to_mathpix(visible_strokes)
```

### 4. S3 업로드 실패 처리

**트랜잭션 보장:**
```python
from django.db import transaction

@transaction.atomic
def save_session_to_s3(session_uuid, data):
    # 1. DB 저장
    session = Session.objects.create(...)

    # 2. S3 업로드
    try:
        s3_url = upload_to_s3(data)
    except Exception as e:
        # 롤백 트리거
        raise Exception(f"S3 upload failed: {e}")

    return session, s3_url
```

---

## 🧪 테스트

### API 테스트

```bash
# 헬스 체크
curl http://127.0.0.1:8000/api/health/

# 문제 목록 조회
curl http://127.0.0.1:8000/api/questions/

# 특정 문제 조회
curl http://127.0.0.1:8000/api/questions/1/

# 답안 제출 (테스트 데이터)
curl -X POST http://127.0.0.1:8000/api/verify-solution/ \
  -H "Content-Type: application/json" \
  -d @test_session.json
```

### 프론트엔드 테스트

```bash
cd frontend_memo_app

# 린트 실행
npm run lint

# 타입스크립트 체크
npx tsc --noEmit

# 빌드 검증
npm run build
```

---

## 📊 데이터 분석 예시

### SQL 쿼리 샘플

#### 1. 문제별 평균 풀이 시간
```sql
SELECT
  problem_id,
  AVG(duration_ms / 1000.0) AS avg_duration_sec,
  COUNT(*) AS attempt_count
FROM sessions
GROUP BY problem_id
ORDER BY avg_duration_sec DESC;
```

#### 2. 부정행위 의심 세션 탐지 (휴리스틱)
```sql
SELECT
  session_uuid,
  problem_id,
  stroke_count,
  undo_count,
  duration_ms
FROM sessions
WHERE
  stroke_count < 5          -- 스트로크가 너무 적음
  AND duration_ms < 30000   -- 30초 미만으로 풀이
  AND is_correct = TRUE;    -- 정답 맞춤
```

#### 3. 스트로크 궤적 재구성
```sql
SELECT
  sp.stroke_id,
  sp.idx,
  sp.x,
  sp.y,
  sp.pressure,
  sp.t_ms
FROM stroke_points sp
JOIN strokes s ON sp.stroke_id = s.stroke_uuid
WHERE s.session_id = '550e8400-e29b-41d4-a716-446655440000'
ORDER BY s.start_ms, sp.idx;
```

---

## 🎬 데모

### 프론트엔드 화면

```
┌──────────────────────────────────────────────────────────┐
│  [← Back]                     문제 1/20             [⚙] │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  문제: 함수 f(x) = x² + 3x + 2의 극값을 구하시오.      │
│                                                          │
│  [이미지: 그래프]                                        │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │                                                  │  │
│  │      [필기 영역 - Canvas]                        │  │
│  │                                                  │  │
│  │                                                  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  선택지:                                                 │
│  ○ 1. x = -3/2                                          │
│  ○ 2. x = 0                                              │
│  ○ 3. x = 1                                              │
│  ○ 4. x = 2                                              │
│  ○ 5. x = 3                                              │
│                                                          │
│  [🖊 펜] [🧹 지우개] [↶ Undo] [↷ Redo] [🔍 Zoom]      │
│                                                          │
│              [제출하기]                                  │
└──────────────────────────────────────────────────────────┘
```

### 관리자 대시보드

Django Admin에서 확인 가능:
- 문제 관리 (`/admin/core/question/`)
- 세션 데이터 조회 (`/admin/api/session/`)
- 실시간 통계 확인

---

## 🔒 보안 및 개인정보 보호

### 수집하지 않는 정보
- ❌ 실제 필기 내용 (이미지/텍스트)
- ❌ 개인 식별 정보 (이름, 학번, IP 주소)
- ❌ 절대 시간 (시계 동기화 문제 회피)

### 수집하는 정보
- ✅ 스트로크 궤적 (좌표, 속도, 필압)
- ✅ 행동 패턴 (undo/redo 횟수, 도구 변경)
- ✅ 세션 요약 통계 (집계값만)
- ✅ 랜덤 UUID (세션 식별)

### CORS 설정
```python
# config/settings.py
CORS_ALLOW_ALL_ORIGINS = True  # 개발 환경

# 프로덕션 환경
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://app.yourdomain.com",
]
```

---

## 📦 배포

### Gunicorn (프로덕션)

```bash
# 서버 시작
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4

# 또는 deploy.sh 사용
chmod +x deploy.sh
./deploy.sh
```

### Docker Compose

```bash
# 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f django

# 서비스 중지
docker-compose down
```

### 정적 파일 서빙

```python
# config/settings.py
STATICFILES_DIRS = [
    BASE_DIR / "frontend_memo_app" / "dist"
]

# Vue 빌드 후 Django가 자동으로 서빙
# / → index.html (SPA)
# /api/* → Django REST API
```

---

## 🤝 기여 가이드

### GitHub Issue 자동화

커밋 메시지에 특정 키워드를 포함하면 자동으로 issue가 생성됩니다:

```bash
# 버그 수정
git commit -m "[bug] API 응답에서 null 값 처리 안 됨"

# 기능 추가/수정
git commit -m "[fix] 세션 타임스탬프 계산 로직 수정"

# 일반 이슈
git commit -m "[issue] 프론트엔드 성능 최적화 필요"
```

### 개발 워크플로우

1. Feature 브랜치 생성
2. 코드 작성 및 테스트
3. 커밋 (키워드 포함)
4. PR 생성
5. 자동 issue 생성 확인
6. 코드 리뷰 후 머지

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 📞 문의

프로젝트 관련 문의사항은 GitHub Issues를 이용해주세요.

**주요 문서:**
- [DEPLOYMENT.md](DEPLOYMENT.md) - 배포 가이드
- [CLAUDE.md](CLAUDE.md) - Claude Code 사용 가이드
- [frontend_memo_app/DATA_COLLECTION.md](frontend_memo_app/DATA_COLLECTION.md) - 데이터 수집 상세

---

<div align="center">

**Built with ❤️ for Educational Integrity**

</div>
