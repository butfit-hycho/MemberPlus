# 🤖 GitHub Actions 버전 - 유효회원/휴면회원 추출 시스템

## 📋 개요
GitHub Actions를 사용하여 **완전 무료**로 서버 없이 자동화된 유효회원/휴면회원 데이터 추출 시스템을 구축합니다.

## ✨ 주요 장점

### 💰 **완전 무료**
- GitHub Actions 무료 사용량 (월 2,000분)
- 서버 비용 없음
- 추가 도구 구독료 없음

### 🔄 **자동 스케줄링**
- 매주 월요일 오전 9시 자동 실행
- 수동 실행 버튼 지원
- 지점별 선택 가능

### 📊 **완전 자동화**
- 코드 푸시 → 자동 배포
- 스케줄 실행 → 자동 데이터 추출
- 결과 → 구글 시트 자동 업로드

### 🔐 **보안**
- GitHub Secrets로 민감정보 보호
- 환경 변수 암호화
- 코드 버전 관리

## 🛠️ 설치 방법

### 1단계: GitHub 리포지토리 생성
```bash
# 1. GitHub에서 새 리포지토리 생성
# 2. 로컬에 클론
git clone https://github.com/{username}/{repo-name}.git
cd {repo-name}

# 3. 폴더 구조 생성
mkdir -p .github/workflows scripts
```

### 2단계: 파일 복사
```bash
# 워크플로우 파일 복사
cp github_actions/.github/workflows/extract_users.yml .github/workflows/

# 스크립트 파일 복사
cp github_actions/scripts/extract_users.py scripts/
```

### 3단계: GitHub Secrets 설정
GitHub 리포지토리에서 **Settings > Secrets and variables > Actions**에 다음 secrets 추가:

```
DB_HOST: butfitseoul-replica.cjilul7too7t.ap-northeast-2.rds.amazonaws.com
DB_PORT: 5432
DB_NAME: master_20221217
DB_USER: hycho
DB_PASSWORD: gaW4Charohchee5shigh0aemeeThohyu
SPREADSHEET_ID: 1Zi2VmX1Mp2swgC5QlwvAjhndc-MH8SM4YR1TlqNMjm4
GOOGLE_SERVICE_ACCOUNT: {"type": "service_account", "project_id": "...", ...}
```

### 4단계: 구글 서비스 계정 설정
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. **API 및 서비스 > 라이브러리**에서 **Google Sheets API** 활성화
4. **IAM 및 관리 > 서비스 계정**에서 새 서비스 계정 생성
5. 서비스 계정 키 생성 (JSON 형태)
6. JSON 내용을 `GOOGLE_SERVICE_ACCOUNT` secret에 추가

### 5단계: 스프레드시트 권한 설정
1. 구글 스프레드시트 열기
2. 공유 버튼 클릭
3. 서비스 계정 이메일 주소 추가 (편집자 권한)

## 🚀 사용 방법

### 자동 스케줄링
- **매주 월요일 오전 9시** 자동 실행
- **전체 지점** 데이터 추출
- 결과는 구글 시트에 자동 업로드

### 수동 실행
1. GitHub 리포지토리 > **Actions** 탭 클릭
2. **유효회원/휴면회원 추출** 워크플로우 선택
3. **Run workflow** 버튼 클릭
4. 지점명 입력 (예: "신도림", "전체")
5. **Run workflow** 실행

### 실행 결과 확인
1. **Actions** 탭에서 실행 상태 확인
2. 로그에서 진행 상황 모니터링
3. 완료 후 구글 시트에서 결과 확인

## 📊 워크플로우 구조

```yaml
트리거:
- 스케줄: 매주 월요일 오전 9시
- 수동 실행: 지점명 입력 가능

실행 단계:
1. 코드 체크아웃
2. Python 환경 설정
3. 패키지 설치
4. 데이터 추출 스크립트 실행
5. 결과 알림
```

## 🔧 커스터마이징

### 스케줄 변경
```yaml
schedule:
  - cron: '0 9 * * 1'  # 매주 월요일 오전 9시
  - cron: '0 18 * * 5' # 매주 금요일 오후 6시
```

### 알림 추가
```yaml
- name: 슬랙 알림
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### 이메일 알림
```yaml
- name: 이메일 알림
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: "데이터 추출 완료: ${{ env.BRANCH_NAME }}"
    body: "유효회원/휴면회원 데이터 추출이 완료되었습니다."
```

## 📈 고급 기능

### 멀티 지점 병렬 실행
```yaml
strategy:
  matrix:
    branch: ["신도림", "강남", "홍대", "건대"]
```

### 실패 시 재시도
```yaml
- name: 데이터 추출 (재시도)
  uses: nick-invision/retry@v2
  with:
    timeout_minutes: 10
    max_attempts: 3
    command: python scripts/extract_users.py
```

### 결과 파일 저장
```yaml
- name: 결과 파일 업로드
  uses: actions/upload-artifact@v3
  with:
    name: extraction-results
    path: results/
```

## 🔍 모니터링

### 실행 로그 확인
```bash
# GitHub Actions 탭에서 실행 로그 확인
✅ 데이터베이스 연결 성공
📊 유효회원 데이터 추출 중...
📊 쿼리 실행 완료: 1,234개 레코드
📊 휴면회원 데이터 추출 중...
📊 쿼리 실행 완료: 567개 레코드
📤 구글 시트 업로드 중...
✅ 유효회원 시트 생성: 1,234개 레코드
✅ 휴면회원 시트 생성: 567개 레코드
✅ 요약 시트 생성
🎉 데이터 추출 및 업로드 완료!
```

### 실행 상태 뱃지
```markdown
![Data Extraction](https://github.com/{username}/{repo}/actions/workflows/extract_users.yml/badge.svg)
```

## ⚠️ 주의사항

### 실행 시간 제한
- GitHub Actions 무료 플랜: **월 2,000분**
- 1회 실행 시 약 **2-5분** 소요
- 월 400-1,000회 실행 가능

### 보안
- 모든 민감정보는 **GitHub Secrets** 사용
- 공개 리포지토리에서는 private으로 설정 권장

### 데이터베이스 연결
- 방화벽 설정 필요 (GitHub Actions IP 허용)
- VPN 연결 불가 시 직접 DB 접근 필요

## 🆚 다른 솔루션과 비교

| 기능 | GitHub Actions | Apps Script | Zapier | Python Server |
|------|---------------|-------------|---------|---------------|
| 비용 | **무료** | 무료 | 유료 | 서버 비용 |
| 설정 | 보통 | 간단 | 매우 간단 | 복잡 |
| 성능 | 높음 | 제한적 | 보통 | 최고 |
| 커스터마이징 | **높음** | 보통 | 낮음 | 최고 |
| 스케줄링 | **내장** | 없음 | 내장 | 별도 설정 |
| 모니터링 | **우수** | 기본 | 기본 | 별도 구축 |

## 💡 추가 아이디어

### 대시보드 구축
- GitHub Pages로 정적 대시보드 생성
- 실행 결과 시각화
- 히스토리 트렌드 분석

### 데이터 검증
- 이상 데이터 감지
- 전월 대비 변화량 체크
- 자동 경고 시스템

### 백업 시스템
- 여러 스프레드시트 동시 업로드
- 로컬 CSV 파일 생성
- 클라우드 스토리지 백업

---

## 🎯 **결론: GitHub Actions가 최적인 이유**

1. **💰 비용**: 완전 무료
2. **🔄 자동화**: 스케줄링 + 수동 실행
3. **📊 모니터링**: 상세한 로그 및 알림
4. **🔐 보안**: GitHub Secrets 암호화
5. **🛠️ 확장성**: 다양한 액션 및 통합

**👉 서버 없이 완전 자동화된 시스템을 원한다면 GitHub Actions를 추천합니다!** 