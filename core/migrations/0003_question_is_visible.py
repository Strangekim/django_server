# Generated migration for adding is_visible field to Question model
# 생성 날짜: 2025-10-03
# 목적: 프론트엔드에서 문제 노출 여부를 제어하기 위한 is_visible 필드 추가

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_initial'),
    ]

    operations = [
        # Question 모델에 is_visible 필드 추가
        # - default=True: 기본값은 노출(True)
        # - 기존 데이터도 모두 True로 설정됨
        migrations.AddField(
            model_name='question',
            name='is_visible',
            field=models.BooleanField(
                default=True,
                help_text='프론트엔드에 이 문제를 표시할지 여부'
            ),
        ),
    ]
