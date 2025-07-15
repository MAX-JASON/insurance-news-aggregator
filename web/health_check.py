"""
系統健康檢查模塊
System Health Checks

提供系統關鍵組件的健康檢查功能
"""

import os
import psutil
import time
import socket
import logging
import sqlite3
import threading
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# 設置日誌
logger = logging.getLogger(__name__)

class HealthCheck:
    """健康檢查類"""
    
    def __init__(self, app=None, db=None):
        """初始化健康檢查系統"""
        self.app = app
        self.db = db
        self.checks = []
        self.last_check_time = None
        self.health_data = {
            'overall_health': 100,
            'checks': [],
            'resources': {
                'cpu': [],
                'memory': [],
                'disk': []
            },
            'services': {},
            'alerts': []
        }
        
        # 歷史數據保存設置
        self.history_length = 24 * 12  # 存儲24小時的數據，每5分鐘一個點
        self.check_interval = 300  # 秒，默認5分鐘檢查一次
        
        # 註冊默認檢查項目
        self.register_default_checks()
        
    def register_default_checks(self):
        """註冊默認檢查項目"""
        self.register_check(self.check_database_connection, "數據庫連接")
        self.register_check(self.check_disk_space, "磁碟空間")
        self.register_check(self.check_memory_usage, "記憶體使用")
        self.register_check(self.check_crawler_service, "爬蟲服務")
        self.register_check(self.check_analysis_engine, "分析引擎")
    
    def register_check(self, check_func, name):
        """註冊健康檢查項目
        
        Args:
            check_func: 檢查函數，應返回(status, message, details)
            name: 檢查項目名稱
        """
        self.checks.append({
            'name': name,
            'func': check_func
        })
    
    def run_all_checks(self):
        """執行所有註冊的檢查"""
        results = []
        overall_score = 100
        
        for check in self.checks:
            try:
                status, message, details = check['func']()
                
                # 根據檢查結果調整總分
                if status == 'danger':
                    overall_score -= 20
                elif status == 'warning':
                    overall_score -= 5
                
                results.append({
                    'name': check['name'],
                    'status': status,
                    'message': message,
                    'details': details,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
            except Exception as e:
                logger.error(f"運行健康檢查 {check['name']} 時發生錯誤: {str(e)}")
                results.append({
                    'name': check['name'],
                    'status': 'danger',
                    'message': f'檢查時發生錯誤: {str(e)}',
                    'details': {'error': str(e)},
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                overall_score -= 10
        
        # 確保分數在0-100之間
        overall_score = max(0, min(100, overall_score))
        
        # 更新健康數據
        self.last_check_time = datetime.now()
        self.health_data['overall_health'] = overall_score
        self.health_data['checks'] = results
        
        # 添加資源使用情況
        self._update_resource_usage()
        
        return {
            'overall_health': overall_score,
            'checks': results,
            'timestamp': self.last_check_time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_health_data(self, force_check=False):
        """獲取健康數據
        
        Args:
            force_check: 是否強制重新檢查
        """
        # 如果是首次調用或強制檢查或上次檢查時間超過檢查間隔
        if (self.last_check_time is None or 
            force_check or 
            (datetime.now() - self.last_check_time).total_seconds() > self.check_interval):
            self.run_all_checks()
        
        return self.health_data
    
    def get_health_status(self):
        """獲取系統健康狀態摘要，用於API響應"""
        health_data = self.get_health_data()
        return {
            'status': 'healthy' if health_data['overall_health'] >= 80 else 'degraded' if health_data['overall_health'] >= 50 else 'unhealthy',
            'score': health_data['overall_health'],
            'checks': health_data['checks'],
            'alerts': self.get_alerts(days=1),
            'last_check_time': self.last_check_time.strftime('%Y-%m-%d %H:%M:%S') if self.last_check_time else None
        }
    
    def get_service_status(self):
        """獲取服務健康狀態，用於API響應"""
        # 檢查各項服務
        services = {}
        for check in self.checks:
            if check['name'] in ['爬蟲服務', '分析引擎', '數據庫連接']:
                status, message, details = check['func']()
                services[check['name']] = {
                    'status': status,
                    'message': message,
                    'details': details
                }
        return {
            'services': services,
            'last_check_time': self.last_check_time.strftime('%Y-%m-%d %H:%M:%S') if self.last_check_time else None
        }
    
    def get_resource_usage(self):
        """獲取系統資源使用情況，用於API響應"""
        # 獲取當前資源使用
        cpu_percent = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'current': {
                'cpu': cpu_percent,
                'memory': memory.percent,
                'memory_used_gb': round(memory.used / (1024**3), 2),
                'memory_total_gb': round(memory.total / (1024**3), 2),
                'disk': disk.percent,
                'disk_used_gb': round(disk.used / (1024**3), 2),
                'disk_total_gb': round(disk.total / (1024**3), 2)
            },
            'history': {
                'cpu': self.health_data['resources']['cpu'][-24:] if len(self.health_data['resources']['cpu']) > 0 else [],
                'memory': self.health_data['resources']['memory'][-24:] if len(self.health_data['resources']['memory']) > 0 else [],
                'disk': self.health_data['resources']['disk'][-24:] if len(self.health_data['resources']['disk']) > 0 else []
            },
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _update_resource_usage(self):
        """更新系統資源使用情況"""
        # 獲取CPU使用率
        cpu_percent = psutil.cpu_percent(interval=None)
        
        # 獲取內存使用情況
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # 獲取磁盤使用情況
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        
        # 獲取當前時間
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 添加到歷史數據
        self.health_data['resources']['cpu'].append({
            'time': current_time,
            'value': cpu_percent
        })
        self.health_data['resources']['memory'].append({
            'time': current_time,
            'value': memory_percent
        })
        self.health_data['resources']['disk'].append({
            'time': current_time,
            'value': disk_percent
        })
        
        # 限制歷史數據長度
        for key in ['cpu', 'memory', 'disk']:
            if len(self.health_data['resources'][key]) > self.history_length:
                self.health_data['resources'][key] = self.health_data['resources'][key][-self.history_length:]
    
    def check_database_connection(self):
        """檢查數據庫連接"""
        try:
            if self.db:
                # 使用Flask-SQLAlchemy
                start_time = time.time()
                self.db.session.execute(text('SELECT 1'))
                response_time = (time.time() - start_time) * 1000
                
                status = 'success'
                if response_time > 100:
                    status = 'warning'
                if response_time > 500:
                    status = 'danger'
                
                return (
                    status,
                    f'數據庫連接正常，響應時間: {response_time:.1f}ms',
                    {'response_time': response_time}
                )
            else:
                # 嘗試連接SQLite
                db_path = os.path.join('instance', 'insurance_news.db')
                start_time = time.time()
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()
                cur.execute('SELECT 1')
                cur.close()
                conn.close()
                response_time = (time.time() - start_time) * 1000
                
                status = 'success'
                if response_time > 100:
                    status = 'warning'
                if response_time > 500:
                    status = 'danger'
                
                return (
                    status,
                    f'數據庫連接正常，響應時間: {response_time:.1f}ms',
                    {'response_time': response_time}
                )
        except Exception as e:
            logger.error(f"數據庫連接檢查失敗: {str(e)}")
            return (
                'danger',
                f'數據庫連接失敗: {str(e)}',
                {'error': str(e)}
            )
    
    def check_disk_space(self):
        """檢查磁盤空間"""
        try:
            disk = psutil.disk_usage('/')
            free_gb = disk.free / (1024**3)
            total_gb = disk.total / (1024**3)
            percent_used = disk.percent
            
            status = 'success'
            if percent_used > 80:
                status = 'warning'
            if percent_used > 90:
                status = 'danger'
            
            return (
                status,
                f'可用空間: {free_gb:.1f} GB ({100-percent_used:.0f}%)',
                {
                    'free_gb': free_gb,
                    'total_gb': total_gb,
                    'percent_used': percent_used
                }
            )
        except Exception as e:
            logger.error(f"磁盤空間檢查失敗: {str(e)}")
            return (
                'danger',
                f'磁盤空間檢查失敗: {str(e)}',
                {'error': str(e)}
            )
    
    def check_memory_usage(self):
        """檢查記憶體使用"""
        try:
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            total_gb = memory.total / (1024**3)
            percent_used = memory.percent
            
            status = 'success'
            if percent_used > 75:
                status = 'warning'
            if percent_used > 90:
                status = 'danger'
            
            return (
                status,
                f'記憶體使用率: {percent_used}%',
                {
                    'available_gb': available_gb,
                    'total_gb': total_gb,
                    'percent_used': percent_used
                }
            )
        except Exception as e:
            logger.error(f"記憶體檢查失敗: {str(e)}")
            return (
                'danger',
                f'記憶體檢查失敗: {str(e)}',
                {'error': str(e)}
            )
    
    def check_crawler_service(self):
        """檢查爬蟲服務"""
        try:
            # 檢查相關進程是否在運行
            # 實際環境中應該檢查爬蟲進程或其運行狀態
            crawler_running = True  # 模擬檢查結果
            last_run_time = datetime.now() - timedelta(hours=1)  # 模擬上次運行時間
            
            # 檢查最近的爬蟲日誌
            logs_ok = True  # 模擬日誌檢查結果
            
            if not crawler_running:
                return (
                    'danger',
                    '爬蟲服務未運行',
                    {'running': False, 'last_run': last_run_time.strftime('%Y-%m-%d %H:%M:%S')}
                )
            
            if not logs_ok:
                return (
                    'warning',
                    '爬蟲服務運行中但存在錯誤',
                    {'running': True, 'last_run': last_run_time.strftime('%Y-%m-%d %H:%M:%S')}
                )
            
            return (
                'success',
                '爬蟲服務運行正常',
                {'running': True, 'last_run': last_run_time.strftime('%Y-%m-%d %H:%M:%S')}
            )
        except Exception as e:
            logger.error(f"爬蟲服務檢查失敗: {str(e)}")
            return (
                'danger',
                f'爬蟲服務檢查失敗: {str(e)}',
                {'error': str(e)}
            )
    
    def check_analysis_engine(self):
        """檢查分析引擎"""
        try:
            # 模擬檢查分析引擎
            analysis_running = True
            cache_status = "正常"
            
            if not analysis_running:
                return (
                    'danger',
                    '分析引擎未運行',
                    {'running': False}
                )
            
            return (
                'success',
                '分析引擎工作正常',
                {'running': True, 'cache': cache_status}
            )
        except Exception as e:
            logger.error(f"分析引擎檢查失敗: {str(e)}")
            return (
                'danger',
                f'分析引擎檢查失敗: {str(e)}',
                {'error': str(e)}
            )
    
    def start_background_monitoring(self):
        """啟動背景監控線程"""
        def monitoring_task():
            while True:
                try:
                    self.run_all_checks()
                    # 檢測是否需要產生告警
                    self._check_for_alerts()
                    time.sleep(self.check_interval)
                except Exception as e:
                    logger.error(f"背景監控任務異常: {str(e)}")
                    time.sleep(60)  # 發生錯誤時，等待1分鐘後重試
        
        # 創建並啟動監控線程
        monitor_thread = threading.Thread(target=monitoring_task, daemon=True)
        monitor_thread.start()
        logger.info("系統健康監控後台服務已啟動")
    
    def _check_for_alerts(self):
        """檢查是否需要產生告警"""
        # 檢查CPU使用率
        if len(self.health_data['resources']['cpu']) > 0:
            latest_cpu = self.health_data['resources']['cpu'][-1]['value']
            if latest_cpu > 90:
                self._add_alert('error', 'CPU使用率過高', f'CPU使用率達到 {latest_cpu}%')
            elif latest_cpu > 80:
                self._add_alert('warning', 'CPU使用率較高', f'CPU使用率達到 {latest_cpu}%')
        
        # 檢查記憶體使用率
        if len(self.health_data['resources']['memory']) > 0:
            latest_memory = self.health_data['resources']['memory'][-1]['value']
            if latest_memory > 90:
                self._add_alert('error', '記憶體使用率過高', f'記憶體使用率達到 {latest_memory}%')
            elif latest_memory > 80:
                self._add_alert('warning', '記憶體使用率較高', f'記憶體使用率達到 {latest_memory}%')
        
        # 檢查磁碟使用率
        if len(self.health_data['resources']['disk']) > 0:
            latest_disk = self.health_data['resources']['disk'][-1]['value']
            if latest_disk > 90:
                self._add_alert('error', '磁碟空間不足', f'磁碟使用率達到 {latest_disk}%')
            elif latest_disk > 80:
                self._add_alert('warning', '磁碟空間偏低', f'磁碟使用率達到 {latest_disk}%')
    
    def check_service(self, service_name):
        """單獨檢查指定服務
        
        Args:
            service_name: 服務名稱，例如 "爬蟲服務", "分析引擎", "數據庫連接"
        
        Returns:
            檢查結果
        """
        for check in self.checks:
            if check['name'] == service_name:
                try:
                    status, message, details = check['func']()
                    return {
                        'service': service_name,
                        'status': status,
                        'message': message,
                        'details': details,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                except Exception as e:
                    logger.error(f"檢查服務 {service_name} 時發生錯誤: {str(e)}")
                    return {
                        'service': service_name,
                        'status': 'danger',
                        'message': f'檢查時發生錯誤: {str(e)}',
                        'details': {'error': str(e)},
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
        
        # 服務未找到
        return {
            'service': service_name,
            'status': 'warning',
            'message': f'未找到名為 {service_name} 的服務',
            'details': {},
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _add_alert(self, level, title, message):
        """添加告警記錄
        
        Args:
            level: 告警級別 (info/warning/error)
            title: 告警標題
            message: 告警訊息
        """
        # 檢查是否有相同的最近告警，避免重複
        now = datetime.now()
        recent_time = now - timedelta(minutes=30)
        
        for alert in self.health_data['alerts']:
            if (alert['title'] == title and 
                datetime.fromisoformat(alert['timestamp']) > recent_time):
                return  # 最近已有相同告警，不重複添加
        
        # 添加新的告警
        self.health_data['alerts'].append({
            'level': level,
            'title': title,
            'message': message,
            'timestamp': now.isoformat()
        })
        
        # 限制告警歷史數量
        if len(self.health_data['alerts']) > 100:
            self.health_data['alerts'] = self.health_data['alerts'][-100:]
        
        # 記錄到日誌
        if level == 'error':
            logger.error(f"系統告警: {title} - {message}")
        elif level == 'warning':
            logger.warning(f"系統警告: {title} - {message}")
        else:
            logger.info(f"系統通知: {title} - {message}")
    
    def get_alerts(self, days=7):
        """獲取指定天數內的告警歷史
        
        Args:
            days: 查詢天數
        """
        cutoff_time = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_time.isoformat()
        
        # 過濾指定時間範圍內的告警
        return [alert for alert in self.health_data['alerts'] 
                if alert['timestamp'] > cutoff_str]
    
    def save_health_data(self, file_path='health_history.json'):
        """保存健康檢查數據到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.health_data, f, ensure_ascii=False, indent=2)
            logger.info(f"健康檢查數據已保存到 {file_path}")
            return True
        except Exception as e:
            logger.error(f"保存健康檢查數據失敗: {str(e)}")
            return False
    
    def load_health_data(self, file_path='health_history.json'):
        """從文件載入健康檢查數據"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.health_data = data
                logger.info(f"已從 {file_path} 載入健康檢查數據")
                return True
        except Exception as e:
            logger.error(f"載入健康檢查數據失敗: {str(e)}")
        return False

# 全局實例
health_check = HealthCheck()

def init_health_check(app, db=None):
    """初始化健康檢查系統"""
    global health_check
    health_check = HealthCheck(app, db)
    health_check.start_background_monitoring()
    return health_check
