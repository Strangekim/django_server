# API 앱 문서

정적 프론트엔드에서 호출할 REST API를 제공하는 Django 앱입니다.

## 📁 구조

```
api/
├── __init__.py
├── views.py          # API 뷰 함수들
├── urls.py           # URL 라우팅 설정
└── README.md         # 이 문서
```

## 🔗 엔드포인트

### 1. Health Check
서버 상태를 확인합니다.

- **URL**: `GET /api/health/`
- **응답**:
```json
{
  "status": "ok",
  "service": "Question API"
}
```

### 2. 모든 문제 목록 조회
카테고리별로 그룹화된 모든 문제 목록을 반환합니다.

- **URL**: `GET /api/questions/`
- **성공 응답** (200):
```json
{
  "success": true,
  "data": {
    "categories": [
      {
        "category_id": 1,
        "category_name": "다항식",
        "question_count": 5,
        "questions": [
          {
            "id": 1,
            "name": "2025_고1_3월 모의고사_1번"
          },
          {
            "id": 2,
            "name": "다항식의 곱셈 문제"
          }
        ]
      }
    ],
    "total_count": 100
  }
}
```

- **에러 응답** (500):
```json
{
  "success": false,
  "error": "에러 메시지"
}
```

## ⚙️ 설정

### CORS 설정
`config/settings.py`에서 CORS 관련 설정을 확인할 수 있습니다:

```python
# 개발 환경: 모든 출처 허용
CORS_ALLOW_ALL_ORIGINS = True

# 프로덕션 환경: 특정 도메인만 허용
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "https://yourdomain.com",
# ]
```

### URL 라우팅
`config/urls.py`에 다음과 같이 등록되어 있습니다:

```python
urlpatterns = [
    path("api/", include("api.urls")),
]
```

## 🧪 테스트

### cURL 테스트
```bash
# Health check
curl http://127.0.0.1:8000/api/health/

# 문제 목록 조회
curl http://127.0.0.1:8000/api/questions/
```

### JavaScript (Fetch API)
```javascript
// 문제 목록 가져오기
fetch('http://127.0.0.1:8000/api/questions/')
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log('카테고리 목록:', data.data.categories);
      console.log('총 문제 수:', data.data.total_count);
    }
  })
  .catch(error => console.error('Error:', error));
```

## 📝 유지보수

### 새로운 API 추가하기

1. `api/views.py`에 새 뷰 함수 작성:
```python
@require_http_methods(["GET"])
@csrf_exempt
def get_question_detail(request, question_id):
    """문제 상세 정보 조회"""
    try:
        question = Question.objects.get(id=question_id)
        return JsonResponse({
            "success": True,
            "data": {
                "id": question.id,
                "name": question.name,
                "problem": question.problem,
                # ... 기타 필드
            }
        }, json_dumps_params={'ensure_ascii': False})
    except Question.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "문제를 찾을 수 없습니다."
        }, status=404)
```

2. `api/urls.py`에 URL 패턴 추가:
```python
urlpatterns = [
    # 기존 패턴...
    path('questions/<int:question_id>/', views.get_question_detail, name='get_question_detail'),
]
```

## 🔒 보안 고려사항

1. **CSRF 보호**: API 엔드포인트는 `@csrf_exempt`로 CSRF 검증을 생략합니다.
2. **CORS**: 개발 환경에서는 모든 출처를 허용하지만, 프로덕션에서는 특정 도메인만 허용하도록 설정해야 합니다.
3. **인증**: 현재는 인증이 없지만, 필요시 Django REST Framework의 TokenAuthentication 등을 추가할 수 있습니다.

## 📦 의존성

- `django-cors-headers`: CORS 헤더 처리
