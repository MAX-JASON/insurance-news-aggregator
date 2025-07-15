#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UI前端測試腳本
用於確認網頁前端改進的功能正常工作
"""

import sys
import os
import time
import logging
import argparse
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ui_test_results.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("UI測試")

class UITester:
    def __init__(self, base_url, headless=True):
        """初始化UI測試器"""
        self.base_url = base_url
        self.headless = headless
        self.driver = None
        self.test_results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0
        }
        self.errors = []
    
    def setup(self):
        """設置Selenium WebDriver"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            
            # 預設使用當前路徑的chromedriver
            service = Service("./chromedriver")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
            logger.info("設置WebDriver成功")
            return True
        except WebDriverException as e:
            logger.error(f"設置WebDriver失敗: {str(e)}")
            return False
    
    def teardown(self):
        """關閉WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver已關閉")
    
    def report(self):
        """報告測試結果"""
        success_rate = (self.test_results['passed'] / self.test_results['total']) * 100 if self.test_results['total'] > 0 else 0
        
        logger.info("=" * 50)
        logger.info("UI測試報告")
        logger.info("=" * 50)
        logger.info(f"總測試數: {self.test_results['total']}")
        logger.info(f"通過: {self.test_results['passed']} ({success_rate:.1f}%)")
        logger.info(f"失敗: {self.test_results['failed']}")
        logger.info(f"跳過: {self.test_results['skipped']}")
        
        if self.errors:
            logger.info("\n錯誤詳情:")
            for i, error in enumerate(self.errors, 1):
                logger.info(f"{i}. {error['test']}: {error['message']}")
        
        return self.test_results['failed'] == 0
    
    def run_test(self, test_name, test_function, *args, **kwargs):
        """運行測試並記錄結果"""
        self.test_results['total'] += 1
        logger.info(f"運行測試: {test_name}")
        
        try:
            result = test_function(*args, **kwargs)
            if result:
                self.test_results['passed'] += 1
                logger.info(f"測試通過: {test_name} ✅")
            else:
                self.test_results['failed'] += 1
                error_msg = "測試失敗，但未拋出異常"
                logger.error(f"測試失敗: {test_name} ❌ - {error_msg}")
                self.errors.append({
                    'test': test_name,
                    'message': error_msg
                })
            return result
        except Exception as e:
            self.test_results['failed'] += 1
            logger.error(f"測試失敗: {test_name} ❌ - {str(e)}")
            self.errors.append({
                'test': test_name,
                'message': str(e)
            })
            return False
    
    def test_home_page_load(self):
        """測試首頁載入"""
        try:
            self.driver.get(f"{self.base_url}/")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            title = self.driver.title
            logger.info(f"首頁載入成功，標題: {title}")
            return "保險新聞聚合器" in title
        except Exception as e:
            logger.error(f"首頁載入失敗: {str(e)}")
            raise
    
    def test_news_list_page(self):
        """測試新聞列表頁面"""
        try:
            self.driver.get(f"{self.base_url}/news")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "newsGrid"))
            )
            
            # 檢查篩選器是否存在
            filter_section = self.driver.find_element(By.CLASS_NAME, "filter-section")
            category_filter = self.driver.find_element(By.ID, "categoryFilter")
            source_filter = self.driver.find_element(By.ID, "sourceFilter")
            
            # 檢查是否有新聞卡片
            news_cards = self.driver.find_elements(By.CLASS_NAME, "news-card")
            
            logger.info(f"新聞列表頁面載入成功，找到 {len(news_cards)} 篇新聞")
            return len(news_cards) > 0
        except Exception as e:
            logger.error(f"新聞列表頁面測試失敗: {str(e)}")
            raise
    
    def test_filter_functionality(self):
        """測試篩選功能"""
        try:
            self.driver.get(f"{self.base_url}/news")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "categoryFilter"))
            )
            
            # 記錄原始新聞數量
            original_cards = len(self.driver.find_elements(By.CLASS_NAME, "news-card"))
            
            # 選擇第一個非空類別
            category_filter = self.driver.find_element(By.ID, "categoryFilter")
            options = category_filter.find_elements(By.TAG_NAME, "option")
            
            # 選擇第二個選項（第一個是"所有分類"）
            if len(options) > 1:
                options[1].click()
                time.sleep(2)  # 等待篩選應用
                
                # 檢查URL是否包含分類參數
                current_url = self.driver.current_url
                logger.info(f"篩選後URL: {current_url}")
                
                return "category=" in current_url
            else:
                logger.info("沒有足夠的類別選項進行測試")
                self.test_results['skipped'] += 1
                return True
        except Exception as e:
            logger.error(f"篩選功能測試失敗: {str(e)}")
            raise
    
    def test_image_error_handling(self):
        """測試圖片錯誤處理"""
        try:
            self.driver.get(f"{self.base_url}/")
            
            # 執行JavaScript來模擬圖片加載錯誤
            script = """
                const images = document.querySelectorAll('img');
                if (images.length > 0) {
                    const event = new Event('error');
                    images[0].dispatchEvent(event);
                    return true;
                }
                return false;
            """
            result = self.driver.execute_script(script)
            
            if result:
                # 檢查圖片是否已設置為預設圖片
                time.sleep(1)
                first_img = self.driver.find_elements(By.TAG_NAME, "img")[0]
                src = first_img.get_attribute("src")
                logger.info(f"圖片處理後的src: {src}")
                
                return "news-placeholder.jpg" in src
            else:
                logger.info("頁面上沒有找到圖片，跳過此測試")
                self.test_results['skipped'] += 1
                return True
        except Exception as e:
            logger.error(f"圖片錯誤處理測試失敗: {str(e)}")
            raise
    
    def test_error_page(self):
        """測試錯誤頁面"""
        try:
            # 訪問不存在的頁面以觸發404
            self.driver.get(f"{self.base_url}/non-existent-page-for-testing")
            
            # 檢查是否顯示了404頁面
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "error-container"))
            )
            
            heading = self.driver.find_element(By.TAG_NAME, "h1").text
            logger.info(f"錯誤頁面標題: {heading}")
            
            return "404" in heading
        except Exception as e:
            logger.error(f"錯誤頁面測試失敗: {str(e)}")
            raise
    
    def test_responsive_design(self):
        """測試響應式設計"""
        try:
            self.driver.get(f"{self.base_url}/")
            
            # 檢查桌面視圖
            self.driver.set_window_size(1920, 1080)
            desktop_navbar = self.driver.find_element(By.CLASS_NAME, "navbar-nav")
            desktop_display = desktop_navbar.value_of_css_property("display")
            
            # 檢查移動視圖
            self.driver.set_window_size(375, 667)  # iPhone 8 尺寸
            time.sleep(1)
            
            # 檢查漢堡按鈕是否可見
            toggler = self.driver.find_element(By.CLASS_NAME, "navbar-toggler")
            toggler_display = toggler.value_of_css_property("display")
            
            logger.info(f"桌面導航欄顯示: {desktop_display}, 漢堡按鈕顯示: {toggler_display}")
            
            # 恢復窗口大小
            self.driver.set_window_size(1920, 1080)
            
            return toggler_display != "none"
        except Exception as e:
            logger.error(f"響應式設計測試失敗: {str(e)}")
            raise
    
    def run_all_tests(self):
        """運行所有測試"""
        if not self.setup():
            logger.error("無法設置WebDriver，跳過測試")
            return False
        
        try:
            # 運行所有測試
            self.run_test("首頁載入測試", self.test_home_page_load)
            self.run_test("新聞列表頁面測試", self.test_news_list_page)
            self.run_test("篩選功能測試", self.test_filter_functionality)
            self.run_test("圖片錯誤處理測試", self.test_image_error_handling)
            self.run_test("錯誤頁面測試", self.test_error_page)
            self.run_test("響應式設計測試", self.test_responsive_design)
            
            return self.report()
        finally:
            self.teardown()


def check_server(url, max_retries=5, retry_interval=2):
    """檢查伺服器是否在線"""
    logger.info(f"檢查伺服器狀態: {url}")
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                logger.info("伺服器正在運行")
                return True
            logger.warning(f"伺服器返回狀態碼: {response.status_code}，重試中 ({i+1}/{max_retries})")
        except requests.exceptions.RequestException as e:
            logger.warning(f"無法連接到伺服器: {str(e)}，重試中 ({i+1}/{max_retries})")
        
        time.sleep(retry_interval)
    
    logger.error("伺服器不可訪問，測試中止")
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UI前端測試腳本")
    parser.add_argument("--url", default="http://localhost:5000", help="伺服器基礎URL")
    parser.add_argument("--headless", action="store_true", default=True, help="以無頭模式運行（不顯示瀏覽器）")
    args = parser.parse_args()
    
    logger.info("開始UI前端測試")
    logger.info(f"目標URL: {args.url}")
    logger.info(f"無頭模式: {args.headless}")
    
    # 檢查伺服器是否在線
    if not check_server(args.url):
        sys.exit(1)
    
    # 創建並運行測試器
    tester = UITester(args.url, args.headless)
    success = tester.run_all_tests()
    
    if not success:
        logger.error("測試存在失敗，請查看日誌獲取詳細信息")
        sys.exit(1)
    
    logger.info("所有測試通過")
    sys.exit(0)
