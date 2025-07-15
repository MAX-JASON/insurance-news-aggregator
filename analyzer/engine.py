"""
台灣保險新聞聚合器 - 分析引擎
提供文本分析、情感分析、關鍵詞提取和趨勢分析功能
整合文本處理、重要性評分和結果緩存
"""

import logging
import re
import os
import json
import jieba
import jieba.analyse
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional, Set, Union
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

from config.logging import get_logger
from analyzer.insurance_dictionary import (
    get_insurance_keywords, 
    get_insurance_companies,
    is_insurance_related,
    extract_insurance_keywords,
    calculate_insurance_relevance_score,
    INSURANCE_COMPANIES,
    INSURANCE_PRODUCTS,
    INSURANCE_TERMS,
    REGULATORY_BODIES,
    FINANCIAL_TERMS,
    MEDICAL_TERMS
)
from analyzer.cache import get_cache, cached_analysis, invalidate_cache
from analyzer.text_processor import get_text_processor, TextProcessor
from analyzer.importance_rating import ImportanceRater

# 初始化日誌
logger = get_logger(__name__)

class InsuranceNewsAnalyzer:
    """保險新聞分析引擎"""
    
    def __init__(self):
        """初始化分析引擎"""
        self.logger = logger
        
        # 初始化相關組件
        self.text_processor = get_text_processor()
        self.importance_rater = ImportanceRater()
        self.cache = get_cache()
        
        # 載入保險專業詞庫
        self._load_insurance_categories()
        
        # 情感詞典設置
        self._setup_sentiment_words()
        
        # TF-IDF 向量化器 (用於文本相似度比較和聚類)
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            stop_words=self.text_processor._get_stop_words()
        )
        
        logger.info("🧠 保險新聞分析引擎初始化完成")
    
    def _load_insurance_categories(self):
        """載入保險分類關鍵詞庫"""
        try:
            # 使用擴展後的保險詞典分類
            self.insurance_categories = {
                '保險公司': list(INSURANCE_COMPANIES),
                '商品類型': list(INSURANCE_PRODUCTS),
                '保險術語': list(INSURANCE_TERMS),
                '法規監管': list(REGULATORY_BODIES),
                '金融概念': list(FINANCIAL_TERMS),
                '醫療健康': list(MEDICAL_TERMS)
            }
            
            # 統計關鍵詞總數
            total_keywords = sum(len(words) for words in self.insurance_categories.values())
            logger.info(f"✅ 保險關鍵詞庫載入完成，共 {len(self.insurance_categories)} 類，總計 {total_keywords} 個關鍵詞")
        
        except Exception as e:
            logger.error(f"❌ 載入保險關鍵詞失敗: {e}")
            self.insurance_categories = {}
    
    def _setup_sentiment_words(self):
        """設置情感詞典"""
        self.positive_words = {
            # 積極情感詞彙
            '成長', '增加', '提升', '改善', '優化', '突破', '創新',
            '便利', '效率', '保障', '安全', '穩定', '優質', '領先',
            '成功', '獲利', '收益', '機會', '前景', '樂觀', '正面',
            '滿意', '卓越', '傑出', '優勢', '創新', '拓展', '提高',
            '卓越', '傑出', '優秀', '強大', '創紀錄', '突破性',
            '增長', '優惠', '獎勵', '節約', '回饋', '多元化'
        }
        
        self.negative_words = {
            # 消極情感詞彙
            '下降', '減少', '惡化', '風險', '損失', '困難', '挑戰',
            '問題', '缺陷', '不足', '危機', '衰退', '虧損', '負面',
            '擔憂', '不確定', '不穩定', '威脅', '障礙', '限制',
            '違規', '罰款', '衰退', '滑落', '降低', '退步', '疲軟',
            '失敗', '嚴重', '困境', '糾紛', '糾紛', '訴訟', '投訴',
            '危險', '警告', '嚴厲', '批評', '責難', '質疑', '爭議'
        }
        
        logger.info("✅ 情感詞典設置完成，正面詞彙 %d 個，負面詞彙 %d 個", 
                   len(self.positive_words), len(self.negative_words))
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        提取文本關鍵詞
        
        Args:
            text: 輸入文本
            top_k: 返回關鍵詞數量
            
        Returns:
            關鍵詞列表，格式為[(詞語, 權重), ...]
        """
        try:
            if not text or not text.strip():
                return []
            
            # 使用文本處理器提取關鍵詞
            keywords = self.text_processor.extract_keywords(text, topK=top_k)
            
            logger.debug(f"提取關鍵詞: {keywords[:5] if keywords else '無'}")
            return keywords
            
        except Exception as e:
            logger.error(f"關鍵詞提取失敗: {e}")
            return []
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        分析文本情感
        
        Args:
            text: 輸入文本
            
        Returns:
            情感分析結果
        """
        try:
            if not text or not text.strip():
                return {
                    'sentiment': 'neutral',
                    'score': 0.0,
                    'confidence': 0.0,
                    'positive_words': [],
                    'negative_words': []
                }
            
            # 使用文本處理器進行分詞
            words = self.text_processor.segment_text(text)
            
            # 統計正負面詞語
            positive_words = [word for word in words if word in self.positive_words]
            negative_words = [word for word in words if word in self.negative_words]
            
            # 計算情感分數
            positive_score = len(positive_words)
            negative_score = len(negative_words)
            total_score = positive_score - negative_score
            
            # 正規化分數
            max_possible = max(positive_score + negative_score, 1)
            normalized_score = total_score / max_possible
            
            # 判斷情感傾向
            if normalized_score > 0.1:
                sentiment = 'positive'
            elif normalized_score < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            # 計算信心度 (考慮情感詞數量佔比)
            sentiment_word_ratio = (positive_score + negative_score) / max(len(words), 1)
            confidence = abs(normalized_score) * min(sentiment_word_ratio * 5, 1.0)
            
            result = {
                'sentiment': sentiment,
                'score': normalized_score,
                'confidence': confidence,
                'positive_words': positive_words,
                'negative_words': negative_words,
                'word_count': len(words),
                'sentiment_word_count': positive_score + negative_score,
                'sentiment_ratio': sentiment_word_ratio
            }
            
            logger.debug(f"情感分析結果: {sentiment} (分數: {normalized_score:.3f}, 信心度: {confidence:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"情感分析失敗: {e}")
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'positive_words': [],
                'negative_words': []
            }
    
    def classify_insurance_category(self, text: str) -> Dict[str, Any]:
        """
        分類保險新聞類別
        
        Args:
            text: 輸入文本
            
        Returns:
            分類結果
        """
        try:
            if not text or not text.strip():
                return {'category': 'unknown', 'confidence': 0.0, 'matches': {}}
            
            # 使用文本處理器分析文本類別
            category_scores = self.text_processor.analyze_text_categories(
                text, 
                {k: list(v) for k, v in self.insurance_categories.items()}
            )
            
            # 查找關鍵詞匹配
            category_matches = {}
            for category, keywords in self.insurance_categories.items():
                matches = self.text_processor.find_keywords_in_text(text, list(keywords), use_synonym=True)
                if matches:
                    category_matches[category] = matches
            
            # 找出最佳匹配類別
            if category_scores:
                # 找出得分最高的類別
                best_category = max(category_scores, key=category_scores.get)
                max_score = category_scores[best_category]
                
                # 計算信心度 (相對於第二高的類別)
                sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
                
                # 如果只有一個類別或者第一名顯著高於第二名
                if len(sorted_categories) == 1 or (len(sorted_categories) > 1 and sorted_categories[0][1] > sorted_categories[1][1] * 1.5):
                    confidence = min(max_score * 1.2, 1.0)  # 增加信心度
                else:
                    # 計算與第二名的差距作為信心度
                    confidence = min(max_score / sorted_categories[1][1] if sorted_categories[1][1] > 0 else 1.0, 1.0)
                
                result = {
                    'category': best_category,
                    'confidence': confidence,
                    'matches': category_matches,
                    'all_scores': category_scores,
                    'top_categories': sorted_categories[:3]  # 返回前三名
                }
            else:
                result = {
                    'category': 'unknown',
                    'confidence': 0.0,
                    'matches': {},
                    'all_scores': {},
                    'top_categories': []
                }
            
            logger.debug(f"分類結果: {result['category']} (信心度: {result.get('confidence', 0):.3f})")
            return result
            
        except Exception as e:
            logger.error(f"文本分類失敗: {e}")
            return {'category': 'unknown', 'confidence': 0.0, 'matches': {}}
    
    def find_similar_articles(self, target_text: str, article_list: List[str], 
                            top_k: int = 5) -> List[Tuple[int, float]]:
        """
        找出相似文章
        
        Args:
            target_text: 目標文本
            article_list: 文章列表
            top_k: 返回相似文章數量
            
        Returns:
            相似文章索引和相似度列表
        """
        try:
            if not target_text or not article_list:
                return []
            
            # 準備文本列表
            texts = [target_text] + article_list
            
            # 對文本進行分詞處理
            processed_texts = []
            for text in texts:
                words = jieba.cut(text)
                processed_text = ' '.join(words)
                processed_texts.append(processed_text)
            
            # 計算TF-IDF矩陣
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(processed_texts)
            
            # 計算相似度
            target_vector = tfidf_matrix[0:1]
            article_vectors = tfidf_matrix[1:]
            
            similarities = cosine_similarity(target_vector, article_vectors)[0]
            
            # 獲取最相似的文章
            similar_indices = np.argsort(similarities)[::-1][:top_k]
            results = [(idx, similarities[idx]) for idx in similar_indices 
                      if similarities[idx] > 0.1]  # 過濾掉相似度過低的文章
            
            logger.debug(f"找到 {len(results)} 篇相似文章")
            return results
            
        except Exception as e:
            logger.error(f"相似文章查找失敗: {e}")
            return []
    
    def analyze_trends(self, articles_data: List[Dict[str, Any]], 
                      time_range: int = 30) -> Dict[str, Any]:
        """
        分析新聞趨勢
        
        Args:
            articles_data: 文章數據列表，包含title, content, published_date等字段
            time_range: 分析時間範圍（天數）
            
        Returns:
            趨勢分析結果
        """
        try:
            if not articles_data:
                return {'trends': {}, 'hot_topics': [], 'sentiment_trend': {}}
            
            # 過濾時間範圍內的文章
            cutoff_date = datetime.now() - timedelta(days=time_range)
            recent_articles = [
                article for article in articles_data
                if article.get('published_date') and 
                   article['published_date'] >= cutoff_date
            ]
            
            if not recent_articles:
                logger.warning("沒有找到指定時間範圍內的文章")
                return {'trends': {}, 'hot_topics': [], 'sentiment_trend': {}}
            
            # 關鍵詞趨勢分析
            all_keywords = []
            daily_keywords = defaultdict(list)
            daily_sentiment = defaultdict(list)
            
            for article in recent_articles:
                text = f"{article.get('title', '')} {article.get('content', '')}"
                
                # 提取關鍵詞
                keywords = self.extract_keywords(text, top_k=10)
                all_keywords.extend([kw[0] for kw in keywords])
                
                # 按日期分組關鍵詞
                date_str = article['published_date'].strftime('%Y-%m-%d')
                daily_keywords[date_str].extend([kw[0] for kw in keywords])
                
                # 情感分析
                sentiment = self.analyze_sentiment(text)
                daily_sentiment[date_str].append(sentiment['score'])
            
            # 統計熱門關鍵詞
            keyword_counter = Counter(all_keywords)
            hot_topics = keyword_counter.most_common(20)
            
            # 計算每日平均情感
            sentiment_trend = {}
            for date, scores in daily_sentiment.items():
                if scores:
                    sentiment_trend[date] = {
                        'average_sentiment': np.mean(scores),
                        'sentiment_variance': np.var(scores),
                        'article_count': len(scores)
                    }
            
            # 關鍵詞趨勢
            keyword_trends = {}
            for date, keywords in daily_keywords.items():
                keyword_counter = Counter(keywords)
                keyword_trends[date] = dict(keyword_counter.most_common(10))
            
            result = {
                'analysis_period': {
                    'start_date': cutoff_date.strftime('%Y-%m-%d'),
                    'end_date': datetime.now().strftime('%Y-%m-%d'),
                    'total_articles': len(recent_articles)
                },
                'hot_topics': hot_topics,
                'keyword_trends': keyword_trends,
                'sentiment_trend': sentiment_trend,
                'category_distribution': self._analyze_category_distribution(recent_articles)
            }
            
            logger.info(f"趨勢分析完成，共分析 {len(recent_articles)} 篇文章")
            return result
            
        except Exception as e:
            logger.error(f"趨勢分析失敗: {e}")
            return {'trends': {}, 'hot_topics': [], 'sentiment_trend': {}}
    
    def _analyze_category_distribution(self, articles: List[Dict[str, Any]]) -> Dict[str, int]:
        """分析文章類別分布"""
        category_count = defaultdict(int)
        
        for article in articles:
            text = f"{article.get('title', '')} {article.get('content', '')}"
            classification = self.classify_insurance_category(text)
            category_count[classification['category']] += 1
        
        return dict(category_count)
    
    def cluster_articles(self, articles_data: List[Dict[str, Any]], 
                        n_clusters: int = 5) -> Dict[str, Any]:
        """
        對文章進行聚類分析
        
        Args:
            articles_data: 文章數據列表
            n_clusters: 聚類數量
            
        Returns:
            聚類結果
        """
        try:
            if len(articles_data) < n_clusters:
                n_clusters = max(1, len(articles_data))
            
            # 準備文本數據
            texts = []
            for article in articles_data:
                text = f"{article.get('title', '')} {article.get('content', '')}"
                words = jieba.cut(text)
                processed_text = ' '.join(words)
                texts.append(processed_text)
            
            if not texts:
                return {'clusters': {}, 'cluster_centers': []}
            
            # TF-IDF向量化
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            
            # K-means聚類
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(tfidf_matrix)
            
            # 組織聚類結果
            clusters = defaultdict(list)
            for idx, label in enumerate(cluster_labels):
                clusters[f"cluster_{label}"].append({
                    'index': idx,
                    'title': articles_data[idx].get('title', ''),
                    'published_date': articles_data[idx].get('published_date')
                })
            
            # 提取聚類中心關鍵詞
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            cluster_centers = []
            
            for i, center in enumerate(kmeans.cluster_centers_):
                top_indices = center.argsort()[-10:][::-1]
                top_keywords = [feature_names[idx] for idx in top_indices]
                cluster_centers.append({
                    f"cluster_{i}": top_keywords
                })
            
            result = {
                'clusters': dict(clusters),
                'cluster_centers': cluster_centers,
                'n_clusters': n_clusters,
                'total_articles': len(articles_data)
            }
            
            logger.info(f"文章聚類完成，共 {n_clusters} 個聚類")
            return result
            
        except Exception as e:
            logger.error(f"文章聚類失敗: {e}")
            return {'clusters': {}, 'cluster_centers': []}
    
    def generate_summary(self, text: str, max_sentences: int = 3) -> str:
        """
        生成文本摘要
        
        Args:
            text: 輸入文本
            max_sentences: 最大句子數量
            
        Returns:
            摘要文本
        """
        try:
            if not text or not text.strip():
                return ""
            
            # 使用文本處理器生成摘要
            summary = self.text_processor.get_text_summary(text, max_length=max_sentences*100)
            
            logger.debug(f"生成摘要，原文長度 {len(text)} 字元，摘要長度 {len(summary)} 字元")
            
            return summary
            
        except Exception as e:
            logger.error(f"摘要生成失敗: {e}")
            return text[:200] + "..." if len(text) > 200 else text
    
    def analyze_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        對單篇文章進行完整分析
        
        Args:
            article_data: 文章數據，包含title, content等字段
            
        Returns:
            完整分析結果
        """
        try:
            title = article_data.get('title', '')
            content = article_data.get('content', '')
            text = f"{title} {content}"
            
            if not text.strip():
                return {'error': '文章內容為空'}
            
            # 執行各項分析
            keywords = self.extract_keywords(text, top_k=10)
            sentiment = self.analyze_sentiment(text)
            classification = self.classify_insurance_category(text)
            summary = self.generate_summary(content, max_sentences=3)
            
            result = {
                'article_info': {
                    'title': title,
                    'content_length': len(content),
                    'published_date': article_data.get('published_date'),
                    'source': article_data.get('source')
                },
                'keywords': keywords,
                'sentiment_analysis': sentiment,
                'classification': classification,
                'summary': summary,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"文章分析完成: {title[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"文章分析失敗: {e}")
            return {'error': str(e)}
    
    @cached_analysis('analysis')
    def analyze_news_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        完整分析單篇新聞文章
        
        Args:
            article_data: 新聞文章數據，包含 title, content, summary 等
            
        Returns:
            完整的分析結果
        """
        try:
            # 提取文章內容
            title = article_data.get('title', '')
            content = article_data.get('content', '')
            summary = article_data.get('summary', '')
            full_text = f"{title} {content} {summary}".strip()
            
            if not full_text:
                return self._empty_analysis_result()
            
            # 1. 保險相關性分析
            insurance_relevance = calculate_insurance_relevance_score(full_text)
            insurance_keywords = extract_insurance_keywords(full_text)
            is_insurance = is_insurance_related(full_text)
            
            # 2. 關鍵詞提取
            keywords = self.extract_keywords(full_text, top_k=15)
            
            # 3. 情感分析
            sentiment = self.analyze_sentiment(full_text)
            
            # 4. 保險類別分類
            category_info = self.classify_insurance_category(full_text)
            
            # 5. 多維度重要性評分
            importance_result = self._calculate_multidimensional_importance(article_data)
            
            # 6. 業務影響分析
            business_impact = self.importance_rater.analyze_business_impact(article_data)
            
            # 7. 客戶興趣評分
            client_interest = self.importance_rater.calculate_client_interest(article_data)
            
            # 8. 文本統計
            segmented_words = self.text_processor.segment_text(full_text)
            word_count = len(segmented_words)
            reading_time = max(1, word_count // 200)  # 假設每分鐘讀200個詞
            
            # 生成智能摘要（如果沒有摘要）
            auto_summary = ""
            if not summary and content and len(content) > 100:
                auto_summary = self.generate_summary(content, max_sentences=3)
            
            analysis_result = {
                # 基本信息
                'analyzed_at': datetime.now(),
                'text_length': len(full_text),
                'word_count': word_count,
                'reading_time': reading_time,
                
                # 保險相關性
                'insurance_relevance': {
                    'score': insurance_relevance,
                    'is_related': is_insurance,
                    'keywords': insurance_keywords[:15],  # 最多15個關鍵詞
                    'keyword_count': len(insurance_keywords)
                },
                
                # 關鍵詞
                'keywords': [{'word': word, 'weight': weight} for word, weight in keywords],
                
                # 情感分析
                'sentiment': sentiment,
                
                # 分類
                'category': category_info,
                
                # 重要性評分（多維度）
                'importance': importance_result,
                
                # 業務影響
                'business_impact': business_impact,
                
                # 客戶興趣
                'client_interest': client_interest,
                
                # 內容特徵
                'features': {
                    'has_title': bool(title),
                    'has_content': bool(content),
                    'has_summary': bool(summary),
                    'title_length': len(title),
                    'content_length': len(content),
                    'auto_summary': auto_summary
                }
            }
            
            logger.info(f"✅ 新聞分析完成: 保險相關度={insurance_relevance:.3f}, 重要性={importance_result.get('final_score', 0):.3f}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ 新聞分析失敗: {e}")
            return self._empty_analysis_result()
    
    def _empty_analysis_result(self) -> Dict[str, Any]:
        """返回空的分析結果"""
        return {
            'analyzed_at': datetime.now(),
            'text_length': 0,
            'word_count': 0,
            'reading_time': 0,
            'insurance_relevance': {
                'score': 0.0,
                'is_related': False,
                'keywords': [],
                'keyword_count': 0
            },
            'keywords': [],
            'sentiment': {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.0
            },
            'category': {
                'category': 'unknown',
                'confidence': 0.0
            },
            'importance': {
                'final_score': 0.0,
                'dimensions': {}
            },
            'business_impact': {
                'type': '未知',
                'level': '低',
                'urgency': '一般參考',
                'action': '追蹤新聞後續發展'
            },
            'client_interest': {
                'level': '低',
                'score': 0.0,
                'reason': '一般行業資訊'
            },
            'features': {
                'has_title': False,
                'has_content': False,
                'has_summary': False,
                'title_length': 0,
                'content_length': 0
            }
        }
    
    def _calculate_multidimensional_importance(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        計算新聞多維度重要性評分
        
        Args:
            article_data: 文章數據
            
        Returns:
            多維度評分結果
        """
        try:
            # 使用重要性評分器計算多維度評分
            importance_score = self.importance_rater.rate_importance(article_data)
            
            # 對文章數據進行重要性維度計算
            title = article_data.get('title', '')
            summary = article_data.get('summary', '')
            content = article_data.get('content', '')
            
            dimensions = self.importance_rater.calculate_dimensions(
                article_data, title, summary, content
            )
            
            # 擴展評分結果
            result = {
                'final_score': importance_score,
                'dimensions': dimensions,
                'level': self._get_importance_level(importance_score)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"多維度重要性評分計算失敗: {e}")
            return {'final_score': 0.5, 'dimensions': {}, 'level': '中'}
    
    def _get_importance_level(self, score: float) -> str:
        """根據分數確定重要性等級"""
        if score >= 0.75:
            return '高'
        elif score >= 0.4:
            return '中'
        else:
            return '低'

# 全局分析器實例
analyzer = None

def get_analyzer() -> InsuranceNewsAnalyzer:
    """獲取分析器實例（單例模式）"""
    global analyzer
    if analyzer is None:
        analyzer = InsuranceNewsAnalyzer()
    return analyzer


# 便捷函數
def analyze_news_article(article_data: Dict[str, Any]) -> Dict[str, Any]:
    """分析單篇新聞文章"""
    return get_analyzer().analyze_article(article_data)

def extract_article_keywords(text: str, top_k: int = 10) -> List[Tuple[str, float]]:
    """提取文章關鍵詞"""
    return get_analyzer().extract_keywords(text, top_k)

def analyze_article_sentiment(text: str) -> Dict[str, Any]:
    """分析文章情感"""
    return get_analyzer().analyze_sentiment(text)

def classify_article_category(text: str) -> Dict[str, Any]:
    """分類文章類別"""
    return get_analyzer().classify_insurance_category(text)

def analyze_news_trends(articles: List[Dict[str, Any]], days: int = 30) -> Dict[str, Any]:
    """分析新聞趨勢"""
    return get_analyzer().analyze_trends(articles, days)
