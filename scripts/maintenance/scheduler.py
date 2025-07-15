"""
自動化爬蟲排程系統
Automated Crawler Scheduler

定期執行新聞爬取任務，確保新聞資料的時效性
"""

import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import schedule

from crawler.manager import CrawlerManager
from database.models import News, NewsSource, db
from app import create_app
from config.settings import Config

logger = logging.getLogger('scheduler')

class CrawlerScheduler:
    """爬蟲排程管理器"""
    
    def __init__(self, app=None):
        """
        初始化排程器
        
        Args:
            app: Flask應用實例
        """
        self.app = app or create_app(Config)
        self.crawler_manager = CrawlerManager()
        self.is_running = False
        self.scheduler_thread = None
        self.last_run_results = {}
        
        # 設定排程配置
        self.schedule_config = {
            'real_news_interval': 30,  # 真實新聞爬取間隔（分鐘）
            'mock_news_interval': 60,  # 模擬新聞爬取間隔（分鐘）
            'cleanup_interval': 24,    # 清理過期資料間隔（小時）
            'stats_interval': 6        # 統計更新間隔（小時）
        }
        
        logger.info("🕐 爬蟲排程系統初始化完成")
    
    def setup_schedules(self):
        """設定排程任務"""
        try:
            # 真實新聞爬取 - 每30分鐘
            schedule.every(self.schedule_config['real_news_interval']).minutes.do(
                self._run_real_news_crawl
            )
            
            # 模擬新聞爬取 - 每小時（備用）
            schedule.every(self.schedule_config['mock_news_interval']).minutes.do(
                self._run_mock_news_crawl
            )
            
            # 資料清理 - 每天
            schedule.every(self.schedule_config['cleanup_interval']).hours.do(
                self._run_cleanup_task
            )
            
            # 統計更新 - 每6小時
            schedule.every(self.schedule_config['stats_interval']).hours.do(
                self._update_statistics
            )
            
            logger.info("✅ 排程任務設定完成")
            
        except Exception as e:
            logger.error(f"❌ 排程設定失敗: {e}")
    
    def start(self):
        """啟動排程器"""
        if self.is_running:
            logger.warning("⚠️ 排程器已在運行中")
            return
        
        self.is_running = True
        self.setup_schedules()
        
        # 啟動排程執行緒
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("🚀 爬蟲排程器已啟動")
        
        # 立即執行一次真實新聞爬取
        threading.Thread(target=self._run_real_news_crawl, daemon=True).start()
    
    def stop(self):
        """停止排程器"""
        self.is_running = False
        schedule.clear()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        logger.info("🛑 爬蟲排程器已停止")
    
    def _run_scheduler(self):
        """執行排程循環"""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # 每分鐘檢查一次
            except Exception as e:
                logger.error(f"❌ 排程執行錯誤: {e}")
                time.sleep(60)
    
    def _run_real_news_crawl(self):
        """執行真實新聞爬取任務"""
        try:
            logger.info("📡 開始執行真實新聞爬取任務...")
            
            with self.app.app_context():
                result = self.crawler_manager.crawl_all_sources(use_mock=False)
                
                self.last_run_results['real_news'] = {
                    'timestamp': datetime.now(),
                    'status': result.get('status'),
                    'message': result.get('message'),
                    'news_count': sum(r.get('news_count', 0) for r in result.get('results', [])),
                    'duration': result.get('duration', 0)
                }
                
                if result.get('status') == 'success':
                    logger.info(f"✅ 真實新聞爬取完成: {self.last_run_results['real_news']['news_count']} 則新聞")
                else:
                    logger.warning(f"⚠️ 真實新聞爬取異常: {result.get('message')}")
                    
        except Exception as e:
            logger.error(f"❌ 真實新聞爬取任務失敗: {e}")
            self.last_run_results['real_news'] = {
                'timestamp': datetime.now(),
                'status': 'error',
                'message': str(e),
                'news_count': 0,
                'duration': 0
            }
    
    def _run_mock_news_crawl(self):
        """執行模擬新聞爬取任務（備用）"""
        try:
            # 檢查最近是否有成功的真實新聞爬取
            real_news_result = self.last_run_results.get('real_news')
            if (real_news_result and 
                real_news_result.get('status') == 'success' and
                datetime.now() - real_news_result['timestamp'] < timedelta(hours=2)):
                logger.info("⏭️ 跳過模擬新聞爬取（真實新聞爬取正常）")
                return
            
            logger.info("📝 執行備用模擬新聞爬取任務...")
            
            with self.app.app_context():
                result = self.crawler_manager.crawl_all_sources(use_mock=True)
                
                self.last_run_results['mock_news'] = {
                    'timestamp': datetime.now(),
                    'status': result.get('status'),
                    'message': result.get('message'),
                    'news_count': sum(r.get('news_count', 0) for r in result.get('results', [])),
                    'duration': result.get('duration', 0)
                }
                
                logger.info(f"✅ 備用新聞爬取完成: {self.last_run_results['mock_news']['news_count']} 則新聞")
                    
        except Exception as e:
            logger.error(f"❌ 模擬新聞爬取任務失敗: {e}")
    
    def _run_cleanup_task(self):
        """執行資料清理任務"""
        try:
            logger.info("🧹 開始執行資料清理任務...")
            
            with self.app.app_context():
                # 刪除超過30天的舊新聞（保留重要新聞）
                cutoff_date = datetime.now() - timedelta(days=30)
                old_news = News.query.filter(
                    News.created_at < cutoff_date,
                    News.importance_score < 0.7  # 保留重要新聞
                ).all()
                
                deleted_count = 0
                for news in old_news:
                    db.session.delete(news)
                    deleted_count += 1
                
                if deleted_count > 0:
                    db.session.commit()
                    logger.info(f"✅ 清理完成：刪除 {deleted_count} 則過期新聞")
                else:
                    logger.info("✅ 清理完成：沒有需要刪除的過期新聞")
                
                # 清理分析快取
                from analyzer.cache import get_cache
                cache = get_cache()
                expired_count = cache.clear_expired()
                logger.info(f"✅ 清理過期快取：{expired_count} 個檔案")
                
        except Exception as e:
            logger.error(f"❌ 資料清理任務失敗: {e}")
    
    def _update_statistics(self):
        """更新統計資料"""
        try:
            logger.info("📊 更新統計資料...")
            
            with self.app.app_context():
                # 更新新聞來源統計
                sources = NewsSource.query.all()
                for source in sources:
                    source.total_news_count = News.query.filter_by(source_id=source.id).count()
                
                db.session.commit()
                logger.info("✅ 統計資料更新完成")
                
        except Exception as e:
            logger.error(f"❌ 統計資料更新失敗: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """取得排程器狀態"""
        return {
            'is_running': self.is_running,
            'last_run_results': self.last_run_results,
            'schedule_config': self.schedule_config,
            'next_runs': {
                'real_news': self._get_next_run_time('real_news'),
                'mock_news': self._get_next_run_time('mock_news'),
                'cleanup': self._get_next_run_time('cleanup'),
                'stats': self._get_next_run_time('stats')
            }
        }
    
    def _get_next_run_time(self, task_type: str) -> Optional[str]:
        """取得下次執行時間"""
        try:
            jobs = schedule.get_jobs()
            for job in jobs:
                if task_type in str(job.job_func):
                    return str(job.next_run) if job.next_run else None
            return None
        except:
            return None
    
    def manual_crawl(self, use_real: bool = True) -> Dict[str, Any]:
        """手動觸發爬取任務"""
        try:
            logger.info(f"🔄 手動觸發爬取任務 (真實新聞: {use_real})")
            
            with self.app.app_context():
                result = self.crawler_manager.crawl_all_sources(use_mock=not use_real)
                
                task_type = 'real_news' if use_real else 'mock_news'
                self.last_run_results[task_type] = {
                    'timestamp': datetime.now(),
                    'status': result.get('status'),
                    'message': result.get('message'),
                    'news_count': sum(r.get('news_count', 0) for r in result.get('results', [])),
                    'duration': result.get('duration', 0),
                    'manual': True
                }
                
                return self.last_run_results[task_type]
                
        except Exception as e:
            logger.error(f"❌ 手動爬取失敗: {e}")
            return {
                'timestamp': datetime.now(),
                'status': 'error',
                'message': str(e),
                'news_count': 0,
                'duration': 0,
                'manual': True
            }

# 全域排程器實例
_scheduler_instance = None

def get_scheduler(app=None) -> CrawlerScheduler:
    """取得全域排程器實例"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = CrawlerScheduler(app)
    return _scheduler_instance

def start_scheduler(app=None):
    """啟動排程器"""
    scheduler = get_scheduler(app)
    scheduler.start()
    return scheduler

if __name__ == "__main__":
    # 測試排程器
    print("🧪 測試爬蟲排程系統...")
    
    scheduler = CrawlerScheduler()
    print("✅ 排程器初始化成功")
    
    # 取得狀態
    status = scheduler.get_status()
    print(f"狀態: {status}")
    
    print("✅ 排程系統測試完成")
