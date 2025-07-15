"""
監控服務模組
Monitoring Service Module

負責監控系統狀態、效能和健康度
"""

import psutil
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import threading
import json
import os

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """系統指標數據類"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    active_processes: int
    network_connections: int

@dataclass
class ApplicationMetrics:
    """應用指標數據類"""
    timestamp: datetime
    total_requests: int
    error_count: int
    response_time_avg: float
    active_users: int
    database_connections: int

class MonitoringService:
    """監控服務類"""
    
    def __init__(self, check_interval: int = 60):
        """
        初始化監控服務
        
        Args:
            check_interval: 檢查間隔（秒）
        """
        self.check_interval = check_interval
        self.is_running = False
        self.monitoring_thread = None
        self.system_metrics_history = []
        self.app_metrics_history = []
        self.alerts = []
        self.max_history_size = 1440  # 24小時的分鐘數
        
        # 警報閾值
        self.cpu_threshold = 80.0
        self.memory_threshold = 85.0
        self.disk_threshold = 90.0
        self.error_rate_threshold = 0.05  # 5%
        
    def start_monitoring(self):
        """開始監控"""
        if not self.is_running:
            self.is_running = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            logger.info("Monitoring service started")
    
    def stop_monitoring(self):
        """停止監控"""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        logger.info("Monitoring service stopped")
    
    def _monitoring_loop(self):
        """監控循環"""
        while self.is_running:
            try:
                # 收集系統指標
                system_metrics = self._collect_system_metrics()
                self._store_system_metrics(system_metrics)
                
                # 收集應用指標
                app_metrics = self._collect_app_metrics()
                self._store_app_metrics(app_metrics)
                
                # 檢查警報條件
                self._check_alerts(system_metrics, app_metrics)
                
                # 清理舊數據
                self._cleanup_old_metrics()
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
            
            time.sleep(self.check_interval)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """
        收集系統指標
        
        Returns:
            系統指標對象
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            process_count = len(psutil.pids())
            
            # 網路連接數
            try:
                connections = len(psutil.net_connections())
            except psutil.AccessDenied:
                connections = 0
            
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage=disk.percent,
                active_processes=process_count,
                network_connections=connections
            )
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_usage=0.0,
                active_processes=0,
                network_connections=0
            )
    
    def _collect_app_metrics(self) -> ApplicationMetrics:
        """
        收集應用指標
        
        Returns:
            應用指標對象
        """
        # 這裡需要與應用的統計系統整合
        # 目前返回模擬數據
        return ApplicationMetrics(
            timestamp=datetime.utcnow(),
            total_requests=0,
            error_count=0,
            response_time_avg=0.0,
            active_users=0,
            database_connections=0
        )
    
    def _store_system_metrics(self, metrics: SystemMetrics):
        """
        儲存系統指標
        
        Args:
            metrics: 系統指標對象
        """
        self.system_metrics_history.append(metrics)
        
        # 限制歷史數據大小
        if len(self.system_metrics_history) > self.max_history_size:
            self.system_metrics_history.pop(0)
    
    def _store_app_metrics(self, metrics: ApplicationMetrics):
        """
        儲存應用指標
        
        Args:
            metrics: 應用指標對象
        """
        self.app_metrics_history.append(metrics)
        
        # 限制歷史數據大小
        if len(self.app_metrics_history) > self.max_history_size:
            self.app_metrics_history.pop(0)
    
    def _check_alerts(self, system_metrics: SystemMetrics, app_metrics: ApplicationMetrics):
        """
        檢查警報條件
        
        Args:
            system_metrics: 系統指標
            app_metrics: 應用指標
        """
        alerts = []
        
        # 檢查 CPU 使用率
        if system_metrics.cpu_percent > self.cpu_threshold:
            alerts.append({
                'type': 'HIGH_CPU',
                'level': 'WARNING',
                'message': f'High CPU usage: {system_metrics.cpu_percent:.1f}%',
                'timestamp': datetime.utcnow(),
                'value': system_metrics.cpu_percent
            })
        
        # 檢查記憶體使用率
        if system_metrics.memory_percent > self.memory_threshold:
            alerts.append({
                'type': 'HIGH_MEMORY',
                'level': 'WARNING',
                'message': f'High memory usage: {system_metrics.memory_percent:.1f}%',
                'timestamp': datetime.utcnow(),
                'value': system_metrics.memory_percent
            })
        
        # 檢查磁碟使用率
        if system_metrics.disk_usage > self.disk_threshold:
            alerts.append({
                'type': 'HIGH_DISK',
                'level': 'CRITICAL',
                'message': f'High disk usage: {system_metrics.disk_usage:.1f}%',
                'timestamp': datetime.utcnow(),
                'value': system_metrics.disk_usage
            })
        
        # 儲存新警報
        for alert in alerts:
            self.alerts.append(alert)
            logger.warning(f"Alert: {alert['message']}")
    
    def _cleanup_old_metrics(self):
        """清理舊的指標數據"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        # 清理系統指標
        self.system_metrics_history = [
            m for m in self.system_metrics_history 
            if m.timestamp > cutoff_time
        ]
        
        # 清理應用指標
        self.app_metrics_history = [
            m for m in self.app_metrics_history 
            if m.timestamp > cutoff_time
        ]
        
        # 清理警報（保留最近1小時）
        alert_cutoff = datetime.utcnow() - timedelta(hours=1)
        self.alerts = [
            a for a in self.alerts 
            if a['timestamp'] > alert_cutoff
        ]
    
    def get_current_status(self) -> Dict:
        """
        獲取當前系統狀態
        
        Returns:
            系統狀態字典
        """
        if not self.system_metrics_history:
            return {'status': 'No data available'}
        
        latest_system = self.system_metrics_history[-1]
        latest_app = self.app_metrics_history[-1] if self.app_metrics_history else None
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'system': {
                'cpu_percent': latest_system.cpu_percent,
                'memory_percent': latest_system.memory_percent,
                'disk_usage': latest_system.disk_usage,
                'active_processes': latest_system.active_processes,
                'network_connections': latest_system.network_connections
            },
            'application': {
                'total_requests': latest_app.total_requests if latest_app else 0,
                'error_count': latest_app.error_count if latest_app else 0,
                'response_time_avg': latest_app.response_time_avg if latest_app else 0.0,
                'active_users': latest_app.active_users if latest_app else 0,
                'database_connections': latest_app.database_connections if latest_app else 0
            },
            'alerts': len([a for a in self.alerts if a['timestamp'] > datetime.utcnow() - timedelta(minutes=5)]),
            'health_status': self._get_health_status()
        }
    
    def _get_health_status(self) -> str:
        """
        獲取健康狀態
        
        Returns:
            健康狀態字符串
        """
        if not self.system_metrics_history:
            return 'UNKNOWN'
        
        latest = self.system_metrics_history[-1]
        
        # 檢查是否有嚴重警報
        recent_critical_alerts = [
            a for a in self.alerts 
            if a['level'] == 'CRITICAL' and 
            a['timestamp'] > datetime.utcnow() - timedelta(minutes=5)
        ]
        
        if recent_critical_alerts:
            return 'CRITICAL'
        
        # 檢查系統指標
        if (latest.cpu_percent > self.cpu_threshold or 
            latest.memory_percent > self.memory_threshold):
            return 'WARNING'
        
        return 'HEALTHY'
    
    def get_metrics_history(self, hours: int = 1) -> Dict:
        """
        獲取指標歷史
        
        Args:
            hours: 時間範圍（小時）
            
        Returns:
            歷史指標字典
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        system_history = [
            {
                'timestamp': m.timestamp.isoformat(),
                'cpu_percent': m.cpu_percent,
                'memory_percent': m.memory_percent,
                'disk_usage': m.disk_usage
            }
            for m in self.system_metrics_history 
            if m.timestamp > cutoff_time
        ]
        
        return {
            'period_hours': hours,
            'system_metrics': system_history,
            'data_points': len(system_history)
        }

# 全域監控服務實例
monitoring_service = MonitoringService()
