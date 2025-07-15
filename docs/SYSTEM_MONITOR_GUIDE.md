# 系統監控與用戶反饋功能使用指南

## 系統監控功能

### 功能概述

系統監控功能提供了對保險新聞聚合系統的實時監控，包括錯誤檢測、自動修復和健康狀態檢查。此功能通過 `system_monitor.py` 腳本實現，整合了錯誤監控和用戶反饋收集功能。

### 啟動方法

1. **使用批處理文件啟動**：
   - 雙擊運行 `start_monitor.bat` 文件
   - 系統將在後台啟動監控服務
   - 日誌將保存在 `logs\system_monitor.log` 文件中

2. **使用命令行啟動**：

   ```bash
   python system_monitor.py --action start
   ```

3. **停止服務**：

   ```bash
   python system_monitor.py --action stop
   ```

4. **重啟服務**：

   ```bash
   python system_monitor.py --action restart
   ```

### 監控功能

1. **錯誤監控**：
   - 系統自動掃描錯誤日誌，每2分鐘進行一次
   - 識別常見錯誤類型並分類
   - 生成錯誤統計和報告，保存在 `logs\reports` 目錄中

2. **自動修復**：
   - 部分錯誤類型支持自動修復
   - 修復策略定義在 `config\repair_strategies.json` 文件中
   - 修復操作記錄在 `logs\error_monitor.log` 文件中

3. **系統健康檢查**：
   - 每小時執行一次健康檢查
   - 檢查項目包括：數據庫連接、爬蟲狀態、API服務、前端Web服務和磁碟空間
   - 異常情況會觸發自動修復操作

### 配置文件

1. **已知錯誤類型**：
   - 文件位置：`config\known_errors.json`
   - 包含錯誤模式識別、嚴重程度和建議操作

2. **修復策略**：
   - 文件位置：`config\repair_strategies.json`
   - 定義不同錯誤類型的修復策略和操作

## 用戶反饋功能

### 反饋系統概述

用戶反饋功能允許系統收集、分析和可視化用戶對系統的反饋。此功能通過 `src/services/user_feedback.py` 模塊實現，提供了Web界面和API接口。

### 反饋系統使用方法

1. **訪問反饋表單**：
   - 訪問 URL：`http://localhost:5000/feedback/form`
   - 用戶可以選擇反饋類別、評分、功能和提交詳細反饋信息

2. **查看反饋儀表板**（管理員）：
   - 訪問 URL：`http://localhost:5000/feedback/dashboard`
   - 需要管理員權限才能查看
   - 包括反饋統計、圖表和最新反饋列表

### API接口

1. **提交反饋**：

   ```http
   POST /feedback/submit
   Content-Type: application/json
   
   {
     "category": "ui",
     "rating": 4,
     "message": "界面設計很直觀，但加載速度可以再優化",
     "features": ["news_list", "search"],
     "source": "web"
   }
   ```

2. **獲取統計信息**（管理員）：

   ```http
   GET /feedback/stats
   ```

3. **導出反饋數據**（管理員）：

   ```http
   GET /feedback/export?format=json
   ```

4. **生成反饋圖表**（管理員）：

   ```http
   GET /feedback/charts
   ```

### 圖表與報告

1. **自動生成的圖表**：
   - 評分分佈圖
   - 類別評分對比圖
   - 反饋時間趨勢圖
   - 反饋關鍵詞雲

2. **圖表位置**：
   - `/static/charts/feedback/` 目錄

## 效能壓力測試

### 壓力測試概述

效能壓力測試功能用於模擬高負載情境，測試系統的穩定性和效能。此功能通過 `tests/load_test.py` 腳本實現。

### 壓力測試使用方法

1. **運行基本壓力測試**：

   ```bash
   python tests/load_test.py
   ```

2. **自定義測試參數**：

   ```bash
   python tests/load_test.py --url http://localhost:5000 --users 20 --requests 50
   ```

   參數說明：
   - `--url`：測試目標URL，默認為 `http://localhost:5000`
   - `--users`：模擬用戶數，默認為10
   - `--requests`：每個用戶的請求數，默認為20
   - `--output`：輸出目錄，默認為 tests/results

### 測試報告

1. **報告位置**：
   - JSON報告：`tests/results/load_test_report_*.json`
   - 圖表：`tests/results/charts/`

2. **圖表類型**：
   - 響應時間對比圖
   - 請求成功率圖
   - 每秒請求數圖

## 問題排查

### 常見問題

1. **監控服務無法啟動**：
   - 檢查Python環境是否正確安裝
   - 檢查必要的目錄是否存在（logs, cache等）
   - 查看錯誤日誌 `logs\system_monitor.log`

2. **自動修復失敗**：
   - 檢查 `logs\error_monitor.log` 中的錯誤信息
   - 確認修復策略配置是否正確

3. **反饋功能無法訪問**：
   - 確認主應用已啟動並正常運行
   - 檢查 `logs\feedback.log` 中的錯誤信息

### 手動啟動服務

如果自動服務出現問題，可以手動運行以下命令進行單獨測試：

1. **錯誤監控**：

   ```bash
   python -m src.maintenance.error_monitor
   ```

2. **用戶反饋收集**：
   在主應用中訪問 `/feedback/form` 和 `/feedback/dashboard`

3. **效能壓力測試**：

   ```bash
   python tests/load_test.py
   ```

## 最佳實踐

1. **定期檢查監控報告**：
   - 每天檢查錯誤報告，及時發現系統問題
   - 定期分析用戶反饋，改進系統功能

2. **調整配置參數**：
   - 根據系統負載調整監控間隔
   - 更新已知錯誤類型和修復策略

3. **定期備份**：
   - 系統自動進行數據庫備份，但建議定期手動備份重要數據
