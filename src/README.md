# 台灣保險新聞聚合器 - 源碼結構說明

## 模組化結構

本專案源碼已重構為模組化結構，便於維護和開發。

### 目錄結構說明

```markdown
src/
├── core/             # 核心應用模組
│   ├── __init__.py   
│   ├── run.py        # 主應用入口副本
│   ├── app_professional_final.py  # 專業版應用
│   ├── scheduler.py              # 排程器
│   └── auto_news_scheduler.py     # 自動新聞排程器
│
├── crawlers/         # 爬蟲模組
│   ├── __init__.py
│   ├── integrated_crawler.py      # 整合爬蟲
│   ├── multi_source_crawler.py    # 多來源爬蟲 
│   ├── rss_news_aggregator.py     # RSS新聞聚合器
│   └── taiwan_insurance_crawler.py # 台灣保險專用爬蟲
│
├── tests/            # 測試模組
│   ├── __init__.py
│   ├── test_analysis.py           # 分析系統測試
│   ├── test_complete.py           # 完整系統測試
│   ├── test_db_direct.py          # 資料庫直接測試
│   ├── test_db_simple.py          # 資料庫簡單測試
│   ├── test_news_detail.py        # 新聞詳情頁測試
│   ├── test_news_list.py          # 新聞列表測試
│   ├── test_real_news_integration.py     # 真實新聞整合測試
│   └── test_real_news_integration_v2.py  # 真實新聞整合測試v2
│
├── utils/            # 工具模組
│   ├── __init__.py
│   ├── data_cleaner.py           # 資料清理工具
│   ├── direct_db_save.py         # 直接資料庫存儲
│   ├── check_status.py           # 狀態檢查工具
│   ├── database_repair.py        # 資料庫修復工具
│   ├── emergency_fix.py          # 緊急修復工具
│   ├── init_db.py                # 資料庫初始化
│   └── quick_check.py            # 快速檢查工具
│
├── maintenance/      # 維護模組
│   ├── __init__.py
│   ├── system_optimizer.py        # 系統優化工具
│   └── system_progress_report.py  # 系統進度報告
│
├── frontend/         # 前端模組
│   ├── __init__.py
│   ├── frontend_deployment.py     # 前端部署工具
│   └── frontend_optimizer.py      # 前端優化工具
│
└── __init__.py       # 套件初始化
```

## 使用說明

1. 主應用仍透過根目錄的 `run.py` 啟動
2. 各模組可直接引用：`from src.crawlers import taiwan_insurance_crawler`
3. 新功能開發請在對應模組中實現

## 開發建議

- 維持模組間的低耦合度
- 使用相對引用避免循環依賴
- 為每個新模組創建測試

## 重構說明

這次重構目的是提高程式碼的可維護性和可讀性，並且降低複雜度。我們將相似功能的文件放在同一個模組中，使新加入的開發者能更快了解專案結構。
