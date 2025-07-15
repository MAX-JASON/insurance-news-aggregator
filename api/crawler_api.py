"""
爬蟲控制API模組
Crawler Control API Module

提供爬蟲控制和監控的API端點
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timezone, timedelta
import logging
import threading
import time

# 創建爬蟲API藍圖
crawler_api_bp = Blueprint('crawler_api', __name__)
logger = logging.getLogger(__name__)

# 全域爬蟲狀態
crawler_status = {
    'is_running': False,
    'last_run_time': None,
    'total_crawls': 0,
    'successful_crawls': 0,
    'failed_crawls': 0,
    'auto_mode': True,
    'scheduler_active': False
}

# 爬蟲任務執行器
crawler_executor = None
auto_scheduler_thread = None
should_stop_scheduler = False

@crawler_api_bp.route('/crawler/status')
def get_crawler_status():
    """獲取爬蟲狀態"""
    try:
        global crawler_status
        
        # 更新運行狀態
        now = datetime.now(timezone.utc)
        
        # 模擬今日統計
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 返回爬蟲狀態
        return jsonify({
            'status': 'success',
            'data': {
                'crawler': {
                    'is_running': crawler_status['is_running'],
                    'auto_mode': crawler_status['auto_mode'],
                    'scheduler_active': crawler_status['scheduler_active'],
                    'last_run': crawler_status['last_run_time']
                },
                'sources': {
                    'total': 8,
                    'active': 6,
                    'inactive': 2
                },
                'statistics': {
                    'total_crawls': crawler_status['total_crawls'],
                    'successful_crawls': crawler_status['successful_crawls'],
                    'failed_crawls': crawler_status['failed_crawls'],
                    'success_rate': round((crawler_status['successful_crawls'] / max(crawler_status['total_crawls'], 1)) * 100, 1)
                },
                'today_stats': {
                    'crawls': 12,
                    'news_found': 87,
                    'new_articles': 23,
                    'last_crawl': (now - timedelta(minutes=15)).isoformat()
                },
                'recent_activities': [
                    {
                        'id': 1,
                        'source': '工商時報保險版',
                        'success': True,
                        'news_found': 15,
                        'news_new': 8,
                        'duration': 45.2,
                        'timestamp': (now - timedelta(minutes=15)).isoformat(),
                        'error_message': None
                    },
                    {
                        'id': 2,
                        'source': '經濟日報保險',
                        'success': True,
                        'news_found': 12,
                        'news_new': 5,
                        'duration': 38.7,
                        'timestamp': (now - timedelta(minutes=30)).isoformat(),
                        'error_message': None
                    },
                    {
                        'id': 3,
                        'source': 'RSS聚合器',
                        'success': False,
                        'news_found': 0,
                        'news_new': 0,
                        'duration': 12.1,
                        'timestamp': (now - timedelta(minutes=45)).isoformat(),
                        'error_message': '連接超時'
                    }
                ]
            }
        })
        
    except Exception as e:
        logger.error(f"獲取爬蟲狀態失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '獲取爬蟲狀態失敗',
            'error': str(e)
        }), 500

@crawler_api_bp.route('/crawler/start', methods=['POST'])
def start_crawler():
    """手動啟動爬蟲"""
    try:
        global crawler_status, crawler_executor
        
        if crawler_status['is_running']:
            return jsonify({
                'status': 'error',
                'message': '爬蟲已在運行中，請等待完成後再試'
            }), 400
        
        # 獲取請求參數
        data = request.get_json() or {}
        use_mock = data.get('use_mock', True)
        sources = data.get('sources', [])
        max_news = data.get('max_news', 50)
        
        logger.info(f"手動啟動爬蟲 - 模擬模式: {use_mock}, 來源: {sources}")
        
        def run_crawler_task():
            """在背景執行爬蟲任務"""
            global crawler_status
            
            crawler_status['is_running'] = True
            start_time = datetime.now(timezone.utc)
            
            try:
                # 模擬爬蟲執行
                time.sleep(2)  # 模擬執行時間
                
                if use_mock:
                    # 使用模擬數據
                    mock_result = {
                        'total_found': 25,
                        'new_articles': 18,
                        'updated_articles': 3,
                        'sources_processed': ['模擬新聞生成器', '工商時報保險版', '經濟日報保險'],
                        'execution_time': 2.5
                    }
                    crawler_status['successful_crawls'] += 1
                    result_message = f"模擬爬蟲執行成功，找到 {mock_result['total_found']} 則新聞，新增 {mock_result['new_articles']} 則"
                else:
                    # 嘗試真實爬蟲
                    try:
                        from crawler.manager import get_crawler_manager
                        manager = get_crawler_manager()
                        result = manager.crawl_all_sources(use_mock=False)
                        
                        if result['status'] == 'success':
                            crawler_status['successful_crawls'] += 1
                            result_message = result['message']
                        else:
                            crawler_status['failed_crawls'] += 1
                            result_message = f"爬蟲執行失敗: {result['message']}"
                            
                    except Exception as e:
                        crawler_status['failed_crawls'] += 1
                        result_message = f"爬蟲執行失敗: {str(e)}"
                
                crawler_status['total_crawls'] += 1
                crawler_status['last_run_time'] = start_time.isoformat()
                
                logger.info(f"爬蟲任務完成: {result_message}")
                
            except Exception as e:
                logger.error(f"爬蟲任務執行失敗: {e}")
                crawler_status['failed_crawls'] += 1
                crawler_status['total_crawls'] += 1
                
            finally:
                crawler_status['is_running'] = False
        
        # 在背景線程執行爬蟲
        crawler_executor = threading.Thread(target=run_crawler_task, daemon=True)
        crawler_executor.start()
        
        return jsonify({
            'status': 'success',
            'message': '爬蟲任務已啟動，正在背景執行',
            'task_id': f'crawler_{int(datetime.now().timestamp())}',
            'estimated_duration': '2-5分鐘'
        })
        
    except Exception as e:
        logger.error(f"啟動爬蟲失敗: {e}")
        return jsonify({
            'status': 'error',
            'message': f'啟動爬蟲失敗: {str(e)}'
        }), 500

@crawler_api_bp.route('/crawler/stop', methods=['POST'])
def stop_crawler():
    """停止爬蟲"""
    try:
        global crawler_status, should_stop_scheduler
        
        if not crawler_status['is_running'] and not crawler_status['scheduler_active']:
            return jsonify({
                'status': 'error',
                'message': '沒有正在運行的爬蟲任務'
            }), 400
        
        # 停止自動排程
        should_stop_scheduler = True
        crawler_status['scheduler_active'] = False
        
        # 注意：手動爬蟲任務可能無法立即停止，但會標記為停止
        if crawler_status['is_running']:
            logger.info("正在停止爬蟲任務...")
            # 實際的停止邏輯依賴於爬蟲實現
        
        return jsonify({
            'status': 'success',
            'message': '爬蟲停止指令已發送'
        })
        
    except Exception as e:
        logger.error(f"停止爬蟲失敗: {e}")
        return jsonify({
            'status': 'error',
            'message': f'停止爬蟲失敗: {str(e)}'
        }), 500

@crawler_api_bp.route('/crawler/toggle-auto', methods=['POST'])
def toggle_auto_mode():
    """切換自動模式"""
    try:
        global crawler_status, auto_scheduler_thread, should_stop_scheduler
        
        data = request.get_json() or {}
        enable_auto = data.get('enable', not crawler_status['auto_mode'])
        
        crawler_status['auto_mode'] = enable_auto
        
        if enable_auto and not crawler_status['scheduler_active']:
            # 啟動自動排程
            should_stop_scheduler = False
            
            def auto_scheduler():
                """自動排程器"""
                global crawler_status, should_stop_scheduler
                
                crawler_status['scheduler_active'] = True
                interval_minutes = 30  # 30分鐘間隔
                
                while not should_stop_scheduler:
                    try:
                        if crawler_status['auto_mode'] and not crawler_status['is_running']:
                            logger.info("執行自動爬蟲任務")
                            
                            # 觸發爬蟲（簡化版本）
                            crawler_status['is_running'] = True
                            time.sleep(3)  # 模擬執行時間
                            crawler_status['is_running'] = False
                            crawler_status['successful_crawls'] += 1
                            crawler_status['total_crawls'] += 1
                            crawler_status['last_run_time'] = datetime.now(timezone.utc).isoformat()
                            
                            logger.info("自動爬蟲任務完成")
                        
                        # 等待間隔時間，每30秒檢查一次停止信號
                        for _ in range(interval_minutes * 2):  # 30分鐘 = 60 * 30秒
                            if should_stop_scheduler:
                                break
                            time.sleep(30)
                            
                    except Exception as e:
                        logger.error(f"自動爬蟲執行失敗: {e}")
                        time.sleep(60)  # 出錯後等待1分鐘
                
                crawler_status['scheduler_active'] = False
                logger.info("自動排程器已停止")
            
            auto_scheduler_thread = threading.Thread(target=auto_scheduler, daemon=True)
            auto_scheduler_thread.start()
            
        elif not enable_auto:
            # 停用自動模式
            should_stop_scheduler = True
            crawler_status['scheduler_active'] = False
        
        status_text = "啟用" if enable_auto else "停用"
        return jsonify({
            'status': 'success',
            'message': f'自動模式已{status_text}',
            'auto_mode': crawler_status['auto_mode'],
            'scheduler_active': crawler_status['scheduler_active']
        })
        
    except Exception as e:
        logger.error(f"切換自動模式失敗: {e}")
        return jsonify({
            'status': 'error',
            'message': f'切換自動模式失敗: {str(e)}'
        }), 500

@crawler_api_bp.route('/crawler/sources')
def get_crawler_sources():
    """獲取爬蟲來源列表"""
    try:
        # 模擬爬蟲來源數據
        sources = [
            {
                'id': 1,
                'name': '工商時報保險版',
                'url': 'https://ctee.com.tw/category/finance/insurance',
                'status': 'active',
                'type': 'web_scraper',
                'last_crawl': (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                'success_rate': 95.2,
                'total_news': 1247,
                'avg_duration': 45.6,
                'last_error': None
            },
            {
                'id': 2,
                'name': '經濟日報保險',
                'url': 'https://money.udn.com/money/cate/10846',
                'status': 'active',
                'type': 'web_scraper',
                'last_crawl': (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                'success_rate': 88.7,
                'total_news': 892,
                'avg_duration': 38.2,
                'last_error': None
            },
            {
                'id': 3,
                'name': 'RSS聚合器',
                'url': 'multiple_rss_feeds',
                'status': 'error',
                'type': 'rss_feed',
                'last_crawl': (datetime.now(timezone.utc) - timedelta(minutes=45)).isoformat(),
                'success_rate': 45.3,
                'total_news': 234,
                'avg_duration': 12.8,
                'last_error': '連接超時'
            },
            {
                'id': 4,
                'name': '模擬新聞生成器',
                'url': 'internal://mock_generator',
                'status': 'active',
                'type': 'mock_generator',
                'last_crawl': (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
                'success_rate': 100.0,
                'total_news': 456,
                'avg_duration': 2.1,
                'last_error': None
            }
        ]
        
        return jsonify({
            'status': 'success',
            'data': sources
        })
        
    except Exception as e:
        logger.error(f"獲取爬蟲來源失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '獲取爬蟲來源失敗'
        }), 500

@crawler_api_bp.route('/crawler/logs')
def get_crawler_logs():
    """獲取爬蟲執行日誌"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        source_id = request.args.get('source_id', type=int)
        
        # 模擬日誌數據
        now = datetime.now(timezone.utc)
        logs = []
        
        for i in range(per_page):
            timestamp = now - timedelta(minutes=i*15)
            success = i % 4 != 2  # 75%成功率
            
            logs.append({
                'id': i + 1,
                'source_name': ['工商時報保險版', '經濟日報保險', 'RSS聚合器', '模擬生成器'][i % 4],
                'source_id': (i % 4) + 1,
                'success': success,
                'start_time': timestamp.isoformat(),
                'duration': round(30 + i * 2.5, 1),
                'news_found': 15 - i if success else 0,
                'news_new': 8 - i//2 if success else 0,
                'news_updated': 2 if success else 0,
                'error_message': None if success else '連接失敗',
                'error_type': None if success else 'NetworkError'
            })
        
        # 模擬分頁資訊
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': 500,
            'pages': 25,
            'has_next': page < 25,
            'has_prev': page > 1
        }
        
        return jsonify({
            'status': 'success',
            'data': {
                'logs': logs,
                'pagination': pagination
            }
        })
        
    except Exception as e:
        logger.error(f"獲取爬蟲日誌失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '獲取爬蟲日誌失敗'
        }), 500

@crawler_api_bp.route('/crawler/health')
def get_crawler_health():
    """獲取爬蟲健康狀態"""
    try:
        global crawler_status
        
        # 計算健康分數
        total_crawls = crawler_status['total_crawls']
        success_rate = (crawler_status['successful_crawls'] / max(total_crawls, 1)) * 100
        
        # 判斷健康狀態
        if success_rate >= 90:
            health_status = 'excellent'
            health_color = '#28a745'
        elif success_rate >= 75:
            health_status = 'good'
            health_color = '#17a2b8'
        elif success_rate >= 50:
            health_status = 'warning'
            health_color = '#ffc107'
        else:
            health_status = 'critical'
            health_color = '#dc3545'
        
        return jsonify({
            'status': 'success',
            'data': {
                'overall_health': health_status,
                'health_color': health_color,
                'success_rate': round(success_rate, 1),
                'total_crawls': total_crawls,
                'successful_crawls': crawler_status['successful_crawls'],
                'failed_crawls': crawler_status['failed_crawls'],
                'is_running': crawler_status['is_running'],
                'auto_mode': crawler_status['auto_mode'],
                'last_run': crawler_status['last_run_time'],
                'recommendations': [
                    '爬蟲運行正常' if success_rate >= 90 else '建議檢查失敗的爬蟲來源',
                    '自動模式已啟用' if crawler_status['auto_mode'] else '建議啟用自動模式以確保資料更新'
                ]
            }
        })
        
    except Exception as e:
        logger.error(f"獲取爬蟲健康狀態失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '獲取爬蟲健康狀態失敗'
        }), 500

@crawler_api_bp.route('/crawler/test', methods=['POST'])
def test_crawler():
    """測試爬蟲連線"""
    try:
        data = request.get_json() or {}
        source_id = data.get('source_id')
        
        if not source_id:
            return jsonify({
                'status': 'error',
                'message': '請提供要測試的來源ID'
            }), 400
        
        # 模擬測試結果
        time.sleep(1)  # 模擬測試時間
        
        test_results = {
            1: {'success': True, 'message': '工商時報保險版連線正常', 'response_time': 1.2},
            2: {'success': True, 'message': '經濟日報保險連線正常', 'response_time': 0.8},
            3: {'success': False, 'message': 'RSS聚合器連線失敗：超時', 'response_time': 5.0},
            4: {'success': True, 'message': '模擬生成器運作正常', 'response_time': 0.1}
        }
        
        result = test_results.get(source_id, {
            'success': False, 
            'message': '未知來源', 
            'response_time': 0
        })
        
        return jsonify({
            'status': 'success',
            'data': {
                'source_id': source_id,
                'test_success': result['success'],
                'message': result['message'],
                'response_time': result['response_time'],
                'test_time': datetime.now(timezone.utc).isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"測試爬蟲失敗: {e}")
        return jsonify({
            'status': 'error',
            'message': f'測試爬蟲失敗: {str(e)}'
        }), 500

# 健康檢查端點
@crawler_api_bp.route('/health')
def health_check():
    """API健康檢查"""
    return jsonify({
        'status': 'ok',
        'service': 'crawler_api',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': '1.0.0'
    })
