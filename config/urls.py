"""
메인 URL 라우팅 설정

Django 프로젝트의 모든 URL 패턴을 정의합니다.
각 앱의 URL은 include()를 통해 분리하여 관리합니다.
"""
from django.contrib import admin
from django.urls import path, include
from core.views import health

urlpatterns = [
    # Django 관리자 페이지
    path('admin/', admin.site.urls),

    # 헬스 체크 엔드포인트
    path("health/", health),

    # Core 앱: 문제 업로드 관련 페이지
    path("problems/", include("core.urls")),

    # API 앱: 정적 프론트엔드에서 호출할 REST API
    # /api/로 시작하는 모든 요청은 api.urls로 라우팅
    path("api/", include("api.urls")),
]
