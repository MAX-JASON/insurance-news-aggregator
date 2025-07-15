"""
Flask 擴展模組
Flask Extensions Module

初始化和配置 Flask 應用的各種擴展
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import os

# 初始化擴展對象
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

def init_extensions(app):
    """
    初始化所有 Flask 擴展
    
    Args:
        app: Flask 應用實例
    """
    # 初始化資料庫
    db.init_app(app)
    
    # 初始化資料庫遷移
    migrate.init_app(app, db)
    
    # 初始化 CORS
    cors.init_app(app, 
                  origins=app.config.get('CORS_ORIGINS', ['http://localhost:3000']),
                  supports_credentials=True)
    
    # 初始化限流器
    limiter.init_app(app)
    
    # 設定日誌
    setup_logging(app)

def setup_logging(app):
    """
    設定應用日誌
    
    Args:
        app: Flask 應用實例
    """
    if not app.debug:
        # 確保日誌目錄存在
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # 設定日誌格式
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s'
        )
        
        # 設定檔案處理器
        file_handler = logging.FileHandler('logs/app.log')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        
        # 設定控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # 添加到應用日誌
        app.logger.addHandler(file_handler)
        app.logger.addHandler(console_handler)
        app.logger.setLevel(logging.INFO)
        
        app.logger.info('Insurance News Aggregator startup')

def register_error_handlers(app):
    """
    註冊錯誤處理器
    
    Args:
        app: Flask 應用實例
    """
    @app.errorhandler(404)
    def not_found_error(error):
        return {"error": "Resource not found"}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {"error": "Internal server error"}, 500
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return {"error": "Rate limit exceeded", "message": str(e.description)}, 429

def create_tables(app):
    """
    創建資料庫表格
    
    Args:
        app: Flask 應用實例
    """
    with app.app_context():
        db.create_all()
        app.logger.info('Database tables created successfully')
