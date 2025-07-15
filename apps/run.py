"""
台灣保險新聞聚合器 - 主應用入口
Insurance News Aggregator - Main Application Entry Point

Author: Development Team
Date: 2025-06-30
Version: 2.2.0 (業務員UI優化)
"""

import sys
import os
import click
import logging
from app import create_app
from config.settings import Config, get_config

# 添加模組路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 設置基本日誌配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('insurance-news')

@click.group()
def cli():
    """台灣保險新聞聚合器命令行工具"""
    pass

@cli.command()
@click.option('--host', default=None, help='服務器主機地址')
@click.option('--port', default=None, type=int, help='服務器端口')
@click.option('--debug/--no-debug', default=None, help='是否啟用調試模式')
@click.option('--env', default=None, help='環境設置(development/testing/production)')
def run(host, port, debug, env):
    """啟動Web應用服務器"""
    # 根據命令行參數更新配置
    config_obj = Config
    if env:
        config_obj = get_config(env)
    
    # 命令行參數優先級高於配置文件
    if host:
        config_obj.HOST = host
    if port:
        config_obj.PORT = port
    if debug is not None:
        config_obj.DEBUG = debug
    
    # 創建應用
    app = create_app(config_obj)
    
    # 顯示啟動信息
    logger.info(f"🚀 台灣保險新聞聚合器 v{config_obj.VERSION} 啟動中...")
    logger.info(f"📍 服務地址: http://{config_obj.HOST}:{config_obj.PORT}")
    logger.info(f"🌐 API 文檔: http://{config_obj.HOST}:{config_obj.PORT}{config_obj.API_PREFIX}/docs")
    logger.info(f"🔧 管理後台: http://{config_obj.HOST}:{config_obj.PORT}/admin")
    logger.info(f"🏠 首頁: http://{config_obj.HOST}:{config_obj.PORT}/")
    logger.info(f"� 業務員區: http://{config_obj.HOST}:{config_obj.PORT}/business")
    
    try:
        app.run(
            host=config_obj.HOST,
            port=config_obj.PORT,
            debug=config_obj.DEBUG
        )
    except KeyboardInterrupt:
        logger.info("👋 服務已手動中止")
    except Exception as e:
        logger.error(f"❌ 應用啟動失敗: {e}", exc_info=True)
        return 1
    
    return 0

@cli.command()
@click.option('--source', help='新聞來源名稱')
@click.option('--limit', default=10, help='抓取數量限制')
def crawl(source, limit):
    """執行爬蟲任務"""
    from crawler.manager import get_crawler_manager
    
    logger.info(f"🕷️ 開始爬取新聞{'(所有來源)' if not source else f'({source})'}")
    
    try:
        manager = get_crawler_manager()
        
        if source:
            # 運行單個爬蟲
            result = manager.run_crawlers(source, limit=limit)
            if result.get('status') == 'success':
                logger.info(f"✅ 爬取完成: {result.get('total', 0)} 條新聞, {result.get('new', 0)} 條新增")
            else:
                logger.error(f"❌ 爬取失敗: {result.get('message', '未知錯誤')}")
                return 1
        else:
            # 運行所有爬蟲
            result = manager.crawl_all_sources(use_mock=True)
            if result.get('status') == 'success':
                logger.info(f"✅ 爬取完成: {result.get('total', 0)} 條新聞, {result.get('new', 0)} 條新增")
            else:
                logger.error(f"❌ 爬取失敗: {result.get('message', '未知錯誤')}")
                return 1
    except Exception as e:
        logger.error(f"❌ 爬取失敗: {e}", exc_info=True)
        return 1
    
    return 0

@cli.command()
def init_db():
    """初始化資料庫結構"""
    from app import db
    from database.models import News, NewsSource, NewsCategory, CrawlLog
    
    logger.info("🗃️ 開始初始化資料庫")
    
    try:
        db.create_all()
        logger.info("✅ 資料庫初始化成功")
    except Exception as e:
        logger.error(f"❌ 資料庫初始化失敗: {e}", exc_info=True)
        return 1
    
    return 0

@cli.command()
def health_check():
    """執行系統健康檢查"""
    from check_status import run_health_check
    
    logger.info("🏥 執行系統健康檢查")
    
    try:
        status = run_health_check()
        if status['status'] == 'healthy':
            logger.info("✅ 系統健康狀態良好")
            for component, info in status['components'].items():
                logger.info(f"  - {component}: {info['status']}")
        else:
            logger.warning("⚠️ 系統健康狀態有異常")
            for component, info in status['components'].items():
                if info['status'] != 'healthy':
                    logger.warning(f"  - {component}: {info['status']} - {info.get('message', '')}")
    except Exception as e:
        logger.error(f"❌ 健康檢查失敗: {e}", exc_info=True)
        return 1
    
    return 0

@cli.command()
def upgrade_db():
    """執行資料庫遷移升級"""
    from flask_migrate import upgrade
    from app import create_app, db
    
    app = create_app(Config)
    
    logger.info("🔄 開始資料庫遷移升級")
    
    with app.app_context():
        try:
            upgrade()
            logger.info("✅ 資料庫遷移升級成功")
        except Exception as e:
            logger.error(f"❌ 資料庫遷移升級失敗: {e}", exc_info=True)
            return 1
    
    return 0

def main():
    """主函數 - 命令行入口"""
    return cli()

if __name__ == "__main__":
    exit(main())
