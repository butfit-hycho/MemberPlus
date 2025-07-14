import logging
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from config.database import DATABASE_CONFIG

logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self):
        self.engine = None
        self.connection = None
        self._connect()
    
    def _connect(self):
        """데이터베이스 연결 설정"""
        try:
            config = DATABASE_CONFIG
            
            if config['driver'] == 'mysql':
                connection_string = f"mysql+pymysql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
            elif config['driver'] == 'postgresql':
                connection_string = f"postgresql+psycopg2://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
            else:
                raise ValueError(f"지원되지 않는 데이터베이스 드라이버: {config['driver']}")
            
            self.engine = create_engine(connection_string, echo=False)
            self.connection = self.engine.connect()
            
            logger.info(f"데이터베이스 연결 성공: {config['host']}:{config['port']}/{config['database']}")
            
        except SQLAlchemyError as e:
            logger.error(f"데이터베이스 연결 실패: {str(e)}")
            raise
    
    def execute_query(self, query, params=None):
        """쿼리 실행 및 결과 반환 (DataFrame)"""
        try:
            logger.info(f"쿼리 실행: {query[:100]}...")
            
            if params:
                result = pd.read_sql_query(text(query), self.connection, params=params)
            else:
                result = pd.read_sql_query(text(query), self.connection)
            
            logger.info(f"쿼리 실행 완료: {len(result)}건의 데이터 조회")
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"쿼리 실행 실패: {str(e)}")
            raise
    
    def test_connection(self):
        """연결 테스트"""
        try:
            result = self.execute_query("SELECT 1 as test")
            return len(result) > 0
        except Exception as e:
            logger.error(f"연결 테스트 실패: {str(e)}")
            return False
    
    def close(self):
        """연결 종료"""
        if self.connection:
            self.connection.close()
            logger.info("데이터베이스 연결 종료")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 