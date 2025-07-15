"""
數據清洗和去重系統
Data Cleaning and Deduplication System

提供新聞數據的清洗、去重、驗證和品質控制功能
"""

import re
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse
from difflib import SequenceMatcher

from database.models import News, NewsSource, db
from analyzer.insurance_dictionary import is_insurance_related, calculate_insurance_relevance_score

logger = logging.getLogger('data_cleaner')

class NewsDataCleaner:
    """新聞數據清洗器"""
    
    def __init__(self):
        """初始化數據清洗器"""
        self.similarity_threshold = 0.85  # 相似度閾值
        self.min_content_length = 50     # 最小內容長度
        self.max_title_length = 200      # 最大標題長度
        self.min_insurance_score = 0.1   # 最小保險相關性分數
        
        # 無效內容模式
        self.invalid_patterns = [
            r'404|not found|頁面不存在',
            r'error|錯誤|系統維護',
            r'測試|test|example',
            r'廣告|advertisement|sponsor'
        ]
        
        logger.info("🧹 新聞數據清洗系統初始化完成")
    
    def clean_text(self, text: str) -> str:
        """
        清洗文本內容
        
        Args:
            text: 原始文本
            
        Returns:
            清洗後的文本
        """
        if not text:
            return ""
        
        # 移除多餘空白和換行
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 移除HTML標籤
        text = re.sub(r'<[^>]+>', '', text)
        
        # 移除特殊字符（保留中文、英文、數字、基本標點）
        text = re.sub(r'[^\u4e00-\u9fff\w\s\.\,\!\?\:\;\-\(\)\[\]「」『』、。，！？：；]', '', text)
        
        # 移除重複標點
        text = re.sub(r'[。，！？：；]{2,}', '。', text)
        text = re.sub(r'[\.]{2,}', '.', text)
        
        return text.strip()
    
    def clean_url(self, url: str) -> str:
        """
        清洗URL
        
        Args:
            url: 原始URL
            
        Returns:
            清洗後的URL
        """
        if not url:
            return ""
        
        # 移除追蹤參數
        tracking_params = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term']
        
        try:
            parsed = urlparse(url)
            if parsed.query:
                query_parts = []
                for part in parsed.query.split('&'):
                    if '=' in part:
                        key = part.split('=')[0]
                        if key not in tracking_params:
                            query_parts.append(part)
                
                clean_query = '&'.join(query_parts)
                url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if clean_query:
                    url += f"?{clean_query}"
            
            return url
        except:
            return url
    
    def validate_news_article(self, article_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        驗證新聞文章的有效性
        
        Args:
            article_data: 新聞文章資料
            
        Returns:
            (是否有效, 錯誤原因列表)
        """
        errors = []
        
        # 檢查必要欄位
        title = article_data.get('title', '')
        content = article_data.get('content', '')
        url = article_data.get('url', '')
        
        if not title or len(title.strip()) < 5:
            errors.append("標題太短或為空")
        
        if len(title) > self.max_title_length:
            errors.append(f"標題過長（超過{self.max_title_length}字符）")
        
        if not content or len(content.strip()) < self.min_content_length:
            errors.append(f"內容太短（少於{self.min_content_length}字符）")
        
        if not url or not self._is_valid_url(url):
            errors.append("URL無效")
        
        # 檢查無效內容模式
        full_text = f"{title} {content}".lower()
        for pattern in self.invalid_patterns:
            if re.search(pattern, full_text, re.IGNORECASE):
                errors.append(f"包含無效內容模式: {pattern}")
        
        # 檢查保險相關性
        insurance_score = calculate_insurance_relevance_score(full_text)
        if insurance_score < self.min_insurance_score:
            errors.append(f"保險相關性過低: {insurance_score:.3f}")
        
        return len(errors) == 0, errors
    
    def _is_valid_url(self, url: str) -> bool:
        """檢查URL是否有效"""
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except:
            return False
    
    def calculate_content_similarity(self, text1: str, text2: str) -> float:
        """
        計算兩段文本的相似度
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            相似度分數 (0-1)
        """
        if not text1 or not text2:
            return 0.0
        
        # 使用SequenceMatcher計算相似度
        similarity = SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
        return similarity
    
    def find_duplicate_news(self, news_list: List[Dict[str, Any]]) -> List[Tuple[int, int, float]]:
        """
        找出重複的新聞
        
        Args:
            news_list: 新聞列表
            
        Returns:
            重複新聞的索引對和相似度
        """
        duplicates = []
        
        for i in range(len(news_list)):
            for j in range(i + 1, len(news_list)):
                news1 = news_list[i]
                news2 = news_list[j]
                
                # 比較標題相似度
                title_similarity = self.calculate_content_similarity(
                    news1.get('title', ''), 
                    news2.get('title', '')
                )
                
                # 比較內容相似度
                content_similarity = self.calculate_content_similarity(
                    news1.get('content', ''), 
                    news2.get('content', '')
                )
                
                # 綜合相似度（標題權重更高）
                combined_similarity = (title_similarity * 0.7 + content_similarity * 0.3)
                
                if combined_similarity >= self.similarity_threshold:
                    duplicates.append((i, j, combined_similarity))
        
        return duplicates
    
    def remove_duplicates_from_database(self) -> Dict[str, Any]:
        """
        從資料庫中移除重複新聞
        
        Returns:
            清理結果統計
        """
        try:
            logger.info("🔍 開始尋找資料庫中的重複新聞...")
            
            news_articles = News.query.filter_by(status='active').all()
            news_data = []
            
            for news in news_articles:
                news_data.append({
                    'id': news.id,
                    'title': news.title,
                    'content': news.content or '',
                    'url': news.url,
                    'published_date': news.published_date
                })
            
            duplicates = self.find_duplicate_news(news_data)
            
            if not duplicates:
                logger.info("✅ 沒有發現重複新聞")
                return {
                    'total_checked': len(news_data),
                    'duplicates_found': 0,
                    'removed_count': 0,
                    'duplicates': []
                }
            
            # 決定要刪除的新聞（保留較新的）
            to_remove = set()
            duplicate_info = []
            
            for i, j, similarity in duplicates:
                news1 = news_data[i]
                news2 = news_data[j]
                
                # 保留較新的新聞
                if news1['published_date'] > news2['published_date']:
                    to_remove.add(news2['id'])
                    kept_id = news1['id']
                    removed_id = news2['id']
                else:
                    to_remove.add(news1['id'])
                    kept_id = news2['id']
                    removed_id = news1['id']
                
                duplicate_info.append({
                    'similarity': similarity,
                    'kept_id': kept_id,
                    'removed_id': removed_id,
                    'kept_title': news1['title'] if kept_id == news1['id'] else news2['title'],
                    'removed_title': news2['title'] if removed_id == news2['id'] else news1['title']
                })
            
            # 執行刪除
            removed_count = 0
            for news_id in to_remove:
                news = News.query.get(news_id)
                if news:
                    db.session.delete(news)
                    removed_count += 1
            
            db.session.commit()
            
            logger.info(f"✅ 重複新聞清理完成：檢查 {len(news_data)} 則，發現 {len(duplicates)} 組重複，刪除 {removed_count} 則")
            
            return {
                'total_checked': len(news_data),
                'duplicates_found': len(duplicates),
                'removed_count': removed_count,
                'duplicates': duplicate_info
            }
            
        except Exception as e:
            logger.error(f"❌ 重複新聞清理失敗: {e}")
            return {
                'total_checked': 0,
                'duplicates_found': 0,
                'removed_count': 0,
                'error': str(e)
            }
    
    def clean_news_batch(self, news_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量清洗新聞數據
        
        Args:
            news_list: 新聞列表
            
        Returns:
            清洗結果
        """
        try:
            logger.info(f"🧹 開始批量清洗 {len(news_list)} 則新聞...")
            
            cleaned_news = []
            invalid_news = []
            duplicates = []
            
            # 清洗每則新聞
            for i, news in enumerate(news_list):
                try:
                    # 清洗文本
                    cleaned_title = self.clean_text(news.get('title', ''))
                    cleaned_content = self.clean_text(news.get('content', ''))
                    cleaned_summary = self.clean_text(news.get('summary', ''))
                    cleaned_url = self.clean_url(news.get('url', ''))
                    
                    cleaned_news_item = {
                        **news,
                        'title': cleaned_title,
                        'content': cleaned_content,
                        'summary': cleaned_summary,
                        'url': cleaned_url
                    }
                    
                    # 驗證清洗後的新聞
                    is_valid, errors = self.validate_news_article(cleaned_news_item)
                    
                    if is_valid:
                        cleaned_news.append(cleaned_news_item)
                    else:
                        invalid_news.append({
                            'index': i,
                            'news': news,
                            'errors': errors
                        })
                        
                except Exception as e:
                    logger.error(f"❌ 清洗第 {i} 則新聞失敗: {e}")
                    invalid_news.append({
                        'index': i,
                        'news': news,
                        'errors': [f"清洗失敗: {str(e)}"]
                    })
            
            # 去重處理
            if cleaned_news:
                duplicate_pairs = self.find_duplicate_news(cleaned_news)
                duplicates = duplicate_pairs
                
                # 移除重複項（保留第一個）
                to_remove = set()
                for i, j, similarity in duplicate_pairs:
                    to_remove.add(j)  # 移除後面的
                
                # 創建去重後的列表
                final_news = [news for i, news in enumerate(cleaned_news) if i not in to_remove]
            else:
                final_news = []
            
            result = {
                'original_count': len(news_list),
                'cleaned_count': len(cleaned_news),
                'final_count': len(final_news),
                'invalid_count': len(invalid_news),
                'duplicate_count': len(duplicates),
                'cleaned_news': final_news,
                'invalid_news': invalid_news,
                'duplicates': duplicates
            }
            
            logger.info(f"✅ 批量清洗完成：{len(news_list)} → {len(final_news)} 則新聞")
            return result
            
        except Exception as e:
            logger.error(f"❌ 批量清洗失敗: {e}")
            return {
                'error': str(e),
                'original_count': len(news_list),
                'cleaned_news': []
            }

# 全域清洗器實例
_cleaner_instance = None

def get_data_cleaner() -> NewsDataCleaner:
    """取得全域數據清洗器實例"""
    global _cleaner_instance
    if _cleaner_instance is None:
        _cleaner_instance = NewsDataCleaner()
    return _cleaner_instance

if __name__ == "__main__":
    # 測試數據清洗系統
    print("🧪 測試新聞數據清洗系統...")
    
    cleaner = NewsDataCleaner()
    
    # 測試文本清洗
    test_text = "  這是一則  <b>保險</b>  新聞!!!   "
    cleaned = cleaner.clean_text(test_text)
    print(f"文本清洗測試: '{test_text}' → '{cleaned}'")
    
    # 測試URL清洗
    test_url = "https://example.com/news?utm_source=google&utm_medium=cpc&id=123"
    cleaned_url = cleaner.clean_url(test_url)
    print(f"URL清洗測試: {test_url} → {cleaned_url}")
    
    # 測試相似度計算
    text1 = "台灣人壽推出新保險產品"
    text2 = "台灣人壽發表新的保險商品"
    similarity = cleaner.calculate_content_similarity(text1, text2)
    print(f"相似度測試: {similarity:.3f}")
    
    print("✅ 數據清洗系統測試完成")
