#!/usr/bin/env python3
"""
유효회원/휴면회원 추출 및 구글 스프레드시트 업로드 시스템
"""

import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import DatabaseConnection
from src.database.queries import QueryBuilder
from src.sheets.uploader import GoogleSheetsUploader

# 로깅 설정
def setup_logging():
    """로깅 설정"""
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f'user_extraction_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"로그 파일: {log_file}")
    return logger

class UserExtractionService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db_connection = None
        self.query_builder = QueryBuilder()
        self.sheets_uploader = GoogleSheetsUploader()
    
    def extract_users(self, branch_name: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> tuple:
        """
        유효회원/휴면회원 데이터 추출
        
        Args:
            branch_name: 지점명 (예: '신도림', '강남' 등)
            filters: 추가 동적 필터 조건
                    예: {'date_range': {'start_date': '2023-01-01', 'end_date': '2023-12-31'}}
        
        Returns:
            (active_users_df, inactive_users_df): 유효회원, 휴면회원 데이터프레임
        """
        self.logger.info("사용자 데이터 추출 시작")
        
        # 필터 생성
        final_filters = filters.copy() if filters else {}
        
        # 지점명 필터 추가
        if branch_name:
            final_filters['branch_name'] = branch_name
            self.logger.info(f"지점명 필터 적용: {branch_name}")
        
        # 필터 유효성 검사
        if final_filters and not self.query_builder.validate_filters(final_filters):
            raise ValueError("유효하지 않은 필터 조건이 포함되어 있습니다.")
        
        try:
            with DatabaseConnection() as db:
                # 연결 테스트
                if not db.test_connection():
                    raise ConnectionError("데이터베이스 연결 테스트 실패")
                
                # 유효회원 조회
                active_query = self.query_builder.get_active_users_query(final_filters)
                active_users_df = db.execute_query(active_query)
                self.logger.info(f"유효회원 조회 완료: {len(active_users_df)}건")
                
                # 휴면회원 조회
                inactive_query = self.query_builder.get_inactive_users_query(final_filters)
                inactive_users_df = db.execute_query(inactive_query)
                self.logger.info(f"휴면회원 조회 완료: {len(inactive_users_df)}건")
                
                return active_users_df, inactive_users_df
                
        except Exception as e:
            self.logger.error(f"데이터 추출 실패: {str(e)}")
            raise
    
    def upload_to_sheets(self, active_users_df, inactive_users_df, branch_name: Optional[str] = None) -> bool:
        """구글 스프레드시트에 데이터 업로드"""
        self.logger.info("구글 스프레드시트 업로드 시작")
        
        try:
            # 유효회원 업로드
            if not self.sheets_uploader.upload_active_users(active_users_df):
                raise Exception("유효회원 데이터 업로드 실패")
            
            # 휴면회원 업로드
            if not self.sheets_uploader.upload_inactive_users(inactive_users_df):
                raise Exception("휴면회원 데이터 업로드 실패")
            
            # 요약 시트 생성
            if not self.sheets_uploader.create_summary_sheet(len(active_users_df), len(inactive_users_df), branch_name):
                self.logger.warning("요약 시트 생성 실패 (데이터 업로드는 성공)")
            
            self.logger.info("구글 스프레드시트 업로드 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"스프레드시트 업로드 실패: {str(e)}")
            return False
    
    def run(self, branch_name: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> bool:
        """전체 프로세스 실행"""
        try:
            self.logger.info("=== 유효회원/휴면회원 추출 시스템 시작 ===")
            
            # 실행 정보 출력
            if branch_name:
                self.logger.info(f"지점명: {branch_name}")
            else:
                self.logger.info("지점명: 전체")
            
            if filters:
                self.logger.info(f"추가 필터: {filters}")
            else:
                self.logger.info("추가 필터: 없음")
            
            # 데이터 추출
            active_users_df, inactive_users_df = self.extract_users(branch_name, filters)
            
            # 스프레드시트 업로드
            if self.upload_to_sheets(active_users_df, inactive_users_df, branch_name):
                spreadsheet_url = self.sheets_uploader.get_spreadsheet_url()
                if spreadsheet_url:
                    self.logger.info(f"스프레드시트 URL: {spreadsheet_url}")
                
                self.logger.info("=== 모든 작업 완료 ===")
                return True
            else:
                self.logger.error("스프레드시트 업로드 실패")
                return False
                
        except Exception as e:
            self.logger.error(f"프로세스 실행 실패: {str(e)}")
            return False

def main():
    """메인 실행 함수"""
    logger = setup_logging()
    
    try:
        # 실행 예시 - 실제 사용 시 필요에 따라 수정
        
        # 1. 신도림 지점 데이터 추출
        branch_name = "신도림"
        
        # 2. 추가 필터 설정 (선택사항)
        filters = {
            # 'date_range': {
            #     'start_date': '2023-01-01',
            #     'end_date': '2023-12-31'
            # },
            # 'membership_type': '프리미엄'
        }
        
        service = UserExtractionService()
        success = service.run(branch_name, filters)
        
        if success:
            logger.info("프로그램 실행 완료")
            sys.exit(0)
        else:
            logger.error("프로그램 실행 실패")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단됨")
        sys.exit(1)
    except Exception as e:
        logger.error(f"예상치 못한 오류: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 