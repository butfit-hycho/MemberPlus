import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 데이터베이스 연결 설정
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'butfitseoul-replica.cjilul7too7t.ap-northeast-2.rds.amazonaws.com'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'username': os.getenv('DB_USERNAME', 'hycho'),
    'password': os.getenv('DB_PASSWORD', 'gaW4Charohchee5shigh0aemeeThohyu'),
    'database': os.getenv('DB_DATABASE', 'master_20221217'),
    'driver': os.getenv('DB_DRIVER', 'postgresql')
}

# 실제 쿼리 설정
QUERIES = {
    'active_users': """
        WITH membership_data AS (
            SELECT
                a.id AS mbs1_id,
                TO_CHAR(f.pay_date, 'YYYY-MM-DD') AS mbs1_결제일,
                TO_CHAR(f.pay_date, 'YYYY-MM') AS mbs1_결제월,
                a.begin_date AS mbs1_시작일,
                a.end_date AS mbs1_종료일,
                TO_CHAR(a.end_date, 'YYYY-MM') AS mbs1_종료월,
                a.title AS mbs1_상품명,
                b.item_price AS mbs1_가격,
                d.name AS mbs1_지점,
                e.id AS mbs1_user_id,
                e.name AS mbs1_user_name,
                REGEXP_REPLACE (e.phone_number, '(02|.{3})(.+)(.{4})', '\\1-\\2-\\3')  AS mbs1_user_phone,
                ROW_NUMBER() OVER (PARTITION BY e.id ORDER BY a.end_date DESC) AS rn,
                e.birth_date as mbs1_user_birth
            FROM
                b_payment_btransactionlog b
                LEFT JOIN b_class_bmembership a ON a.transaction_log_id = b.id
                LEFT JOIN b_class_bpass c ON c.id = a.b_pass_id
                LEFT JOIN b_class_bplace d ON d.id = b.b_place_id
                LEFT JOIN user_user e ON e.id = c.user_id
                LEFT JOIN b_payment_btransaction f ON f.id = b.transaction_id
            WHERE
                a.refund_transaction_id IS NULL
                AND a.id IS NOT NULL
                {dynamic_filters}
        ),
        -- 현재 유효한 멤버십이 있는 회원 (현재 날짜 이후까지 멤버십이 존재하는 회원)
        active_membership AS (
            SELECT *
            FROM membership_data
            WHERE mbs1_종료일 >= CURRENT_DATE  -- 현재 유효한 멤버십만 선택
              AND rn = 1 -- 가장 최근 멤버십만 선택
              AND mbs1_상품명 NOT LIKE '%버핏레이스%' -- 제외할 멤버십 1
              AND mbs1_상품명 NOT LIKE '%건강 선물%' -- 제외할 멤버십 2
              AND mbs1_상품명 NOT LIKE '%리뉴얼%' -- 제외할 멤버십 3
              AND mbs1_상품명 NOT LIKE '%베네핏%' -- 제외할 멤버십 4
        )
        -- 최종 결과 출력
        SELECT 
            am.mbs1_user_name AS "회원 이름",
            am.mbs1_user_phone AS "전화번호",
            am.mbs1_user_birth as "생년월",
            am.mbs1_상품명 AS "현재 멤버십 상품명",
            am.mbs1_시작일 AS "이용 시작일",
            am.mbs1_종료일 AS "이용 종료일"
        FROM 
            active_membership am
        WHERE
            am.mbs1_user_name not like '%(탈퇴)%'
        ORDER BY 
            am.mbs1_user_name ASC, am.mbs1_종료일 DESC
    """,
    
    'inactive_users': """
        WITH membership_data AS (
            SELECT
                a.id AS mbs1_id,
                TO_CHAR(f.pay_date, 'YYYY-MM-DD') AS mbs1_결제일,
                TO_CHAR(f.pay_date, 'YYYY-MM') AS mbs1_결제월,
                a.begin_date AS mbs1_시작일,
                a.end_date AS mbs1_종료일,
                TO_CHAR(a.end_date, 'YYYY-MM') AS mbs1_종료월,
                a.title AS mbs1_상품명,
                b.item_price AS mbs1_가격,
                d.name AS mbs1_지점,
                e.id AS mbs1_user_id,
                e.name AS mbs1_user_name,
                REGEXP_REPLACE (e.phone_number, '(02|.{3})(.+)(.{4})', '\\1-\\2-\\3') AS mbs1_user_phone,
                ROW_NUMBER() OVER (PARTITION BY e.id ORDER BY a.end_date DESC) AS rn
            FROM
                b_payment_btransactionlog b
                LEFT JOIN b_class_bmembership a ON a.transaction_log_id = b.id
                LEFT JOIN b_class_bpass c ON c.id = a.b_pass_id
                LEFT JOIN b_class_bplace d ON d.id = b.b_place_id
                LEFT JOIN user_user e ON e.id = c.user_id
                LEFT JOIN b_payment_btransaction f ON f.id = b.transaction_id
            WHERE
                a.refund_transaction_id IS NULL
                AND a.id IS NOT NULL
                {dynamic_filters}
        ),
        -- 현재 유효한 멤버십이 있는 회원 (현재 날짜 이후까지 멤버십이 존재하는 회원)
        active_membership AS (
            SELECT DISTINCT mbs1_user_id
            FROM membership_data
            WHERE mbs1_종료일 >= CURRENT_DATE
        ),
        -- 현재 유효한 멤버십이 없는 회원 중에서 가장 최근의 멤버십 데이터 조회
        inactive_membership AS (
            SELECT *
            FROM membership_data
            WHERE mbs1_종료일 < CURRENT_DATE  -- 현재보다 과거에 종료된 멤버십만 선택
              AND rn = 1 -- 가장 최근 멤버십만 선택
              AND mbs1_user_id NOT IN (SELECT mbs1_user_id FROM active_membership) -- 현재 유효한 멤버십이 없는 회원만 선택
              AND mbs1_상품명 NOT LIKE '%버핏레이스%' -- 제외할 멤버십 1
              AND mbs1_상품명 NOT LIKE '%건강 선물%' -- 제외할 멤버십 2
              AND mbs1_상품명 NOT LIKE '%리뉴얼%' -- 제외할 멤버십 3
              AND mbs1_상품명 NOT LIKE '%베네핏%' -- 제외할 멤버십 4
              AND mbs1_상품명 NOT LIKE '%1일권%' -- 제외할 멤버십 5
        )
        -- 최종 결과 출력
        SELECT 
            im.mbs1_user_name AS "회원 이름",
            im.mbs1_user_phone AS "전화번호",
            im.mbs1_상품명 AS "마지막 멤버십 상품명",
            im.mbs1_시작일 AS "이용 시작일",
            im.mbs1_종료일 AS "이용 종료일"
        FROM 
            inactive_membership im
        WHERE 
            im.mbs1_user_name not like '%(탈퇴)%'
        ORDER BY 
            im.mbs1_user_name ASC, im.mbs1_종료일 DESC
    """,
    
    'branches': """
        SELECT DISTINCT d.name AS branch_name
        FROM b_class_bplace d
        WHERE d.name IS NOT NULL
        ORDER BY d.name
    """
}

# 동적 필터 조건들
DYNAMIC_FILTERS = {
    'branch_name': "AND d.name LIKE '{value}'",
    'date_range': "AND f.pay_date BETWEEN '{start_date}' AND '{end_date}'",
    'membership_type': "AND a.title LIKE '%{value}%'"
} 