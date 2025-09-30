"""
API 뷰 모듈

정적 프론트엔드에서 호출할 REST API 엔드포인트들을 제공합니다.
모든 응답은 JSON 형식으로 반환됩니다.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from core.models import Question, Category


@require_http_methods(["GET"])
@csrf_exempt
def get_all_questions(request):
    """
    모든 문제 목록을 카테고리별로 그룹화하여 반환하는 API

    **엔드포인트**: GET /api/questions/

    **응답 형식**:
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
                            "name": "문제 제목"
                        },
                        ...
                    ]
                },
                ...
            ],
            "total_count": 100
        }
    }
    ```

    **에러 응답**:
    ```json
    {
        "success": false,
        "error": "에러 메시지"
    }
    ```

    Args:
        request: Django HttpRequest 객체

    Returns:
        JsonResponse: 카테고리별로 그룹화된 문제 목록
    """
    try:
        # 1. 모든 카테고리 조회 (ID 순으로 정렬)
        categories = Category.objects.all().order_by('id')

        # 2. 카테고리별로 문제를 그룹화
        result = []
        total_question_count = 0

        for category in categories:
            # 해당 카테고리에 속한 문제들 조회 (최신순)
            questions = Question.objects.filter(category=category).order_by('-created_at')

            # 문제가 없는 카테고리는 제외
            if not questions.exists():
                continue

            # 문제 데이터 구성
            question_list = [
                {
                    "id": q.id,
                    "name": q.name,
                }
                for q in questions
            ]

            # 카테고리 데이터 구성
            result.append({
                "category_id": category.id,
                "category_name": category.name,
                "question_count": len(question_list),
                "questions": question_list
            })

            total_question_count += len(question_list)

        # 3. 성공 응답 반환
        return JsonResponse({
            "success": True,
            "data": {
                "categories": result,
                "total_count": total_question_count
            }
        }, json_dumps_params={'ensure_ascii': False})

    except Exception as e:
        # 4. 에러 발생 시 에러 응답 반환
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500, json_dumps_params={'ensure_ascii': False})


@require_http_methods(["GET"])
@csrf_exempt
def health_check(request):
    """
    API 서버 상태 확인 엔드포인트

    **엔드포인트**: GET /api/health/

    **응답 형식**:
    ```json
    {
        "status": "ok",
        "service": "Question API"
    }
    ```

    Args:
        request: Django HttpRequest 객체

    Returns:
        JsonResponse: 서버 상태 정보
    """
    return JsonResponse({
        "status": "ok",
        "service": "Question API"
    })
