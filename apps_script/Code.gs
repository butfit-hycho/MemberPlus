/**
 * 유효회원/휴면회원 추출 시스템 - Google Apps Script 버전
 * 레플리카 데이터베이스에서 유효회원과 휴면회원을 동적으로 추출하여 구글 스프레드시트에 업로드
 */

// 데이터베이스 연결 정보
const DB_CONFIG = {
  host: 'butfitseoul-replica.cjilul7too7t.ap-northeast-2.rds.amazonaws.com',
  port: 5432,
  database: 'master_20221217',
  username: 'hycho',
  password: 'gaW4Charohchee5shigh0aemeeThohyu'
};

// 구글 스프레드시트 ID
const SPREADSHEET_ID = '1Zi2VmX1Mp2swgC5QlwvAjhndc-MH8SM4YR1TlqNMjm4';

/**
 * 메인 함수 - 웹 UI 실행
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('유효회원/휴면회원 추출')
    .addItem('데이터 추출 시작', 'showMainDialog')
    .addItem('지점 목록 새로고침', 'refreshBranches')
    .addToUi();
}

/**
 * 메인 다이얼로그 표시
 */
function showMainDialog() {
  const html = HtmlService.createHtmlOutputFromFile('index')
    .setWidth(800)
    .setHeight(600);
  
  SpreadsheetApp.getUi()
    .showModalDialog(html, '유효회원/휴면회원 추출 시스템');
}

/**
 * 데이터베이스 연결
 */
function connectToDatabase() {
  try {
    const url = `jdbc:postgresql://${DB_CONFIG.host}:${DB_CONFIG.port}/${DB_CONFIG.database}`;
    const conn = Jdbc.getConnection(url, DB_CONFIG.username, DB_CONFIG.password);
    
    console.log('데이터베이스 연결 성공');
    return conn;
  } catch (error) {
    console.error('데이터베이스 연결 실패:', error);
    throw new Error('데이터베이스 연결에 실패했습니다: ' + error.message);
  }
}

/**
 * 지점 목록 조회
 */
function getBranches() {
  const conn = connectToDatabase();
  
  try {
    const query = `
      SELECT DISTINCT branch_name
      FROM membership 
      WHERE branch_name IS NOT NULL 
        AND branch_name != ''
      ORDER BY branch_name;
    `;
    
    const stmt = conn.createStatement();
    const results = stmt.executeQuery(query);
    
    const branches = ['전체'];
    while (results.next()) {
      const branchName = results.getString('branch_name');
      if (branchName && branchName.trim() !== '') {
        branches.push(branchName);
      }
    }
    
    results.close();
    stmt.close();
    conn.close();
    
    return branches;
  } catch (error) {
    conn.close();
    throw new Error('지점 목록 조회 실패: ' + error.message);
  }
}

/**
 * 유효회원 쿼리 생성
 */
function getActiveUsersQuery(branchName) {
  const branchCondition = branchName === '전체' ? '' : 
    `AND m.branch_name = '${branchName}'`;
  
  return `
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
        ${branchCondition}
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
  `;
}

/**
 * 휴면회원 쿼리 생성
 */
function getInactiveUsersQuery(branchName) {
  const branchCondition = branchName === '전체' ? '' : 
    `AND m.branch_name = '${branchName}'`;
  
  return `
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
        ${branchCondition}
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
  `;
}

/**
 * 데이터 추출 및 업로드
 */
function extractAndUploadData(branchName) {
  try {
    const conn = connectToDatabase();
    
    // 유효회원 데이터 추출
    console.log('유효회원 데이터 추출 중...');
    const activeQuery = getActiveUsersQuery(branchName);
    const activeData = executeQuery(conn, activeQuery);
    
    // 휴면회원 데이터 추출
    console.log('휴면회원 데이터 추출 중...');
    const inactiveQuery = getInactiveUsersQuery(branchName);
    const inactiveData = executeQuery(conn, inactiveQuery);
    
    conn.close();
    
    // 구글 시트에 업로드
    console.log('구글 시트 업로드 중...');
    const result = uploadToGoogleSheets(branchName, activeData, inactiveData);
    
    return {
      success: true,
      message: '데이터 추출 및 업로드 완료',
      activeCount: activeData.length,
      inactiveCount: inactiveData.length,
      sheets: result.sheets
    };
    
  } catch (error) {
    console.error('데이터 추출 실패:', error);
    return {
      success: false,
      message: '데이터 추출 실패: ' + error.message
    };
  }
}

/**
 * 쿼리 실행
 */
function executeQuery(conn, query) {
  const stmt = conn.createStatement();
  const results = stmt.executeQuery(query);
  
  const data = [];
  const metaData = results.getMetaData();
  const columnCount = metaData.getColumnCount();
  
  // 헤더 추가
  const headers = [];
  for (let i = 1; i <= columnCount; i++) {
    headers.push(metaData.getColumnName(i));
  }
  data.push(headers);
  
  // 데이터 추가
  while (results.next()) {
    const row = [];
    for (let i = 1; i <= columnCount; i++) {
      const value = results.getString(i);
      row.push(value || '');
    }
    data.push(row);
  }
  
  results.close();
  stmt.close();
  
  return data;
}

/**
 * 구글 시트에 업로드
 */
function uploadToGoogleSheets(branchName, activeData, inactiveData) {
  const spreadsheet = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheets = [];
  
  // 시트 이름 생성
  const activeSheetName = `${branchName}_유효회원`;
  const inactiveSheetName = `${branchName}_휴면회원`;
  const summarySheetName = `${branchName}_요약`;
  
  // 기존 시트 삭제 (있는 경우)
  [activeSheetName, inactiveSheetName, summarySheetName].forEach(name => {
    const existingSheet = spreadsheet.getSheetByName(name);
    if (existingSheet) {
      spreadsheet.deleteSheet(existingSheet);
    }
  });
  
  // 유효회원 시트 생성
  const activeSheet = spreadsheet.insertSheet(activeSheetName);
  if (activeData.length > 0) {
    activeSheet.getRange(1, 1, activeData.length, activeData[0].length).setValues(activeData);
    activeSheet.getRange(1, 1, 1, activeData[0].length).setFontWeight('bold');
  }
  sheets.push(activeSheetName);
  
  // 휴면회원 시트 생성
  const inactiveSheet = spreadsheet.insertSheet(inactiveSheetName);
  if (inactiveData.length > 0) {
    inactiveSheet.getRange(1, 1, inactiveData.length, inactiveData[0].length).setValues(inactiveData);
    inactiveSheet.getRange(1, 1, 1, inactiveData[0].length).setFontWeight('bold');
  }
  sheets.push(inactiveSheetName);
  
  // 요약 시트 생성
  const summarySheet = spreadsheet.insertSheet(summarySheetName);
  const summaryData = [
    ['구분', '수량'],
    ['유효회원', activeData.length - 1], // 헤더 제외
    ['휴면회원', inactiveData.length - 1], // 헤더 제외
    ['총합', (activeData.length - 1) + (inactiveData.length - 1)],
    ['추출 시간', new Date().toLocaleString('ko-KR')]
  ];
  
  summarySheet.getRange(1, 1, summaryData.length, 2).setValues(summaryData);
  summarySheet.getRange(1, 1, 1, 2).setFontWeight('bold');
  sheets.push(summarySheetName);
  
  // 첫 번째 시트로 이동
  spreadsheet.setActiveSheet(activeSheet);
  
  return { sheets };
}

/**
 * 스프레드시트 URL 가져오기
 */
function getSpreadsheetUrl() {
  return `https://docs.google.com/spreadsheets/d/${SPREADSHEET_ID}`;
}

/**
 * 테스트 함수
 */
function testConnection() {
  try {
    const conn = connectToDatabase();
    const stmt = conn.createStatement();
    const results = stmt.executeQuery('SELECT 1 as test');
    
    if (results.next()) {
      console.log('연결 테스트 성공');
      return { success: true, message: '데이터베이스 연결 성공' };
    }
    
    results.close();
    stmt.close();
    conn.close();
    
  } catch (error) {
    console.error('연결 테스트 실패:', error);
    return { success: false, message: '연결 테스트 실패: ' + error.message };
  }
} 