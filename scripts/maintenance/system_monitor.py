"""
整合系統監控與反饋收集服務

此腳本用於整合錯誤監控和用戶反饋收集功能到保險新聞聚合系統中
"""

import os
import sys
import logging
import argparse
import threading
import time
from pathlib import Path

# 設置基本路徑
BASE_DIR = Path(__file__).resolve().parent

# 添加路徑到系統路徑
sys.path.insert(0, str(BASE_DIR))

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'logs', 'system_monitor.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('system.monitor')

# 導入所需模組
try:
    from src.maintenance.error_monitor import ErrorMonitor, ErrorFixer
    from src.services.user_feedback import FeedbackManager
    logger.info("成功導入錯誤監控和用戶反饋模組")
except ImportError as e:
    logger.error(f"導入模組失敗: {e}")
    sys.exit(1)

class SystemMonitor:
    """系統監控與反饋整合類"""
    
    def __init__(self):
        """初始化系統監控器"""
        self.error_monitor = None
        self.error_fixer = None
        self.feedback_manager = None
        self.is_running = False
        self.check_thread = None
    
    def start(self):
        """啟動系統監控"""
        logger.info("啟動系統監控服務")
        
        # 初始化錯誤監控器
        self.error_monitor = ErrorMonitor()
        self.error_monitor.start_monitoring(interval=120)  # 每2分鐘檢查一次錯誤日誌
        
        # 初始化錯誤修復器
        self.error_fixer = ErrorFixer()
        
        # 初始化反饋管理器
        self.feedback_manager = FeedbackManager()
        
        # 啟動系統檢查線程
        self.is_running = True
        self.check_thread = threading.Thread(target=self._system_check_loop, daemon=True)
        self.check_thread.start()
        
        logger.info("所有監控服務已啟動")
    
    def stop(self):
        """停止系統監控"""
        logger.info("停止系統監控服務")
        
        # 停止錯誤監控
        if self.error_monitor:
            self.error_monitor.stop_monitoring()
        
        # 停止系統檢查線程
        self.is_running = False
        if self.check_thread:
            self.check_thread.join(timeout=5)
        
        logger.info("所有監控服務已停止")
    
    def _system_check_loop(self):
        """系統定期檢查循環"""
        check_interval = 3600  # 每小時檢查一次系統狀態
        
        while self.is_running:
            try:
                # 執行系統健康檢查
                self._perform_health_check()
                
                # 生成系統報告
                if self.error_monitor:
                    self.error_monitor.generate_error_report()
                
                # 生成反饋圖表
                if self.feedback_manager:
                    self.feedback_manager.generate_feedback_charts()
                
                # 等待下一次檢查
                for _ in range(check_interval):
                    if not self.is_running:
                        break
                    time.sleep(1)
                
            except Exception as e:
                logger.error(f"系統檢查循環出錯: {e}")
                time.sleep(60)  # 錯誤後等待1分鐘再重試
    
    def _perform_health_check(self):
        """執行系統健康檢查"""
        logger.info("執行系統健康檢查")
        
        # 檢查數據庫連接
        db_status = self._check_database()
        
        # 檢查爬蟲狀態
        crawler_status = self._check_crawler()
        
        # 檢查API服務
        api_status = self._check_api()
        
        # 檢查前端服務
        web_status = self._check_web()
        
        # 檢查磁碟空間
        disk_status = self._check_disk_space()
        
        # 整合狀態報告
        status_report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'database': db_status,
            'crawler': crawler_status,
            'api': api_status,
            'web': web_status,
            'disk': disk_status,
            'overall': 'healthy' if all(s == 'healthy' for s in 
                                       [db_status, crawler_status, api_status, web_status, disk_status]) 
                                else 'warning'
        }
        
        # 記錄狀態報告
        logger.info(f"系統健康狀態: {status_report['overall']}")
        logger.debug(f"詳細狀態報告: {status_report}")
        
        # 如果系統不健康，嘗試自動修復
        if status_report['overall'] != 'healthy':
            self._attempt_auto_repair(status_report)
    
    def _check_database(self):
        """檢查數據庫連接狀態"""
        try:
            # 嘗試執行簡單的數據庫查詢
            import sqlite3
            db_path = os.path.join(BASE_DIR, 'instance', 'insurance_news.db')
            
            if not os.path.exists(db_path):
                logger.warning(f"數據庫文件不存在: {db_path}")
                return 'error'
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT sqlite_version();")
            cursor.fetchone()
            conn.close()
            
            return 'healthy'
        except Exception as e:
            logger.error(f"數據庫檢查失敗: {e}")
            return 'error'
    
    def _check_crawler(self):
        """檢查爬蟲狀態"""
        try:
            # 檢查爬蟲日誌是否正常更新
            crawler_log_path = os.path.join(BASE_DIR, 'logs', 'crawler.log')
            
            if not os.path.exists(crawler_log_path):
                logger.warning(f"爬蟲日誌文件不存在: {crawler_log_path}")
                return 'warning'
            
            # 檢查日誌是否在最近24小時內更新
            log_mtime = os.path.getmtime(crawler_log_path)
            if time.time() - log_mtime > 86400:  # 24小時 = 86400秒
                logger.warning("爬蟲日誌超過24小時未更新")
                return 'warning'
            
            return 'healthy'
        except Exception as e:
            logger.error(f"爬蟲檢查失敗: {e}")
            return 'warning'
    
    def _check_api(self):
        """檢查API服務狀態"""
        try:
            # 嘗試請求API狀態端點
            import requests
            response = requests.get('http://localhost:5000/api/status', timeout=5)
            
            if response.status_code == 200:
                return 'healthy'
            else:
                logger.warning(f"API狀態檢查返回非正常狀態碼: {response.status_code}")
                return 'warning'
        except Exception as e:
            logger.error(f"API檢查失敗: {e}")
            return 'warning'
    
    def _check_web(self):
        """檢查前端Web服務狀態"""
        try:
            # 嘗試請求首頁
            import requests
            response = requests.get('http://localhost:5000/', timeout=5)
            
            if response.status_code == 200:
                return 'healthy'
            else:
                logger.warning(f"Web狀態檢查返回非正常狀態碼: {response.status_code}")
                return 'warning'
        except Exception as e:
            logger.error(f"Web檢查失敗: {e}")
            return 'warning'
    
    def _check_disk_space(self):
        """檢查磁碟空間"""
        try:
            # 獲取目前磁碟使用情況
            import shutil
            total, used, free = shutil.disk_usage(BASE_DIR)
            
            # 計算使用比例
            usage_percent = (used / total) * 100
            
            # 如果使用超過90%，發出警告
            if usage_percent > 90:
                logger.warning(f"磁碟空間使用率高: {usage_percent:.1f}%")
                return 'warning'
            
            return 'healthy'
        except Exception as e:
            logger.error(f"磁碟空間檢查失敗: {e}")
            return 'warning'
    
    def _attempt_auto_repair(self, status_report):
        """嘗試自動修復系統問題
        
        Args:
            status_report: 系統狀態報告
        """
        logger.info("嘗試自動修復系統問題")
        
        # 檢查並修復數據庫問題
        if status_report['database'] != 'healthy' and self.error_fixer:
            self.error_fixer.attempt_repair('DatabaseError', {'db_path': os.path.join(BASE_DIR, 'instance', 'insurance_news.db')})
        
        # 清理緩存和釋放內存
        if status_report['crawler'] != 'healthy' or status_report['api'] != 'healthy' or status_report['web'] != 'healthy':
            if self.error_fixer:
                self.error_fixer._clean_memory_cache()
        
        # 處理磁碟空間不足
        if status_report['disk'] != 'healthy':
            self._clean_temp_files()
    
    def _clean_temp_files(self):
        """清理臨時文件以釋放磁碟空間"""
        try:
            # 清理日誌目錄中的舊文件
            logs_dir = os.path.join(BASE_DIR, 'logs')
            self._clean_old_files(logs_dir, days=7)
            
            # 清理緩存目錄
            cache_dir = os.path.join(BASE_DIR, 'cache')
            self._clean_old_files(cache_dir, days=3)
            
            logger.info("已清理臨時文件")
        except Exception as e:
            logger.error(f"清理臨時文件失敗: {e}")
    
    def _clean_old_files(self, directory, days=7):
        """清理指定目錄中的舊文件
        
        Args:
            directory: 要清理的目錄
            days: 超過多少天的文件將被清理
        """
        import os
        from datetime import datetime, timedelta
        
        if not os.path.exists(directory):
            return
        
        # 計算截止日期
        cutoff = datetime.now() - timedelta(days=days)
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                
                # 獲取文件修改時間
                try:
                    mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    # 如果文件超過指定天數，刪除它
                    if mtime < cutoff:
                        os.remove(file_path)
                        logger.debug(f"已刪除舊文件: {file_path}")
                except Exception as e:
                    logger.error(f"處理文件 {file_path} 時出錯: {e}")

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='保險新聞聚合器系統監控服務')
    parser.add_argument('--action', choices=['start', 'stop', 'restart'], default='start',
                       help='控制監控服務的動作 (start, stop, restart)')
    
    args = parser.parse_args()
    
    # 處理服務動作
    if args.action == 'start':
        logger.info("啟動系統監控服務")
        monitor = SystemMonitor()
        monitor.start()
        
        try:
            # 保持程序運行
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("接收到停止信號")
            monitor.stop()
    
    elif args.action == 'stop':
        logger.info("停止系統監控服務")
        # 實際停止邏輯需要外部進程管理實現
        print("系統監控服務已停止")
    
    elif args.action == 'restart':
        logger.info("重啟系統監控服務")
        # 實際重啟邏輯需要外部進程管理實現
        monitor = SystemMonitor()
        monitor.start()
        
        try:
            # 保持程序運行
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("接收到停止信號")
            monitor.stop()

if __name__ == "__main__":
    main()
