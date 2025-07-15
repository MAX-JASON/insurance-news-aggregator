"""
錯誤監控和修復服務
Error Monitoring and Fixing Service

用於監控系統錯誤並提供自動修復功能
"""

import os
import sys
import json
import time
import logging
import traceback
import threading
import datetime
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any, Optional, Union, Set

# 設置基本路徑
BASE_DIR = Path(__file__).resolve().parent.parent

# 添加路徑到系統路徑
sys.path.insert(0, str(BASE_DIR))

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'logs', 'error_monitor.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('error.monitor')

class ErrorMonitor:
    """錯誤監控類，負責收集、分析和報告系統錯誤"""
    
    def __init__(self, config=None):
        """初始化錯誤監控器
        
        Args:
            config: 監控配置
        """
        self.config = config or {}
        self.error_log_path = os.path.join(BASE_DIR.parent, 'logs', 'error.log')
        self.report_dir = os.path.join(BASE_DIR.parent, 'logs', 'reports')
        os.makedirs(self.report_dir, exist_ok=True)
        
        # 記錄已知錯誤類型
        self.known_errors = self._load_known_errors()
        
        # 錯誤統計數據
        self.error_stats = defaultdict(int)
        self.error_details = defaultdict(list)
        self.error_timestamps = defaultdict(list)
        
        # 防止重複報警
        self.alerted_errors = set()
        
        # 監控線程
        self.monitor_thread = None
        self.is_running = False
        
        # 最後掃描時間
        self.last_scan_time = time.time()
    
    def _load_known_errors(self) -> Dict[str, Dict]:
        """載入已知錯誤類型
        
        Returns:
            已知錯誤類型字典
        """
        try:
            known_errors_path = os.path.join(BASE_DIR.parent, 'config', 'known_errors.json')
            
            if not os.path.exists(known_errors_path):
                # 創建默認的已知錯誤文件
                default_errors = {
                    "ConnectionError": {
                        "pattern": "ConnectionError",
                        "severity": "medium",
                        "possible_causes": ["網絡連接問題", "目標服務器無響應"],
                        "recommended_actions": ["檢查網絡連接", "確認目標服務可用性"]
                    },
                    "DatabaseError": {
                        "pattern": "DatabaseError|sqlite3.Error|SQLAlchemyError",
                        "severity": "high",
                        "possible_causes": ["資料庫連接問題", "SQL語法錯誤", "資料庫鎖定"],
                        "recommended_actions": ["檢查資料庫連接", "檢查SQL語法", "確認資料庫服務狀態"]
                    },
                    "RateLimitError": {
                        "pattern": "RateLimitExceeded|429 Too Many Requests",
                        "severity": "medium",
                        "possible_causes": ["API請求頻率過高", "達到服務提供商的限制"],
                        "recommended_actions": ["實施請求節流", "增加請求間隔", "考慮升級服務計劃"]
                    },
                    "ParsingError": {
                        "pattern": "ParsingError|ValueError: Invalid JSON|HTMLParseError",
                        "severity": "medium",
                        "possible_causes": ["目標網站結構變更", "返回的數據格式無效"],
                        "recommended_actions": ["更新解析邏輯", "檢查返回數據格式"]
                    },
                    "MemoryError": {
                        "pattern": "MemoryError|MemoryWarning",
                        "severity": "high",
                        "possible_causes": ["內存不足", "內存泄漏"],
                        "recommended_actions": ["優化內存使用", "增加系統內存"]
                    }
                }
                
                # 保存默認錯誤配置
                with open(known_errors_path, 'w', encoding='utf-8') as f:
                    json.dump(default_errors, f, ensure_ascii=False, indent=2)
                
                return default_errors
            else:
                # 載入已有的錯誤配置
                with open(known_errors_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        
        except Exception as e:
            logger.error(f"載入已知錯誤類型失敗: {e}")
            return {}
    
    def start_monitoring(self, interval=60):
        """開始監控錯誤日誌
        
        Args:
            interval: 掃描間隔(秒)
        """
        if self.is_running:
            logger.warning("錯誤監控已經在運行")
            return
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, args=(interval,), daemon=True)
        self.monitor_thread.start()
        logger.info(f"錯誤監控已啟動，掃描間隔: {interval}秒")
    
    def stop_monitoring(self):
        """停止錯誤監控"""
        if not self.is_running:
            logger.warning("錯誤監控未在運行")
            return
        
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("錯誤監控已停止")
    
    def _monitoring_loop(self, interval):
        """監控循環
        
        Args:
            interval: 掃描間隔(秒)
        """
        while self.is_running:
            try:
                # 掃描錯誤日誌
                self.scan_error_logs()
                
                # 分析錯誤模式
                self.analyze_error_patterns()
                
                # 檢測異常峰值
                self.detect_error_spikes()
                
                # 生成定期報告
                if time.time() - self.last_scan_time >= 3600:  # 每小時生成一次報告
                    self.generate_error_report()
                    self.last_scan_time = time.time()
                
                # 等待下一次掃描
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"錯誤監控循環出錯: {e}")
                time.sleep(interval)
    
    def scan_error_logs(self):
        """掃描錯誤日誌文件"""
        if not os.path.exists(self.error_log_path):
            logger.warning(f"錯誤日誌文件不存在: {self.error_log_path}")
            return
        
        try:
            with open(self.error_log_path, 'r', encoding='utf-8', errors='ignore') as f:
                # 移動到文件末尾
                f.seek(0, 2)
                file_size = f.tell()
                
                # 只讀取最後的10MB數據
                read_size = min(10 * 1024 * 1024, file_size)
                f.seek(max(0, file_size - read_size), 0)
                
                # 讀取並解析日誌
                log_content = f.read()
                self._parse_error_logs(log_content)
            
            logger.info("成功掃描錯誤日誌")
        
        except Exception as e:
            logger.error(f"掃描錯誤日誌失敗: {e}")
    
    def _parse_error_logs(self, log_content):
        """解析錯誤日誌內容
        
        Args:
            log_content: 日誌內容
        """
        import re
        
        # 時間戳模式
        timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}'
        
        # 錯誤級別模式
        error_level_pattern = r'ERROR|CRITICAL|FATAL'
        
        # 日誌條目模式
        log_entry_pattern = f"({timestamp_pattern}).*?({error_level_pattern}).*?(\n.*?)(?=(?:{timestamp_pattern})|$)"
        
        # 查找所有錯誤日誌條目
        entries = re.findall(log_entry_pattern, log_content, re.DOTALL)
        
        for timestamp_str, level, message in entries:
            # 解析時間戳
            try:
                timestamp = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
            except ValueError:
                timestamp = datetime.datetime.now()
            
            # 分類錯誤類型
            error_type = self._classify_error(message)
            
            if error_type:
                # 更新統計數據
                self.error_stats[error_type] += 1
                
                # 儲存錯誤詳情(最多保留100條相同錯誤)
                if len(self.error_details[error_type]) < 100:
                    self.error_details[error_type].append(message.strip())
                
                # 儲存錯誤時間戳
                self.error_timestamps[error_type].append(timestamp)
    
    def _classify_error(self, message):
        """分類錯誤類型
        
        Args:
            message: 錯誤消息
            
        Returns:
            錯誤類型
        """
        import re
        
        # 檢查是否匹配已知錯誤類型
        for error_name, error_info in self.known_errors.items():
            if re.search(error_info['pattern'], message, re.IGNORECASE):
                return error_name
        
        # 嘗試從回溯中提取錯誤類型
        exception_match = re.search(r'(?:Exception|Error): (.*?)(?:\n|$)', message)
        if exception_match:
            return exception_match.group(1).strip()
        
        # 如果無法確定具體類型，返回通用錯誤
        return "UnknownError"
    
    def analyze_error_patterns(self):
        """分析錯誤模式和趨勢"""
        now = datetime.datetime.now()
        
        # 分析每種錯誤類型的時間分佈
        for error_type, timestamps in self.error_timestamps.items():
            # 跳過數量太少的錯誤
            if len(timestamps) < 5:
                continue
            
            # 計算最近一小時的錯誤數
            recent_count = sum(1 for ts in timestamps if (now - ts).total_seconds() <= 3600)
            
            # 如果最近一小時的錯誤超過閾值，生成警報
            if recent_count >= 10 and error_type not in self.alerted_errors:
                self._generate_alert(error_type, recent_count)
                self.alerted_errors.add(error_type)
            
            # 24小時後重置警報狀態
            self.alerted_errors = {e for e in self.alerted_errors 
                                  if any((now - ts).total_seconds() <= 86400 
                                        for ts in self.error_timestamps.get(e, []))}
    
    def detect_error_spikes(self):
        """檢測錯誤峰值"""
        now = datetime.datetime.now()
        
        for error_type, timestamps in self.error_timestamps.items():
            if len(timestamps) < 10:
                continue
            
            # 計算最近10分鐘的錯誤數
            recent_count = sum(1 for ts in timestamps if (now - ts).total_seconds() <= 600)
            
            # 計算之前1小時的平均10分鐘錯誤數
            hour_ago = now - datetime.timedelta(hours=1)
            prev_periods = [sum(1 for ts in timestamps 
                              if hour_ago + datetime.timedelta(minutes=i*10) <= ts < hour_ago + datetime.timedelta(minutes=(i+1)*10))
                           for i in range(6)]
            
            if prev_periods:
                avg_count = sum(prev_periods) / len(prev_periods)
                
                # 如果最近10分鐘的錯誤數是平均值的3倍以上，生成警報
                if recent_count >= 5 and recent_count >= avg_count * 3:
                    self._generate_alert(error_type, recent_count, is_spike=True)
    
    def _generate_alert(self, error_type, count, is_spike=False):
        """生成錯誤警報
        
        Args:
            error_type: 錯誤類型
            count: 錯誤數量
            is_spike: 是否為突發錯誤
        """
        alert_type = "突發錯誤峰值" if is_spike else "頻繁錯誤"
        
        message = f"{alert_type}警報: 檢測到 {count} 個 '{error_type}' 錯誤"
        
        # 添加已知錯誤的詳細信息
        if error_type in self.known_errors:
            error_info = self.known_errors[error_type]
            severity = error_info.get('severity', 'medium')
            causes = error_info.get('possible_causes', [])
            actions = error_info.get('recommended_actions', [])
            
            message += f"\n嚴重性: {severity.upper()}"
            
            if causes:
                message += "\n可能原因:"
                for cause in causes:
                    message += f"\n - {cause}"
            
            if actions:
                message += "\n建議操作:"
                for action in actions:
                    message += f"\n - {action}"
        
        # 添加最新的錯誤示例
        if error_type in self.error_details and self.error_details[error_type]:
            message += "\n\n最新錯誤示例:\n"
            message += self.error_details[error_type][0]
        
        logger.warning(message)
        
        # TODO: 發送通知到外部系統(如郵件、Slack等)
        self._send_notification(error_type, message)
    
    def _send_notification(self, error_type, message):
        """發送錯誤通知
        
        Args:
            error_type: 錯誤類型
            message: 通知消息
        """
        # 將通知保存到文件
        try:
            alert_path = os.path.join(self.report_dir, 'alerts.log')
            with open(alert_path, 'a', encoding='utf-8') as f:
                f.write(f"\n{'=' * 80}\n")
                f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {error_type}\n")
                f.write(f"{message}\n")
            
            logger.info(f"已保存 {error_type} 的錯誤警報")
        except Exception as e:
            logger.error(f"保存錯誤警報失敗: {e}")
    
    def generate_error_report(self):
        """生成錯誤報告"""
        try:
            report = {
                'timestamp': datetime.datetime.now().isoformat(),
                'summary': {
                    'total_errors': sum(self.error_stats.values()),
                    'unique_errors': len(self.error_stats),
                    'top_errors': dict(sorted(self.error_stats.items(), key=lambda x: x[1], reverse=True)[:5])
                },
                'errors': {}
            }
            
            # 生成每種錯誤類型的詳細報告
            for error_type, count in self.error_stats.items():
                # 獲取最早和最晚的錯誤時間
                timestamps = self.error_timestamps.get(error_type, [])
                first_seen = min(timestamps).isoformat() if timestamps else None
                last_seen = max(timestamps).isoformat() if timestamps else None
                
                # 獲取最近的錯誤示例
                examples = self.error_details.get(error_type, [])[:3]
                
                # 添加到報告
                report['errors'][error_type] = {
                    'count': count,
                    'first_seen': first_seen,
                    'last_seen': last_seen,
                    'known_error': error_type in self.known_errors,
                    'examples': examples
                }
                
                # 如果是已知錯誤，添加額外信息
                if error_type in self.known_errors:
                    report['errors'][error_type]['info'] = self.known_errors[error_type]
            
            # 保存報告
            report_path = os.path.join(self.report_dir, f'error_report_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"錯誤報告已保存至: {report_path}")
            return report
        
        except Exception as e:
            logger.error(f"生成錯誤報告失敗: {e}")
            return None

class ErrorFixer:
    """錯誤修復類，提供自動和半自動錯誤修復功能"""
    
    def __init__(self):
        """初始化錯誤修復器"""
        self.repair_strategies = self._load_repair_strategies()
    
    def _load_repair_strategies(self) -> Dict[str, Dict]:
        """載入錯誤修復策略
        
        Returns:
            修復策略字典
        """
        try:
            strategies_path = os.path.join(BASE_DIR.parent, 'config', 'repair_strategies.json')
            
            if not os.path.exists(strategies_path):
                # 創建默認的修復策略文件
                default_strategies = {
                    "ConnectionError": {
                        "auto_fixable": True,
                        "max_retries": 3,
                        "retry_delay": 5,
                        "actions": [
                            "retry_connection",
                            "check_network_status"
                        ]
                    },
                    "DatabaseError": {
                        "auto_fixable": False,
                        "severity": "high",
                        "actions": [
                            "backup_database",
                            "check_database_integrity"
                        ]
                    },
                    "RateLimitError": {
                        "auto_fixable": True,
                        "actions": [
                            "pause_requests",
                            "implement_backoff_strategy"
                        ],
                        "backoff_time": 60
                    },
                    "ParsingError": {
                        "auto_fixable": False,
                        "actions": [
                            "log_html_content",
                            "alert_developer"
                        ]
                    },
                    "MemoryError": {
                        "auto_fixable": True,
                        "actions": [
                            "clean_memory_cache",
                            "reduce_batch_size"
                        ]
                    }
                }
                
                # 保存默認修復策略
                with open(strategies_path, 'w', encoding='utf-8') as f:
                    json.dump(default_strategies, f, ensure_ascii=False, indent=2)
                
                return default_strategies
            else:
                # 載入已有的修復策略
                with open(strategies_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        
        except Exception as e:
            logger.error(f"載入錯誤修復策略失敗: {e}")
            return {}
    
    def attempt_repair(self, error_type, error_context=None):
        """嘗試修復錯誤
        
        Args:
            error_type: 錯誤類型
            error_context: 錯誤上下文
            
        Returns:
            是否成功修復
        """
        if error_type not in self.repair_strategies:
            logger.warning(f"沒有找到錯誤類型 '{error_type}' 的修復策略")
            return False
        
        strategy = self.repair_strategies[error_type]
        
        # 檢查是否可以自動修復
        if not strategy.get('auto_fixable', False):
            logger.info(f"錯誤類型 '{error_type}' 不支持自動修復")
            return False
        
        # 執行修復操作
        actions = strategy.get('actions', [])
        
        success = True
        for action in actions:
            try:
                action_success = self._execute_repair_action(action, error_type, error_context, strategy)
                success = success and action_success
            except Exception as e:
                logger.error(f"執行修復操作 '{action}' 失敗: {e}")
                success = False
        
        return success
    
    def _execute_repair_action(self, action, error_type, error_context, strategy):
        """執行修復操作
        
        Args:
            action: 修復操作名稱
            error_type: 錯誤類型
            error_context: 錯誤上下文
            strategy: 修復策略
            
        Returns:
            是否成功執行
        """
        logger.info(f"執行修復操作: {action} 用於錯誤類型 {error_type}")
        
        # 根據操作類型執行不同的修復邏輯
        if action == 'retry_connection':
            return self._retry_connection(error_context, strategy.get('max_retries', 3), strategy.get('retry_delay', 5))
        
        elif action == 'check_network_status':
            return self._check_network_status()
        
        elif action == 'backup_database':
            return self._backup_database(error_context)
        
        elif action == 'check_database_integrity':
            return self._check_database_integrity(error_context)
        
        elif action == 'pause_requests':
            return self._pause_requests(strategy.get('backoff_time', 60))
        
        elif action == 'implement_backoff_strategy':
            return self._implement_backoff_strategy(error_context, strategy.get('backoff_time', 60))
        
        elif action == 'log_html_content':
            return self._log_html_content(error_context)
        
        elif action == 'alert_developer':
            return self._alert_developer(error_type, error_context)
        
        elif action == 'clean_memory_cache':
            return self._clean_memory_cache()
        
        elif action == 'reduce_batch_size':
            return self._reduce_batch_size(error_context)
        
        else:
            logger.warning(f"未知的修復操作: {action}")
            return False
    
    def _retry_connection(self, error_context, max_retries=3, retry_delay=5):
        """重試連接
        
        Args:
            error_context: 錯誤上下文
            max_retries: 最大重試次數
            retry_delay: 重試延遲(秒)
            
        Returns:
            是否成功重連
        """
        if not error_context or 'url' not in error_context:
            logger.warning("重試連接缺少URL信息")
            return False
        
        import requests
        url = error_context['url']
        
        for attempt in range(max_retries):
            try:
                logger.info(f"嘗試重連 {url}，第 {attempt + 1} 次嘗試")
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    logger.info(f"成功重連 {url}")
                    return True
                else:
                    logger.warning(f"重連 {url} 返回狀態碼 {response.status_code}")
            
            except Exception as e:
                logger.error(f"重連 {url} 失敗: {e}")
            
            # 等待一段時間再重試
            time.sleep(retry_delay)
        
        logger.error(f"重連 {url} 失敗，已超過最大重試次數 {max_retries}")
        return False
    
    def _check_network_status(self):
        """檢查網絡狀態
        
        Returns:
            網絡是否正常
        """
        import socket
        
        # 檢查DNS解析
        try:
            socket.gethostbyname('www.google.com')
            logger.info("DNS解析正常")
        except socket.gaierror:
            logger.error("DNS解析失敗")
            return False
        
        # 檢查常用站點連接
        sites = ['https://www.google.com', 'https://www.baidu.com', 'https://www.microsoft.com']
        import requests
        
        success_count = 0
        for site in sites:
            try:
                response = requests.get(site, timeout=5)
                if response.status_code == 200:
                    success_count += 1
            except Exception:
                pass
        
        network_ok = success_count > 0
        
        if network_ok:
            logger.info(f"網絡連接正常 ({success_count}/{len(sites)} 個站點可訪問)")
        else:
            logger.error("網絡連接失敗，所有測試站點均不可訪問")
        
        return network_ok
    
    def _backup_database(self, error_context):
        """備份數據庫
        
        Args:
            error_context: 錯誤上下文
            
        Returns:
            是否成功備份
        """
        try:
            from shutil import copyfile
            import datetime
            
            # 確定數據庫文件路徑
            db_path = error_context.get('db_path') if error_context else None
            
            if not db_path:
                # 使用默認路徑
                db_path = os.path.join(BASE_DIR.parent, 'instance', 'insurance_news.db')
            
            if not os.path.exists(db_path):
                logger.error(f"數據庫文件不存在: {db_path}")
                return False
            
            # 創建備份目錄
            backup_dir = os.path.join(BASE_DIR.parent, 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            # 創建備份文件
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f'db_backup_{timestamp}.db')
            
            # 複製數據庫文件
            copyfile(db_path, backup_path)
            
            logger.info(f"數據庫已成功備份至: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"備份數據庫失敗: {e}")
            return False
    
    def _check_database_integrity(self, error_context):
        """檢查數據庫完整性
        
        Args:
            error_context: 錯誤上下文
            
        Returns:
            數據庫是否完整
        """
        try:
            import sqlite3
            
            # 確定數據庫文件路徑
            db_path = error_context.get('db_path') if error_context else None
            
            if not db_path:
                # 使用默認路徑
                db_path = os.path.join(BASE_DIR.parent, 'instance', 'insurance_news.db')
            
            if not os.path.exists(db_path):
                logger.error(f"數據庫文件不存在: {db_path}")
                return False
            
            # 連接數據庫
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 檢查完整性
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            
            conn.close()
            
            if result == 'ok':
                logger.info("數據庫完整性檢查通過")
                return True
            else:
                logger.error(f"數據庫完整性檢查失敗: {result}")
                return False
                
        except Exception as e:
            logger.error(f"檢查數據庫完整性失敗: {e}")
            return False
    
    def _pause_requests(self, pause_time=60):
        """暫停請求
        
        Args:
            pause_time: 暫停時間(秒)
            
        Returns:
            是否成功暫停
        """
        logger.info(f"暫停請求 {pause_time} 秒")
        
        # 寫入暫停標記文件
        try:
            pause_path = os.path.join(BASE_DIR.parent, 'cache', 'pause_requests')
            os.makedirs(os.path.dirname(pause_path), exist_ok=True)
            
            with open(pause_path, 'w') as f:
                f.write(str(int(time.time() + pause_time)))
            
            logger.info(f"已設置請求暫停，持續 {pause_time} 秒")
            return True
            
        except Exception as e:
            logger.error(f"設置請求暫停失敗: {e}")
            return False
    
    def _implement_backoff_strategy(self, error_context, backoff_time=60):
        """實施退避策略
        
        Args:
            error_context: 錯誤上下文
            backoff_time: 退避時間(秒)
            
        Returns:
            是否成功實施退避策略
        """
        logger.info(f"為請求實施退避策略，退避時間: {backoff_time}秒")
        
        try:
            # 保存退避配置
            backoff_path = os.path.join(BASE_DIR.parent, 'cache', 'backoff_config.json')
            os.makedirs(os.path.dirname(backoff_path), exist_ok=True)
            
            backoff_config = {
                'backoff_time': backoff_time,
                'start_time': time.time(),
                'domain': error_context.get('domain') if error_context else 'all'
            }
            
            with open(backoff_path, 'w', encoding='utf-8') as f:
                json.dump(backoff_config, f)
            
            logger.info(f"已設置退避策略: {backoff_config}")
            return True
            
        except Exception as e:
            logger.error(f"設置退避策略失敗: {e}")
            return False
    
    def _log_html_content(self, error_context):
        """記錄HTML內容，用於調試解析錯誤
        
        Args:
            error_context: 錯誤上下文
            
        Returns:
            是否成功記錄
        """
        if not error_context or 'html' not in error_context:
            logger.warning("記錄HTML內容缺少HTML數據")
            return False
        
        try:
            # 創建日誌目錄
            html_log_dir = os.path.join(BASE_DIR.parent, 'logs', 'html_logs')
            os.makedirs(html_log_dir, exist_ok=True)
            
            # 生成日誌文件名
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            source = error_context.get('source', 'unknown')
            html_log_path = os.path.join(html_log_dir, f'parsing_error_{source}_{timestamp}.html')
            
            # 保存HTML內容
            with open(html_log_path, 'w', encoding='utf-8') as f:
                f.write(error_context['html'])
            
            logger.info(f"已記錄HTML內容至: {html_log_path}")
            return True
            
        except Exception as e:
            logger.error(f"記錄HTML內容失敗: {e}")
            return False
    
    def _alert_developer(self, error_type, error_context):
        """通知開發者
        
        Args:
            error_type: 錯誤類型
            error_context: 錯誤上下文
            
        Returns:
            是否成功發送通知
        """
        try:
            # 創建警報日誌
            alert_path = os.path.join(BASE_DIR.parent, 'logs', 'dev_alerts.log')
            
            # 準備警報消息
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message = f"[{timestamp}] 開發者警報: {error_type}\n"
            
            # 添加錯誤上下文
            if error_context:
                message += "錯誤上下文:\n"
                for key, value in error_context.items():
                    if key == 'html' and isinstance(value, str) and len(value) > 500:
                        value = value[:500] + "... [截斷]"
                    message += f"  {key}: {value}\n"
            
            # 保存警報消息
            with open(alert_path, 'a', encoding='utf-8') as f:
                f.write(f"{message}\n{'=' * 80}\n")
            
            logger.info(f"已發送開發者警報: {error_type}")
            return True
            
        except Exception as e:
            logger.error(f"發送開發者警報失敗: {e}")
            return False
    
    def _clean_memory_cache(self):
        """清理內存緩存
        
        Returns:
            是否成功清理
        """
        try:
            # 檢查和清理各模塊的緩存
            modules_to_clean = ['analyzer.cache', 'crawler.engine']
            
            for module_name in modules_to_clean:
                try:
                    # 動態導入模塊
                    module = __import__(module_name, fromlist=['*'])
                    
                    # 嘗試清理緩存
                    if hasattr(module, 'clear_cache'):
                        module.clear_cache()
                        logger.info(f"已清理模塊 {module_name} 的緩存")
                    else:
                        logger.info(f"模塊 {module_name} 沒有緩存清理功能")
                
                except ImportError:
                    logger.warning(f"無法導入模塊 {module_name}")
                except Exception as e:
                    logger.error(f"清理模塊 {module_name} 的緩存時出錯: {e}")
            
            # 強制進行垃圾回收
            import gc
            collected = gc.collect()
            logger.info(f"執行垃圾回收，釋放了 {collected} 個對象")
            
            return True
            
        except Exception as e:
            logger.error(f"清理內存緩存失敗: {e}")
            return False
    
    def _reduce_batch_size(self, error_context):
        """減小批處理大小
        
        Args:
            error_context: 錯誤上下文
            
        Returns:
            是否成功調整批大小
        """
        try:
            # 獲取當前的批大小設置
            config_path = os.path.join(BASE_DIR.parent, 'config', 'config.yaml')
            
            if not os.path.exists(config_path):
                logger.error(f"配置文件不存在: {config_path}")
                return False
            
            # 讀取配置
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 檢查批處理大小設置
            if 'crawler' in config and 'batch_size' in config['crawler']:
                current_batch_size = config['crawler']['batch_size']
                new_batch_size = max(1, int(current_batch_size * 0.5))  # 減半
                
                # 如果批大小已經很小，則不再減小
                if new_batch_size == current_batch_size:
                    logger.info(f"批處理大小已經最小 ({new_batch_size})，不再減小")
                    return True
                
                # 更新配置
                config['crawler']['batch_size'] = new_batch_size
                
                # 保存配置
                with open(config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f)
                
                logger.info(f"已將批處理大小從 {current_batch_size} 減小到 {new_batch_size}")
                return True
            else:
                logger.warning("配置中未找到批處理大小設置")
                return False
                
        except Exception as e:
            logger.error(f"減小批處理大小失敗: {e}")
            return False

# 初始化錯誤監控和修復
def init_error_monitor():
    """初始化錯誤監控"""
    monitor = ErrorMonitor()
    monitor.start_monitoring()
    return monitor

# 主函數
def main():
    """主函數"""
    logger.info("啟動錯誤監控和修復服務")
    
    # 初始化錯誤監控
    monitor = init_error_monitor()
    
    try:
        # 保持程序運行
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("接收到停止信號，正在停止錯誤監控")
        monitor.stop_monitoring()
    
    logger.info("錯誤監控和修復服務已停止")

if __name__ == "__main__":
    main()
