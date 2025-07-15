"""
資料庫修復工具
Database Repair Tool

修復資料庫連接和路徑問題
"""
import os
import sys
import sqlite3
from pathlib import Path

def test_database_connection():
    """測試資料庫連接"""
    print("🔍 測試資料庫連接...")
    
    # 獲取專案根目錄
    base_dir = Path(__file__).parent.absolute()
    instance_dir = base_dir / "instance"
    
    print(f"📁 專案根目錄: {base_dir}")
    print(f"📁 Instance目錄: {instance_dir}")
    
    # 確保 instance 目錄存在
    instance_dir.mkdir(exist_ok=True)
    
    # 測試資料庫路徑
    db_paths = [
        instance_dir / "insurance_news.db",
        instance_dir / "dev_insurance_news.db",
        base_dir / "insurance_news.db"
    ]
    
    for db_path in db_paths:
        print(f"\n🔍 測試資料庫: {db_path}")
        print(f"   存在: {db_path.exists()}")
        
        if db_path.exists():
            print(f"   大小: {db_path.stat().st_size} bytes")
            
            try:
                # 測試連接
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                # 檢查表格
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                print(f"   表格數量: {len(tables)}")
                
                if 'news' in [table[0] for table in tables]:
                    cursor.execute("SELECT COUNT(*) FROM news")
                    count = cursor.fetchone()[0]
                    print(f"   新聞數量: {count}")
                
                conn.close()
                print("   ✅ 連接成功")
                
            except Exception as e:
                print(f"   ❌ 連接失敗: {e}")
    
    return instance_dir / "insurance_news.db"

def create_unified_database():
    """建立統一的資料庫"""
    print("\n🔧 建立統一資料庫...")
    
    base_dir = Path(__file__).parent.absolute()
    instance_dir = base_dir / "instance"
    instance_dir.mkdir(exist_ok=True)
    
    # 新的統一資料庫路徑
    unified_db = instance_dir / "insurance_news.db"
    
    try:
        # 建立新資料庫連接
        conn = sqlite3.connect(str(unified_db))
        cursor = conn.cursor()
        
        # 建立基本表格
        print("📋 建立資料表...")
        
        # 新聞來源表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL UNIQUE,
                url VARCHAR(500) NOT NULL,
                description TEXT,
                status VARCHAR(20) DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 新聞分類表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 新聞表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(500) NOT NULL,
                content TEXT NOT NULL,
                summary TEXT,
                url VARCHAR(1000) UNIQUE NOT NULL,
                source_id INTEGER,
                category_id INTEGER,
                published_date DATETIME NOT NULL,
                crawled_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES news_sources (id),
                FOREIGN KEY (category_id) REFERENCES news_categories (id)
            )
        """)
        
        # 插入預設資料
        print("📊 插入預設資料...")
        
        # 預設新聞來源
        sources = [
            ("Google新聞-保險", "https://news.google.com/rss/search?q=保險&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"),
            ("Google新聞-金融", "https://news.google.com/rss/search?q=金融&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"),
            ("工商時報", "https://www.ctee.com.tw"),
            ("經濟日報", "https://money.udn.com"),
            ("自由時報", "https://ec.ltn.com.tw"),
            ("中時新聞網", "https://www.chinatimes.com")
        ]
        
        for name, url in sources:
            cursor.execute(
                "INSERT OR IGNORE INTO news_sources (name, url) VALUES (?, ?)",
                (name, url)
            )
        
        # 預設分類
        categories = [
            ("人壽保險", "人壽保險相關新聞"),
            ("產物保險", "產物保險相關新聞"),
            ("保險監理", "保險監理相關新聞"),
            ("保險科技", "保險科技創新新聞"),
            ("其他", "其他保險相關新聞")
        ]
        
        for name, desc in categories:
            cursor.execute(
                "INSERT OR IGNORE INTO news_categories (name, description) VALUES (?, ?)",
                (name, desc)
            )
        
        conn.commit()
        conn.close()
        
        print(f"✅ 統一資料庫建立完成: {unified_db}")
        print(f"   大小: {unified_db.stat().st_size} bytes")
        
        return str(unified_db)
        
    except Exception as e:
        print(f"❌ 資料庫建立失敗: {e}")
        return None

def update_config():
    """更新配置文件"""
    print("\n⚙️ 更新配置文件...")
    
    config_path = Path(__file__).parent / "config" / "settings.py"
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 更新資料庫路徑配置
        base_dir_line = 'BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))'
        
        if base_dir_line not in content:
            # 找到資料庫配置區域並更新
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'SQLALCHEMY_DATABASE_URI' in line and 'BASE_DIR' not in line:
                    # 插入 BASE_DIR 定義
                    lines.insert(i, '    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))')
                    lines[i+1] = '    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, \'instance\', \'insurance_news.db\')}")'
                    break
            
            # 寫回文件
            with open(config_path, "w", encoding="utf-8") as f:
                f.write('\n'.join(lines))
            
            print("✅ 配置文件已更新")
        else:
            print("✅ 配置文件已經是最新的")
            
    except Exception as e:
        print(f"❌ 配置更新失敗: {e}")

if __name__ == "__main__":
    print("🔧 台灣保險新聞聚合器 - 資料庫修復工具")
    print("=" * 50)
    
    # 測試資料庫連接
    main_db = test_database_connection()
    
    # 建立統一資料庫
    unified_db = create_unified_database()
    
    # 更新配置
    update_config()
    
    print("\n" + "=" * 50)
    print("✅ 資料庫修復完成！")
    print("\n建議執行:")
    print("1. python quick_check.py - 檢查系統狀態")
    print("2. python run.py - 啟動應用程式")
