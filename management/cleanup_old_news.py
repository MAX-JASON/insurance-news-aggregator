#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清理舊新聞腳本
Clean up old news script

刪除超過指定天數的新聞，保持資料庫整潔
"""

import os
import sys
import sqlite3
from datetime import datetime, timedelta, timezone
import argparse

def cleanup_old_news(max_age_days=7, dry_run=False):
    """
    清理超過指定天數的舊新聞
    
    Args:
        max_age_days (int): 保留新聞的最大天數
        dry_run (bool): 是否為試運行（只顯示將要刪除的新聞，不實際刪除）
    """
    
    # 找到資料庫檔案
    db_path = "instance/insurance_news.db"
    if not os.path.exists(db_path):
        db_path = "instance/dev_insurance_news.db"
    
    if not os.path.exists(db_path):
        print("❌ 找不到資料庫檔案")
        return False
    
    print(f"📂 使用資料庫: {db_path}")
    print(f"🗓️  保留天數: {max_age_days} 天")
    print(f"🔍 模式: {'試運行' if dry_run else '實際執行'}")
    print("=" * 60)
    
    try:
        # 連接資料庫
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 計算截止日期
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=max_age_days)).isoformat()
        
        # 查找要刪除的新聞
        cursor.execute("""
            SELECT id, title, published_date, crawled_date 
            FROM news 
            WHERE (published_date < ? OR crawled_date < ?)
            AND status = 'active'
            ORDER BY published_date DESC
        """, (cutoff_date, cutoff_date))
        
        old_news = cursor.fetchall()
        
        if not old_news:
            print("✅ 沒有找到需要清理的舊新聞")
            return True
        
        print(f"🔍 找到 {len(old_news)} 條超過 {max_age_days} 天的舊新聞:")
        print()
        
        # 顯示將要刪除的新聞
        for i, (news_id, title, pub_date, crawl_date) in enumerate(old_news, 1):
            print(f"  {i:3d}. ID:{news_id}")
            print(f"       標題: {title[:50]}...")
            print(f"       發布: {pub_date or '未知'}")
            print(f"       爬取: {crawl_date or '未知'}")
            print()
        
        if dry_run:
            print("🔍 這是試運行，沒有實際刪除任何新聞")
            print("💡 如要實際執行刪除，請運行: python cleanup_old_news.py --execute")
        else:
            # 確認刪除
            print(f"⚠️  即將刪除 {len(old_news)} 條舊新聞")
            response = input("確定要繼續嗎？(輸入 'yes' 確認): ")
            
            if response.lower() != 'yes':
                print("❌ 取消刪除操作")
                return False
            
            # 執行刪除
            news_ids = [str(news_id) for news_id, _, _, _ in old_news]
            placeholders = ','.join(['?'] * len(news_ids))
            
            # 軟刪除（標記為 deleted 而不是實際刪除）
            cursor.execute(f"""
                UPDATE news 
                SET status = 'deleted', updated_at = ?
                WHERE id IN ({placeholders})
            """, [datetime.now(timezone.utc).isoformat()] + news_ids)
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            print(f"✅ 成功刪除 {deleted_count} 條舊新聞")
        
        # 顯示清理後的統計
        cursor.execute("SELECT COUNT(*) FROM news WHERE status = 'active'")
        active_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM news WHERE status = 'deleted'")
        deleted_count = cursor.fetchone()[0]
        
        print(f"\n📊 清理後統計:")
        print(f"   活躍新聞: {active_count}")
        print(f"   已刪除:   {deleted_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 清理失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_by_count(keep_count=100):
    """
    按數量清理新聞，只保留最新的指定數量
    
    Args:
        keep_count (int): 要保留的新聞數量
    """
    
    # 找到資料庫檔案
    db_path = "instance/insurance_news.db"
    if not os.path.exists(db_path):
        db_path = "instance/dev_insurance_news.db"
    
    if not os.path.exists(db_path):
        print("❌ 找不到資料庫檔案")
        return False
    
    print(f"📂 使用資料庫: {db_path}")
    print(f"📊 保留數量: {keep_count} 條最新新聞")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 找到要保留的新聞ID
        cursor.execute("""
            SELECT id FROM news 
            WHERE status = 'active'
            ORDER BY published_date DESC, crawled_date DESC
            LIMIT ?
        """, (keep_count,))
        
        keep_ids = [str(row[0]) for row in cursor.fetchall()]
        
        if len(keep_ids) <= keep_count:
            print("✅ 新聞數量未超過限制，無需清理")
            return True
        
        # 刪除不在保留列表中的新聞
        placeholders = ','.join(['?'] * len(keep_ids))
        cursor.execute(f"""
            UPDATE news 
            SET status = 'deleted', updated_at = ?
            WHERE status = 'active' AND id NOT IN ({placeholders})
        """, [datetime.now(timezone.utc).isoformat()] + keep_ids)
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"✅ 成功刪除 {deleted_count} 條舊新聞，保留最新 {len(keep_ids)} 條")
        return True
        
    except Exception as e:
        print(f"❌ 清理失敗: {e}")
        return False

def main():
    """主程式"""
    parser = argparse.ArgumentParser(description='清理舊新聞')
    parser.add_argument('--days', type=int, default=7, help='保留新聞的天數 (預設: 7)')
    parser.add_argument('--execute', action='store_true', help='實際執行刪除 (預設為試運行)')
    parser.add_argument('--by-count', type=int, help='按數量清理，只保留指定數量的最新新聞')
    
    args = parser.parse_args()
    
    print("🧹 保險新聞聚合器 - 舊新聞清理工具")
    print("=" * 60)
    
    if args.by_count:
        # 按數量清理
        success = cleanup_by_count(args.by_count)
    else:
        # 按日期清理
        success = cleanup_old_news(args.days, not args.execute)
    
    if success:
        print("\n🎉 清理完成！")
        if not args.execute and not args.by_count:
            print("💡 提示: 如要實際執行刪除，請加上 --execute 參數")
    else:
        print("\n❌ 清理失敗")
        sys.exit(1)

if __name__ == "__main__":
    main()
