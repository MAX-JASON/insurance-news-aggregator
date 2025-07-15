"""
資料庫查詢優化腳本
Database Query Optimization Script

提供優化SQL查詢和索引的工具，提升應用程式效能
"""

from flask import current_app
from sqlalchemy import text, inspect
import time
import logging
from sqlalchemy.exc import OperationalError
from app import create_app, db
from config.settings import Config

# 設置日誌
logger = logging.getLogger('maintenance.db_optimization')

def analyze_table(table_name):
    """分析資料表，收集統計資訊以優化查詢計劃"""
    try:
        sql = f"ANALYZE {table_name};"
        db.session.execute(text(sql))
        db.session.commit()
        logger.info(f"已分析資料表 {table_name}")
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"分析資料表 {table_name} 失敗: {e}")
        return False

def check_index_exists(table_name, index_name):
    """檢查索引是否存在"""
    inspector = inspect(db.engine)
    indexes = inspector.get_indexes(table_name)
    for index in indexes:
        if index['name'] == index_name:
            return True
    return False

def create_index(table_name, index_name, columns, unique=False):
    """創建索引"""
    try:
        # 檢查索引是否已存在
        if check_index_exists(table_name, index_name):
            logger.info(f"索引 {index_name} 已存在於 {table_name}")
            return True

        # 創建索引
        unique_str = "UNIQUE" if unique else ""
        columns_str = ", ".join(columns)
        sql = f"CREATE {unique_str} INDEX {index_name} ON {table_name} ({columns_str});"
        db.session.execute(text(sql))
        db.session.commit()
        logger.info(f"已創建索引 {index_name} 於 {table_name} ({columns_str})")
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"創建索引 {index_name} 失敗: {e}")
        return False

def create_full_text_index(table_name, index_name, column):
    """創建全文索引"""
    try:
        # 檢查索引是否已存在
        if check_index_exists(table_name, index_name):
            logger.info(f"全文索引 {index_name} 已存在於 {table_name}")
            return True

        # 對於 SQLite
        if db.engine.dialect.name == 'sqlite':
            # SQLite 使用 FTS5 虛擬表
            db.session.execute(text(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS {table_name}_fts USING fts5({column}, content='{table_name}');
            """))
            
            # 填充現有數據
            db.session.execute(text(f"""
                INSERT INTO {table_name}_fts({column}) SELECT {column} FROM {table_name};
            """))
            
            # 創建觸發器以保持同步
            db.session.execute(text(f"""
                CREATE TRIGGER IF NOT EXISTS {table_name}_ai AFTER INSERT ON {table_name} BEGIN
                    INSERT INTO {table_name}_fts({column}) VALUES (new.{column});
                END;
            """))
            
            db.session.execute(text(f"""
                CREATE TRIGGER IF NOT EXISTS {table_name}_ad AFTER DELETE ON {table_name} BEGIN
                    INSERT INTO {table_name}_fts({table_name}_fts, {column}) VALUES('delete', old.{column});
                END;
            """))
            
            db.session.execute(text(f"""
                CREATE TRIGGER IF NOT EXISTS {table_name}_au AFTER UPDATE ON {table_name} BEGIN
                    INSERT INTO {table_name}_fts({table_name}_fts, {column}) VALUES('delete', old.{column});
                    INSERT INTO {table_name}_fts({column}) VALUES (new.{column});
                END;
            """))
            
        # 對於 PostgreSQL
        elif db.engine.dialect.name == 'postgresql':
            # 添加tsvector列
            db.session.execute(text(f"""
                ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column}_tsv tsvector;
            """))
            
            # 創建GIN索引
            db.session.execute(text(f"""
                CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} USING gin({column}_tsv);
            """))
            
            # 更新tsvector列
            db.session.execute(text(f"""
                UPDATE {table_name} SET {column}_tsv = to_tsvector('chinese', {column});
            """))
            
            # 創建觸發器以保持同步
            db.session.execute(text(f"""
                CREATE OR REPLACE FUNCTION {table_name}_tsvector_update_trigger() RETURNS trigger AS $$
                BEGIN
                    NEW.{column}_tsv := to_tsvector('chinese', NEW.{column});
                    RETURN NEW;
                END
                $$ LANGUAGE plpgsql;
            """))
            
            db.session.execute(text(f"""
                DROP TRIGGER IF EXISTS {table_name}_tsvector_update ON {table_name};
            """))
            
            db.session.execute(text(f"""
                CREATE TRIGGER {table_name}_tsvector_update
                BEFORE INSERT OR UPDATE ON {table_name}
                FOR EACH ROW EXECUTE PROCEDURE {table_name}_tsvector_update_trigger();
            """))
        
        db.session.commit()
        logger.info(f"已創建全文索引 {index_name} 於 {table_name}.{column}")
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"創建全文索引 {index_name} 失敗: {e}")
        return False

def optimize_queries():
    """優化常用查詢"""
    with open('src/maintenance/optimize_queries.sql', 'r', encoding='utf-8') as f:
        queries = f.read().split(';')
    
    success_count = 0
    for query in queries:
        query = query.strip()
        if not query:
            continue
        
        try:
            db.session.execute(text(query))
            db.session.commit()
            success_count += 1
        except Exception as e:
            db.session.rollback()
            logger.error(f"執行查詢優化失敗: {e}\n查詢: {query}")
    
    logger.info(f"成功執行 {success_count}/{len(queries)} 個查詢優化")
    return success_count

def test_query_performance():
    """測試常用查詢的效能"""
    test_queries = {
        'latest_news': "SELECT * FROM news ORDER BY published_date DESC LIMIT 10",
        'news_by_category': "SELECT * FROM news WHERE category_id = 1 ORDER BY published_date DESC LIMIT 10",
        'news_by_source': "SELECT * FROM news WHERE source_id = 1 ORDER BY published_date DESC LIMIT 10",
        'news_search': "SELECT * FROM news WHERE title LIKE '%保險%' OR content LIKE '%保險%' LIMIT 10",
        'news_with_source': """
            SELECT n.id, n.title, n.published_date, s.name as source_name 
            FROM news n 
            JOIN news_sources s ON n.source_id = s.id 
            ORDER BY n.published_date DESC 
            LIMIT 10
        """
    }
    
    results = {}
    for name, query in test_queries.items():
        start_time = time.time()
        try:
            db.session.execute(text(query))
            duration = time.time() - start_time
            results[name] = {
                'status': 'success',
                'duration': duration,
                'query': query
            }
            logger.info(f"查詢 {name} 耗時: {duration:.4f}秒")
        except Exception as e:
            results[name] = {
                'status': 'error',
                'error': str(e),
                'query': query
            }
            logger.error(f"查詢 {name} 失敗: {e}")
    
    return results

def optimize_database():
    """執行所有資料庫優化任務"""
    logger.info("開始資料庫優化...")
    
    # 1. 創建必要的索引
    indexes = [
        # News表索引
        ('news', 'idx_news_title', ['title']),
        ('news', 'idx_news_created', ['created_at']),
        ('news', 'idx_news_source_date', ['source_id', 'published_date']),
        ('news', 'idx_news_category_date', ['category_id', 'published_date']),
        ('news', 'idx_news_importance_date', ['importance_score', 'published_date']),
        ('news', 'idx_news_sentiment_date', ['sentiment_score', 'published_date']),
        
        # CrawlLog表索引
        ('crawl_logs', 'idx_crawl_logs_date', ['start_time']),
        ('crawl_logs', 'idx_crawl_logs_source_date', ['source_id', 'start_time']),
        
        # AnalysisLog表索引
        ('analysis_logs', 'idx_analysis_logs_news', ['news_id']),
        ('analysis_logs', 'idx_analysis_logs_type_date', ['analysis_type', 'start_time']),
        
        # ErrorLog表索引
        ('error_logs', 'idx_error_logs_date', ['timestamp']),
        ('error_logs', 'idx_error_logs_level_date', ['level', 'timestamp']),
        ('error_logs', 'idx_error_logs_module', ['module']),
        
        # SavedNews表索引
        ('saved_news', 'idx_saved_news_user', ['user_id']),
        ('saved_news', 'idx_saved_news_news', ['news_id']),
        ('saved_news', 'idx_saved_news_folder', ['user_id', 'folder']),
    ]
    
    index_results = []
    for table_name, index_name, columns in indexes:
        result = create_index(table_name, index_name, columns)
        index_results.append({
            'table': table_name,
            'index': index_name,
            'columns': columns,
            'success': result
        })
    
    # 2. 創建全文索引
    fulltext_indexes = [
        ('news', 'idx_news_fulltext_title', 'title'),
        ('news', 'idx_news_fulltext_content', 'content'),
    ]
    
    fulltext_results = []
    for table_name, index_name, column in fulltext_indexes:
        result = create_full_text_index(table_name, index_name, column)
        fulltext_results.append({
            'table': table_name,
            'index': index_name,
            'column': column,
            'success': result
        })
    
    # 3. 分析資料表
    tables = ['news', 'news_sources', 'news_categories', 'crawl_logs', 'analysis_logs', 'error_logs', 'users', 'saved_news']
    analyze_results = []
    for table in tables:
        result = analyze_table(table)
        analyze_results.append({
            'table': table,
            'success': result
        })
    
    # 4. 優化常用查詢
    query_optimization_count = optimize_queries()
    
    # 5. 測試查詢效能
    performance_results = test_query_performance()
    
    return {
        'indexes': index_results,
        'fulltext_indexes': fulltext_results,
        'table_analyze': analyze_results,
        'query_optimization_count': query_optimization_count,
        'query_performance': performance_results
    }

def main():
    """主函數"""
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/db_optimization.log'),
            logging.StreamHandler()
        ]
    )
    
    logger.info("啟動資料庫優化腳本")
    
    # 創建應用上下文
    app = create_app(Config)
    
    with app.app_context():
        # 執行優化
        start_time = time.time()
        results = optimize_database()
        duration = time.time() - start_time
        
        # 記錄優化結果
        logger.info(f"資料庫優化完成，耗時: {duration:.2f}秒")
        logger.info(f"創建索引結果: 成功 {sum(1 for r in results['indexes'] if r['success'])} / {len(results['indexes'])}")
        logger.info(f"創建全文索引結果: 成功 {sum(1 for r in results['fulltext_indexes'] if r['success'])} / {len(results['fulltext_indexes'])}")
        logger.info(f"分析資料表結果: 成功 {sum(1 for r in results['table_analyze'] if r['success'])} / {len(results['table_analyze'])}")
        logger.info(f"查詢優化結果: 成功執行 {results['query_optimization_count']} 個優化查詢")
        
        # 回傳結果
        return results

if __name__ == "__main__":
    main()
