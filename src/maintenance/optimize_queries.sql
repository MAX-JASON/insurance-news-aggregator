-- 保險新聞聚合器查詢優化腳本
-- 建立視圖以優化常用查詢

-- 1. 最新新聞視圖
CREATE VIEW IF NOT EXISTS vw_latest_news AS
SELECT 
    n.id, 
    n.title, 
    n.summary, 
    n.published_date, 
    n.crawled_date,
    n.view_count,
    n.importance_score,
    n.sentiment_score,
    s.name AS source_name,
    c.name AS category_name,
    n.image_url
FROM 
    news n
JOIN 
    news_sources s ON n.source_id = s.id
LEFT JOIN 
    news_categories c ON n.category_id = c.id
WHERE 
    n.status = 'active'
ORDER BY 
    n.published_date DESC
LIMIT 100;

-- 2. 重要新聞視圖
CREATE VIEW IF NOT EXISTS vw_important_news AS
SELECT 
    n.id, 
    n.title, 
    n.summary, 
    n.published_date, 
    n.importance_score,
    n.sentiment_score,
    s.name AS source_name,
    c.name AS category_name
FROM 
    news n
JOIN 
    news_sources s ON n.source_id = s.id
LEFT JOIN 
    news_categories c ON n.category_id = c.id
WHERE 
    n.status = 'active'
    AND n.importance_score >= 0.7
ORDER BY 
    n.importance_score DESC,
    n.published_date DESC
LIMIT 100;

-- 3. 各來源新聞統計視圖
CREATE VIEW IF NOT EXISTS vw_news_by_source_stats AS
SELECT 
    s.id AS source_id,
    s.name AS source_name,
    COUNT(n.id) AS news_count,
    MAX(n.published_date) AS latest_news_date,
    AVG(n.importance_score) AS avg_importance_score
FROM 
    news_sources s
LEFT JOIN 
    news n ON s.id = n.source_id AND n.status = 'active'
GROUP BY 
    s.id, s.name;

-- 4. 各分類新聞統計視圖
CREATE VIEW IF NOT EXISTS vw_news_by_category_stats AS
SELECT 
    c.id AS category_id,
    c.name AS category_name,
    COUNT(n.id) AS news_count,
    MAX(n.published_date) AS latest_news_date,
    AVG(n.importance_score) AS avg_importance_score
FROM 
    news_categories c
LEFT JOIN 
    news n ON c.id = n.category_id AND n.status = 'active'
GROUP BY 
    c.id, c.name;

-- 5. 每日新聞統計視圖
CREATE VIEW IF NOT EXISTS vw_daily_news_stats AS
SELECT 
    DATE(n.published_date) AS news_date,
    COUNT(n.id) AS news_count,
    COUNT(DISTINCT n.source_id) AS source_count,
    AVG(n.importance_score) AS avg_importance_score
FROM 
    news n
WHERE 
    n.status = 'active'
    AND n.published_date >= date('now', '-30 days')
GROUP BY 
    DATE(n.published_date)
ORDER BY 
    news_date DESC;

-- 6. 新聞情感分析視圖
CREATE VIEW IF NOT EXISTS vw_news_sentiment_analysis AS
SELECT 
    DATE(n.published_date) AS news_date,
    AVG(CASE WHEN n.sentiment_score > 0.3 THEN 1 ELSE 0 END) AS positive_ratio,
    AVG(CASE WHEN n.sentiment_score < -0.3 THEN 1 ELSE 0 END) AS negative_ratio,
    AVG(CASE WHEN n.sentiment_score BETWEEN -0.3 AND 0.3 THEN 1 ELSE 0 END) AS neutral_ratio,
    COUNT(n.id) AS news_count
FROM 
    news n
WHERE 
    n.status = 'active'
    AND n.published_date >= date('now', '-30 days')
    AND n.sentiment_score IS NOT NULL
GROUP BY 
    DATE(n.published_date)
ORDER BY 
    news_date DESC;

-- 7. 熱門關鍵詞視圖 (SQLite不支持JSON操作，需要在應用程式層面實現)
-- 此部分在PostgreSQL中可以實現，但SQLite需要在程式中處理

-- 8. 爬蟲執行統計視圖
CREATE VIEW IF NOT EXISTS vw_crawl_performance_stats AS
SELECT 
    cl.source_id,
    s.name AS source_name,
    COUNT(cl.id) AS crawl_count,
    SUM(CASE WHEN cl.success THEN 1 ELSE 0 END) AS success_count,
    SUM(CASE WHEN NOT cl.success THEN 1 ELSE 0 END) AS failure_count,
    AVG(cl.duration) AS avg_duration,
    MAX(cl.start_time) AS last_crawl_time,
    SUM(cl.news_new) AS total_news_added,
    SUM(cl.news_updated) AS total_news_updated
FROM 
    crawl_logs cl
JOIN 
    news_sources s ON cl.source_id = s.id
WHERE 
    cl.start_time >= date('now', '-30 days')
GROUP BY 
    cl.source_id, s.name;

-- 9. 用戶活動統計視圖
CREATE VIEW IF NOT EXISTS vw_user_activity_stats AS
SELECT 
    u.id AS user_id,
    u.username,
    u.role,
    COUNT(DISTINCT sn.news_id) AS saved_news_count,
    (
        SELECT COUNT(DISTINCT news_id) 
        FROM saved_news 
        WHERE user_id = u.id AND created_at >= date('now', '-7 days')
    ) AS recent_saved_count,
    u.last_login,
    (
        SELECT MAX(created_at) 
        FROM saved_news 
        WHERE user_id = u.id
    ) AS last_activity
FROM 
    users u
LEFT JOIN 
    saved_news sn ON u.id = sn.user_id
GROUP BY 
    u.id, u.username, u.role;

-- 10. 系統錯誤統計視圖
CREATE VIEW IF NOT EXISTS vw_error_logs_summary AS
SELECT 
    DATE(timestamp) AS error_date,
    level,
    module,
    COUNT(*) AS error_count
FROM 
    error_logs
WHERE 
    timestamp >= date('now', '-30 days')
GROUP BY 
    DATE(timestamp), level, module
ORDER BY 
    error_date DESC, error_count DESC;
