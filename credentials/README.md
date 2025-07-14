# 구글 서비스 계정 키 파일 설정

이 폴더에 구글 서비스 계정 키 파일을 저장하세요.

## 설정 방법

1. **구글 클라우드 콘솔 접속**
   - https://console.cloud.google.com/

2. **프로젝트 생성 또는 선택**
   - 새 프로젝트 만들기 또는 기존 프로젝트 선택

3. **API 활성화**
   - Google Sheets API 활성화
   - Google Drive API 활성화

4. **서비스 계정 생성**
   - IAM 및 관리자 → 서비스 계정
   - 서비스 계정 만들기
   - 이름: `user-extraction-service`
   - 역할: `편집자` 또는 `Google Sheets API 사용자`

5. **키 파일 다운로드**
   - 생성된 서비스 계정 클릭
   - 키 탭 → 키 추가 → 새 키 만들기
   - 키 유형: JSON
   - 파일 이름을 `google_service_account.json`로 변경
   - 이 폴더에 저장

6. **스프레드시트 공유**
   - 대상 스프레드시트 열기
   - 공유 버튼 클릭
   - 서비스 계정 이메일 주소 추가
   - 권한: 편집자

## 파일 구조
```
credentials/
├── README.md (이 파일)
└── google_service_account.json (여기에 키 파일 저장)
```

## 보안 주의사항
- 키 파일은 절대 공개 저장소에 올리지 마세요
- `.gitignore`에 추가하여 실수로 커밋되지 않도록 하세요
- 필요 없어진 키는 구글 클라우드 콘솔에서 삭제하세요 