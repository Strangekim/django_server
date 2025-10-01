"""
메인 URL 라우팅 설정

Django 프로젝트의 모든 URL 패턴을 정의합니다.
각 앱의 URL은 include()를 통해 분리하여 관리합니다.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
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

    # 루트 URL: Vue SPA 서빙 (index.html)
    # 다른 모든 URL보다 낮은 우선순위로 배치
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html'), name='frontend'),
]

# 정적 파일 서빙 (개발 및 프로덕션)
# static() 헬퍼는 개발 환경(DEBUG=True)에서만 작동하지만,
# Gunicorn 사용 시에도 Django가 정적 파일을 서빙할 수 있도록 추가
if settings.DEBUG or True:  # 프로덕션에서도 Django가 정적 파일 서빙
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
