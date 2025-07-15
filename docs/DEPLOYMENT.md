# 部署指南 (Deployment Guide)

## 概覽

本文檔提供保險新聞聚合器的完整部署指南，包含開發環境、測試環境和生產環境的部署方式。

## 環境要求

### 系統要求
- **作業系統**: Linux (Ubuntu 20.04+) / Windows 10+ / macOS 10.15+
- **Python**: 3.8 或更高版本
- **記憶體**: 最少 2GB，建議 4GB+
- **硬碟**: 最少 10GB 可用空間
- **網路**: 穩定的網際網路連線

### 軟體依賴
- Git
- Python 3.8+
- pip
- virtualenv 或 conda
- SQLite (開發/測試) 或 PostgreSQL (生產)
- Nginx (生產環境)
- Redis (可選，用於快取)

## 開發環境部署

### 1. 獲取源碼

```bash
git clone https://github.com/your-repo/insurance-news-aggregator.git
cd insurance-news-aggregator
```

### 2. 建立虛擬環境

```bash
# 使用 venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 或使用 conda
conda create -n insurance-news python=3.8
conda activate insurance-news
```

### 3. 安裝依賴

```bash
pip install -r requirements.txt
```

### 4. 設定配置

```bash
# 複製配置範例
cp config/config.example.yaml config/config.yaml

# 編輯配置檔案
nano config/config.yaml  # 或使用其他編輯器
```

關鍵配置項目:
```yaml
database:
  url: "sqlite:///instance/insurance_news.db"

logging:
  level: "DEBUG"
  file: "logs/app.log"

crawler:
  delay: 2
  user_agents:
    - "Mozilla/5.0 (compatible; InsuranceBot/1.0)"

api:
  debug: true
  port: 5000
```

### 5. 初始化資料庫

```bash
# 執行資料庫遷移
alembic upgrade head

# 或手動初始化（如果沒有遷移檔案）
python -c "from database.models import *; from app import db; db.create_all()"
```

### 6. 啟動開發伺服器

```bash
python run.py
```

應用將在 http://localhost:5000 啟動

## 測試環境部署

### 1. 設定測試配置

建立 `config/config.test.yaml`:
```yaml
database:
  url: "sqlite:///instance/test_insurance_news.db"

logging:
  level: "INFO"

testing:
  enabled: true
```

### 2. 執行測試

```bash
# 安裝測試依賴
pip install -r requirements-test.txt

# 執行單元測試
python -m pytest tests/

# 執行整合測試
python -m pytest tests/integration/

# 產生測試報告
python -m pytest --cov=. --cov-report=html
```

## 生產環境部署

### 方案一：傳統部署

#### 1. 系統準備

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx postgresql

# CentOS/RHEL
sudo yum install python3 python3-pip nginx postgresql-server
```

#### 2. 建立應用用戶

```bash
sudo useradd -m -s /bin/bash insurance-news
sudo su - insurance-news
```

#### 3. 部署應用

```bash
# 在 insurance-news 用戶下
git clone https://github.com/your-repo/insurance-news-aggregator.git
cd insurance-news-aggregator

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 4. 生產配置

建立 `config/config.prod.yaml`:
```yaml
database:
  url: "postgresql://username:password@localhost/insurance_news"

security:
  secret_key: "your-secret-key-here"
  
api:
  debug: false
  host: "0.0.0.0"
  port: 8000

logging:
  level: "WARNING"
  file: "/var/log/insurance-news/app.log"
```

#### 5. 設定 PostgreSQL

```sql
-- 建立資料庫和用戶
CREATE USER insurance_user WITH PASSWORD 'secure_password';
CREATE DATABASE insurance_news OWNER insurance_user;
GRANT ALL PRIVILEGES ON DATABASE insurance_news TO insurance_user;
```

#### 6. 設定 Gunicorn

建立 `gunicorn.conf.py`:
```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

#### 7. 建立 Systemd 服務

建立 `/etc/systemd/system/insurance-news.service`:
```ini
[Unit]
Description=Insurance News Aggregator
After=network.target

[Service]
User=insurance-news
Group=insurance-news
WorkingDirectory=/home/insurance-news/insurance-news-aggregator
Environment="PATH=/home/insurance-news/insurance-news-aggregator/venv/bin"
ExecStart=/home/insurance-news/insurance-news-aggregator/venv/bin/gunicorn -c gunicorn.conf.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

啟動服務:
```bash
sudo systemctl daemon-reload
sudo systemctl enable insurance-news
sudo systemctl start insurance-news
```

#### 8. 設定 Nginx

建立 `/etc/nginx/sites-available/insurance-news`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/insurance-news/insurance-news-aggregator/web/static;
    }
}
```

啟用網站:
```bash
sudo ln -s /etc/nginx/sites-available/insurance-news /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 方案二：Docker 部署

#### 1. 建立 Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴檔案
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY . .

# 建立必要目錄
RUN mkdir -p logs instance

# 設定環境變數
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 5000

# 啟動命令
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]
```

#### 2. 建立 docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./logs:/app/logs
      - ./instance:/app/instance
      - ./config:/app/config
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/insurance_news
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: insurance_news
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web

volumes:
  postgres_data:
```

#### 3. 部署命令

```bash
# 建立和啟動容器
docker-compose up -d

# 檢查服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f web
```

## SSL 憑證設定

### 使用 Let's Encrypt

```bash
# 安裝 Certbot
sudo apt install certbot python3-certbot-nginx

# 取得憑證
sudo certbot --nginx -d your-domain.com

# 設定自動更新
sudo crontab -e
# 加入以下行：
# 0 2 * * * /usr/bin/certbot renew --quiet
```

## 監控與維護

### 1. 日誌監控

設定 logrotate (`/etc/logrotate.d/insurance-news`):
```
/var/log/insurance-news/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 insurance-news insurance-news
    postrotate
        systemctl reload insurance-news
    endscript
}
```

### 2. 健康檢查

建立健康檢查端點:
```python
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })
```

### 3. 備份策略

資料庫備份腳本:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/insurance-news"
DB_NAME="insurance_news"

mkdir -p $BACKUP_DIR

# PostgreSQL 備份
pg_dump $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# 壓縮備份
gzip $BACKUP_DIR/db_backup_$DATE.sql

# 刪除 7 天前的備份
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete
```

### 4. 效能監控

使用 New Relic, DataDog 或 Prometheus + Grafana 進行監控。

## 故障排除

### 常見問題

1. **應用無法啟動**
   - 檢查 Python 版本和依賴
   - 檢查配置檔案格式
   - 查看應用日誌

2. **資料庫連線失敗**
   - 檢查資料庫服務狀態
   - 驗證連線字串
   - 檢查防火牆設定

3. **爬蟲功能異常**
   - 檢查網路連線
   - 驗證目標網站可訪問性
   - 檢查爬蟲設定

### 日誌查看

```bash
# 系統日誌
sudo journalctl -u insurance-news -f

# 應用日誌
tail -f /var/log/insurance-news/app.log

# Nginx 日誌
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

## 安全建議

1. **定期更新**: 保持系統和依賴套件更新
2. **防火牆**: 只開放必要端口
3. **SSL/TLS**: 使用 HTTPS 加密傳輸
4. **密碼策略**: 使用強密碼和密鑰輪換
5. **備份**: 定期備份資料和配置
6. **監控**: 設定異常警報

---

**最後更新**: 2025年6月15日  
**維護團隊**: DevOps Team
