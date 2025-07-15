"""
手動觸發爬蟲腳本
Manual Crawler Trigger Script

用於手動執行爬蟲並應用7天日期過濾
"""

import sys
import os
import logging

# 添加專案根目錄到Python路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def trigger_crawler():
    """觸發爬蟲執行"""
    try:
        # 設置日誌
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        print("🚀 正在觸發爬蟲...")
        
        from crawler.manager import get_crawler_manager
        
        # 獲取爬蟲管理器
        manager = get_crawler_manager()
        
        # 檢查日期過濾器狀態
        print("\n📊 檢查日期過濾器狀態...")
        status = manager.get_crawler_status()
        filter_status = status.get('date_filter', {})
        
        print(f"  啟用: {'是' if filter_status.get('enabled', False) else '否'}")
        print(f"  最大天數: {filter_status.get('max_age_days', '未知')}")
        if filter_status.get('cutoff_date_formatted'):
            print(f"  截止日期: {filter_status['cutoff_date_formatted']}")
        
        # 執行爬蟲
        print("\n🕷️ 開始執行爬蟲...")
        result = manager.crawl_all_sources(use_mock=False)
        
        print(f"\n✅ 爬蟲執行完成!")
        print(f"📊 結果: {result.get('message', '未知')}")
        print(f"📈 統計: 總計處理 {result.get('total', 0)} 則新聞，實際保存 {result.get('new', 0)} 則")
        
        # 顯示詳細結果
        if 'results' in result:
            print("\n📋 各來源詳細結果:")
            for source_result in result['results']:
                source_name = source_result.get('source', '未知來源')
                success = source_result.get('success', False)
                news_count = source_result.get('news_count', 0)
                message = source_result.get('message', '')
                
                status_icon = "✅" if success else "❌"
                print(f"  {status_icon} {source_name}: {news_count} 則新聞 - {message}")
        
        return True
        
    except Exception as e:
        print(f"❌ 爬蟲執行失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database_news():
    """檢查資料庫中的新聞"""
    try:
        from datetime import datetime, timezone, timedelta
        from app import create_app
        from config.settings import Config
        from database.models import db, News
        
        app = create_app(Config)
        with app.app_context():
            # 查看最新的5則新聞
            print("\n📰 最新5則新聞:")
            latest_news = News.query.order_by(News.published_date.desc()).limit(5).all()
            for i, news in enumerate(latest_news, 1):
                days_ago = (datetime.now(timezone.utc) - news.published_date).days
                print(f"  {i}. {news.title[:60]}... ({days_ago}天前)")
            
            # 統計信息
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)
            recent_count = News.query.filter(News.published_date >= cutoff_date).count()
            total_count = News.query.count()
            
            print(f"\n📊 統計信息:")
            print(f"  總新聞數量: {total_count}")
            print(f"  7天內新聞: {recent_count}")
            print(f"  過期新聞: {total_count - recent_count}")
            
        return True
        
    except Exception as e:
        print(f"❌ 檢查資料庫失敗: {e}")
        return False

def main():
    """主程式"""
    print("🎯 手動爬蟲觸發器")
    print("=" * 50)
    
    # 觸發爬蟲
    if trigger_crawler():
        print("\n" + "=" * 50)
        # 檢查結果
        check_database_news()
        
        print("\n🎉 操作完成!")
        print("💡 提示: 現在重新整理網頁應該能看到最新的新聞了")
    else:
        print("\n❌ 爬蟲執行失敗，請檢查錯誤信息")

if __name__ == "__main__":
    main()
