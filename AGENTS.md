# 문서 요약
- 이 문서는 저장소 내 주요 Markdown 파일의 핵심을 빠르게 훑어보기 위한 요약본입니다.
- 최신 절차나 설정 값은 반드시 각 원본 문서와 소스 코드를 함께 확인해 주세요.

## 공통 운영 지침 (기존 AGENTS.md)
- 디렉터리 역할: `config/`는 전역 설정과 엔트리포인트, `core/`는 공용 도메인 로직, `api/`는 외부 연동 API 뷰, `frontend_memo_app/`는 Vite 기반 Vue 프런트엔드 소스를 담당하며 배포 스크립트는 루트의 `deploy.sh`, `docker-compose.yml`, `DEPLOYMENT.md`에 정리되어 있음.
- 기본 명령: Django 개발 서버는 `python manage.py runserver 0.0.0.0:8000`, 테스트는 `python manage.py test`, 프런트엔드 개발은 `cd frontend_memo_app && npm install && npm run dev`, 배포는 `./deploy.sh`.
- 코딩 규칙: Python은 PEP 8과 4칸 들여쓰기, 가능하면 타입 힌트 사용; Django 모델은 단수 명사, 매니저·서비스 함수는 동사구; Vue 컴포넌트는 파스칼 표기, 상태 변수는 카멜 표기; 프런트엔드는 ESLint(`npm run lint`)로 정렬.
- 테스트 전략: 신규 기능은 최소 한 개의 Django 테스트를 추가하고 외부 호출은 `@patch`로 모킹; API 통합 테스트는 `api/tests.py`에서 `TestCase` 확장; 프런트엔드는 자동 테스트 스크립트가 없으므로 중요 기능은 Cypress/Vitest 제안 또는 수동 시나리오 기록; 핵심 업무 흐름 커버리지는 70% 이상을 목표로 함.
- 협업 규칙: 커밋 프리픽스는 소문자(`fix:`, `create:` 등), 메시지는 1줄 요약 후 필요 시 한글 상세; PR에는 목적, 영향 범위, 테스트 결과(`python manage.py test`)를 포함하고 UI·API 변경 시 스크린샷/예시와 이슈 번호(`#123`)를 첨부.
- 보안: 비밀 키·외부 토큰은 `.env`나 환경 변수로 관리하며 설정 파일에 커밋하지 않음; 로컬 개발 시 `frontend_memo_app/.env.development`를 복제하되 민감 정보는 비워두고 개인 키를 입력; S3 관련 장애는 `S3_ISSUE_ANALYSIS.md` 우선 확인; 배포 시 `ALLOWED_HOSTS`와 `DEPLOYMENT.md`를 함께 갱신.

## 파일별 핵심 정리

### README.md
- 프로젝트명만 소개하는 최소한의 안내문이며 상세 워크플로우는 다른 문서를 참고해야 함.

### DEPLOYMENT.md
- 초기 EC2 세팅: 가상환경 생성·활성화, `pip install -r requirements.txt`, Node.js 18 설치 방법, Gunicorn systemd 서비스와 Nginx 리버스 프록시 설정 절차를 단계별로 제공.
- 개발 환경: 프런트엔드(`npm install`, `npm run dev`)와 Django(`python manage.py runserver`) 개발 서버 구동 절차, 기본 포트(3000/8000) 안내.
- 프로덕션 빌드: `npm run build` 후 `./verify-build.sh`로 정적 자산 검사, `python manage.py collectstatic --noinput` 실행, Git 푸시 전 점검 사항을 요약.
- 배포 전략: 자동화 스크립트(`./deploy.sh`) 사용법과 수동 배포 체크리스트(코드 갱신, 의존성 설치, 프런트 빌드, 정적 파일 수집, 마이그레이션, Gunicorn·Nginx 재시작)를 비교 정리.
- 트러블슈팅: pip `externally-managed-environment` 오류, 정적 파일 404, Vite 자산 경로 오류, API 응답 실패, Gunicorn 재시작 실패 등 대표 장애와 해결 절차를 정리.
- 운영 체크리스트: 배포 전·후 점검 항목, 서비스 상태·로그·파일 권한·디스크 사용량 확인 명령과 venv 활성화·collectstatic·서비스 재시작·로그 모니터링 등 반복 실수 방지 팁을 제공.

### S3_ISSUE_ANALYSIS.md
- 문제 요약: `AWS_S3_REGION_NAME`과 `AWS_REGION` 변수 불일치로 세션 데이터 업로드가 실패하지만 API는 성공(200) 응답을 반환해 장애가 은폐되던 상황.
- 세부 분석: 예외를 광범위하게 처리하며 콘솔 로그만 남겨 문제 파악이 지연; S3 디렉터리 구조(`questions/`, `answers/`)와 장애 로그 패턴을 정리.
- 진단 방법: EC2 `.env`에서 AWS 관련 키 확인, Gunicorn 로그에서 오류 grep, S3 버킷 권한과 실제 객체 존재 여부 점검.
- 권장 조치: 환경 변수 명 통일, 로그 모니터링 강화, `manage.py shell`로 실시간 환경 변수 확인 등 후속 개선을 제안.

### .claude_instructions.md
- 작업 원칙: 백엔드 데이터 무결성을 우선 검증하고 문제 원인을 명확히 한 뒤 수정, 모든 주석·문서·식별자에 한국어 사용(기술 용어는 예외 허용).
- 업무 흐름: 요구 파악 → 관련 코드 분석 → 원인·해결 방안 정리 및 공유 → 필요 시 사용자 확인 → 수정 → 영향 범위 점검 → 결과 보고 순서를 권장.
- 주의 영역: Canvas 렌더링, 히스토리(Undo/Redo) 로직, API 전송 구조를 변경할 때 상태 변수(`historyIndex` 등) 일관성을 유지해야 함.
- 금지 사항: 백엔드 데이터 구조 무분별 변경, 히스토리 로직 삭제, 영문 주석 사용, 원인 확인 전 선제 수정, 근거 없는 추측 진행.
- Todo 사용 규칙: 3단계 이상 복잡한 작업은 Todo로 계획을 공유하고 단계 완료 시 즉시 상태를 업데이트.

### api/README.md
- 디렉터리 구성: `views.py`, `urls.py`가 중심이며 REST API 엔드포인트를 제공함.
- 제공 엔드포인트: `GET /api/health/`(서비스 상태)와 `GET /api/questions/`(카테고리별 문제 목록) 응답 구조 예시를 포함.
- 설정 가이드: 개발 환경은 CORS 전체 허용, 프로덕션은 허용 도메인 제한; `config/urls.py`에 `api/` 네임스페이스를 포함해야 함.
- 활용 예시: cURL, Fetch API 예제로 클라이언트 호출 방법을 설명.
- 확장 지침: 문제 상세 조회 API 추가 예시와 보안 고려 사항(CSRF, CORS, 인증 전략)을 제안.

### frontend_memo_app/README.md
- 앱 개요: 부정행위 탐지를 위한 수학 문제 풀이 데이터 수집용 Vue 3/Vite 웹앱으로 고정밀 입력 처리와 행동 패턴 분석 기능을 제공.
- 주요 기능: 펜·지우개·캔버스 이동 등 도구 제공, 압력·기울기·트위스트·coalesced events 수집, Undo/Redo·줌/팬 지원, 실시간 분석 패널과 JSON 내보내기 지원.
- 기술 스택 및 명령어: Vue 3 Composition API, PointerEvent, HTML5 Canvas, Vite, Capacitor; `npm install`, `npm run dev`, `npm run build`, `npm run lint`, `npm run android`, `npm run ios`.
- 지원 환경: Chrome/Edge 권장, Safari는 압력 지원 제한, Firefox는 기본 기능 지원; 펜 입력 태블릿 및 데스크톱 마우스를 모두 지원.
- 사용 흐름: 문제 선택 → 메모 작성 → 데이터 모니터링 → JSON 다운로드 순서로 운영하며 수집 데이터는 치팅 패턴 탐지에 활용.
- 개인정보 보호: 개인 식별 정보 미수집, 무작위 세션 ID 사용, 로컬 처리 및 사용자 주도 다운로드, MIT 라이선스 명시.

### frontend_memo_app/DATA_COLLECTION.md
- 수집 목적: 부정행위 탐지 모델 학습을 위해 자연스러운 필기와 의심스러운 행동을 구분할 수 있는 정밀 데이터를 확보.
- 스트로크 데이터: ID, 도구, 색상, 굵기, 시작/종료 시각, 이동 거리·속도·압력, 바운딩 박스, 모든 포인터 샘플(좌표·압력·기울기·트위스트·속도·coalesced 여부 등)을 저장.
- 상호작용 이벤트: 스트로크 시작/종료, 도구·색·굵기 변경, Undo/Redo, 줌·캔버스 이동, 이미지 드래그, 세션 상태 변화, 데이터 다운로드 등을 기록.
- 세션 통계: 전체 소요 시간, 스트로크 수, 이동 거리, 평균 스트로크 길이, Undo/Redo·지우개·줌·팬 횟수 등 요약 지표를 산출.
- 기기/환경 정보: User Agent, 플랫폼, 픽셀 비율, 화면 크기, 입력 기능 지원 여부(압력/기울기/트위스트/coalesced), 캔버스 크기와 변환 상태를 포함.
- 개인정보 보호: 민감 정보 미수집, 무작위 UUID 세션 ID, 상대 시간 사용, 기기 정보는 비식별 수준으로 제한.
- 데이터 형식 및 활용: JSON 구조 예시, 정상 vs 비정상 패턴 분석, 특징 추출·라벨링·증강 전략, PointerEvent 활용 코드와 실시간 분석 메모, 향후 WebGL·AI 분석 확장 계획을 제시.
