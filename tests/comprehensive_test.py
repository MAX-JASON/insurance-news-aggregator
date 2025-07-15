"""
綜合系統測試腳本
Comprehensive System Test Script

測試所有核心功能，包括爬蟲、API、可視化等
"""

import requests
import json
import time
from datetime import datetime

def test_api_endpoint(url, method='GET', data=None, description=""):
    """測試API端點"""
    try:
        print(f"\n🔍 測試: {description}")
        print(f"📡 請求: {method} {url}")
        
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        
        print(f"📊 狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ API回應成功")
                if 'status' in result:
                    print(f"📋 狀態: {result['status']}")
                if 'message' in result:
                    print(f"💬 訊息: {result['message']}")
                if 'data' in result and isinstance(result['data'], dict):
                    print(f"📦 數據鍵: {list(result['data'].keys())}")
                return True, result
            except json.JSONDecodeError:
                print(f"⚠️ 非JSON回應，內容長度: {len(response.text)}")
                return True, response.text
        else:
            print(f"❌ API錯誤: {response.status_code}")
            print(f"🔍 錯誤內容: {response.text[:200]}...")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 請求失敗: {e}")
        return False, None
    except Exception as e:
        print(f"❌ 其他錯誤: {e}")
        return False, None

def test_web_page(url, description=""):
    """測試網頁端點"""
    try:
        print(f"\n🌐 測試網頁: {description}")
        print(f"📡 請求: GET {url}")
        
        response = requests.get(url, timeout=10)
        print(f"📊 狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            content_length = len(response.text)
            print(f"✅ 網頁載入成功，內容長度: {content_length}")
            
            # 檢查是否包含關鍵字
            if '保險新聞' in response.text or 'Insurance' in response.text:
                print(f"🎯 內容驗證通過")
            else:
                print(f"⚠️ 內容可能異常")
            
            return True, response.text
        else:
            print(f"❌ 網頁錯誤: {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ 網頁測試失敗: {e}")
        return False, None

def main():
    """主測試函數"""
    print("🧪 保險新聞聚合器綜合測試")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5000"
    
    # 測試結果統計
    tests_total = 0
    tests_passed = 0
    
    # 1. 基本連接測試
    success, _ = test_web_page(f"{base_url}/", "首頁")
    tests_total += 1
    if success:
        tests_passed += 1
    
    # 2. API健康檢查
    success, _ = test_api_endpoint(f"{base_url}/api/health", description="API健康檢查")
    tests_total += 1
    if success:
        tests_passed += 1
    
    # 3. 爬蟲狀態API (V1)
    success, data = test_api_endpoint(f"{base_url}/api/v1/crawler/status", description="V1爬蟲狀態查詢")
    tests_total += 1
    if success:
        tests_passed += 1
    
    # 4. 爬蟲來源API (V1)  
    success, data = test_api_endpoint(f"{base_url}/api/v1/crawler/sources", description="V1爬蟲來源列表")
    tests_total += 1
    if success:
        tests_passed += 1
        if data and 'data' in data:
            sources_count = len(data['data'])
            print(f"📊 爬蟲來源數量: {sources_count}")
    
    # 5. V1統計API
    success, data = test_api_endpoint(f"{base_url}/api/v1/stats", description="V1統計數據")
    tests_total += 1
    if success:
        tests_passed += 1
    
    # 6. 儀表板統計API
    success, data = test_api_endpoint(f"{base_url}/api/stats/dashboard", description="儀表板統計數據")
    tests_total += 1
    if success:
        tests_passed += 1
        if data and 'data' in data:
            dashboard_data = data['data']
            print(f"📊 總新聞數: {dashboard_data.get('overview', {}).get('total_news', 'N/A')}")
            print(f"📰 新聞來源數: {dashboard_data.get('overview', {}).get('total_sources', 'N/A')}")
    
    # 7. V1爬蟲啟動測試
    success, data = test_api_endpoint(
        f"{base_url}/api/v1/crawler/start", 
        method='POST',
        data={'use_mock': True, 'max_news': 10},
        description="V1爬蟲手動啟動"
    )
    tests_total += 1
    if success:
        tests_passed += 1
    
    # 8. 業務員頁面測試
    success, _ = test_web_page(f"{base_url}/business", "業務員工作台")
    tests_total += 1
    if success:
        tests_passed += 1
    
    # 9. 可視化儀表板測試
    success, _ = test_web_page(f"{base_url}/analysis", "分析儀表板")
    tests_total += 1
    if success:
        tests_passed += 1
    
    # 10. 爬蟲監控頁面測試
    success, _ = test_web_page(f"{base_url}/crawler/monitor", "爬蟲監控頁面")
    tests_total += 1
    if success:
        tests_passed += 1
    
    # 11. 新聞列表頁面測試
    success, _ = test_web_page(f"{base_url}/news", "新聞列表")
    tests_total += 1
    if success:
        tests_passed += 1
    
    # 12. 反饋系統測試
    success, _ = test_web_page(f"{base_url}/feedback", "用戶反饋")
    tests_total += 1
    if success:
        tests_passed += 1
    
    # 測試總結
    print("\n" + "=" * 50)
    print("📋 測試總結")
    print(f"🧪 總測試數: {tests_total}")
    print(f"✅ 通過數: {tests_passed}")
    print(f"❌ 失敗數: {tests_total - tests_passed}")
    print(f"📊 成功率: {tests_passed/tests_total*100:.1f}%")
    
    if tests_passed == tests_total:
        print("🎉 所有測試通過！系統運行正常")
    elif tests_passed >= tests_total * 0.8:
        print("⚠️ 大部分測試通過，系統基本正常")
    else:
        print("❌ 多個測試失敗，請檢查系統狀態")
    
    print(f"\n⏰ 測試完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
