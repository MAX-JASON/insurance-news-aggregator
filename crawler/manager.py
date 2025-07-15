"""
爬蟲管理器
Crawler Manager

統一管理所有爬蟲的執行和調度
"""

import logging
import threading
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# 避免循環依賴
import importlib

# 導入輔助模組
from crawler.helper import CrawlerHelper
from crawler.date_filter import NewsDateFilter

logger = logging.getLogger('crawler.manager')

class CrawlerManager:
    """爬蟲管理器"""
    
    def __init__(self):
        # 初始化日期過濾器
        self.date_filter = NewsDateFilter()
        
        # 動態加載模組
        mock_generator = importlib.import_module('crawler.mock_generator').MockNewsGenerator
        rss_crawler = importlib.import_module('crawler.rss_crawler').RSSNewsCrawler
        
        try:
            ctee_crawler = importlib.import_module('crawler.ctee_insurance_crawler').CTeeInsuranceCrawler
            logger.info("已載入爬蟲: 工商時報保險版")
        except Exception as e:
            logger.error(f"載入工商時報爬蟲失敗: {e}")
            ctee_crawler = None

        # 初始化爬蟲
        self.crawlers = {
            'mock': mock_generator(),
            'rss': rss_crawler(),
        }
        
        if ctee_crawler:
            self.crawlers['ctee'] = ctee_crawler()
        
        try:
            # 其他可能的爬蟲
            real_crawler = importlib.import_module('crawler.real_crawler_fixed').RealInsuranceNewsCrawler
            self.crawlers['real'] = real_crawler()
            logger.info("已載入爬蟲: 示範爬蟲")
        except Exception as e:
            logger.warning(f"載入真實爬蟲失敗 (非關鍵錯誤): {e}")
        
        self.is_running = False
        self.last_crawl_time = None
        self.stats = {
            'total_news': 0,
            'successful_crawls': 0,
            'failed_crawls': 0
        }
        
        # 爬蟲控制設置
        self.auto_crawl_enabled = True  # 是否啟用自動爬蟲
        self.scheduler_thread = None  # 定時爬蟲線程
        self.should_stop = False  # 停止信號
    
    def run_crawlers(self, source_name=None, limit=10):
        """
        運行爬蟲的兼容方法
        
        Args:
            source_name: 新聞來源名稱
            limit: 抓取數量限制
            
        Returns:
            結果字典
        """
        logger.info(f"運行爬蟲: {source_name or '全部'}, 限制: {limit}")
        
        if source_name:
            # 運行特定爬蟲
            crawler = self.crawlers.get(source_name)
            if not crawler:
                return {
                    'status': 'error',
                    'message': f'找不到爬蟲: {source_name}',
                    'total': 0,
                    'new': 0
                }
                
            try:
                if hasattr(crawler, 'crawl'):
                    result = crawler.crawl(max_pages=1, max_details=limit)
                    news_items = result.get('news', [])
                else:
                    news_items = crawler.generate_news(count=limit)
                
                return {
                    'status': 'success',
                    'message': '爬蟲執行成功',
                    'total': len(news_items),
                    'new': len(news_items),
                    'news': news_items
                }
            except Exception as e:
                logger.error(f"爬蟲執行失敗: {e}")
                return {
                    'status': 'error',
                    'message': f'爬蟲執行失敗: {e}',
                    'total': 0,
                    'new': 0
                }
        else:
            # 運行所有爬蟲
            return self.crawl_all_sources(use_mock=True)
    
    def crawl_all_sources(self, use_mock: bool = True) -> Dict[str, Any]:
        """爬取所有來源的新聞"""
        if self.is_running:
            return {'status': 'error', 'message': '爬蟲已在運行中'}
        
        self.is_running = True
        start_time = datetime.now(timezone.utc)
        all_news = []
        crawl_results = []
        
        try:
            logger.info("🚀 開始執行新聞爬取任務")
            
            if use_mock:
                # 使用模擬數據
                logger.info("📝 使用模擬新聞生成器")
                mock_news = self.crawlers['mock'].generate_news(count=5)
                all_news.extend(mock_news)
                crawl_results.append({
                    'source': '模擬新聞生成器',
                    'success': True,
                    'news_count': len(mock_news),
                    'message': '成功生成模擬新聞'
                })
                self.stats['successful_crawls'] += 1
            
            # 嘗試工商時報爬蟲
            if 'ctee' in self.crawlers:
                logger.info("🔍 嘗試工商時報保險版爬蟲")
                try:
                    ctee_crawler = self.crawlers['ctee']
                    result = ctee_crawler.crawl(max_pages=1, max_details=10)
                    ctee_news = result.get('news', [])
                    all_news.extend(ctee_news)
                    crawl_results.append({
                        'source': '工商時報保險版',
                        'success': True,
                        'news_count': len(ctee_news),
                        'message': f'成功爬取工商時報新聞 {len(ctee_news)} 則'
                    })
                    self.stats['successful_crawls'] += 1
                except Exception as e:
                    logger.error(f"工商時報爬蟲失敗: {e}")
                    crawl_results.append({
                        'source': '工商時報保險版', 
                        'success': False,
                        'news_count': 0,
                        'message': f'爬取失敗: {str(e)}'
                    })
                    self.stats['failed_crawls'] += 1
            
            # 嘗試其他爬蟲
            if 'real' in self.crawlers:
                # 使用真實爬蟲
                logger.info("🔍 嘗試真實新聞爬蟲")
                try:
                    real_news = self.crawlers['real'].crawl_all_sources()
                    all_news.extend(real_news)
                    crawl_results.append({
                        'source': '真實新聞爬蟲',
                        'success': True,
                        'news_count': len(real_news),
                        'message': f'成功爬取真實新聞 {len(real_news)} 則'
                    })
                    self.stats['successful_crawls'] += 1
                except Exception as e:
                    logger.error(f"真實爬蟲失敗: {e}")
                    crawl_results.append({
                        'source': '真實爬蟲', 
                        'success': False,
                        'news_count': 0,
                        'message': f'爬取失敗: {str(e)}'
                    })
                    self.stats['failed_crawls'] += 1
            
            # 備用RSS爬蟲 (實驗性)
            logger.info("🔍 嘗試RSS爬蟲 (備用)")
            try:
                rss_news = self.crawlers['rss'].crawl_all_feeds()
                all_news.extend(rss_news)
                crawl_results.append({
                    'source': 'RSS爬蟲',
                    'success': True,
                    'news_count': len(rss_news),
                    'message': '成功爬取RSS新聞'
                })
                self.stats['successful_crawls'] += 1
            except Exception as e:
                logger.error(f"RSS爬蟲失敗: {e}")
                crawl_results.append({
                    'source': 'RSS爬蟲', 
                    'success': False,
                    'news_count': 0,
                    'message': f'爬取失敗: {str(e)}'
                })
                self.stats['failed_crawls'] += 1
            
            # 儲存新聞到資料庫
            if all_news:
                # 應用日期過濾
                filtered_news = self.date_filter.filter_news_list(all_news)
                if filtered_news:
                    saved_count = self._save_news_to_database(filtered_news)
                    self.stats['total_news'] += saved_count
                    logger.info(f"💾 成功儲存 {saved_count} 則新聞到資料庫")
                else:
                    logger.info("⚠️ 經過日期過濾後沒有新聞需要儲存")
            
            self.last_crawl_time = start_time
            
            return {
                'status': 'success',
                'message': f'爬取完成，共處理 {len(all_news)} 則新聞，過濾後保存 {len(filtered_news) if "filtered_news" in locals() else 0} 則',
                'start_time': start_time.isoformat(),
                'duration': (datetime.now(timezone.utc) - start_time).total_seconds(),
                'results': crawl_results,
                'stats': self.stats,
                'filter_status': self.date_filter.get_status(),
                'total': len(all_news),
                'new': len(filtered_news) if "filtered_news" in locals() else 0
            }
            
        except Exception as e:
            logger.error(f"❌ 爬取任務執行失敗: {e}")
            return {
                'status': 'error',
                'message': f'爬取失敗: {str(e)}',
                'results': crawl_results,
                'total': 0,
                'new': 0
            }
        finally:
            self.is_running = False
    
    def _save_news_to_database(self, news_list: List[Dict[str, Any]]) -> int:
        """將新聞儲存到資料庫"""
        try:
            # 動態導入避免循環導入
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            from app import create_app
            from config.settings import Config
            from database.models import db, News, NewsCategory, NewsSource
            
            app = create_app(Config)
            saved_count = 0
            
            with app.app_context():
                for news_data in news_list:
                    try:
                        # 開始新的事務處理每條新聞
                        with db.session.begin():
                            # 檢查重複 - 使用URL檢查(更可靠)
                            url = news_data.get('url', '')
                            if url:
                                # 使用 no_autoflush 避免在查詢時觸發 flush
                                with db.session.no_autoflush:
                                    existing = News.query.filter_by(url=url).first()
                                    if existing:
                                        logger.info(f"新聞已存在，跳過: {news_data.get('title', 'No title')}")
                                        continue
                            
                            # 如果沒有URL，則檢查標題
                            if not url:
                                with db.session.no_autoflush:
                                    existing = News.query.filter_by(title=news_data['title']).first()
                                    if existing:
                                        logger.info(f"相同標題新聞已存在，跳過: {news_data['title']}")
                                        continue
                            
                            # 處理分類
                            category_name = news_data.get('category', '其他')
                            with db.session.no_autoflush:
                                category = NewsCategory.query.filter_by(name=category_name).first()
                            if not category:
                                category = NewsCategory(
                                    name=category_name,
                                    description=f"{category_name}相關新聞"
                                )
                                db.session.add(category)
                                db.session.flush()
                            
                            # 處理來源
                            source_name = news_data.get('source', '未知來源')
                            with db.session.no_autoflush:
                                source = NewsSource.query.filter_by(name=source_name).first()
                            if not source:
                                source = NewsSource(
                                    name=source_name,
                                    url='',
                                    description=f"{source_name}新聞來源"
                                )
                                db.session.add(source)
                                db.session.flush()
                            
                            # 創建新聞
                            news = News(
                                title=news_data['title'],
                                content=news_data.get('content', ''),
                                summary=news_data.get('summary', ''),
                                url=news_data.get('url', ''),
                                source_id=source.id,
                                category_id=category.id,
                                published_date=news_data.get('published_date', datetime.now(timezone.utc)),
                                crawled_date=datetime.now(timezone.utc),
                                keywords=news_data.get('keywords', ''),
                                importance_score=news_data.get('importance_score', 0.5),
                                sentiment_score=news_data.get('sentiment_score', 0.0),
                                status='active'
                            )
                            
                            db.session.add(news)
                            # 事務會在 with 塊結束時自動提交
                            saved_count += 1
                            
                    except Exception as e:
                        logger.error(f"儲存單則新聞失敗: {e}")
                        # 事務會自動回滾
                        continue
                
                return saved_count
                
        except Exception as e:
            logger.error(f"資料庫操作失敗: {e}")
            return 0
    
    def get_crawler_status(self) -> Dict[str, Any]:
        """獲取爬蟲狀態"""
        return {
            'is_running': self.is_running,
            'auto_crawl_enabled': self.auto_crawl_enabled,
            'scheduler_running': self.scheduler_thread is not None and self.scheduler_thread.is_alive(),
            'last_crawl_time': self.last_crawl_time.isoformat() if self.last_crawl_time else None,
            'stats': self.stats,
            'available_crawlers': list(self.crawlers.keys()),
            'date_filter': self.date_filter.get_status()
        }
    
    def update_date_filter_settings(self, max_age_days: int = None, enable_filter: bool = None) -> Dict[str, Any]:
        """
        更新日期過濾器設定
        
        Args:
            max_age_days: 最大天數
            enable_filter: 是否啟用過濾
            
        Returns:
            Dict: 更新後的狀態
        """
        self.date_filter.update_settings(max_age_days=max_age_days, enable_filter=enable_filter)
        
        status_msg = []
        if max_age_days is not None:
            status_msg.append(f"最大天數設為 {max_age_days} 天")
        if enable_filter is not None:
            status_msg.append(f"過濾功能{'啟用' if enable_filter else '停用'}")
        
        logger.info(f"日期過濾器設定已更新: {', '.join(status_msg)}")
        
        return {
            'status': 'success',
            'message': f"日期過濾器設定已更新: {', '.join(status_msg)}",
            'filter_status': self.date_filter.get_status()
        }
    
    def start_scheduled_crawling(self, interval_minutes: int = 60):
        """開始定期爬取 (背景執行)"""
        # 如果已經有爬蟲線程在運行，則不重複啟動
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            logger.info("定期爬蟲已在運行中，不重複啟動")
            return False
            
        # 重置停止信號
        self.should_stop = False
        self.auto_crawl_enabled = True
        
        def run_scheduler():
            while not self.should_stop:
                try:
                    if self.auto_crawl_enabled:
                        logger.info(f"⏰ 定期爬取任務開始 (間隔: {interval_minutes}分鐘)")
                        result = self.crawl_all_sources(use_mock=True)
                        logger.info(f"⏰ 定期爬取完成: {result['message']}")
                    
                    # 等待下次執行，每5秒檢查一次是否應該停止
                    for _ in range(int(interval_minutes * 60 / 5)):
                        if self.should_stop:
                            break
                        time.sleep(5)
                        
                except Exception as e:
                    logger.error(f"定期爬取任務失敗: {e}")
                    # 失敗後等待1分鐘再試，但同時檢查是否應該停止
                    for _ in range(12):  # 1分鐘，每5秒檢查一次
                        if self.should_stop:
                            break
                        time.sleep(5)
            
            logger.info("定期爬蟲已停止")
        
        # 在背景執行緒中執行
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info(f"📅 定期爬取已啟動 (間隔: {interval_minutes}分鐘)")
        return True
        
    def stop_scheduled_crawling(self):
        """停止定期爬取"""
        if not self.scheduler_thread or not self.scheduler_thread.is_alive():
            logger.info("定期爬蟲未在運行中")
            return False
            
        logger.info("正在停止定期爬蟲...")
        self.should_stop = True
        return True
        
    def toggle_auto_crawl(self, enabled=None):
        """切換自動爬蟲功能
        
        Args:
            enabled: 是否啟用，如果不提供則切換當前狀態
        """
        if enabled is None:
            self.auto_crawl_enabled = not self.auto_crawl_enabled
        else:
            self.auto_crawl_enabled = enabled
            
        status = "啟用" if self.auto_crawl_enabled else "禁用"
        logger.info(f"自動爬蟲功能已{status}")
        return self.auto_crawl_enabled
        
    def run_all_crawlers(self, use_real=True) -> Dict[str, Any]:
        """
        運行所有可用爬蟲，優先使用真實爬蟲
        
        Args:
            use_real: 是否使用真實爬蟲（而非僅模擬數據）
            
        Returns:
            Dict 包含爬取結果
        """
        logger.info(f"📡 運行所有爬蟲 (使用真實爬蟲: {use_real})")
        
        if self.is_running:
            logger.warning("⚠️ 爬蟲已在運行中，忽略此次請求")
            return {
                'status': 'error',
                'message': '爬蟲已在運行中，請稍後再試',
                'total': 0,
                'new': 0
            }
        
        self.is_running = True
        try:
            # 使用輔助模組執行爬蟲
            result = CrawlerHelper.run_all_crawlers(self, use_real=use_real)
            
            # 處理結果
            all_news = result.get('news', [])
            
            # 將新聞保存到資料庫
            if all_news:
                # 應用日期過濾
                filtered_news = self.date_filter.filter_news_list(all_news)
                if filtered_news:
                    saved_count = self._save_news_to_database(filtered_news)
                    self.stats['total_news'] += saved_count
                    logger.info(f"💾 成功儲存 {saved_count} 則新聞到資料庫")
                else:
                    logger.info("⚠️ 經過日期過濾後沒有新聞需要儲存")
            
            # 更新爬取時間
            self.last_crawl_time = datetime.now(timezone.utc)
            
            # 整合返回結果
            return {
                'status': 'success',
                'message': f'爬取完成，共處理 {len(all_news)} 則新聞，過濾後保存 {len(filtered_news) if "filtered_news" in locals() else 0} 則',
                'start_time': self.last_crawl_time.isoformat(),
                'duration': result.get('elapsed_time', 0),
                'results': result.get('results', []),
                'stats': self.stats,
                'filter_status': self.date_filter.get_status(),
                'total': len(all_news),
                'new': len(filtered_news) if "filtered_news" in locals() else 0
            }
        
        except Exception as e:
            logger.error(f"❌ 爬取任務執行失敗: {e}")
            return {
                'status': 'error',
                'message': f'爬取失敗: {str(e)}',
                'total': 0,
                'new': 0
            }
        finally:
            self.is_running = False


# 創建全局爬蟲管理器實例
_crawler_manager = None

def get_crawler_manager() -> CrawlerManager:
    """
    獲取爬蟲管理器實例
    
    Returns:
        爬蟲管理器實例
    """
    global _crawler_manager
    if _crawler_manager is None:
        _crawler_manager = CrawlerManager()
    return _crawler_manager


def test_crawler_manager():
    """測試爬蟲管理器"""
    logging.basicConfig(level=logging.INFO)
    manager = get_crawler_manager()
    
    print("🧪 測試爬蟲管理器...")
    
    # 測試爬取
    result = manager.crawl_all_sources(use_mock=True)
    print(f"✅ 爬取結果: {result['message']}")
    print(f"📊 統計: {result['stats']}")
    
    # 測試狀態查詢
    status = manager.get_crawler_status()
    print(f"📋 爬蟲狀態: {status}")

if __name__ == "__main__":
    test_crawler_manager()
