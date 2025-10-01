# 배포 가이드

## 📋 목차
1. [로컬 개발 환경](#로컬-개발-환경)
2. [프로덕션 빌드](#프로덕션-빌드)
3. [EC2 배포](#ec2-배포)
4. [트러블슈팅](#트러블슈팅)

---

## 🖥️ 로컬 개발 환경

### Frontend 개발 서버 실행
```bash
cd frontend_memo_app
npm install
npm run dev
```
- 브라우저: http://localhost:3000
- API 호출: http://localhost:8000/api (Django 개발 서버)

### Django 개발 서버 실행
```bash
python manage.py runserver
```
- 브라우저: http://localhost:8000

---

## 🏗️ 프로덕션 빌드

### 1. Frontend 빌드
```bash
cd frontend_memo_app
npm run build
```

### 2. 빌드 검증
```bash
./verify-build.sh
```

**검증 항목:**
- ✅ `dist/index.html`에 `/static/assets/` 경로 사용
- ✅ 상대 경로 `./assets/` 없음
- ✅ `dist/assets/` 디렉토리에 파일 존재
- ✅ `.env.development`, `.env.production` 존재

### 3. Git Push
```bash
git add .
git commit -m "Build frontend for production"
git push origin main
```

---

## 🚀 EC2 배포

### 방법 1: 자동 배포 스크립트 (권장)
```bash
# EC2 서버에서 실행
cd /path/to/django_server
./deploy.sh
```

이 스크립트는 다음 작업을 자동으로 수행합니다:
1. Git Pull
2. Python 의존성 설치
3. Frontend 빌드
4. 빌드 검증
5. collectstatic 실행
6. 데이터베이스 마이그레이션
7. Gunicorn/uWSGI 재시작

### 방법 2: 수동 배포
```bash
# 1. 최신 코드 가져오기
git pull origin main

# 2. Python 의존성 설치
pip install -r requirements.txt

# 3. Frontend 빌드
cd frontend_memo_app
npm install
npm run build
cd ..

# 4. 정적 파일 수집
python manage.py collectstatic --clear --noinput

# 5. 데이터베이스 마이그레이션
python manage.py migrate

# 6. 서비스 재시작
sudo systemctl restart gunicorn
sudo systemctl reload nginx
```

---

## 🔧 설정 파일

### Vite 설정 (frontend_memo_app/vite.config.js)
- 개발: base = '/'
- 프로덕션: base = '/static/'

### 환경 변수

**.env.development** (개발)
```
VITE_API_BASE=http://localhost:8000
```

**.env.production** (프로덕션)
```
VITE_API_BASE=
```

### Django 설정 (config/settings.py)
```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / "frontend_memo_app" / "dist"]
```

---

## 🐛 트러블슈팅

### 정적 파일 404 에러
```bash
python manage.py collectstatic --clear --noinput
sudo systemctl reload nginx
```

### CSS/JS 경로가 ./assets/로 나옴
```bash
cd frontend_memo_app
rm -rf dist node_modules/.vite
npm install
npm run build
```

### API 호출 실패
Nginx 설정에서 /api/ 프록시 확인

---

## 📊 배포 체크리스트

배포 전:
- [ ] npm run build 실행
- [ ] verify-build.sh 통과
- [ ] Git push 완료

배포 후:
- [ ] 사이트 접속 테스트
- [ ] API 호출 테스트
- [ ] 정적 파일 로딩 확인
