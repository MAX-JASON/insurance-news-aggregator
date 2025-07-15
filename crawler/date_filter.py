"""
新聞日期過濾器
News Date Filter

提供日期過濾功能，確保只抓取指定時間範圍內的新聞
"""

import logging
import yaml
import os
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from dateutil import parser

logger = logging.getLogger('crawler.date_filter')

class NewsDateFilter:
    """新聞日期過濾器"""
    
    def __init__(self, config_path: str = None):
        """
        初始化日期過濾器
        
        Args:
            config_path: 配置文件路徑，如果不提供則使用預設配置
        """
        self.config = self._load_config(config_path)
        self.max_age_days = self.config.get('crawler', {}).get('max_news_age_days', 7)
        self.enable_filter = self.config.get('crawler', {}).get('enable_date_filter', True)
        
        logger.info(f"日期過濾器初始化完成 - 最大天數: {self.max_age_days}, 啟用: {self.enable_filter}")
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """載入配置文件"""
        if config_path is None:
            # 使用預設配置路徑
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, '..', 'config', 'config.yaml')
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"無法載入配置文件 {config_path}: {e}, 使用預設配置")
            return {}
    
    def is_within_time_limit(self, published_date: datetime) -> bool:
        """
        檢查新聞發布日期是否在時間限制內
        
        Args:
            published_date: 新聞發布日期
            
        Returns:
            bool: True表示在時間限制內，False表示超出限制
        """
        if not self.enable_filter:
            return True
        
        if not published_date:
            logger.warning("新聞發布日期為空，預設允許")
            return True
        
        # 確保published_date有時區信息
        if published_date.tzinfo is None:
            published_date = published_date.replace(tzinfo=timezone.utc)
        
        # 計算時間差
        now = datetime.now(timezone.utc)
        cutoff_date = now - timedelta(days=self.max_age_days)
        
        within_limit = published_date >= cutoff_date
        
        if not within_limit:
            age_days = (now - published_date).days
            logger.debug(f"新聞超出時間限制: {age_days}天 > {self.max_age_days}天")
        
        return within_limit
    
    def filter_news_list(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        過濾新聞列表，只保留在時間限制內的新聞
        
        Args:
            news_list: 新聞列表
            
        Returns:
            List[Dict]: 過濾後的新聞列表
        """
        if not self.enable_filter:
            logger.info("日期過濾已停用，返回完整新聞列表")
            return news_list
        
        filtered_news = []
        total_count = len(news_list)
        
        for news in news_list:
            published_date = self._extract_published_date(news)
            
            if self.is_within_time_limit(published_date):
                filtered_news.append(news)
            else:
                logger.debug(f"過濾掉過期新聞: {news.get('title', '無標題')[:50]}...")
        
        filtered_count = len(filtered_news)
        removed_count = total_count - filtered_count
        
        logger.info(f"日期過濾完成: 原始 {total_count} 篇，保留 {filtered_count} 篇，移除 {removed_count} 篇")
        
        return filtered_news
    
    def _extract_published_date(self, news: Dict[str, Any]) -> Optional[datetime]:
        """
        從新聞字典中提取發布日期
        
        Args:
            news: 新聞字典
            
        Returns:
            Optional[datetime]: 發布日期，如果無法解析則返回None
        """
        # 嘗試不同的日期欄位名稱
        date_fields = ['published_date', 'publish_date', 'date', 'created_at', 'pubDate']
        
        for field in date_fields:
            date_value = news.get(field)
            if date_value:
                return self._parse_date(date_value)
        
        logger.warning(f"無法從新聞中提取發布日期: {news.get('title', '無標題')[:30]}...")
        return None
    
    def _parse_date(self, date_value: Any) -> Optional[datetime]:
        """
        解析日期值
        
        Args:
            date_value: 日期值（可能是字符串、datetime等）
            
        Returns:
            Optional[datetime]: 解析後的日期，失敗則返回None
        """
        if isinstance(date_value, datetime):
            return date_value
        
        if isinstance(date_value, str):
            try:
                # 使用dateutil.parser進行靈活解析
                parsed_date = parser.parse(date_value)
                
                # 如果沒有時區信息，假設為UTC
                if parsed_date.tzinfo is None:
                    parsed_date = parsed_date.replace(tzinfo=timezone.utc)
                
                return parsed_date
            except Exception as e:
                logger.debug(f"日期解析失敗: {date_value}, 錯誤: {e}")
                return None
        
        logger.debug(f"不支援的日期格式: {type(date_value)}")
        return None
    
    def get_cutoff_date(self) -> datetime:
        """
        獲取截止日期
        
        Returns:
            datetime: 截止日期（早於此日期的新聞將被過濾）
        """
        now = datetime.now(timezone.utc)
        return now - timedelta(days=self.max_age_days)
    
    def update_settings(self, max_age_days: int = None, enable_filter: bool = None):
        """
        更新過濾器設定
        
        Args:
            max_age_days: 最大天數
            enable_filter: 是否啟用過濾
        """
        if max_age_days is not None:
            self.max_age_days = max_age_days
            logger.info(f"更新最大天數設定: {max_age_days}")
        
        if enable_filter is not None:
            self.enable_filter = enable_filter
            status = "啟用" if enable_filter else "停用"
            logger.info(f"更新過濾器狀態: {status}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        獲取過濾器狀態
        
        Returns:
            Dict: 狀態信息
        """
        cutoff_date = self.get_cutoff_date()
        
        return {
            'enabled': self.enable_filter,
            'max_age_days': self.max_age_days,
            'cutoff_date': cutoff_date.isoformat(),
            'cutoff_date_formatted': cutoff_date.strftime('%Y-%m-%d %H:%M:%S UTC')
        }


def create_date_filter(max_age_days: int = 7, enable_filter: bool = True) -> NewsDateFilter:
    """
    創建日期過濾器的便捷函數
    
    Args:
        max_age_days: 最大天數
        enable_filter: 是否啟用過濾
        
    Returns:
        NewsDateFilter: 配置好的日期過濾器
    """
    filter_instance = NewsDateFilter()
    filter_instance.update_settings(max_age_days=max_age_days, enable_filter=enable_filter)
    return filter_instance


def test_date_filter():
    """測試日期過濾器"""
    import json
    
    print("🧪 測試新聞日期過濾器...")
    
    # 創建測試數據
    now = datetime.now(timezone.utc)
    test_news = [
        {
            'title': '最新保險新聞',
            'published_date': now,
            'content': '這是最新的新聞'
        },
        {
            'title': '3天前的新聞',
            'published_date': now - timedelta(days=3),
            'content': '這是3天前的新聞'
        },
        {
            'title': '10天前的新聞',
            'published_date': now - timedelta(days=10),
            'content': '這是10天前的新聞'
        },
        {
            'title': '無日期的新聞',
            'content': '這是沒有日期的新聞'
        }
    ]
    
    # 測試過濾器
    date_filter = create_date_filter(max_age_days=7, enable_filter=True)
    
    print(f"📊 過濾器狀態: {json.dumps(date_filter.get_status(), indent=2, ensure_ascii=False)}")
    print(f"📰 測試新聞數量: {len(test_news)}")
    
    # 執行過濾
    filtered_news = date_filter.filter_news_list(test_news)
    
    print(f"✅ 過濾後新聞數量: {len(filtered_news)}")
    print("\n過濾結果:")
    for i, news in enumerate(filtered_news, 1):
        print(f"  {i}. {news['title']}")
    
    # 測試停用過濾器
    print("\n🔧 測試停用過濾器...")
    date_filter.update_settings(enable_filter=False)
    filtered_news_disabled = date_filter.filter_news_list(test_news)
    print(f"✅ 停用過濾器後新聞數量: {len(filtered_news_disabled)}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_date_filter()
