"""
爬蟲實用工具
Crawler Utility Functions

提供爬蟲相關的實用函數
"""

import os
import sys
import logging
import traceback
from typing import Dict, Any, List
from datetime import datetime
import sqlite3

# 設置日誌
logger = logging.getLogger('crawler.utils')

def check_crawler_status() -> Dict[str, Any]:
    """
    檢查爬蟲狀態
    
    Returns:
        狀態字典
    """
    status = {
        'running': False,
        'last_run': None,
        'db_available': False,
        'news_count': 0,
        'sources': [],
        'error': None
    }
    
    try:
        # 檢查資料庫
        db_path = os.path.join('instance', 'insurance_news.db')
        
        if not os.path.exists(db_path):
            status['error'] = '資料庫檔案不存在'
            return status
            
        # 連接數據庫
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        status['db_available'] = True
        
        # 查詢新聞總數
        try:
            cursor.execute('SELECT COUNT(*) FROM news')
            status['news_count'] = cursor.fetchone()[0]
        except sqlite3.OperationalError:
            status['error'] = '資料庫中沒有news表'
        
        # 查詢來源統計
        try:
            cursor.execute('SELECT source, COUNT(*) as count FROM news GROUP BY source ORDER BY count DESC')
            status['sources'] = [{'name': source, 'count': count} for source, count in cursor.fetchall()]
        except sqlite3.OperationalError:
            pass
        
        # 查詢最後爬取時間
        try:
            cursor.execute('SELECT MAX(crawled_date) FROM news')
            last_run = cursor.fetchone()[0]
            if last_run:
                status['last_run'] = last_run
        except sqlite3.OperationalError:
            pass
        
        conn.close()
        
    except Exception as e:
        status['error'] = str(e)
        logger.error(f"檢查爬蟲狀態時出錯: {e}")
        
    return status

def run_crawler(use_mock=True) -> Dict[str, Any]:
    """
    執行爬蟲
    
    Args:
        use_mock: 是否使用模擬數據
        
    Returns:
        結果字典
    """
    result = {
        'success': False,
        'message': '',
        'total': 0,
        'new': 0,
        'elapsed_time': 0,
        'error': None
    }
    
    try:
        import time
        from crawler.manager import get_crawler_manager
        
        # 獲取爬蟲管理器
        manager = get_crawler_manager()
        
        # 執行爬蟲
        start_time = time.time()
        crawler_result = manager.crawl_all_sources(use_mock=use_mock)
        elapsed_time = time.time() - start_time
        
        # 處理結果
        if crawler_result['status'] == 'success':
            result['success'] = True
            result['message'] = crawler_result['message']
            result['total'] = crawler_result.get('total', 0)
            result['new'] = crawler_result.get('new', 0)
            result['elapsed_time'] = elapsed_time
        else:
            result['message'] = crawler_result.get('message', '未知錯誤')
            result['error'] = crawler_result.get('message', '爬蟲執行失敗')
            
    except ImportError:
        result['error'] = '無法導入爬蟲管理器'
        result['message'] = '爬蟲管理器導入失敗'
    except Exception as e:
        result['error'] = str(e)
        result['message'] = f'爬蟲執行失敗: {str(e)}'
        logger.error(f"執行爬蟲時出錯: {traceback.format_exc()}")
        
    return result

def fix_crawler_errors() -> Dict[str, Any]:
    """
    嘗試修復爬蟲常見錯誤
    
    Returns:
        修復結果字典
    """
    result = {
        'success': True,
        'message': '檢查完成',
        'fixes': []
    }
    
    try:
        # 檢查並創建必要的目錄
        directories = [
            'instance',
            'logs',
            'cache',
            'data/feedback',
            'temp'
        ]
        
        for directory in directories:
            dir_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), directory)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                result['fixes'].append(f'創建了缺少的目錄: {directory}')
        
        # 檢查日誌文件
        log_file = os.path.join('logs', 'crawler.log')
        if not os.path.exists(log_file):
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f'Log file created at {datetime.now().isoformat()}\n')
            result['fixes'].append('創建了缺少的日誌文件')
        
        # 檢查資料庫
        db_path = os.path.join('instance', 'insurance_news.db')
        if not os.path.exists(db_path):
            result['fixes'].append('發現資料庫文件缺失')
            
            try:
                # 嘗試初始化資料庫
                from app import create_app
                from config.settings import Config
                
                app = create_app(Config)
                with app.app_context():
                    from app import db
                    db.create_all()
                    
                result['fixes'].append('已成功初始化資料庫')
            except Exception as e:
                result['fixes'].append(f'無法初始化資料庫: {str(e)}')
                result['success'] = False
        
    except Exception as e:
        result['success'] = False
        result['message'] = f'修復過程中出錯: {str(e)}'
        logger.error(f"嘗試修復爬蟲錯誤時失敗: {e}")
        
    return result

def main():
    """命令行入口點"""
    import argparse
    
    parser = argparse.ArgumentParser(description='爬蟲實用工具')
    parser.add_argument('--check', action='store_true', help='檢查爬蟲狀態')
    parser.add_argument('--run', action='store_true', help='執行爬蟲')
    parser.add_argument('--fix', action='store_true', help='嘗試修復錯誤')
    parser.add_argument('--mock', action='store_true', help='使用模擬數據')
    
    args = parser.parse_args()
    
    if args.check:
        status = check_crawler_status()
        print("爬蟲狀態:")
        print(f"- 資料庫可用: {'是' if status['db_available'] else '否'}")
        print(f"- 新聞總數: {status['news_count']}")
        print(f"- 最後運行: {status['last_run'] or '未知'}")
        if status['error']:
            print(f"- 錯誤: {status['error']}")
        print("\n來源統計:")
        for source in status['sources']:
            print(f"- {source['name']}: {source['count']} 條新聞")
            
    elif args.run:
        result = run_crawler(use_mock=args.mock)
        if result['success']:
            print(f"爬蟲執行成功: {result['message']}")
            print(f"- 總共處理: {result['total']} 條新聞")
            print(f"- 新增: {result['new']} 條")
            print(f"- 耗時: {result['elapsed_time']:.2f} 秒")
        else:
            print(f"爬蟲執行失敗: {result['message']}")
            if result['error']:
                print(f"錯誤: {result['error']}")
                
    elif args.fix:
        result = fix_crawler_errors()
        print(f"修復結果: {result['message']}")
        for fix in result['fixes']:
            print(f"- {fix}")
        print(f"狀態: {'成功' if result['success'] else '部分失敗'}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
