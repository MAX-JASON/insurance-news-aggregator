"""
爬蟲輔助模組
Crawler Helper Module

提供爬蟲的輔助功能，特別是用於管理器中的整合功能
"""

import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import os
import json

logger = logging.getLogger('crawler.helper')

class CrawlerHelper:
    """爬蟲輔助類"""
    
    @staticmethod
    def run_all_crawlers(crawler_manager, use_real=True) -> Dict[str, Any]:
        """
        運行所有爬蟲，優先使用真實爬蟲
        
        Args:
            crawler_manager: 爬蟲管理器實例
            use_real: 是否使用真實爬蟲（而非模擬數據）
        
        Returns:
            Dict 包含爬取結果
        """
        all_news = []
        crawl_results = []
        
        # 記錄開始時間
        start_time = time.time()
        
        try:
            # 優先使用真實爬蟲
            if use_real:
                # 1. 使用RSS爬蟲
                if 'rss' in crawler_manager.crawlers:
                    try:
                        logger.info("🔍 使用RSS爬蟲抓取新聞...")
                        rss_news = crawler_manager.crawlers['rss'].crawl_all_feeds()
                        all_news.extend(rss_news)
                        crawl_results.append({
                            'source': 'RSS新聞源',
                            'success': True,
                            'news_count': len(rss_news),
                            'message': f'成功爬取RSS新聞 {len(rss_news)} 則'
                        })
                        logger.info(f"✅ RSS爬蟲完成，獲取 {len(rss_news)} 則新聞")
                    except Exception as e:
                        logger.error(f"❌ RSS爬蟲失敗: {e}")
                        crawl_results.append({
                            'source': 'RSS新聞源', 
                            'success': False,
                            'news_count': 0,
                            'message': f'爬取失敗: {str(e)}'
                        })
                
                # 2. 使用真實保險新聞爬蟲
                if 'real' in crawler_manager.crawlers:
                    try:
                        logger.info("🔍 使用真實新聞爬蟲抓取新聞...")
                        # 檢查是否有 crawl_google_news 方法
                        if hasattr(crawler_manager.crawlers['real'], 'crawl_google_news'):
                            real_news = crawler_manager.crawlers['real'].crawl_google_news()
                            method_name = 'crawl_google_news'
                        # 或者檢查是否有 crawl_all_sources 方法
                        elif hasattr(crawler_manager.crawlers['real'], 'crawl_all_sources'):
                            real_news = crawler_manager.crawlers['real'].crawl_all_sources()
                            method_name = 'crawl_all_sources'
                        else:
                            logger.error("❌ 真實爬蟲缺少適當的爬取方法")
                            real_news = []
                            method_name = "unknown_method"
                            
                        all_news.extend(real_news)
                        crawl_results.append({
                            'source': '真實新聞爬蟲',
                            'success': True,
                            'news_count': len(real_news),
                            'method': method_name,
                            'message': f'成功爬取真實新聞 {len(real_news)} 則'
                        })
                        logger.info(f"✅ 真實爬蟲完成，獲取 {len(real_news)} 則新聞")
                    except Exception as e:
                        logger.error(f"❌ 真實爬蟲失敗: {e}")
                        crawl_results.append({
                            'source': '真實爬蟲', 
                            'success': False,
                            'news_count': 0,
                            'message': f'爬取失敗: {str(e)}'
                        })
                
                # 3. 使用工商時報專用爬蟲
                if 'ctee' in crawler_manager.crawlers:
                    try:
                        logger.info("🔍 使用工商時報專用爬蟲抓取新聞...")
                        ctee_news = crawler_manager.crawlers['ctee'].crawl()
                        all_news.extend(ctee_news)
                        crawl_results.append({
                            'source': '工商時報保險版',
                            'success': True,
                            'news_count': len(ctee_news),
                            'message': f'成功爬取工商時報新聞 {len(ctee_news)} 則'
                        })
                        logger.info(f"✅ 工商時報爬蟲完成，獲取 {len(ctee_news)} 則新聞")
                    except Exception as e:
                        logger.error(f"❌ 工商時報爬蟲失敗: {e}")
                        crawl_results.append({
                            'source': '工商時報保險版', 
                            'success': False,
                            'news_count': 0,
                            'message': f'爬取失敗: {str(e)}'
                        })
            
            # 如果沒有獲得任何新聞，嘗試使用模擬數據
            if not all_news and 'mock' in crawler_manager.crawlers:
                logger.warning("⚠️ 未獲取到真實新聞，使用模擬數據作為備用")
                mock_news = crawler_manager.crawlers['mock'].generate(10)
                all_news.extend(mock_news)
                crawl_results.append({
                    'source': '模擬數據生成器',
                    'success': True,
                    'news_count': len(mock_news),
                    'message': '使用模擬數據作為備用'
                })
            
            # 計算耗時
            elapsed_time = time.time() - start_time
            
            return {
                'total_news': len(all_news),
                'news': all_news,
                'results': crawl_results,
                'elapsed_time': elapsed_time
            }
            
        except Exception as e:
            logger.error(f"運行爬蟲時發生錯誤: {e}")
            return {
                'total_news': 0,
                'news': [],
                'results': [{'success': False, 'message': str(e)}],
                'elapsed_time': time.time() - start_time
            }
