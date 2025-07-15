"""
分析結果快取系統
Analysis Result Cache System

提供新聞分析結果的快取功能，提升系統效能
"""

import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from functools import wraps
import pickle
import os
from pathlib import Path

logger = logging.getLogger('analyzer.cache')

class AnalysisCache:
    """分析結果快取管理器"""
    
    def __init__(self, cache_dir: str = "cache", ttl_hours: int = 24, memory_cache_size: int = 500):
        """
        初始化快取系統
        
        Args:
            cache_dir: 快取檔案目錄
            ttl_hours: 快取生存時間（小時）
            memory_cache_size: 記憶體快取大小（項目數）
        """
        # 檔案快取設定
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        
        # 記憶體快取設定
        self.memory_cache_size = memory_cache_size
        self.memory_cache = {}  # 格式: {(category, key): (data, timestamp)}
        self.memory_cache_hits = 0
        self.memory_cache_misses = 0
        self.file_cache_hits = 0
        self.file_cache_misses = 0
        
        # 建立子目錄
        for category in ['analysis', 'importance', 'keywords', 'sentiment', 'trends', 'recommendations']:
            (self.cache_dir / category).mkdir(exist_ok=True)
        
        logger.info(f"✅ 分析快取系統初始化完成，目錄: {self.cache_dir}，記憶體快取大小: {memory_cache_size}")
    
    def _get_cache_key(self, data: Any) -> str:
        """
        產生快取鍵值
        
        Args:
            data: 要快取的數據
            
        Returns:
            MD5 雜湊鍵值
        """
        # 預處理包含datetime的數據
        data = self._preprocess_for_json(data)
        
        if isinstance(data, dict):
            # 對字典排序後序列化
            sorted_data = json.dumps(data, sort_keys=True, ensure_ascii=False)
        elif isinstance(data, str):
            sorted_data = data
        else:
            sorted_data = str(data)
        
        return hashlib.md5(sorted_data.encode('utf-8')).hexdigest()
        
    def _preprocess_for_json(self, data: Any) -> Any:
        """處理包含datetime的數據以便JSON序列化"""
        from datetime import datetime
        
        if isinstance(data, datetime):
            # 將datetime轉換為ISO格式字符串
            return data.isoformat()
        elif isinstance(data, dict):
            # 遞歸處理字典
            return {k: self._preprocess_for_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            # 遞歸處理列表
            return [self._preprocess_for_json(item) for item in data]
        elif isinstance(data, tuple):
            # 處理元組
            return tuple(self._preprocess_for_json(item) for item in data)
        else:
            # 其他類型直接返回
            return data
    
    def _get_cache_path(self, category: str, key: str) -> Path:
        """取得快取檔案路徑"""
        return self.cache_dir / category / f"{key}.cache"
    
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """檢查快取是否仍然有效"""
        if not cache_path.exists():
            return False
        
        # 檢查檔案修改時間
        file_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        return datetime.now() - file_time < self.ttl
    
    def get(self, category: str, key: str) -> Optional[Dict[str, Any]]:
        """
        從快取中取得資料
        
        Args:
            category: 快取分類 (analysis, keywords, sentiment, trends)
            key: 快取鍵值
            
        Returns:
            快取的資料，如果不存在或過期則返回 None
        """
        try:
            # 1. 先檢查記憶體快取
            cache_key = (category, key)
            if cache_key in self.memory_cache:
                data, timestamp = self.memory_cache[cache_key]
                if datetime.now() - timestamp < self.ttl:
                    self.memory_cache_hits += 1
                    logger.debug(f"✅ 記憶體快取命中: {category}/{key}")
                    return data
                else:
                    # 過期項目從記憶體中移除
                    del self.memory_cache[cache_key]
            
            self.memory_cache_misses += 1
            
            # 2. 檢查檔案快取
            cache_path = self._get_cache_path(category, key)
            
            if not self._is_cache_valid(cache_path):
                self.file_cache_misses += 1
                return None
            
            with open(cache_path, 'rb') as f:
                cached_data = pickle.load(f)
            
            # 加入記憶體快取
            self._add_to_memory_cache(category, key, cached_data)
            
            self.file_cache_hits += 1
            logger.debug(f"✅ 檔案快取命中: {category}/{key}")
            return cached_data
            
        except Exception as e:
            logger.debug(f"❌ 讀取快取失敗: {category}/{key} - {e}")
            return None
    
    def _add_to_memory_cache(self, category: str, key: str, data: Dict[str, Any]) -> None:
        """將資料加入記憶體快取"""
        cache_key = (category, key)
        
        # 如果記憶體快取已滿，移除最舊的項目
        if len(self.memory_cache) >= self.memory_cache_size:
            # 簡單的 LRU 策略：移除第一個項目
            oldest_key = next(iter(self.memory_cache))
            del self.memory_cache[oldest_key]
        
        # 加入新項目
        self.memory_cache[cache_key] = (data, datetime.now())
    
    def set(self, category: str, key: str, data: Dict[str, Any]) -> bool:
        """
        將資料存入快取
        
        Args:
            category: 快取分類
            key: 快取鍵值
            data: 要快取的資料
            
        Returns:
            是否成功存入
        """
        try:
            # 1. 存入記憶體快取
            self._add_to_memory_cache(category, key, data)
            
            # 2. 存入檔案快取
            cache_path = self._get_cache_path(category, key)
            
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            
            logger.debug(f"✅ 資料已快取: {category}/{key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 快取寫入失敗: {category}/{key} - {e}")
            return False
    
    def delete(self, category: str, key: str) -> bool:
        """
        刪除特定快取
        
        Args:
            category: 快取分類
            key: 快取鍵值
            
        Returns:
            是否成功刪除
        """
        try:
            # 1. 從記憶體快取中刪除
            cache_key = (category, key)
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]
            
            # 2. 從檔案快取中刪除
            cache_path = self._get_cache_path(category, key)
            if cache_path.exists():
                cache_path.unlink()
                logger.debug(f"✅ 快取已刪除: {category}/{key}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ 快取刪除失敗: {category}/{key} - {e}")
            return False
    
    def clear_category(self, category: str) -> int:
        """
        清空特定分類的所有快取
        
        Args:
            category: 快取分類
            
        Returns:
            刪除的檔案數量
        """
        try:
            # 1. 清空記憶體快取中的該分類項目
            keys_to_remove = [k for k in self.memory_cache.keys() if k[0] == category]
            for key in keys_to_remove:
                del self.memory_cache[key]
            
            # 2. 清空檔案快取
            category_dir = self.cache_dir / category
            if not category_dir.exists():
                return 0
            
            count = 0
            for cache_file in category_dir.glob("*.cache"):
                cache_file.unlink()
                count += 1
            
            logger.info(f"✅ 已清空 {category} 快取，刪除 {count} 個檔案")
            return count
            
        except Exception as e:
            logger.error(f"❌ 清空快取失敗: {category} - {e}")
            return 0
    
    def clear_expired(self) -> int:
        """
        清理過期的快取
        
        Returns:
            刪除的檔案數量
        """
        try:
            # 1. 清理記憶體快取
            now = datetime.now()
            keys_to_remove = []
            for k, (_, timestamp) in self.memory_cache.items():
                if now - timestamp >= self.ttl:
                    keys_to_remove.append(k)
            
            for key in keys_to_remove:
                del self.memory_cache[key]
            
            memory_count = len(keys_to_remove)
            logger.debug(f"✅ 已清理 {memory_count} 個過期記憶體快取項目")
            
            # 2. 清理檔案快取
            file_count = 0
            for cache_file in self.cache_dir.rglob("*.cache"):
                if not self._is_cache_valid(cache_file):
                    cache_file.unlink()
                    file_count += 1
            
            logger.info(f"✅ 已清理 {memory_count} 個記憶體快取項目和 {file_count} 個過期快取檔案")
            return file_count + memory_count
            
        except Exception as e:
            logger.error(f"❌ 清理過期快取失敗: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        取得快取統計資訊
        
        Returns:
            快取統計資料
        """
        try:
            now = datetime.now()
            stats = {
                'categories': {},
                'total_files': 0,
                'total_size': 0,
                'expired_files': 0,
                'memory_cache': {
                    'total_items': len(self.memory_cache),
                    'max_size': self.memory_cache_size,
                    'usage_percent': len(self.memory_cache) / self.memory_cache_size * 100 if self.memory_cache_size > 0 else 0,
                    'hits': self.memory_cache_hits,
                    'misses': self.memory_cache_misses,
                    'hit_ratio': self.memory_cache_hits / (self.memory_cache_hits + self.memory_cache_misses) * 100 if (self.memory_cache_hits + self.memory_cache_misses) > 0 else 0,
                    'categories': {}
                },
                'file_cache': {
                    'hits': self.file_cache_hits,
                    'misses': self.file_cache_misses,
                    'hit_ratio': self.file_cache_hits / (self.file_cache_hits + self.file_cache_misses) * 100 if (self.file_cache_hits + self.file_cache_misses) > 0 else 0
                }
            }
            
            # 記憶體快取統計
            memory_categories = {}
            valid_memory_items = 0
            expired_memory_items = 0
            
            for (cat, _), (_, timestamp) in self.memory_cache.items():
                if cat not in memory_categories:
                    memory_categories[cat] = {'count': 0, 'expired': 0}
                
                memory_categories[cat]['count'] += 1
                
                if now - timestamp >= self.ttl:
                    memory_categories[cat]['expired'] += 1
                    expired_memory_items += 1
                else:
                    valid_memory_items += 1
            
            stats['memory_cache']['categories'] = memory_categories
            stats['memory_cache']['valid_items'] = valid_memory_items
            stats['memory_cache']['expired_items'] = expired_memory_items
            
            # 檔案快取統計
            for category_dir in self.cache_dir.iterdir():
                if category_dir.is_dir():
                    category_name = category_dir.name
                    cache_files = list(category_dir.glob("*.cache"))
                    
                    valid_files = 0
                    expired_files = 0
                    category_size = 0
                    
                    for cache_file in cache_files:
                        file_size = cache_file.stat().st_size
                        category_size += file_size
                        
                        if self._is_cache_valid(cache_file):
                            valid_files += 1
                        else:
                            expired_files += 1
                    
                    stats['categories'][category_name] = {
                        'valid_files': valid_files,
                        'expired_files': expired_files,
                        'total_files': len(cache_files),
                        'size_bytes': category_size,
                        'memory_items': memory_categories.get(category_name, {}).get('count', 0)
                    }
                    
                    stats['total_files'] += len(cache_files)
                    stats['total_size'] += category_size
                    stats['expired_files'] += expired_files
            
            # 計算整體效能
            total_hits = self.memory_cache_hits + self.file_cache_hits
            total_requests = total_hits + self.file_cache_misses
            
            stats['overall_hit_ratio'] = total_hits / total_requests * 100 if total_requests > 0 else 0
            stats['overall_performance'] = {
                'total_hits': total_hits,
                'total_misses': self.file_cache_misses,
                'total_requests': total_requests
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ 取得快取統計失敗: {e}")
            return {}

# 全域快取實例
_cache_instance = None

def get_cache() -> AnalysisCache:
    """取得全域快取實例"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = AnalysisCache()
    return _cache_instance

def cached_analysis(category: str = 'analysis', ttl_hours: int = None, skip_args: List[int] = None, skip_kwargs: List[str] = None):
    """
    分析結果快取裝飾器
    
    Args:
        category: 快取分類
        ttl_hours: 覆寫預設的快取生存時間（小時）
        skip_args: 要排除在快取鍵值計算外的位置參數索引列表
        skip_kwargs: 要排除在快取鍵值計算外的關鍵字參數名稱列表
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # 產生快取鍵值 (排除指定的參數)
            filtered_args = []
            
            # 特殊處理第一個參數（通常是 self），不包含在快取鍵值計算中
            if len(args) > 0:
                filtered_args = list(args[1:])  # 跳過第一個參數（self）
            
            if skip_args:
                for i in sorted(skip_args, reverse=True):
                    if i < len(filtered_args):
                        filtered_args[i] = '_SKIPPED_'
            
            filtered_kwargs = kwargs.copy()
            if skip_kwargs:
                for k in skip_kwargs:
                    if k in filtered_kwargs:
                        filtered_kwargs[k] = '_SKIPPED_'
            
            cache_data = {
                'func_name': func.__name__,
                'args': filtered_args,
                'kwargs': filtered_kwargs
            }
            cache_key = cache._get_cache_key(cache_data)
            
            # 嘗試從快取取得結果
            cached_result = cache.get(category, cache_key)
            if cached_result is not None:
                logger.debug(f"✅ 使用快取結果: {func.__name__}")
                return cached_result
            
            # 執行函數並快取結果
            result = func(*args, **kwargs)
            cache.set(category, cache_key, result)
            logger.debug(f"✅ 新增快取結果: {func.__name__}")
            
            return result
        
        return wrapper
    return decorator

def invalidate_cache(category: str = None, pattern: str = None):
    """
    無效化快取的裝飾器
    
    Args:
        category: 要清空的快取分類，如果為 None 則不清空任何分類
        pattern: 匹配要刪除的快取鍵值模式，如果為 None 則刪除整個分類
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # 執行函數
            result = func(*args, **kwargs)
            
            # 無效化快取
            if category:
                if pattern:
                    # 尋找匹配的鍵值刪除
                    keys_to_delete = []
                    category_path = cache.cache_dir / category
                    if category_path.exists():
                        for cache_file in category_path.glob("*.cache"):
                            if pattern in cache_file.name:
                                keys_to_delete.append(cache_file.stem)
                    
                    for key in keys_to_delete:
                        cache.delete(category, key)
                        
                    logger.debug(f"✅ 已無效化 {len(keys_to_delete)} 個快取項目: {category}/{pattern}")
                else:
                    # 清空整個分類
                    count = cache.clear_category(category)
                    logger.debug(f"✅ 已無效化分類 {category}，清除 {count} 個項目")
            
            return result
            
        return wrapper
    return decorator

if __name__ == "__main__":
    # 測試快取系統
    print("🧪 測試分析結果快取系統...")
    
    cache = AnalysisCache(cache_dir="test_cache", ttl_hours=1)
    
    # 測試基本操作
    test_data = {
        'sentiment': 'positive',
        'score': 0.8,
        'keywords': ['保險', '理賠', '服務']
    }
    
    # 存入快取
    cache.set('analysis', 'test_key', test_data)
    
    # 從快取讀取
    cached_data = cache.get('analysis', 'test_key')
    print(f"快取測試結果: {cached_data}")
    
    # 取得統計
    stats = cache.get_cache_stats()
    print(f"快取統計: {stats}")
    
    # 清理測試快取
    import shutil
    shutil.rmtree("test_cache")
    print("✅ 快取系統測試完成")
