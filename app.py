import streamlit as st
import pandas as pd
import psycopg2
import gspread
import gspread.exceptions
import json
from google.oauth2.service_account import Credentials
from datetime import datetime
import uuid
import hashlib

# 페이지 설정
st.set_page_config(
    page_title="버핏 회원 관리 시스템",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 새로운 버핏 디자인 시스템 적용 - 단순화된 버전
st.markdown("""
<style>
    /* 폰트 임포트 - Pretendard (한글 최적화) */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.6/dist/web/static/pretendard.css');
    
    /* 전체 앱 배경 - 흰색 배경 */
    .stApp {
        background: white;
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    }
    
    /* 메인 헤더 - 단순화된 디자인 */
    .main-header {
        text-align: center;
        padding: 2rem;
        background: white;
        color: #444FA9;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
        border: 2px solid #444FA9;
    }
    
    .main-header h1 {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: #444FA9;
        letter-spacing: -0.025em;
    }
    
    .main-header p {
        font-size: 1rem;
        margin: 0;
        font-weight: 500;
        color: #6b7280;
        letter-spacing: -0.01em;
    }
    
    /* 사이드바 스타일링 */
    .css-1d391kg {
        background: #f9fafb;
        border-right: 1px solid #e5e7eb;
    }
    
    /* 카드 스타일 - 단순화 */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #e5e7eb;
        margin: 1rem 0;
        transition: all 0.2s ease;
    }
    
    .metric-card:hover {
        border-color: #444FA9;
        box-shadow: 0 4px 12px rgba(68, 79, 169, 0.1);
    }
    
    .metric-card h3 {
        color: #444FA9;
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
        letter-spacing: -0.025em;
    }
    
    /* 상태 박스 - 단순화 */
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid;
        font-weight: 500;
        letter-spacing: -0.01em;
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
    
    /* 버튼 스타일 - 단순화 */
    .stButton > button {
        background: #444FA9;
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        font-family: 'Pretendard', sans-serif;
        letter-spacing: -0.01em;
    }
    
    .stButton > button:hover {
        background: #3730a3;
        transform: translateY(-1px);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* 선택 박스 스타일 */
    .stSelectbox > div > div {
        background: white;
        border: 1px solid #d1d5db;
        border-radius: 0.5rem;
        font-family: 'Pretendard', sans-serif;
        transition: all 0.2s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #444FA9;
        box-shadow: 0 0 0 3px rgba(68, 79, 169, 0.1);
    }
    
    /* 데이터프레임 스타일 */
    .dataframe {
        border-radius: 0.5rem;
        overflow: hidden;
        border: 1px solid #e5e7eb;
    }
    
    /* 진행바 스타일 */
    .stProgress > div > div {
        background: #444FA9;
        border-radius: 0.25rem;
        height: 0.5rem;
    }
    
    .stProgress > div {
        background: #e5e7eb;
        border-radius: 0.25rem;
        height: 0.5rem;
    }
    
    /* 사이드바 컨텐츠 */
    .sidebar-content {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border: 1px solid #e5e7eb;
        transition: all 0.2s ease;
    }
    
    .sidebar-content:hover {
        border-color: #444FA9;
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
    
    /* 푸터 - 단순화 */
    .footer {
        text-align: center;
        padding: 2rem;
        background: #f9fafb;
        border-radius: 0.5rem;
        margin-top: 2rem;
        border: 1px solid #e5e7eb;
    }
    
    .footer h4 {
        color: #444FA9;
        font-weight: 700;
        margin-bottom: 1rem;
        font-size: 1.1rem;
    }
    
    /* 특수 효과 제거 */
    .feature-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        border: 1px solid #e5e7eb;
        margin: 0.5rem;
        transition: all 0.2s ease;
    }
    
    .feature-card:hover {
        border-color: #444FA9;
    }
    
    .feature-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
        color: #444FA9;
    }
    
    .feature-text {
        font-size: 0.8rem;
        color: #6b7280;
        font-weight: 500;
    }
    
    /* 알림 스타일 개선 */
    .stAlert {
        border-radius: 0.5rem;
        border: none;
        font-family: 'Pretendard', sans-serif;
        font-weight: 500;
    }
    
    .stSuccess {
        background: #f0fdf4;
        color: #166534;
    }
    
    .stError {
        background: #fef2f2;
        color: #dc2626;
    }
    
    .stWarning {
        background: #fffbeb;
        color: #d97706;
    }
    
    .stInfo {
        background: #f0f9ff;
        color: #0369a1;
    }
    
    /* 반응형 디자인 */
    @media (max-width: 768px) {
        .main-header {
            padding: 1.5rem 1rem;
        }
        
        .main-header h1 {
            font-size: 1.5rem;
        }
        
        .metric-card {
            padding: 1rem;
        }
        
        .sidebar-content {
            padding: 0.75rem;
        }
        
        .footer {
            padding: 1.5rem 1rem;
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
            st.warning("🔧 **구글 시트 연결 설정 필요**: Streamlit Cloud의 Secrets에 google_service_account를 설정해주세요.")
            return None
            
        google_credentials = st.secrets["google_service_account"]
        
        # 필수 키들이 모두 있는지 확인
        required_keys = ["type", "project_id", "private_key", "client_email"]
        missing_keys = [key for key in required_keys if key not in google_credentials or not google_credentials[key]]
        
        if missing_keys:
            st.warning(f"🔧 **구글 서비스 계정 설정 불완전**: 다음 키들이 누락되었거나 비어있습니다: {', '.join(missing_keys)}")
            return None
            
        credentials = Credentials.from_service_account_info(
            google_credentials,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        return gspread.authorize(credentials)
    except Exception as e:
        st.error(f"❌ 구글 시트 연결 실패: {e}")
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
        # 연결 닫기
        if conn:
            conn.close()

def create_google_sheet(member_type, branch_name, df):
    """구글 시트 생성 또는 업데이트"""
    gc = get_google_sheets_client()
    if not gc:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        st.markdown("""
        <div class="warning-box">
        <strong>🔧 구글 시트 연결 없음</strong><br/>
        데이터는 추출되었지만 구글 시트에 업로드할 수 없습니다.<br/>
        아래에서 데이터를 확인하고 CSV로 다운로드하세요.
        </div>
        """, unsafe_allow_html=True)
        
        # 구글 시트 연결이 없어도 결과 반환 (로컬에서 볼 수 있도록)
        return {
            'sheet_name': branch_name,
            'url': f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}",
            'count': len(df),
            'local_only': True
        }
    
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
            # 헤더 정보 + 컬럼 헤더 + 데이터
            data_to_upload = header_info + [df.columns.values.tolist()] + df.values.tolist()
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
    
    # 헤더 - 단순화된 디자인
    st.markdown("""
        <div class="main-header">
            <h1>📊 버핏 회원 관리 시스템</h1>
            <p>유효회원/휴면회원 추출 • 다중 사용자 지원 • 실시간 데이터 처리 • 지점별 시트 자동 관리</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 세션 초기화
    if 'extraction_result' not in st.session_state:
        st.session_state.extraction_result = None
    
    # 사이드바 설정
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.markdown("## 🔧 추출 설정")
        
        # 회원 유형 선택
        member_type = st.selectbox(
            "👥 회원 유형",
            ["유효회원", "휴면회원"],
            help="추출할 회원 유형을 선택하세요"
        )
        
        # 지점 선택
        branches = get_branches()
        selected_branch = st.selectbox(
            "📍 지점 선택",
            branches,
            help="데이터를 추출할 지점을 선택하세요"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        # 시스템 정보
        st.markdown("## ℹ️ 시스템 정보")
        st.markdown("""
        <div class="info-box">
        <strong style="color: #1e40af; font-weight: 600;">🗄️ 데이터베이스</strong><br/>
        레플리카 DB (읽기 전용)<br/><br/>
        
        <strong style="color: #1e40af; font-weight: 600;">📍 사용 가능 지점</strong><br/>
        9개 (전체 + 8개 지점)<br/><br/>
        
        <strong style="color: #1e40af; font-weight: 600;">📊 결과 저장</strong><br/>
        구글 스프레드시트 (지점별 시트)<br/><br/>
        
        <strong style="color: #1e40af; font-weight: 600;">👥 동시 사용자</strong><br/>
        지원<br/><br/>
        
        <strong style="color: #1e40af; font-weight: 600;">🔄 데이터 관리</strong><br/>
        기존 데이터 삭제 후 새로 입력
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        # 연결 테스트
        if st.button("🧪 연결 테스트", type="secondary"):
            with st.spinner("연결 테스트 중..."):
                conn = get_database_connection()
                if conn:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("SELECT 1")
                        cursor.close()
                        st.success("✅ 데이터베이스 연결 성공!")
                    except Exception as e:
                        st.error(f"❌ 데이터베이스 테스트 실패: {e}")
                    finally:
                        conn.close()
                else:
                    st.error("❌ 데이터베이스 연결 실패")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 메인 컨텐츠
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
            <div class="metric-card">
                <h3>📋 데이터 추출</h3>
                <p style="color: #6b7280; margin-bottom: 1.5rem; font-weight: 500;">
                    선택된 조건: <strong style="color: #444FA9;">{}</strong> • <strong style="color: #444FA9;">{}</strong>
                </p>
            </div>
        """.format(member_type, selected_branch), unsafe_allow_html=True)
        
        # 추출 버튼
        if st.button("🚀 데이터 추출 시작", type="primary", use_container_width=True):
            
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
                        if sheet_result.get('local_only', False):
                            st.info(f"""
                            📊 **데이터 추출 완료!** (로컬 모드)
                            
                            - **회원 유형**: {member_type}
                            - **지점**: {selected_branch}
                            - **추출 건수**: {len(df):,}명
                            - **상태**: 구글 시트 연결 없음 (아래에서 CSV 다운로드 가능)
                            """)
                            
                            # CSV 다운로드 버튼
                            csv = df.to_csv(index=False, encoding='utf-8-sig')
                            st.download_button(
                                label="📥 CSV 파일 다운로드",
                                data=csv,
                                file_name=f"{selected_branch}_{member_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv",
                                type="primary"
                            )
                        else:
                            st.success(f"""
                            🎉 **데이터 추출 완료!**
                            
                            - **회원 유형**: {member_type}
                            - **지점**: {selected_branch}
                            - **추출 건수**: {len(df):,}명
                            - **시트명**: {sheet_result['sheet_name']}
                            - **기존 데이터 삭제 후 새로 입력됨**
                            """)
                            
                            # 구글 시트 열기 버튼
                            if st.button("📄 구글 시트 열기", type="secondary"):
                                st.markdown(f"[구글 시트에서 보기]({sheet_result['url']})")
                    else:
                        st.error("❌ 구글 시트 생성에 실패했습니다.")
                    
                    # 진행 표시 제거
                    progress_bar.empty()
                    status_text.empty()
                    
            except Exception as e:
                st.error(f"❌ 처리 중 오류가 발생했습니다: {e}")
                progress_bar.empty()
                status_text.empty()
    
    with col2:
        st.markdown("""
            <div class="metric-card">
                <h3>📈 실시간 현황</h3>
                <p style="color: #6b7280; font-weight: 500;">시스템 상태 및 추출 결과</p>
            </div>
        """, unsafe_allow_html=True)
        
        # 지점별 통계 (간단한 예시)
        if selected_branch != "전체":
            st.markdown(f"""
            <div class="metric-card">
                <h3>📍 선택된 지점</h3>
                <div style="text-align: center; padding: 1rem;">
                    <div style="font-size: 2rem; color: #444FA9; margin-bottom: 0.5rem;">🏢</div>
                    <div style="font-size: 1.2rem; font-weight: 600; color: #1f2937;">{selected_branch}</div>
                    <div style="font-size: 0.9rem; color: #6b7280; font-weight: 500;">대상 지점</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # 최근 추출 결과 표시
        if st.session_state.extraction_result:
            result = st.session_state.extraction_result
            
            st.markdown(f"""
            <div class="metric-card">
                <h3>🎯 최근 추출 결과</h3>
                <div style="padding: 1rem 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span style="color: #6b7280; font-weight: 500;">회원 유형:</span>
                        <strong style="color: #444FA9;">{result['member_type']}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span style="color: #6b7280; font-weight: 500;">지점:</span>
                        <strong style="color: #444FA9;">{result['branch']}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                        <span style="color: #6b7280; font-weight: 500;">추출 건수:</span>
                        <strong style="color: #10b981; font-size: 1.1rem;">{len(result['df']):,}명</strong>
                    </div>
                    <hr style="margin: 1rem 0; border: none; height: 1px; background: #e5e7eb;">
                    <div style="text-align: center;">
                        <a href="{result['sheet_result']['url']}" target="_blank" 
                           style="color: #444FA9; text-decoration: none; font-weight: 600;">
                            📄 구글 시트에서 보기 →
                        </a>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 데이터 미리보기
            st.markdown("""
                <div class="metric-card">
                    <h3>👀 데이터 미리보기</h3>
                </div>
            """, unsafe_allow_html=True)
            st.dataframe(result['df'].head(), use_container_width=True)
    
    # 푸터 - 단순화된 디자인
    st.markdown("""
        <div class="footer">
            <h4>🏢 버핏 회원 관리 시스템</h4>
            <p style="color: #6b7280; margin: 1rem 0; font-weight: 500;">
                💡 다중 사용자 동시 접속 지원 • 📊 실시간 데이터 처리 • 🔄 지점별 시트 자동 업데이트
            </p>
            <hr style="margin: 2rem 0; border: none; height: 1px; background: #e5e7eb;">
            <p style="color: #9ca3af; font-size: 0.875rem; margin: 0; font-weight: 500;">
                © 2024 Butfit Member Management System. All rights reserved.
            </p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 