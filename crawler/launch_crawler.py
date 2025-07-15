"""
簡易爬蟲啟動器
Simple Crawler Launcher

提供一個簡單的腳本來單獨運行爬蟲功能
"""

import os
import sys
import logging
import time
from datetime import datetime

# 設置路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(project_root, 'logs', 'crawler_launcher.log'))
    ]
)
logger = logging.getLogger('crawler_launcher')

def run_crawler():
    """運行爬蟲"""
    logger.info("=" * 50)
    logger.info("啟動保險新聞爬蟲")
    logger.info("=" * 50)
    
    try:
        # 載入爬蟲管理器
        logger.info("正在載入爬蟲管理器...")
        from crawler.manager import get_crawler_manager
        
        # 獲取爬蟲管理器實例
        manager = get_crawler_manager()
        logger.info("爬蟲管理器載入成功")
        
        # 執行爬取
        logger.info("開始執行爬取任務...")
        start_time = time.time()
        result = manager.crawl_all_sources(use_mock=True)
        end_time = time.time()
        
        # 檢查結果
        if result['status'] == 'success':
            logger.info(f"爬取任務完成! 耗時: {end_time - start_time:.2f} 秒")
            logger.info(f"總共爬取了 {result.get('total', 0)} 條新聞")
            logger.info(f"新增了 {result.get('new', 0)} 條新聞")
            
            # 顯示每個來源的結果
            for crawl_result in result.get('results', []):
                source = crawl_result.get('source', 'Unknown')
                success = crawl_result.get('success', False)
                news_count = crawl_result.get('news_count', 0)
                
                status = "成功" if success else "失敗"
                logger.info(f"來源 [{source}]: {status}, 新聞數量: {news_count}")
            
            return 0
        else:
            logger.error(f"爬取任務失敗: {result.get('message', '未知錯誤')}")
            return 1
            
    except ImportError as e:
        logger.error(f"無法導入爬蟲管理器: {e}")
        return 2
    except Exception as e:
        logger.error(f"執行爬蟲時發生錯誤: {e}", exc_info=True)
        return 3

if __name__ == "__main__":
    exit_code = run_crawler()
    sys.exit(exit_code)
