#!/usr/bin/env python
"""
GitHub Issue 자동 생성 스크립트

커밋 메시지에 [issue], [bug], [fix] 키워드가 포함되어 있으면
자동으로 GitHub issue를 생성합니다.

사용법:
    python scripts/auto_issue.py              # 최근 커밋에 대해 실행
    python scripts/auto_issue.py <commit-hash>  # 특정 커밋에 대해 실행
"""

import os
import sys
import subprocess
import requests
from datetime import datetime
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO_OWNER = os.getenv("GITHUB_REPO_OWNER")
GITHUB_REPO_NAME = os.getenv("GITHUB_REPO_NAME")

# 키워드와 라벨 매핑
KEYWORD_LABELS = {
    "[issue]": ["auto-generated"],
    "[bug]": ["bug", "auto-generated"],
    "[fix]": ["fix", "auto-generated"],
}


def get_commit_info(commit_hash="HEAD"):
    """
    커밋 정보를 가져옵니다.

    Args:
        commit_hash (str): 커밋 해시 (기본값: HEAD - 최근 커밋)

    Returns:
        dict: 커밋 정보
            - hash: 커밋 해시 (짧은 형식)
            - message: 커밋 메시지
            - author: 작성자
            - date: 날짜
            - changed_files: 변경된 파일 목록
            - diff: 변경 내용 (diff)
    """
    try:
        # 커밋 해시 (짧은 형식)
        commit_hash_short = subprocess.check_output(
            ["git", "log", "-1", "--pretty=%h", commit_hash],
            stderr=subprocess.DEVNULL
        ).decode().strip()

        # 커밋 메시지
        commit_message = subprocess.check_output(
            ["git", "log", "-1", "--pretty=%B", commit_hash],
            stderr=subprocess.DEVNULL
        ).decode().strip()

        # 작성자
        author = subprocess.check_output(
            ["git", "log", "-1", "--pretty=%an <%ae>", commit_hash],
            stderr=subprocess.DEVNULL
        ).decode().strip()

        # 날짜
        date = subprocess.check_output(
            ["git", "log", "-1", "--pretty=%ai", commit_hash],
            stderr=subprocess.DEVNULL
        ).decode().strip()

        # 변경된 파일 목록
        changed_files = subprocess.check_output(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash],
            stderr=subprocess.DEVNULL
        ).decode().strip().split("\n")

        # diff (변경 내용)
        diff = subprocess.check_output(
            ["git", "show", "--pretty=format:", "--unified=3", commit_hash],
            stderr=subprocess.DEVNULL
        ).decode()

        return {
            "hash": commit_hash_short,
            "message": commit_message,
            "author": author,
            "date": date,
            "changed_files": [f for f in changed_files if f],  # 빈 문자열 제거
            "diff": diff
        }
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 명령 실행 실패: {e}")
        return None


def detect_keyword(commit_message):
    """
    커밋 메시지에서 키워드를 감지합니다.

    Args:
        commit_message (str): 커밋 메시지

    Returns:
        str or None: 감지된 키워드 ([issue], [bug], [fix]) 또는 None
    """
    message_lower = commit_message.lower()

    for keyword in KEYWORD_LABELS.keys():
        if keyword.lower() in message_lower:
            return keyword

    return None


def create_github_issue(title, body, labels):
    """
    GitHub issue를 생성합니다.

    Args:
        title (str): Issue 제목
        body (str): Issue 본문
        labels (list): 라벨 목록

    Returns:
        str or None: 생성된 issue URL 또는 None (실패 시)
    """
    # 환경 변수 확인
    if not GITHUB_TOKEN:
        print("❌ GITHUB_TOKEN 환경 변수가 설정되지 않았습니다.")
        print("   .env 파일에 GITHUB_TOKEN을 추가하세요.")
        return None

    if not GITHUB_REPO_OWNER or not GITHUB_REPO_NAME:
        print("❌ GITHUB_REPO_OWNER 또는 GITHUB_REPO_NAME 환경 변수가 설정되지 않았습니다.")
        print("   .env 파일에 GITHUB_REPO_OWNER와 GITHUB_REPO_NAME을 추가하세요.")
        return None

    # GitHub API 엔드포인트
    url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/issues"

    # 요청 헤더
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }

    # 요청 데이터
    data = {
        "title": title,
        "body": body,
        "labels": labels
    }

    try:
        # API 호출
        response = requests.post(url, json=data, headers=headers, timeout=10)

        if response.status_code == 201:
            issue_data = response.json()
            issue_url = issue_data["html_url"]
            issue_number = issue_data["number"]
            print(f"✅ Issue #{issue_number} 생성 완료")
            print(f"   URL: {issue_url}")
            return issue_url
        else:
            print(f"❌ Issue 생성 실패 (HTTP {response.status_code})")
            print(f"   응답: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ API 요청 실패: {e}")
        return None


def format_issue_body(commit_info, keyword):
    """
    Issue 본문을 포맷팅합니다.

    Args:
        commit_info (dict): 커밋 정보
        keyword (str): 감지된 키워드

    Returns:
        str: 포맷된 Issue 본문
    """
    # diff 길이 제한 (5000자)
    diff = commit_info["diff"]
    if len(diff) > 5000:
        diff = diff[:5000] + "\n\n... (diff가 너무 길어 생략됨)"

    # 변경된 파일 목록
    files_list = "\n".join([f"- `{f}`" for f in commit_info["changed_files"]])

    # Issue 본문 템플릿
    body = f"""## 📝 커밋 정보

**커밋 해시:** `{commit_info['hash']}`
**작성자:** {commit_info['author']}
**날짜:** {commit_info['date']}
**키워드:** `{keyword}`

---

## 💬 커밋 메시지

```
{commit_info['message']}
```

---

## 📂 변경된 파일 ({len(commit_info['changed_files'])}개)

{files_list}

---

## 🔍 변경 내용 (Diff)

<details>
<summary>Diff 보기 (클릭하여 펼치기)</summary>

```diff
{diff}
```

</details>

---

*🤖 이 issue는 커밋 후 자동으로 생성되었습니다.*
"""

    return body


def main():
    """메인 함수"""
    # 명령줄 인자 처리
    commit_hash = sys.argv[1] if len(sys.argv) > 1 else "HEAD"

    print(f"🔍 커밋 정보 확인 중... (커밋: {commit_hash})")

    # 커밋 정보 가져오기
    commit_info = get_commit_info(commit_hash)
    if not commit_info:
        print("❌ 커밋 정보를 가져올 수 없습니다.")
        sys.exit(1)

    print(f"   커밋 해시: {commit_info['hash']}")
    print(f"   커밋 메시지: {commit_info['message'][:50]}...")

    # 키워드 감지
    keyword = detect_keyword(commit_info["message"])

    if not keyword:
        print("ℹ️  Issue 생성 조건에 맞지 않음 (키워드 없음: [issue], [bug], [fix])")
        sys.exit(0)

    print(f"✓ 키워드 감지: {keyword}")

    # Issue 제목 (커밋 메시지 첫 줄, 최대 100자)
    first_line = commit_info["message"].split("\n")[0]
    title = f"[{commit_info['hash']}] {first_line}"
    if len(title) > 100:
        title = title[:97] + "..."

    # Issue 본문
    body = format_issue_body(commit_info, keyword)

    # 라벨
    labels = KEYWORD_LABELS[keyword]

    print(f"📤 GitHub issue 생성 중...")
    print(f"   제목: {title}")
    print(f"   라벨: {', '.join(labels)}")

    # Issue 생성
    issue_url = create_github_issue(title, body, labels)

    if issue_url:
        print(f"\n🎉 완료!")
    else:
        print(f"\n⚠️  Issue 생성에 실패했습니다.")
        sys.exit(1)


if __name__ == "__main__":
    main()
