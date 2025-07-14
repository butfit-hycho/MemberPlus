#!/usr/bin/env python3
"""
간편 실행 스크립트
"""

from src.main import UserExtractionService, setup_logging

def main():
    """간편 실행 함수"""
    
    # 로깅 설정
    logger = setup_logging()
    
    print("=== 유효회원/휴면회원 추출 시스템 ===")
    print()
    
    # 지점명 입력
    print("지점명을 입력하세요 (예: 신도림, 강남, 홍대 등)")
    print("전체 지점 조회하려면 엔터를 누르세요")
    branch_name = input("지점명: ").strip()
    
    if not branch_name:
        branch_name = None
        print("-> 전체 지점 조회")
    else:
        print(f"-> {branch_name} 지점 조회")
    
    print()
    print("데이터 추출 및 업로드를 시작합니다...")
    print()
    
    try:
        service = UserExtractionService()
        success = service.run(branch_name)
        
        if success:
            print()
            print("✅ 성공적으로 완료되었습니다!")
            print("구글 스프레드시트에서 결과를 확인하세요.")
            print("URL: https://docs.google.com/spreadsheets/d/1Zi2VmX1Mp2swgC5QlwvAjhndc-MH8SM4YR1TlqNMjm4")
        else:
            print()
            print("❌ 작업 중 오류가 발생했습니다.")
            print("로그를 확인하여 문제를 해결하세요.")
            
    except KeyboardInterrupt:
        print()
        print("⏹️  사용자에 의해 중단되었습니다.")
    except Exception as e:
        print()
        print(f"❌ 예상치 못한 오류: {str(e)}")
        print("로그를 확인하여 문제를 해결하세요.")

if __name__ == "__main__":
    main() 