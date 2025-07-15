"""
全系統整合測試腳本
System Integration Test Script

測試所有功能的協同工作
"""

import os
import sys
import logging
import time
import sqlite3
import json
import requests
import unittest
import threading
import subprocess
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# 設置基本路徑
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 添加路徑到系統路徑
sys.path.insert(0, str(BASE_DIR))

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'logs', 'integration_test.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('integration.test')

class InsuranceNewsIntegrationTest(unittest.TestCase):
    """保險新聞聚合器整合測試類"""
    
    @classmethod
    def setUpClass(cls):
        """測試前設置"""
        cls.app_process = None
        cls.base_url = 'http://localhost:5000'
        cls.admin_user = {'username': 'admin', 'password': 'admin123'}
        cls.test_user = {'username': 'testuser', 'password': 'testpass'}
        cls.db_path = os.path.join(BASE_DIR, 'instance', 'insurance_news.db')
        cls.api_token = None
        
        # 啟動應用
        cls.start_application()
        
        # 等待應用啟動
        time.sleep(5)
        
        # 獲取API令牌
        cls.api_token = cls.get_api_token()
    
    @classmethod
    def tearDownClass(cls):
        """測試後清理"""
        # 停止應用
        cls.stop_application()
    
    @classmethod
    def start_application(cls):
        """啟動應用"""
        try:
            logger.info("啟動應用...")
            cls.app_process = subprocess.Popen(
                ['python', os.path.join(BASE_DIR, 'run.py')],
                cwd=BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logger.info(f"應用已啟動，進程ID: {cls.app_process.pid}")
        except Exception as e:
            logger.error(f"啟動應用失敗: {e}")
    
    @classmethod
    def stop_application(cls):
        """停止應用"""
        if cls.app_process:
            logger.info("停止應用...")
            cls.app_process.terminate()
            cls.app_process.wait(timeout=10)
            logger.info("應用已停止")
    
    @classmethod
    def get_api_token(cls):
        """獲取API令牌"""
        try:
            response = requests.post(
                f"{cls.base_url}/api/auth/login",
                json=cls.admin_user
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('token')
                logger.info("成功獲取API令牌")
                return token
            else:
                logger.error(f"獲取API令牌失敗: {response.text}")
                return None
        except Exception as e:
            logger.error(f"獲取API令牌錯誤: {e}")
            return None
    
    def setUp(self):
        """每個測試前準備"""
        pass
    
    def tearDown(self):
        """每個測試後清理"""
        pass
    
    def test_01_api_status(self):
        """測試API狀態"""
        try:
            response = requests.get(f"{self.base_url}/api/status")
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data['status'], 'ok')
            logger.info("API狀態測試通過")
        except Exception as e:
            logger.error(f"API狀態測試失敗: {e}")
            self.fail(f"API狀態測試失敗: {e}")
    
    def test_02_database_connection(self):
        """測試數據庫連接"""
        try:
            # 連接數據庫
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 檢查news表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='news'")
            result = cursor.fetchone()
            
            self.assertIsNotNone(result)
            self.assertEqual(result[0], 'news')
            
            # 關閉連接
            conn.close()
            logger.info("數據庫連接測試通過")
        except Exception as e:
            logger.error(f"數據庫連接測試失敗: {e}")
            self.fail(f"數據庫連接測試失敗: {e}")
    
    def test_03_user_authentication(self):
        """測試用戶認證"""
        try:
            # 登錄測試
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=self.admin_user
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('token', data)
            
            # 無效登錄測試
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={'username': 'invalid', 'password': 'invalid'}
            )
            
            self.assertNotEqual(response.status_code, 200)
            logger.info("用戶認證測試通過")
        except Exception as e:
            logger.error(f"用戶認證測試失敗: {e}")
            self.fail(f"用戶認證測試失敗: {e}")
    
    def test_04_news_api(self):
        """測試新聞API"""
        try:
            # 獲取最新新聞
            headers = {}
            if self.api_token:
                headers['Authorization'] = f"Bearer {self.api_token}"
            
            response = requests.get(
                f"{self.base_url}/api/news/latest",
                headers=headers
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('news', data)
            self.assertIsInstance(data['news'], list)
            
            # 獲取重要新聞
            response = requests.get(
                f"{self.base_url}/api/news/important",
                headers=headers
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('news', data)
            self.assertIsInstance(data['news'], list)
            
            logger.info("新聞API測試通過")
        except Exception as e:
            logger.error(f"新聞API測試失敗: {e}")
            self.fail(f"新聞API測試失敗: {e}")
    
    def test_05_crawler_api(self):
        """測試爬蟲API"""
        try:
            headers = {}
            if self.api_token:
                headers['Authorization'] = f"Bearer {self.api_token}"
            
            # 獲取爬蟲狀態
            response = requests.get(
                f"{self.base_url}/api/crawler/status",
                headers=headers
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('status', data)
            
            logger.info("爬蟲API測試通過")
        except Exception as e:
            logger.error(f"爬蟲API測試失敗: {e}")
            self.fail(f"爬蟲API測試失敗: {e}")
    
    def test_06_analyzer_api(self):
        """測試分析器API"""
        try:
            headers = {}
            if self.api_token:
                headers['Authorization'] = f"Bearer {self.api_token}"
            
            # 獲取關鍵詞
            response = requests.get(
                f"{self.base_url}/api/analyzer/keywords",
                headers=headers
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn('keywords', data)
            self.assertIsInstance(data['keywords'], list)
            
            logger.info("分析器API測試通過")
        except Exception as e:
            logger.error(f"分析器API測試失敗: {e}")
            self.fail(f"分析器API測試失敗: {e}")
    
    def test_07_optimization_modules(self):
        """測試優化模塊"""
        try:
            # 檢查併發處理模塊
            concurrency_path = os.path.join(BASE_DIR, 'src', 'optimization', 'concurrency.py')
            self.assertTrue(os.path.exists(concurrency_path))
            
            # 檢查請求處理模塊
            requests_path = os.path.join(BASE_DIR, 'src', 'optimization', 'requests.py')
            self.assertTrue(os.path.exists(requests_path))
            
            # 檢查優化管理器
            manager_path = os.path.join(BASE_DIR, 'src', 'optimization', 'manager.py')
            self.assertTrue(os.path.exists(manager_path))
            
            # 執行優化初始化腳本
            result = subprocess.run(
                ['python', os.path.join(BASE_DIR, 'init_optimization.py')],
                cwd=BASE_DIR,
                capture_output=True,
                text=True
            )
            
            self.assertEqual(result.returncode, 0)
            
            logger.info("優化模塊測試通過")
        except Exception as e:
            logger.error(f"優化模塊測試失敗: {e}")
            self.fail(f"優化模塊測試失敗: {e}")
    
    def test_08_service_modules(self):
        """測試服務模塊"""
        try:
            # 檢查客戶問答模塊
            qa_path = os.path.join(BASE_DIR, 'src', 'services', 'client_qa_templates.py')
            self.assertTrue(os.path.exists(qa_path))
            
            # 檢查商機監測模塊
            opportunity_path = os.path.join(BASE_DIR, 'src', 'services', 'business_opportunity_monitor.py')
            self.assertTrue(os.path.exists(opportunity_path))
            
            # 檢查商品推薦模塊
            recommendation_path = os.path.join(BASE_DIR, 'src', 'services', 'product_recommendation.py')
            self.assertTrue(os.path.exists(recommendation_path))
            
            # 檢查業務員分析模塊
            analytics_path = os.path.join(BASE_DIR, 'src', 'services', 'agent_analytics.py')
            self.assertTrue(os.path.exists(analytics_path))
            
            logger.info("服務模塊測試通過")
        except Exception as e:
            logger.error(f"服務模塊測試失敗: {e}")
            self.fail(f"服務模塊測試失敗: {e}")
    
    def test_09_web_pages(self):
        """測試網頁訪問"""
        try:
            # 測試主頁
            response = requests.get(f"{self.base_url}/")
            self.assertEqual(response.status_code, 200)
            
            # 測試登錄頁
            response = requests.get(f"{self.base_url}/login")
            self.assertEqual(response.status_code, 200)
            
            # 測試公開新聞頁
            response = requests.get(f"{self.base_url}/news")
            self.assertEqual(response.status_code, 200)
            
            logger.info("網頁訪問測試通過")
        except Exception as e:
            logger.error(f"網頁訪問測試失敗: {e}")
            self.fail(f"網頁訪問測試失敗: {e}")
    
    def test_10_concurrent_requests(self):
        """測試併發請求"""
        try:
            # 測試多個併發請求
            urls = [
                f"{self.base_url}/api/news/latest",
                f"{self.base_url}/api/news/important",
                f"{self.base_url}/api/status",
                f"{self.base_url}/api/analyzer/keywords"
            ]
            
            headers = {}
            if self.api_token:
                headers['Authorization'] = f"Bearer {self.api_token}"
            
            def fetch_url(url):
                try:
                    response = requests.get(url, headers=headers)
                    return response.status_code == 200
                except:
                    return False
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                results = list(executor.map(fetch_url, urls * 5))  # 每個URL請求5次
            
            # 檢查所有請求是否成功
            self.assertTrue(all(results))
            
            logger.info("併發請求測試通過")
        except Exception as e:
            logger.error(f"併發請求測試失敗: {e}")
            self.fail(f"併發請求測試失敗: {e}")

def run_tests():
    """運行測試"""
    test_suite = unittest.TestLoader().loadTestsFromTestCase(InsuranceNewsIntegrationTest)
    test_result = unittest.TextTestRunner(verbosity=2).run(test_suite)
    
    # 返回測試結果
    return {
        'total': test_result.testsRun,
        'failures': len(test_result.failures),
        'errors': len(test_result.errors),
        'success': test_result.wasSuccessful()
    }

def main():
    """主函數"""
    logger.info("開始執行全系統整合測試")
    
    # 運行測試
    results = run_tests()
    
    # 輸出測試結果
    logger.info(f"測試完成: 總計 {results['total']} 項測試，失敗 {results['failures']}，錯誤 {results['errors']}")
    
    # 返回測試結果
    return {
        'status': 'success' if results['success'] else 'failed',
        'test_results': results
    }

if __name__ == "__main__":
    main()
