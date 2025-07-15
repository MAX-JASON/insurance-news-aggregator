// 保險新聞聚合器 - 前端腳本
document.addEventListener('DOMContentLoaded', function() {
    console.log('保險新聞聚合器已加載');
    
    // 初始化功能
    initializeApp();
    
    // 載入統計數據
    loadStats();
});

function initializeApp() {
    // 自動刷新新聞列表
    setupAutoRefresh();
    
    // 設置搜索功能
    setupSearch();
    
    // 設置新聞詳情模態框
    setupNewsModal();
    
    // 設置主題切換
    setupThemeToggle();
}

// 自動刷新功能
function setupAutoRefresh() {
    const refreshButton = document.getElementById('refresh-news');
    if (refreshButton) {
        refreshButton.addEventListener('click', function() {
            location.reload();
        });
    }
    
    // 每5分鐘自動刷新一次
    setInterval(function() {
        if (document.visibilityState === 'visible') {
            console.log('自動刷新新聞');
            // 這裡可以添加 AJAX 刷新邏輯
        }
    }, 300000); // 5分鐘
}

// 搜索功能
function setupSearch() {
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    
    if (searchInput && searchButton) {
        // 即時搜索
        searchInput.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            filterNews(query);
        });
        
        // 搜索按鈕點擊
        searchButton.addEventListener('click', function() {
            const query = searchInput.value;
            if (query.trim()) {
                performSearch(query);
            }
        });
        
        // 回車搜索
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const query = this.value;
                if (query.trim()) {
                    performSearch(query);
                }
            }
        });
    }
}

// 過濾新聞
function filterNews(query) {
    const newsItems = document.querySelectorAll('.news-item');
    newsItems.forEach(function(item) {
        const title = item.querySelector('.news-title')?.textContent.toLowerCase() || '';
        const content = item.querySelector('.news-content')?.textContent.toLowerCase() || '';
        
        if (title.includes(query) || content.includes(query)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

// 執行搜索
function performSearch(query) {
    console.log('搜索:', query);
    // 這裡可以添加向後端 API 發送搜索請求的邏輯
    window.location.href = `/search?q=${encodeURIComponent(query)}`;
}

// 新聞詳情模態框
function setupNewsModal() {
    const newsLinks = document.querySelectorAll('.news-link');
    newsLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const newsId = this.dataset.newsId;
            if (newsId) {
                showNewsModal(newsId);
            }
        });
    });
}

// 顯示新聞詳情模態框
function showNewsModal(newsId) {
    // 創建模態框
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">新聞詳情</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="spinner-border" role="status">
                        <span class="visually-hidden">載入中...</span>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // 使用 Bootstrap 模態框
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    // 載入新聞詳情
    fetch(`/api/v1/news/${newsId}`)
        .then(response => response.json())
        .then(data => {
            const modalBody = modal.querySelector('.modal-body');
            modalBody.innerHTML = `
                <h5>${data.title}</h5>
                <p class="text-muted">
                    <small>
                        來源: ${data.source} | 
                        發布時間: ${new Date(data.published_at).toLocaleString('zh-TW')}
                    </small>
                </p>
                <div class="news-content">
                    ${data.content || '暫無詳細內容'}
                </div>
                <hr>
                <p class="text-muted">
                    <small>
                        <a href="${data.url}" target="_blank" class="btn btn-outline-primary btn-sm">
                            查看原文
                        </a>
                    </small>
                </p>
            `;
        })
        .catch(error => {
            console.error('載入新聞詳情失敗:', error);
            const modalBody = modal.querySelector('.modal-body');
            modalBody.innerHTML = '<p class="text-danger">載入失敗，請稍後再試</p>';
        });
    
    // 清理模態框
    modal.addEventListener('hidden.bs.modal', function() {
        document.body.removeChild(modal);
    });
}

// 主題切換
function setupThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        // 載入保存的主題
        const savedTheme = localStorage.getItem('theme') || 'light';
        setTheme(savedTheme);
        
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.body.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            setTheme(newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }
}

// 設置主題
function setTheme(theme) {
    document.body.setAttribute('data-theme', theme);
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.textContent = theme === 'light' ? '🌙' : '☀️';
    }
}

// 工具函數：格式化日期
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-TW', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 工具函數：截取文本
function truncateText(text, maxLength = 150) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// 通知功能
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // 自動移除通知
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// 爬蟲監控相關功能
function updateCrawlerStatus() {
    // 只在爬蟲監控頁面或首頁更新狀態
    const shouldUpdate = window.location.pathname === '/' || 
                        window.location.pathname.includes('/crawler') ||
                        document.getElementById('crawler-status');
    
    if (!shouldUpdate) {
        return;
    }
    
    fetch('/api/v1/crawler/status')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const statusElement = document.getElementById('crawler-status');
            if (statusElement && data.data) {
                const isRunning = data.data.crawls.today.total > 0;
                statusElement.textContent = isRunning ? '運行中' : '待機中';
                statusElement.className = `badge ${isRunning ? 'bg-success' : 'bg-secondary'}`;
            }
            
            const statsElement = document.getElementById('crawler-stats');
            if (statsElement && data.data) {
                statsElement.innerHTML = `
                    <small class="text-muted">
                        總新聞: ${data.data.news.total} | 
                        今日新增: ${data.data.news.today}
                    </small>
                `;
            }
        })
        .catch(error => {
            console.error('更新爬蟲狀態失敗:', error);
            // 不顯示錯誤給用戶，只在控制台記錄
        });
}

// 載入統計數據
function loadStats() {
    fetch('/api/v1/stats')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateStatsDisplay(data.data);
            }
        })
        .catch(error => {
            console.warn('無法載入統計數據:', error);
            // 保持原有的模板數據，不做任何更改
        });
}

// 更新統計數據顯示
function updateStatsDisplay(stats) {
    // 更新統計卡片
    const statsCards = {
        totalNews: stats.totalNews,
        totalSources: stats.totalSources,
        totalCategories: stats.totalCategories,
        todayNews: stats.todayNews
    };
    
    // 查找並更新統計數據
    const cardTitles = document.querySelectorAll('.card-title');
    cardTitles.forEach(title => {
        const cardText = title.nextElementSibling;
        if (cardText && cardText.classList.contains('card-text')) {
            const text = cardText.textContent;
            if (text.includes('總新聞數量')) {
                title.textContent = statsCards.totalNews;
            } else if (text.includes('新聞來源')) {
                title.textContent = statsCards.totalSources;
            } else if (text.includes('新聞分類')) {
                title.textContent = statsCards.totalCategories;
            } else if (text.includes('今日更新')) {
                title.textContent = statsCards.todayNews;
            }
        }
    });
    
    console.log('統計數據已更新:', statsCards);
}

// 頁面載入完成後的初始化
document.addEventListener('DOMContentLoaded', function() {
    // 立即更新一次爬蟲狀態
    updateCrawlerStatus();
    
    // 只在首頁和爬蟲監控頁面設置定時器
    const shouldSetTimer = window.location.pathname === '/' || 
                          window.location.pathname.includes('/crawler') ||
                          document.getElementById('crawler-status');
    
    if (shouldSetTimer) {
        // 每30秒更新一次爬蟲狀態
        setInterval(updateCrawlerStatus, 30000);
    }
});

// 錯誤處理
window.addEventListener('error', function(e) {
    console.error('JavaScript錯誤:', e.error);
    showNotification('頁面發生錯誤，請刷新重試', 'warning');
});

// 網絡錯誤處理
window.addEventListener('unhandledrejection', function(e) {
    console.error('Promise錯誤:', e.reason);
    showNotification('網絡請求失敗，請檢查連接', 'warning');
});
