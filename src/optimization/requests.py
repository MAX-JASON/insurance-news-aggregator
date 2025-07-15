"""
請求處理優化器
Request Processing Optimizer

優化和管理API請求處理的模塊
"""

from flask import request, current_app, g
import time
import functools
import threading
import re
import json
import logging
from werkzeug.contrib.cache import SimpleCache
from collections import defaultdict, deque
from datetime import datetime, timedelta
import pickle

# 導入併發處理工具
from src.optimization.concurrency import limit_concurrency, rate_limit, retry, timeout

# 設置日誌
logger = logging.getLogger('optimization.requests')

# 請求緩存
request_cache = SimpleCache(threshold=1000, default_timeout=300)

# 請求計數和統計
class RequestStats:
    """請求統計"""
    def __init__(self, window_size=60):
        """初始化請求統計
        
        Args:
            window_size: 統計窗口大小（秒）
        """
        self.lock = threading.RLock()
        self.window_size = window_size
        self.endpoints = defaultdict(lambda: {
            'total': 0,
            'success': 0,
            'errors': 0,
            'times': deque(maxlen=1000)
        })
        self.requests_timeline = deque(maxlen=window_size * 10)  # 每0.1秒的請求數
        self.last_cleanup = time.time()
    
    def record_request(self, endpoint, duration, status_code):
        """記錄請求
        
        Args:
            endpoint: 端點路徑
            duration: 處理時間（秒）
            status_code: 狀態碼
        """
        with self.lock:
            stats = self.endpoints[endpoint]
            stats['total'] += 1
            if status_code < 400:
                stats['success'] += 1
            else:
                stats['errors'] += 1
            stats['times'].append(duration)
            
            # 記錄時間線
            now = time.time()
            self.requests_timeline.append((now, endpoint))
            
            # 清理舊數據
            if now - self.last_cleanup > 10:
                self._cleanup(now)
                self.last_cleanup = now
    
    def _cleanup(self, now):
        """清理過期數據
        
        Args:
            now: 當前時間戳
        """
        cutoff = now - self.window_size
        while self.requests_timeline and self.requests_timeline[0][0] < cutoff:
            self.requests_timeline.popleft()
    
    def get_request_rate(self):
        """獲取請求速率
        
        Returns:
            每秒請求數
        """
        with self.lock:
            now = time.time()
            cutoff = now - self.window_size
            count = sum(1 for ts, _ in self.requests_timeline if ts > cutoff)
            return count / self.window_size if self.window_size > 0 else 0
    
    def get_stats(self):
        """獲取統計數據
        
        Returns:
            統計數據字典
        """
        with self.lock:
            stats = {}
            now = time.time()
            self._cleanup(now)
            
            # 全局統計
            total_requests = len(self.requests_timeline)
            request_rate = self.get_request_rate()
            
            # 端點統計
            endpoints = {}
            for endpoint, data in self.endpoints.items():
                if data['total'] > 0:
                    avg_time = sum(data['times']) / len(data['times']) if data['times'] else 0
                    endpoints[endpoint] = {
                        'total': data['total'],
                        'success': data['success'],
                        'errors': data['errors'],
                        'avg_time': avg_time
                    }
            
            return {
                'global': {
                    'total_requests': total_requests,
                    'request_rate': request_rate
                },
                'endpoints': endpoints
            }

# 創建全局請求統計實例
request_stats = RequestStats()

def init_request_optimizer(app):
    """初始化請求優化
    
    Args:
        app: Flask應用實例
    """
    # 請求前處理
    @app.before_request
    def before_request():
        """請求前處理"""
        # 記錄開始時間
        g.start_time = time.time()
        
        # 檢查是否需要限速
        if should_rate_limit(request):
            client_ip = get_client_ip()
            if not check_rate_limit(client_ip):
                logger.warning(f"請求頻率限制：{client_ip}")
                return {"error": "請求過於頻繁，請稍後再試"}, 429
    
    # 請求後處理
    @app.after_request
    def after_request(response):
        """請求後處理
        
        Args:
            response: Flask響應對象
            
        Returns:
            Flask響應對象
        """
        # 計算請求處理時間
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            # 記錄請求統計
            endpoint = request.endpoint or request.path
            request_stats.record_request(endpoint, duration, response.status_code)
            
            # 添加處理時間到響應頭
            response.headers['X-Processing-Time'] = str(duration)
        
        return response
    
    # 添加路由以獲取請求統計
    @app.route('/monitor/api/system/requests', methods=['GET'])
    def request_stats_api():
        """請求統計API"""
        if not current_app.config.get('DEBUG'):
            return {
                'status': 'disabled',
                'message': '僅在調試模式下可用'
            }, 403
        
        stats = request_stats.get_stats()
        return {
            'status': 'success',
            'data': stats
        }
    
    logger.info("Flask請求處理優化已初始化")

def cached_response(timeout=300, key_prefix='view'):
    """裝飾器：緩存響應
    
    Args:
        timeout: 緩存超時時間（秒）
        key_prefix: 緩存鍵前綴
        
    Returns:
        裝飾器函數
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # 跳過非GET請求
            if request.method != 'GET':
                return f(*args, **kwargs)
            
            # 生成緩存鍵
            cache_key = f"{key_prefix}:{request.path}:{hash(frozenset(request.args.items()))}"
            
            # 嘗試從緩存獲取
            rv = request_cache.get(cache_key)
            if rv is not None:
                return rv
            
            # 執行函數
            rv = f(*args, **kwargs)
            
            # 存入緩存
            request_cache.set(cache_key, rv, timeout=timeout)
            return rv
        return decorated_function
    return decorator

def get_client_ip():
    """獲取客戶端IP
    
    Returns:
        客戶端IP地址
    """
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr

# IP請求頻率限制
class RateLimiter:
    """IP請求頻率限制器"""
    def __init__(self, limit=60, window=60):
        """初始化
        
        Args:
            limit: 窗口期內最大請求數
            window: 窗口期大小（秒）
        """
        self.limit = limit
        self.window = window
        self.clients = {}
        self.lock = threading.RLock()
    
    def check(self, client_ip):
        """檢查客戶端是否超過限制
        
        Args:
            client_ip: 客戶端IP
            
        Returns:
            布爾值，True表示允許請求
        """
        with self.lock:
            now = time.time()
            
            # 清理過期數據
            if client_ip in self.clients:
                self.clients[client_ip] = [ts for ts in self.clients[client_ip] if now - ts < self.window]
            else:
                self.clients[client_ip] = []
            
            # 檢查請求數
            if len(self.clients[client_ip]) >= self.limit:
                return False
            
            # 記錄請求
            self.clients[client_ip].append(now)
            return True
    
    def get_client_status(self, client_ip):
        """獲取客戶端狀態
        
        Args:
            client_ip: 客戶端IP
            
        Returns:
            狀態字典
        """
        with self.lock:
            now = time.time()
            if client_ip not in self.clients:
                return {
                    'count': 0,
                    'limit': self.limit,
                    'remaining': self.limit,
                    'reset': now + self.window
                }
            
            # 清理過期請求
            self.clients[client_ip] = [ts for ts in self.clients[client_ip] if now - ts < self.window]
            count = len(self.clients[client_ip])
            
            # 計算重置時間
            if count > 0:
                oldest = min(self.clients[client_ip])
                reset = oldest + self.window
            else:
                reset = now + self.window
            
            return {
                'count': count,
                'limit': self.limit,
                'remaining': max(0, self.limit - count),
                'reset': reset
            }

# 創建全局限速器
rate_limiter = RateLimiter()

def check_rate_limit(client_ip):
    """檢查IP頻率限制
    
    Args:
        client_ip: 客戶端IP
        
    Returns:
        布爾值，True表示允許請求
    """
    return rate_limiter.check(client_ip)

def should_rate_limit(req):
    """檢查請求是否需要限速
    
    Args:
        req: Flask請求對象
        
    Returns:
        布爾值，True表示需要限速
    """
    # 本地請求不限速
    if req.remote_addr == '127.0.0.1':
        return False
    
    # API端點需要限速
    if req.path.startswith('/api/'):
        return True
    
    # 監控API不限速
    if req.path.startswith('/monitor/api/'):
        return False
    
    # 默認不限速
    return False

def compress_response(f):
    """裝飾器：壓縮響應
    
    Args:
        f: 要裝飾的函數
        
    Returns:
        包裝後的函數
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        
        # 檢查是否已經是壓縮格式
        if response.content_encoding is not None:
            return response
        
        # 檢查客戶端是否支持gzip
        accept_encoding = request.headers.get('Accept-Encoding', '')
        if 'gzip' not in accept_encoding.lower():
            return response
        
        # 檢查內容類型
        content_type = response.content_type or ''
        if not (content_type.startswith('text/') or 
                content_type == 'application/json' or
                content_type == 'application/javascript'):
            return response
        
        # 壓縮響應
        import gzip
        import io
        
        response.direct_passthrough = False
        
        if hasattr(response, 'data') and response.data:
            buffer = io.BytesIO()
            with gzip.GzipFile(mode='wb', fileobj=buffer) as gz:
                if isinstance(response.data, str):
                    gz.write(response.data.encode('utf-8'))
                else:
                    gz.write(response.data)
            
            response.data = buffer.getvalue()
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = len(response.data)
            
        return response
    
    return decorated_function

def optimize_api_endpoint(rate_limit_per_minute=60, cache_timeout=0, compress=True):
    """裝飾器：優化API端點
    
    Args:
        rate_limit_per_minute: 每分鐘請求限制數
        cache_timeout: 緩存超時時間（秒），0表示不緩存
        compress: 是否壓縮響應
        
    Returns:
        裝飾器函數
    """
    def decorator(f):
        # 應用頻率限制
        if rate_limit_per_minute > 0:
            f = rate_limit(rate_limit_per_minute)(f)
        
        # 應用緩存
        if cache_timeout > 0:
            f = cached_response(timeout=cache_timeout)(f)
        
        # 應用壓縮
        if compress:
            f = compress_response(f)
        
        # 應用限制併發
        f = limit_concurrency(max_concurrent=20)(f)
        
        # 應用超時
        f = timeout(10)(f)
        
        return f
    return decorator

def main():
    """主函數"""
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/requests.log'),
            logging.StreamHandler()
        ]
    )
    
    logger.info("啟動請求處理優化")
    
    # 初始化Flask應用
    try:
        from app import create_app
        from config.settings import Config
        
        app = create_app(Config)
        
        with app.app_context():
            init_request_optimizer(app)
            logger.info("請求處理優化已完成")
    except ImportError:
        logger.warning("未找到Flask應用，跳過初始化")
    
    return {
        'status': 'success',
        'rate_limiter': {
            'limit': rate_limiter.limit,
            'window': rate_limiter.window
        },
        'request_stats': request_stats.get_stats()
    }

if __name__ == "__main__":
    main()
