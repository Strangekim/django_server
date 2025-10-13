# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

부정행위 탐지를 위한 고정밀도 행동 데이터 수집 기능을 갖춘 수학 문제 풀이 애플리케이션입니다.

**시스템 구성:**
1. **Django 백엔드** - PostgreSQL 기반 REST API 서버
2. **Vue.js 프론트엔드** - 태블릿 최적화 메모 앱 (고정밀도 펜 입력 추적)
3. **데이터 수집** - 스트로크 데이터, 필압, 기울기, 행동 패턴 수집 (ML 모델 학습용)

## 데이터베이스 아키텍처

PostgreSQL의 커스텀 `questions` 스키마 사용:

- **questions.category** - 수학 단원 카테고리 (id, name)
- **questions.list** - 문제 정보 (OCR 처리된 본문, 선택지, 정답, 난이도, 이미지 URL)
- **sessions** - 사용자 세션 메타데이터 (기기/캔버스 정보, 집계 통계)
- **strokes** - 개별 펜 스트로크 (포인터 메타데이터, 바운딩 박스)
- **stroke_points** - 고정밀도 포인트 데이터 (좌표, 필압, 기울기, 회전, 타임스탬프)
- **events** - 사용자 상호작용 이벤트 (undo, redo, zoom, pan, 도구 변경)

**중요:** `questions` 스키마는 raw SQL 마이그레이션으로 관리됩니다. 모델은 `db_table = 'questions"."category'` 표기법을 사용합니다.

## 환경 설정

`.env` 파일 생성 필요 (환경 변수):

```bash
# Django
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DATABASE_URL=postgres://user:password@host:5432/dbname
ALLOWED_HOSTS=127.0.0.1,localhost

# AWS S3 (이미지 저장소)
AWS_S3_REGION_NAME=ap-northeast-2
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name

# Mathpix OCR API
MATHPIX_APP_ID=your-app-id
MATHPIX_APP_KEY=your-app-key

# OpenAI API
OPENAI_API_KEY=your-openai-api-key
```

## 주요 명령어

### 백엔드 (Django)

```bash
# Python 의존성 설치
pip install -r requirements.txt

# 데이터베이스 마이그레이션 실행
python manage.py migrate

# 관리자 계정 생성
python manage.py createsuperuser

# 개발 서버 실행 (포트 8000)
python manage.py runserver

# 프로덕션 서버 실행 (Gunicorn)
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# Django 관리자 페이지 접속
# http://127.0.0.1:8000/admin/
```

### 프론트엔드 (Vue.js)

```bash
cd frontend_memo_app

# Node.js 의존성 설치
npm install

# 개발 서버 실행 (포트 3000)
npm run dev

# 프로덕션 빌드 (dist/ 폴더에 출력)
npm run build

# Android 빌드 및 동기화
npm run android

# iOS 빌드 및 동기화
npm run ios
```

### 데이터베이스 작업

```bash
# PostgreSQL 접속
PGPASSWORD=secret psql -h 127.0.0.1 -U admin -d mydb

# 문제 조회 쿼리 예시
PGPASSWORD=secret psql -h 127.0.0.1 -U admin -d mydb -c "SELECT id, answer, choices FROM questions.list WHERE id = 11;"
```

### API 엔드포인트 테스트

```bash
# 헬스 체크
curl http://127.0.0.1:8000/api/health/

# 전체 문제 목록 조회 (카테고리별 그룹화)
curl http://127.0.0.1:8000/api/questions/

# 풀이 검증 (세션 데이터와 함께 POST)
curl -X POST http://127.0.0.1:8000/api/verify-solution/ \
  -H "Content-Type: application/json" \
  -d '{"question_id": 1, "user_answer": {...}, "session_data": {...}}'
```

## 핵심 API 엔드포인트

- `GET /api/health/` - 서버 상태 확인
- `GET /api/questions/` - 노출 설정된 전체 문제 목록 (카테고리별 그룹화)
- `GET /api/questions/<id>/` - 문제 상세 정보 (정답과 원본 이미지 제외)
- `POST /api/verify-solution/` - 답안 제출 (세션 데이터 포함), DB/S3 저장, OpenAI 검증
- `GET /problems/upload/` - 관리자 전용 문제 업로드 폼 (staff 로그인 필요)

## 시스템 아키텍처

### 세션 데이터 흐름

1. 프론트엔드가 고정밀도 스트로크 데이터 수집 (PointerEvent API 사용)
2. 답안 제출 시 `/api/verify-solution/`로 전송
3. 백엔드가 PostgreSQL에 저장 (sessions, strokes, stroke_points, events 테이블)
4. 원본 JSON을 gzip 압축하여 S3 업로드 (`answers/{problem_id}_{session_uuid}.json.gz`)
5. 정답인 경우, 화면에 보이는 스트로크를 Mathpix API로 텍스트 변환
6. OpenAI로 풀이 과정 검증 (gpt-5-nano, 구조화된 출력)

### 문제 업로드 흐름

1. 관리자가 `/problems/upload/`에서 이미지 업로드
2. Mathpix OCR로 문제 텍스트 추출
3. OpenAI로 데이터 구조화 (난이도, 선택지, 풀이 단계)
4. DB에 저장 (카테고리 FK 설정)
5. 원본 및 분리된 이미지를 S3에 업로드
6. S3 URL로 DB 업데이트

### 프론트엔드 아키텍처

- **Canvas 기반 드로잉** - PointerEvent API로 필압/기울기 감지
- **스트로크 추적** - coalesced events로 고주파수 데이터 수집
- **세션 통계** - 클라이언트 측에서 계산 (스트로크 수, 거리, 속도, 도구 변경)
- **Undo/Redo** - 히스토리 스냅샷 방식 (이벤트는 백엔드에 로깅)
- **가시 스트로크** - 지워진 내용 제외하고 Mathpix로 전송

## 구현 세부사항

### 선택지 형식

- 프론트엔드는 `selectedIndex` 전송 (0-based: 0, 1, 2, 3, 4)
- 백엔드는 1-based 문자열로 변환 ("1", "2", "3", "4", "5") 후 DB 비교
- `Question.answer`는 문자열로 저장 ("1"은 1번 선택지, "2"는 2번 선택지)

### 타임스탬프 형식

- 프론트엔드는 세션 시작 기준 상대 밀리초로 기록
- `StrokePoint.t_ms`는 스트로크 시작 기준 상대 시간 (포인트 타임스탬프 - 스트로크 시작 시간)
- 시계 동기화 문제 없이 정확한 시간 분석 가능

### Label 필드

- `Session.label`은 지도학습 지원: 0 (정상), 1 (치팅), null (미분류)
- verify-solution 요청에서 선택적 파라미터로 전송

### CORS 설정

- 개발 환경: `CORS_ALLOW_ALL_ORIGINS = True`
- 프로덕션: `CORS_ALLOWED_ORIGINS`에 특정 도메인 설정 필요

### 정적 파일

- Vue 빌드 출력: `frontend_memo_app/dist/`
- Django는 `STATICFILES_DIRS` 설정으로 서빙
- 루트 경로(`/`)는 Vue SPA (`index.html`) 서빙
- API 경로는 `/api/` 접두사로 충돌 방지

## 데이터 수집 시스템

### 수집하는 데이터

#### 1. 스트로크 데이터 (각 펜/지우개 스트로크마다)
- 기본 정보: 도구, 색상, 선 굵기, 시작/종료 시각
- 통계: 총 거리, 평균 속도, 평균 필압
- 바운딩 박스: [minX, minY, maxX, maxY]

#### 2. 포인트 데이터 (각 스트로크의 모든 포인트)
- 좌표: x, y (픽셀)
- 필압: 0.0-1.0 (지원 시)
- 기울기: tiltX, tiltY (-90 ~ 90도)
- 회전: twist (0-359도)
- 포인터 타입: pen, touch, mouse
- 접촉 영역: width, height

#### 3. 상호작용 이벤트
- 스트로크: stroke_start, stroke_end
- 도구 변경: tool_change, color_change, stroke_width_change
- 편집: undo, redo, clear_all
- 화면 조작: zoom_in/out, canvas_pan, image_drag
- 세션: session_start/end, window_focus/blur

#### 4. 세션 통계
- strokeCount, totalDistance, averageStrokeLength
- undoCount, redoCount, eraserCount
- zoomCount, panCount, toolChanges

### 개인정보 보호

- ✅ 개인 식별 정보 미수집
- ✅ 실제 답안 내용 미수집
- ✅ 랜덤 UUID 세션 ID 사용
- ✅ 상대 시간 기준 (절대 시간 아님)
- ✅ 로컬 처리, 선택적 다운로드

## 문제 처리 파이프라인 (mathpix.py)

### 기능
1. **Mathpix OCR** - 문제 이미지에서 텍스트 및 도표 추출
2. **OpenAI 구조화** - 추출된 텍스트를 JSON 형태로 구조화
3. **LaTeX 형식화** - 모든 수식을 LaTeX 형식 ($...$, $$...$$)으로 변환

### 처리 결과
- `problem`: 문제 본문 (번호, 배점 제거, 수식 LaTeX 형식)
- `choices`: 선택지 배열 (보기 기호 제거, 수식 LaTeX 형식)
- `difficulty`: 난이도 (1-100)
- `solution_steps`: 풀이 단계 배열 (각 단계는 {"step_number", "description"})
- `seperate_img`: 분리된 도표 이미지 (PNG 바이트)

### 명령줄 사용
```bash
python mathpix.py "문제이름" "이미지경로"
```

## OpenAI API 사용

### 문제 구조화 (mathpix.py)
- 모델: `gpt-5-nano`
- 방식: `responses.parse` (구조화된 출력)
- 스키마: `ProblemData` (Pydantic)
- 목적: OCR 텍스트를 JSON 형태로 변환

### 풀이 검증 (api/views.py)
- 모델: `gpt-5-nano`
- 방식: `responses.parse` (구조화된 출력)
- 스키마: `SolutionVerification` (Pydantic)
- 평가 항목:
  - logic_score: 논리성 (0-100)
  - accuracy_score: 정확성 (0-100)
  - process_score: 풀이 과정 (0-100)
  - total_score: 총점 (가중평균: 40% + 40% + 20%)
  - is_correct: 정답 여부 (total_score >= 60)
  - comment: 전반적 평가
  - detailed_feedback: 단계별 피드백

## 배포 관련

- `django-environ`으로 환경 변수 관리
- PostgreSQL 필수 (ArrayField, 스키마 네임스페이스 사용)
- S3 버킷은 문제 이미지에 대해 public read 권한 필요
- 프로덕션 WSGI 서버는 Gunicorn 권장
- 프론트엔드는 Capacitor로 모바일 앱 빌드 가능 (Android/iOS)

## 주의사항

### 정답 검증 로직
- 오답인 경우 Mathpix/OpenAI 검증 스킵 (즉시 응답 반환)
- 정답이면서 스트로크 데이터가 있는 경우에만 풀이 검증 수행

### 가시 스트로크 vs 전체 스트로크
- DB에는 **전체 스트로크** 저장 (지워진 것 포함)
- Mathpix로는 **가시 스트로크**만 전송 (visibleStrokes 필드 우선, 없으면 전체 사용)

### 마이그레이션
- `questions` 스키마는 0001 마이그레이션에서 생성
- 모델의 `db_table`은 스키마 포함 형식: `'questions"."category'`

### 에러 처리
- S3 업로드 실패 시 DB 레코드 롤백
- Mathpix/OpenAI 실패 시에도 세션 데이터는 DB/S3에 저장 유지

## GitHub Issue 자동화

### 커밋 메시지 규칙

코드 수정 후 특정 키워드로 커밋하면 GitHub issue가 자동 생성됩니다:

- **`[issue]`** - 일반 issue 생성 (라벨: `auto-generated`)
- **`[bug]`** - 버그 issue 생성 (라벨: `bug`, `auto-generated`)
- **`[fix]`** - 수정 issue 생성 (라벨: `fix`, `auto-generated`)

예시:
```bash
git commit -m "[bug] API 응답에서 null 값 처리 안 됨"
git commit -m "[fix] 세션 타임스탬프 계산 로직 수정"
git commit -m "[issue] 프론트엔드 성능 최적화 필요"
```

### Issue 생성 조건

다음 상황에서 Claude Code는 issue 생성을 제안하거나 자동으로 생성해야 합니다:

1. **버그 수정**
   - 예상치 못한 동작 발견
   - 에러 처리 추가
   - 데이터 검증 로직 수정

2. **중요한 기능 변경**
   - API 엔드포인트 추가/수정
   - 데이터베이스 스키마 변경
   - 핵심 비즈니스 로직 수정

3. **아키텍처 변경**
   - 새로운 의존성 추가
   - 설정 파일 변경
   - 배포 관련 수정

4. **문제 상황 발견**
   - 보안 취약점
   - 성능 이슈
   - 확장성 문제

### Issue에 포함되는 내용

자동 생성되는 issue에는 다음 정보가 포함됩니다:

- 커밋 해시 및 날짜
- 커밋 메시지 전체
- 변경된 파일 목록
- 코드 변경 내용 (diff)
- 관련 라벨

### 수동으로 Issue 생성

필요한 경우 수동으로 issue를 생성할 수 있습니다:

```bash
# Python 스크립트 직접 실행
python scripts/auto_issue.py

# 또는 특정 커밋에 대해 실행
python scripts/auto_issue.py <commit-hash>
```

### 환경 변수 설정

`.env` 파일에 GitHub 관련 변수를 추가해야 합니다:

```bash
# GitHub Issue 자동화
GITHUB_TOKEN=ghp_your_github_personal_access_token
GITHUB_REPO_OWNER=your-github-username
GITHUB_REPO_NAME=django_server
```

**GitHub Token 생성 방법:**
1. GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token" 클릭
3. `repo` 권한 체크
4. 생성된 토큰을 `.env` 파일에 추가

### Claude Code의 역할

Claude Code는 다음과 같이 동작합니다:

1. **작업 완료 후 제안**
   - 중요한 수정 완료 시 "GitHub issue를 생성하시겠습니까?" 제안
   - 적절한 커밋 메시지 형식 제시

2. **커밋 메시지 작성**
   - 버그 수정 시 자동으로 `[bug]` 접두사 추가
   - 기능 추가 시 `[issue]` 접두사 추가
   - 수정 작업 시 `[fix]` 접두사 추가

3. **Issue 내용 제안**
   - 문제 상황 명확히 설명
   - 해결 방법 상세히 기술
   - 영향 받는 컴포넌트 명시
