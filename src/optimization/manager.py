"""
優化管理器主控台
Optimization Manager Console

整合所有優化功能，提供統一管理介面
"""

import os
import sys
import time
import logging
import argparse
import threading
import importlib
import json
from pathlib import Path

# 設置基本路徑
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 添加路徑到系統路徑
sys.path.insert(0, str(BASE_DIR))

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'logs', 'optimization.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('optimization.manager')

class OptimizationManager:
    """優化管理器"""
    
    def __init__(self):
        """初始化管理器"""
        self.modules = {}
        self.status = {}
        self.running = False
        self.lock = threading.RLock()
    
    def load_module(self, module_name):
        """載入優化模塊
        
        Args:
            module_name: 模塊名稱
            
        Returns:
            布爾值，表示是否載入成功
        """
        try:
            if module_name in self.modules:
                return True
            
            # 導入模塊
            full_module_name = f"src.optimization.{module_name}"
            module = importlib.import_module(full_module_name)
            
            # 檢查模塊是否有main函數
            if not hasattr(module, 'main'):
                logger.error(f"模塊 {module_name} 沒有main函數")
                return False
            
            # 添加到模塊列表
            self.modules[module_name] = module
            self.status[module_name] = {
                'loaded': True,
                'running': False,
                'last_run': None,
                'results': None
            }
            
            logger.info(f"成功載入模塊 {module_name}")
            return True
        
        except ImportError as e:
            logger.error(f"載入模塊 {module_name} 失敗: {e}")
            return False
        except Exception as e:
            logger.error(f"載入模塊 {module_name} 時發生錯誤: {e}")
            return False
    
    def run_module(self, module_name):
        """運行優化模塊
        
        Args:
            module_name: 模塊名稱
            
        Returns:
            運行結果
        """
        with self.lock:
            # 檢查模塊是否已載入
            if module_name not in self.modules:
                if not self.load_module(module_name):
                    return {'status': 'error', 'message': f"模塊 {module_name} 載入失敗"}
            
            # 獲取模塊
            module = self.modules[module_name]
            
            # 更新狀態
            self.status[module_name]['running'] = True
            
            try:
                # 運行模塊的main函數
                results = module.main()
                
                # 更新狀態
                self.status[module_name]['running'] = False
                self.status[module_name]['last_run'] = time.time()
                self.status[module_name]['results'] = results
                
                logger.info(f"模塊 {module_name} 運行成功")
                return results
            
            except Exception as e:
                # 更新狀態
                self.status[module_name]['running'] = False
                self.status[module_name]['last_run'] = time.time()
                self.status[module_name]['error'] = str(e)
                
                logger.error(f"模塊 {module_name} 運行失敗: {e}")
                return {'status': 'error', 'message': str(e)}
    
    def get_module_status(self, module_name=None):
        """獲取模塊狀態
        
        Args:
            module_name: 模塊名稱，None表示獲取所有模塊狀態
            
        Returns:
            模塊狀態字典
        """
        with self.lock:
            if module_name is not None:
                return self.status.get(module_name, {'loaded': False})
            else:
                return self.status
    
    def discover_modules(self):
        """發現可用的優化模塊
        
        Returns:
            可用模塊列表
        """
        available_modules = []
        
        try:
            # 查找optimization目錄下的所有Python文件
            optimization_dir = os.path.join(BASE_DIR, 'src', 'optimization')
            if not os.path.exists(optimization_dir):
                logger.error(f"優化模塊目錄不存在: {optimization_dir}")
                return []
            
            # 遍歷目錄
            for file in os.listdir(optimization_dir):
                if file.endswith('.py') and file != '__init__.py':
                    module_name = file[:-3]  # 去掉.py後綴
                    available_modules.append(module_name)
            
            logger.info(f"發現 {len(available_modules)} 個優化模塊")
            return available_modules
        
        except Exception as e:
            logger.error(f"發現模塊時發生錯誤: {e}")
            return []
    
    def run_all_modules(self):
        """運行所有優化模塊
        
        Returns:
            運行結果字典
        """
        results = {}
        
        # 發現可用模塊
        modules = self.discover_modules()
        
        # 依次運行每個模塊
        for module_name in modules:
            results[module_name] = self.run_module(module_name)
        
        return results
    
    def run_optimization_pipeline(self):
        """運行優化流程
        
        Returns:
            運行結果
        """
        with self.lock:
            if self.running:
                return {'status': 'error', 'message': '優化流程已在運行中'}
            
            self.running = True
        
        try:
            # 按照順序運行模塊
            pipeline = [
                'database',    # 數據庫優化
                'concurrency', # 併發處理優化
                'requests',    # 請求處理優化
                'static',      # 靜態資源優化
                'memory'       # 內存優化
            ]
            
            results = {}
            
            # 運行流程
            for module_name in pipeline:
                if self.load_module(module_name):
                    logger.info(f"運行模塊: {module_name}")
                    results[module_name] = self.run_module(module_name)
                else:
                    results[module_name] = {'status': 'error', 'message': f"模塊 {module_name} 載入失敗"}
            
            with self.lock:
                self.running = False
            
            return {
                'status': 'success',
                'results': results
            }
        
        except Exception as e:
            logger.error(f"運行優化流程時發生錯誤: {e}")
            
            with self.lock:
                self.running = False
            
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def get_pipeline_status(self):
        """獲取優化流程狀態
        
        Returns:
            流程狀態
        """
        with self.lock:
            pipeline_modules = [
                'database', 'concurrency', 'requests', 'static', 'memory'
            ]
            
            status = {
                'running': self.running,
                'modules': {}
            }
            
            for module_name in pipeline_modules:
                if module_name in self.status:
                    status['modules'][module_name] = self.status[module_name]
                else:
                    status['modules'][module_name] = {'loaded': False}
            
            return status

def parse_arguments():
    """解析命令列參數
    
    Returns:
        解析後的參數
    """
    parser = argparse.ArgumentParser(description='優化管理器')
    parser.add_argument('action', choices=['run', 'status', 'discover', 'pipeline'], 
                        help='要執行的操作')
    parser.add_argument('--module', help='要操作的模塊名稱')
    
    return parser.parse_args()

def main():
    """主函數"""
    # 解析參數
    args = parse_arguments()
    
    # 創建管理器
    manager = OptimizationManager()
    
    # 執行操作
    if args.action == 'run':
        if args.module:
            # 運行特定模塊
            results = manager.run_module(args.module)
        else:
            # 運行所有模塊
            results = manager.run_all_modules()
        
        print(json.dumps(results, indent=2, ensure_ascii=False))
    
    elif args.action == 'status':
        if args.module:
            # 獲取特定模塊狀態
            status = manager.get_module_status(args.module)
        else:
            # 獲取所有模塊狀態
            status = manager.get_module_status()
        
        print(json.dumps(status, indent=2, ensure_ascii=False))
    
    elif args.action == 'discover':
        # 發現可用模塊
        modules = manager.discover_modules()
        print(json.dumps(modules, indent=2, ensure_ascii=False))
    
    elif args.action == 'pipeline':
        # 運行優化流程
        results = manager.run_optimization_pipeline()
        print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
