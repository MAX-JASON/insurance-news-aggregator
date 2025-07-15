# 🛠️ 系統管理工具

這個資料夾包含所有的系統管理和維護工具。

## 📁 檔案說明

### 🤖 自動化服務
- **`auto_cleanup_service.py`** - 🤖 自動清理服務
  - 📅 排程清理（每日02:00）
  - 📊 新聞數量限制（最多500篇）
  - 🔄 6小時檢查一次
  - 📈 狀態監控和報告

### 🧹 手動清理工具
- **`cleanup_old_news.py`** - 🧹 手動清理舊新聞
  - 🗓️ 按天數清理（預設7天）
  - 📊 按數量清理（保留指定數量）
  - 🔍 乾執行模式（--dry-run）
  - ⚡ 執行模式（--execute）

### ⚙️ 系統配置
- **`configure_date_filter.py`** - 📅 日期過濾器配置
  - 🔧 配置7天過濾規則
  - 📝 API端點設定
  - 🎛️ 過濾器開關控制

## 🚀 使用方法

### 檢查系統狀態
```bash
python auto_cleanup_service.py --status
```

### 手動清理新聞
```bash
# 查看會刪除什麼（不實際刪除）
python cleanup_old_news.py --dry-run

# 執行清理（實際刪除）
python cleanup_old_news.py --execute

# 清理超過3天的新聞
python cleanup_old_news.py --execute --days 3

# 只保留最新100篇新聞
python cleanup_old_news.py --execute --max-count 100
```

### 啟動自動清理服務
```bash
# 前台執行（會顯示日誌）
python auto_cleanup_service.py

# 背景執行
python auto_cleanup_service.py --run-once
```

### 配置日期過濾器
```bash
python configure_date_filter.py
```

## 📊 清理規則

### 自動清理服務規則
- **時間規則**: 超過7天的新聞自動刪除
- **數量規則**: 超過500篇時保留最新500篇
- **檢查頻率**: 每6小時檢查一次
- **清理時間**: 每日凌晨02:00執行

### 手動清理選項
- **按時間**: `--days N` 刪除N天前的新聞
- **按數量**: `--max-count N` 只保留最新N篇
- **安全模式**: `--dry-run` 只顯示不執行
- **執行模式**: `--execute` 實際執行刪除

## ⚠️ 注意事項

1. **備份重要**: 清理前建議備份資料庫
2. **測試先行**: 使用 `--dry-run` 確認清理範圍
3. **逐步清理**: 大量清理時分批執行
4. **監控狀態**: 定期檢查 `--status` 輸出

## 📈 最佳實踐

### 日常維護
```bash
# 每天檢查狀態
python auto_cleanup_service.py --status

# 每週手動清理一次
python cleanup_old_news.py --dry-run
python cleanup_old_news.py --execute
```

### 系統重置
```bash
# 大量清理（只保留最新50篇）
python cleanup_old_news.py --execute --max-count 50

# 重新配置過濾器
python configure_date_filter.py
```
