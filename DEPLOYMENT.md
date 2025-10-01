# 배포 가이드

## 📋 목차
1. [초기 EC2 설정](#초기-ec2-설정)
2. [로컬 개발 환경](#로컬-개발-환경)
3. [프로덕션 빌드](#프로덕션-빌드)
4. [EC2 배포](#ec2-배포)
5. [트러블슈팅](#트러블슈팅)

---

## 🏗️ 초기 EC2 설정 (최초 1회만)

### 1. Python 가상환경 생성
```bash
cd /home/ubuntu/django_server

# Python 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# pip 업그레이드
pip install --upgrade pip

# 의존성 설치
pip install -r requirements.txt
```

### 2. Node.js 설치 (없는 경우)
```bash
# Node.js 18.x 설치
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 설치 확인
node -v
npm -v
```

### 3. Gunicorn 서비스 설정
`/etc/systemd/system/gunicorn.service`:
```ini
[Unit]
Description=Gunicorn daemon for Django project
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/django_server
Environment="PATH=/home/ubuntu/django_server/venv/bin"
ExecStart=/home/ubuntu/django_server/venv/bin/gunicorn \
    --workers 3 \
    --bind 0.0.0.0:8000 \
    config.wsgi:application

[Install]
WantedBy=multi-user.target
```

서비스 시작:
```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

### 4. Nginx 설정
`/etc/nginx/sites-available/django`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Django 정적 파일
    location /static/ {
        alias /home/ubuntu/django_server/staticfiles/;
    }

    # Django API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Django Admin
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Frontend (index.html)
    location / {
        root /home/ubuntu/django_server/staticfiles;
        try_files $uri /index.html;
    }
}
```

심볼릭 링크 생성 및 Nginx 재시작:
```bash
sudo ln -s /etc/nginx/sites-available/django /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🖥️ 로컬 개발 환경

### Frontend 개발 서버
```bash
cd frontend_memo_app
npm install
npm run dev
```
- http://localhost:3000
- API: http://localhost:8000/api

### Django 개발 서버
```bash
python manage.py runserver
```
- http://localhost:8000

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

검증 항목:
- ✅ `/static/assets/` 경로
- ✅ 상대 경로 제거
- ✅ assets 파일 존재

### 3. Git Push
```bash
git add .
git commit -m "Update build"
git push origin main
```

---

## 🚀 EC2 배포

### 방법 1: 자동 배포 (권장)

**가상환경이 있는 경우:**
```bash
cd /home/ubuntu/django_server
./deploy.sh
```

**가상환경 경로가 다른 경우:**
```bash
VENV_PATH=/path/to/your/venv ./deploy.sh
```

**deploy.sh가 자동으로 수행하는 작업:**
1. ✅ 가상환경 자동 감지 및 활성화
2. ✅ Git Pull
3. ✅ Python 의존성 설치
4. ✅ Frontend 빌드
5. ✅ 빌드 검증
6. ✅ collectstatic
7. ✅ 데이터베이스 마이그레이션
8. ✅ Gunicorn 재시작

### 방법 2: 수동 배포

```bash
# 1. 프로젝트 디렉토리로 이동
cd /home/ubuntu/django_server

# 2. 가상환경 활성화
source venv/bin/activate

# 3. 최신 코드 가져오기
git pull origin main

# 4. Python 의존성 설치
pip install -r requirements.txt

# 5. Frontend 빌드
cd frontend_memo_app
npm install
npm run build
cd ..

# 6. 정적 파일 수집
python manage.py collectstatic --clear --noinput

# 7. 데이터베이스 마이그레이션
python manage.py migrate

# 8. Gunicorn 재시작
sudo systemctl restart gunicorn

# 9. Nginx 재시작 (필요시)
sudo systemctl reload nginx
```

---

## 🐛 트러블슈팅

### 1. "externally-managed-environment" 오류

**문제:**
```
error: externally-managed-environment
× This environment is externally managed
```

**원인:** Ubuntu 23.04 이상에서 시스템 Python에 직접 패키지 설치 불가

**해결책:**
```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 배포 스크립트 실행
./deploy.sh
```

### 2. 정적 파일 404 에러

**해결:**
```bash
source venv/bin/activate
python manage.py collectstatic --clear --noinput
sudo systemctl restart gunicorn
sudo systemctl reload nginx
```

### 3. CSS/JS 경로가 ./assets/로 나옴

**해결:**
```bash
cd frontend_memo_app
rm -rf dist node_modules/.vite
npm install
npm run build
./verify-build.sh
```

### 4. API 호출 실패

**확인 사항:**
- Nginx 설정에 `/api/` 프록시 있는지 확인
- Gunicorn이 8000 포트에서 실행 중인지 확인

```bash
sudo systemctl status gunicorn
sudo netstat -tlnp | grep 8000
```

### 5. Gunicorn 재시작 실패

**로그 확인:**
```bash
sudo journalctl -u gunicorn -n 50
```

**일반적인 해결책:**
```bash
# 가상환경 경로 확인
source /home/ubuntu/django_server/venv/bin/activate

# 의존성 재설치
pip install -r requirements.txt

# 서비스 재시작
sudo systemctl restart gunicorn
```

---

## 📊 배포 체크리스트

### 로컬 (Push 전)
- [ ] `npm run build` 실행
- [ ] `./verify-build.sh` 통과
- [ ] Git commit & push

### EC2 (배포 시)
- [ ] 가상환경 활성화 확인
- [ ] `./deploy.sh` 실행
- [ ] 사이트 접속 테스트
- [ ] API 호출 테스트 (`/api/health/`)
- [ ] 정적 파일 로딩 확인 (개발자 도구)

---

## 🔍 유용한 명령어

### 서비스 상태 확인
```bash
sudo systemctl status gunicorn
sudo systemctl status nginx
```

### 로그 확인
```bash
# Gunicorn 로그 (실시간)
sudo journalctl -u gunicorn -f

# Nginx 에러 로그
sudo tail -f /var/log/nginx/error.log

# Nginx 액세스 로그
sudo tail -f /var/log/nginx/access.log
```

### 파일 권한 확인
```bash
# staticfiles 권한 확인
ls -la staticfiles/

# 필요시 권한 수정
sudo chown -R ubuntu:www-data staticfiles/
sudo chmod -R 755 staticfiles/
```

### 디스크 사용량 확인
```bash
df -h
du -sh /home/ubuntu/django_server/*
```

---

## 📞 자주 하는 실수

1. **가상환경 활성화 안함**
   - 항상 `source venv/bin/activate` 먼저 실행

2. **collectstatic 안함**
   - 빌드 후 반드시 `collectstatic` 실행

3. **Gunicorn 재시작 안함**
   - Python 코드 변경 시 반드시 재시작

4. **Nginx 설정 변경 후 reload 안함**
   - `sudo systemctl reload nginx` 실행

5. **로그 확인 안함**
   - 에러 발생 시 로그부터 확인
