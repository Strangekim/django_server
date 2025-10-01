# S3 업로드 문제 원인 분석

## 🔍 발견된 문제점

### 1️⃣ **환경 변수명 불일치**

#### Problems 업로드 (core/views.py)
```python
aws_region = os.getenv('AWS_S3_REGION_NAME')  # ✅ 이 변수명 사용
```

#### Session 업로드 (api/views.py)
```python
aws_region = os.getenv('AWS_REGION')  # ❌ 다른 변수명 사용!
```

**결과:**
- Problems: `AWS_S3_REGION_NAME`에서 region 읽음
- Sessions: `AWS_REGION`에서 region 읽음
- 만약 `AWS_REGION`이 설정 안되어 있으면 → `aws_region = None`
- `if not all([...])` 체크에서 실패 → ValueError 발생
- **하지만 예외 처리로 인해 에러가 조용히 무시됨** (486번째 줄)

---

### 2️⃣ **예외 처리가 에러를 숨김**

```python
except Exception as e:
    # S3 업로드 실패해도 DB 데이터는 유지 (경고만 로깅)
    print(f"S3 업로드 실패 (세션 {session_uuid}): {str(e)}")
    return session_uuid, ""  # 빈 문자열 반환
```

**문제:**
- S3 업로드 실패해도 API 응답은 성공(200)
- 사용자는 모름
- 서버 콘솔에만 에러 출력 (print)
- **Gunicorn 로그를 확인해야만 에러 발견 가능**

---

### 3️⃣ **S3 경로 구조**

#### Problems (questions 폴더)
```
s3://bucket-name/questions/
  ├── 1_original.png
  ├── 1_separate.png
  ├── 2_original.png
  └── ...
```

#### Sessions (answers 폴더)
```
s3://bucket-name/answers/
  ├── 1_uuid-xxx.json.gz
  ├── 2_uuid-yyy.json.gz
  └── ...
```

---

## 🔬 원인 진단 체크리스트

### ✅ 확인 필요 사항

1. **EC2 서버의 .env 파일 확인**
   ```bash
   cat /home/ubuntu/django_server/.env | grep AWS
   ```
   
   필요한 환경 변수:
   - `AWS_S3_REGION_NAME` (problems용)
   - `AWS_REGION` (sessions용) ← **이게 없을 가능성 높음!**
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_STORAGE_BUCKET_NAME`

2. **Gunicorn 로그에서 S3 에러 확인**
   ```bash
   sudo journalctl -u gunicorn -n 100 | grep "S3 업로드"
   ```
   
   예상 에러 메시지:
   - `S3 업로드 실패 (세션 xxx): AWS 환경 변수가 설정되지 않았습니다.`
   - `S3 업로드 실패 (세션 xxx): NoCredentialsError`

3. **S3 버킷 권한 확인**
   - `answers/` 폴더에 쓰기 권한이 있는지
   - IAM 정책에 `s3:PutObject` 권한 있는지

4. **실제 S3 버킷 확인**
   ```bash
   aws s3 ls s3://your-bucket-name/answers/
   ```

---

## 🎯 예상되는 주요 원인

### **가장 가능성 높은 원인: 환경 변수 누락**

```
AWS_S3_REGION_NAME=ap-northeast-2  ✅ 설정됨 (problems 업로드 됨)
AWS_REGION=                        ❌ 설정 안됨! (sessions 업로드 실패)
```

**증거:**
1. Problems는 잘 업로드됨 → `AWS_S3_REGION_NAME` 있음
2. Sessions는 업로드 안됨 → `AWS_REGION` 없음
3. DB에는 잘 저장됨 → API 자체는 작동
4. 500 에러 없음 → 예외 처리로 에러 숨김

---

## 🔧 해결 방법 (코드 수정 전 확인용)

### 1. EC2에서 환경 변수 확인
```bash
cd /home/ubuntu/django_server
source venv/bin/activate
cat .env | grep AWS
```

### 2. 로그 확인
```bash
sudo journalctl -u gunicorn -n 200 | grep -A 5 "S3 업로드"
```

### 3. Python 쉘에서 직접 테스트
```bash
python manage.py shell
```
```python
import os
from dotenv import load_dotenv
load_dotenv()

print("AWS_REGION:", os.getenv('AWS_REGION'))
print("AWS_S3_REGION_NAME:", os.getenv('AWS_S3_REGION_NAME'))
print("AWS_ACCESS_KEY_ID:", os.getenv('AWS_ACCESS_KEY_ID')[:10] if os.getenv('AWS_ACCESS_KEY_ID') else None)
print("AWS_STORAGE_BUCKET_NAME:", os.getenv('AWS_STORAGE_BUCKET_NAME'))
```
