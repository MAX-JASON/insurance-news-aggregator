"""
初始化併發處理優化模塊
Initialize Concurrency Optimization

將併發處理優化功能集成到系統中
"""

import os
import sys
import logging
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
        logging.FileHandler(os.path.join(BASE_DIR, 'logs', 'initialization.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('init.optimization')

def init_optimization():
    """初始化優化模塊"""
    try:
        logger.info("開始初始化優化模塊")
        
        # 創建必要的目錄
        os.makedirs(os.path.join(BASE_DIR, 'src', 'optimization'), exist_ok=True)
        os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)
        os.makedirs(os.path.join(BASE_DIR, 'cache', 'optimization'), exist_ok=True)
        os.makedirs(os.path.join(BASE_DIR, 'data', 'templates'), exist_ok=True)
        
        # 創建初始化文件
        init_file = os.path.join(BASE_DIR, 'src', 'optimization', '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write('"""優化模塊包\n\n提供各種系統優化功能\n"""\n')
        
        # 導入優化管理器
        try:
            from src.optimization.manager import OptimizationManager
            manager = OptimizationManager()
            
            # 發現可用模塊
            modules = manager.discover_modules()
            logger.info(f"發現 {len(modules)} 個優化模塊")
            
            # 載入模塊
            loaded_modules = []
            for module_name in modules:
                if manager.load_module(module_name):
                    loaded_modules.append(module_name)
            
            logger.info(f"已載入 {len(loaded_modules)} 個優化模塊: {', '.join(loaded_modules)}")
            
            return {
                'status': 'success',
                'modules': loaded_modules
            }
        
        except ImportError:
            logger.error("未找到優化管理器，請先創建")
            return {
                'status': 'error',
                'message': '未找到優化管理器'
            }
        
    except Exception as e:
        logger.error(f"初始化優化模塊失敗: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }

def init_webapp_integration():
    """初始化Web應用集成"""
    try:
        # 檢查Flask應用
        try:
            from app import create_app
            from config.settings import Config
            
            # 創建應用實例
            app = create_app(Config)
            
            # 集成併發處理優化
            with app.app_context():
                try:
                    from src.optimization.concurrency import init_flask_concurrency
                    init_flask_concurrency(app)
                    logger.info("併發處理優化已集成到Flask應用")
                except ImportError:
                    logger.warning("未找到併發處理優化模塊")
                
                # 集成請求處理優化
                try:
                    from src.optimization.requests import init_request_optimizer
                    init_request_optimizer(app)
                    logger.info("請求處理優化已集成到Flask應用")
                except ImportError:
                    logger.warning("未找到請求處理優化模塊")
            
            logger.info("Web應用優化集成完成")
            return {
                'status': 'success',
                'app_name': app.name,
                'modules': ['concurrency', 'requests']
            }
        
        except ImportError:
            logger.error("未找到Flask應用")
            return {
                'status': 'error',
                'message': '未找到Flask應用'
            }
        
    except Exception as e:
        logger.error(f"初始化Web應用集成失敗: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }

def init_template_services():
    """初始化範本服務"""
    try:
        # 導入客戶問答範本管理
        from src.services.client_qa_templates import TemplateManager, create_template_samples
        
        # 創建示例範本
        if not os.path.exists(os.path.join(BASE_DIR, 'data', 'templates', 'insurance.json')):
            create_template_samples()
            logger.info("已創建示例範本")
        
        # 初始化範本管理器
        template_manager = TemplateManager()
        template_count = len(template_manager.templates)
        categories = template_manager.get_categories()
        
        logger.info(f"範本服務初始化完成，共 {template_count} 個範本，{len(categories)} 個分類")
        return {
            'status': 'success',
            'template_count': template_count,
            'categories': categories
        }
    
    except ImportError:
        logger.error("未找到範本服務模塊")
        return {
            'status': 'error',
            'message': '未找到範本服務模塊'
        }
    except Exception as e:
        logger.error(f"初始化範本服務失敗: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }

def init_business_monitor():
    """初始化商業機會監測"""
    try:
        # 導入商業機會監測
        from src.services.business_opportunity_monitor import BusinessOpportunityMonitor, create_default_config
        
        # 創建默認配置
        create_default_config()
        
        # 初始化監測器
        monitor = BusinessOpportunityMonitor()
        
        # 獲取統計數據
        stats = monitor.get_opportunity_stats()
        
        logger.info("商業機會監測初始化完成")
        return {
            'status': 'success',
            'stats': stats
        }
    
    except ImportError:
        logger.error("未找到商業機會監測模塊")
        return {
            'status': 'error',
            'message': '未找到商業機會監測模塊'
        }
    except Exception as e:
        logger.error(f"初始化商業機會監測失敗: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }

def main():
    """主函數"""
    logger.info("開始初始化系統優化")
    
    results = {
        'optimization': init_optimization(),
        'webapp': init_webapp_integration(),
        'templates': init_template_services(),
        'business_monitor': init_business_monitor()
    }
    
    # 檢查整體狀態
    overall_status = all(r.get('status') == 'success' for r in results.values())
    results['overall_status'] = 'success' if overall_status else 'partial'
    
    logger.info(f"系統優化初始化完成，狀態: {results['overall_status']}")
    return results

if __name__ == "__main__":
    main()
