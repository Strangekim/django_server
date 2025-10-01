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

# 가상환경 경로 설정 (기본값: venv)
VENV_PATH="${VENV_PATH:-$PROJECT_DIR/venv}"

# 가상환경 확인 및 활성화
if [ -d "$VENV_PATH" ]; then
  echo "🐍 가상환경 발견: $VENV_PATH"
  echo "   가상환경 활성화 중..."
  source "$VENV_PATH/bin/activate"
  echo "✅ 가상환경 활성화 완료"
else
  echo "⚠️  경고: 가상환경을 찾을 수 없습니다: $VENV_PATH"
  echo "   가상환경 없이 계속 진행합니다."
  echo ""
  echo "💡 가상환경 생성 방법:"
  echo "   python3 -m venv venv"
  echo "   source venv/bin/activate"
  echo "   pip install -r requirements.txt"
  echo ""
fi

# 1. Git Pull
echo ""
echo "📥 최신 코드 가져오기..."
git pull origin main

# 2. Python 의존성 설치
echo ""
echo "🐍 Python 의존성 설치..."
if [ -d "$VENV_PATH" ]; then
  # 가상환경이 있으면 pip 사용
  pip install -r requirements.txt
else
  # 가상환경이 없으면 pip3 사용 (시스템 패키지)
  echo "⚠️  가상환경 없이 설치 시도 중..."
  pip3 install -r requirements.txt --user 2>/dev/null || {
    echo "❌ pip 설치 실패. 가상환경을 생성하고 다시 시도하세요."
    echo ""
    echo "가상환경 생성 명령어:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
  }
fi

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
if [ -d "$VENV_PATH" ]; then
  python manage.py collectstatic --clear --noinput
else
  python3 manage.py collectstatic --clear --noinput
fi

# 6. 데이터베이스 마이그레이션
echo ""
echo "💾 데이터베이스 마이그레이션..."
if [ -d "$VENV_PATH" ]; then
  python manage.py migrate
else
  python3 manage.py migrate
fi

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
