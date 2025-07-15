# 🕷️ 爬蟲腳本集合

這個資料夾包含了所有的新聞爬蟲腳本，每個都有特定的功能和用途。

## 📁 檔案說明

### 🌟 推薦使用
- **`daily_crawler_60.py`** - 📰 每日60篇精選新聞爬蟲
  - 🎯 專為每日閱讀設計
  - 📊 智能關鍵字分配
  - 🔄 自動去重機制
  - ⚡ 快速執行（約30-40秒）

### 🔧 進階爬蟲
- **`enhanced_crawler.py`** - 🔧 增強版爬蟲
  - 改良的重複檢測算法
  - 支援多搜索詞
  
- **`smart_insurance_crawler.py`** - 🧠 智能保險爬蟲
  - 智能去重和URL清理
  - 87個擴展關鍵字
  
- **`super_insurance_crawler.py`** - 🚀 超級保險爬蟲
  - 21個搜索關鍵字
  - 並行處理提升效率

- **`ultimate_insurance_aggregator.py`** - 🌟 終極新聞聚合器
  - 50個關鍵字，300則新聞
  - 並行抓取，最大覆蓋

### 🔄 基礎爬蟲
- **`standalone_crawler.py`** - 🔄 獨立爬蟲
  - 基礎功能爬蟲
  - 適合測試和學習

- **`trigger_crawler.py`** - ⚡ 觸發式爬蟲
  - 事件觸發型爬蟲

## 🚀 使用方法

### 日常推薦
```bash
# 每日新聞更新（推薦）
python daily_crawler_60.py
```

### 大量抓取
```bash
# 智能爬蟲（平衡效果）
python smart_insurance_crawler.py

# 終極聚合器（最大覆蓋）
python ultimate_insurance_aggregator.py
```

### 測試用途
```bash
# 基礎爬蟲（測試）
python standalone_crawler.py
```

## 📊 效能比較

| 爬蟲 | 關鍵字數 | 預期新聞數 | 執行時間 | 適用場景 |
|------|----------|------------|----------|----------|
| daily_crawler_60 | 26 | 60篇 | ~35秒 | 每日閱讀 |
| smart_insurance_crawler | 87 | 200+篇 | ~60秒 | 深度更新 |
| ultimate_insurance_aggregator | 50 | 300篇 | ~90秒 | 全面覆蓋 |
| enhanced_crawler | 4 | 14篇 | ~15秒 | 快速測試 |

## 💡 選擇建議

- **每日使用**: `daily_crawler_60.py`
- **週末深度更新**: `smart_insurance_crawler.py`
- **初次建置**: `ultimate_insurance_aggregator.py`
- **測試除錯**: `standalone_crawler.py`
