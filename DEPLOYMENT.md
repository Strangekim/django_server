# 배포 가이드

이 문서는 EC2 서버에서 Django + Vue.js 프로젝트를 배포하는 방법을 설명합니다.

## 프로젝트 구조

```
django_server/
├── config/              # Django 설정
├── core/                # 문제 업로드 앱
├── api/                 # REST API 앱
├── frontend_memo_app/   # Vue.js 프론트엔드
│   ├── dist/           # 빌드된 정적 파일 (배포용)
│   └── src/            # Vue 소스 코드
├── manage.py
└── requirements.txt
```

## EC2 서버 배포 절차

### 1. 저장소에서 코드 가져오기

```bash
cd /path/to/your/project
git pull origin main
```

### 2. Python 가상환경 활성화 및 의존성 설치

```bash
source venv/bin/activate  # Linux/Mac
# 또는
source venv/Scripts/activate  # Windows Git Bash

pip install -r requirements.txt
```

### 3. 프론트엔드 빌드

```bash
cd frontend_memo_app
npm install  # 처음 한 번만
npm run build
cd ..
```

빌드 결과는 `frontend_memo_app/dist/` 폴더에 생성됩니다:
- `index.html` - 메인 HTML 파일
- `assets/` - CSS, JS 파일들

### 4. 정적 파일 수집 (프로덕션)

```bash
python manage.py collectstatic --noinput
```

이 명령은 다음을 수행합니다:
- `frontend_memo_app/dist/assets/` → `staticfiles/static/` 복사
- Django admin 정적 파일 복사

### 5. 데이터베이스 마이그레이션

```bash
python manage.py migrate
```

### 6. Gunicorn + Nginx로 서버 실행

#### Gunicorn 설정 예시

```bash
gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

#### Nginx 설정 예시 (`/etc/nginx/sites-available/django_server`)

```nginx
server {
    listen 80;
    server_name 54.180.150.130;

    client_max_body_size 20M;

    # 정적 파일 서빙
    location /static/ {
        alias /path/to/django_server/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # API 및 Django 요청을 Gunicorn으로 프록시
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
```

#### Nginx 재시작

```bash
sudo nginx -t  # 설정 테스트
sudo systemctl restart nginx
```

## URL 구조

배포 후 다음 URL로 접속할 수 있습니다:

### 프론트엔드 (Vue SPA)
- **메인 페이지**: `http://54.180.150.130/`
- Vue Router가 클라이언트 사이드 라우팅 처리

### 백엔드 API
- **헬스체크**: `http://54.180.150.130/health/`
- **문제 업로드**: `http://54.180.150.130/problems/upload/`
- **문제 목록 API**: `http://54.180.150.130/api/questions/`
- **문제 상세 API**: `http://54.180.150.130/api/questions/<id>/`
- **답안 검증 API**: `http://54.180.150.130/api/verify-solution/`

### Django 관리자
- **Admin**: `http://54.180.150.130/admin/`

## 환경 변수 설정

`.env` 파일에 다음 변수들이 설정되어 있어야 합니다:

```bash
# Django
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
ALLOWED_HOSTS=54.180.150.130,localhost,127.0.0.1

# Database
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# AWS S3
AWS_REGION=ap-northeast-2
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_STORAGE_BUCKET_NAME=your_bucket_name

# Mathpix
MATHPIX_APP_ID=your_app_id
MATHPIX_APP_KEY=your_app_key

# OpenAI
OPENAI_API_KEY=your_api_key
```

## 프로덕션 체크리스트

배포 전 확인사항:

- [ ] `.env` 파일에 모든 환경 변수 설정
- [ ] `DEBUG=False` 설정
- [ ] `ALLOWED_HOSTS`에 EC2 IP 추가
- [ ] 프론트엔드 빌드 완료 (`npm run build`)
- [ ] 정적 파일 수집 완료 (`collectstatic`)
- [ ] 데이터베이스 마이그레이션 완료
- [ ] Gunicorn 실행 확인
- [ ] Nginx 설정 및 재시작
- [ ] S3 버킷 접근 권한 확인
- [ ] PostgreSQL 데이터베이스 연결 확인

## 개발 vs 프로덕션

### 개발 환경 (localhost)
- 프론트엔드: `npm run dev` → `http://localhost:3000`
- 백엔드: `python manage.py runserver` → `http://localhost:8000`
- API 호출: `http://localhost:8000`

### 프로덕션 환경 (EC2)
- 프론트엔드: Django가 빌드된 파일 서빙 → `http://54.180.150.130/`
- 백엔드: Gunicorn + Nginx → `http://54.180.150.130`
- API 호출: `http://54.180.150.130`

프론트엔드 코드는 자동으로 환경을 감지합니다 (`src/api/config.js`):
```javascript
export const API_BASE_URL = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : 'http://54.180.150.130'
```

## 트러블슈팅

### 정적 파일이 로드되지 않는 경우

```bash
# 정적 파일 재수집
python manage.py collectstatic --clear --noinput

# Nginx 로그 확인
sudo tail -f /var/log/nginx/error.log
```

### API 호출 실패 (CORS 에러)

`config/settings.py`에서 CORS 설정 확인:
```python
CORS_ALLOW_ALL_ORIGINS = True  # 개발용
# 또는
CORS_ALLOWED_ORIGINS = [
    "http://54.180.150.130",
]
```

### 500 에러 발생

```bash
# Gunicorn 로그 확인
sudo journalctl -u gunicorn -f

# Django 로그 확인
tail -f /path/to/logs/django.log
```

### 데이터베이스 연결 실패

```bash
# PostgreSQL 상태 확인
sudo systemctl status postgresql

# 연결 테스트
python manage.py dbshell
```

## 업데이트 절차

코드가 변경되었을 때 배포 절차:

```bash
# 1. 코드 업데이트
git pull origin main

# 2. 의존성 업데이트 (필요시)
pip install -r requirements.txt

# 3. 프론트엔드 리빌드 (프론트엔드 변경 시)
cd frontend_memo_app
npm run build
cd ..

# 4. 정적 파일 재수집
python manage.py collectstatic --noinput

# 5. 마이그레이션 (모델 변경 시)
python manage.py migrate

# 6. Gunicorn 재시작
sudo systemctl restart gunicorn

# 7. Nginx 재시작 (설정 변경 시)
sudo systemctl restart nginx
```

## 모니터링

### 서비스 상태 확인

```bash
# Gunicorn 상태
sudo systemctl status gunicorn

# Nginx 상태
sudo systemctl status nginx

# PostgreSQL 상태
sudo systemctl status postgresql
```

### 로그 모니터링

```bash
# Gunicorn 로그
sudo journalctl -u gunicorn -f

# Nginx 접근 로그
sudo tail -f /var/log/nginx/access.log

# Nginx 에러 로그
sudo tail -f /var/log/nginx/error.log
```
