#!/usr/bin/env python
import os
import json
import sys
import requests
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional

# -------------------------
# 환경 변수 로드
# -------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MATHPIX_APP_ID = os.getenv("MATHPIX_APP_ID")
MATHPIX_APP_KEY = os.getenv("MATHPIX_APP_KEY")

# -------------------------
# Pydantic 스키마 정의
# -------------------------
class SolutionStep(BaseModel):
    """
    풀이 단계를 나타내는 스키마

    Attributes:
        step_number (int): 단계 번호 (1부터 시작)
        description (str): 해당 단계의 설명
    """
    step_number: int
    description: str

class ProblemData(BaseModel):
    """
    문제 데이터 전체 스키마

    Attributes:
        grade (str, optional): 학년 정보
        problem (str): 문제 본문
        choices (List[str]): 선택지 리스트 (객관식이 아닐 경우 빈 리스트)
        difficulty (int): 난이도 (1-100)
        solution_steps (List[SolutionStep]): 풀이 단계 리스트
    """
    grade: Optional[str]
    problem: str
    choices: List[str]
    difficulty: int
    solution_steps: List[SolutionStep]

# -------------------------
# Mathpix OCR 함수
# -------------------------
def extract_from_mathpix(image_path: str):
    r = requests.post(
        "https://api.mathpix.com/v3/text",
        files={"file": open(image_path, "rb")},
        data={
            "options_json": json.dumps({
                "ocr": ["math", "text"],
                "math_inline_delimiters": ["$", "$"],
                "math_display_delimiters": ["$$", "$$"],
                "rm_spaces": True,
                "formats": ["latex_styled", "text"],
                "alphabets_allowed": {"ko": True},
                "numbers_default_to_math": True,
                "include_line_data": True
            }, ensure_ascii=False)
        },
        headers={"app_id": MATHPIX_APP_ID, "app_key": MATHPIX_APP_KEY}
    )

    result = r.json()
    problem_text = result.get("text", "")

    # # 보기 추출
    # choices = [line.strip() for line in problem_text.splitlines() if line.strip().startswith("(")]

    # 그림 영역 잘라내기
    seperate_img = None
    diagram_coords = []
    for block in result.get("line_data", []):
        if block.get("type") in ["chart", "diagram"] and block.get("cnt"):
            xs = [p[0] for p in block["cnt"]]
            ys = [p[1] for p in block["cnt"]]
            diagram_coords.append((min(xs), min(ys), max(xs), max(ys)))

    if diagram_coords:
        left   = min(c[0] for c in diagram_coords)
        upper  = min(c[1] for c in diagram_coords)
        right  = max(c[2] for c in diagram_coords)
        lower  = max(c[3] for c in diagram_coords)

        img = Image.open(image_path)
        cropped = img.crop((left, upper, right, lower))

        # 메모리 바이트로 반환
        buf = BytesIO()
        cropped.save(buf, format="PNG")
        seperate_img = buf.getvalue()

    return problem_text, seperate_img

# -------------------------
# OpenAI API로 JSON 구조화
# -------------------------
def structure_with_openai(problem_name, problem_text):
    """
    OpenAI API를 사용하여 추출된 문제 텍스트를 구조화된 JSON 형태로 변환합니다.

    Args:
        problem_name (str): 문제 제목
        problem_text (str): Mathpix OCR로 추출된 문제 텍스트

    Returns:
        dict: 구조화된 문제 데이터 (problem, choices, difficulty, solution_steps 포함)
    """
    system_prompt = """
입력으로 문제이름, 문제 내용이 주어지면 아래 규칙에 따라 추출하세요:

1. 'problem' : 문제 본문만 추출 (문제 번호와 [점수] 같은 부분은 제거)
2. 'choices' : 보기가 있으면 리스트로 추출. 없으면 빈 리스트.
3. 'difficulty' : 문제의 난이도를 1~100 사이 정수로 추정하세요.
4. 'solution_steps' : 문제 풀이를 난이도에 따라 3~5단계로 나누어 작성하세요.
   - 반드시 JSON 배열 형태로 작성하세요.
   - 각 단계는 {"step_number": 숫자, "description": "설명"} 형태의 객체입니다.
   - step_number는 1부터 시작하는 정수입니다.
   - description에는 풀이 "흐름"만 설명하세요.
   - 수식 전개, 계산 결과, 정답 번호는 절대로 말하지 마세요.
   - 예: {"step_number": 1, "description": "구의 부피 공식을 세운다"}
   - 설명은 학생이 이해하기 쉽게 따뜻한 말투로 하세요.
"""

    user_prompt = f"""
문제 이름: {problem_name}
문제:
{problem_text}
"""

    response = client.responses.parse(
        model="gpt-5-nano",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        text_format=ProblemData
    )

    return response.output_parsed.model_dump()

# -------------------------
# 최종 함수
# -------------------------
def process_problem(problem_name: str, original_img_path: str):
    """
    문제 이미지를 처리하여 구조화된 데이터를 반환합니다.

    Args:
        problem_name (str): 문제 제목
        original_img_path (str): 원본 이미지 파일 경로

    Returns:
        dict: 처리된 문제 데이터
            - seperate_img (bytes): 분리된 도표 이미지 데이터 (없으면 None)
            - difficulty (int): 문제 난이도 (1-100)
            - problem (str): 문제 본문, 문제 본문은 점수와 번호를 제거하고 적을 것.
            - description (list[dict]): 풀이 단계 리스트, 각 항목은 {"step_number": int, "description": str}
            - choices (list[str]): 선택지 리스트 (없으면 빈 리스트)
    """
    # 1. Mathpix OCR로 텍스트 및 도표 추출
    problem_text, seperate_img = extract_from_mathpix(original_img_path)

    # 2. OpenAI로 구조화
    structured = structure_with_openai(problem_name, problem_text)

    # 3. solution_steps를 dict 리스트로 변환
    # OpenAI 응답이 이미 dict 형태일 수도 있고 Pydantic 모델일 수도 있음
    solution_steps_dict = []
    for step in structured["solution_steps"]:
        if isinstance(step, dict):
            # 이미 dict 형태인 경우
            solution_steps_dict.append({
                "step_number": step.get("step_number", 0),
                "description": step.get("description", "")
            })
        else:
            # Pydantic 모델인 경우
            solution_steps_dict.append({
                "step_number": step.step_number,
                "description": step.description
            })

    return {
        "seperate_img": seperate_img,   # 바이트 데이터 (도표가 없으면 None)
        "difficulty": structured["difficulty"],
        "problem": structured["problem"],
        "description": solution_steps_dict,  # [{"step_number": 1, "description": "..."}, ...]
        "choices": structured["choices"],
    }

# -------------------------
# 실행부 (터미널 인자)
# -------------------------
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python mathpix.py '문제이름' '이미지경로'")
        sys.exit(1)

    problem_name = sys.argv[1]
    img_path = sys.argv[2]

    result = process_problem(problem_name, img_path)

    # seperate_img는 길이만 출력
    print(json.dumps(
        {k: (f"<이미지 {len(v)} bytes>" if k == "seperate_img" and v else None) if k == "seperate_img" else v
         for k, v in result.items()},
        ensure_ascii=False,
        indent=2
    ))
