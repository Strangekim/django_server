from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField
from django.db.models import CheckConstraint, Q

class Category(models.Model):
    id = models.BigAutoField(primary_key=True)                     # = idx bigserial/identity
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'questions"."category'                          # schema-qualified
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Question(models.Model):
    id = models.BigAutoField(primary_key=True)                     # = idx
    name = models.CharField(max_length=100, unique=True)

    original_img = models.TextField(null=True, blank=True)
    separate_img = models.TextField(null=True, blank=True)

    difficulty = models.SmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # FK: questions.category(idx) 참조
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,                                   # 삭제 보호 (원하면 CASCADE로)
        db_column="category",                                       # 컬럼명 그대로 'category'
        related_name="questions",
    )

    problem = models.TextField()

    # 배열 (고정 5개로 강제하고 싶으면 validators/CheckConstraint 추가 가능)
    choices = ArrayField(
        base_field=models.TextField(),
        default=list,     # ✅ 빈 배열이 기본값 (NULL 아님)
        blank=True,       # admin/form에서 비워도 OK → 빈 배열로 저장
        null=False        # DB NOT NULL
    )

    # 설명도 배열이지만 “항상 있어야” 하면 비슷하게:
    description = ArrayField(
        base_field=models.TextField(),
        default=list,     # 필요 시 기본값을 빈 배열로
        blank=True,
        null=False
    )

    answer = models.CharField(max_length=50)

    # 프론트엔드 노출 여부 (True: 노출, False: 숨김)
    # Default: True (모든 문제는 기본적으로 노출됨)
    # 관리자가 특정 문제를 숨기고 싶을 때 False로 설정
    is_visible = models.BooleanField(
        default=True,
        help_text="프론트엔드에 이 문제를 표시할지 여부"
    )

    created_at = models.DateTimeField(auto_now_add=True)            # = DEFAULT now()
    updated_at = models.DateTimeField(auto_now=True)                # = DEFAULT now()

    class Meta:
        db_table = 'questions"."list'
        constraints = [
            CheckConstraint(
                name="difficulty_0_100",
                check=Q(difficulty__gte=0) & Q(difficulty__lte=100),
            ),
        ]

    def __str__(self):
        return f"[{self.id}] {self.name}"
