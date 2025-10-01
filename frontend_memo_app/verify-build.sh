#!/bin/bash

# 빌드 결과물 검증 스크립트
# 이 스크립트는 프로덕션 빌드가 올바르게 생성되었는지 검증합니다.

set -e  # 에러 발생 시 즉시 종료

echo "=========================================="
echo "🔍 프론트엔드 빌드 검증 시작"
echo "=========================================="

# 1. dist 디렉토리 존재 확인
if [ ! -d "dist" ]; then
  echo "❌ 오류: dist 디렉토리가 없습니다."
  echo "   npm run build를 먼저 실행하세요."
  exit 1
fi

# 2. index.html 존재 확인
if [ ! -f "dist/index.html" ]; then
  echo "❌ 오류: dist/index.html이 없습니다."
  exit 1
fi

# 3. index.html에서 경로 검증
echo ""
echo "📄 index.html 경로 검증 중..."

# /static/assets/ 경로가 있는지 확인
if grep -q "/static/assets/" "dist/index.html"; then
  echo "✅ /static/assets/ 경로가 올바르게 설정되었습니다."
else
  echo "❌ 오류: /static/assets/ 경로를 찾을 수 없습니다."
  exit 1
fi

# 상대 경로 (./assets/)가 남아있는지 확인
if grep -q "\"./assets/" "dist/index.html" || grep -q "'./assets/" "dist/index.html"; then
  echo "❌ 오류: 상대 경로 (./assets/)가 남아있습니다!"
  echo ""
  echo "문제가 있는 라인:"
  grep -n "./assets/" "dist/index.html"
  exit 1
else
  echo "✅ 상대 경로가 없습니다."
fi

# 4. assets 디렉토리 확인
if [ ! -d "dist/assets" ]; then
  echo "❌ 오류: dist/assets 디렉토리가 없습니다."
  exit 1
fi

# assets 내 파일 개수 확인
asset_count=$(ls -1 dist/assets/ | wc -l)
if [ "$asset_count" -eq 0 ]; then
  echo "❌ 오류: dist/assets/ 디렉토리가 비어있습니다."
  exit 1
else
  echo "✅ assets 디렉토리에 $asset_count 개의 파일이 있습니다."
fi

# 5. 환경 변수 파일 존재 확인
echo ""
echo "📋 환경 설정 파일 확인 중..."

if [ ! -f ".env.development" ]; then
  echo "⚠️  경고: .env.development 파일이 없습니다."
else
  echo "✅ .env.development 존재"
fi

if [ ! -f ".env.production" ]; then
  echo "⚠️  경고: .env.production 파일이 없습니다."
else
  echo "✅ .env.production 존재"
fi

echo ""
echo "=========================================="
echo "✅ 모든 검증 통과!"
echo "=========================================="
echo ""
echo "다음 단계:"
echo "1. git add ."
echo "2. git commit -m \"your message\""
echo "3. git push"
echo ""
echo "EC2에서 실행할 명령어:"
echo "1. git pull"
echo "2. cd frontend_memo_app && npm install && npm run build"
echo "3. cd .. && python manage.py collectstatic --clear --noinput"
echo "4. sudo systemctl restart gunicorn (또는 uwsgi)"
echo ""
