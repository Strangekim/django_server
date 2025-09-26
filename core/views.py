from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponseBadRequest


def health(request):
    return JsonResponse({"status": "ok"})

# 학년별 단원(예시) — 템플릿에도 동일 키로 렌더링해서 탭 생성
GRADE_UNITS = {
    "고1": [
        ("공통수학1-다항식", "공통수학1 - 다항식"),
        ("공통수학1-방정식부등식", "공통수학1 - 방정식과 부등식"),
        ("공통수학1-경우의수", "공통수학1 - 경우의 수"),
        ("공통수학1-행렬", "공통수학1 - 행렬"),
        ("공통수학2-도형의방정식", "공통수학2 - 도형의 방정식"),
        ("공통수학2-집합과명제", "공통수학2 - 집합과 명제"),
        ("공통수학2-함수와그래프", "공통수학2 - 함수와 그래프"),
    ],
    "고2": [
        ("대수-지수로그", "대수 - 지수/로그"),
        ("대수-삼각함수", "대수 - 삼각함수"),
        ("대수-수열", "대수 - 수열"),
        ("미적분1-극한연속", "미적분 I - 극한과 연속"),
        ("미적분1-미분", "미적분 I - 미분"),
        ("미적분1-적분", "미적분 I - 적분"),
        ("확통-경우의수", "확률과 통계 - 경우의 수"),
        ("확통-확률", "확률과 통계 - 확률"),
        ("확통-통계", "확률과 통계 - 통계"),
    ],
    "고3": [
        ("기하-벡터좌표", "기하 - 벡터/좌표"),
        ("기하-이차곡선", "기하 - 이차곡선"),
        ("미적분2-심화미분적분", "미적분 II - 심화 미분/적분"),
        ("경제수학-기초", "경제수학 - 기초"),
        ("인공지능수학-개론", "인공지능 수학 - 개론"),
    ],
}

CURRICULUM_CHOICES = [
    ("2022", "2022 개정(2025 적용)"),
    ("2015", "2015 개정"),
    ("기타", "기타/학교자율"),
]

def problem_upload(request):
    if request.method == "GET":
        first_grade = next(iter(GRADE_UNITS.keys()))
        return render(
            request,
            "problems/upload.html",
            {
                "grade_units": GRADE_UNITS,
                "first_grade": first_grade,
            },
        )

    # POST
    grade = request.POST.get("grade")
    unit = request.POST.get("unit")
    file = request.FILES.get("problem_file")

    if not grade or not unit or grade not in GRADE_UNITS:
        return HttpResponseBadRequest("학년/단원 선택이 올바르지 않습니다.")
    valid_units = {u[0] for u in GRADE_UNITS[grade]}
    if unit not in valid_units:
        return HttpResponseBadRequest("선택한 단원이 해당 학년에 속하지 않습니다.")

    return render(
        request,
        "problems/upload_result.html",
        {
            "grade": grade,
            "unit": unit,
            "filename": getattr(file, "name", None),
            "has_file": file is not None,
        },
    )