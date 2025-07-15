"""
文本處理模組
Text Processing Module

提供中文文本分詞、關鍵字提取等自然語言處理功能
"""

import jieba
import jieba.analyse
import re
import logging
import os
from typing import List, Dict, Set, Tuple, Any
from collections import Counter

from analyzer.insurance_dictionary import ALL_INSURANCE_KEYWORDS

logger = logging.getLogger(__name__)

class TextProcessor:
    """文本處理器類"""
    
    def __init__(self, custom_dict_path: str = None):
        """
        初始化文本處理器
        
        Args:
            custom_dict_path: 自定義詞典路徑
        """
        self.logger = logging.getLogger(__name__)
        
        # 初始化jieba
        self.init_jieba(custom_dict_path)
        
        # 載入同義詞詞典
        self.synonyms = self._load_synonyms()
        
        # 載入停用詞
        self.stop_words = self._load_stop_words()
        
        self.logger.info("✅ 文本處理器初始化完成")
    
    def init_jieba(self, custom_dict_path: str = None):
        """
        初始化jieba分詞器
        
        Args:
            custom_dict_path: 自定義詞典路徑
        """
        try:
            # 添加保險專業詞彙到jieba詞典
            for keyword in ALL_INSURANCE_KEYWORDS:
                jieba.add_word(keyword, freq=10, tag='n')
            
            # 載入自定義詞典（如果提供）
            if custom_dict_path and os.path.exists(custom_dict_path):
                jieba.load_userdict(custom_dict_path)
                self.logger.info(f"✅ 已載入自定義詞典: {custom_dict_path}")
            
            # 調整jieba參數
            jieba.initialize()  # 確保jieba完全載入
            
            self.logger.info("✅ jieba分詞器初始化完成")
            
        except Exception as e:
            self.logger.error(f"❌ 初始化jieba分詞器失敗: {e}")
    
    def _load_synonyms(self) -> Dict[str, List[str]]:
        """
        載入同義詞詞典
        
        Returns:
            同義詞對應表，格式為 {詞: [同義詞列表]}
        """
        # 基本同義詞表（可擴充）
        basic_synonyms = {
            "保險": ["保障", "保單", "保險單"],
            "理賠": ["給付", "賠償", "保險金"],
            "壽險": ["人壽保險", "人壽", "死亡給付"],
            "健康險": ["醫療險", "醫療保險", "疾病險"],
            "金管會": ["金融監督管理委員會", "金融監理單位"],
            "銷售": ["業務", "招攬", "行銷"],
            "保費": ["保險費", "保險費率", "繳費"]
        }
        
        return basic_synonyms
    
    def segment_text(self, text: str) -> List[str]:
        """
        中文文本分詞
        
        Args:
            text: 待分詞的文本
            
        Returns:
            分詞結果列表
        """
        if not text:
            return []
        
        try:
            # 預處理
            text = self._preprocess_text(text)
            
            # 使用jieba進行分詞
            words = jieba.lcut(text)
            
            # 過濾停用詞和標點
            words = [w for w in words if len(w.strip()) > 1 and not self._is_punctuation(w)]
            
            return words
            
        except Exception as e:
            self.logger.error(f"❌ 分詞錯誤: {e}")
            return []
    
    def _preprocess_text(self, text: str) -> str:
        """
        文本預處理，清理文本中的雜訊
        
        Args:
            text: 原始文本
            
        Returns:
            預處理後的文本
        """
        if not text:
            return ""
        
        # 統一全形轉半形
        text = self._full_to_half(text)
        
        # 移除HTML標籤
        text = re.sub(r'<[^>]+>', '', text)
        
        # 統一空白字符
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _full_to_half(self, text: str) -> str:
        """
        全形字符轉半形
        
        Args:
            text: 包含全形字符的文本
            
        Returns:
            轉換後的文本
        """
        result = ""
        for char in text:
            code = ord(char)
            # 全形字符範圍
            if 0xFF01 <= code <= 0xFF5E:
                # 轉為半形
                result += chr(code - 0xFEE0)
            else:
                result += char
        return result
    
    def _is_punctuation(self, word: str) -> bool:
        """
        判斷是否為標點符號
        
        Args:
            word: 單詞
            
        Returns:
            是否為標點符號
        """
        return bool(re.match(r'^[^\w\s]$', word))
        
    def _load_stop_words(self) -> Set[str]:
        """
        載入停用詞表
        
        Returns:
            停用詞集合
        """
        # 基本中文停用詞表
        basic_stop_words = {
            '的', '了', '和', '是', '就', '都', '而', '及', '與', '著',
            '或', '一個', '沒有', '我們', '你們', '他們', '她們', '它們',
            '這', '那', '這個', '那個', '這些', '那些', '這樣', '那樣',
            '之', '得', '地', '有', '在', '上', '下', '不', '可', '里',
            '來', '去', '進', '出', '時', '把', '被', '從', '但', '因為',
            '所以', '如果', '雖然', '只有', '因此', '由於', '如此', '那麼',
            '非常', '很', '太', '越來越', '更加', '最', '比較', '一定', '可能',
            '也', '還', '又', '另外', '只是', '並', '才', '已經', '還是',
            '能', '會', '應該', '可以', '需要', '必須', '要', '想', '看',
            '看到', '聽', '聽到', '知道', '覺得', '認為', '發現', '找到',
            '拿', '給', '對', '對於', '向', '往', '這裡', '那裡', '哪裡',
            '誰', '什麼', '哪個', '怎麼', '多少', '為什麼', '如何'
        }
        
        return basic_stop_words
        
    def _get_stop_words(self) -> List[str]:
        """
        獲取停用詞列表
        
        Returns:
            停用詞列表
        """
        return list(self.stop_words)
    
    def extract_keywords(self, text: str, topK: int = 10) -> List[Tuple[str, float]]:
        """
        從文本中提取關鍵詞
        
        Args:
            text: 待分析文本
            topK: 返回的關鍵詞數量
            
        Returns:
            關鍵詞及其權重列表，格式為 [(關鍵詞, 權重)]
        """
        if not text:
            return []
        
        try:
            # 使用TF-IDF算法提取關鍵詞
            keywords = jieba.analyse.extract_tags(
                text, 
                topK=topK, 
                withWeight=True
            )
            
            return keywords
            
        except Exception as e:
            self.logger.error(f"❌ 提取關鍵詞錯誤: {e}")
            return []
    
    def find_keywords_in_text(self, text: str, keywords: List[str], use_synonym: bool = True) -> Dict[str, int]:
        """
        在文本中查找關鍵字，支援同義詞查找
        
        Args:
            text: 待查找的文本
            keywords: 關鍵字列表
            use_synonym: 是否使用同義詞查找
            
        Returns:
            找到的關鍵字及其出現次數，格式為 {關鍵字: 出現次數}
        """
        if not text or not keywords:
            return {}
        
        try:
            text = text.lower()
            result = {}
            
            # 分詞處理
            segmented_text = self.segment_text(text)
            text_words = set(segmented_text)
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                
                # 精確匹配
                count = text.count(keyword_lower)
                
                # 分詞匹配
                if keyword_lower in text_words:
                    count = max(count, 1)
                
                # 同義詞匹配
                if use_synonym and keyword in self.synonyms:
                    for synonym in self.synonyms[keyword]:
                        synonym_lower = synonym.lower()
                        synonym_count = text.count(synonym_lower)
                        
                        if synonym_lower in text_words:
                            synonym_count = max(synonym_count, 1)
                        
                        if synonym_count > 0:
                            count = max(count, synonym_count)
                
                if count > 0:
                    result[keyword] = count
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ 查找關鍵字錯誤: {e}")
            return {}
    
    def analyze_text_categories(self, text: str, category_keywords: Dict[str, List[str]]) -> Dict[str, float]:
        """
        分析文本所屬類別
        
        Args:
            text: 待分析文本
            category_keywords: 類別關鍵字，格式為 {類別: [關鍵字列表]}
            
        Returns:
            各類別的相關性分數，格式為 {類別: 分數}
        """
        if not text or not category_keywords:
            return {}
        
        try:
            result = {}
            
            for category, keywords in category_keywords.items():
                matched = self.find_keywords_in_text(text, keywords, use_synonym=True)
                
                # 計算類別分數 (考慮關鍵字出現次數)
                if matched:
                    matched_count = sum(matched.values())
                    unique_match_ratio = len(matched) / len(keywords) if keywords else 0
                    
                    # 權重 = 匹配數量 * 唯一匹配率
                    score = matched_count * unique_match_ratio * 100
                    result[category] = min(score, 1.0)
                else:
                    result[category] = 0.0
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ 分析文本類別錯誤: {e}")
            return {}

    def get_text_summary(self, text: str, max_length: int = 200) -> str:
        """
        生成文本摘要
        
        Args:
            text: 原文本
            max_length: 摘要最大長度
            
        Returns:
            文本摘要
        """
        if not text:
            return ""
        
        try:
            # 簡單摘要方法：選擇前幾句話
            sentences = re.split(r'[。！？!?]', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            summary = ""
            for sentence in sentences:
                if len(summary) + len(sentence) <= max_length:
                    summary += sentence + "。"
                else:
                    break
            
            if len(summary) < len(text) and len(summary) < max_length - 3:
                summary += "..."
            
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ 生成摘要錯誤: {e}")
            return text[:max_length] + "..." if len(text) > max_length else text


# 全域文本處理器實例
_processor_instance = None

def get_text_processor() -> TextProcessor:
    """
    取得全域文本處理器實例
    
    Returns:
        TextProcessor實例
    """
    global _processor_instance
    if _processor_instance is None:
        _processor_instance = TextProcessor()
    return _processor_instance


if __name__ == "__main__":
    # 測試文本處理功能
    logging.basicConfig(level=logging.INFO)
    
    test_text = """
    金管會昨日宣佈新的保險業監管措施，要求壽險公司提高資本適足率。
    根據金融監督管理委員會的新規定，保險公司需要增加責任準備金，以應對可能的市場風險。
    台灣人壽與國泰人壽等大型保險公司表示，將全力配合新政策的實施。
    專家指出，這項新措施可能會影響保險商品的設計與定價，消費者可能需要支付較高的保費。
    """
    
    processor = TextProcessor()
    
    print("1. 分詞結果:")
    words = processor.segment_text(test_text)
    print(words)
    
    print("\n2. 關鍵詞提取:")
    keywords = processor.extract_keywords(test_text, topK=8)
    print(keywords)
    
    print("\n3. 關鍵字查找:")
    search_keywords = ["保險", "金管會", "法規"]
    found = processor.find_keywords_in_text(test_text, search_keywords)
    print(found)
    
    print("\n4. 文本摘要:")
    summary = processor.get_text_summary(test_text, max_length=50)
    print(summary)
