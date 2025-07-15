"""
併發處理優化模塊
Concurrent Processing Optimization

提供請求處理的併發優化功能，改進系統效能
"""

import threading
import queue
import concurrent.futures
import time
import logging
import functools
import asyncio
from flask import current_app, g, request
from werkzeug.local import Local, LocalProxy
from contextlib import contextmanager

# 設置日誌
logger = logging.getLogger('optimization.concurrency')

# 創建執行緒池
task_executor = concurrent.futures.ThreadPoolExecutor(
    max_workers=10,
    thread_name_prefix="TaskExecutor"
)

# 創建背景作業佇列
background_queue = queue.Queue()
background_workers = []
WORKER_COUNT = 3
STOP_SIGNAL = object()  # 用於停止工作執行緒的信號

class TaskManager:
    """任務管理器"""
    
    def __init__(self, max_workers=10):
        """初始化
        
        Args:
            max_workers: 最大工作執行緒數
        """
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="TaskManager"
        )
        self.active_tasks = {}
        self.lock = threading.RLock()
        self.metrics = {
            'submitted': 0,
            'completed': 0,
            'failed': 0,
            'average_time': 0.0
        }
    
    def submit(self, task_id, func, *args, **kwargs):
        """提交任務
        
        Args:
            task_id: 任務ID
            func: 要執行的函數
            *args, **kwargs: 函數參數
            
        Returns:
            Future對象
        """
        with self.lock:
            future = self.executor.submit(self._wrapped_task, task_id, func, *args, **kwargs)
            self.active_tasks[task_id] = {
                'future': future,
                'start_time': time.time(),
                'func_name': func.__name__
            }
            self.metrics['submitted'] += 1
            return future
    
    def _wrapped_task(self, task_id, func, *args, **kwargs):
        """包裝任務函數，用於收集指標
        
        Args:
            task_id: 任務ID
            func: 要執行的函數
            *args, **kwargs: 函數參數
            
        Returns:
            函數執行結果
        """
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            with self.lock:
                task_time = time.time() - start_time
                self.metrics['completed'] += 1
                self.metrics['average_time'] = (
                    (self.metrics['average_time'] * (self.metrics['completed'] - 1) + task_time) / 
                    self.metrics['completed']
                )
                self.active_tasks.pop(task_id, None)
            return result
        except Exception as e:
            logger.error(f"任務執行失敗 {task_id}: {e}")
            with self.lock:
                self.metrics['failed'] += 1
                self.active_tasks.pop(task_id, None)
            raise
    
    def wait_for(self, task_id, timeout=None):
        """等待指定任務完成
        
        Args:
            task_id: 任務ID
            timeout: 超時時間（秒）
            
        Returns:
            任務結果
        """
        with self.lock:
            if task_id not in self.active_tasks:
                return None
            future = self.active_tasks[task_id]['future']
        
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            logger.warning(f"任務等待超時 {task_id}")
            return None
        except Exception as e:
            logger.error(f"任務執行出錯 {task_id}: {e}")
            return None
    
    def cancel_task(self, task_id):
        """取消任務
        
        Args:
            task_id: 任務ID
            
        Returns:
            是否取消成功
        """
        with self.lock:
            if task_id not in self.active_tasks:
                return False
            
            future = self.active_tasks[task_id]['future']
            cancelled = future.cancel()
            
            if cancelled:
                self.active_tasks.pop(task_id, None)
            
            return cancelled
    
    def get_active_tasks(self):
        """獲取所有活躍任務
        
        Returns:
            活躍任務字典
        """
        with self.lock:
            active_tasks = {}
            for task_id, task_info in self.active_tasks.items():
                elapsed = time.time() - task_info['start_time']
                active_tasks[task_id] = {
                    'func_name': task_info['func_name'],
                    'elapsed': elapsed
                }
            return active_tasks
    
    def get_metrics(self):
        """獲取任務指標
        
        Returns:
            任務指標字典
        """
        with self.lock:
            metrics = dict(self.metrics)
            metrics['active_count'] = len(self.active_tasks)
            return metrics
    
    def shutdown(self):
        """關閉任務管理器"""
        self.executor.shutdown(wait=False)

# 創建全域任務管理器
task_manager = TaskManager()

def init_background_workers():
    """初始化背景工作執行緒"""
    global background_workers
    
    # 停止所有現有工作執行緒
    stop_background_workers()
    
    # 創建新的工作執行緒
    background_workers = []
    for i in range(WORKER_COUNT):
        worker = threading.Thread(
            target=background_worker_loop,
            args=(i,),
            daemon=True,
            name=f"BackgroundWorker-{i}"
        )
        worker.start()
        background_workers.append(worker)
        logger.info(f"已啟動背景工作執行緒 {i}")
    
    logger.info(f"已初始化 {WORKER_COUNT} 個背景工作執行緒")

def background_worker_loop(worker_id):
    """背景工作執行緒循環
    
    Args:
        worker_id: 工作執行緒ID
    """
    logger.info(f"背景工作執行緒 {worker_id} 已啟動")
    
    while True:
        try:
            # 從佇列中取出任務
            job = background_queue.get()
            
            # 檢查是否為停止信號
            if job is STOP_SIGNAL:
                logger.info(f"背景工作執行緒 {worker_id} 收到停止信號")
                background_queue.task_done()
                break
            
            # 執行任務
            func, args, kwargs = job
            try:
                start_time = time.time()
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.debug(f"背景任務 {func.__name__} 完成，耗時 {duration:.3f}s")
            except Exception as e:
                logger.error(f"背景任務執行失敗: {e}")
            
            # 標記任務完成
            background_queue.task_done()
            
        except Exception as e:
            logger.error(f"背景工作執行緒 {worker_id} 發生錯誤: {e}")

def stop_background_workers():
    """停止所有背景工作執行緒"""
    global background_workers
    
    if not background_workers:
        return
    
    # 發送停止信號
    for _ in background_workers:
        background_queue.put(STOP_SIGNAL)
    
    # 等待所有工作執行緒結束
    for worker in background_workers:
        worker.join(timeout=5.0)
    
    background_workers = []
    logger.info("所有背景工作執行緒已停止")

def run_in_background(func):
    """裝飾器：在背景執行函數
    
    Args:
        func: 要裝飾的函數
        
    Returns:
        包裝後的函數
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        background_queue.put((func, args, kwargs))
        return True
    return wrapper

def run_task(func):
    """裝飾器：作為任務執行函數
    
    Args:
        func: 要裝飾的函數
        
    Returns:
        包裝後的函數
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        import uuid
        task_id = str(uuid.uuid4())
        return task_manager.submit(task_id, func, *args, **kwargs)
    return wrapper

def limit_concurrency(max_concurrent=10):
    """裝飾器：限制函數的併發執行數量
    
    Args:
        max_concurrent: 最大併發數
        
    Returns:
        裝飾器函數
    """
    semaphore = threading.BoundedSemaphore(max_concurrent)
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with semaphore:
                return func(*args, **kwargs)
        return wrapper
    return decorator

def rate_limit(requests_per_minute=60):
    """裝飾器：限制函數的呼叫頻率
    
    Args:
        requests_per_minute: 每分鐘允許的請求數
        
    Returns:
        裝飾器函數
    """
    interval = 60.0 / requests_per_minute
    last_called = {}
    lock = threading.RLock()
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                now = time.time()
                key = func.__name__
                
                if key in last_called:
                    time_since_last = now - last_called[key]
                    if time_since_last < interval:
                        # 需要等待
                        sleep_time = interval - time_since_last
                        time.sleep(sleep_time)
                
                last_called[key] = time.time()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def retry(max_attempts=3, backoff_factor=0.5):
    """裝飾器：在失敗時重試函數
    
    Args:
        max_attempts: 最大嘗試次數
        backoff_factor: 退避因子
        
    Returns:
        裝飾器函數
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(f"達到最大重試次數 {max_attempts}，放棄: {e}")
                        raise
                    
                    # 計算等待時間
                    wait_time = backoff_factor * (2 ** (attempt - 1))
                    logger.warning(f"操作失敗，第 {attempt} 次重試，等待 {wait_time:.2f}s: {e}")
                    time.sleep(wait_time)
        return wrapper
    return decorator

def timeout(seconds):
    """裝飾器：限制函數的執行時間
    
    Args:
        seconds: 超時時間（秒）
        
    Returns:
        裝飾器函數
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = [None]
            exception = [None]
            
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(seconds)
            
            if thread.is_alive():
                raise TimeoutError(f"函數 {func.__name__} 執行超過 {seconds} 秒")
            
            if exception[0] is not None:
                raise exception[0]
            
            return result[0]
        return wrapper
    return decorator

def init_flask_concurrency(app):
    """為Flask應用初始化並發處理
    
    Args:
        app: Flask應用實例
    """
    # 初始化背景工作執行緒
    init_background_workers()
    
    # 在關閉時停止工作執行緒
    @app.teardown_appcontext
    def cleanup(exception=None):
        """關閉前清理"""
        pass
    
    # 提供任務管理器和背景佇列的訪問
    @app.before_request
    def before_request():
        """請求前處理"""
        g.task_manager = task_manager
    
    # 添加路由以獲取系統狀態
    @app.route('/monitor/api/system/concurrency', methods=['GET'])
    def concurrency_status():
        """併發處理狀態API"""
        if not current_app.config.get('DEBUG'):
            return {
                'status': 'disabled',
                'message': '僅在調試模式下可用'
            }, 403
        
        metrics = task_manager.get_metrics()
        active_tasks = task_manager.get_active_tasks()
        background_size = background_queue.qsize()
        
        return {
            'status': 'success',
            'data': {
                'task_metrics': metrics,
                'active_tasks': active_tasks,
                'background_queue': background_size,
                'background_workers': len(background_workers)
            }
        }
    
    logger.info("Flask並發處理優化已初始化")

def main():
    """主函數"""
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/concurrency.log'),
            logging.StreamHandler()
        ]
    )
    
    logger.info("啟動併發處理優化")
    
    # 初始化背景工作執行緒
    init_background_workers()
    
    # 初始化Flask應用
    try:
        from app import create_app
        from config.settings import Config
        
        app = create_app(Config)
        
        with app.app_context():
            init_flask_concurrency(app)
            logger.info("併發處理優化已完成")
    except ImportError:
        logger.warning("未找到Flask應用，跳過初始化")
    
    return {
        'status': 'success',
        'background_workers': len(background_workers),
        'task_metrics': task_manager.get_metrics()
    }

if __name__ == "__main__":
    main()
