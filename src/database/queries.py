import logging
from typing import Dict, Any, Optional, List
from config.database import QUERIES, DYNAMIC_FILTERS

logger = logging.getLogger(__name__)

class QueryBuilder:
    def __init__(self):
        self.queries = QUERIES
        self.dynamic_filters = DYNAMIC_FILTERS
    
    def build_query(self, query_type: str, filters: Optional[Dict[str, Any]] = None) -> str:
        """
        동적 쿼리 생성
        
        Args:
            query_type: 'active_users', 'inactive_users', 또는 'branches'
            filters: 동적 필터 조건 딕셔너리
                    예: {'branch_name': '강남점', 'date_range': {'start_date': '2023-01-01', 'end_date': '2023-12-31'}}
        
        Returns:
            완성된 SQL 쿼리 문자열
        """
        if query_type not in self.queries:
            raise ValueError(f"지원되지 않는 쿼리 타입: {query_type}")
        
        base_query = self.queries[query_type]
        
        # branches 쿼리는 필터 적용 안함
        if query_type == 'branches':
            return base_query
        
        # 동적 필터 생성
        dynamic_filter_parts = []
        
        if filters:
            for filter_name, filter_value in filters.items():
                if filter_name in self.dynamic_filters:
                    filter_template = self.dynamic_filters[filter_name]
                    
                    if filter_name == 'date_range' and isinstance(filter_value, dict):
                        # 날짜 범위 필터
                        filter_part = filter_template.format(
                            start_date=filter_value.get('start_date'),
                            end_date=filter_value.get('end_date')
                        )
                    else:
                        # 일반 필터
                        filter_part = filter_template.format(value=filter_value)
                    
                    dynamic_filter_parts.append(filter_part)
        
        # 동적 필터를 쿼리에 삽입
        dynamic_filters_str = " ".join(dynamic_filter_parts) if dynamic_filter_parts else ""
        final_query = base_query.format(dynamic_filters=dynamic_filters_str)
        
        logger.info(f"동적 쿼리 생성 완료: {query_type}")
        logger.debug(f"생성된 쿼리: {final_query}")
        
        return final_query
    
    def get_active_users_query(self, filters: Optional[Dict[str, Any]] = None) -> str:
        """유효회원 조회 쿼리 생성"""
        return self.build_query('active_users', filters)
    
    def get_inactive_users_query(self, filters: Optional[Dict[str, Any]] = None) -> str:
        """휴면회원 조회 쿼리 생성"""
        return self.build_query('inactive_users', filters)
    
    def get_branches_query(self) -> str:
        """지점 목록 조회 쿼리 생성"""
        return self.build_query('branches')
    
    def validate_filters(self, filters: Dict[str, Any]) -> bool:
        """필터 유효성 검사"""
        if not filters:
            return True
        
        for filter_name in filters.keys():
            if filter_name not in self.dynamic_filters:
                logger.warning(f"지원되지 않는 필터: {filter_name}")
                return False
        
        return True 