from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponseBadRequest
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction, IntegrityError
import os
import tempfile
import boto3
from botocore.exceptions import ClientError
from .models import Category, Question
from mathpix import process_problem


def health(request):
    return JsonResponse({"status": "ok"})


@staff_member_required
def problem_upload(request):
    """
    문제 업로드 뷰 (superuser만 접근 가능)

    GET: 업로드 폼 렌더링
    POST: 문제 이미지를 처리하여 DB와 S3에 저장
    """
    if request.method == "GET":
        return render(request, "problems/upload.html")

    # =====================
    # POST: 문제 업로드 처리
    # =====================

    # 1. 폼 데이터 추출
    problem_title = request.POST.get("problem_title", "").strip()
    subject = request.POST.get("subject", "").strip()
    unit = request.POST.get("unit", "").strip()
    answer = request.POST.get("problem_answer", "").strip()
    uploaded_file = request.FILES.get("problem_file")

    # 2. 입력 검증
    if not problem_title:
        return render(request, "problems/error.html", {
            "error_title": "입력 오류",
            "error_message": "문제 제목을 입력해주세요."
        })

    if not subject:
        return render(request, "problems/error.html", {
            "error_title": "입력 오류",
            "error_message": "과목을 선택해주세요."
        })

    if not unit:
        return render(request, "problems/error.html", {
            "error_title": "입력 오류",
            "error_message": "단원을 선택해주세요."
        })

    if not answer:
        return render(request, "problems/error.html", {
            "error_title": "입력 오류",
            "error_message": "정답을 입력해주세요."
        })

    if not uploaded_file:
        return render(request, "problems/error.html", {
            "error_title": "입력 오류",
            "error_message": "문제 파일을 업로드해주세요."
        })

    # 3. 임시 파일로 저장 (Mathpix가 파일 경로를 필요로 함)
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
            temp_file_path = temp_file.name

        # 4. Mathpix OCR + OpenAI 구조화 처리
        try:
            processed_data = process_problem(problem_title, temp_file_path)
        except Exception as e:
            return render(request, "problems/error.html", {
                "error_title": "문제 처리 실패",
                "error_message": f"문제 이미지를 분석하는 중 오류가 발생했습니다: {str(e)}"
            })

        # 4-1. OpenAI 응답 데이터 검증
        required_keys = ["difficulty", "problem", "choices", "description", "seperate_img"]
        missing_keys = [key for key in required_keys if key not in processed_data]
        if missing_keys:
            return render(request, "problems/error.html", {
                "error_title": "데이터 구조 오류",
                "error_message": f"AI 응답에서 필수 데이터가 누락되었습니다: {', '.join(missing_keys)}"
            })

        # difficulty 범위 검증
        if not isinstance(processed_data["difficulty"], int) or not (1 <= processed_data["difficulty"] <= 100):
            return render(request, "problems/error.html", {
                "error_title": "데이터 검증 오류",
                "error_message": f"난이도 값이 올바르지 않습니다: {processed_data.get('difficulty')}"
            })

        # description이 리스트인지 검증
        if not isinstance(processed_data["description"], list):
            return render(request, "problems/error.html", {
                "error_title": "데이터 구조 오류",
                "error_message": "풀이 단계 데이터 형식이 올바르지 않습니다."
            })

        # choices가 리스트인지 검증
        if not isinstance(processed_data["choices"], list):
            return render(request, "problems/error.html", {
                "error_title": "데이터 구조 오류",
                "error_message": "선택지 데이터 형식이 올바르지 않습니다."
            })

        # 5. Category 조회 (unit 값은 1~40의 숫자)
        try:
            category = Category.objects.get(id=int(unit))
        except (ValueError, Category.DoesNotExist):
            return render(request, "problems/error.html", {
                "error_title": "카테고리 오류",
                "error_message": f"유효하지 않은 단원 번호입니다: {unit}"
            })

        # 6. DB 저장 (이미지 URL은 나중에 업데이트)
        try:
            with transaction.atomic():
                question = Question.objects.create(
                    name=problem_title,
                    category=category,
                    difficulty=processed_data["difficulty"],
                    problem=processed_data["problem"],
                    choices=processed_data["choices"],
                    description=processed_data["description"],
                    answer=answer,
                    original_img="",  # S3 업로드 후 업데이트
                    separate_img=""   # S3 업로드 후 업데이트
                )
                question_id = question.id
        except IntegrityError as e:
            # UNIQUE 제약 위반 (중복된 문제 제목)
            if 'unique' in str(e).lower() or 'duplicate' in str(e).lower():
                return render(request, "problems/error.html", {
                    "error_title": "중복된 문제 제목",
                    "error_message": f"'{problem_title}' 제목은 이미 사용 중입니다. 다른 제목을 입력해주세요."
                })
            else:
                return render(request, "problems/error.html", {
                    "error_title": "데이터베이스 저장 실패",
                    "error_message": f"데이터 무결성 오류: {str(e)}"
                })
        except Exception as e:
            return render(request, "problems/error.html", {
                "error_title": "데이터베이스 저장 실패",
                "error_message": f"문제를 데이터베이스에 저장하는 중 오류가 발생했습니다: {str(e)}"
            })

        # 7. S3 업로드
        try:
            # 환경 변수 검증
            aws_region = os.getenv('AWS_S3_REGION_NAME')
            aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
            aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME')

            if not all([aws_region, aws_access_key, aws_secret_key, bucket_name]):
                raise ValueError("AWS 환경 변수가 설정되지 않았습니다.")

            s3_client = boto3.client(
                's3',
                region_name=aws_region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )

            # 원본 이미지 업로드
            original_key = f"questions/{question_id}_original{os.path.splitext(uploaded_file.name)[1]}"
            with open(temp_file_path, 'rb') as f:
                s3_client.upload_fileobj(f, bucket_name, original_key)
            original_url = f"https://{bucket_name}.s3.{aws_region}.amazonaws.com/{original_key}"

            # 분리된 이미지 업로드 (있는 경우)
            separate_url = ""
            if processed_data.get("seperate_img"):
                separate_key = f"questions/{question_id}_separate.png"
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=separate_key,
                    Body=processed_data["seperate_img"],
                    ContentType='image/png'
                )
                separate_url = f"https://{bucket_name}.s3.{aws_region}.amazonaws.com/{separate_key}"

        except Exception as e:
            # S3 업로드 실패 시 DB 레코드 삭제
            Question.objects.filter(id=question_id).delete()
            return render(request, "problems/error.html", {
                "error_title": "S3 업로드 실패",
                "error_message": f"이미지를 S3에 업로드하는 중 오류가 발생했습니다: {str(e)}"
            })

        # 8. DB 업데이트 (이미지 URL)
        try:
            question.original_img = original_url
            question.separate_img = separate_url
            question.save()
        except Exception as e:
            return render(request, "problems/error.html", {
                "error_title": "데이터베이스 업데이트 실패",
                "error_message": f"이미지 URL을 저장하는 중 오류가 발생했습니다: {str(e)}"
            })

    finally:
        # 9. 임시 파일 삭제
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass  # 임시 파일 삭제 실패는 무시

    # 10. 성공 페이지 렌더링
    return render(
        request,
        "problems/upload_result.html",
        {
            "question_id": question_id,
            "problem_title": problem_title,
            "subject": subject,
            "unit": category.name,
            "answer": answer,
            "difficulty": processed_data["difficulty"],
            "problem": processed_data["problem"],
            "choices": processed_data["choices"],
            "description": processed_data["description"],
            "original_img_url": original_url,
            "separate_img_url": separate_url if separate_url else None,
            "has_separate_img": bool(processed_data["seperate_img"])
        },
    )