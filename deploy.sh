#!/bin/bash

# EC2 배포 자동화 스크립트
# 이 스크립트는 EC2 서버에서 실행됩니다.

set -e  # 에러 발생 시 즉시 종료

echo "=========================================="
echo "🚀 Django 프로젝트 배포 시작"
echo "=========================================="

# 현재 디렉토리 확인
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "📁 프로젝트 디렉토리: $PROJECT_DIR"

# 1. Git Pull
echo ""
echo "📥 최신 코드 가져오기..."
git pull origin main

# 2. Python 의존성 설치
echo ""
echo "🐍 Python 의존성 설치..."
pip install -r requirements.txt

# 3. Frontend 빌드
echo ""
echo "⚛️  Frontend 빌드..."
cd frontend_memo_app
npm install
npm run build
cd ..

# 4. 빌드 결과 검증
echo ""
echo "🔍 빌드 결과 검증..."
if grep -q "/static/assets/" "frontend_memo_app/dist/index.html"; then
  echo "✅ 빌드 경로가 올바릅니다."
else
  echo "❌ 오류: 빌드 경로가 올바르지 않습니다!"
  exit 1
fi

# 5. Django collectstatic
echo ""
echo "📦 정적 파일 수집..."
python manage.py collectstatic --clear --noinput

# 6. 데이터베이스 마이그레이션
echo ""
echo "💾 데이터베이스 마이그레이션..."
python manage.py migrate

# 7. 서비스 재시작 (gunicorn 또는 uwsgi)
echo ""
echo "🔄 서비스 재시작..."

# Gunicorn 사용하는 경우
if systemctl is-active --quiet gunicorn; then
  echo "   Gunicorn 재시작 중..."
  sudo systemctl restart gunicorn
  echo "✅ Gunicorn 재시작 완료"
fi

# uWSGI 사용하는 경우
if systemctl is-active --quiet uwsgi; then
  echo "   uWSGI 재시작 중..."
  sudo systemctl restart uwsgi
  echo "✅ uWSGI 재시작 완료"
fi

# Nginx 재시작 (선택적)
# sudo systemctl reload nginx

echo ""
echo "=========================================="
echo "✅ 배포 완료!"
echo "=========================================="
echo ""
echo "서비스 상태 확인:"
echo "  sudo systemctl status gunicorn"
echo "  sudo systemctl status nginx"
echo ""
echo "로그 확인:"
echo "  sudo journalctl -u gunicorn -f"
echo "  sudo tail -f /var/log/nginx/error.log"
echo ""
