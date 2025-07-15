"""
新聞詳情頁面測試腳本
News Detail Page Test Script

測試新聞詳情頁面的各種情況
"""

import requests
import json
from datetime import datetime

def test_news_detail_pages():
    """測試新聞詳情頁面"""
    base_url = "http://localhost:5000"
    
    print("🧪 測試新聞詳情頁面功能")
    print("=" * 50)
    
    # 測試多個新聞ID
    test_ids = [1, 2, 3, 10, 50, 100, 999]
    
    for news_id in test_ids:
        try:
            url = f"{base_url}/news/{news_id}"
            print(f"\n📰 測試新聞ID: {news_id}")
            print(f"   URL: {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ 狀態: {response.status_code} - 頁面載入成功")
                
                # 檢查頁面內容
                content = response.text
                if "台灣保險新聞" in content:
                    print(f"   ✅ 內容: 包含台灣保險新聞標題")
                if "查看原文" in content:
                    print(f"   ✅ 功能: 包含原文連結按鈕")
                if "分享這篇新聞" in content:
                    print(f"   ✅ 功能: 包含分享功能")
                    
            elif response.status_code == 404:
                print(f"   ⚠️ 狀態: {response.status_code} - 新聞不存在（正常）")
            else:
                print(f"   ❌ 狀態: {response.status_code} - 未預期的狀態碼")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ 連接錯誤: {e}")
        except Exception as e:
            print(f"   ❌ 測試錯誤: {e}")

def test_homepage():
    """測試首頁新聞連結"""
    base_url = "http://localhost:5000"
    
    print(f"\n🏠 測試首頁新聞連結")
    print("-" * 30)
    
    try:
        response = requests.get(base_url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ 首頁載入成功")
            
            content = response.text
            
            # 檢查是否有新聞連結
            if '/news/' in content:
                print(f"✅ 發現新聞詳情連結")
            
            if "台灣保險新聞聚合器" in content:
                print(f"✅ 頁面標題正確")
                
            if "最新保險新聞" in content:
                print(f"✅ 包含新聞區塊")
                
        else:
            print(f"❌ 首頁載入失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 首頁測試錯誤: {e}")

def test_api_endpoints():
    """測試API端點"""
    base_url = "http://localhost:5000"
    
    print(f"\n🔌 測試API端點")
    print("-" * 30)
    
    api_endpoints = [
        "/api/v1/health",
        "/api/v1/stats",
        "/api/v1/news"
    ]
    
    for endpoint in api_endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {endpoint} - 正常")
                
                # 如果是JSON回應，檢查格式
                if 'application/json' in response.headers.get('content-type', ''):
                    try:
                        data = response.json()
                        print(f"   📊 回應: {len(str(data))} 字元")
                    except:
                        print(f"   ⚠️ JSON解析失敗")
            else:
                print(f"❌ {endpoint} - 狀態: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint} - 錯誤: {e}")

def main():
    """主測試函數"""
    print("🇹🇼 台灣保險新聞聚合器 - 功能測試")
    print("=" * 60)
    print(f"📅 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 測試各個功能
    test_homepage()
    test_news_detail_pages()
    test_api_endpoints()
    
    print("\n" + "=" * 60)
    print("✅ 功能測試完成")
    print("\n建議接下來：")
    print("1. 在瀏覽器中訪問 http://localhost:5000")
    print("2. 點擊任一新聞標題測試詳情頁面")
    print("3. 測試「查看原文」按鈕功能")
    print("4. 驗證新聞內容顯示是否正確")

if __name__ == "__main__":
    main()
