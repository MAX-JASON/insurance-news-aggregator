"""
自動化新聞排程器
Automated News Scheduler

定期執行RSS新聞聚合，實現自動化新聞收集
"""

import schedule
import time
import logging
import threading
from datetime import datetime
import subprocess
import os
from pathlib import Path

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('news_scheduler')

class NewsScheduler:
    """新聞排程器"""
    
    def __init__(self):
        self.is_running = False
        self.last_run = None
        self.total_runs = 0
        self.successful_runs = 0
        self.failed_runs = 0
        
    def run_rss_aggregator(self):
        """執行RSS新聞聚合器"""
        try:
            logger.info("🚀 開始執行RSS新聞聚合...")
            self.last_run = datetime.now()
            self.total_runs += 1
            
            # 執行RSS聚合器
            result = subprocess.run(
                ['python', 'rss_news_aggregator.py'],
                capture_output=True,
                text=True,
                timeout=300  # 5分鐘超時
            )
            
            if result.returncode == 0:
                self.successful_runs += 1
                logger.info("✅ RSS新聞聚合完成")
                
                # 分析輸出中的新增新聞數量
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if '新增:' in line and '篇' in line:
                        logger.info(f"📰 {line.strip()}")
                        break
            else:
                self.failed_runs += 1
                logger.error(f"❌ RSS新聞聚合失敗: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self.failed_runs += 1
            logger.error("⏰ RSS新聞聚合超時")
        except Exception as e:
            self.failed_runs += 1
            logger.error(f"❌ RSS新聞聚合異常: {e}")
    
    def run_data_cleanup(self):
        """執行資料清理"""
        try:
            logger.info("🧹 開始執行資料清理...")
            
            # 檢查是否有重複新聞並清理
            from direct_db_save import save_news_directly
            import sqlite3
            
            db_path = Path(__file__).parent / "instance" / "insurance_news.db"
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # 查找重複的新聞標題
            cursor.execute("""
                SELECT title, COUNT(*) as count 
                FROM news 
                GROUP BY title 
                HAVING count > 1
            """)
            duplicates = cursor.fetchall()
            
            cleaned_count = 0
            for title, count in duplicates:
                # 保留最新的，刪除舊的
                cursor.execute("""
                    DELETE FROM news 
                    WHERE title = ? AND id NOT IN (
                        SELECT MAX(id) FROM news WHERE title = ?
                    )
                """, (title, title))
                cleaned_count += count - 1
            
            conn.commit()
            conn.close()
            
            if cleaned_count > 0:
                logger.info(f"🧹 清理了 {cleaned_count} 篇重複新聞")
            else:
                logger.info("✨ 沒有發現重複新聞")
                
        except Exception as e:
            logger.error(f"❌ 資料清理失敗: {e}")
    
    def generate_status_report(self):
        """生成狀態報告"""
        try:
            logger.info("📊 生成排程器狀態報告...")
            
            print("\\n" + "="*50)
            print("📊 新聞排程器狀態報告")
            print("="*50)
            print(f"⏰ 報告時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"🔄 運行狀態: {'運行中' if self.is_running else '已停止'}")
            print(f"🕐 最後執行: {self.last_run.strftime('%Y-%m-%d %H:%M:%S') if self.last_run else '未執行'}")
            print(f"📈 總執行次數: {self.total_runs}")
            print(f"✅ 成功次數: {self.successful_runs}")
            print(f"❌ 失敗次數: {self.failed_runs}")
            
            if self.total_runs > 0:
                success_rate = (self.successful_runs / self.total_runs) * 100
                print(f"📊 成功率: {success_rate:.1f}%")
            
            # 檢查資料庫狀態
            db_path = Path(__file__).parent / "instance" / "insurance_news.db"
            if db_path.exists():
                import sqlite3
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM news")
                total_news = cursor.fetchone()[0]
                
                today = datetime.now().date()
                cursor.execute("SELECT COUNT(*) FROM news WHERE date(created_at) = ?", (today,))
                today_news = cursor.fetchone()[0]
                
                print(f"📰 資料庫狀態:")
                print(f"   總新聞: {total_news} 篇")
                print(f"   今日新增: {today_news} 篇")
                
                conn.close()
            
            print("="*50 + "\\n")
            
        except Exception as e:
            logger.error(f"❌ 狀態報告生成失敗: {e}")
    
    def start_scheduler(self):
        """啟動排程器"""
        logger.info("🚀 啟動新聞排程器...")
        self.is_running = True
        
        # 設定排程
        # 每小時執行RSS聚合
        schedule.every().hour.at(":00").do(self.run_rss_aggregator)
        
        # 每天凌晨3點執行資料清理
        schedule.every().day.at("03:00").do(self.run_data_cleanup)
        
        # 每6小時生成狀態報告
        schedule.every(6).hours.do(self.generate_status_report)
        
        # 立即執行一次RSS聚合
        logger.info("🎯 立即執行首次RSS聚合...")
        self.run_rss_aggregator()
        
        logger.info("⏰ 排程已設定:")
        logger.info("   📡 RSS聚合: 每小時執行")
        logger.info("   🧹 資料清理: 每日凌晨3點")
        logger.info("   📊 狀態報告: 每6小時")
        
        # 開始排程循環
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # 每分鐘檢查一次
            except KeyboardInterrupt:
                logger.info("⏹️ 收到停止信號...")
                self.stop_scheduler()
                break
            except Exception as e:
                logger.error(f"❌ 排程器異常: {e}")
                time.sleep(60)
    
    def stop_scheduler(self):
        """停止排程器"""
        logger.info("⏹️ 停止新聞排程器...")
        self.is_running = False
        schedule.clear()
    
    def start_background(self):
        """在背景執行排程器"""
        scheduler_thread = threading.Thread(target=self.start_scheduler, daemon=True)
        scheduler_thread.start()
        logger.info("🔙 排程器已在背景啟動")
        return scheduler_thread

def main():
    """主函數"""
    print("🤖 台灣保險新聞聚合器 - 自動化排程器")
    print("="*50)
    print("功能:")
    print("  📡 每小時自動獲取RSS新聞")
    print("  🧹 每日自動清理重複資料")
    print("  📊 定期生成狀態報告")
    print("="*50)
    
    scheduler = NewsScheduler()
    
    try:
        scheduler.start_scheduler()
    except KeyboardInterrupt:
        print("\\n⏹️ 用戶中斷，正在停止排程器...")
        scheduler.stop_scheduler()
    except Exception as e:
        print(f"\\n❌ 排程器啟動失敗: {e}")

if __name__ == "__main__":
    main()
