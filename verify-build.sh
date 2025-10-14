#!/bin/bash

# 배포 서버 빌드 검증 스크립트
# 빌드 후 문제를 진단하는 도구

echo "=========================================="
echo "🔍 배포 빌드 검증 도구"
echo "=========================================="

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo ""
echo "1. 빌드 파일 존재 확인..."
if [ -f "$PROJECT_DIR/frontend_memo_app/dist/index.html" ]; then
  echo "✅ index.html 존재"
else
  echo "❌ index.html 없음"
  exit 1
fi

if [ -d "$PROJECT_DIR/frontend_memo_app/dist/assets" ]; then
  echo "✅ assets 디렉토리 존재"
  echo "   파일 개수: $(ls -1 $PROJECT_DIR/frontend_memo_app/dist/assets | wc -l)"
else
  echo "❌ assets 디렉토리 없음"
  exit 1
fi

echo ""
echo "2. 빌드 경로 검증..."
if grep -q "/static/assets/" "$PROJECT_DIR/frontend_memo_app/dist/index.html"; then
  echo "✅ 빌드 경로 올바름 (/static/assets/)"
else
  echo "❌ 빌드 경로 오류!"
  echo "   현재 경로:"
  grep "assets/" "$PROJECT_DIR/frontend_memo_app/dist/index.html"
  exit 1
fi

echo ""
echo "3. staticfiles 디렉토리 확인..."
if [ -d "$PROJECT_DIR/staticfiles" ]; then
  echo "✅ staticfiles 디렉토리 존재"
  if [ -d "$PROJECT_DIR/staticfiles/assets" ]; then
    echo "✅ staticfiles/assets 존재"
    echo "   파일 개수: $(ls -1 $PROJECT_DIR/staticfiles/assets | wc -l)"
  else
    echo "⚠️  staticfiles/assets 없음 (collectstatic 실행 필요)"
  fi
else
  echo "⚠️  staticfiles 디렉토리 없음 (collectstatic 실행 필요)"
fi

echo ""
echo "4. index.html 내용 확인..."
echo "   JS 파일:"
grep "\.js" "$PROJECT_DIR/frontend_memo_app/dist/index.html"
echo ""
echo "   CSS 파일:"
grep "\.css" "$PROJECT_DIR/frontend_memo_app/dist/index.html"

echo ""
echo "5. Node 모듈 확인..."
if [ -d "$PROJECT_DIR/frontend_memo_app/node_modules/pinia" ]; then
  echo "✅ Pinia 설치됨"
else
  echo "❌ Pinia 미설치!"
fi

if [ -d "$PROJECT_DIR/frontend_memo_app/node_modules/vue" ]; then
  echo "✅ Vue 설치됨"
else
  echo "❌ Vue 미설치!"
fi

echo ""
echo "6. 빌드된 JS 파일 분석..."
JS_FILE=$(ls -1 $PROJECT_DIR/frontend_memo_app/dist/assets/*.js 2>/dev/null | head -1)
if [ -f "$JS_FILE" ]; then
  FILE_SIZE=$(du -h "$JS_FILE" | cut -f1)
  echo "✅ JS 파일 크기: $FILE_SIZE"

  echo ""
  echo "   주요 컴포넌트 포함 여부:"
  if grep -q "MemoCanvas" "$JS_FILE"; then
    echo "   ✅ MemoCanvas 포함됨"
  else
    echo "   ❌ MemoCanvas 누락!"
  fi

  if grep -q "createPinia" "$JS_FILE"; then
    echo "   ✅ Pinia 포함됨"
  else
    echo "   ❌ Pinia 누락!"
  fi

  if grep -q "problemStore" "$JS_FILE"; then
    echo "   ✅ problemStore 포함됨"
  else
    echo "   ❌ problemStore 누락!"
  fi
else
  echo "❌ JS 파일을 찾을 수 없음!"
fi

echo ""
echo "=========================================="
echo "검증 완료!"
echo "=========================================="
echo ""
echo "💡 배포 서버에서 문제가 발생하면:"
echo "   1. 브라우저 개발자 도구 Console 확인"
echo "   2. Network 탭에서 404 에러 확인"
echo "   3. Django 로그 확인: sudo journalctl -u gunicorn -f"
echo "   4. Nginx 로그 확인: sudo tail -f /var/log/nginx/error.log"
echo ""
