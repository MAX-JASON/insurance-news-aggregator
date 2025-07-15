# 台灣保險新聞聚合器 - 專案結構說明

## 📁 專案組織架構

```
D:\insurance-news-aggregator\
├── 📂 crawler/              # 核心爬蟲引擎 (原有)
├── 📂 crawlers/             # 自定義爬蟲腳本 ⭐
├── 📂 management/           # 系統管理工具 ⭐
├── 📂 startup/              # 啟動腳本 ⭐
├── 📂 tools/                # 開發工具 ⭐
├── 📂 web/                  # 前端網頁
├── 📂 api/                  # API介面
├── 📂 app/                  # Flask應用
├── 📂 database/             # 資料庫模型
├── 📂 config/               # 配置檔案
├── 📂 docs/                 # 文檔
├── 📂 tests/                # 測試檔案
├── 📂 logs/                 # 日誌檔案
├── 📂 instance/             # 資料庫實例
└── 📂 cache/                # 快取檔案
```

## 🎯 新增資料夾說明

### 📂 crawlers/ - 爬蟲腳本集合
專門存放各種爬蟲腳本，依照功能分類：

- `daily_crawler_60.py` - 📰 每日60篇精選新聞爬蟲
- `enhanced_crawler.py` - 🔧 增強版爬蟲（改良去重）
- `smart_insurance_crawler.py` - 🧠 智能保險爬蟲
- `super_insurance_crawler.py` - 🚀 超級保險爬蟲
- `ultimate_insurance_aggregator.py` - 🌟 終極新聞聚合器
- `standalone_crawler.py` - 🔄 獨立爬蟲
- `trigger_crawler.py` - ⚡ 觸發式爬蟲

### 📂 management/ - 系統管理
存放系統管理和維護相關工具：

- `auto_cleanup_service.py` - 🤖 自動清理服務（排程清理）
- `cleanup_old_news.py` - 🧹 手動清理舊新聞工具
- `configure_date_filter.py` - 📅 日期過濾器配置工具

### 📂 startup/ - 啟動管理
統一的系統啟動腳本：

- `start_7day_system.py` - 🎮 主要啟動腳本（7天過濾版）

### 📂 tools/ - 開發工具
開發和測試輔助工具：

- `check_database.py` - 🔍 資料庫檢查工具
- `add_test_news.py` - 📝 測試新聞添加工具
- `test_date_filter.py` - 🧪 日期過濾器測試

## 🚀 快速啟動指南

### 方法一：使用啟動腳本（推薦）
```bash
cd D:\insurance-news-aggregator\startup
python start_7day_system.py
```

### 方法二：直接執行爬蟲
```bash
# 每日60篇新聞（推薦）
cd D:\insurance-news-aggregator\crawlers
python daily_crawler_60.py

# 智能爬蟲
python smart_insurance_crawler.py
```

### 方法三：管理系統
```bash
# 手動清理
cd D:\insurance-news-aggregator\management
python cleanup_old_news.py --execute

# 啟動自動清理服務
python auto_cleanup_service.py
```

## 🎯 常用操作

### 📰 每日新聞更新
```bash
cd startup
python start_7day_system.py
# 選擇選項 6：每日爬蟲 (60篇精選新聞)
```

### 🧹 清理舊新聞
```bash
cd startup  
python start_7day_system.py
# 選擇選項 2：只清理舊新聞
```

### 🌐 啟動網站
```bash
cd startup
python start_7day_system.py
# 選擇選項 3：只啟動網站
```

### 📊 檢查系統狀態
```bash
cd startup
python start_7day_system.py
# 選擇選項 4：檢查系統狀態
```

## 🔧 開發者指南

### 新增爬蟲
1. 在 `crawlers/` 目錄創建新的爬蟲檔案
2. 參考 `daily_crawler_60.py` 的結構
3. 更新 `startup/start_7day_system.py` 添加新選項

### 新增管理工具
1. 在 `management/` 目錄創建管理工具
2. 參考 `auto_cleanup_service.py` 的結構
3. 添加到啟動腳本的選項中

### 新增開發工具
1. 在 `tools/` 目錄創建開發輔助工具
2. 主要用於測試和除錯

## 📈 系統功能特色

### ✅ 智能新聞管理
- 📅 7天自動過濾
- 🔄 智能去重機制
- 📰 每日60篇精選新聞
- 🤖 自動排程清理

### ✅ 多元爬蟲策略
- 🎯 精確關鍵字搜索
- 🏢 保險公司專門追蹤
- 🏛️ 政策法規即時更新
- 🔬 保險科技趨勢關注

### ✅ 完整管理界面
- 🎮 一鍵啟動系統
- 📊 即時狀態監控
- 🧹 靈活清理選項
- 🌐 網站快速啟動

## 🎉 最佳實踐建議

### 每日使用流程
1. 執行每日爬蟲獲取新聞
2. 啟動網站瀏覽內容
3. 定期檢查系統狀態
4. 視需要清理舊新聞

### 維護建議
- 📅 每天執行一次每日爬蟲
- 🧹 每週檢查一次新聞數量
- 📊 每月查看一次系統狀態
- 🔧 根據需要調整關鍵字配置

## 📞 技術支援

如需協助或發現問題，請：
1. 查看 `logs/` 目錄下的日誌檔案
2. 使用 `tools/check_database.py` 檢查資料庫
3. 參考 `docs/` 目錄下的文檔
4. 檢查 `config/` 目錄下的配置檔案

---

**專案整理完成日期**: 2025年7月9日  
**整理者**: AI Assistant  
**版本**: v2.2 - 結構化版本
