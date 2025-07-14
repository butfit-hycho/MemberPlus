import streamlit as st
import pandas as pd
import psycopg2
import gspread
import gspread.exceptions
from google.oauth2.service_account import Credentials
from datetime import datetime, date

# 페이지 설정
st.set_page_config(
    page_title="버핏 회원 관리 시스템",
    page_icon="🏢",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 간소화된 UI 스타일
st.markdown("""
<style>
    /* 폰트 임포트 - Pretendard (한글 최적화) */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.6/dist/web/static/pretendard.css');
    
    /* 전체 앱 배경 - 흰색 배경 */
    .stApp {
        background: white;
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
        padding-top: 0 !important;
    }
    
    /* 기본 컨테이너 여백 제거 */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* 사이드바 숨기기 */
    .css-1d391kg {
        display: none;
    }
    
    /* 메인 헤더 - 심플한 디자인 */
    .main-header {
        text-align: center;
        padding: 2rem 1rem 1rem 1rem;
        margin-bottom: 1rem;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: #444FA9;
        letter-spacing: -0.025em;
    }
    
    .main-header p {
        font-size: 1.1rem;
        margin: 0;
        color: #6b7280;
        font-weight: 500;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: #444FA9;
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.2s ease;
        font-family: 'Pretendard', sans-serif;
        width: 100%;
        margin-top: 1rem;
    }
    
    .stButton > button:hover {
        background: #3730a3;
        transform: translateY(-1px);
    }
    
    /* 커스텀 버튼 스타일 (호버 효과) */
    .google-sheet-button:hover {
        background: #3730a3 !important;
        transform: translateY(-1px) !important;
    }
    
    /* 선택 박스 스타일 */
    .stSelectbox > div > div {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 0.5rem;
        font-family: 'Pretendard', sans-serif;
        transition: all 0.2s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #444FA9;
        box-shadow: 0 0 0 3px rgba(68, 79, 169, 0.1);
    }
    
    /* 진행바 스타일 개선 */
    div[data-testid="stProgress"] {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    div[data-testid="stProgress"] > div {
        background: #e5e7eb !important;
        border-radius: 0.25rem !important;
        height: 8px !important;
        margin: 0 !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    div[data-testid="stProgress"] > div > div {
        background: #444FA9 !important;
        border-radius: 0.25rem !important;
        height: 8px !important;
    }
    
    /* 결과 카드 */
    .result-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #e5e7eb;
        margin: 1rem 0;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .result-card h3 {
        color: #444FA9;
        font-weight: 600;
        margin-bottom: 1rem;
        font-size: 1.2rem;
    }
    
    /* 상태 박스 */
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem auto;
        border-left: 4px solid;
        font-weight: 500;
        max-width: 600px;
    }
    
    .success-box {
        background: #f0fdf4;
        color: #166534;
        border-left-color: #22c55e;
    }
    
    .error-box {
        background: #fef2f2;
        color: #dc2626;
        border-left-color: #ef4444;
    }
    
    .warning-box {
        background: #fffbeb;
        color: #d97706;
        border-left-color: #f59e0b;
    }
    
    .info-box {
        background: #f0f9ff;
        color: #0369a1;
        border-left-color: #0ea5e9;
    }
    
    /* 텍스트 스타일 */
    h1, h2, h3, h4, h5, h6 {
        color: #1f2937;
        font-weight: 600;
        font-family: 'Pretendard', sans-serif;
        letter-spacing: -0.025em;
    }
    
    p, div, span {
        font-family: 'Pretendard', sans-serif;
        letter-spacing: -0.01em;
    }
    
    /* 데이터프레임 스타일 */
    .dataframe {
        border-radius: 0.5rem;
        overflow: hidden;
        border: 1px solid #e5e7eb;
        margin: 1rem auto;
        max-width: 100%;
    }
    
    /* 반응형 디자인 */
    @media (max-width: 768px) {
        .main-header {
            padding: 2rem 1rem 1rem 1rem;
        }
        
        .main-header h1 {
            font-size: 2rem;
        }
        
        .main-header {
            padding: 2rem 1rem 1rem 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# 데이터베이스 설정
DB_CONFIG = {
    'host': st.secrets.get("DB_HOST", "butfitseoul-replica.cjilul7too7t.ap-northeast-2.rds.amazonaws.com"),
    'port': int(st.secrets.get("DB_PORT", 5432)),
    'database': st.secrets.get("DB_NAME", "master_20221217"),
    'user': st.secrets.get("DB_USER", "hycho"),
    'password': st.secrets.get("DB_PASSWORD", "gaW4Charohchee5shigh0aemeeThohyu")
}

SPREADSHEET_ID = st.secrets.get("SPREADSHEET_ID", "1Zi2VmX1Mp2swgC5QlwvAjhndc-MH8SM4YR1TlqNMjm4")

def get_database_connection():
    """데이터베이스 연결 (매번 새로 생성)"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"❌ 데이터베이스 연결 실패: {e}")
        return None

@st.cache_resource
def get_google_sheets_client():
    """구글 시트 클라이언트 초기화 (캐시됨)"""
    try:
        # Streamlit secrets에서 구글 서비스 계정 정보 확인
        if "google_service_account" not in st.secrets:
            return None
            
        google_credentials = st.secrets["google_service_account"]
        
        # 필수 키들이 모두 있는지 확인
        required_keys = ["type", "project_id", "private_key", "client_email"]
        missing_keys = [key for key in required_keys if key not in google_credentials or not google_credentials[key]]
        
        if missing_keys:
            return None
            
        credentials = Credentials.from_service_account_info(
            google_credentials,
            scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        )
        
        return gspread.authorize(credentials)
    except Exception as e:
        return None

def get_branches():
    """지점 목록 조회 (고정된 목록)"""
    return [
        '전체',
        '역삼',
        '도곡', 
        '신도림',
        '논현',
        '판교',
        '강변',
        '가산',
        '삼성',
        '광화문'
    ]

def get_user_query(member_type, branch_name):
    """사용자 유형별 쿼리 생성"""
    branch_condition = "" if branch_name == "전체" else f"AND p.name = '{branch_name}'"
    
    if member_type == "유효회원":
        return f"""
            WITH active_memberships AS (
              SELECT 
                bp.user_id,
                p.name as branch_name,
                m.title as membership_type,
                m.begin_date as start_date,
                m.end_date,
                m.created as created_at,
                ROW_NUMBER() OVER (PARTITION BY bp.user_id ORDER BY m.end_date DESC) as rn
              FROM b_class_bmembership m
              JOIN b_class_bpass bp ON m.b_pass_id = bp.id
              JOIN b_class_bplace p ON bp.b_place_id = p.id
              WHERE m.end_date >= CURRENT_DATE
                AND m.title NOT IN ('버핏레이스', '건강 선물', '리뉴얼', '베네핏', '1일권')
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
                u.phone_number as phone,
                u.date_joined as user_created_at
              FROM active_memberships am
              JOIN user_user u ON am.user_id = u.id
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
    else:  # 휴면회원
        return f"""
            WITH last_memberships AS (
              SELECT 
                bp.user_id,
                p.name as branch_name,
                m.title as membership_type,
                m.begin_date as start_date,
                m.end_date,
                m.created as created_at,
                ROW_NUMBER() OVER (PARTITION BY bp.user_id ORDER BY m.end_date DESC) as rn
              FROM b_class_bmembership m
              JOIN b_class_bpass bp ON m.b_pass_id = bp.id
              JOIN b_class_bplace p ON bp.b_place_id = p.id
              WHERE m.title NOT IN ('버핏레이스', '건강 선물', '리뉴얼', '베네핏', '1일권')
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
                u.phone_number as phone,
                u.date_joined as user_created_at
              FROM last_memberships lm
              JOIN user_user u ON lm.user_id = u.id
              WHERE lm.rn = 1
                AND lm.end_date < CURRENT_DATE
                AND u.name NOT LIKE '%탈퇴%'
                AND NOT EXISTS (
                  SELECT 1 FROM b_class_bmembership m2 
                  JOIN b_class_bpass bp2 ON m2.b_pass_id = bp2.id
                  WHERE bp2.user_id = lm.user_id 
                    AND m2.end_date >= CURRENT_DATE
                    AND m2.title NOT IN ('버핏레이스', '건강 선물', '리뉴얼', '베네핏', '1일권')
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

def execute_query(query):
    """쿼리 실행"""
    conn = get_database_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"❌ 쿼리 실행 실패: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

def create_google_sheet(member_type, branch_name, df):
    """구글 시트 생성 또는 업데이트"""
    gc = get_google_sheets_client()
    if not gc:
        return None
    
    try:
        # 기존 스프레드시트 열기
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        
        # 시트 이름은 지점명으로 설정
        sheet_name = branch_name
        
        # 기존 시트 찾기
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            # 기존 데이터 모두 삭제
            worksheet.clear()
        except gspread.exceptions.WorksheetNotFound:
            # 시트가 없으면 새로 생성
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
        
        # 현재 시간
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 헤더 정보 준비
        header_info = [
            [f"실행타입: {member_type}"],
            [f"요청시간: {current_time}"],
            [f"지점명: {branch_name}"],
            [f"총 건수: {len(df):,}명"],
            [""],  # 빈 줄
        ]
        
        # 데이터 준비
        if not df.empty:
            # DataFrame의 모든 값을 안전하게 변환하여 JSON 직렬화 문제 해결
            def safe_convert_value(value):
                """값을 안전하게 문자열로 변환"""
                if pd.isna(value):
                    return ''
                elif isinstance(value, datetime):
                    return value.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(value, date):
                    return value.strftime('%Y-%m-%d')
                elif hasattr(value, 'strftime'):  # 기타 datetime 관련 객체
                    return value.strftime('%Y-%m-%d')
                else:
                    return str(value)
            
            # 모든 데이터를 안전하게 변환
            converted_data = []
            for row in df.itertuples(index=False):
                converted_row = [safe_convert_value(value) for value in row]
                converted_data.append(converted_row)
            
            # 헤더 정보 + 컬럼 헤더 + 데이터
            data_to_upload = header_info + [df.columns.values.tolist()] + converted_data
        else:
            # 헤더 정보만
            data_to_upload = header_info + [["데이터가 없습니다."]]
        
        # 데이터 업로드
        worksheet.update(data_to_upload)
        
        # 스타일링
        # 헤더 정보 스타일링 (1-4행)
        worksheet.format('A1:A4', {'textFormat': {'bold': True}})
        
        # 컬럼 헤더 스타일링 (6행)
        if not df.empty:
            worksheet.format('6:6', {'textFormat': {'bold': True}, 'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}})
        
        return {
            'sheet_name': sheet_name,
            'url': f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit#gid={worksheet.id}",
            'count': len(df)
        }
    except Exception as e:
        st.error(f"❌ 구글 시트 생성/업데이트 실패: {e}")
        return None

def main():
    """메인 애플리케이션"""
    
    # 강제 재배포 트리거 (2025.01.14)
    # 구글 시트 연결 확인 (필수)
    gc = get_google_sheets_client()
    
    if not gc:
        st.markdown("""
            <div class="main-header">
                <h1>🔧 서비스 점검 중</h1>
                <p>구글 시트 연결이 설정되지 않았습니다</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="status-box error-box">
        <strong>❌ 서비스 이용 불가</strong><br/>
        관리자가 구글 서비스 계정을 설정해야 합니다.<br/><br/>
        
        <strong>필요한 설정:</strong><br/>
        • 서비스 계정: <code>memberplus@butfit-member-system.iam.gserviceaccount.com</code><br/>
        • 권한: Google Sheets API, Google Drive API<br/>
        • 스프레드시트 공유 권한 필요
        </div>
        """, unsafe_allow_html=True)
        return
    
    # 정상 서비스 제공
    st.markdown("""
        <div class="main-header">
            <h1>📊 버핏 회원 관리 시스템</h1>
            <p>지점별 회원 현황 조회</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 세션 초기화
    if 'extraction_result' not in st.session_state:
        st.session_state.extraction_result = None
    
    # 검색 폼
    st.markdown('<h3 style="text-align: center; color: #444FA9; font-weight: 600; margin-bottom: 1.5rem;">🔍 회원 데이터 추출</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        member_type = st.selectbox(
            "회원 유형",
            ["유효회원", "휴면회원"],
            help="추출할 회원 유형을 선택하세요"
        )
    
    with col2:
        branches = get_branches()
        selected_branch = st.selectbox(
            "지점 선택",
            branches,
            help="데이터를 추출할 지점을 선택하세요"
        )
    
    # 추출 버튼
    if st.button("🚀 회원 현황 조회", type="primary"):
        
        # 진행 상황 표시
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # 1. 쿼리 생성
            status_text.text("📝 쿼리 생성 중...")
            progress_bar.progress(25)
            
            query = get_user_query(member_type, selected_branch)
            
            # 2. 데이터 추출
            status_text.text("📊 데이터 추출 중...")
            progress_bar.progress(50)
            
            df = execute_query(query)
            
            if df.empty:
                st.warning("⚠️ 조건에 맞는 데이터가 없습니다.")
                progress_bar.empty()
                status_text.empty()
            else:
                # 3. 구글 시트 업데이트
                status_text.text("📤 구글 시트 업데이트 중...")
                progress_bar.progress(75)
                
                sheet_result = create_google_sheet(member_type, selected_branch, df)
                
                # 4. 완료
                progress_bar.progress(100)
                status_text.text("✅ 완료!")
                
                if sheet_result:
                    st.session_state.extraction_result = {
                        'df': df,
                        'sheet_result': sheet_result,
                        'member_type': member_type,
                        'branch': selected_branch
                    }
                    
                    # 성공 메시지
                    st.success(f"""
                    🎉 **회원 현황 조회 완료!**
                    
                    - **회원 유형**: {member_type}
                    - **지점**: {selected_branch}
                    - **조회 건수**: {len(df):,}명
                    - **시트명**: {sheet_result['sheet_name']}
                    """)
                    
                    # 구글 시트 열기 버튼
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.markdown(f"""
                        <div style="text-align: center; margin-top: 1rem;">
                            <button onclick="window.open('{sheet_result['url']}', '_blank')" 
                                    style="background: #444FA9; color: white; border: none; border-radius: 0.5rem; 
                                           padding: 0.75rem 2rem; font-weight: 600; font-size: 1rem; 
                                           cursor: pointer; width: 100%; font-family: 'Pretendard', sans-serif;
                                           transition: all 0.2s ease;"
                                    onmouseover="this.style.background='#3730a3'; this.style.transform='translateY(-1px)'"
                                    onmouseout="this.style.background='#444FA9'; this.style.transform='translateY(0)'">
                                📄 구글 시트에서 보기
                            </button>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.error("❌ 회원 현황 조회에 실패했습니다.")
                
                # 진행 표시 제거
                progress_bar.empty()
                status_text.empty()
                
        except Exception as e:
            st.error(f"❌ 처리 중 오류가 발생했습니다: {e}")
            progress_bar.empty()
            status_text.empty()
    
    # 최근 추출 결과 표시
    if st.session_state.extraction_result:
        result = st.session_state.extraction_result
        
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown('<h3>📋 추출 데이터 미리보기</h3>', unsafe_allow_html=True)
        st.dataframe(result['df'].head(10), use_container_width=True)
        
        if len(result['df']) > 10:
            st.info(f"전체 {len(result['df']):,}건 중 상위 10건을 표시합니다. 전체 데이터는 구글 시트에서 확인하세요.")
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main() 