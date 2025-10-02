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
입력으로 문제이름, 문제 내용이 주어지면 아래 규칙에 따라 반드시 정확하게 추출하세요.

[필수] 모든 필드는 반드시 포함되어야 하며, 데이터 타입을 엄격히 준수하세요.

[LaTeX 수식 형식화 규칙 - 최우선 적용]
모든 수학 수식은 반드시 LaTeX 형식 $...$ 또는 $$...$$ 로 감싸야 합니다.

▶ 단일 수식 변수 (인라인):
  - 수학 변수: $x$, $y$, $a$, $b$, $n$ 등
  - 예외: 일반 텍스트로 사용된 경우는 제외 (예: "a는 상수", "b번 항목")
  - 판단 기준: 문맥상 수학적 의미를 갖는 경우만 LaTeX 처리

▶ 연산식 (인라인):
  - 사칙연산: $x + a$, $x - 3$, $2x$, $x/2$
  - 거듭제곱: $x^2$, $x^{2}$, $a^n$, $2^{10}$
  - 복잡한 식: $x^2 + bx + 6$, $(x+a)(x-3)$
  - 함수: $f(x)$, $g(x)$, $\sin(x)$, $\log(n)$

▶ 곱셈 표현:
  - 변수의 곱: $ab$, $xyz$, $2xy$
  - 괄호와 변수: $(x+1)(x-2)$
  - 계수와 변수: $3x$, $-2y$

▶ 분수:
  - 간단한 분수: $\frac{1}{2}$, $\frac{3}{4}$, $\frac{x}{y}$
  - 복잡한 분수: $\frac{x+1}{x-1}$, $\frac{a^2 + b^2}{2}$

▶ 루트/근호:
  - 제곱근: $\sqrt{2}$, $\sqrt{x}$, $\sqrt{x^2 + y^2}$
  - n제곱근: $\sqrt[3]{8}$, $\sqrt[n]{x}$

▶ 절댓값:
  - 절댓값: $|x|$, $|x-2|$, $|a+b|$

▶ 집합/부등식:
  - 부등식: $x > 0$, $x \leq 10$, $a < b$
  - 집합: $\{1, 2, 3\}$, $x \in \mathbb{R}$

▶ 그리스 문자:
  - $\alpha$, $\beta$, $\theta$, $\pi$, $\sigma$

▶ 복잡한 수식 (블록):
  - 여러 줄이거나 중요한 수식: $$x^2 + 2x + 1 = 0$$

▶ 혼합 텍스트 예시:
  ✅ 올바른 예:
  "다항식 $(x+a)(x-3)$을 전개한 식이 $x^2+bx+6$일 때, $ab$의 값은? (단, $a$, $b$는 상수이다.)"
  "함수 $f(x) = x^2 + 2x + 1$이 있을 때, $f(2)$의 값을 구하시오."
  "$\log_2(8) + \sqrt{16}$의 값은?"
  "$2^n > 1000$을 만족하는 최소 자연수 $n$을 구하시오."

  ❌ 잘못된 예:
  "다항식 (x+a)(x-3)을 전개한 식이 x^2+bx+6일 때, ab의 값은? (단, a, b는 상수이다.)"
  "함수 f(x) = x^2 + 2x + 1이 있을 때, f(2)의 값을 구하시오."

▶ 일반 텍스트와 구분:
  - "a는 상수이다" → "a는 상수이다" (수식이 아닌 설명)
  - "변수 a" → "변수 $a$" (수학적 의미)
  - "1번 문제" → "1번 문제" (숫자가 수식이 아님)
  - "값은 30이다" → "값은 30이다" (결과 숫자는 일반 텍스트)
  - 하지만 "값은 $2^5 = 32$이다" → 수식 부분만 LaTeX

1. 'problem' (필수, 문자열 타입)
   [중요] problem 추출 규칙:

   ▶ 반드시 제거해야 할 메타정보:
   - 문제 번호: "1.", "2.", "5번", "3)", "문제 1" 등 → 완전히 제거
   - 배점 표시: "[3점]", "[4점]", "(2점)", "2점" 등 → 완전히 제거
   - 평가영역: "[계산]", "[이해]", "[적용]" 등 → 완전히 제거
   - 난이도: "[상]", "[중]", "[하]" 등 → 완전히 제거
   - 그래프 축 레이블: "(명)", "(cm)", "(개)", "(kg)" 등 단독으로 나오는 단위 → 제거
   - 특수 기호: "+", "-", "*", "=" 등이 줄 끝에 단독으로 있는 경우 → 제거
   - 불필요한 공백 줄, 탭 문자 → 모두 제거

   ▶ 문제 본문 추출 범위:
   - 시작: 메타정보를 모두 제거한 후 실제 문제 내용이 시작되는 부분부터
   - 끝: 질문이 완료되는 지점까지만 포함
   - 질문 종결 패턴: "~구하시오.", "~구하여라.", "~값은?", "~개수는?", "~얼마인가?", "~몇인가?", "~무엇인가?" 등
   - 보기(선택지)가 시작되기 직전까지만 포함
   - 보기 시작 패턴: "①", "②", "(1)", "(2)", "가.", "나." 등

   ▶ 텍스트 정제:
   - 연속된 공백은 하나의 공백으로 통일
   - 문장 간 줄바꿈은 유지하되, 불필요한 빈 줄은 제거
   - 문장이 자연스럽게 이어지도록 정리
   - OCR 오류로 인한 오타가 명확한 경우 수정 (예: "학큽" → "학급", "학셩" → "학생")

   ▶ [LaTeX 적용] 문제 본문의 모든 수식은 위 LaTeX 규칙에 따라 반드시 형식으로 감싸세요.

   ▶ 올바른 변환 예시:
   입력: "5. 어느 학큽 학생들의 키를 조사하여 나타낸 도수분포다각형이 그림과 같다.+\n(명)\n\n이 학셩들 중 키가 160 cm 이상인 학셩의 수는? [3점]"
   출력: "어느 학급 학생들의 키를 조사하여 나타낸 도수분포다각형이 그림과 같다. 이 학생들 중 키가 $160 \mathrm{~cm}$ 이상인 학생의 수는?"

   입력: "1. 다항식 (x+a)(x-3)을 전개한 식이 x^2+bx+6일 때, ab의 값은? (단, a, b는 상수이다.) [4점]\n+ (1) 30 (2) 32..."
   출력: "다항식 $(x+a)(x-3)$을 전개한 식이 $x^2+bx+6$일 때, $ab$의 값은? (단, $a$, $b$는 상수이다.)"

   ▶ 예외 처리:
   - 문제 본문을 찾을 수 없다면: "문제 내용을 추출할 수 없습니다" 반환
   - 빈 문자열("")은 절대 반환하지 마세요

2. 'choices' (필수, 문자열 배열 타입)
   [중요] choices 추출 규칙:
   - 반드시 배열 형태로 반환하세요. 보기가 없으면 빈 배열 []을 반환하세요.
   - 보기 번호나 기호((1), (2), ①, ②, 가, 나 등)는 절대로 포함하지 마세요.
   - 보기의 실제 내용만 추출하세요.
   - [LaTeX 적용] 선택지에 수식이 포함된 경우 반드시 LaTeX 형식으로 감싸세요.
   - 예시:
     * 단순 분수: ["$\\frac{3}{8}$", "$\\frac{1}{2}$", "$\\frac{5}{8}$", "$\\frac{3}{4}$", "$\\frac{7}{8}$"]
     * 단순 숫자: ["30", "32", "34", "36", "38"]
     * 수식 포함: ["$x+2$", "$x-2$", "$2x$", "$\\frac{x}{2}$"]
     * 복잡한 수식: ["$x^2 + 2x + 1$", "$x^2 - 1$", "$(x+1)^2$", "$x(x+2)$"]
     * 혼합 예시: ["$2\\pi r$", "$\\pi r^2$", "$4\\pi r^2$", "$\\frac{4}{3}\\pi r^3$"]

3. 'difficulty' (필수, 정수 타입, 범위: 1-100)
   - 문제의 난이도를 1에서 100 사이의 정수로 반드시 추정하세요.
   - 1~100 범위를 벗어나거나 정수가 아닌 값은 절대 반환하지 마세요.
   - 난이도를 판단할 수 없다면 50을 반환하세요.

4. 'solution_steps' (필수, 객체 배열 타입)
   [중요] 반드시 3개 이상 5개 이하의 단계를 생성하세요.
   - 각 단계는 반드시 {"step_number": 정수, "description": "문자열"} 형태의 객체입니다.
   - step_number는 1부터 시작하며, 순차적으로 증가해야 합니다.
   - description에는 풀이 "흐름"만 설명하세요.
   - [LaTeX 적용] description에 수식이 포함된 경우 반드시 LaTeX 형식으로 감싸세요.
   - 수식 전개, 계산 결과, 정답 번호는 절대로 말하지 마세요.
   - 예시:
     * [{"step_number": 1, "description": "구의 부피 공식 $V = \\frac{4}{3}\\pi r^3$을 세운다"},
        {"step_number": 2, "description": "원기둥의 부피 $V = \\pi r^2 h$와 비교한다"}]
     * [{"step_number": 1, "description": "다항식 $(x+a)(x-3)$을 전개한다"},
        {"step_number": 2, "description": "전개한 식과 $x^2+bx+6$을 계수 비교한다"},
        {"step_number": 3, "description": "$a$와 $b$의 값을 구한 후 $ab$를 계산한다"}]
   - 설명은 학생이 이해하기 쉽게 따뜻한 말투로 하세요.
   - 빈 배열이나 null을 반환하지 마세요. 반드시 최소 3개의 단계를 생성하세요.

[중요] 위의 모든 필드(problem, choices, difficulty, solution_steps)는 필수이며, 누락되거나 null이면 안 됩니다.
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
