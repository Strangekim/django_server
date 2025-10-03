from django.contrib import admin
from .models import Category, Question


# Category 모델 Admin 설정
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    카테고리 관리 페이지 설정
    """
    # 목록 페이지에 표시할 필드
    list_display = ['id', 'name']

    # 검색 가능한 필드
    search_fields = ['name']

    # ID 순으로 정렬
    ordering = ['id']


# Question 모델 Admin 설정
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    문제 관리 페이지 설정
    - is_visible 필드를 통해 프론트엔드 노출 여부를 쉽게 관리 가능
    """
    # 목록 페이지에 표시할 필드
    list_display = [
        'id',
        'name',
        'category',
        'difficulty',
        'is_visible',  # 노출 여부 표시
        'created_at',
        'updated_at'
    ]

    # 필터링 옵션 (우측 사이드바)
    list_filter = [
        'is_visible',   # 노출 여부로 필터링
        'category',     # 카테고리로 필터링
        'difficulty',   # 난이도로 필터링
        'created_at'    # 생성일로 필터링
    ]

    # 검색 가능한 필드
    search_fields = ['name', 'problem', 'answer']

    # 목록에서 직접 수정 가능한 필드
    # - name: 문제 제목 수정
    # - difficulty: 난이도 수정
    # - is_visible: 노출 여부 수정 (체크박스)
    # 주의: list_display의 첫 번째 필드(id)는 list_editable에 포함할 수 없음
    list_editable = ['name', 'difficulty', 'is_visible']

    # 최신순 정렬
    ordering = ['-created_at']

    # 상세 페이지 필드 그룹화
    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'category', 'difficulty', 'is_visible')
        }),
        ('문제 내용', {
            'fields': ('problem', 'choices', 'description', 'answer')
        }),
        ('이미지', {
            'fields': ('original_img', 'separate_img'),
            'classes': ('collapse',)  # 기본적으로 접힌 상태
        }),
        ('메타 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # 기본적으로 접힌 상태
        }),
    )

    # 읽기 전용 필드 (자동 생성 필드)
    readonly_fields = ['created_at', 'updated_at']

    # 한 페이지에 표시할 항목 수
    list_per_page = 50
