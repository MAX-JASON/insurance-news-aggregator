"""
配置管理器
Configuration Manager

統一管理應用程序的配置參數，支持多環境配置切換和動態配置更新。
"""

import os
import yaml
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger('config')

class ConfigManager:
    """
    配置管理器類，用於統一管理應用配置
    """
    
    def __init__(self, default_config_path: str = None):
        """
        初始化配置管理器
        
        Args:
            default_config_path: 默認配置文件路徑
        """
        self._config = {}
        self._config_path = default_config_path or self._get_default_config_path()
        self._last_load_time = None
        self._auto_reload = False
        self._reload_interval = 300  # 默認5分鐘檢查一次配置更新
        
        # 初始化載入配置
        self.load_config()
    
    def _get_default_config_path(self) -> str:
        """
        獲取默認配置文件路徑
        
        Returns:
            str: 配置文件路徑
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 環境配置優先級: 環境變量 > 當前環境配置 > 默認配置
        env = os.environ.get('FLASK_ENV') or 'development'
        
        # 嘗試按優先順序載入配置
        config_paths = [
            os.path.join(base_dir, 'config', f'config.{env}.yaml'),
            os.path.join(base_dir, 'config', 'config.yaml'),
            os.path.join(base_dir, 'config', 'config.example.yaml')
        ]
        
        for path in config_paths:
            if os.path.exists(path):
                return path
        
        # 如果都找不到，返回默認路徑
        return os.path.join(base_dir, 'config', 'config.yaml')
    
    def load_config(self) -> bool:
        """
        載入配置文件
        
        Returns:
            bool: 是否成功載入
        """
        if not os.path.exists(self._config_path):
            logger.error(f"配置文件不存在: {self._config_path}")
            return False
        
        try:
            with open(self._config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
            
            logger.info(f"已成功載入配置: {self._config_path}")
            self._last_load_time = datetime.now()
            return True
        except Exception as e:
            logger.error(f"載入配置文件失敗: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        獲取配置值
        
        Args:
            key: 配置鍵名，支持點分隔的多級配置
            default: 未找到時的默認值
        
        Returns:
            配置值
        """
        # 检查是否需要自动重新加载
        self._check_reload()
        
        # 处理多级键名
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def _check_reload(self) -> None:
        """檢查並在必要時重新載入配置"""
        if not self._auto_reload or not self._last_load_time:
            return
        
        now = datetime.now()
        if (now - self._last_load_time).total_seconds() > self._reload_interval:
            # 檢查文件是否被修改
            if os.path.getmtime(self._config_path) > self._last_load_time.timestamp():
                logger.info("檢測到配置文件變更，重新載入")
                self.load_config()
    
    def set(self, key: str, value: Any) -> None:
        """
        設置配置值（僅在內存中）
        
        Args:
            key: 配置鍵名，支持點分隔的多級配置
            value: 配置值
        """
        keys = key.split('.')
        config = self._config
        
        # 導航到最後一級
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 設置值
        config[keys[-1]] = value
    
    def save(self, file_path: str = None) -> bool:
        """
        將當前配置保存到文件
        
        Args:
            file_path: 保存路徑，默認為當前配置路徑
        
        Returns:
            bool: 是否成功保存
        """
        save_path = file_path or self._config_path
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"已成功保存配置: {save_path}")
            return True
        except Exception as e:
            logger.error(f"保存配置文件失敗: {e}")
            return False
    
    def enable_auto_reload(self, enabled: bool = True, interval: int = 300) -> None:
        """
        啟用配置自動重載
        
        Args:
            enabled: 是否啟用
            interval: 檢查間隔（秒）
        """
        self._auto_reload = enabled
        self._reload_interval = interval
        
        status = "啟用" if enabled else "禁用"
        logger.info(f"配置自動重載已{status}, 檢查間隔: {interval}秒")
    
    def get_all(self) -> Dict[str, Any]:
        """
        獲取所有配置
        
        Returns:
            dict: 所有配置的副本
        """
        # 檢查是否需要自動重新載入
        self._check_reload()
        
        # 返回副本以防止外部修改
        return self._config.copy()
    
    def merge_config(self, config_dict: Dict[str, Any]) -> None:
        """
        合併配置
        
        Args:
            config_dict: 要合併的配置字典
        """
        def _merge(source, update):
            for key, value in update.items():
                if key in source and isinstance(source[key], dict) and isinstance(value, dict):
                    _merge(source[key], value)
                else:
                    source[key] = value
        
        _merge(self._config, config_dict)
        logger.info("已合併新配置")
    
    def load_json_config(self, json_path: str, section: str = None) -> bool:
        """
        載入JSON格式的配置文件
        
        Args:
            json_path: JSON配置文件路徑
            section: 配置應該合併到的部分，None表示合併到根配置
            
        Returns:
            bool: 是否成功載入
        """
        if not os.path.exists(json_path):
            logger.error(f"JSON配置文件不存在: {json_path}")
            return False
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json_config = json.load(f)
            
            if section:
                # 確保section部分存在
                if section not in self._config:
                    self._config[section] = {}
                
                # 合併到指定section
                self.merge_config({section: json_config})
            else:
                # 合併到根配置
                self.merge_config(json_config)
                
            logger.info(f"已成功載入JSON配置: {json_path}")
            return True
        except Exception as e:
            logger.error(f"載入JSON配置文件失敗: {e}")
            return False
    
    def reset(self) -> None:
        """重置配置到文件中的狀態"""
        self._config = {}
        self.load_config()
        logger.info("已重置配置到文件狀態")


# 創建全局配置管理器實例
config_manager = ConfigManager()

def get_config_manager() -> ConfigManager:
    """
    獲取配置管理器實例
    
    Returns:
        ConfigManager: 配置管理器實例
    """
    return config_manager