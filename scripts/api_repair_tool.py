#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API端點修復工具
API Endpoint Repair Tool

專門修復前端404 API錯誤的工具
"""

import os
import sys
import json
import requests
import time
from datetime import datetime

# 設置路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_api_endpoint(url, description=""):
    """測試單個API端點"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {description}: {url} - 正常 (200)")
            return True
        else:
            print(f"❌ {description}: {url} - 錯誤 ({response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {description}: {url} - 連接失敗 ({str(e)})")
        return False

def test_all_api_endpoints():
    """測試所有關鍵API端點"""
    base_url = "http://localhost:5000"
    
    # 要測試的端點列表
    endpoints = [
        ("/api/health", "健康檢查"),
        ("/api/v1/stats", "統計數據"),
        ("/api/v1/crawler/status", "爬蟲狀態"),
        ("/api/v1/crawler/sources", "爬蟲來源"),
        ("/monitor/api/crawler/status", "監控爬蟲狀態"),
        ("/monitor/api/news/stats", "監控新聞統計"),
        ("/api/crawler/status", "爬蟲狀態V2"),
        ("/api/business/category-news", "業務分類新聞"),
        ("/api/cyber-news", "賽博新聞"),
        ("/api/cyber-clients", "賽博客戶"),
        ("/api/cyber-stats", "賽博統計")
    ]
    
    print("🔍 測試API端點可用性...")
    print("=" * 60)
    
    success_count = 0
    total_count = len(endpoints)
    
    for endpoint, description in endpoints:
        url = base_url + endpoint
        if test_api_endpoint(url, description):
            success_count += 1
        time.sleep(0.5)  # 避免請求過快
    
    print("=" * 60)
    print(f"📊 測試結果: {success_count}/{total_count} 個端點正常")
    
    if success_count == total_count:
        print("🎉 所有API端點工作正常！")
        return True
    else:
        print("⚠️ 部分API端點有問題，但系統會自動處理")
        return False

def check_server_status():
    """檢查服務器是否運行"""
    try:
        response = requests.get("http://localhost:5000/", timeout=3)
        if response.status_code in [200, 404]:  # 404也表示服務器在運行
            print("✅ 服務器正在運行")
            return True
        else:
            print(f"⚠️ 服務器響應異常: {response.status_code}")
            return False
    except:
        print("❌ 服務器未運行或無法連接")
        return False

def create_api_test_report():
    """創建API測試報告"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"api_test_report_{timestamp}.json"
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "server_status": check_server_status(),
        "endpoint_tests": []
    }
    
    if report["server_status"]:
        base_url = "http://localhost:5000"
        endpoints = [
            ("/api/health", "健康檢查"),
            ("/api/v1/stats", "統計數據"),
            ("/api/v1/crawler/status", "爬蟲狀態"),
            ("/api/v1/crawler/sources", "爬蟲來源")
        ]
        
        for endpoint, description in endpoints:
            url = base_url + endpoint
            try:
                response = requests.get(url, timeout=5)
                test_result = {
                    "endpoint": endpoint,
                    "description": description,
                    "url": url,
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "response_time": response.elapsed.total_seconds(),
                    "error": None
                }
                if response.status_code == 200:
                    try:
                        test_result["response_data"] = response.json()
                    except:
                        test_result["response_data"] = response.text[:200]
            except Exception as e:
                test_result = {
                    "endpoint": endpoint,
                    "description": description,
                    "url": url,
                    "status_code": None,
                    "success": False,
                    "response_time": None,
                    "error": str(e)
                }
            
            report["endpoint_tests"].append(test_result)
    
    # 保存報告
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"📄 測試報告已保存: {report_file}")
    except Exception as e:
        print(f"⚠️ 無法保存測試報告: {e}")
    
    return report

def show_troubleshooting_guide():
    """顯示除錯指南"""
    print("\n🔧 API端點除錯指南")
    print("=" * 40)
    print("1. 如果看到404錯誤：")
    print("   - 確保使用 test_cyberpunk_ui.py 啟動")
    print("   - 檢查服務器視窗是否顯示錯誤")
    print("   - 重新啟動應用程式")
    print()
    print("2. 如果看到500錯誤：")
    print("   - 檢查資料庫是否存在")
    print("   - 查看服務器日誌訊息")
    print("   - 確認依賴套件已安裝")
    print()
    print("3. 如果連接失敗：")
    print("   - 確認服務器正在運行")
    print("   - 檢查防火牆設置")
    print("   - 嘗試使用 http://127.0.0.1:5000 替代")
    print()
    print("4. 推薦啟動順序：")
    print("   - 運行: python test_cyberpunk_ui.py")
    print("   - 等待: 看到 '賽博朋克系統啟動完成'")
    print("   - 測試: python api_repair_tool.py")
    print("   - 瀏覽: http://localhost:5000/business/cyber-news")

def main():
    """主函數"""
    print("🤖 API端點修復工具")
    print("=" * 40)
    print("此工具將檢查並診斷API端點問題")
    print()
    
    # 檢查服務器狀態
    print("🔍 步驟1: 檢查服務器狀態")
    server_running = check_server_status()
    
    if not server_running:
        print()
        print("❌ 服務器未運行！")
        print("💡 請先運行以下命令啟動服務器：")
        print("   python test_cyberpunk_ui.py")
        print("   或")
        print("   雙擊 UI啟動.bat")
        print()
        show_troubleshooting_guide()
        return 1
    
    print()
    print("🔍 步驟2: 測試API端點")
    api_success = test_all_api_endpoints()
    
    print()
    print("🔍 步驟3: 生成測試報告")
    report = create_api_test_report()
    
    print()
    if api_success:
        print("🎉 所有系統正常！前端應該不會出現404錯誤了。")
    else:
        print("⚠️ 部分API端點有問題，但賽博朋克啟動器包含備用方案。")
        print("💡 建議使用 test_cyberpunk_ui.py 啟動以獲得最佳體驗。")
    
    print()
    show_troubleshooting_guide()
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n👋 測試已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 工具執行失敗: {e}")
        sys.exit(1)
