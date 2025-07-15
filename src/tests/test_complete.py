#!/usr/bin/env python3
"""
完整功能測試腳本
"""

import requests
import json
from datetime import datetime

def test_api_endpoints():
    """測試API端點"""
    base_url = "http://localhost:5000"
    
    print("🔌 API端點測試")
    print("=" * 50)
    
    # 測試 health 端點
    try:
        r = requests.get(f"{base_url}/api/v1/health", timeout=5)
        print(f"✅ /api/v1/health - 狀態: {r.status_code}")
    except Exception as e:
        print(f"❌ /api/v1/health - 錯誤: {e}")
    
    # 測試 stats 端點
    try:
        r = requests.get(f"{base_url}/api/v1/stats", timeout=5)
        if r.status_code == 200:
            data = r.json()['data']
            print(f"✅ /api/v1/stats - 狀態: {r.status_code}")
            print(f"   📰 總新聞: {data['totalNews']}")
            print(f"   🌐 總來源: {data['totalSources']}")
            print(f"   📁 總分類: {data['totalCategories']}")
            print(f"   📅 今日新聞: {data['todayNews']}")
        else:
            print(f"❌ /api/v1/stats - 狀態: {r.status_code}")
    except Exception as e:
        print(f"❌ /api/v1/stats - 錯誤: {e}")
    
    # 測試 news 端點
    try:
        r = requests.get(f"{base_url}/api/v1/news", timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(f"✅ /api/v1/news - 狀態: {r.status_code}")
            print(f"   📰 返回新聞數: {len(data['data'])}")
            if data['data']:
                print(f"   📑 第一則: {data['data'][0]['title'][:50]}...")
        else:
            print(f"❌ /api/v1/news - 狀態: {r.status_code}")
    except Exception as e:
        print(f"❌ /api/v1/news - 錯誤: {e}")

def test_web_pages():
    """測試網頁端點"""
    base_url = "http://localhost:5000"
    
    print("\n🌐 網頁端點測試")
    print("=" * 50)
    
    # 測試首頁
    try:
        r = requests.get(f"{base_url}/", timeout=10)
        print(f"✅ 首頁 - 狀態: {r.status_code}")
        if "台灣保險新聞聚合器" in r.text:
            print("   📄 頁面標題正確")
        if "總新聞數量" in r.text:
            print("   📊 包含統計區塊")
    except Exception as e:
        print(f"❌ 首頁 - 錯誤: {e}")
    
    # 測試新聞列表
    try:
        r = requests.get(f"{base_url}/news", timeout=10)
        print(f"✅ 新聞列表 - 狀態: {r.status_code}")
        if "新聞列表" in r.text:
            print("   📰 包含新聞列表")
    except Exception as e:
        print(f"❌ 新聞列表 - 錯誤: {e}")
    
    # 測試新聞詳情
    try:
        r = requests.get(f"{base_url}/news/1", timeout=10)
        print(f"✅ 新聞詳情 - 狀態: {r.status_code}")
        if "新聞詳情" in r.text or "台灣保險新聞" in r.text:
            print("   📑 包含新聞內容")
    except Exception as e:
        print(f"❌ 新聞詳情 - 錯誤: {e}")

def test_frontend_functionality():
    """測試前端功能"""
    print("\n🎨 前端功能檢查")
    print("=" * 50)
    
    # 獲取首頁統計數據
    try:
        r = requests.get("http://localhost:5000/api/v1/stats")
        if r.status_code == 200:
            stats = r.json()['data']
            print("📊 統計數據可用:")
            print(f"   📰 總新聞數量: {stats['totalNews']}")
            print(f"   🌐 新聞來源: {stats['totalSources']}")
            print(f"   📁 新聞分類: {stats['totalCategories']}")
            print(f"   📅 今日更新: {stats['todayNews']}")
        else:
            print("❌ 統計數據不可用")
    except Exception as e:
        print(f"❌ 統計數據錯誤: {e}")

if __name__ == "__main__":
    print("🇹🇼 台灣保險新聞聚合器 - 完整功能測試")
    print("=" * 60)
    print(f"📅 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_api_endpoints()
    test_web_pages()
    test_frontend_functionality()
    
    print("\n" + "=" * 60)
    print("✅ 測試完成")
    print("\n建議檢查：")
    print("1. 打開瀏覽器訪問 http://localhost:5000")
    print("2. 查看首頁統計數據是否正確顯示")
    print("3. 點擊新聞列表查看是否有內容")
    print("4. 測試新聞詳情頁面功能")
