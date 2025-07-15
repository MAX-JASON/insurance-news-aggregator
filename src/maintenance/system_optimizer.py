"""
系統優化與監控腳本
System Optimization and Monitoring Script

根據實施計劃進行系統優化、錯誤處理改善和效能監控
"""

import os
import sys
import sqlite3
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from pathlib import Path

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('system_optimizer')

class SystemOptimizer:
    """系統優化器"""
    
    def __init__(self):
        """初始化優化器"""
        self.db_path = "instance/insurance_news.db"
        self.logs_dir = "logs"
        self.optimization_report = {
            'timestamp': datetime.now().isoformat(),
            'optimizations': [],
            'errors': [],
            'performance': {}
        }
        logger.info("🔧 系統優化器初始化完成")
    
    def optimize_database(self):
        """優化資料庫"""
        logger.info("📊 開始資料庫優化...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 檢查並創建索引
            self._create_database_indexes(cursor)
            
            # 清理重複數據
            self._clean_duplicate_data(cursor)
            
            # 優化資料庫
            cursor.execute("VACUUM")
            cursor.execute("ANALYZE")
            
            conn.commit()
            conn.close()
            
            self.optimization_report['optimizations'].append({
                'type': 'database',
                'action': '資料庫優化、索引創建、重複數據清理',
                'status': 'success'
            })
            
            logger.info("✅ 資料庫優化完成")
            
        except Exception as e:
            logger.error(f"❌ 資料庫優化失敗: {e}")
            self.optimization_report['errors'].append({
                'type': 'database',
                'error': str(e)
            })
    
    def _create_database_indexes(self, cursor):
        """創建資料庫索引"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_news_published_date ON news(published_date)",
            "CREATE INDEX IF NOT EXISTS idx_news_status ON news(status)",
            "CREATE INDEX IF NOT EXISTS idx_news_source_id ON news(source_id)",
            "CREATE INDEX IF NOT EXISTS idx_news_category_id ON news(category_id)",
            "CREATE INDEX IF NOT EXISTS idx_news_title ON news(title)",
            "CREATE INDEX IF NOT EXISTS idx_news_created_at ON news(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_news_importance_score ON news(importance_score)",
            "CREATE INDEX IF NOT EXISTS idx_news_sentiment_score ON news(sentiment_score)"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                logger.info(f"✅ 索引創建成功: {index_sql.split('IF NOT EXISTS')[1].split('ON')[0].strip()}")
            except Exception as e:
                logger.warning(f"⚠️ 索引創建失敗: {e}")
    
    def _clean_duplicate_data(self, cursor):
        """清理重複數據"""
        # 查找重複標題的新聞
        cursor.execute("""
            SELECT title, COUNT(*) as count 
            FROM news 
            GROUP BY title 
            HAVING count > 1
        """)
        
        duplicates = cursor.fetchall()
        
        if duplicates:
            logger.info(f"發現 {len(duplicates)} 組重複新聞")
            
            for title, count in duplicates:
                # 保留最新的一條，刪除其他重複的
                cursor.execute("""
                    DELETE FROM news 
                    WHERE title = ? AND id NOT IN (
                        SELECT id FROM news 
                        WHERE title = ? 
                        ORDER BY created_at DESC 
                        LIMIT 1
                    )
                """, (title, title))
                
                deleted_count = cursor.rowcount
                if deleted_count > 0:
                    logger.info(f"刪除重複新聞: {title} (刪除 {deleted_count} 條)")
    
    def check_system_health(self):
        """檢查系統健康狀態"""
        logger.info("🏥 開始系統健康檢查...")
        
        health_report = {
            'database': self._check_database_health(),
            'files': self._check_file_system(),
            'logs': self._check_log_files(),
            'dependencies': self._check_dependencies()
        }
        
        self.optimization_report['performance']['health_check'] = health_report
        
        # 計算總體健康分數
        total_score = 0
        max_score = 0
        
        for category, status in health_report.items():
            if isinstance(status, dict) and 'score' in status:
                total_score += status['score']
                max_score += 100
        
        overall_score = (total_score / max_score * 100) if max_score > 0 else 0
        
        logger.info(f"📊 系統健康分數: {overall_score:.1f}/100")
        
        return health_report
    
    def _check_database_health(self):
        """檢查資料庫健康狀態"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 檢查表格完整性
            cursor.execute("PRAGMA integrity_check")
            integrity = cursor.fetchone()[0]
            
            # 檢查數據量
            cursor.execute("SELECT COUNT(*) FROM news")
            news_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM news_source")
            sources_count = cursor.fetchone()[0]
            
            # 檢查最新數據時間
            cursor.execute("SELECT MAX(created_at) FROM news")
            latest_news = cursor.fetchone()[0]
            
            conn.close()
            
            # 計算分數
            score = 100
            if integrity != 'ok':
                score -= 50
            if news_count < 10:
                score -= 20
            if sources_count < 1:
                score -= 20
            
            if latest_news:
                latest_date = datetime.fromisoformat(latest_news.replace('Z', '+00:00'))
                hours_old = (datetime.now() - latest_date.replace(tzinfo=None)).total_seconds() / 3600
                if hours_old > 24:
                    score -= 10
            
            return {
                'status': 'healthy' if score >= 80 else 'warning' if score >= 60 else 'critical',
                'score': max(0, score),
                'details': {
                    'integrity': integrity,
                    'news_count': news_count,
                    'sources_count': sources_count,
                    'latest_news': latest_news
                }
            }
            
        except Exception as e:
            logger.error(f"資料庫健康檢查失敗: {e}")
            return {
                'status': 'critical',
                'score': 0,
                'error': str(e)
            }
    
    def _check_file_system(self):
        """檢查文件系統"""
        try:
            required_dirs = ['logs', 'instance', 'web/static', 'web/templates']
            required_files = ['run.py', 'config/settings.py', 'database/models.py']
            
            missing_dirs = []
            missing_files = []
            
            for dir_path in required_dirs:
                if not os.path.exists(dir_path):
                    missing_dirs.append(dir_path)
            
            for file_path in required_files:
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
            
            score = 100
            score -= len(missing_dirs) * 10
            score -= len(missing_files) * 15
            
            return {
                'status': 'healthy' if score >= 80 else 'warning' if score >= 60 else 'critical',
                'score': max(0, score),
                'missing_dirs': missing_dirs,
                'missing_files': missing_files
            }
            
        except Exception as e:
            return {
                'status': 'critical',
                'score': 0,
                'error': str(e)
            }
    
    def _check_log_files(self):
        """檢查日誌文件"""
        try:
            if not os.path.exists(self.logs_dir):
                return {
                    'status': 'warning',
                    'score': 50,
                    'message': '日誌目錄不存在'
                }
            
            log_files = list(Path(self.logs_dir).glob('*.log'))
            
            # 檢查日誌文件大小
            large_files = []
            for log_file in log_files:
                size_mb = log_file.stat().st_size / 1024 / 1024
                if size_mb > 100:  # 超過100MB
                    large_files.append(f"{log_file.name}: {size_mb:.1f}MB")
            
            score = 100
            if len(log_files) == 0:
                score -= 30
            score -= len(large_files) * 10
            
            return {
                'status': 'healthy' if score >= 80 else 'warning',
                'score': max(0, score),
                'log_files_count': len(log_files),
                'large_files': large_files
            }
            
        except Exception as e:
            return {
                'status': 'critical',
                'score': 0,
                'error': str(e)
            }
    
    def _check_dependencies(self):
        """檢查依賴項"""
        try:
            required_packages = [
                'flask', 'sqlalchemy', 'requests', 'beautifulsoup4',
                'jieba', 'textblob', 'feedparser', 'schedule'
            ]
            
            missing_packages = []
            
            for package in required_packages:
                try:
                    __import__(package)
                except ImportError:
                    missing_packages.append(package)
            
            score = 100 - len(missing_packages) * 12.5
            
            return {
                'status': 'healthy' if score >= 80 else 'warning' if score >= 60 else 'critical',
                'score': max(0, score),
                'missing_packages': missing_packages,
                'checked_packages': len(required_packages)
            }
            
        except Exception as e:
            return {
                'status': 'critical',
                'score': 0,
                'error': str(e)
            }
    
    def optimize_logs(self):
        """優化日誌文件"""
        logger.info("📝 開始日誌優化...")
        
        try:
            if not os.path.exists(self.logs_dir):
                os.makedirs(self.logs_dir)
                logger.info("✅ 創建日誌目錄")
            
            # 壓縮大型日誌文件
            log_files = list(Path(self.logs_dir).glob('*.log'))
            optimized_count = 0
            
            for log_file in log_files:
                size_mb = log_file.stat().st_size / 1024 / 1024
                
                # 如果日誌文件超過50MB，創建備份並清空
                if size_mb > 50:
                    backup_name = f"{log_file.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                    backup_path = log_file.parent / backup_name
                    
                    # 重命名原文件為備份
                    log_file.rename(backup_path)
                    
                    # 創建新的空日誌文件
                    log_file.touch()
                    
                    logger.info(f"✅ 優化日誌文件: {log_file.name} ({size_mb:.1f}MB)")
                    optimized_count += 1
            
            self.optimization_report['optimizations'].append({
                'type': 'logs',
                'action': f'優化 {optimized_count} 個日誌文件',
                'status': 'success'
            })
            
            logger.info(f"✅ 日誌優化完成，處理 {optimized_count} 個文件")
            
        except Exception as e:
            logger.error(f"❌ 日誌優化失敗: {e}")
            self.optimization_report['errors'].append({
                'type': 'logs',
                'error': str(e)
            })
    
    def performance_benchmark(self):
        """效能基準測試"""
        logger.info("⚡ 開始效能基準測試...")
        
        try:
            # 資料庫查詢效能測試
            db_performance = self._test_database_performance()
            
            # 文件I/O效能測試
            io_performance = self._test_io_performance()
            
            performance_data = {
                'database': db_performance,
                'io': io_performance,
                'timestamp': datetime.now().isoformat()
            }
            
            self.optimization_report['performance']['benchmark'] = performance_data
            
            logger.info("✅ 效能基準測試完成")
            return performance_data
            
        except Exception as e:
            logger.error(f"❌ 效能基準測試失敗: {e}")
            return {'error': str(e)}
    
    def _test_database_performance(self):
        """測試資料庫效能"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 測試簡單查詢
            start_time = time.time()
            cursor.execute("SELECT COUNT(*) FROM news")
            cursor.fetchone()
            simple_query_time = time.time() - start_time
            
            # 測試複雜查詢
            start_time = time.time()
            cursor.execute("""
                SELECT n.title, s.name, COUNT(*) as count
                FROM news n 
                LEFT JOIN news_source s ON n.source_id = s.id 
                WHERE n.status = 'active' 
                GROUP BY s.name 
                ORDER BY count DESC 
                LIMIT 10
            """)
            cursor.fetchall()
            complex_query_time = time.time() - start_time
            
            conn.close()
            
            return {
                'simple_query_ms': round(simple_query_time * 1000, 2),
                'complex_query_ms': round(complex_query_time * 1000, 2),
                'status': 'good' if complex_query_time < 0.1 else 'slow'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _test_io_performance(self):
        """測試I/O效能"""
        try:
            test_file = "temp_performance_test.txt"
            test_data = "測試數據" * 1000
            
            # 寫入測試
            start_time = time.time()
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_data)
            write_time = time.time() - start_time
            
            # 讀取測試
            start_time = time.time()
            with open(test_file, 'r', encoding='utf-8') as f:
                f.read()
            read_time = time.time() - start_time
            
            # 清理測試文件
            os.remove(test_file)
            
            return {
                'write_ms': round(write_time * 1000, 2),
                'read_ms': round(read_time * 1000, 2),
                'status': 'good' if write_time < 0.01 else 'slow'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def generate_optimization_report(self):
        """生成優化報告"""
        report_file = f"optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.optimization_report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📋 優化報告已生成: {report_file}")
            return report_file
            
        except Exception as e:
            logger.error(f"❌ 報告生成失敗: {e}")
            return None
    
    def run_full_optimization(self):
        """執行完整優化"""
        logger.info("🚀 開始系統完整優化...")
        
        start_time = time.time()
        
        # 執行各項優化
        self.optimize_database()
        self.optimize_logs()
        
        # 健康檢查
        health_status = self.check_system_health()
        
        # 效能測試
        performance_data = self.performance_benchmark()
        
        # 記錄總執行時間
        total_time = time.time() - start_time
        self.optimization_report['execution_time_seconds'] = round(total_time, 2)
        
        # 生成報告
        report_file = self.generate_optimization_report()
        
        logger.info(f"🎉 系統優化完成！耗時 {total_time:.2f} 秒")
        
        return {
            'status': 'success',
            'execution_time': total_time,
            'report_file': report_file,
            'health_status': health_status,
            'performance': performance_data
        }

def main():
    """主執行函數"""
    print("🔧 啟動系統優化與監控...")
    
    optimizer = SystemOptimizer()
    result = optimizer.run_full_optimization()
    
    print(f"\n📋 優化結果:")
    print(f"  狀態: {result['status']}")
    print(f"  執行時間: {result['execution_time']:.2f} 秒")
    print(f"  報告文件: {result['report_file']}")
    
    # 顯示健康狀態摘要
    health = result['health_status']
    print(f"\n🏥 系統健康狀態:")
    for component, status in health.items():
        if isinstance(status, dict):
            score = status.get('score', 0)
            state = status.get('status', 'unknown')
            print(f"  {component}: {state} ({score}/100)")

if __name__ == "__main__":
    main()
