"""
日期過濾器配置工具
Date Filter Configuration Tool

用於配置爬蟲的新聞時間限制
"""

import sys
import os
import yaml
import json
from pathlib import Path

# 添加專案根目錄到Python路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def load_config():
    """載入現有配置"""
    config_path = Path(project_root) / 'config' / 'config.yaml'
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"❌ 無法載入配置文件: {e}")
        return {}

def save_config(config):
    """儲存配置"""
    config_path = Path(project_root) / 'config' / 'config.yaml'
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        return True
    except Exception as e:
        print(f"❌ 無法儲存配置文件: {e}")
        return False

def show_current_settings():
    """顯示目前設定"""
    config = load_config()
    crawler_config = config.get('crawler', {})
    
    print("📋 目前的日期過濾設定:")
    print("="*40)
    print(f"最大新聞天數: {crawler_config.get('max_news_age_days', 7)} 天")
    print(f"啟用日期過濾: {'是' if crawler_config.get('enable_date_filter', True) else '否'}")
    print("="*40)

def configure_date_filter():
    """互動式配置日期過濾器"""
    print("🔧 配置爬蟲日期過濾器")
    print("="*40)
    
    config = load_config()
    if 'crawler' not in config:
        config['crawler'] = {}
    
    crawler_config = config['crawler']
    
    # 設定最大天數
    current_days = crawler_config.get('max_news_age_days', 7)
    print(f"\n📅 設定新聞時間限制 (目前: {current_days} 天)")
    print("建議選項:")
    print("  1 - 只抓取今天的新聞")
    print("  3 - 抓取3天內的新聞")
    print("  7 - 抓取7天內的新聞 (預設)")
    print("  14 - 抓取14天內的新聞")
    print("  30 - 抓取30天內的新聞")
    
    while True:
        try:
            days_input = input(f"\n請輸入天數 (1-365，預設 {current_days}): ").strip()
            if not days_input:
                days = current_days
                break
            
            days = int(days_input)
            if 1 <= days <= 365:
                break
            else:
                print("❌ 請輸入1-365之間的數字")
        except ValueError:
            print("❌ 請輸入有效的數字")
    
    crawler_config['max_news_age_days'] = days
    
    # 設定是否啟用過濾
    current_enabled = crawler_config.get('enable_date_filter', True)
    print(f"\n🔄 是否啟用日期過濾 (目前: {'啟用' if current_enabled else '停用'})")
    print("  y/yes - 啟用日期過濾")
    print("  n/no - 停用日期過濾 (抓取所有新聞)")
    
    while True:
        enable_input = input(f"\n啟用日期過濾? (y/n，預設 {'y' if current_enabled else 'n'}): ").strip().lower()
        if not enable_input:
            enabled = current_enabled
            break
        
        if enable_input in ['y', 'yes', 'true']:
            enabled = True
            break
        elif enable_input in ['n', 'no', 'false']:
            enabled = False
            break
        else:
            print("❌ 請輸入 y/yes 或 n/no")
    
    crawler_config['enable_date_filter'] = enabled
    
    # 顯示新設定
    print("\n📋 新的設定:")
    print("="*40)
    print(f"最大新聞天數: {days} 天")
    print(f"啟用日期過濾: {'是' if enabled else '否'}")
    
    if enabled:
        print(f"\n📝 說明: 爬蟲將只抓取{days}天內發布的新聞")
        if days <= 1:
            print("⚠️  注意: 只抓取今天的新聞可能會讓新聞數量很少")
        elif days <= 3:
            print("ℹ️  適用於: 需要最新新聞的場景")
        elif days <= 7:
            print("ℹ️  適用於: 一般使用，平衡新聞時效性和數量")
        elif days <= 14:
            print("ℹ️  適用於: 需要較多歷史新聞的場景")
        else:
            print("ℹ️  適用於: 需要大量歷史資料的分析場景")
    else:
        print("\n📝 說明: 爬蟲將抓取所有找到的新聞，不限制時間")
        print("⚠️  注意: 這可能會導致大量舊新聞被重複抓取")
    
    print("="*40)
    
    # 確認儲存
    while True:
        save_input = input("\n💾 儲存這些設定? (y/n): ").strip().lower()
        if save_input in ['y', 'yes']:
            if save_config(config):
                print("✅ 設定已儲存!")
                return True
            else:
                print("❌ 儲存失敗!")
                return False
        elif save_input in ['n', 'no']:
            print("❌ 設定未儲存")
            return False
        else:
            print("❌ 請輸入 y 或 n")

def test_configuration():
    """測試配置"""
    print("\n🧪 測試配置...")
    
    try:
        from crawler.date_filter import NewsDateFilter
        
        filter_instance = NewsDateFilter()
        status = filter_instance.get_status()
        
        print("📊 日期過濾器狀態:")
        print(f"  啟用: {'是' if status['enabled'] else '否'}")
        print(f"  最大天數: {status['max_age_days']}")
        print(f"  截止日期: {status['cutoff_date_formatted']}")
        
        print("✅ 配置測試成功!")
        return True
        
    except Exception as e:
        print(f"❌ 配置測試失敗: {e}")
        return False

def main():
    """主程式"""
    print("🚀 保險新聞聚合器 - 日期過濾器配置工具")
    print("="*50)
    
    while True:
        print("\n📋 請選擇操作:")
        print("  1 - 查看目前設定")
        print("  2 - 配置日期過濾器")
        print("  3 - 測試配置")
        print("  4 - 退出")
        
        choice = input("\n請選擇 (1-4): ").strip()
        
        if choice == '1':
            show_current_settings()
        elif choice == '2':
            configure_date_filter()
        elif choice == '3':
            test_configuration()
        elif choice == '4':
            print("👋 再見!")
            break
        else:
            print("❌ 無效選擇，請輸入 1-4")

if __name__ == "__main__":
    main()
