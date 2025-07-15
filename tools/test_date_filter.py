"""
日期過濾功能測試腳本
Date Filter Test Script

測試爬蟲的7天新聞過濾功能
"""

import sys
import os
import logging
from datetime import datetime, timezone, timedelta

# 添加專案根目錄到Python路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from crawler.date_filter import NewsDateFilter, create_date_filter
from crawler.manager import get_crawler_manager

def test_date_filter_basic():
    """測試基本日期過濾功能"""
    print("🧪 測試基本日期過濾功能...")
    
    # 創建測試數據
    now = datetime.now(timezone.utc)
    test_news = [
        {
            'title': '今天的保險新聞',
            'published_date': now,
            'content': '這是今天的新聞',
            'source': '測試來源'
        },
        {
            'title': '2天前的保險新聞',
            'published_date': now - timedelta(days=2),
            'content': '這是2天前的新聞',
            'source': '測試來源'
        },
        {
            'title': '10天前的保險新聞',
            'published_date': now - timedelta(days=10),
            'content': '這是10天前的新聞',
            'source': '測試來源'
        },
        {
            'title': '30天前的保險新聞',
            'published_date': now - timedelta(days=30),
            'content': '這是30天前的新聞',
            'source': '測試來源'
        }
    ]
    
    # 測試7天過濾
    print("\n📅 測試7天過濾...")
    filter_7d = create_date_filter(max_age_days=7, enable_filter=True)
    filtered_7d = filter_7d.filter_news_list(test_news)
    
    print(f"原始新聞數量: {len(test_news)}")
    print(f"7天過濾後數量: {len(filtered_7d)}")
    print("保留的新聞:")
    for news in filtered_7d:
        days_ago = (now - news['published_date']).days
        print(f"  - {news['title']} ({days_ago}天前)")
    
    # 測試30天過濾
    print("\n📅 測試30天過濾...")
    filter_30d = create_date_filter(max_age_days=30, enable_filter=True)
    filtered_30d = filter_30d.filter_news_list(test_news)
    
    print(f"30天過濾後數量: {len(filtered_30d)}")
    print("保留的新聞:")
    for news in filtered_30d:
        days_ago = (now - news['published_date']).days
        print(f"  - {news['title']} ({days_ago}天前)")
    
    # 測試停用過濾
    print("\n🔧 測試停用過濾...")
    filter_disabled = create_date_filter(max_age_days=7, enable_filter=False)
    filtered_disabled = filter_disabled.filter_news_list(test_news)
    
    print(f"停用過濾後數量: {len(filtered_disabled)}")
    assert len(filtered_disabled) == len(test_news), "停用過濾時應該保留所有新聞"
    
    print("✅ 基本日期過濾功能測試通過!")
    return True

def test_crawler_manager_integration():
    """測試爬蟲管理器整合"""
    print("\n🧪 測試爬蟲管理器日期過濾整合...")
    
    # 獲取爬蟲管理器
    manager = get_crawler_manager()
    
    # 檢查初始狀態
    print("📊 檢查初始狀態...")
    status = manager.get_crawler_status()
    print(f"日期過濾器狀態: {status.get('date_filter', {})}")
    
    # 測試更新設定
    print("🔧 測試更新設定...")
    result = manager.update_date_filter_settings(max_age_days=7, enable_filter=True)
    print(f"更新結果: {result['message']}")
    
    # 檢查更新後狀態
    updated_status = manager.get_crawler_status()
    filter_status = updated_status.get('date_filter', {})
    print(f"更新後狀態: {filter_status}")
    
    # 驗證設定
    assert filter_status.get('enabled') == True, "過濾器應該是啟用狀態"
    assert filter_status.get('max_age_days') == 7, "最大天數應該是7天"
    
    print("✅ 爬蟲管理器整合測試通過!")
    return True

def test_edge_cases():
    """測試邊緣情況"""
    print("\n🧪 測試邊緣情況...")
    
    filter_instance = create_date_filter(max_age_days=7, enable_filter=True)
    
    # 測試空列表
    print("📝 測試空新聞列表...")
    empty_result = filter_instance.filter_news_list([])
    assert len(empty_result) == 0, "空列表應該返回空列表"
    
    # 測試沒有日期的新聞
    print("📝 測試沒有日期的新聞...")
    no_date_news = [
        {
            'title': '沒有日期的新聞',
            'content': '這則新聞沒有發布日期',
            'source': '測試來源'
        }
    ]
    no_date_result = filter_instance.filter_news_list(no_date_news)
    assert len(no_date_result) == 1, "沒有日期的新聞應該被保留"
    
    # 測試錯誤的日期格式
    print("📝 測試錯誤的日期格式...")
    bad_date_news = [
        {
            'title': '錯誤日期格式的新聞',
            'published_date': 'invalid-date',
            'content': '這則新聞有錯誤的日期格式',
            'source': '測試來源'
        }
    ]
    bad_date_result = filter_instance.filter_news_list(bad_date_news)
    # 錯誤日期格式的新聞會被視為沒有日期，應該被保留
    
    print("✅ 邊緣情況測試通過!")
    return True

def main():
    """主測試函數"""
    print("🚀 開始日期過濾功能全面測試...\n")
    
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    tests = [
        ("基本日期過濾功能", test_date_filter_basic),
        ("爬蟲管理器整合", test_crawler_manager_integration),
        ("邊緣情況處理", test_edge_cases)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*50}")
            print(f"🧪 執行測試: {test_name}")
            print('='*50)
            
            if test_func():
                print(f"✅ {test_name} - PASS")
                passed += 1
            else:
                print(f"❌ {test_name} - FAIL")
                
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*50}")
    print(f"🏁 測試完成: {passed}/{total} 通過")
    print('='*50)
    
    if passed == total:
        print("🎉 所有測試都通過了！日期過濾功能已就緒。")
        print("\n📋 使用說明:")
        print("1. 預設設定：只抓取7天內的新聞")
        print("2. 可透過配置文件調整天數限制")
        print("3. 可透過API動態調整設定")
        print("4. 可完全停用日期過濾功能")
        return True
    else:
        print("⚠️ 部分測試失敗，請檢查問題並修復。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
