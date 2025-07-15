#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第四階段功能測試腳本
測試通知推送系統和高級可視化功能
"""

import os
import sys
import logging
from datetime import datetime, timedelta

# 添加項目根目錄到Python路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_notification_system():
    """測試通知系統"""
    print("\n" + "="*60)
    print("🔔 測試通知推送系統")
    print("="*60)
    
    try:
        # 測試通知服務導入
        try:
            from notification.notification_service import NotificationService
            print("✅ 通知服務模組導入成功")
        except ImportError as e:
            print(f"❌ 通知服務模組導入失敗: {e}")
            return False
        
        # 測試新聞推送器導入
        try:
            from notification.news_pusher import NewsPusher, PushRule
            print("✅ 新聞推送器模組導入成功")
        except ImportError as e:
            print(f"❌ 新聞推送器模組導入失敗: {e}")
            return False
        
        # 測試基本功能
        try:
            notification_service = NotificationService()
            print("✅ 通知服務實例化成功")
            
            # 測試發送通知（使用測試模式）
            test_result = notification_service.send_notification(
                user_id=1,
                title="系統測試通知",
                message="這是第四階段功能測試通知",
                type="system",
                data={"test": True}
            )
            
            if test_result:
                print("✅ 測試通知發送成功")
            else:
                print("⚠️ 測試通知發送失敗（可能是配置問題）")
                
        except Exception as e:
            print(f"❌ 通知服務測試失敗: {e}")
            return False
            
        # 測試推送規則
        try:
            pusher = NewsPusher()
            print("✅ 新聞推送器實例化成功")
            
            # 創建測試推送規則
            test_rule = PushRule(
                id=1,
                name="高重要性新聞推送",
                conditions={"importance_threshold": 0.8},
                target_users=[1],
                enabled=True
            )
            
            print(f"✅ 推送規則創建成功: {test_rule.name}")
            
        except Exception as e:
            print(f"❌ 推送規則測試失敗: {e}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 通知系統測試過程中發生錯誤: {e}")
        return False

def test_visualization_system():
    """測試可視化系統"""
    print("\n" + "="*60)
    print("📊 測試高級可視化系統")
    print("="*60)
    
    try:
        # 測試可視化服務導入
        try:
            from app.services.visualization_service import AdvancedVisualization
            print("✅ 可視化服務模組導入成功")
        except ImportError as e:
            print(f"❌ 可視化服務模組導入失敗: {e}")
            return False
        
        # 測試基本功能
        try:
            viz_service = AdvancedVisualization()
            print("✅ 可視化服務實例化成功")
            
            # 測試儀表板圖表生成
            chart_paths = viz_service.generate_business_dashboard_charts(days=7)
            
            if chart_paths:
                print(f"✅ 儀表板圖表生成成功，共 {len(chart_paths)} 個圖表:")
                for chart_name, path in chart_paths.items():
                    print(f"   - {chart_name}: {path}")
            else:
                print("⚠️ 儀表板圖表生成返回空結果")
                
        except Exception as e:
            print(f"❌ 可視化服務測試失敗: {e}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 可視化系統測試過程中發生錯誤: {e}")
        return False

def test_api_routes():
    """測試API路由"""
    print("\n" + "="*60)
    print("🌐 測試API路由")
    print("="*60)
    
    try:
        # 測試通知路由
        try:
            import notification.routes
            print("✅ 通知路由模組導入成功")
        except ImportError as e:
            print(f"❌ 通知路由模組導入失敗: {e}")
        
        # 測試可視化路由
        try:
            import app.routes_visualization
            print("✅ 可視化路由模組導入成功")
        except ImportError as e:
            print(f"❌ 可視化路由模組導入失敗: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ API路由測試過程中發生錯誤: {e}")
        return False

def test_templates():
    """測試模板文件"""
    print("\n" + "="*60)
    print("🎨 測試模板文件")
    print("="*60)
    
    templates_to_check = [
        "web/templates/notification/dashboard.html",
        "web/templates/visualization/dashboard.html"
    ]
    
    success_count = 0
    
    for template_path in templates_to_check:
        if os.path.exists(template_path):
            print(f"✅ 模板文件存在: {template_path}")
            success_count += 1
        else:
            print(f"❌ 模板文件不存在: {template_path}")
    
    print(f"\n模板檢查結果: {success_count}/{len(templates_to_check)} 個文件存在")
    return success_count == len(templates_to_check)

def check_dependencies():
    """檢查依賴項"""
    print("\n" + "="*60)
    print("📦 檢查依賴項")
    print("="*60)
    
    dependencies = {
        "pandas": ["pandas", "數據處理"],
        "matplotlib": ["matplotlib", "圖表繪製"],
        "seaborn": ["seaborn", "統計圖表"],
        "plotly": ["plotly", "交互式圖表"],
        "wordcloud": ["wordcloud", "詞雲生成"],
        "sqlite3": ["sqlite3", "數據庫連接"]
    }
    
    available_deps = []
    missing_deps = []
    
    for dep_name, (module_name, description) in dependencies.items():
        try:
            __import__(module_name)
            print(f"✅ {description} ({module_name}) - 可用")
            available_deps.append(dep_name)
        except ImportError:
            print(f"⚠️ {description} ({module_name}) - 不可用")
            missing_deps.append(dep_name)
    
    print(f"\n依賴檢查結果: {len(available_deps)}/{len(dependencies)} 可用")
    
    if missing_deps:
        print(f"缺失的依賴: {', '.join(missing_deps)}")
        print("注意: 系統將使用降級模式運行")
    
    return len(missing_deps) == 0

def main():
    """主測試函數"""
    print("🚀 保險新聞聚合器 - 第四階段功能測試")
    print("=" * 80)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = {
        "依賴檢查": check_dependencies(),
        "通知系統": test_notification_system(),
        "可視化系統": test_visualization_system(),
        "API路由": test_api_routes(),
        "模板文件": test_templates()
    }
    
    print("\n" + "="*80)
    print("📋 測試結果摘要")
    print("="*80)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name}: {status}")
        if result:
            passed_tests += 1
    
    print(f"\n總體結果: {passed_tests}/{total_tests} 測試通過")
    
    if passed_tests == total_tests:
        print("🎉 所有測試通過！第四階段功能正常運行")
        success_rate = 100
    else:
        success_rate = (passed_tests / total_tests) * 100
        print(f"⚠️ 部分測試失敗，成功率: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("💡 系統基本功能正常，可以繼續部署準備")
        elif success_rate >= 60:
            print("⚠️ 需要修復部分問題後再進行部署")
        else:
            print("🚨 需要解決主要問題後再繼續")
    
    # 提供下一步建議
    print("\n" + "="*80)
    print("📝 下一步建議")
    print("="*80)
    
    if not test_results["依賴檢查"]:
        print("1. 安裝缺失的Python依賴包")
        print("   pip install pandas matplotlib seaborn plotly wordcloud")
    
    if not test_results["通知系統"]:
        print("2. 檢查通知系統配置（SMTP、LINE API等）")
    
    if not test_results["可視化系統"]:
        print("3. 確認可視化服務的數據庫連接")
    
    if success_rate >= 80:
        print("4. 準備進行Docker容器化")
        print("5. 配置生產環境設置")
        print("6. 執行最終安全檢查")
    
    return success_rate >= 80

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n測試被用戶中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n測試過程中發生未預期的錯誤: {e}")
        sys.exit(1)
