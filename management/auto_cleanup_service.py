#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自動新聞清理服務
Auto News Cleanup Service

定期清理超過指定天數的新聞，保持系統效能和資料整潔
"""

import os
import sys
import time
import schedule
import sqlite3
from datetime import datetime, timedelta, timezone
import logging

# 設置日誌
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
log_file = os.path.join(project_root, 'logs', 'news_cleanup.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class NewsCleanupService:
    """新聞清理服務"""
    
    def __init__(self, max_age_days=7):
        self.max_age_days = max_age_days
        self.db_path = self._find_database()
        
    def _find_database(self):
        """尋找資料庫檔案"""
        # 取得管理腳本所在目錄的上一層目錄（專案根目錄）
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        possible_paths = [
            os.path.join(project_root, "instance", "insurance_news.db"),
            os.path.join(project_root, "instance", "dev_insurance_news.db")
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        raise FileNotFoundError(f"找不到資料庫檔案，搜尋路徑: {possible_paths}")
    
    def cleanup_old_news(self):
        """清理舊新聞"""
        try:
            logger.info(f"開始清理超過 {self.max_age_days} 天的舊新聞...")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 計算截止日期
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=self.max_age_days)).isoformat()
            
            # 查找要刪除的新聞
            cursor.execute("""
                SELECT COUNT(*) 
                FROM news 
                WHERE (published_date < ? OR crawled_date < ?)
                AND status = 'active'
            """, (cutoff_date, cutoff_date))
            
            old_count = cursor.fetchone()[0]
            
            if old_count == 0:
                logger.info("沒有找到需要清理的舊新聞")
                return True
            
            # 執行軟刪除
            cursor.execute("""
                UPDATE news 
                SET status = 'deleted', updated_at = ?
                WHERE (published_date < ? OR crawled_date < ?)
                AND status = 'active'
            """, (datetime.now(timezone.utc).isoformat(), cutoff_date, cutoff_date))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            # 獲取統計資訊
            cursor.execute("SELECT COUNT(*) FROM news WHERE status = 'active'")
            active_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM news WHERE status = 'deleted'")
            deleted_total = cursor.fetchone()[0]
            
            conn.close()
            
            logger.info(f"✅ 成功清理 {deleted_count} 條舊新聞")
            logger.info(f"📊 當前統計 - 活躍: {active_count}, 已刪除: {deleted_total}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 清理失敗: {e}")
            return False
    
    def cleanup_by_count(self, max_count=200):
        """按數量限制清理新聞"""
        try:
            logger.info(f"開始按數量清理，保留最新 {max_count} 條新聞...")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 獲取當前活躍新聞總數
            cursor.execute("SELECT COUNT(*) FROM news WHERE status = 'active'")
            current_count = cursor.fetchone()[0]
            
            if current_count <= max_count:
                logger.info(f"當前新聞數量 ({current_count}) 未超過限制 ({max_count})")
                return True
            
            # 找到要保留的新聞ID
            cursor.execute("""
                SELECT id FROM news 
                WHERE status = 'active'
                ORDER BY published_date DESC, crawled_date DESC
                LIMIT ?
            """, (max_count,))
            
            keep_ids = [str(row[0]) for row in cursor.fetchall()]
            
            # 刪除不在保留列表中的新聞
            placeholders = ','.join(['?'] * len(keep_ids))
            cursor.execute(f"""
                UPDATE news 
                SET status = 'deleted', updated_at = ?
                WHERE status = 'active' AND id NOT IN ({placeholders})
            """, [datetime.now(timezone.utc).isoformat()] + keep_ids)
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"✅ 按數量清理完成，刪除了 {deleted_count} 條舊新聞")
            return True
            
        except Exception as e:
            logger.error(f"❌ 按數量清理失敗: {e}")
            return False
    
    def get_status(self):
        """獲取清理服務狀態"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 統計資訊
            cursor.execute("SELECT COUNT(*) FROM news WHERE status = 'active'")
            active_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM news WHERE status = 'deleted'")
            deleted_count = cursor.fetchone()[0]
            
            # 最舊的活躍新聞
            cursor.execute("""
                SELECT published_date FROM news 
                WHERE status = 'active' AND published_date IS NOT NULL
                ORDER BY published_date ASC LIMIT 1
            """)
            oldest_result = cursor.fetchone()
            oldest_date = oldest_result[0] if oldest_result else None
            
            # 最新的活躍新聞
            cursor.execute("""
                SELECT published_date FROM news 
                WHERE status = 'active' AND published_date IS NOT NULL
                ORDER BY published_date DESC LIMIT 1
            """)
            newest_result = cursor.fetchone()
            newest_date = newest_result[0] if newest_result else None
            
            conn.close()
            
            return {
                'active_news': active_count,
                'deleted_news': deleted_count,
                'oldest_news_date': oldest_date,
                'newest_news_date': newest_date,
                'max_age_days': self.max_age_days,
                'database_path': self.db_path
            }
            
        except Exception as e:
            logger.error(f"獲取狀態失敗: {e}")
            return None

def run_scheduled_cleanup():
    """執行排程清理"""
    logger.info("🧹 執行排程新聞清理...")
    
    service = NewsCleanupService(max_age_days=7)
    
    # 先按日期清理
    if service.cleanup_old_news():
        # 再按數量限制清理（避免資料庫過大）
        service.cleanup_by_count(max_count=500)
    
    logger.info("🎉 排程清理完成")

def start_scheduler():
    """啟動排程器"""
    logger.info("🚀 啟動新聞清理排程服務...")
    logger.info("📅 排程設定:")
    logger.info("  - 每日 02:00 自動清理舊新聞")
    logger.info("  - 每 6 小時檢查一次數量限制")
    
    # 設定排程
    schedule.every().day.at("02:00").do(run_scheduled_cleanup)
    schedule.every(6).hours.do(lambda: NewsCleanupService().cleanup_by_count(500))
    
    # 立即執行一次清理
    run_scheduled_cleanup()
    
    # 持續運行排程
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分鐘檢查一次
    except KeyboardInterrupt:
        logger.info("🛑 排程服務已停止")

def main():
    """主程式"""
    import argparse
    
    parser = argparse.ArgumentParser(description='新聞清理服務')
    parser.add_argument('--run-once', action='store_true', help='只執行一次清理，不啟動排程')
    parser.add_argument('--status', action='store_true', help='顯示清理服務狀態')
    parser.add_argument('--days', type=int, default=7, help='保留新聞的天數')
    
    args = parser.parse_args()
    
    if args.status:
        # 顯示狀態
        service = NewsCleanupService(args.days)
        status = service.get_status()
        
        if status:
            print("📊 新聞清理服務狀態:")
            print("=" * 40)
            print(f"活躍新聞: {status['active_news']}")
            print(f"已刪除新聞: {status['deleted_news']}")
            print(f"保留天數: {status['max_age_days']}")
            print(f"最舊新聞: {status['oldest_news_date']}")
            print(f"最新新聞: {status['newest_news_date']}")
            print(f"資料庫: {status['database_path']}")
        else:
            print("❌ 無法獲取狀態資訊")
            
    elif args.run_once:
        # 執行一次清理
        service = NewsCleanupService(args.days)
        service.cleanup_old_news()
        service.cleanup_by_count(500)
        
    else:
        # 啟動排程服務
        start_scheduler()

if __name__ == "__main__":
    main()
