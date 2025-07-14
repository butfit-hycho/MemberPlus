#!/usr/bin/env python3
"""
유효회원/휴면회원 추출 스크립트 - GitHub Actions 버전
"""

import os
import sys
import json
import psycopg2
import gspread
import pandas as pd
from datetime import datetime
from google.oauth2.service_account import Credentials

# 환경 변수에서 설정 로드
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'butfitseoul-replica.cjilul7too7t.ap-northeast-2.rds.amazonaws.com'),
    'port': int(os.environ.get('DB_PORT', 5432)),
    'database': os.environ.get('DB_NAME', 'master_20221217'),
    'user': os.environ.get('DB_USER', 'hycho'),
    'password': os.environ.get('DB_PASSWORD', 'gaW4Charohchee5shigh0aemeeThohyu')
}

SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID', '1Zi2VmX1Mp2swgC5QlwvAjhndc-MH8SM4YR1TlqNMjm4')
BRANCH_NAME = os.environ.get('BRANCH_NAME', '전체')

def connect_database():
    """데이터베이스 연결"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ 데이터베이스 연결 성공")
        return conn
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        sys.exit(1)

def get_active_users_query(branch_name):
    """유효회원 쿼리 생성"""
    branch_condition = "" if branch_name == "전체" else f"AND m.branch_name = '{branch_name}'"
    
    return f"""
    WITH active_memberships AS (
      SELECT 
        m.user_id,
        m.branch_name,
        m.membership_type,
        m.start_date,
        m.end_date,
        m.created_at,
        ROW_NUMBER() OVER (PARTITION BY m.user_id ORDER BY m.end_date DESC) as rn
      FROM membership m
      WHERE m.end_date >= CURRENT_DATE
        AND m.membership_type NOT IN ('버핏레이스', '건강 선물', '리뉴얼', '베네핏', '1일권')
        {branch_condition}
    ),
    active_users AS (
      SELECT 
        am.user_id,
        am.branch_name,
        am.membership_type,
        am.start_date,
        am.end_date,
        u.name,
        u.email,
        u.phone,
        u.created_at as user_created_at
      FROM active_memberships am
      JOIN users u ON am.user_id = u.id
      WHERE am.rn = 1
        AND u.name NOT LIKE '%탈퇴%'
    )
    SELECT 
      user_id,
      name,
      email,
      phone,
      branch_name,
      membership_type,
      start_date,
      end_date,
      user_created_at
    FROM active_users
    ORDER BY branch_name, name;
    """

def get_inactive_users_query(branch_name):
    """휴면회원 쿼리 생성"""
    branch_condition = "" if branch_name == "전체" else f"AND m.branch_name = '{branch_name}'"
    
    return f"""
    WITH last_memberships AS (
      SELECT 
        m.user_id,
        m.branch_name,
        m.membership_type,
        m.start_date,
        m.end_date,
        m.created_at,
        ROW_NUMBER() OVER (PARTITION BY m.user_id ORDER BY m.end_date DESC) as rn
      FROM membership m
      WHERE m.membership_type NOT IN ('버핏레이스', '건강 선물', '리뉴얼', '베네핏', '1일권')
        {branch_condition}
    ),
    inactive_users AS (
      SELECT 
        lm.user_id,
        lm.branch_name,
        lm.membership_type,
        lm.start_date,
        lm.end_date,
        u.name,
        u.email,
        u.phone,
        u.created_at as user_created_at
      FROM last_memberships lm
      JOIN users u ON lm.user_id = u.id
      WHERE lm.rn = 1
        AND lm.end_date < CURRENT_DATE
        AND u.name NOT LIKE '%탈퇴%'
        AND NOT EXISTS (
          SELECT 1 FROM membership m2 
          WHERE m2.user_id = lm.user_id 
            AND m2.end_date >= CURRENT_DATE
            AND m2.membership_type NOT IN ('버핏레이스', '건강 선물', '리뉴얼', '베네핏', '1일권')
        )
    )
    SELECT 
      user_id,
      name,
      email,
      phone,
      branch_name,
      membership_type,
      start_date,
      end_date,
      user_created_at
    FROM inactive_users
    ORDER BY branch_name, name;
    """

def execute_query(conn, query):
    """쿼리 실행"""
    try:
        df = pd.read_sql_query(query, conn)
        print(f"📊 쿼리 실행 완료: {len(df)}개 레코드")
        return df
    except Exception as e:
        print(f"❌ 쿼리 실행 실패: {e}")
        return pd.DataFrame()

def setup_google_sheets():
    """구글 시트 설정"""
    try:
        # 환경 변수에서 서비스 계정 키 로드
        service_account_info = json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT'])
        
        credentials = Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        gc = gspread.authorize(credentials)
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        
        print("✅ 구글 시트 연결 성공")
        return spreadsheet
    except Exception as e:
        print(f"❌ 구글 시트 연결 실패: {e}")
        sys.exit(1)

def upload_to_sheets(spreadsheet, branch_name, active_df, inactive_df):
    """구글 시트에 데이터 업로드"""
    try:
        # 시트 이름 생성
        active_sheet_name = f"{branch_name}_유효회원"
        inactive_sheet_name = f"{branch_name}_휴면회원"
        summary_sheet_name = f"{branch_name}_요약"
        
        # 기존 시트 삭제
        for sheet_name in [active_sheet_name, inactive_sheet_name, summary_sheet_name]:
            try:
                sheet = spreadsheet.worksheet(sheet_name)
                spreadsheet.del_worksheet(sheet)
                print(f"🗑️ 기존 시트 삭제: {sheet_name}")
            except gspread.WorksheetNotFound:
                pass
        
        # 유효회원 시트 생성
        active_sheet = spreadsheet.add_worksheet(title=active_sheet_name, rows=len(active_df)+1, cols=len(active_df.columns))
        if not active_df.empty:
            active_sheet.update([active_df.columns.values.tolist()] + active_df.values.tolist())
            print(f"✅ 유효회원 시트 생성: {len(active_df)}개 레코드")
        
        # 휴면회원 시트 생성
        inactive_sheet = spreadsheet.add_worksheet(title=inactive_sheet_name, rows=len(inactive_df)+1, cols=len(inactive_df.columns))
        if not inactive_df.empty:
            inactive_sheet.update([inactive_df.columns.values.tolist()] + inactive_df.values.tolist())
            print(f"✅ 휴면회원 시트 생성: {len(inactive_df)}개 레코드")
        
        # 요약 시트 생성
        summary_sheet = spreadsheet.add_worksheet(title=summary_sheet_name, rows=10, cols=2)
        summary_data = [
            ['구분', '수량'],
            ['유효회원', len(active_df)],
            ['휴면회원', len(inactive_df)],
            ['총합', len(active_df) + len(inactive_df)],
            ['추출 시간', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        summary_sheet.update(summary_data)
        print(f"✅ 요약 시트 생성")
        
        return True
    except Exception as e:
        print(f"❌ 구글 시트 업로드 실패: {e}")
        return False

def main():
    """메인 함수"""
    print("🚀 유효회원/휴면회원 추출 시작")
    print(f"📍 지점: {BRANCH_NAME}")
    
    # 데이터베이스 연결
    conn = connect_database()
    
    try:
        # 유효회원 데이터 추출
        print("📊 유효회원 데이터 추출 중...")
        active_query = get_active_users_query(BRANCH_NAME)
        active_df = execute_query(conn, active_query)
        
        # 휴면회원 데이터 추출
        print("📊 휴면회원 데이터 추출 중...")
        inactive_query = get_inactive_users_query(BRANCH_NAME)
        inactive_df = execute_query(conn, inactive_query)
        
        # 구글 시트에 업로드
        print("📤 구글 시트 업로드 중...")
        spreadsheet = setup_google_sheets()
        
        if upload_to_sheets(spreadsheet, BRANCH_NAME, active_df, inactive_df):
            print("🎉 데이터 추출 및 업로드 완료!")
            print(f"📊 결과: 유효회원 {len(active_df)}명, 휴면회원 {len(inactive_df)}명")
            print(f"🔗 스프레드시트: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")
        else:
            print("❌ 업로드 실패")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 처리 중 오류 발생: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main() 