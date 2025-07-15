# Apps 資料夾

這個資料夾包含主要的應用程序入口文件。

## 文件說明

- `start_app.py` - 主要應用程序啟動器，用於啟動Flask Web應用
- `run.py` - 另一個應用程序入口點
- `app_professional_final.py` - 專業版應用程序主文件
- `debug_app.py` - 調試版本的應用程序啟動器

## 使用說明

### 啟動應用程序
```bash
# 使用主要啟動器
python apps/start_app.py

# 使用run.py啟動
python apps/run.py

# 啟動調試模式
python apps/debug_app.py
```

### 部署說明
- `start_app.py` 是推薦的生產環境啟動器
- `debug_app.py` 僅用於開發和調試
- `app_professional_final.py` 包含專業版功能
