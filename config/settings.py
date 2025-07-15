"""
應用配置設定
Application Configuration Settings
"""
import os
from datetime import timedelta
from typing import Dict, Any

# 從 .env 文件載入環境變數
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # 如果沒有 python-dotenv，忽略
    pass

class BaseConfig:
    """基礎配置類"""
    
    # 應用基本設定
    APP_NAME = "台灣保險新聞聚合器"
    VERSION = "2.0.0"
    DESCRIPTION = "自動收集、分析並呈現台灣保險業相關新聞的智能聚合平台"
    
    # 服務器配置
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = False
    TESTING = False
    
    # 安全配置
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)    # 資料庫配置
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_PATH = os.path.join(BASE_DIR, 'instance', 'insurance_news.db')
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # API 配置
    API_PREFIX = "/api/v1"
    API_TITLE = "保險新聞聚合器 API"
    API_VERSION = "1.0.0"
    
    # 爬蟲配置
    CRAWLER_INTERVAL = int(os.getenv("CRAWLER_INTERVAL", 3600))  # 1小時
    CRAWLER_TIMEOUT = int(os.getenv("CRAWLER_TIMEOUT", 30))  # 30秒
    CRAWLER_DELAY = float(os.getenv("CRAWLER_DELAY", 2.0))  # 2秒延遲
    MAX_CONCURRENT_CRAWLERS = int(os.getenv("MAX_CONCURRENT_CRAWLERS", 5))
    
    # 分析配置
    ANALYSIS_KEYWORDS = [
        "保險", "理賠", "保費", "保單", "投保", "承保",
        "壽險", "產險", "車險", "健康險", "意外險", "醫療險",
        "金管會", "保險局", "保險公司", "保險業", "保險市場"
    ]
    
    # 分頁配置
    POSTS_PER_PAGE = int(os.getenv("POSTS_PER_PAGE", 20))
    MAX_POSTS_PER_PAGE = 100
    
    # 日誌配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_FILE_BACKUP_COUNT = 5
    
    @staticmethod
    def init_app(app):
        """初始化應用特定配置"""
        pass

class DevelopmentConfig(BaseConfig):
    """開發環境配置"""
    DEBUG = True
    # 繼承BaseConfig的資料庫設置，不再覆蓋
    
    # 開發環境特定的爬蟲配置
    CRAWLER_INTERVAL = 300  # 5分鐘，更頻繁的測試
    CRAWLER_DELAY = 1.0  # 更短的延遲
    
    @classmethod
    def init_app(cls, app):
        print("🔧 開發模式已啟用")

class TestingConfig(BaseConfig):
    """測試環境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    
    @classmethod
    def init_app(cls, app):
        print("🧪 測試模式已啟用")

class ProductionConfig(BaseConfig):
    """生產環境配置"""
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    
    # 生產環境安全設置
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    @classmethod
    def init_app(cls, app):
        print("🚀 生產模式已啟用")

# 配置映射
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# 便利的配置獲取函數
def get_config(config_name=None):
    """獲取配置對象"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    return config.get(config_name, config['default'])

# 當前配置（用於運行時訪問）
Config = get_config()
