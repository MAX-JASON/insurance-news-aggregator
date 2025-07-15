
/**
 * 台灣保險新聞聚合器 - 增強JavaScript功能 v2.0
 */

// 全局應用對象
window.InsuranceNewsApp = {
    // 配置
    config: {
        apiBase: '/api/v1',
        updateInterval: 60000, // 1分鐘
        notificationDuration: 5000 // 5秒
    },
    
    // 初始化
    init: function() {
        console.log('🚀 保險新聞聚合器前端系統啟動');
        this.setupEventListeners();
        this.initializeAnimations();
        this.setupScrollToTop();
        this.startPeriodicUpdates();
    },
    
    // 設置事件監聽器
    setupEventListeners: function() {
        // 頁面載入完成
        document.addEventListener('DOMContentLoaded', () => {
            this.addFadeInAnimations();
            this.setupSearchFunctionality();
        });
        
        // 視窗滾動
        window.addEventListener('scroll', () => {
            this.handleScroll();
        });
    },
    
    // 設置搜索功能
    setupSearchFunctionality: function() {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            // 創建搜索容器
            const container = document.createElement('div');
            container.className = 'search-container position-relative';
            searchInput.parentNode.insertBefore(container, searchInput);
            container.appendChild(searchInput);
            
            // 添加搜索圖標
            const icon = document.createElement('i');
            icon.className = 'fas fa-search search-icon';
            container.appendChild(icon);
            
            // 添加樣式
            searchInput.className += ' search-input';
            searchInput.placeholder = '搜索保險新聞...';
            
            // 搜索事件
            searchInput.addEventListener('input', this.debounce(this.handleSearch, 300));
        }
    },
    
    // 處理搜索
    handleSearch: function(event) {
        const query = event.target.value.trim();
        if (query.length >= 2) {
            InsuranceNewsApp.performSearch(query);
        } else if (query.length === 0) {
            InsuranceNewsApp.clearSearch();
        }
    },
    
    // 執行搜索
    performSearch: function(query) {
        this.showLoadingState();
        
        fetch(`${this.config.apiBase}/news?keyword=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    this.updateNewsDisplay(data.data);
                    this.showNotification(`找到 ${data.data.length} 篇相關新聞`, 'success');
                } else {
                    this.showNotification('搜索失敗，請稍後再試', 'error');
                }
                this.hideLoadingState();
            })
            .catch(error => {
                console.error('搜索失敗:', error);
                this.showNotification('搜索失敗，請稍後再試', 'error');
                this.hideLoadingState();
            });
    },
    
    // 清除搜索
    clearSearch: function() {
        // 重新載入原始新聞列表
        location.reload();
    },
    
    // 更新新聞顯示
    updateNewsDisplay: function(articles) {
        const container = document.getElementById('newsContainer');
        if (!container) return;
        
        container.innerHTML = '';
        
        if (articles.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center py-5">
                    <i class="fas fa-search fa-3x text-muted mb-3"></i>
                    <h4 class="text-muted">暫無相關新聞</h4>
                    <p class="text-muted">請嘗試其他關鍵詞或稍後再試</p>
                </div>
            `;
            return;
        }
        
        articles.forEach((article, index) => {
            const articleElement = this.createArticleCard(article, index);
            container.appendChild(articleElement);
        });
        
        this.addFadeInAnimations();
    },
    
    // 創建新聞卡片
    createArticleCard: function(article, index) {
        const div = document.createElement('div');
        div.className = 'col-lg-6 col-md-6 mb-4';
        div.style.animationDelay = `${index * 0.1}s`;
        
        const publishedDate = new Date(article.published_date);
        const formattedDate = publishedDate.toLocaleDateString('zh-TW', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        div.innerHTML = `
            <div class="card news-card h-100 fade-in">
                <div class="card-body">
                    <h5 class="card-title mb-3">
                        <a href="${article.url}" class="news-title" target="_blank">
                            ${this.escapeHtml(article.title)}
                        </a>
                    </h5>
                    <div class="news-meta mb-2">
                        <i class="fas fa-calendar-alt me-1"></i>
                        ${formattedDate}
                        <span class="ms-3">
                            <i class="fas fa-globe me-1"></i>
                            ${this.escapeHtml(article.source?.name || '未知來源')}
                        </span>
                    </div>
                    ${article.summary ? `<p class="news-summary">${this.escapeHtml(article.summary.substring(0, 150))}...</p>` : ''}
                    <div class="d-flex justify-content-between align-items-center mt-3">
                        <div>
                            ${article.category ? `<span class="badge bg-primary">${article.category.name}</span>` : ''}
                            ${article.importance_score ? `<span class="badge bg-success ms-1">重要度: ${Math.round(article.importance_score * 100)}%</span>` : ''}
                        </div>
                        <a href="${article.url}" class="btn btn-primary btn-sm" target="_blank">
                            閱讀全文 <i class="fas fa-external-link-alt ms-1"></i>
                        </a>
                    </div>
                </div>
            </div>
        `;
        
        return div;
    },
    
    // 顯示載入狀態
    showLoadingState: function() {
        let overlay = document.getElementById('loadingOverlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'loadingOverlay';
            overlay.className = 'loading-overlay';
            overlay.innerHTML = `
                <div class="text-center">
                    <div class="loading-spinner mb-3"></div>
                    <h5>正在搜索新聞...</h5>
                </div>
            `;
            document.body.appendChild(overlay);
        }
        overlay.style.display = 'flex';
    },
    
    // 隱藏載入狀態
    hideLoadingState: function() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    },
    
    // 顯示通知
    showNotification: function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification alert alert-${type} alert-dismissible fade show`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // 自動移除
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, this.config.notificationDuration);
    },
    
    // 處理滾動
    handleScroll: function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const backToTopButton = document.querySelector('.back-to-top');
        
        if (backToTopButton) {
            backToTopButton.style.display = scrollTop > 300 ? 'block' : 'none';
        }
    },
    
    // 設置回到頂部按鈕
    setupScrollToTop: function() {
        const button = document.createElement('button');
        button.innerHTML = '<i class="fas fa-arrow-up"></i>';
        button.className = 'back-to-top';
        button.title = '回到頂部';
        
        button.onclick = () => {
            window.scrollTo({ 
                top: 0, 
                behavior: 'smooth' 
            });
        };
        
        document.body.appendChild(button);
    },
    
    // 開始定期更新
    startPeriodicUpdates: function() {
        // 定期更新統計數據
        setInterval(() => {
            this.updateStatsQuietly();
        }, this.config.updateInterval);
    },
    
    // 靜默更新統計
    updateStatsQuietly: function() {
        fetch(`${this.config.apiBase}/stats`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    this.updateStatsDisplay(data.data);
                }
            })
            .catch(error => {
                console.debug('統計更新失敗:', error);
            });
    },
    
    // 更新統計顯示
    updateStatsDisplay: function(stats) {
        const elements = {
            totalNewsCount: stats.totalNews,
            totalSourcesCount: stats.totalSources,
            totalCategoriesCount: stats.totalCategories,
            todayNewsCount: stats.todayNews
        };
        
        Object.keys(elements).forEach(id => {
            const element = document.getElementById(id);
            if (element && elements[id] !== undefined) {
                this.animateCounter(element, elements[id]);
            }
        });
    },
    
    // 數字動畫
    animateCounter: function(element, targetValue) {
        const currentValue = parseInt(element.textContent) || 0;
        const difference = targetValue - currentValue;
        
        if (difference === 0) return;
        
        const increment = difference / 20;
        let current = currentValue;
        
        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= targetValue) || 
                (increment < 0 && current <= targetValue)) {
                element.textContent = targetValue;
                clearInterval(timer);
            } else {
                element.textContent = Math.round(current);
            }
        }, 50);
    },
    
    // 初始化動畫
    initializeAnimations: function() {
        // 為所有卡片添加動畫
        const cards = document.querySelectorAll('.card');
        cards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.1}s`;
            card.classList.add('fade-in');
        });
    },
    
    // 添加淡入動畫
    addFadeInAnimations: function() {
        const elements = document.querySelectorAll('.card:not(.fade-in)');
        elements.forEach((element, index) => {
            element.style.animationDelay = `${index * 0.1}s`;
            element.classList.add('fade-in');
        });
    },
    
    // 工具函數
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    escapeHtml: function(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// 應用啟動
document.addEventListener('DOMContentLoaded', function() {
    InsuranceNewsApp.init();
});

// 全局錯誤處理
window.addEventListener('error', function(event) {
    console.error('全局錯誤:', event.error);
});

// 導出到全局
window.InsuranceNewsApp = InsuranceNewsApp;
