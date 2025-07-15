"""
爬蟲與系統監控路由
Crawler and System Monitoring Routes

提供爬蟲運行狀態和系統健康度的監控功能
"""

from flask import Blueprint, render_template, jsonify, current_app, request
from datetime import datetime, timedelta
import os
import psutil
from sqlalchemy import func, desc
import logging
import json
from database.models import CrawlLog, News, ErrorLog
from app.extensions import db
from sqlalchemy import func, desc
from web.health_check import health_check, init_health_check

# 創建藍圖
monitor = Blueprint('monitor', __name__)

@monitor.route('/')
def index():
    """監控首頁"""
    return render_template('monitor/index.html')

@monitor.route('/api/status')
def api_status():
    """獲取系統狀態API"""
    # 獲取CPU使用率
    cpu_percent = psutil.cpu_percent(interval=None)
    
    # 獲取內存使用情況
    memory = psutil.virtual_memory()
    memory_used_gb = memory.used / (1024**3)
    memory_total_gb = memory.total / (1024**3)
    memory_percent = memory.percent
    
    # 獲取磁盤使用情況
    disk = psutil.disk_usage('/')
    disk_used_gb = disk.used / (1024**3)
    disk_total_gb = disk.total / (1024**3)
    disk_percent = disk.percent
    
    # 獲取當前時間
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 獲取應用運行時間
    app_start_time = current_app.config.get('START_TIME', datetime.now())
    uptime_seconds = (datetime.now() - app_start_time).total_seconds()
    uptime = {
        'days': int(uptime_seconds // (24*60*60)),
        'hours': int((uptime_seconds % (24*60*60)) // 3600),
        'minutes': int((uptime_seconds % 3600) // 60),
        'seconds': int(uptime_seconds % 60)
    }
    
    return jsonify({
        'time': current_time,
        'uptime': uptime,
        'system': {
            'cpu': {
                'percent': cpu_percent
            },
            'memory': {
                'used': round(memory_used_gb, 2),
                'total': round(memory_total_gb, 2),
                'percent': memory_percent
            },
            'disk': {
                'used': round(disk_used_gb, 2),
                'total': round(disk_total_gb, 2),
                'percent': disk_percent
            }
        }
    })

@monitor.route('/api/crawler/status')
def crawler_status():
    """獲取爬蟲狀態API"""
    from database.models import CrawlLog, ErrorLog, News, NewsSource, db
    
    # 獲取最近的爬蟲運行記錄
    recent_logs = CrawlLog.query.order_by(
        CrawlLog.start_time.desc()
    ).limit(10).all()
    
    # 統計過去24小時的爬蟲運行情況
    yesterday = datetime.now() - timedelta(days=1)
    
    # 修正：使用正確的欄位名稱和關聯查詢
    stats = db.session.query(
        NewsSource.name.label('source_name'),
        func.count(CrawlLog.id).label('runs'),
        func.sum(CrawlLog.news_found).label('found'),
        func.sum(CrawlLog.news_new).label('new'),
        func.avg(CrawlLog.duration).label('avg_duration')
    ).join(
        NewsSource, CrawlLog.source_id == NewsSource.id
    ).filter(
        CrawlLog.start_time >= yesterday
    ).group_by(
        NewsSource.name
    ).all()
    
    # 統計每個來源的新聞數量
    source_stats = db.session.query(
        NewsSource.name.label('source_name'),
        func.count(News.id).label('count')
    ).join(
        NewsSource, News.source_id == NewsSource.id
    ).group_by(
        NewsSource.name
    ).all()
    
    # 獲取最近的錯誤日誌
    recent_errors = ErrorLog.query.order_by(
        ErrorLog.timestamp.desc()
    ).limit(5).all()
    
    return jsonify({
        'recent_runs': [{
            'id': log.id,
            'source': log.source.name if log.source else '未知來源',
            'start_time': log.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration': log.duration or 0,
            'found': log.news_found or 0,
            'new': log.news_new or 0,
            'status': 'success' if log.success else 'failed'
        } for log in recent_logs],
        'daily_stats': [{
            'source': stat.source_name,
            'runs': stat.runs,
            'found': int(stat.found) if stat.found else 0,
            'new': int(stat.new) if stat.new else 0,
            'avg_duration': round(float(stat.avg_duration), 2) if stat.avg_duration else 0
        } for stat in stats],
        'source_totals': [{
            'source': stat.source_name,
            'count': stat.count
        } for stat in source_stats],
        'recent_errors': [{
            'id': err.id,
            'module': err.module,
            'timestamp': err.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'level': err.level,
            'message': err.message
        } for err in recent_errors]
    })

@monitor.route('/api/news/stats')
def news_stats():
    """獲取新聞統計信息"""
    # 獲取過去7天的新聞數量趨勢
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    days = []
    daily_counts = []
    
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        next_day = day + timedelta(days=1)
        
        count = News.query.filter(
            News.published_date >= day,
            News.published_date < next_day
        ).count()
        
        days.append(day.strftime('%m-%d'))
        daily_counts.append(count)
    
    # 獲取總新聞數
    total_news = News.query.count()
    
    # 獲取今日新聞數
    today_news = News.query.filter(
        News.published_date >= today
    ).count()
    
    # 獲取各來源新聞占比
    source_distribution = db.session.query(
        News.source,
        func.count(News.id).label('count')
    ).group_by(
        News.source
    ).all()
    
    return jsonify({
        'total': total_news,
        'today': today_news,
        'trend': {
            'dates': days,
            'counts': daily_counts
        },
        'sources': [{
            'name': src.source,
            'count': src.count,
            'percentage': round(src.count / total_news * 100, 1) if total_news else 0
        } for src in source_distribution]
    })

@monitor.route('/api/logs/errors')
def error_logs():
    """獲取錯誤日誌"""
    from flask import request
    days = int(request.args.get('days', 1))
    since = datetime.now() - timedelta(days=days)
    
    logs = ErrorLog.query.filter(
        ErrorLog.timestamp >= since
    ).order_by(
        ErrorLog.timestamp.desc()
    ).limit(100).all()
    
    return jsonify({
        'logs': [{
            'id': log.id,
            'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'level': log.level,
            'module': log.module,
            'message': log.message,
            'traceback': log.traceback
        } for log in logs]
    })

@monitor.route('/crawler')
def crawler_dashboard():
    """爬蟲監控儀表板頁面"""
    return render_template('monitor/crawler.html')

@monitor.route('/api/crawler/control', methods=['POST'])
def crawler_control():
    """爬蟲控制API
    
    可用操作:
    - start: 手動執行一次爬蟲
    - stop: 停止後台爬蟲
    - enable_auto: 啟用自動爬蟲
    - disable_auto: 禁用自動爬蟲
    """
    try:
        # 獲取請求參數
        action = request.json.get('action', '')
        
        # 導入爬蟲管理器
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'crawler'))
        from manager import get_crawler_manager
        
        crawler_manager = get_crawler_manager()
        
        # 執行相應操作
        if action == 'start':
            use_mock = request.json.get('use_mock', True)
            result = crawler_manager.crawl_all_sources(use_mock=use_mock)
            return jsonify({
                'status': 'success',
                'message': '爬蟲執行成功',
                'data': result
            })
        
        elif action == 'stop':
            success = crawler_manager.stop_scheduled_crawling()
            return jsonify({
                'status': 'success',
                'message': '爬蟲已停止' if success else '爬蟲未在運行中',
                'data': {'stopped': success}
            })
        
        elif action == 'enable_auto':
            enabled = crawler_manager.toggle_auto_crawl(True)
            interval = request.json.get('interval', 30)
            crawler_manager.start_scheduled_crawling(interval_minutes=interval)
            return jsonify({
                'status': 'success',
                'message': f'自動爬蟲已啟用，間隔{interval}分鐘',
                'data': {'enabled': enabled}
            })
        
        elif action == 'disable_auto':
            enabled = crawler_manager.toggle_auto_crawl(False)
            return jsonify({
                'status': 'success',
                'message': '自動爬蟲已禁用',
                'data': {'enabled': enabled}
            })
        
        else:
            return jsonify({
                'status': 'error',
                'message': f'未知操作: {action}'
            }), 400
            
    except Exception as e:
        current_app.logger.error(f"爬蟲控制API錯誤: {e}")
        return jsonify({
            'status': 'error',
            'message': f'操作失敗: {str(e)}'
        }), 500

@monitor.route('/api/crawler/status')
def api_crawler_status():
    """獲取爬蟲狀態API"""
    try:
        # 導入爬蟲管理器
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'crawler'))
        from manager import get_crawler_manager
        
        crawler_manager = get_crawler_manager()
        return jsonify({
            'status': 'success',
            'data': crawler_manager.get_crawler_status()
        })
    except Exception as e:
        current_app.logger.error(f"獲取爬蟲狀態失敗: {e}")
        return jsonify({
            'status': 'error',
            'message': f'獲取爬蟲狀態失敗: {str(e)}'
        }), 500

@monitor.route('/system')
def system_dashboard():
    """系統監控儀表板頁面"""
    return render_template('monitor/system.html')

@monitor.route('/api/health')
def health_status():
    """獲取系統健康狀態API"""
    return jsonify(health_check.get_health_status())

@monitor.route('/api/health/services')
def service_status():
    """獲取服務健康狀態API"""
    return jsonify(health_check.get_service_status())

@monitor.route('/api/health/resources')
def resource_status():
    """獲取資源使用狀態API"""
    return jsonify(health_check.get_resource_usage())

@monitor.route('/api/health/run_check', methods=['POST'])
def run_health_check():
    """手動執行健康檢查"""
    service_name = request.json.get('service')
    result = health_check.check_service(service_name) if service_name else health_check.run_all_checks()
    return jsonify({"success": True, "result": result})

@monitor.route('/logs')
def logs_dashboard():
    """日誌查看儀表板頁面"""
    return render_template('monitor/logs.html')

@monitor.route('/manual_crawl')
def manual_crawl():
    """手動執行爬蟲頁面"""
    return render_template('monitor/manual_crawl.html')

@monitor.route('/settings')
def monitor_settings():
    """監控設定頁面"""
    return render_template('monitor/settings.html')
