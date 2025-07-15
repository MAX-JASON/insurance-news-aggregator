# 🔧 開發工具集

這個資料夾包含開發和測試輔助工具。

## 📁 檔案說明

### 🔍 資料庫工具
- **`check_database.py`** - 🔍 資料庫檢查工具
  - 📊 檢查資料庫結構
  - 📈 統計新聞數量
  - 🔍 驗證資料完整性

### 📝 測試工具
- **`add_test_news.py`** - 📝 測試新聞添加工具
  - 🧪 添加測試數據
  - 📰 模擬新聞內容
  - 🔬 開發環境測試

- **`test_date_filter.py`** - 🧪 日期過濾器測試
  - 📅 測試日期過濾功能
  - ✅ 驗證過濾邏輯
  - 🔧 除錯過濾器問題

## 🚀 使用方法

### 檢查資料庫
```bash
python check_database.py
```

### 添加測試數據
```bash
python add_test_news.py
```

### 測試日期過濾
```bash
python test_date_filter.py
```

## 🧪 開發流程

### 新功能開發
1. 使用 `check_database.py` 檢查初始狀態
2. 使用 `add_test_news.py` 添加測試數據
3. 開發新功能
4. 使用相關測試工具驗證功能
5. 清理測試數據

### 問題除錯
1. 使用 `check_database.py` 檢查資料庫狀態
2. 使用 `test_date_filter.py` 測試過濾功能
3. 分析日誌檔案
4. 重現問題並修復

## 🔧 工具特色

### check_database.py
- ✅ 檢查資料庫連接
- 📊 統計各類新聞數量
- 📅 顯示最新和最舊新聞
- 🔍 檢查資料完整性

### add_test_news.py
- 📝 快速添加測試新聞
- 🎲 隨機生成內容
- 📅 指定日期範圍
- 🏷️ 自定義標籤

### test_date_filter.py
- 📅 測試7天過濾邏輯
- ✅ 驗證過濾結果
- 🔧 除錯過濾問題
- 📊 顯示過濾統計

## 💡 最佳實踐

### 開發前準備
```bash
# 檢查資料庫狀態
python check_database.py

# 備份現有數據
cp ../instance/insurance_news.db ../instance/backup_$(date +%Y%m%d).db
```

### 功能測試
```bash
# 添加測試數據
python add_test_news.py

# 測試功能
python test_date_filter.py

# 檢查結果
python check_database.py
```

### 清理測試環境
```bash
# 恢復備份
cp ../instance/backup_YYYYMMDD.db ../instance/insurance_news.db

# 或手動清理測試數據
cd ../management
python cleanup_old_news.py --execute --max-count 100
```

## ⚠️ 注意事項

1. **備份重要**: 測試前務必備份資料庫
2. **隔離環境**: 建議使用獨立測試資料庫
3. **清理測試**: 測試完成後清理測試數據
4. **版本控制**: 不要提交測試數據到版本庫

## 🎯 適用場景

- **功能開發**: 需要測試數據時
- **問題除錯**: 重現和修復問題
- **系統驗證**: 確認系統運行正常
- **效能測試**: 測試大量數據處理
