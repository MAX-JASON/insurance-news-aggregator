# 雲端部署指南

## 🚀 Render 部署（推薦 - 免費）

1. 前往 [Render.com](https://render.com)
2. 連接您的 GitHub 帳號
3. 點擊 "New Web Service"
4. 選擇您的 `insurance-news-aggregator` 倉庫
5. 配置如下：
   - **Name**: insurance-news-aggregator
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free

## 🔥 Railway 部署

1. 前往 [Railway.app](https://railway.app)
2. 點擊 "Start a New Project"
3. 選擇 "Deploy from GitHub repo"
4. 選擇您的倉庫
5. Railway 會自動檢測並部署

## 🟣 Heroku 部署

```bash
# 安裝 Heroku CLI
# 然後執行：
heroku create your-app-name
git push heroku main
```

## 📱 iPad 使用方式

部署完成後，您會獲得一個網址，例如：
- `https://your-app-name.onrender.com`
- `https://your-app-name.up.railway.app`
- `https://your-app-name.herokuapp.com`

直接在 iPad 的 Safari 中輸入這個網址就可以使用了！

## 🌐 方案二：GitHub Codespaces

1. 在 GitHub 倉庫頁面點擊綠色的 "Code" 按鈕
2. 選擇 "Codespaces" 標籤
3. 點擊 "Create codespace on main"
4. 等待環境啟動後，在終端執行：
   ```bash
   python apps/start_app.py
   ```
5. 點擊彈出的鏈接就可以在 iPad 上使用

## 📋 環境變數設定

在雲端平台中設定以下環境變數：
- `SECRET_KEY`: 隨機字串（用於安全性）
- `DATABASE_URL`: 資料庫連接字串（可選，預設使用 SQLite）
