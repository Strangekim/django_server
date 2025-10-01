"""
API 앱 URL 라우팅 설정

정적 프론트엔드에서 호출할 API 엔드포인트들의 URL 매핑을 정의합니다.
"""

from django.urls import path
from . import views

# API 앱의 네임스페이스
app_name = 'api'

urlpatterns = [
    # API 상태 확인 엔드포인트
    # GET /api/health/
    path('health/', views.health_check, name='health_check'),

    # 모든 문제 목록 조회 (카테고리별 그룹화)
    # GET /api/questions/
    path('questions/', views.get_all_questions, name='get_all_questions'),

    # 특정 문제 상세 정보 조회 (정답과 원본 이미지 제외)
    # GET /api/questions/<question_id>/
    path('questions/<int:question_id>/', views.get_question_detail, name='get_question_detail'),

    # 문제 풀이 검증 (필기 인식 + AI 평가)
    # POST  
    path('verify-solution/', views.verify_solution, name='verify_solution'),
]
