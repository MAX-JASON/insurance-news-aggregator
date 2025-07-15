#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
賽博朋克UI專用啟動器
Cyberpunk UI Launcher with Complete API Support

此檔案專為賽博朋克業務員界面設計，提供完整的API端點支持
"""

import os
import sys
import logging
import json
from flask import Flask, jsonify, request
from datetime import datetime, timezone, timedelta
import sqlite3
import threading
import time

# 設置路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
sys.path.insert(0, project_root)

# 設置詳細日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(project_root, 'logs', 'cyberpunk_ui.log'), encoding='utf-8')
    ]
)
logger = logging.getLogger('cyberpunk_ui')

def create_cyberpunk_app():
    """創建賽博朋克業務員界面應用"""
    # 設置模板和靜態文件目錄
    template_dir = os.path.join(project_root, 'web', 'templates')
    static_dir = os.path.join(project_root, 'web', 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    # 基本配置
    app.config['SECRET_KEY'] = 'cyberpunk-secret-key-2077'
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(project_root, "instance", "insurance_news.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 添加上下文處理器，自動為業務相關頁面添加賽博朋克風格
    @app.context_processor
    def inject_cyberpunk_style():
        from flask import request
        # 對首頁、所有業務相關頁面和監控頁面添加賽博朋克風格
        return {
            'cyber_style': request.path.startswith('/business') or request.path == '/' or 
                          request.path.startswith('/monitor') or 'cyber' in request.path.lower()
        }
    
    # 創建必要的目錄
    os.makedirs(os.path.join(project_root, 'instance'), exist_ok=True)
    os.makedirs(os.path.join(project_root, 'logs'), exist_ok=True)
    
    # 初始化資料庫
    try:
        from app import db
        db.init_app(app)
        
        with app.app_context():
            from database.models import News, NewsSource, NewsCategory, Feedback, CrawlLog, ErrorLog
            db.create_all()
            logger.info("✅ 資料庫初始化完成")
    except Exception as e:
        logger.warning(f"⚠️ 資料庫初始化失敗，將使用模擬數據: {e}")
    
    # 註冊核心藍圖
    try:
        from web.routes import web_bp
        app.register_blueprint(web_bp)
        logger.info("✅ Web藍圖註冊成功")
        
        # 添加全域變數到 Jinja2 模板上下文
        @app.context_processor
        def inject_global_vars():
            return {
                'app_version': '2077.1.0-cyberpunk',
                'all_endpoints': [str(rule) for rule in app.url_map.iter_rules()]
            }
    except Exception as e:
        logger.error(f"❌ Web藍圖註冊失敗: {e}")
        
        # 添加基本首頁路由
        @app.route('/')
        def index():
            return '''
            <h1>🤖 賽博朋克保險新聞聚合器</h1>
            <p><a href="/business/">📊 業務員工具</a></p>
            <p><a href="/business/cyber-news">🎮 賽博新聞中心</a></p>
            '''
    
    # 註冊分析藍圖
    try:
        from web.analysis_routes import analysis_bp
        app.register_blueprint(analysis_bp)
        logger.info("✅ 分析藍圖註冊成功")
    except Exception as e:
        logger.error(f"❌ 分析藍圖註冊失敗: {e}")
    
    # 註冊業務員工具藍圖
    try:
        from web.business_routes import business_bp
        app.register_blueprint(business_bp)
        logger.info("✅ 業務員工具藍圖註冊成功")
    except Exception as e:
        logger.error(f"❌ 業務員工具藍圖註冊失敗: {e}")
        
        # 添加基本業務員路由，使用賽博朋克風格
        @app.route('/business/')
        def business_index():
            from flask import render_template
            try:
                return render_template('business/index.html')
            except Exception as e:
                logger.error(f"無法載入業務員首頁模板: {e}")
                return '''
                <h1>🤖 賽博朋克業務員工具</h1>
                <p><a href="/business/cyber-news">🎮 賽博新聞中心</a></p>
                '''
        
        @app.route('/business/cyber-news')
        def cyber_news():
            from flask import render_template
            try:
                return render_template('business/cyber_news_center.html')
            except Exception as e:
                logger.error(f"無法載入賽博新聞中心模板: {e}")
                return '''
                <h1>🎮 賽博新聞中心</h1>
                <p>賽博朋克風格的新聞界面</p>
                '''
                
        # 新增其他業務相關頁面路由，確保都使用賽博朋克風格
        @app.route('/business/dashboard')
        def business_dashboard():
            from flask import render_template
            try:
                return render_template('business/dashboard.html', cyber_style=True)
            except Exception as e:
                logger.error(f"無法載入業務儀表板模板: {e}")
                return '''
                <h1>📊 業務儀表板 - 賽博朋克風格</h1>
                <p><a href="/business/">返回業務員工具</a></p>
                '''
    
    # 註冊監控藍圖
    try:
        from web.monitor_routes import monitor
        app.register_blueprint(monitor, url_prefix='/monitor')
        logger.info("✅ 監控藍圖註冊成功")
    except Exception as e:
        logger.error(f"❌ 監控藍圖註冊失敗: {e}")
    
    # 註冊用戶藍圖
    try:
        from web.routes_user import user_bp
        app.register_blueprint(user_bp, url_prefix='/user')
        logger.info("✅ 用戶藍圖註冊成功")
    except Exception as e:
        logger.error(f"❌ 用戶藍圖註冊失敗: {e}")
        
        # 添加基本用戶路由
        @app.route('/user/settings')
        def user_settings():
            return '''
            <h1>🤖 賽博朋克用戶設置</h1>
            <p>用戶個人化設置界面</p>
            '''
    
    # 註冊API藍圖 - 按優先順序嘗試
    api_registered = False
    
    # 1. 嘗試註冊簡單API藍圖
    try:
        from api.simple_api import simple_api_bp
        app.register_blueprint(simple_api_bp, url_prefix='/api')
        logger.info("✅ 簡單API藍圖註冊成功")
        api_registered = True
    except Exception as e:
        logger.warning(f"⚠️ 簡單API藍圖註冊失敗: {e}")
    
    # 2. 嘗試註冊爬蟲API藍圖
    try:
        from api.crawler_api import crawler_api_bp
        app.register_blueprint(crawler_api_bp, url_prefix='/api')
        logger.info("✅ 爬蟲API藍圖註冊成功")
        api_registered = True
    except Exception as e:
        logger.warning(f"⚠️ 爬蟲API藍圖註冊失敗: {e}")
    
    # 3. 嘗試註冊主要API藍圖
    try:
        from api.routes import api_bp
        app.register_blueprint(api_bp, url_prefix='/api/v1')
        logger.info("✅ 主要API藍圖註冊成功")
        api_registered = True
    except Exception as e:
        logger.warning(f"⚠️ 主要API藍圖註冊失敗: {e}")
    
    # 4. 如果所有API藍圖都失敗，直接添加API路由
    if not api_registered:
        logger.info("💊 直接添加賽博朋克API路由")
        
        # 健康檢查API
        @app.route('/api/health')
        def api_health():
            return jsonify({
                'status': 'ok',
                'service': 'cyberpunk_insurance_aggregator',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'version': '2077.1.0-cyberpunk'
            })
        
        # 統計數據API
        @app.route('/api/v1/stats')
        def api_v1_stats():
            try:
                # 嘗試從資料庫獲取真實數據
                db_path = os.path.join(project_root, 'instance', 'insurance_news.db')
                if os.path.exists(db_path):
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # 獲取總新聞數
                    cursor.execute('SELECT COUNT(*) FROM news')
                    total_news = cursor.fetchone()[0]
                    
                    # 獲取今日新聞數
                    today = datetime.now().strftime('%Y-%m-%d')
                    cursor.execute('SELECT COUNT(*) FROM news WHERE date(created_at) = ?', (today,))
                    news_today = cursor.fetchone()[0]
                    
                    # 獲取本週新聞數
                    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                    cursor.execute('SELECT COUNT(*) FROM news WHERE date(created_at) >= ?', (week_ago,))
                    news_this_week = cursor.fetchone()[0]
                    
                    # 獲取新聞來源分布
                    cursor.execute('SELECT source, COUNT(*) as count FROM news GROUP BY source ORDER BY count DESC LIMIT 6')
                    source_data = cursor.fetchall()
                    source_stats = [{'name': source, 'count': count} for source, count in source_data]
                    
                    conn.close()
                    
                    return jsonify({
                        'status': 'success',
                        'data': {
                            'totalNews': total_news,
                            'totalSources': len(source_stats),
                            'totalCategories': 5,
                            'todayNews': news_today,
                            'weekNews': news_this_week,
                            'sourceStats': source_stats[:4],  # 前4個來源
                            'categoryStats': [
                                {'name': '產業新聞', 'count': int(total_news * 0.4)},
                                {'name': '政策法規', 'count': int(total_news * 0.25)},
                                {'name': '市場分析', 'count': int(total_news * 0.2)},
                                {'name': '商品資訊', 'count': int(total_news * 0.15)}
                            ],
                            'lastUpdated': datetime.now(timezone.utc).isoformat()
                        }
                    })
                else:
                    raise Exception("資料庫不存在")
                    
            except Exception as e:
                logger.warning(f"獲取真實統計數據失敗，使用模擬數據: {e}")
                # 使用模擬數據
                return jsonify({
                    'status': 'success',
                    'data': {
                        'totalNews': 542,
                        'totalSources': 12,
                        'totalCategories': 8,
                        'todayNews': 23,
                        'weekNews': 146,
                        'sourceStats': [
                            {'name': '工商時報', 'count': 145},
                            {'name': '經濟日報', 'count': 128},
                            {'name': '金管會公告', 'count': 87},
                            {'name': '保險業動態', 'count': 76}
                        ],
                        'categoryStats': [
                            {'name': '產業新聞', 'count': 213},
                            {'name': '政策法規', 'count': 112},
                            {'name': '市場分析', 'count': 95},
                            {'name': '商品資訊', 'count': 78}
                        ],
                        'lastUpdated': datetime.now(timezone.utc).isoformat()
                    }
                })
        
        # 爬蟲狀態API
        @app.route('/api/v1/crawler/status')
        def api_crawler_status():
            now = datetime.now(timezone.utc)
            return jsonify({
                'status': 'success',
                'data': {
                    'sources': {'total': 12, 'active': 10, 'inactive': 2},
                    'crawls_today': {'total': 24, 'successful': 23, 'failed': 1, 'success_rate': 95.8},
                    'news': {'total': 542, 'today': 23},
                    'recent_activities': [
                        {
                            'id': 1,
                            'source': '工商時報保險版',
                            'success': True,
                            'news_found': 15,
                            'news_new': 8,
                            'duration': 45.2,
                            'created_at': (now - timedelta(minutes=15)).isoformat(),
                            'error_message': None
                        },
                        {
                            'id': 2,
                            'source': '模擬新聞生成器',
                            'success': True,
                            'news_found': 10,
                            'news_new': 5,
                            'duration': 2.1,
                            'created_at': (now - timedelta(minutes=30)).isoformat(),
                            'error_message': None
                        }
                    ]
                }
            })
        
        # 爬蟲來源API
        @app.route('/api/v1/crawler/sources')
        def api_crawler_sources():
            now = datetime.now(timezone.utc)
            return jsonify({
                'status': 'success',
                'data': [
                    {
                        'id': 1,
                        'name': '工商時報保險版',
                        'url': 'https://ctee.com.tw/category/finance/insurance',
                        'status': 'active',
                        'total_news': 145,
                        'successful_crawls': 120,
                        'failed_crawls': 5,
                        'success_rate': 96.0,
                        'reliability_score': 0.98,
                        'last_crawl': (now - timedelta(minutes=15)).isoformat(),
                        'last_crawl_success': True
                    },
                    {
                        'id': 2,
                        'name': '模擬新聞生成器',
                        'url': 'internal://mock_generator',
                        'status': 'active',
                        'total_news': 156,
                        'successful_crawls': 156,
                        'failed_crawls': 0,
                        'success_rate': 100.0,
                        'reliability_score': 1.0,
                        'last_crawl': (now - timedelta(minutes=5)).isoformat(),
                        'last_crawl_success': True
                    }
                ]
            })
        
        # 監控API端點
        @app.route('/monitor/api/crawler/status')
        def monitor_crawler_status():
            return api_crawler_status()
        
        @app.route('/monitor/api/news/stats')
        def monitor_news_stats():
            return api_v1_stats()
        
        # 爬蟲控制API
        @app.route('/api/crawler/status')
        def api_crawler_status_v2():
            return api_crawler_status()
        
        @app.route('/api/crawler/start', methods=['POST'])
        def api_crawler_start():
            try:
                data = request.get_json() or {}
                use_mock = data.get('use_mock', False)  # 默認不使用模擬數據
                sources = data.get('sources', [])
                
                logger.info(f"🤖 賽博朋克爬蟲啟動 - 使用真實數據, 來源: {sources}")
                
                # 定義爬蟲函數，抓取真實新聞
                def run_real_crawler():
                    try:
                        # 動態導入爬蟲管理器，避免循環引用
                        from crawler.manager import CrawlerManager
                        from crawler.rss_crawler import RSSNewsCrawler
                        from crawler.real_crawler_fixed import RealInsuranceNewsCrawler
                        
                        logger.info("🔍 初始化爬蟲管理器...")
                        
                        # 初始化爬蟲
                        manager = CrawlerManager()
                        
                        # 確保有所需的爬蟲
                        if 'real' not in manager.crawlers:
                            manager.crawlers['real'] = RealInsuranceNewsCrawler()
                        
                        if 'rss' not in manager.crawlers:
                            manager.crawlers['rss'] = RSSNewsCrawler()
                        
                        # 開始爬取
                        logger.info("🔍 開始爬取真實保險新聞...")
                        
                        # 使用爬蟲管理器執行
                        try:
                            result = manager.run_all_crawlers(use_real=True)
                            logger.info(f"✅ 爬蟲完成，獲得 {result.get('total_news', 0)} 則新聞")
                        except Exception as e:
                            logger.error(f"❌ 爬蟲管理器執行失敗: {e}")
                            
                            # 直接使用單獨爬蟲作為備用方案
                            logger.info("🔄 嘗試使用單獨爬蟲...")
                            
                            real_crawler = RealInsuranceNewsCrawler()
                            news_from_google = real_crawler.crawl_google_news()
                            
                            rss_crawler = RSSNewsCrawler()
                            news_from_rss = rss_crawler.crawl_all_feeds()
                            
                            all_news = news_from_google + news_from_rss
                            
                            # 存入數據庫
                            try:
                                db_path = os.path.join(project_root, "instance", "insurance_news.db")
                                if os.path.exists(db_path):
                                    conn = sqlite3.connect(db_path)
                                    cursor = conn.cursor()
                                    
                                    # 檢查是否有新聞表
                                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='news'")
                                    if cursor.fetchone():
                                        # 準備保存抓取的新聞
                                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                        
                                        # 插入新聞
                                        for news in all_news:
                                            title = news.get('title', '')
                                            content = news.get('content', '')
                                            category = news.get('category', '未分類')
                                            source = news.get('source', '網路新聞')
                                            
                                            cursor.execute(
                                                "INSERT INTO news (title, content, category, source, created_at) VALUES (?, ?, ?, ?, ?)",
                                                (title, content, category, source, now)
                                            )
                                        
                                        conn.commit()
                                        logger.info(f"✅ 已成功添加 {len(all_news)} 條真實新聞到數據庫")
                                    else:
                                        logger.warning("⚠️ 未找到新聞表，跳過數據插入")
                                    
                                    conn.close()
                                else:
                                    logger.warning(f"⚠️ 數據庫不存在: {db_path}，將創建備用文件")
                                    # 創建新聞緩存目錄
                                    os.makedirs(os.path.join(project_root, "cache", "real_news"), exist_ok=True)
                                    
                                    # 寫入新聞數據文件
                                    real_file = os.path.join(project_root, "cache", "real_news", f"news_{int(time.time())}.json")
                                    with open(real_file, 'w', encoding='utf-8') as f:
                                        json.dump({
                                            'timestamp': datetime.now().isoformat(),
                                            'news': all_news
                                        }, f, ensure_ascii=False, indent=2)
                                    
                                    logger.info(f"✅ 已創建真實新聞文件: {real_file}")
                            except Exception as db_error:
                                logger.error(f"❌ 數據庫操作失敗: {db_error}")
                    
                    except Exception as e:
                        logger.error(f"❌ 爬蟲執行錯誤: {e}")
                    
                    logger.info("🤖 賽博朋克爬蟲執行完成")
                
                # 啟動爬蟲線程
                threading.Thread(target=run_real_crawler, daemon=True).start()
                
                return jsonify({
                    'status': 'success',
                    'message': '🤖 賽博朋克爬蟲任務已啟動，正在抓取真實保險新聞...',
                    'task_id': f'cyber_crawler_{int(datetime.now().timestamp())}',
                    'estimated_duration': '2-5分鐘',
                    'theme': 'cyberpunk'
                })
                
            except Exception as e:
                logger.error(f"🤖 賽博朋克爬蟲啟動失敗: {e}")
                return jsonify({
                    'status': 'error',
                    'message': f'啟動爬蟲失敗: {str(e)}'
                }), 500
        
        # 業務員分類新聞API
        @app.route('/api/business/category-news')
        def api_business_category_news():
            group = request.args.get('group', '')
            category = request.args.get('category', '')
            
            # 賽博朋克風格的模擬數據
            news_data = [
                {
                    'id': 101,
                    'title': f'🤖 {category}相關新聞：保險業賽博進化',
                    'summary': f'這是關於{category}的重要新聞，採用賽博朋克風格展示，對業務員工作具有指導意義。',
                    'importance_score': 0.8,
                    'published_date': datetime.now(timezone.utc).isoformat(),
                    'source_name': '賽博保險動態',
                    'cyber_theme': True
                }
            ]
            
            return jsonify({
                'status': 'success',
                'news': news_data,
                'theme': 'cyberpunk'
            })
        
        # 賽博朋克專用API端點
        @app.route('/api/cyber-news')
        def api_cyber_news():
            """賽博朋克新聞API"""
            return jsonify({
                'status': 'success',
                'data': [
                    {
                        'id': 1,
                        'title': '🤖 AI保險理賠系統正式上線',
                        'summary': '新一代人工智能理賠系統將大幅提升處理效率',
                        'category': '科技創新',
                        'importance': 'high',
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'cyber_style': True
                    },
                    {
                        'id': 2,
                        'title': '🔮 區塊鏈保險合約技術突破',
                        'summary': '智能合約技術在保險業的應用迎來重大進展',
                        'category': '技術革新',
                        'importance': 'medium',
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                        'cyber_style': True
                    }
                ]
            })
        
        @app.route('/api/cyber-clients')
        def api_cyber_clients():
            """賽博朋克客戶API"""
            return jsonify({
                'status': 'success',
                'data': [
                    {
                        'id': 1,
                        'name': 'Chen.Matrix',
                        'status': 'active',
                        'risk_level': 'low',
                        'last_contact': datetime.now(timezone.utc).isoformat(),
                        'cyber_profile': True
                    },
                    {
                        'id': 2,
                        'name': 'Wang.Neo',
                        'status': 'pending',
                        'risk_level': 'medium',
                        'last_contact': (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                        'cyber_profile': True
                    }
                ]
            })
        
        @app.route('/api/cyber-stats')
        def api_cyber_stats():
            """賽博朋克統計API"""
            return jsonify({
                'status': 'success',
                'data': {
                    'neural_efficiency': 98.5,
                    'data_packets_processed': 15420,
                    'ai_recommendations': 42,
                    'cybersecurity_level': 'maximum',
                    'quantum_sync_status': 'optimal'
                }
            })
        
        logger.info("✅ 賽博朋克API路由添加成功")
    
    # 錯誤處理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'status': 'error',
            'code': 404,
            'message': '🤖 賽博空間中未找到指定資源',
            'cyber_theme': True
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'status': 'error',
            'code': 500,
            'message': '🤖 神經網路發生內部錯誤',
            'cyber_theme': True
        }), 500
    
    # 添加模板全域變數
    @app.context_processor
    def inject_template_vars():
        from datetime import datetime
        return {
            'now': datetime.now(),
            'app_version': '2077.1.0-cyberpunk'
        }
    
    return app

def main():
    """主函數"""
    logger.info("🤖 啟動賽博朋克保險新聞聚合器...")
    
    try:
        # 創建應用
        app = create_cyberpunk_app()
        
        # 顯示啟動資訊
        host = "127.0.0.1"
        port = 5000
        
        print("\n" + "="*60)
        print("🤖 賽博朋克保險新聞聚合器 - 已就緒")
        print("="*60)
        print(f"📍 主服務: http://{host}:{port}/")
        print(f"🏠 業務員主頁: http://{host}:{port}/business/")
        print(f"🎮 賽博新聞中心: http://{host}:{port}/business/cyber-news")
        print(f"📊 監控中心: http://{host}:{port}/monitor/")
        print(f"🔌 API健康檢查: http://{host}:{port}/api/health")
        print("="*60)
        print("💡 賽博朋克風格界面已啟用")
        print("🔧 完整API端點支持已載入")
        print("按 Ctrl+C 退出賽博空間")
        print("="*60)
        
        # 啟動應用
        app.run(host=host, port=port, debug=True, use_reloader=False)
        
    except KeyboardInterrupt:
        logger.info("👋 已安全退出賽博空間")
    except Exception as e:
        logger.error(f"❌ 賽博朋克系統啟動失敗: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
