"""
保險新聞聚合器 - 應用程式工廠
Insurance News Aggregator - Application Factory

這個模組包含Flask應用程式的工廠函數和初始化邏輯
"""

from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import logging
import os
import click

# 全局擴展對象
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
jwt = JWTManager()

def create_app(config_object=None):
    """
    Flask 應用程式工廠函數
    
    Args:
        config_object: 配置對象，默認從環境變數獲取
        
    Returns:
        Flask: 配置完成的Flask應用實例
    """
    # 設置模板和靜態文件目錄
    template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'web', 'templates')
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'web', 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    # 載入配置
    if config_object:
        app.config.from_object(config_object)
    else:
        # 從環境變數載入配置
        from config.settings import get_config
        config_name = os.environ.get('FLASK_ENV', 'development')
        config_obj = get_config(config_name)
        app.config.from_object(config_obj)
        # 調用配置初始化
        config_obj.init_app(app)
    
    # 設置日誌系統（必須在其他初始化之前）
    setup_logging(app)
    
    # 初始化擴展
    init_extensions(app)
    
    # 註冊藍圖
    register_blueprints(app)
    
    # 註冊錯誤處理器
    register_error_handlers(app)
    
    # 添加應用上下文處理器
    register_context_processors(app)
    
    # 註冊命令行命令
    register_cli_commands(app)
    
    # 啟動自動爬蟲服務
    setup_auto_crawl(app)
    
    # 啟動系統健康監控
    setup_health_monitoring(app)
    
    app.logger.info(f"🎉 {app.config.get('APP_NAME')} v{app.config.get('VERSION')} 應用啟動完成")
    
    return app

def setup_auto_crawl(app):
    """設置自動爬蟲功能"""
    import threading
    import time
    
    # 啟動時自動執行一次爬蟲
    def initial_crawl():
        app.logger.info("🕷️ 應用啟動時自動執行爬蟲...")
        with app.app_context():
            try:
                # 導入爬蟲管理器
                import sys
                import os
                sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'crawler'))
                from manager import get_crawler_manager
                
                crawler_manager = get_crawler_manager()
                result = crawler_manager.crawl_all_sources(use_mock=True)
                
                if result['status'] == 'success':
                    app.logger.info(f"✅ 自動爬取完成: {result.get('total', 0)} 條新聞, {result.get('new', 0)} 條新增")
                else:
                    app.logger.warning(f"⚠️ 自動爬取未完全成功: {result.get('message', '未知錯誤')}")
            except Exception as e:
                app.logger.error(f"❌ 自動爬取失敗: {e}")
    
    # 導入爬蟲管理器
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'crawler'))
    from manager import get_crawler_manager
    
    with app.app_context():
        # 獲取爬蟲管理器
        crawler_manager = get_crawler_manager()
        
        # 配置並啟動定時爬蟲
        interval_minutes = app.config.get('CRAWLER_INTERVAL_MINUTES', 30)
        app.logger.info(f"配置自動爬蟲服務 (間隔: {interval_minutes}分鐘)")
        
        # 啟動定期爬取
        crawler_manager.start_scheduled_crawling(interval_minutes=interval_minutes)
    
    app.logger.info("🚀 自動爬蟲服務已啟動")

def setup_health_monitoring(app):
    """設置系統健康監控"""
    app.logger.info("🔍 正在初始化系統健康監控...")
    
    try:
        from web.health_check import init_health_check
        
        # 初始化健康檢查系統
        health_check_instance = init_health_check(app)
        
        # 將健康檢查實例添加到應用上下文
        app.health_check = health_check_instance
        
        app.logger.info("✅ 系統健康監控初始化完成")
    except Exception as e:
        app.logger.error(f"❌ 系統健康監控初始化失敗: {e}")

def init_extensions(app):
    """初始化Flask擴展"""
    app.logger.info("🔧 正在初始化Flask擴展...")
    
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, origins=app.config.get('CORS_ORIGINS', ['*']))
    jwt.init_app(app)
    
    app.logger.info("✅ Flask擴展初始化完成")

def register_blueprints(app):
    """註冊藍圖"""
    app.logger.info("📋 正在註冊藍圖...")
    
    try:
        # API 藍圖
        from api.routes import api_bp
        app.register_blueprint(api_bp, url_prefix=app.config.get('API_PREFIX', '/api/v1'))
        app.logger.info("✅ API藍圖註冊成功")
    except ImportError as e:
        app.logger.warning(f"⚠️ API藍圖註冊失敗: {e}")
    
    try:
        # 爬蟲API藍圖
        from api.crawler_api import crawler_api_bp
        app.register_blueprint(crawler_api_bp, url_prefix='/api')
        app.logger.info("✅ 爬蟲API藍圖註冊成功")
    except ImportError as e:
        app.logger.warning(f"⚠️ 爬蟲API藍圖註冊失敗: {e}")
        
    try:
        # 簡單API藍圖 (備用)
        from api.simple_api import simple_api_bp
        app.register_blueprint(simple_api_bp, url_prefix='/api')
        app.logger.info("✅ 簡單API藍圖註冊成功")
    except ImportError as e:
        app.logger.warning(f"⚠️ 簡單API藍圖註冊失敗: {e}")
    
    try:
        # Web 藍圖
        from web.routes import web_bp
        app.register_blueprint(web_bp)
        app.logger.info("✅ Web藍圖註冊成功")
    except ImportError as e:
        app.logger.warning(f"⚠️ Web藍圖註冊失敗: {e}")
    
    try:
        # 分析藍圖
        from web.analysis_routes import analysis_bp
        app.register_blueprint(analysis_bp)
        app.logger.info("✅ 分析藍圖註冊成功")
    except ImportError as e:
        app.logger.warning(f"⚠️ 分析藍圖註冊失敗: {e}")
    
    try:
        # 業務員藍圖
        from web.business_routes import business_bp
        app.register_blueprint(business_bp)
        app.logger.info("✅ 業務員藍圖註冊成功")
    except ImportError as e:
        app.logger.warning(f"⚠️ 業務員藍圖註冊失敗: {e}")
        
    try:
        # 用戶設置藍圖
        from web.routes_user import user_bp
        app.register_blueprint(user_bp, url_prefix='/user')
        app.logger.info("✅ 用戶設置藍圖註冊成功")
    except ImportError as e:
        app.logger.warning(f"⚠️ 用戶設置藍圖註冊失敗: {e}")
        
    try:
        # 監控藍圖
        from web.monitor_routes import monitor
        app.register_blueprint(monitor, url_prefix='/monitor')
        app.logger.info("✅ 監控藍圖註冊成功")
    except ImportError as e:
        app.logger.warning(f"⚠️ 監控藍圖註冊失敗: {e}")
        
    try:
        # 簡易反饋藍圖
        from web.feedback_simple import register_feedback_simple
        register_feedback_simple(app)
        app.logger.info("✅ 簡易反饋藍圖註冊成功")
    except ImportError as e:
        app.logger.warning(f"⚠️ 簡易反饋藍圖註冊失敗: {e}")

def setup_logging(app):
    """設置日誌系統"""
    from config.logging import logger_setup
    logger_setup.init_app(app)

def register_error_handlers(app):
    """註冊錯誤處理器"""
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f"404錯誤: {request.url}")
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Not found',
                'message': '請求的資源不存在',
                'status_code': 404
            }), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"500錯誤: {error}")
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Internal server error',
                'message': '伺服器內部錯誤',
                'status_code': 500
            }), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        app.logger.warning(f"403錯誤: {request.url}")
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Forbidden',
                'message': '沒有訪問權限',
                'status_code': 403
            }), 403
        return render_template('errors/403.html'), 403

def register_context_processors(app):
    """註冊上下文處理器"""
    @app.context_processor
    def inject_config():
        return {
            'config': app.config,
            'app_name': app.config.get('APP_NAME'),
            'app_version': app.config.get('VERSION')
        }

def register_cli_commands(app):
    """註冊命令行命令"""
    
    @app.cli.command()
    def init_db():
        """初始化資料庫"""
        # 導入模型（在函數內部使用具體導入）
        from database.models import News, NewsSource, NewsCategory, CrawlLog, SystemConfig
        db.create_all()
        click.echo("✅ 資料庫初始化完成")
    
    @app.cli.command()
    def create_admin():
        """創建管理員用戶"""
        # 這裡可以添加創建管理員的邏輯
        click.echo("👤 管理員用戶創建功能待實現")
    
    @app.cli.command()
    def test_crawler():
        """測試爬蟲功能"""
        click.echo("🕷️ 爬蟲測試功能待實現")
