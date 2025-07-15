"""
測試爬蟲啟動修復後的功能
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_crawler_start_api():
    """測試爬蟲啟動 API"""
    print("🧪 測試爬蟲啟動 API...")
    
    try:
        # 測試爬蟲啟動端點
        response = requests.post(
            f"{BASE_URL}/api/v1/crawler/start",
            json={"use_mock": True},
            timeout=10
        )
        
        print(f"📊 狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API 回應成功")
            print(f"📋 狀態: {data.get('status')}")
            print(f"💬 訊息: {data.get('message')}")
            
            # 檢查數據結構
            if 'data' in data:
                result_data = data['data']
                print(f"📦 數據結構包含:")
                for key, value in result_data.items():
                    print(f"   - {key}: {value}")
                
                # 檢查前端期望的關鍵字段
                required_fields = ['total', 'new', 'duration']
                for field in required_fields:
                    if field in result_data:
                        print(f"✅ 包含前端期望字段 {field}: {result_data[field]}")
                    else:
                        print(f"❌ 缺少前端期望字段 {field}")
            else:
                print(f"❌ 缺少 data 結構")
                
        else:
            print(f"❌ API 錯誤: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ 請求失敗: {e}")

def test_crawler_status_api():
    """測試爬蟲狀態 API"""
    print("\n🔍 測試爬蟲狀態 API...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/crawler/status", timeout=10)
        print(f"📊 狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API 回應成功")
            
            if data.get('status') == 'success' and 'data' in data:
                status_data = data['data']
                required_fields = ['source_totals', 'recent_runs']
                
                for field in required_fields:
                    if field in status_data:
                        field_data = status_data[field]
                        print(f"✅ 包含 {field}: {type(field_data)} (長度: {len(field_data) if isinstance(field_data, list) else '非列表'})")
                        if isinstance(field_data, list) and field_data:
                            print(f"   - 第一個項目: {field_data[0]}")
                    else:
                        print(f"❌ 缺少 {field}")
            else:
                print(f"⚠️ 狀態 API 回應格式異常")
                
        else:
            print(f"❌ 狀態 API 錯誤: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ 狀態 API 請求失敗: {e}")

def test_web_page_response():
    """測試網頁回應時間"""
    print("\n🌐 測試爬蟲監控頁面...")
    
    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/monitor/crawler", timeout=10)
        end_time = time.time()
        
        print(f"📊 狀態碼: {response.status_code}")
        print(f"⏱️ 回應時間: {(end_time - start_time):.2f} 秒")
        
        if response.status_code == 200:
            content_length = len(response.text)
            print(f"✅ 頁面載入成功，內容長度: {content_length}")
            
            # 檢查是否包含修復的 JavaScript
            if "querySelectorAll('small')" in response.text:
                print("✅ JavaScript 選擇器已修復")
            else:
                print("⚠️ 可能還有 JavaScript 選擇器問題")
                
            if "resultData.total || 0" in response.text or "const total = resultData.total" in response.text:
                print("✅ 數據讀取保護已加入")
            else:
                print("⚠️ 可能還有數據讀取問題")
                
        else:
            print(f"❌ 頁面載入失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 頁面測試失敗: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 爬蟲修復驗證測試")
    print(f"⏰ 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 執行測試
    test_crawler_start_api()
    test_crawler_status_api()
    test_web_page_response()
    
    print("\n" + "=" * 60)
    print("🎯 修復驗證完成!")
    print("💡 請在瀏覽器中測試爬蟲啟動功能")
    print("📍 點擊'手動執行爬蟲'按鈕，確認不再出現錯誤")
    print("=" * 60)
