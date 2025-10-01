"""
API 뷰 모듈

정적 프론트엔드에서 호출할 REST API 엔드포인트들을 제공합니다.
모든 응답은 JSON 형식으로 반환됩니다.
"""

import os
import json
import requests
import uuid
import gzip
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional
from core.models import Question, Category
from api.models import Session, Stroke, StrokePoint, Event
import boto3
from botocore.exceptions import ClientError

# OpenAI 클라이언트 초기화
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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
def get_question_detail(request, question_id):
    """
    특정 문제의 상세 정보를 반환하는 API

    정답과 원본 이미지를 제외한 모든 정보를 반환합니다.
    문제 풀이 화면에서 사용됩니다.

    **엔드포인트**: GET /api/questions/<question_id>/

    **URL 파라미터**:
    - question_id (int): 조회할 문제의 ID

    **성공 응답** (200):
    ```json
    {
        "success": true,
        "data": {
            "id": 1,
            "name": "2025_고1_3월 모의고사_1번",
            "category": {
                "id": 1,
                "name": "다항식"
            },
            "difficulty": 45,
            "problem": "문제 본문 텍스트...",
            "choices": ["선택지1", "선택지2", "선택지3", "선택지4", "선택지5"],
            "description": [
                {
                    "step_number": 1,
                    "description": "주어진 조건을 식으로 나타낸다"
                },
                {
                    "step_number": 2,
                    "description": "식을 정리하여 미지수를 구한다"
                }
            ],
            "separate_img": "https://s3.../separate.png",
            "created_at": "2025-01-15T10:30:00Z",
            "updated_at": "2025-01-15T10:30:00Z"
        }
    }
    ```

    **에러 응답** (404):
    ```json
    {
        "success": false,
        "error": "문제를 찾을 수 없습니다."
    }
    ```

    **에러 응답** (500):
    ```json
    {
        "success": false,
        "error": "서버 오류 메시지"
    }
    ```

    Args:
        request: Django HttpRequest 객체
        question_id (int): 조회할 문제의 ID

    Returns:
        JsonResponse: 문제 상세 정보 (정답과 원본 이미지 제외)
    """
    try:
        # 1. 문제 ID로 문제 조회
        try:
            question = Question.objects.select_related('category').get(id=question_id)
        except Question.DoesNotExist:
            # 문제가 존재하지 않는 경우 404 에러 반환
            return JsonResponse({
                "success": False,
                "error": "문제를 찾을 수 없습니다."
            }, status=404, json_dumps_params={'ensure_ascii': False})

        # 2. 응답 데이터 구성
        # 주의: answer(정답)와 original_img(원본 이미지)는 제외
        response_data = {
            "id": question.id,
            "name": question.name,
            # 카테고리 정보
            "category": {
                "id": question.category.id,
                "name": question.category.name
            },
            # 난이도 (1-100)
            "difficulty": question.difficulty,
            # 문제 본문
            "problem": question.problem,
            # 선택지 배열 (객관식인 경우, 주관식이면 빈 배열)
            "choices": question.choices if question.choices else [],
            # 풀이 단계 배열 (각 항목은 step_number와 description 포함)
            "description": question.description if question.description else [],
            # 분리된 도표 이미지 URL (없으면 빈 문자열)
            "separate_img": question.separate_img if question.separate_img else "",
            # 생성 및 수정 시간
            "created_at": question.created_at.isoformat(),
            "updated_at": question.updated_at.isoformat()
        }

        # 3. 성공 응답 반환
        return JsonResponse({
            "success": True,
            "data": response_data
        }, json_dumps_params={'ensure_ascii': False})

    except Exception as e:
        # 4. 예상치 못한 에러 발생 시 500 에러 반환
        return JsonResponse({
            "success": False,
            "error": f"서버 오류가 발생했습니다: {str(e)}"
        }, status=500, json_dumps_params={'ensure_ascii': False})


def save_session_to_db_and_s3(question, session_data, user_answer, is_correct, problem_name, category_id, difficulty):
    """
    세션 데이터를 DB에 저장하고 원본 JSON을 S3에 업로드

    Args:
        question (Question): 문제 객체
        session_data (dict): 프론트엔드에서 전송된 전체 세션 데이터
        user_answer (str): 사용자가 입력한 답안
        is_correct (bool): 정답 여부
        problem_name (str): 문제 이름
        category_id (int): 카테고리 ID
        difficulty (int): 난이도

    Returns:
        tuple: (session_uuid, s3_url)

    Raises:
        Exception: DB 저장 또는 S3 업로드 실패 시
    """
    # 1. 세션 메타데이터 추출
    metadata = session_data.get('metadata', {})
    device_caps = session_data.get('deviceCapabilities', {})
    canvas_data = session_data.get('canvasData', {})
    statistics = session_data.get('statistics', {})

    # 세션 UUID (프론트엔드에서 생성한 것 사용 또는 새로 생성)
    session_uuid = uuid.UUID(metadata.get('sessionId')) if metadata.get('sessionId') else uuid.uuid4()

    # 시작/종료 시간 파싱
    start_time = None
    end_time = None
    if metadata.get('startTime'):
        try:
            start_time = datetime.fromisoformat(metadata['startTime'].replace('Z', '+00:00'))
        except:
            pass
    if metadata.get('endTime'):
        try:
            end_time = datetime.fromisoformat(metadata['endTime'].replace('Z', '+00:00'))
        except:
            pass

    # 2. DB에 데이터 저장 (트랜잭션 사용)
    with transaction.atomic():
        # 2-1. Session 테이블에 메인 레코드 저장
        session = Session.objects.create(
            session_uuid=session_uuid,
            start_time=start_time,
            end_time=end_time,
            duration_ms=metadata.get('duration', 0),

            # 문제 메타데이터
            problem_id=question.id,
            category=category_id or question.category.id,

            # 기기/환경 정보
            user_agent=session_data.get('deviceInfo', {}).get('userAgent', ''),
            platform=session_data.get('deviceInfo', {}).get('platform', ''),
            pixel_ratio=session_data.get('deviceInfo', {}).get('pixelRatio'),
            screen_width=session_data.get('deviceInfo', {}).get('screenSize', {}).get('width'),
            screen_height=session_data.get('deviceInfo', {}).get('screenSize', {}).get('height'),

            # 캔버스 상태
            logical_width=session_data.get('canvasInfo', {}).get('logicalSize', {}).get('width'),
            logical_height=session_data.get('canvasInfo', {}).get('logicalSize', {}).get('height'),
            css_width=session_data.get('canvasInfo', {}).get('cssSize', {}).get('width'),
            css_height=session_data.get('canvasInfo', {}).get('cssSize', {}).get('height'),
            zoom=session_data.get('canvasInfo', {}).get('transform', {}).get('zoom', 1.0),
            pan_x=session_data.get('canvasInfo', {}).get('transform', {}).get('panX', 0),
            pan_y=session_data.get('canvasInfo', {}).get('transform', {}).get('panY', 0),

            # 포인터 기능 지원
            supports_pressure=device_caps.get('pressure', False),
            supports_tilt=device_caps.get('tilt', False),
            supports_twist=device_caps.get('twist', False),
            supports_coalesced=device_caps.get('coalesced', False),

            # 요약 통계
            stroke_count=statistics.get('strokeCount', 0) or len(canvas_data.get('strokes', [])),
            total_distance_px=statistics.get('totalDistance', 0.0),
            average_stroke_length_px=statistics.get('averageStrokeLength'),
            undo_count=statistics.get('undoCount', 0),
            redo_count=statistics.get('redoCount', 0),
            eraser_count=statistics.get('eraserCount', 0),
            zoom_count=statistics.get('zoomCount', 0),
            pan_count=statistics.get('panCount', 0),
            tool_change_count=statistics.get('toolChanges', 0),

            # 사용자 답안
            answer=str(user_answer) if user_answer else None,
            is_correct=is_correct,

            # 지도학습 라벨 (나중에 수동으로 설정 가능)
            label=None
        )

        # 2-2. Stroke 데이터 저장
        strokes_list = canvas_data.get('strokes', [])
        for stroke_data in strokes_list:
            # 스트로크 UUID 생성 또는 추출
            stroke_uuid = uuid.uuid4()

            # 포인트 데이터 추출
            points = stroke_data.get('points', [])

            # bbox 계산
            if points:
                x_coords = [p.get('x', 0) for p in points]
                y_coords = [p.get('y', 0) for p in points]
                bbox_min_x = int(min(x_coords))
                bbox_min_y = int(min(y_coords))
                bbox_max_x = int(max(x_coords))
                bbox_max_y = int(max(y_coords))
            else:
                bbox_min_x = bbox_min_y = bbox_max_x = bbox_max_y = 0

            # 스트로크 생성
            stroke = Stroke.objects.create(
                stroke_uuid=stroke_uuid,
                session=session,
                tool=stroke_data.get('tool', 'pen'),
                color=stroke_data.get('color', '#000000'),
                stroke_width=int(stroke_data.get('strokeWidth', 3)),
                start_ms=int(stroke_data.get('startTime', 0)),
                end_ms=int(stroke_data.get('endTime', 0)),
                pointer_type=stroke_data.get('pointerType', 'pen'),
                is_coalesced=stroke_data.get('coalesced', False),
                total_distance_px=float(stroke_data.get('totalDistance', 0.0)),
                average_speed_pxps=stroke_data.get('averageSpeed'),
                average_pressure=stroke_data.get('averagePressure'),
                bbox_min_x=bbox_min_x,
                bbox_min_y=bbox_min_y,
                bbox_max_x=bbox_max_x,
                bbox_max_y=bbox_max_y
            )

            # 2-3. StrokePoint 데이터 저장 (bulk_create 사용으로 성능 최적화)
            point_objects = []
            for idx, point in enumerate(points):
                point_objects.append(StrokePoint(
                    session=session,
                    stroke=stroke,
                    idx=idx,
                    t_ms=int(point.get('timestamp', 0)),
                    x=int(point.get('x', 0)),
                    y=int(point.get('y', 0)),
                    pressure=point.get('pressure'),
                    tilt_x=point.get('tiltX'),
                    tilt_y=point.get('tiltY'),
                    twist=point.get('twist'),
                    pointer_type=point.get('pointerType', 'pen'),
                    pointer_id=point.get('pointerId'),
                    buttons=point.get('buttons', 0),
                    width=point.get('width'),
                    height=point.get('height')
                ))

            if point_objects:
                StrokePoint.objects.bulk_create(point_objects)

        # 2-4. Event 데이터 저장
        events_list = canvas_data.get('events', [])
        event_objects = []
        for event_data in events_list:
            event_objects.append(Event(
                session=session,
                ts_ms=int(event_data.get('timestamp', 0)),
                type=event_data.get('type', 'unknown'),
                details=event_data.get('details') or {}
            ))

        if event_objects:
            Event.objects.bulk_create(event_objects)

    # 3. S3에 원본 JSON 업로드 (gzip 압축)
    try:
        # AWS 환경 변수 확인
        aws_region = os.getenv('AWS_REGION')
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME')

        if not all([aws_region, aws_access_key, aws_secret_key, bucket_name]):
            raise ValueError("AWS 환경 변수가 설정되지 않았습니다.")

        # S3 클라이언트 생성
        s3_client = boto3.client(
            's3',
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )

        # 전체 세션 데이터에 메타 정보 추가
        upload_data = {
            **session_data,
            "db_session_id": str(session_uuid),
            "problem_id": question.id,
            "problem_name": problem_name,
            "category_name": question.category.name,
            "difficulty": difficulty,
            "user_answer": user_answer,
            "is_correct": is_correct,
            "uploaded_at": datetime.utcnow().isoformat()
        }

        # JSON을 gzip으로 압축
        json_bytes = json.dumps(upload_data, ensure_ascii=False, indent=2).encode('utf-8')
        compressed_data = gzip.compress(json_bytes)

        # S3 키 생성: answers/{problem_id}_{session_uuid}.json.gz
        s3_key = f"answers/{question.id}_{session_uuid}.json.gz"

        # S3 업로드
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=compressed_data,
            ContentType='application/gzip',
            ContentEncoding='gzip',
            Metadata={
                'problem-id': str(question.id),
                'session-id': str(session_uuid),
                'is-correct': str(is_correct)
            }
        )

        # S3 URL 생성
        s3_url = f"https://{bucket_name}.s3.{aws_region}.amazonaws.com/{s3_key}"

        print(f"세션 {session_uuid} 저장 완료 - S3: {s3_url}")

        return session_uuid, s3_url

    except Exception as e:
        # S3 업로드 실패해도 DB 데이터는 유지 (경고만 로깅)
        print(f"S3 업로드 실패 (세션 {session_uuid}): {str(e)}")
        return session_uuid, ""


@require_http_methods(["POST"])
@csrf_exempt
def verify_solution(request):
    """
    사용자의 문제 풀이를 검증하고 데이터를 저장하는 API

    프론트엔드에서 전송된 세션 데이터(필기 기록)를 DB에 저장하고,
    원본 JSON을 S3에 업로드한 후, 사용자 답안의 정확성을 검증합니다.

    **엔드포인트**: POST /api/verify-solution/

    **요청 본문**:
    ```json
    {
        "question_id": 1,
        "problem_name": "2025_고1_3월 모의고사_9번",
        "category_id": 4,
        "category_name": "이차방정식과 이차함수",
        "difficulty": 65,
        "user_answer": {
            "type": "multiple_choice",
            "selectedIndex": 2,
            "selectedValue": "3"
        },
        "session_data": {
            "metadata": {...},
            "deviceCapabilities": {...},
            "canvasData": {
                "strokes": [...],
                "events": [...]
            },
            "statistics": {...}
        }
    }
    ```

    **성공 응답** (200):
    ```json
    {
        "success": true,
        "data": {
            "session_id": "uuid",
            "is_correct": true,
            "verification": {
                "total_score": 85,
                "logic_score": 90,
                "accuracy_score": 80,
                "process_score": 85,
                "is_correct": true,
                "comment": "전반적인 평가",
                "detailed_feedback": "상세 피드백"
            },
            "s3_url": "https://..."
        }
    }
    ```

    Args:
        request: Django HttpRequest 객체 (POST)

    Returns:
        JsonResponse: 검증 결과 및 저장된 세션 ID
    """
    try:
        # 1. 요청 데이터 파싱
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "error": "유효하지 않은 JSON 형식입니다."
            }, status=400, json_dumps_params={'ensure_ascii': False})

        # 2. 필수 파라미터 검증
        question_id = data.get('question_id')
        user_answer = data.get('user_answer')
        session_data = data.get('session_data')

        if not question_id:
            return JsonResponse({
                "success": False,
                "error": "question_id가 필요합니다."
            }, status=400, json_dumps_params={'ensure_ascii': False})

        if not user_answer:
            return JsonResponse({
                "success": False,
                "error": "user_answer가 필요합니다."
            }, status=400, json_dumps_params={'ensure_ascii': False})

        if not session_data:
            return JsonResponse({
                "success": False,
                "error": "session_data가 필요합니다."
            }, status=400, json_dumps_params={'ensure_ascii': False})

        # 3. 문제 조회
        try:
            question = Question.objects.select_related('category').get(id=question_id)
        except Question.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": f"ID {question_id}에 해당하는 문제를 찾을 수 없습니다."
            }, status=404, json_dumps_params={'ensure_ascii': False})

        # 4. 정답 여부 확인 (Question 모델의 answer 필드와 비교)
        user_answer_value = user_answer.get('selectedValue') if user_answer.get('type') == 'multiple_choice' else user_answer.get('answer')
        is_correct = str(user_answer_value).strip() == str(question.answer).strip()

        # 5. DB에 세션 데이터 저장 및 S3 업로드
        try:
            session_id, s3_url = save_session_to_db_and_s3(
                question=question,
                session_data=session_data,
                user_answer=user_answer_value,
                is_correct=is_correct,
                problem_name=data.get('problem_name', ''),
                category_id=data.get('category_id'),
                difficulty=data.get('difficulty')
            )
        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": f"데이터 저장 실패: {str(e)}"
            }, status=500, json_dumps_params={'ensure_ascii': False})

        # 6. OpenAI로 풀이 검증 (선택적 - strokes가 있는 경우만)
        verification_result = None
        strokes = session_data.get('canvasData', {}).get('strokes', [])

        if strokes:
            try:
                # Mathpix로 필기 변환
                converted_text = convert_strokes_to_text(strokes)

                # OpenAI로 풀이 검증
                verification_result = verify_solution_with_openai(
                    question=question,
                    user_solution=converted_text
                )
            except Exception as e:
                # 검증 실패해도 데이터는 저장되었으므로 경고만 로깅
                print(f"풀이 검증 실패 (세션 {session_id}): {str(e)}")
                verification_result = {
                    "total_score": 0,
                    "logic_score": 0,
                    "accuracy_score": 0,
                    "process_score": 0,
                    "is_correct": is_correct,
                    "comment": "풀이 검증에 실패했습니다.",
                    "detailed_feedback": str(e)
                }

        # 7. 성공 응답 반환
        return JsonResponse({
            "success": True,
            "data": {
                "session_id": str(session_id),
                "is_correct": is_correct,
                "verification": verification_result or {
                    "total_score": 100 if is_correct else 0,
                    "logic_score": 0,
                    "accuracy_score": 0,
                    "process_score": 0,
                    "is_correct": is_correct,
                    "comment": "정답" if is_correct else "오답",
                    "detailed_feedback": "필기 데이터가 없어 자동 검증되지 않았습니다."
                },
                "s3_url": s3_url
            }
        }, json_dumps_params={'ensure_ascii': False})

    except Exception as e:
        # 예상치 못한 에러
        import traceback
        traceback.print_exc()
        return JsonResponse({
            "success": False,
            "error": f"서버 오류가 발생했습니다: {str(e)}"
        }, status=500, json_dumps_params={'ensure_ascii': False})


def convert_strokes_to_text(strokes):
    """
    Mathpix Strokes API를 사용하여 필기 데이터를 텍스트로 변환

    Args:
        strokes (list): 필기 stroke 배열
            [
                {
                    "id": "stroke_1",
                    "points": [[x, y, timestamp], ...]
                },
                ...
            ]

    Returns:
        str: 변환된 텍스트 (LaTeX 및 일반 텍스트 포함)

    Raises:
        Exception: Mathpix API 호출 실패 시
    """
    # Mathpix API 자격 증명
    app_id = os.getenv('MATHPIX_APP_ID')
    app_key = os.getenv('MATHPIX_APP_KEY')

    if not app_id or not app_key:
        raise Exception("Mathpix API 자격 증명이 설정되지 않았습니다.")

    # Mathpix Strokes API 엔드포인트
    url = "https://api.mathpix.com/v3/strokes"

    # 요청 헤더
    headers = {
        'app_id': app_id,
        'app_key': app_key,
        'Content-Type': 'application/json'
    }

    # 요청 본문
    payload = {
        'strokes': strokes,
        'alphabet': 'all',  # 모든 문자 인식 (수식, 한글, 영어 등)
        'mode': 'text'  # 텍스트 형식으로 반환
    }

    # API 호출
    response = requests.post(url, headers=headers, json=payload, timeout=30)

    # 응답 확인
    if response.status_code != 200:
        error_message = response.json().get('error', 'Unknown error')
        raise Exception(f"Mathpix API 오류 (status {response.status_code}): {error_message}")

    # 변환된 텍스트 추출
    result = response.json()
    converted_text = result.get('text', '')

    if not converted_text:
        raise Exception("Mathpix API가 텍스트를 변환하지 못했습니다.")

    return converted_text


# Pydantic 스키마 정의
class SolutionVerification(BaseModel):
    """
    풀이 검증 결과 스키마

    Attributes:
        total_score (int): 총점 (0-100)
        logic_score (int): 논리성 점수 (0-100)
        accuracy_score (int): 정확성 점수 (0-100)
        process_score (int): 풀이 과정 점수 (0-100)
        is_correct (bool): 정답 여부
        comment (str): 전반적인 평가 코멘트
        detailed_feedback (str): 단계별 상세 피드백
    """
    total_score: int
    logic_score: int
    accuracy_score: int
    process_score: int
    is_correct: bool
    comment: str
    detailed_feedback: str


def verify_solution_with_openai(question, user_solution):
    """
    OpenAI를 사용하여 사용자의 풀이를 검증

    Args:
        question (Question): 문제 객체 (DB 모델)
        user_solution (str): 사용자가 작성한 풀이 (텍스트 형태)

    Returns:
        dict: 검증 결과
            {
                "total_score": 85,
                "logic_score": 90,
                "accuracy_score": 80,
                "process_score": 85,
                "is_correct": true,
                "comment": "평가 코멘트",
                "detailed_feedback": "상세 피드백"
            }

    Raises:
        Exception: OpenAI API 호출 실패 시
    """
    # 시스템 프롬프트: AI의 역할 정의
    system_prompt = """
당신은 수학 문제 풀이를 평가하는 전문 교사입니다.

학생의 풀이를 다음 기준으로 평가하세요:

1. **logic_score (논리성, 0-100점)**:
   - 풀이 과정의 논리적 흐름이 올바른가?
   - 각 단계가 이전 단계에서 자연스럽게 이어지는가?
   - 수학적 추론이 타당한가?

2. **accuracy_score (정확성, 0-100점)**:
   - 최종 답이 정답과 일치하는가?
   - 계산이 정확한가?
   - 수식 표현이 올바른가?

3. **process_score (풀이 과정, 0-100점)**:
   - 문제를 해결하기 위한 적절한 방법을 사용했는가?
   - 필요한 단계를 빠짐없이 수행했는가?
   - 불필요한 단계는 없는가?

4. **total_score (총점, 0-100점)**:
   - 위 세 점수를 종합한 점수
   - 가중치: logic_score(40%) + accuracy_score(40%) + process_score(20%)

5. **is_correct (정답 여부, boolean)**:
   - total_score가 60점 이상이면 true, 아니면 false

[중요 주의사항]
- 필기 인식 과정에서 발생할 수 있는 OCR 오류를 고려하세요.
- 예: "x²"가 "x2"로 인식되거나, "÷"가 "/"로 인식될 수 있음
- 의도가 명확하다면 사소한 표기 오류는 감점하지 마세요.
- 학생이 이해하기 쉬운 친절한 톤으로 피드백을 작성하세요.

**comment**: 2-3줄의 전반적인 평가 (긍정적인 부분과 개선점 포함)
**detailed_feedback**: 각 단계별로 구체적인 피드백 (좋은 점, 실수한 부분, 개선 방법)
"""

    # 사용자 프롬프트: 문제와 풀이 제공
    user_prompt = f"""
[문제]
{question.problem}

[정답]
{question.answer}

[선택지]
{', '.join(question.choices) if question.choices else '(주관식)'}

[모범 풀이 단계]
{chr(10).join([f"{step.get('step_number', i+1)}단계: {step.get('description', '')}" for i, step in enumerate(question.description)])}

[학생의 풀이]
{user_solution}

위 정보를 바탕으로 학생의 풀이를 평가해주세요.
"""

    # OpenAI API 호출
    response = openai_client.responses.parse(
        model="gpt-5-nano",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        text_format=SolutionVerification
    )

    # 결과 파싱 및 반환
    result = response.output_parsed.model_dump()
    return result


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
