"""
手動添加測試新聞
Manual Test News Addition
"""

import sqlite3
import os
from datetime import datetime, timezone

def add_test_news():
    """手動添加測試新聞到資料庫"""
    try:
        # 找到資料庫
        db_path = "instance/insurance_news.db"
        if not os.path.exists(db_path):
            db_path = "instance/dev_insurance_news.db"
        
        if not os.path.exists(db_path):
            print("❌ 找不到資料庫檔案")
            return False
        
        print(f"📂 使用資料庫: {db_path}")
        
        # 連接資料庫
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 準備測試新聞數據（今天的新聞）
        now = datetime.now(timezone.utc).isoformat()
        test_news = [
            {
                'title': f'【測試】2025年7月9日最新保險政策更新 - {datetime.now().strftime("%H:%M")}',
                'summary': '金管會今日宣布多項保險業新政策，包括提高保險保障額度、簡化理賠程序等重要措施。',
                'content': '金融監督管理委員會今日召開記者會，宣布實施多項保險業新政策。新政策主要包括：1. 提高人壽保險最高保障額度至新台幣5000萬元；2. 簡化理賠申請程序，縮短理賠處理時間；3. 強化保險業者財務監理機制。這些措施預計將於本月底開始實施，有助於提升保險業服務品質和消費者權益保障。',
                'url': f'https://example.com/test-news-{datetime.now().strftime("%Y%m%d%H%M")}',
                'source_id': 4,
                'category_id': 1
            },
            {
                'title': f'【測試】台灣保險業數位轉型成效顯著 - {datetime.now().strftime("%H:%M")}',
                'summary': '根據最新統計，台灣保險業在數位轉型方面取得重大進展，線上投保率較去年同期成長超過50%。',
                'content': '台灣保險暨金融發展中心今日發布「2025年台灣保險業數位轉型報告」。報告顯示，台灣保險業在數位轉型方面成效卓著：線上投保率成長52%、數位理賠處理時間縮短40%、客戶滿意度提升至85%。主要保險公司紛紛投入AI客服、區塊鏈理賠等創新技術，為保險業發展注入新動能。',
                'url': f'https://example.com/test-news-digital-{datetime.now().strftime("%Y%m%d%H%M")}',
                'source_id': 4,
                'category_id': 1
            },
            {
                'title': f'【測試】長照險需求激增，業者積極推出新商品 - {datetime.now().strftime("%H:%M")}',
                'summary': '隨著台灣進入超高齡社會，長期照護保險需求快速增長，各大保險公司紛紛推出創新長照險商品。',
                'content': '台灣即將邁入超高齡社會，長期照護需求日益增加。根據保險業者統計，長照險投保率較去年成長35%。富邦人壽、國泰人壽、新光人壽等主要業者紛紛推出新型長照險商品，包括「預防型長照險」、「家庭照護險」等創新產品，提供更全面的照護保障。專家建議民眾及早規劃長照保險，為未來生活建立安全網。',
                'url': f'https://example.com/test-news-longcare-{datetime.now().strftime("%Y%m%d%H%M")}',
                'source_id': 4,
                'category_id': 1
            }
        ]
        
        saved_count = 0
        
        for news_data in test_news:
            try:
                # 檢查是否已存在相同標題的新聞
                cursor.execute("SELECT id FROM news WHERE title = ?", (news_data['title'],))
                if cursor.fetchone():
                    print(f"  跳過重複: {news_data['title'][:50]}...")
                    continue
                
                # 插入新聞
                cursor.execute("""
                    INSERT INTO news (
                        title, content, summary, url, source_id, category_id,
                        published_date, crawled_date, importance_score, 
                        sentiment_score, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    news_data['title'],
                    news_data['content'],
                    news_data['summary'],
                    news_data['url'],
                    news_data['source_id'],
                    news_data['category_id'],
                    now,  # published_date
                    now,  # crawled_date
                    0.8,  # importance_score
                    0.1,  # sentiment_score
                    'active',
                    now,  # created_at
                    now   # updated_at
                ))
                
                saved_count += 1
                print(f"  ✅ 添加: {news_data['title'][:50]}...")
                
            except Exception as e:
                print(f"  ❌ 添加失敗: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ 成功添加 {saved_count} 則測試新聞")
        
        if saved_count > 0:
            print("🎉 測試新聞已添加！現在重新整理網頁應該能看到最新的新聞")
            return True
        else:
            print("⚠️ 沒有新的測試新聞被添加")
            return False
            
    except Exception as e:
        print(f"❌ 添加測試新聞失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_addition():
    """驗證新聞是否成功添加"""
    try:
        db_path = "instance/insurance_news.db"
        if not os.path.exists(db_path):
            db_path = "instance/dev_insurance_news.db"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查看今天添加的新聞
        cursor.execute("""
            SELECT id, title, crawled_date 
            FROM news 
            WHERE date(crawled_date) = date('now')
            ORDER BY crawled_date DESC
        """)
        
        today_news = cursor.fetchall()
        
        print(f"\n📰 今天添加的新聞 ({len(today_news)} 則):")
        for i, (news_id, title, crawled_date) in enumerate(today_news, 1):
            print(f"  {i}. ID:{news_id} - {title}")
            print(f"     時間: {crawled_date}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 驗證失敗: {e}")

def main():
    """主程式"""
    print("🎯 手動添加測試新聞")
    print("=" * 50)
    
    if add_test_news():
        verify_addition()
        print("\n💡 提示: 請重新整理您的網頁，應該能看到這些最新的測試新聞")
    else:
        print("\n❌ 添加失敗")

if __name__ == "__main__":
    main()
