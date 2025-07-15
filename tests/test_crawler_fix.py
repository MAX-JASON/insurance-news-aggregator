"""
測試爬蟲修復後的功能
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_crawler_api():
    """測試爬蟲相關的 API"""
    print("🧪 測試爬蟲 API...")
    
    # 測試爬蟲狀態端點
    endpoints = [
        ("/api/v1/crawler/status", "爬蟲狀態 V1"),
        ("/api/v1/stats", "統計資料 V1"),
        ("/api/v1/crawler/sources", "爬蟲來源 V1"),
    ]
    
    for endpoint, description in endpoints:
        print(f"\n📡 測試: {description}")
        print(f"🔗 URL: {BASE_URL}{endpoint}")
        
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            print(f"📊 狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API 回應成功")
                
                # 檢查數據結構
                if data.get('status') == 'success' and 'data' in data:
                    print(f"📦 包含數據結構")
                    
                    # 檢查爬蟲狀態特定欄位
                    if endpoint == "/api/v1/crawler/status":
                        required_fields = ['source_totals', 'recent_runs', 'total_news', 'today_news']
                        for field in required_fields:
                            if field in data['data']:
                                print(f"✅ 包含 {field}: {type(data['data'][field])}")
                                if field == 'source_totals' and data['data'][field]:
                                    print(f"   - 第一個來源: {data['data'][field][0]}")
                            else:
                                print(f"❌ 缺少 {field}")
                    
                    # 檢查統計資料特定欄位
                    elif endpoint == "/api/v1/stats":
                        required_fields = ['totalNews', 'totalSources', 'source_totals']
                        for field in required_fields:
                            if field in data['data']:
                                print(f"✅ 包含 {field}: {type(data['data'][field])}")
                            else:
                                print(f"❌ 缺少 {field}")
                
                else:
                    print(f"⚠️ 回應格式異常: {list(data.keys())}")
                    
            else:
                print(f"❌ API 錯誤: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ 請求失敗: {e}")

def test_web_pages():
    """測試網頁是否正常載入"""
    print("\n🌐 測試網頁載入...")
    
    pages = [
        ("/monitor/crawler", "爬蟲監控頁面"),
        ("/monitor/manual_crawl", "手動執行爬蟲頁面"),
        ("/monitor/settings", "監控設定頁面"),
        ("/", "首頁"),
    ]
    
    for page, description in pages:
        print(f"\n🔍 測試: {description}")
        print(f"🔗 URL: {BASE_URL}{page}")
        
        try:
            response = requests.get(f"{BASE_URL}{page}", timeout=10)
            print(f"📊 狀態碼: {response.status_code}")
            
            if response.status_code == 200:
                content_length = len(response.text)
                print(f"✅ 頁面載入成功，內容長度: {content_length}")
                
                # 檢查是否包含重要的 JavaScript 或 HTML 元素
                if "bootstrap" in response.text.lower():
                    print("✅ 包含 Bootstrap 框架")
                if "api/v1" in response.text:
                    print("✅ 包含 V1 API 調用")
                if "source_totals" in response.text:
                    print("✅ 包含 source_totals 處理")
                    
            else:
                print(f"❌ 頁面錯誤: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 請求失敗: {e}")

def test_crawler_start():
    """測試爬蟲啟動功能"""
    print("\n🚀 測試爬蟲啟動...")
    
    try:
        # 使用模擬數據啟動爬蟲
        response = requests.post(
            f"{BASE_URL}/api/v1/crawler/start",
            json={"use_mock": True},
            timeout=30
        )
        
        print(f"📊 狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 爬蟲啟動回應: {data.get('message', '無訊息')}")
            
            if data.get('status') == 'success':
                print("🎉 爬蟲啟動成功！")
            else:
                print(f"⚠️ 爬蟲啟動狀態: {data.get('status')}")
                
        else:
            print(f"❌ 爬蟲啟動失敗: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ 爬蟲啟動請求失敗: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 保險新聞聚合器 - 爬蟲修復測試")
    print(f"⏰ 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 執行測試
    test_crawler_api()
    test_web_pages()
    test_crawler_start()
    
    print("\n" + "=" * 60)
    print("🎯 測試完成!")
    print("💡 請檢查瀏覽器中的爬蟲監控頁面是否正常顯示數據")
    print("=" * 60)
