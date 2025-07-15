# 保險新聞聚合器 (Insurance News Aggregator)

這是一個專為保險業設計的新聞聚合和分析系統，能夠自動收集、分析和展示保險相關新聞。

## 功能特色

- 🔍 **智能新聞抓取**: 自動從多個新聞源收集保險相關新聞
- 📊 **重要性評級**: 根據內容自動評估新聞重要性
- 🎯 **關鍵字分析**: 智能識別和分析新聞關鍵字
- 📈 **趨勢分析**: 追蹤保險業趨勢和發展
- 🌐 **Web 介面**: 直觀的網頁操作介面
- 📱 **響應式設計**: 支援桌面和行動裝置使用

## 快速開始

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 配置設定

1. 複製配置範例檔案：
```bash
cp config/config.example.yaml config/config.yaml
```

2. 根據需要修改配置檔案

### 啟動應用

#### 方式一：使用批次檔案（推薦）
```bash
.\啟動系統-簡化版.bat
```

#### 方式二：使用 Python 指令
```bash
python start_app.py
```

#### 方式三：使用 VS Code Tasks
- 按 `Ctrl+Shift+P` 開啟命令面板
- 選擇 "Tasks: Run Task"
- 選擇 "Start Full App"

## 專案結構

```
├── analyzer/          # 新聞分析引擎
├── api/              # API 接口
├── app/              # Flask 應用
├── config/           # 配置檔案
├── crawler/          # 新聞爬蟲
├── database/         # 資料庫模型
├── web/              # 前端資源
└── docs/             # 文件
```

## 使用說明

1. **啟動系統**: 執行啟動腳本後，系統會自動開始收集新聞
2. **查看結果**: 開啟瀏覽器訪問 `http://localhost:5000`
3. **分析報告**: 在 Web 介面中查看新聞分析和趨勢報告

## 技術架構

- **後端**: Python Flask
- **資料庫**: SQLAlchemy + SQLite/PostgreSQL
- **前端**: HTML/CSS/JavaScript
- **新聞源**: RSS 訂閱源、網頁爬蟲
- **分析引擎**: 自然語言處理、機器學習

## 開發

### 除錯模式
```bash
python debug_app.py
```

### 測試
```bash
python -m pytest tests/
```

## 授權

本專案僅供學習和研究使用。

## 支援

如有問題或建議，請查看 `docs/` 資料夾中的詳細文件。
