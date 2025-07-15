#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
測試分析引擎的多維度評分與文本處理功能
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, List

from analyzer.engine import InsuranceNewsAnalyzer
from analyzer.text_processor import get_text_processor
from analyzer.importance_rating import ImportanceRater
from analyzer.cache import get_cache

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger('test_analyzer')

def create_test_article() -> Dict[str, Any]:
    """創建測試文章"""
    return {
        'title': '金管會公布保險業最新監管政策，壽險公司須增提準備金因應長壽風險',
        'content': '''
        金融監督管理委員會昨日公布最新保險業監理政策，要求所有壽險公司自明年起增提責任準備金，以因應國人平均壽命延長帶來的長壽風險。
        
        根據金管會的說明，台灣已進入高齡社會，65歲以上人口佔總人口比例超過14%，預計2025年將成為超高齡社會。壽險公司銷售的終身壽險、年金保險等長期性商品，面臨的長壽風險日益嚴峻，因此有必要調整準備金提存標準。
        
        新規定將分三年實施：第一年增提3%、第二年增提5%、第三年增提7%。市場人士預估，此政策可能影響壽險業獲利，但有利於產業長期健全發展。
        
        國泰人壽、富邦人壽等大型壽險公司表示，將配合政策調整，並可能重新檢視長期性保險商品的費率結構。保險局局長強調，此次調整是為了確保保險業者能夠履行對保戶的長期承諾，保障消費者權益。
        
        專家分析指出，消費者可能會看到部分長期性保險商品的保費調整，建議民眾在此政策正式實施前，審慎評估自身保險需求並做好規劃。
        ''',
        'summary': '金管會要求壽險業增提準備金因應長壽風險，將分三年實施，影響壽險業獲利但有利於產業長期健全發展',
        'source': '財經日報',
        'published_date': datetime.now(),
        'url': 'https://example.com/news/20230705-insurance',
        'category': 'finance',
    }

def create_test_articles() -> List[Dict[str, Any]]:
    """創建多篇測試文章"""
    return [
        {
            'title': '金管會公布保險業最新監管政策，壽險公司須增提準備金因應長壽風險',
            'content': '金融監督管理委員會昨日公布最新保險業監理政策，要求所有壽險公司自明年起增提責任準備金，以因應國人平均壽命延長帶來的長壽風險。',
            'summary': '金管會要求壽險業增提準備金因應長壽風險，將分三年實施，影響壽險業獲利但有利於產業長期健全發展',
            'source': '財經日報',
            'published_date': datetime.now(),
        },
        {
            'title': '投保新知：儲蓄險vs投資型保單，哪個更適合退休規劃？',
            'content': '在規劃退休金時，許多人會考慮購買儲蓄險或投資型保單。儲蓄險提供穩定的保證利率，適合風險承受度較低的人；而投資型保單則連結投資標的，有機會獲取更高報酬，但也承擔較高風險。',
            'summary': '比較儲蓄險和投資型保單在退休規劃中的優缺點',
            'source': '理財週刊',
            'published_date': datetime.now(),
        },
        {
            'title': '數位轉型加速，保險業線上投保服務成長50%',
            'content': '受到疫情影響，保險業數位轉型腳步加快，根據保險局統計，去年線上投保件數較前年成長50%，投保金額更是大增65%。各家保險公司紛紛加碼投資數位服務，提供更便利的線上保單管理、理賠申請功能。',
            'summary': '保險業數位服務快速成長，線上投保件數年增50%',
            'source': '科技日報',
            'published_date': datetime.now(),
        },
    ]

def test_text_processor():
    """測試文本處理功能"""
    logger.info("============ 測試文本處理器 ============")
    test_text = "金融監督管理委員會昨日公布最新保險業監理政策，要求所有壽險公司自明年起增提責任準備金，以因應國人平均壽命延長帶來的長壽風險。"
    
    processor = get_text_processor()
    
    # 測試分詞
    logger.info("測試分詞功能")
    segmented = processor.segment_text(test_text)
    logger.info(f"分詞結果: {segmented}")
    
    # 測試關鍵詞提取
    logger.info("\n測試關鍵詞提取")
    keywords = processor.extract_keywords(test_text, topK=8)
    logger.info(f"關鍵詞: {keywords}")
    
    # 測試關鍵詞查找
    logger.info("\n測試關鍵詞查找")
    search_keywords = ["金管會", "保險業", "準備金", "壽險"]
    found = processor.find_keywords_in_text(test_text, search_keywords)
    logger.info(f"查找結果: {found}")
    
    # 測試摘要生成
    logger.info("\n測試摘要生成")
    summary = processor.get_text_summary(test_text * 3, max_length=100)
    logger.info(f"摘要: {summary}")
    
    return True

def test_importance_rating():
    """測試重要性評分功能"""
    logger.info("\n\n============ 測試重要性評分 ============")
    
    rater = ImportanceRater()
    test_article = create_test_article()
    
    # 測試多維度評分
    logger.info("測試多維度重要性評分")
    score = rater.rate_importance(test_article)
    logger.info(f"重要性分數: {score:.3f}")
    
    # 測試業務影響分析
    logger.info("\n測試業務影響分析")
    impact = rater.analyze_business_impact(test_article)
    logger.info(f"業務影響: {impact}")
    
    # 測試客戶興趣評估
    logger.info("\n測試客戶興趣評估")
    interest = rater.calculate_client_interest(test_article)
    logger.info(f"客戶興趣: {interest}")
    
    return True

def test_analyzer():
    """測試分析引擎"""
    logger.info("\n\n============ 測試分析引擎 ============")
    
    analyzer = InsuranceNewsAnalyzer()
    test_article = create_test_article()
    
    # 測試完整分析
    logger.info("測試完整文章分析")
    result = analyzer.analyze_news_article(test_article)
    
    logger.info(f"分析完成，重要性分數: {result.get('importance', {}).get('final_score', 0):.3f}")
    logger.info(f"業務影響類型: {result.get('business_impact', {}).get('type', '未知')}")
    logger.info(f"客戶興趣等級: {result.get('client_interest', {}).get('level', '未知')}")
    logger.info(f"提取的關鍵詞: {[kw['word'] for kw in result.get('keywords', [])][:5]}")
    
    # 測試多篇文章分析
    logger.info("\n測試多篇文章分析")
    test_articles = create_test_articles()
    for i, article in enumerate(test_articles):
        logger.info(f"分析第 {i+1} 篇文章: {article['title']}")
        result = analyzer.analyze_news_article(article)
        logger.info(f"重要性: {result.get('importance', {}).get('final_score', 0):.3f}, "
                   f"類型: {result.get('business_impact', {}).get('type', '未知')}, "
                   f"客戶興趣: {result.get('client_interest', {}).get('level', '未知')}")
    
    return True

def test_cache():
    """測試快取功能"""
    logger.info("\n\n============ 測試快取功能 ============")
    
    cache = get_cache()
    
    # 清理所有快取
    logger.info("清理現有快取")
    cache.clear_category('analysis')
    
    # 測試寫入與讀取
    test_data = {'test': 'data', 'value': 123}
    logger.info("測試寫入快取")
    cache.set('analysis', 'test_key', test_data)
    
    logger.info("測試讀取快取")
    cached_data = cache.get('analysis', 'test_key')
    logger.info(f"快取讀取結果: {cached_data}")
    
    # 測試快取統計
    logger.info("測試快取統計")
    stats = cache.get_cache_stats()
    logger.info(f"快取統計: {stats}")
    
    return True

def main():
    """執行所有測試"""
    logger.info("開始測試分析模組功能...")
    
    # 測試文本處理
    if test_text_processor():
        logger.info("✅ 文本處理測試成功")
    else:
        logger.error("❌ 文本處理測試失敗")
    
    # 測試重要性評分
    if test_importance_rating():
        logger.info("✅ 重要性評分測試成功")
    else:
        logger.error("❌ 重要性評分測試失敗")
    
    # 測試分析引擎
    if test_analyzer():
        logger.info("✅ 分析引擎測試成功")
    else:
        logger.error("❌ 分析引擎測試失敗")
    
    # 測試快取功能
    if test_cache():
        logger.info("✅ 快取功能測試成功")
    else:
        logger.error("❌ 快取功能測試失敗")
    
    logger.info("\n\n所有測試完成！")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
