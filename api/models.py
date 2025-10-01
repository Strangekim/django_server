# api/models.py
from django.db import models

class Session(models.Model):
    # 세션/문항 메타 + 요약치(학습/대시보드 캐시)
    session_uuid = models.UUIDField(primary_key=True)
    # 절대시각(옵션) — 상대 ms는 하위 테이블에서 사용
    start_time = models.DateTimeField(null=True, blank=True)
    end_time   = models.DateTimeField(null=True, blank=True)
    duration_ms = models.IntegerField()

    # 문제 메타 (요청: int)
    problem_id = models.IntegerField(db_index=True)
    category   = models.IntegerField(db_index=True)  # 카테고리 INT 코드

    # 기기/환경(쿼리 필요 시)
    user_agent = models.TextField(null=True, blank=True)
    platform   = models.CharField(max_length=64, null=True, blank=True)
    pixel_ratio = models.FloatField(null=True, blank=True)
    screen_width  = models.IntegerField(null=True, blank=True)
    screen_height = models.IntegerField(null=True, blank=True)

    # 캔버스 상태(요약)
    logical_width  = models.IntegerField(null=True, blank=True)
    logical_height = models.IntegerField(null=True, blank=True)
    css_width      = models.IntegerField(null=True, blank=True)
    css_height     = models.IntegerField(null=True, blank=True)
    zoom           = models.FloatField(null=True, blank=True)
    pan_x          = models.IntegerField(null=True, blank=True)
    pan_y          = models.IntegerField(null=True, blank=True)

    # 포인터 기능 지원
    supports_pressure  = models.BooleanField(default=False)
    supports_tilt      = models.BooleanField(default=False)
    supports_twist     = models.BooleanField(default=False)
    supports_coalesced = models.BooleanField(default=False)

    # 요약 통계(캐시)
    stroke_count = models.IntegerField()
    total_distance_px = models.FloatField()
    average_stroke_length_px = models.FloatField(null=True, blank=True)
    undo_count = models.IntegerField(default=0)
    redo_count = models.IntegerField(default=0)
    eraser_count = models.IntegerField(default=0)
    zoom_count   = models.IntegerField(default=0)
    pan_count    = models.IntegerField(default=0)
    tool_change_count = models.IntegerField(default=0)  # 도구 변경 횟수

    # 사용자 답안 (선택적)
    answer = models.CharField(max_length=255, null=True, blank=True)  # 사용자가 제출한 답
    is_correct = models.BooleanField(null=True, blank=True)  # 정답 여부

    # 지도학습 라벨(운영 수집 시 NULL)
    label = models.SmallIntegerField(null=True, blank=True)  # 0=정상,1=치팅

    class Meta:
        db_table = "sessions"


class Stroke(models.Model):
    # 스트로크 메타
    stroke_uuid = models.UUIDField(primary_key=True)  # 클라 생성 or 서버에서 uuid4
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="strokes")
    tool = models.CharField(max_length=16)            # 'pen' | 'eraser'
    color = models.CharField(max_length=16)           # '#RRGGBB'
    stroke_width = models.IntegerField()              # px (항상 숫자형으로)
    start_ms = models.IntegerField()                  # 세션 기준 상대 ms
    end_ms   = models.IntegerField()

    # 입력 기기 정보
    pointer_type = models.CharField(max_length=16, default='pen')  # 'pen'|'touch'|'mouse'
    is_coalesced = models.BooleanField(default=False)  # 고주파수 이벤트 여부

    # 요약치
    total_distance_px = models.FloatField()
    average_speed_pxps = models.FloatField(null=True, blank=True)
    average_pressure   = models.FloatField(null=True, blank=True)

    # bbox
    bbox_min_x = models.IntegerField()
    bbox_min_y = models.IntegerField()
    bbox_max_x = models.IntegerField()
    bbox_max_y = models.IntegerField()

    class Meta:
        db_table = "strokes"
        indexes = [
            models.Index(fields=["session", "start_ms"]),
        ]


class StrokePoint(models.Model):
    # 대용량: 파티셔닝 권장(월/수집일 기준) — raw SQL migration에서 분할
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="points")
    stroke  = models.ForeignKey(Stroke, on_delete=models.CASCADE, related_name="points")
    idx     = models.IntegerField()        # 스트로크 내 순번 (0..N-1)
    t_ms    = models.IntegerField()        # 스트로크 시작 기준 ms
    x       = models.IntegerField()
    y       = models.IntegerField()
    pressure = models.FloatField(null=True, blank=True)  # 마우스는 NULL
    tilt_x   = models.IntegerField(null=True, blank=True)
    tilt_y   = models.IntegerField(null=True, blank=True)
    twist    = models.IntegerField(null=True, blank=True)
    pointer_type = models.CharField(max_length=16)  # 'pen'|'touch'|'mouse'
    pointer_id   = models.IntegerField(null=True, blank=True)
    buttons      = models.IntegerField(default=0)
    width        = models.IntegerField(null=True, blank=True)
    height       = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "stroke_points"
        unique_together = ("stroke", "idx")
        indexes = [
            models.Index(fields=["session", "stroke", "idx"]),
            models.Index(fields=["session", "t_ms"]),
        ]


class Event(models.Model):
    # 이벤트 고유 ID (동일 시각에 여러 이벤트 허용)
    id = models.BigAutoField(primary_key=True)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="events")
    ts_ms   = models.IntegerField()  # 세션 시작 기준 ms
    type    = models.CharField(max_length=32)  # 'undo','redo','stroke_start','stroke_end',... 등
    details = models.JSONField(null=True, blank=True)  # prev/new, 위치 정보 등

    class Meta:
        db_table = "events"
        # unique_together 제거 (동일 시각 동일 타입 이벤트 허용)
        indexes = [
            models.Index(fields=["session", "ts_ms"]),
            models.Index(fields=["type"]),
        ]
