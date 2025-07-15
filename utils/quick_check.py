"""
快速系統狀態檢查與基本優化
Quick System Stat            # 檢查新聞來源分布 (檢查 source_id)
            cursor.execute("SELECT source_id, COUNT(*) FROM news GROUP BY source_id")
            sources = cursor.fetchall()
            print(f"  🌐 新聞來源: {len(sources)} 個")
            
            if sources:
                print("     來源統計:")
                for source_id, count in sources[:5]:  # 只顯示前5個
                    print(f"     - 來源ID {source_id}: {count} 篇")
                if len(sources) > 5:
                    print(f"     ... 還有 {len(sources) - 5} 個來源")d Basic Optimization
"""

import os
import sqlite3
import logging
from datetime import datetime, timedelta

print("🔍 台灣保險新聞聚合器 - 快速狀態檢查")
print("=" * 50)

# 1. 檢查資料庫狀態
print("\n📊 資料庫狀態檢查:")
try:
    if os.path.exists("instance/insurance_news.db"):
        conn = sqlite3.connect("instance/insurance_news.db")
        cursor = conn.cursor()
        
        # 檢查表格
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"  ✅ 資料庫連接正常，發現 {len(tables)} 個表格")
        
        # 檢查新聞數量
        if 'news' in tables:
            cursor.execute("SELECT COUNT(*) FROM news")
            total_news = cursor.fetchone()[0]
            print(f"  📰 總新聞數量: {total_news}")
            
            # 檢查今日新聞
            today = datetime.now().date()
            cursor.execute("SELECT COUNT(*) FROM news WHERE date(created_at) = ?", (today,))
            today_news = cursor.fetchone()[0]
            print(f"  📅 今日新聞: {today_news}")
            
            # 檢查新聞來源
            cursor.execute("SELECT source_id, COUNT(*) FROM news WHERE source_id IS NOT NULL GROUP BY source_id")
            sources = cursor.fetchall()
            print(f"  🌐 新聞來源: {len(sources)} 個")
            
            if sources:
                print("     來源統計:")
                for source_id, count in sources[:5]:  # 只顯示前5個
                    print(f"     - 來源ID {source_id}: {count} 篇")
                if len(sources) > 5:
                    print(f"     ... 還有 {len(sources) - 5} 個來源")
        
        conn.close()
    else:
        print("  ❌ 資料庫文件不存在")
        
except Exception as e:
    print(f"  ❌ 資料庫檢查失敗: {e}")

# 2. 檢查核心文件
print("\n📁 核心文件檢查:")
core_files = [
    "run.py",
    "config/settings.py",
    "database/models.py",
    "web/routes.py",
    "api/routes.py",
    "analyzer/engine.py",
    "crawler/engine.py"
]

for file_path in core_files:
    if os.path.exists(file_path):
        print(f"  ✅ {file_path}")
    else:
        print(f"  ❌ {file_path} - 文件缺失")

# 3. 檢查擴展文件
print("\n🔧 優化組件檢查:")
optimization_files = [
    "scheduler.py",
    "data_cleaner.py", 
    "integrated_crawler.py",
    "analyzer/cache.py",
    "analyzer/insurance_dictionary.py"
]

for file_path in optimization_files:
    if os.path.exists(file_path):
        print(f"  ✅ {file_path}")
    else:
        print(f"  ⚠️ {file_path} - 組件缺失")

# 4. 檢查日誌目錄
print("\n📝 日誌系統檢查:")
if os.path.exists("logs"):
    log_files = [f for f in os.listdir("logs") if f.endswith(".log")]
    print(f"  ✅ 日誌目錄存在，包含 {len(log_files)} 個日誌文件")
    
    # 檢查日誌文件大小
    for log_file in log_files[:3]:  # 只檢查前3個
        file_path = os.path.join("logs", log_file)
        size_mb = os.path.getsize(file_path) / 1024 / 1024
        print(f"     {log_file}: {size_mb:.1f} MB")
else:
    print("  ⚠️ 日誌目錄不存在")

# 5. 檢查Python依賴
print("\n🐍 Python依賴檢查:")
required_packages = [
    ("flask", "flask"),
    ("sqlite3", "sqlite3"), 
    ("requests", "requests"),
    ("beautifulsoup4", "bs4"),
    ("jieba", "jieba")
]

for package_name, import_name in required_packages:
    try:
        __import__(import_name)
        print(f"  ✅ {package_name}")
    except ImportError:
        print(f"  ❌ {package_name} - 需要安裝")

# 6. 系統建議
print("\n💡 系統建議:")

# 檢查是否需要優化
optimization_needed = []

# 檢查資料庫是否需要索引
try:
    if os.path.exists("instance/insurance_news.db"):
        conn = sqlite3.connect("instance/insurance_news.db")
        cursor = conn.cursor()
        
        # 檢查是否有索引
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = cursor.fetchall()
        
        if len(indexes) < 5:  # 基本索引數量
            optimization_needed.append("建議創建資料庫索引以提升查詢效能")
        
        # 檢查資料更新頻率
        cursor.execute("SELECT MAX(created_at) FROM news")
        latest = cursor.fetchone()[0]
        
        if latest:
            latest_date = datetime.fromisoformat(latest)
            hours_old = (datetime.now() - latest_date).total_seconds() / 3600
            
            if hours_old > 24:
                optimization_needed.append("新聞數據超過24小時未更新，建議執行爬蟲")
        
        conn.close()
        
except Exception as e:
    optimization_needed.append(f"資料庫檢查異常: {e}")

# 檢查日誌文件大小
if os.path.exists("logs"):
    for log_file in os.listdir("logs"):
        if log_file.endswith(".log"):
            file_path = os.path.join("logs", log_file)
            size_mb = os.path.getsize(file_path) / 1024 / 1024
            if size_mb > 50:
                optimization_needed.append(f"日誌文件 {log_file} 過大 ({size_mb:.1f}MB)，建議清理")

if optimization_needed:
    for suggestion in optimization_needed:
        print(f"  🔧 {suggestion}")
else:
    print("  ✅ 系統狀態良好，無需立即優化")

# 7. 快速操作建議
print("\n⚡ 快速操作建議:")
print("  1. 啟動應用: python run.py")
print("  2. 執行爬蟲: python integrated_crawler.py")
print("  3. 系統優化: python system_optimizer.py")
print("  4. 前端優化: python frontend_optimizer.py")
print("  5. 狀態檢查: python check_status.py")

print("\n" + "=" * 50)
print("✅ 快速狀態檢查完成")
