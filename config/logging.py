"""
日誌系統配置
Logging System Configuration

統一的日誌管理模組，支持多種日誌輸出格式和級別
"""

import os
import sys
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Optional

class ColoredFormatter(logging.Formatter):
    """彩色日誌格式化器"""
    
    # ANSI 顏色代碼
    COLORS = {
        'DEBUG': '\033[36m',     # 青色
        'INFO': '\033[32m',      # 綠色
        'WARNING': '\033[33m',   # 黃色
        'ERROR': '\033[31m',     # 紅色
        'CRITICAL': '\033[35m',  # 紫色
        'RESET': '\033[0m'       # 重置
    }
    
    def format(self, record):
        # 添加顏色
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}"
                f"{record.levelname}"
                f"{self.COLORS['RESET']}"
            )
        return super().format(record)

class LoggerSetup:
    """日誌設置類"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化應用的日誌系統"""
        self.app = app
        
        # 創建日誌目錄
        log_dir = Path(app.instance_path).parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # 設置根日誌級別
        log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
        
        # 清除現有的處理器
        for handler in app.logger.handlers[:]:
            app.logger.removeHandler(handler)
        
        # 設置應用日誌級別
        app.logger.setLevel(log_level)
        
        # 創建格式化器
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台處理器（開發環境）
        if app.config.get('DEBUG'):
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(ColoredFormatter(
                '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                datefmt='%H:%M:%S'
            ))
            console_handler.setLevel(logging.DEBUG)
            app.logger.addHandler(console_handler)
        
        # 文件處理器（所有環境）
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / 'app.log',
            maxBytes=app.config.get('LOG_FILE_MAX_BYTES', 10*1024*1024),
            backupCount=app.config.get('LOG_FILE_BACKUP_COUNT', 5),
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)
        
        # 錯誤日誌處理器
        error_handler = logging.handlers.RotatingFileHandler(
            log_dir / 'error.log',
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)
        app.logger.addHandler(error_handler)
        
        # 設置其他日誌器
        self._setup_module_loggers(log_dir, formatter, log_level)
        
        # 日誌啟動信息
        app.logger.info(f"🚀 {app.config.get('APP_NAME', 'Application')} 日誌系統已啟動")
        app.logger.info(f"📝 日誌級別: {logging.getLevelName(log_level)}")
        app.logger.info(f"📁 日誌目錄: {log_dir}")
    
    def _setup_module_loggers(self, log_dir: Path, formatter, log_level):
        """設置模組特定的日誌器"""
        
        # 爬蟲日誌
        crawler_logger = logging.getLogger('crawler')
        crawler_handler = logging.handlers.RotatingFileHandler(
            log_dir / 'crawler.log',
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        crawler_handler.setFormatter(formatter)
        crawler_logger.addHandler(crawler_handler)
        crawler_logger.setLevel(log_level)
        
        # 分析日誌
        analyzer_logger = logging.getLogger('analyzer')
        analyzer_handler = logging.handlers.RotatingFileHandler(
            log_dir / 'analyzer.log',
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        analyzer_handler.setFormatter(formatter)
        analyzer_logger.addHandler(analyzer_handler)
        analyzer_logger.setLevel(log_level)
        
        # API 訪問日誌
        api_logger = logging.getLogger('api')
        api_handler = logging.handlers.RotatingFileHandler(
            log_dir / 'api.log',
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        api_handler.setFormatter(formatter)
        api_logger.addHandler(api_handler)
        api_logger.setLevel(log_level)

def get_logger(name: str) -> logging.Logger:
    """獲取指定名稱的日誌器"""
    return logging.getLogger(name)

def log_function_call(func):
    """函數調用日誌裝飾器"""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"📞 呼叫函數: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"✅ 函數 {func.__name__} 執行成功")
            return result
        except Exception as e:
            logger.error(f"❌ 函數 {func.__name__} 執行失敗: {str(e)}")
            raise
    return wrapper

def log_execution_time(func):
    """執行時間日誌裝飾器"""
    import time
    
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"⏱️ {func.__name__} 執行時間: {execution_time:.2f}秒")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"⏱️ {func.__name__} 執行失敗，耗時: {execution_time:.2f}秒，錯誤: {str(e)}")
            raise
    return wrapper

# 全局日誌設置實例
logger_setup = LoggerSetup()
