# API 文檔 (API Documentation)

## 概覽

保險新聞聚合器提供 RESTful API，支援新聞資料的獲取、搜索和分析功能。

**Base URL**: `http://localhost:5000/api`  
**版本**: v1  
**認證**: Bearer Token (部分端點需要)

## 認證

### 獲取 Token
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

響應:
```json
{
  "status": "success",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_in": 3600
  }
}
```

## 新聞 API

### 獲取新聞列表

```http
GET /api/news
```

參數:
- `page` (int, optional): 頁碼，預設 1
- `per_page` (int, optional): 每頁數量，預設 20，最大 100
- `category` (string, optional): 分類篩選
- `date_from` (string, optional): 開始日期 (YYYY-MM-DD)
- `date_to` (string, optional): 結束日期 (YYYY-MM-DD)

範例:
```http
GET /api/news?page=1&per_page=10&category=life_insurance
```

響應:
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "title": "保險新聞標題",
      "summary": "新聞摘要...",
      "source": "工商時報",
      "published_at": "2025-06-15T10:00:00Z",
      "category": "life_insurance",
      "url": "https://example.com/news/1"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 150,
    "pages": 15
  }
}
```

### 獲取新聞詳情

```http
GET /api/news/{id}
```

響應:
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "title": "保險新聞完整標題",
    "content": "完整新聞內容...",
    "summary": "新聞摘要",
    "source": "工商時報",
    "author": "記者姓名",
    "published_at": "2025-06-15T10:00:00Z",
    "created_at": "2025-06-15T10:30:00Z",
    "updated_at": "2025-06-15T10:30:00Z",
    "category": "life_insurance",
    "tags": ["壽險", "保費", "監管"],
    "url": "https://example.com/news/1",
    "analysis": {
      "sentiment": "neutral",
      "importance_score": 0.75,
      "keywords": ["保險", "法規", "金管會"]
    }
  }
}
```

## 搜索 API

### 基本搜索

```http
GET /api/search
```

參數:
- `q` (string, required): 搜索關鍵字
- `page` (int, optional): 頁碼
- `per_page` (int, optional): 每頁數量
- `sort` (string, optional): 排序方式 (`relevance`, `date`, `importance`)

範例:
```http
GET /api/search?q=壽險&sort=date&page=1
```

### 高級搜索

```http
POST /api/search/advanced
Content-Type: application/json
```

請求體:
```json
{
  "keywords": ["保險", "理賠"],
  "exclude_keywords": ["廣告"],
  "category": "life_insurance",
  "source": ["工商時報", "經濟日報"],
  "date_range": {
    "from": "2025-01-01",
    "to": "2025-06-15"
  },
  "sentiment": "positive",
  "importance_min": 0.5
}
```

## 分析 API

### 獲取分析報告

```http
GET /api/analysis
```

參數:
- `type` (string): 報告類型 (`daily`, `weekly`, `monthly`)
- `date` (string): 報告日期

範例:
```http
GET /api/analysis?type=daily&date=2025-06-15
```

響應:
```json
{
  "status": "success",
  "data": {
    "report_type": "daily",
    "date": "2025-06-15",
    "summary": {
      "total_news": 25,
      "categories": {
        "life_insurance": 10,
        "property_insurance": 8,
        "health_insurance": 7
      },
      "sentiment": {
        "positive": 12,
        "neutral": 10,
        "negative": 3
      }
    },
    "top_keywords": [
      {"keyword": "保險", "count": 45},
      {"keyword": "理賠", "count": 32},
      {"keyword": "保費", "count": 28}
    ],
    "trending_topics": [
      "新冠肺炎保險理賠",
      "數位保險服務",
      "ESG永續保險"
    ]
  }
}
```

### 新聞趨勢分析

```http
GET /api/analysis/trends
```

參數:
- `period` (string): 時間週期 (`7d`, `30d`, `90d`)
- `category` (string, optional): 分類篩選

## 統計 API

### 系統統計

```http
GET /api/stats
Authorization: Bearer {token}
```

響應:
```json
{
  "status": "success",
  "data": {
    "total_news": 1500,
    "sources_count": 8,
    "categories_count": 6,
    "last_update": "2025-06-15T10:00:00Z",
    "crawler_status": "active",
    "daily_stats": {
      "today": 25,
      "yesterday": 23,
      "growth_rate": 0.087
    }
  }
}
```

## 錯誤處理

### 錯誤響應格式

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "Invalid page parameter",
    "details": "Page must be a positive integer"
  },
  "timestamp": "2025-06-15T10:00:00Z"
}
```

### 常見錯誤碼

| 狀態碼 | 錯誤碼 | 說明 |
|--------|--------|------|
| 400 | INVALID_PARAMETER | 參數錯誤 |
| 401 | UNAUTHORIZED | 未授權 |
| 403 | FORBIDDEN | 權限不足 |
| 404 | NOT_FOUND | 資源不存在 |
| 429 | RATE_LIMIT_EXCEEDED | 請求頻率超限 |
| 500 | INTERNAL_ERROR | 內部錯誤 |

## 限流規則

- 未認證用戶: 100 請求/小時
- 認證用戶: 1000 請求/小時
- 搜索 API: 50 請求/小時 (額外限制)

## SDK 和範例

### Python 範例

```python
import requests

# 基本配置
BASE_URL = "http://localhost:5000/api"
headers = {"Authorization": "Bearer YOUR_TOKEN"}

# 獲取新聞列表
response = requests.get(f"{BASE_URL}/news", headers=headers)
news_list = response.json()

# 搜索新聞
search_params = {"q": "壽險", "sort": "date"}
response = requests.get(f"{BASE_URL}/search", 
                       params=search_params, headers=headers)
search_results = response.json()
```

### JavaScript 範例

```javascript
const API_BASE = 'http://localhost:5000/api';
const token = 'YOUR_TOKEN';

// 獲取新聞
async function getNews() {
  const response = await fetch(`${API_BASE}/news`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return await response.json();
}

// 搜索新聞
async function searchNews(query) {
  const response = await fetch(`${API_BASE}/search?q=${query}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return await response.json();
}
```

## 變更日誌

### v1.0.0 (2025-06-15)
- 初始版本發布
- 基本新聞 CRUD 操作
- 搜索功能
- 分析報告 API

---

**最後更新**: 2025年6月15日  
**技術支援**: api-support@example.com
