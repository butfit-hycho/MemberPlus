import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 구글 스프레드시트 설정
GOOGLE_SHEETS_CONFIG = {
    'service_account_file': os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', 'credentials/google_service_account.json'),
    'scopes': [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
}

# 스프레드시트 정보
SPREADSHEET_CONFIG = {
    'spreadsheet_id': os.getenv('SPREADSHEET_ID', '1Zi2VmX1Mp2swgC5QlwvAjhndc-MH8SM4YR1TlqNMjm4'),
    'clear_before_upload': True  # 업로드 전 시트 내용 삭제 여부
}

# 지점별 시트명 생성 함수
def get_sheet_names(branch_name: str):
    """지점별 시트명 생성"""
    if branch_name:
        return {
            'active_users_sheet': f'{branch_name}_유효회원',
            'inactive_users_sheet': f'{branch_name}_휴면회원',
            'summary_sheet': f'{branch_name}_요약'
        }
    else:
        return {
            'active_users_sheet': '전체_유효회원',
            'inactive_users_sheet': '전체_휴면회원',
            'summary_sheet': '전체_요약'
        }

# 유효회원 컬럼 매핑 (쿼리 결과 → 스프레드시트 헤더)
ACTIVE_USERS_COLUMNS = {
    '회원 이름': '회원 이름',
    '전화번호': '전화번호',
    '생년월': '생년월',
    '현재 멤버십 상품명': '현재 멤버십 상품명',
    '이용 시작일': '이용 시작일',
    '이용 종료일': '이용 종료일'
}

# 휴면회원 컬럼 매핑 (쿼리 결과 → 스프레드시트 헤더)
INACTIVE_USERS_COLUMNS = {
    '회원 이름': '회원 이름',
    '전화번호': '전화번호',
    '마지막 멤버십 상품명': '마지막 멤버십 상품명',
    '이용 시작일': '이용 시작일',
    '이용 종료일': '이용 종료일'
} 