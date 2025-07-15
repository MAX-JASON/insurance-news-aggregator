# Scripts 資料夾

這個資料夾包含所有的腳本文件，按功能分類組織。

## 子資料夾結構

### `/tests`
包含所有測試相關的Python腳本：
- `test_analysis.py` - 分析功能測試
- `test_complete.py` - 完整系統測試
- `test_crawler_run.py` - 爬蟲運行測試
- `test_db_*.py` - 資料庫相關測試
- `test_fix.py` - 修復功能測試
- `test_news_*.py` - 新聞相關功能測試
- `test_real_news_integration*.py` - 實際新聞整合測試
- `test_ui_frontend.py` - 前端UI測試

### `/maintenance`
包含系統維護、監控和爬蟲相關的腳本：
- `system_*.py` - 系統監控、優化和進度報告
- `*crawler*.py` - 各種爬蟲實現
- `database_repair.py` - 資料庫修復工具
- `data_cleaner.py` - 數據清理工具
- `emergency_fix.py` - 緊急修復腳本
- `scheduler.py` - 任務調度器
- `rss_news_aggregator.py` - RSS新聞聚合器

### `/deployment`
包含部署和初始化相關的腳本：
- `frontend_*.py` - 前端部署和優化
- `init_*.py` - 系統初始化腳本
- `create_*.py` - 資料庫表創建和測試用戶創建

## 使用說明

1. **測試腳本**: 在開發和維護過程中運行相應的測試
2. **維護腳本**: 定期運行系統監控和維護腳本
3. **部署腳本**: 在系統部署和更新時使用
