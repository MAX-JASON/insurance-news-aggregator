"""
基本功能測試
Basic Functionality Tests

測試核心功能的基本運行狀況
"""

import unittest
import os
import sys
import json

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from config.settings import TestingConfig as TestConfig
from database.models import News, NewsSource

class BasicTestCase(unittest.TestCase):
    """基本功能測試案例"""
    
    def setUp(self):
        """測試前設置"""
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
    def tearDown(self):
        """測試後清理"""
        self.app_context.pop()
    
    def test_app_exists(self):
        """測試應用是否存在"""
        self.assertTrue(self.app is not None)
        
    def test_app_is_testing(self):
        """測試是否處於測試配置"""
        self.assertTrue(self.app.config['TESTING'])
        
    def test_home_page(self):
        """測試首頁是否正常訪問"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response.content_type)
        
    def test_api_status(self):
        """測試API狀態端點是否正常"""
        response = self.client.get('/api/v1/status')
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/json', response.content_type)
        
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'ok')
        
    def test_business_page(self):
        """測試業務頁面是否正常訪問"""
        response = self.client.get('/business')
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response.content_type)
        
    def test_error_handling_404(self):
        """測試404錯誤處理"""
        response = self.client.get('/non_existent_page')
        self.assertEqual(response.status_code, 404)


class ConfigTestCase(unittest.TestCase):
    """配置系統測試案例"""
    
    def test_config_loading(self):
        """測試配置加載"""
        from config.config_manager import ConfigManager
        
        # 使用測試配置路徑
        test_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                      'config', 'config.example.yaml')
        
        config_manager = ConfigManager(test_config_path)
        self.assertTrue(config_manager.load_config())
        
        # 測試獲取配置值
        app_name = config_manager.get('app.name')
        self.assertIsNotNone(app_name)
        
        # 測試獲取嵌套配置
        crawler_delay = config_manager.get('crawler.delay', 0)
        self.assertIsInstance(crawler_delay, (int, float))
        
        # 測試獲取默認值
        non_existent = config_manager.get('non_existent_key', 'default_value')
        self.assertEqual(non_existent, 'default_value')


class CrawlerTestCase(unittest.TestCase):
    """爬蟲系統基本測試"""
    
    def test_crawler_engine(self):
        """測試爬蟲引擎基本功能"""
        from crawler.engine import CrawlerEngine
        
        engine = CrawlerEngine()
        self.assertIsNotNone(engine)


if __name__ == '__main__':
    unittest.main()