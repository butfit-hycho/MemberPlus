# 유효회원/휴면회원 추출 시스템

## 프로젝트 개요
레플리카 데이터베이스에서 유효회원과 휴면회원을 동적으로 추출하여 구글 스프레드시트에 업로드하는 시스템입니다.
지점별로 별도의 시트를 생성하여 동시 사용이 가능합니다.

## 주요 기능
- 웹 UI를 통한 간편한 지점 선택 및 데이터 추출
- 지점별 동적 쿼리 실행 (드롭다운 선택)
- 유효회원/휴면회원 분류 및 추출
- 지점별 구글 스프레드시트 시트 자동 생성
- 추출 완료 후 자동으로 스프레드시트 열기
- 실행 로그 및 에러 핸들링

## 기술 스택
- Python 3.8+
- Streamlit (웹 UI)
- Database: PostgreSQL (레플리카 DB)
- Google Sheets API
- pandas (데이터 처리)
- SQLAlchemy (DB 연결)

## 디렉토리 구조
```
├── README.md
├── requirements.txt
├── app.py                  # 웹 UI 메인 파일
├── run.py                  # CLI 실행 스크립트
├── config/
│   ├── database.py        # 데이터베이스 설정
│   └── google_sheets.py   # 구글 스프레드시트 설정
├── src/
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py  # DB 연결
│   │   └── queries.py     # 동적 쿼리 생성
│   ├── sheets/
│   │   ├── __init__.py
│   │   └── uploader.py    # 지점별 스프레드시트 업로드
│   └── main.py            # CLI 메인 로직
├── credentials/
│   └── google_service_account.json  # 구글 서비스 계정 키
└── logs/
```

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 설정
- DB 사용자명/비밀번호는 이미 설정되어 있음
- `credentials/` 폴더에 구글 서비스 계정 키 파일 저장

### 3. 실행 방법

#### 🌐 웹 UI 실행 (추천)
```bash
streamlit run app.py
```
- 브라우저에서 자동으로 열림
- 지점 드롭다운 선택
- 원클릭 데이터 추출 및 업로드
- 완료 후 스프레드시트 자동 열기

#### 📱 CLI 실행
```bash
python3 run.py
```
- 터미널에서 지점명 입력
- 간단한 대화형 인터페이스

#### 🔧 직접 실행
```bash
python3 src/main.py
```
- 코드에서 지점명 수정 필요

## 사용법

### 웹 UI 사용법
1. `streamlit run app.py` 실행
2. 사이드바에서 지점 선택 (드롭다운)
3. "데이터 추출 시작" 버튼 클릭
4. 데이터 추출 및 업로드 진행상황 확인
5. 완료 후 "스프레드시트 열기" 버튼 클릭

### 지점별 시트 구조
각 지점별로 3개의 시트가 생성됩니다:
- `{지점명}_유효회원`: 유효회원 데이터
- `{지점명}_휴면회원`: 휴면회원 데이터
- `{지점명}_요약`: 요약 통계

예시:
- `신도림_유효회원`
- `신도림_휴면회원`
- `신도림_요약`

### 전체 지점 조회
"전체" 선택 시:
- `전체_유효회원`
- `전체_휴면회원`
- `전체_요약`

## 데이터베이스 설정
- **Host**: butfitseoul-replica.cjilul7too7t.ap-northeast-2.rds.amazonaws.com
- **Port**: 5432
- **Database**: master_20221217
- **Driver**: postgresql
- **Username**: hycho
- **Password**: 설정됨

## 구글 스프레드시트 설정
- **Spreadsheet ID**: 1Zi2VmX1Mp2swgC5QlwvAjhndc-MH8SM4YR1TlqNMjm4
- **URL**: https://docs.google.com/spreadsheets/d/1Zi2VmX1Mp2swgC5QlwvAjhndc-MH8SM4YR1TlqNMjm4

### 구글 서비스 계정 설정
`credentials/README.md` 파일의 안내를 따라 설정하세요:
1. 구글 클라우드 콘솔에서 서비스 계정 생성
2. Sheets API 및 Drive API 활성화
3. JSON 키 파일을 `credentials/google_service_account.json`로 저장
4. 스프레드시트에 서비스 계정 이메일 공유 권한 부여

## 쿼리 구조
- **유효회원**: 현재 날짜 기준 유효한 멤버십을 가진 회원
- **휴면회원**: 멤버십이 만료되고 현재 유효한 멤버십이 없는 회원
- **제외 멤버십**: 버핏레이스, 건강 선물, 리뉴얼, 베네핏, 1일권 등
- **탈퇴 회원**: 이름에 '(탈퇴)'가 포함된 회원 제외

## 동시 사용 지원
- 지점별로 별도의 시트를 생성하여 여러 지점 동시 추출 가능
- 각 지점의 데이터가 독립적으로 관리됨
- 실시간 업데이트 시간 표시

## 로그 파일
- `logs/` 폴더에 날짜별 로그 파일 생성
- 웹 UI: `user_extraction_web_YYYYMMDD_HHMMSS.log`
- CLI: `user_extraction_YYYYMMDD_HHMMSS.log`

## 주의사항
- 레플리카 DB 사용으로 프로덕션에 영향 없음
- 개인정보 처리 시 보안 주의
- 구글 API 호출 제한 고려
- 대용량 데이터 추출 시 시간 소요 가능 