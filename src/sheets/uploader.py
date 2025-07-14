import logging
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from typing import Dict, List, Optional
from config.google_sheets import GOOGLE_SHEETS_CONFIG, SPREADSHEET_CONFIG, ACTIVE_USERS_COLUMNS, INACTIVE_USERS_COLUMNS, get_sheet_names

logger = logging.getLogger(__name__)

class GoogleSheetsUploader:
    def __init__(self):
        self.gc = None
        self.spreadsheet = None
        self._authenticate()
    
    def _authenticate(self):
        """구글 스프레드시트 인증"""
        try:
            credentials = Credentials.from_service_account_file(
                GOOGLE_SHEETS_CONFIG['service_account_file'],
                scopes=GOOGLE_SHEETS_CONFIG['scopes']
            )
            
            self.gc = gspread.authorize(credentials)
            
            if SPREADSHEET_CONFIG['spreadsheet_id']:
                self.spreadsheet = self.gc.open_by_key(SPREADSHEET_CONFIG['spreadsheet_id'])
            else:
                logger.warning("스프레드시트 ID가 설정되지 않았습니다.")
            
            logger.info("구글 스프레드시트 인증 완료")
            
        except Exception as e:
            logger.error(f"구글 스프레드시트 인증 실패: {str(e)}")
            raise
    
    def _prepare_active_users_data(self, df: pd.DataFrame) -> List[List]:
        """유효회원 데이터프레임을 스프레드시트 업로드용 형태로 변환"""
        # 컬럼 순서 정렬 및 헤더 적용
        ordered_columns = list(ACTIVE_USERS_COLUMNS.keys())
        headers = [ACTIVE_USERS_COLUMNS[col] for col in ordered_columns]
        
        # 데이터프레임 컬럼 순서 조정
        df_ordered = df[ordered_columns].copy()
        
        # 날짜 컬럼 포맷팅
        date_columns = ['이용 시작일', '이용 종료일']
        for col in date_columns:
            if col in df_ordered.columns:
                df_ordered[col] = pd.to_datetime(df_ordered[col], errors='coerce').dt.strftime('%Y-%m-%d')
        
        # 생년월 컬럼 포맷팅
        if '생년월' in df_ordered.columns:
            df_ordered['생년월'] = pd.to_datetime(df_ordered['생년월'], errors='coerce').dt.strftime('%Y-%m-%d')
        
        # NaN 값을 빈 문자열로 변환
        df_ordered = df_ordered.fillna('')
        
        # 헤더 + 데이터 결합
        data_rows = [headers]
        data_rows.extend(df_ordered.values.tolist())
        
        return data_rows
    
    def _prepare_inactive_users_data(self, df: pd.DataFrame) -> List[List]:
        """휴면회원 데이터프레임을 스프레드시트 업로드용 형태로 변환"""
        # 컬럼 순서 정렬 및 헤더 적용
        ordered_columns = list(INACTIVE_USERS_COLUMNS.keys())
        headers = [INACTIVE_USERS_COLUMNS[col] for col in ordered_columns]
        
        # 데이터프레임 컬럼 순서 조정
        df_ordered = df[ordered_columns].copy()
        
        # 날짜 컬럼 포맷팅
        date_columns = ['이용 시작일', '이용 종료일']
        for col in date_columns:
            if col in df_ordered.columns:
                df_ordered[col] = pd.to_datetime(df_ordered[col], errors='coerce').dt.strftime('%Y-%m-%d')
        
        # NaN 값을 빈 문자열로 변환
        df_ordered = df_ordered.fillna('')
        
        # 헤더 + 데이터 결합
        data_rows = [headers]
        data_rows.extend(df_ordered.values.tolist())
        
        return data_rows
    
    def upload_to_sheet(self, df: pd.DataFrame, sheet_name: str, data_type: str, clear_before_upload: bool = True) -> bool:
        """데이터프레임을 지정된 시트에 업로드"""
        try:
            if not self.spreadsheet:
                logger.error("스프레드시트가 설정되지 않았습니다.")
                return False
            
            # 시트 가져오기 또는 생성
            try:
                worksheet = self.spreadsheet.worksheet(sheet_name)
            except gspread.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(title=sheet_name, rows=2000, cols=20)
                logger.info(f"새 시트 생성: {sheet_name}")
            
            # 기존 데이터 삭제 (선택사항)
            if clear_before_upload:
                worksheet.clear()
                logger.info(f"기존 데이터 삭제: {sheet_name}")
            
            # 데이터 타입에 따른 데이터 준비
            if data_type == 'active':
                data_rows = self._prepare_active_users_data(df)
            elif data_type == 'inactive':
                data_rows = self._prepare_inactive_users_data(df)
            else:
                logger.error(f"지원되지 않는 데이터 타입: {data_type}")
                return False
            
            # 데이터 업로드
            if data_rows:
                worksheet.update('A1', data_rows)
            
            logger.info(f"데이터 업로드 완료: {sheet_name} ({len(df)}건)")
            return True
            
        except Exception as e:
            logger.error(f"시트 업로드 실패: {str(e)}")
            return False
    
    def upload_users_by_branch(self, active_users_df: pd.DataFrame, inactive_users_df: pd.DataFrame, branch_name: str = None) -> bool:
        """지점별 유효회원/휴면회원 데이터 업로드"""
        try:
            # 지점별 시트명 생성
            sheet_names = get_sheet_names(branch_name)
            
            # 유효회원 업로드
            if not self.upload_to_sheet(
                active_users_df, 
                sheet_names['active_users_sheet'],
                'active',
                SPREADSHEET_CONFIG['clear_before_upload']
            ):
                raise Exception("유효회원 데이터 업로드 실패")
            
            # 휴면회원 업로드
            if not self.upload_to_sheet(
                inactive_users_df, 
                sheet_names['inactive_users_sheet'],
                'inactive',
                SPREADSHEET_CONFIG['clear_before_upload']
            ):
                raise Exception("휴면회원 데이터 업로드 실패")
            
            logger.info(f"지점별 데이터 업로드 완료: {branch_name or '전체'}")
            return True
            
        except Exception as e:
            logger.error(f"지점별 업로드 실패: {str(e)}")
            return False
    
    def create_summary_sheet(self, active_count: int, inactive_count: int, branch_name: str = None) -> bool:
        """지점별 요약 시트 생성"""
        try:
            sheet_names = get_sheet_names(branch_name)
            current_time = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            
            summary_data = [
                ['구분', '건수', '지점명', '업데이트 시간'],
                ['유효회원', active_count, branch_name or '전체', current_time],
                ['휴면회원', inactive_count, branch_name or '전체', current_time]
            ]
            
            # 요약 시트 가져오기 또는 생성
            try:
                worksheet = self.spreadsheet.worksheet(sheet_names['summary_sheet'])
            except gspread.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(title=sheet_names['summary_sheet'], rows=100, cols=10)
            
            worksheet.clear()
            worksheet.update('A1', summary_data)
            
            logger.info(f"요약 시트 생성 완료: {sheet_names['summary_sheet']}")
            return True
            
        except Exception as e:
            logger.error(f"요약 시트 생성 실패: {str(e)}")
            return False
    
    def get_spreadsheet_url(self) -> Optional[str]:
        """스프레드시트 URL 반환"""
        if self.spreadsheet:
            return f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_CONFIG['spreadsheet_id']}"
        return None 