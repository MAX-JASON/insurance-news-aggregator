# 保險新聞聚合器開發指南 (Development Guide)

## 環境設置

### 系統要求

- **作業系統**: Windows 10+, macOS 10.15+, Ubuntu 20.04+ 或其他 Linux 發行版
- **Python**: 3.8 或更高版本
- **Git**: 最新穩定版
- **VS Code** 或其他 IDE (建議)

### 開發環境設置

#### 1. 複製專案

```bash
git clone https://github.com/your-repo/insurance-news-aggregator.git
cd insurance-news-aggregator
```

#### 2. 建立虛擬環境

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. 安裝依賴

```bash
pip install -r requirements.txt
```

#### 4. 設定開發配置

複製範例設定檔:
```bash
cp config/config.example.yaml config/config.yaml
```

編輯 `config/config.yaml` 內的開發設置。

#### 5. 初始化資料庫

```bash
python init_db.py
```

#### 6. 啟動開發伺服器

```bash
python run.py
```

應用將在 `http://localhost:5000` 啟動

## 專案結構

```text
insurance-news-aggregator/
├── analyzer/          # 新聞分析模組
├── api/              # API 路由
├── app/              # 應用核心
│   ├── services/     # 服務模組
│   └── templates/    # 應用模板
├── config/           # 配置文件
├── crawler/          # 爬蟲引擎
├── database/         # 資料庫模型
├── docs/             # 專案文檔
├── instance/         # 資料庫實例
├── logs/             # 日誌文件
├── migrations/       # 資料庫遷移
├── src/              # 源碼模組
├── web/              # Web 介面
└── tests/            # 測試程式
```

## 核心模組說明

### 爬蟲模組 (`crawler/`)

爬蟲模組負責從各新聞源獲取保險相關新聞。主要包含:

- `engine.py`: 爬蟲引擎核心
- `manager.py`: 爬蟲任務管理
- `real_crawler.py`: 真實網站爬取邏輯
- `rss_crawler.py`: RSS 訂閱源處理

#### 新增爬蟲源

如需新增新的爬蟲源，請按以下步驟:

1. 在 `config/sources.yaml` 中新增定義
2. 在 `crawler/` 中實現相應的爬取邏輯
3. 在 `crawler/manager.py` 中注冊新爬蟲
4. 撰寫測試確保爬取效果

### 分析模組 (`analyzer/`)

分析模組負責處理爬取的新聞，進行分類、關鍵字提取等。主要包含:

- `engine.py`: 分析引擎核心
- `insurance_dictionary.py`: 保險專業詞庫
- `cache.py`: 分析結果快取

#### 擴展分析功能

如需擴展分析能力，可在以下方面著手:

1. 擴充 `insurance_dictionary.py` 中的專業詞庫
2. 在 `engine.py` 中新增分析方法
3. 優化分類和關鍵字提取算法

### API 模組 (`api/`)

API 模組提供 RESTful 接口供外部調用。主要包含:

- `routes.py`: API 路由定義

#### API 開發規範

1. 所有 API 端點應遵循 RESTful 設計原則
2. 端點命名使用名詞複數形式 (e.g., `/api/news`)
3. 回應格式統一為 JSON
4. 必須包含狀態碼和資料欄位
5. 詳細錯誤處理和有意義的錯誤訊息

### Web 界面 (`web/`)

Web 界面模組處理前端頁面呈現。主要包含:

- `routes.py`: Web 路由定義
- `templates/`: HTML 模板
- `static/`: 靜態資源 (CSS, JS, 圖片等)

#### 前端開發指引

1. 使用 Bootstrap 5 作為 UI 框架
2. JavaScript 盡量使用模組化結構
3. 響應式設計支援移動端
4. 維護良好的無障礙支援

## 開發流程與規範

### Git 工作流

1. **分支管理**:
   - `main`: 穩定版本分支
   - `dev`: 開發分支
   - 功能分支命名: `feature/功能名稱`
   - 修復分支命名: `fix/問題描述`

2. **提交規範**:
   - 使用明確的提交訊息
   - 格式: `[模組] 動作: 詳細描述`
   - 例如: `[crawler] Fix: 修復工商時報爬取失敗問題`

### 測試規範

1. **單元測試**:
   - 所有核心功能必須有單元測試
   - 測試檔案命名: `test_<被測模組>.py`
   - 使用 pytest 框架

2. **執行測試**:

   ```bash
   python -m pytest
   ```

3. **測試覆蓋率**:

   ```bash
   python -m pytest --cov=.
   ```

### 代碼規範

1. **Python 風格**:
   - 遵循 PEP 8 規範
   - 使用 Black 格式化工具
   - 行長度限制: 88 字元

2. **命名規範**:
   - 類名: 駱駝命名法 (CamelCase)
   - 函數和變數: 蛇形命名法 (snake_case)
   - 常量: 大寫蛇形 (UPPER_SNAKE_CASE)

3. **文檔要求**:
   - 所有公開函數必須有 docstring
   - 複雜邏輯必須有註釋
   - 使用英文撰寫註釋

## 貢獻指南

### 新功能開發流程

1. 在 GitHub Issues 中提出功能建議
2. 討論並確定實施計劃
3. 從 `dev` 分支創建功能分支
4. 開發並測試新功能
5. 提交 Pull Request 到 `dev` 分支
6. 代碼審查通過後合併

### 錯誤修復流程

1. 在 GitHub Issues 中報告錯誤
2. 從 `dev` 分支創建修復分支
3. 修復並測試
4. 提交 Pull Request 到 `dev` 分支
5. 代碼審查通過後合併

## 資源與參考

### 官方文檔

- [Flask 文檔](https://flask.palletsprojects.com/)
- [SQLAlchemy 文檔](https://docs.sqlalchemy.org/)
- [BeautifulSoup 文檔](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

### 開發工具

- [VS Code](https://code.visualstudio.com/) - 推薦的編輯器
- [PyCharm](https://www.jetbrains.com/pycharm/) - 替代 IDE
- [Postman](https://www.postman.com/) - API 測試工具
- [SQLite Browser](https://sqlitebrowser.org/) - 資料庫查看工具

### 學習資源

- [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
- [Web Scraping with Python](https://realpython.com/beautiful-soup-web-scraper-python/)
- [SQLAlchemy ORM Tutorial](https://auth0.com/blog/sqlalchemy-orm-tutorial-for-python-developers/)

---

**文檔最後更新**: 2025年6月30日  
**維護團隊**: 開發團隊  
**聯絡郵件**: `dev-team@example.com`
