#!/usr/bin/env python3
"""
新聞列表功能測試腳本
"""

import requests
import time
from bs4 import BeautifulSoup

def test_news_list_functionality():
    """測試新聞列表頁的各項功能"""
    base_url = "http://localhost:5000"
    
    print("🧪 開始測試新聞列表功能...")
    
    # 等待服務器啟動
    print("⏳ 等待服務器啟動...")
    time.sleep(3)
    
    try:
        # 1. 測試基本新聞列表頁
        print("\n1️⃣ 測試基本新聞列表頁...")
        response = requests.get(f"{base_url}/news")
        print(f"   狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 檢查篩選表單
            category_filter = soup.find('select', {'id': 'categoryFilter'})
            source_filter = soup.find('select', {'id': 'sourceFilter'})
            sort_filter = soup.find('select', {'id': 'sortFilter'})
            search_input = soup.find('input', {'id': 'searchInput'})
            
            print(f"   ✅ 分類下拉選單: {'存在' if category_filter else '❌ 不存在'}")
            print(f"   ✅ 來源下拉選單: {'存在' if source_filter else '❌ 不存在'}")
            print(f"   ✅ 排序下拉選單: {'存在' if sort_filter else '❌ 不存在'}")
            print(f"   ✅ 搜尋輸入框: {'存在' if search_input else '❌ 不存在'}")
            
            # 檢查分類選項是否為動態生成
            if category_filter:
                options = category_filter.find_all('option')
                print(f"   📊 分類選項數量: {len(options)}")
                for option in options[:5]:  # 只顯示前5個選項
                    if option.get('value'):
                        print(f"      - {option.get('value')}")
            
            # 檢查來源選項是否為動態生成
            if source_filter:
                options = source_filter.find_all('option')
                print(f"   📰 來源選項數量: {len(options)}")
                for option in options[:5]:  # 只顯示前5個選項
                    if option.get('value'):
                        print(f"      - {option.get('value')}")
            
            # 檢查新聞卡片
            news_cards = soup.find_all('div', class_='news-card')
            print(f"   📄 新聞卡片數量: {len(news_cards)}")
            
        # 2. 測試分類篩選
        print("\n2️⃣ 測試分類篩選...")
        response = requests.get(f"{base_url}/news?category=保險新聞")
        print(f"   分類篩選狀態碼: {response.status_code}")
        
        # 3. 測試來源篩選
        print("\n3️⃣ 測試來源篩選...")
        response = requests.get(f"{base_url}/news?source=Google新聞-保險")
        print(f"   來源篩選狀態碼: {response.status_code}")
        
        # 4. 測試搜尋功能
        print("\n4️⃣ 測試搜尋功能...")
        response = requests.get(f"{base_url}/news?search=保險")
        print(f"   搜尋功能狀態碼: {response.status_code}")
        
        # 5. 測試排序功能
        print("\n5️⃣ 測試排序功能...")
        response = requests.get(f"{base_url}/news?sort=view")
        print(f"   排序功能狀態碼: {response.status_code}")
        
        # 6. 測試組合篩選
        print("\n6️⃣ 測試組合篩選...")
        response = requests.get(f"{base_url}/news?category=保險新聞&sort=date&search=台灣")
        print(f"   組合篩選狀態碼: {response.status_code}")
        
        # 7. 測試分頁功能
        print("\n7️⃣ 測試分頁功能...")
        response = requests.get(f"{base_url}/news?page=2")
        print(f"   分頁功能狀態碼: {response.status_code}")
        
        print("\n✅ 新聞列表功能測試完成!")
        print("📝 建議：開啟瀏覽器訪問 http://localhost:5000/news 查看實際效果")
        
    except requests.exceptions.ConnectionError:
        print("❌ 無法連接到服務器，請確保應用正在運行")
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")

if __name__ == "__main__":
    test_news_list_functionality()
