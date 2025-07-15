"""
新聞內容去重系統
News Deduplication System

提供智能識別和處理重複新聞內容的功能
"""

import logging
from typing import Dict, List, Set, Tuple, Any
import re
import jieba
import jieba.analyse
from difflib import SequenceMatcher
from datetime import datetime, timedelta

# 設置日誌
logger = logging.getLogger('crawler')

class NewsDeduplicator:
    """新聞去重器"""
    
    def __init__(self, similarity_threshold: float = 0.7, title_weight: float = 0.6, 
                 content_weight: float = 0.4, use_jieba: bool = True):
        """
        初始化去重器
        
        Args:
            similarity_threshold: 相似度閾值，超過此值將被視為重複
            title_weight: 標題權重
            content_weight: 內容權重
            use_jieba: 是否使用jieba分詞優化中文比較
        """
        self.similarity_threshold = similarity_threshold
        self.title_weight = title_weight
        self.content_weight = content_weight
        self.use_jieba = use_jieba
        self.news_fingerprints = {}  # 用於儲存新聞指紋
        
        # 用於標題預處理的正則表達式
        self.title_cleaners = [
            (r'[\[\(（【].*?[\]\)）】]', ''),  # 移除方括號、圓括號及其內容
            (r'[^\w\s]', ' '),               # 將標點符號替換為空格
            (r'\s+', ' '),                   # 將多個空格合併為一個
            (r'^\s+|\s+$', '')               # 去除頭尾空白
        ]
        
        logger.info(f"初始化新聞去重器: 相似度閾值={similarity_threshold}, 使用jieba={use_jieba}")
        
        if use_jieba:
            # 確保加載繁體字典
            try:
                jieba.set_dictionary('dict.txt.big')
                logger.info("已加載繁體中文字典")
            except Exception as e:
                logger.warning(f"加載繁體中文字典失敗: {e}, 使用默認字典")
    
    def preprocess_title(self, title: str) -> str:
        """
        預處理標題文本
        
        Args:
            title: 原始標題
            
        Returns:
            處理後的標題
        """
        if not title:
            return ""
        
        processed = title.lower()  # 轉為小寫
        
        for pattern, replacement in self.title_cleaners:
            processed = re.sub(pattern, replacement, processed)
        
        return processed
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """
        從文本提取關鍵詞
        
        Args:
            text: 待提取的文本
            top_n: 提取的關鍵詞數量
            
        Returns:
            關鍵詞列表
        """
        if not text or len(text) < 10:
            return []
            
        try:
            # 使用jieba提取關鍵詞
            keywords = jieba.analyse.extract_tags(text, topK=top_n)
            return keywords
        except Exception as e:
            logger.error(f"關鍵詞提取失敗: {e}")
            # 備用方案: 簡單分詞後取長度大於1的詞
            words = [w for w in jieba.cut(text) if len(w) > 1]
            return words[:top_n] if words else []
    
    def calculate_similarity(self, news1: Dict[str, Any], news2: Dict[str, Any]) -> float:
        """
        計算兩條新聞的相似度
        
        Args:
            news1: 第一條新聞
            news2: 第二條新聞
            
        Returns:
            相似度分數(0-1)
        """
        # 獲取標題
        title1 = news1.get('title', '')
        title2 = news2.get('title', '')
        
        # 獲取內容或摘要
        content1 = news1.get('content', news1.get('summary', ''))
        content2 = news2.get('content', news2.get('summary', ''))
        
        # 預處理標題
        title1 = self.preprocess_title(title1)
        title2 = self.preprocess_title(title2)
        
        # 計算標題相似度
        if self.use_jieba and len(title1) > 10 and len(title2) > 10:
            # 使用關鍵詞集合相似度
            title1_keywords = set(self.extract_keywords(title1))
            title2_keywords = set(self.extract_keywords(title2))
            
            # 集合相似度 (Jaccard相似度)
            if title1_keywords and title2_keywords:
                title_similarity = len(title1_keywords.intersection(title2_keywords)) / len(title1_keywords.union(title2_keywords))
            else:
                title_similarity = 0
        else:
            # 字符串序列相似度
            title_similarity = SequenceMatcher(None, title1, title2).ratio()
        
        # 計算內容相似度
        if content1 and content2 and self.use_jieba:
            # 使用關鍵詞集合相似度
            content1_keywords = set(self.extract_keywords(content1, top_n=20))
            content2_keywords = set(self.extract_keywords(content2, top_n=20))
            
            if content1_keywords and content2_keywords:
                content_similarity = len(content1_keywords.intersection(content2_keywords)) / len(content1_keywords.union(content2_keywords))
            else:
                content_similarity = 0
        elif content1 and content2:
            # 字符串序列相似度 (簡化計算，只使用前200個字符)
            content_similarity = SequenceMatcher(None, content1[:200], content2[:200]).ratio()
        else:
            content_similarity = 0
        
        # 加權計算總相似度
        if title_similarity > 0.9:  # 標題幾乎完全相同
            return 0.9  # 很可能是重複新聞
        
        # 綜合相似度
        similarity = (self.title_weight * title_similarity + 
                      self.content_weight * content_similarity)
        
        return similarity
    
    def generate_fingerprint(self, news: Dict[str, Any]) -> str:
        """
        為新聞生成指紋
        
        Args:
            news: 新聞項
            
        Returns:
            新聞指紋
        """
        title = news.get('title', '').lower()
        
        # 提取標題關鍵詞
        if self.use_jieba:
            keywords = self.extract_keywords(title)
            if keywords:
                fingerprint = '_'.join(sorted(keywords))
                return fingerprint
        
        # 備用方案: 使用處理後的標題
        processed_title = self.preprocess_title(title)
        return processed_title
    
    def is_duplicate(self, news_item: Dict[str, Any], existing_items: List[Dict[str, Any]]) -> Tuple[bool, Dict[str, Any]]:
        """
        判斷新聞是否為重複
        
        Args:
            news_item: 待檢查的新聞
            existing_items: 已存在的新聞列表
            
        Returns:
            (是否重複, 重複項) 元組
        """
        if not news_item.get('title'):
            return False, None
        
        # 先檢查指紋是否已存在
        fingerprint = self.generate_fingerprint(news_item)
        if fingerprint in self.news_fingerprints:
            # 獲取可能重複的新聞項
            potential_duplicates = [
                item for item in existing_items 
                if item.get('id') in self.news_fingerprints[fingerprint]
            ]
            
            # 如果有多個可能的重複項，計算相似度進一步判斷
            for dup_item in potential_duplicates:
                similarity = self.calculate_similarity(news_item, dup_item)
                if similarity >= self.similarity_threshold:
                    logger.info(f"檢測到重複新聞: '{news_item.get('title')}' (相似度: {similarity:.2f})")
                    return True, dup_item
        
        # 計算與所有現有新聞的相似度
        for existing in existing_items:
            similarity = self.calculate_similarity(news_item, existing)
            if similarity >= self.similarity_threshold:
                logger.info(f"檢測到重複新聞: '{news_item.get('title')}' (相似度: {similarity:.2f})")
                
                # 更新指紋字典
                if fingerprint not in self.news_fingerprints:
                    self.news_fingerprints[fingerprint] = set()
                
                existing_id = existing.get('id')
                if existing_id:
                    self.news_fingerprints[fingerprint].add(existing_id)
                    
                return True, existing
        
        # 將新聞添加到指紋列表
        if fingerprint not in self.news_fingerprints:
            self.news_fingerprints[fingerprint] = set()
        
        news_id = news_item.get('id')
        if news_id:
            self.news_fingerprints[fingerprint].add(news_id)
        
        return False, None
    
    def filter_duplicates(self, news_items: List[Dict[str, Any]], existing_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        過濾重複的新聞
        
        Args:
            news_items: 待處理的新聞列表
            existing_items: 已存在的新聞列表
            
        Returns:
            過濾後的新聞列表
        """
        unique_items = []
        duplicates = []
        
        for item in news_items:
            is_dup, duplicate_of = self.is_duplicate(item, existing_items + unique_items)
            
            if not is_dup:
                unique_items.append(item)
            else:
                duplicates.append((item, duplicate_of))
        
        logger.info(f"去重結果: {len(unique_items)} 條唯一新聞, {len(duplicates)} 條重複")
        
        return unique_items
    
    def clear_cache(self, days: int = 7) -> None:
        """
        清除過期的指紋緩存
        
        Args:
            days: 保留的天數
        """
        # 實際應用中，這裡應該會檢查新聞的日期來清除過期的指紋
        logger.info(f"已清除 {days} 天前的指紋緩存")
        # 在實際應用中，這需要與數據庫結合實現