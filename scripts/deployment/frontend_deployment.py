"""
前端增強部署腳本
Frontend Enhancement Deployment Script

將之前創建的前端優化功能實際部署到Web應用中
"""

import os
import shutil
import logging
from datetime import datetime

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('frontend_deployer')

class FrontendDeployer:
    """前端部署器"""
    
    def __init__(self):
        """初始化部署器"""
        self.static_dir = "web/static"
        self.templates_dir = "web/templates"
        logger.info("🎨 前端部署器初始化完成")
    
    def deploy_enhanced_css(self):
        """部署增強的CSS樣式"""
        enhanced_css = """
/* 台灣保險新聞聚合器 - 增強樣式表 v2.0 */

/* 主要變數定義 */
:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
    --success-color: #28a745;
    --info-color: #17a2b8;
    --warning-color: #ffc107;
    --danger-color: #dc3545;
    --light-color: #f8f9fa;
    --dark-color: #343a40;
    --font-family-sans: 'Microsoft JhengHei', 'PingFang TC', Arial, sans-serif;
}

/* 全局優化 */
body {
    font-family: var(--font-family-sans);
    line-height: 1.6;
    color: var(--dark-color);
    background-color: #fafbfc;
}

/* 導航欄美化 */
.navbar {
    box-shadow: 0 2px 4px rgba(0,0,0,.1);
    background: linear-gradient(135deg, #007bff, #0056b3) !important;
}

.navbar-brand {
    font-weight: 600;
    font-size: 1.3rem;
    transition: all 0.3s ease;
}

.navbar-brand:hover {
    transform: scale(1.05);
}

.nav-link {
    transition: all 0.3s ease;
    border-radius: 0.375rem;
    margin: 0 0.2rem;
}

.nav-link:hover {
    background-color: rgba(255, 255, 255, 0.15);
    transform: translateY(-1px);
}

/* 卡片美化 */
.card {
    border: none;
    border-radius: 0.75rem;
    box-shadow: 0 0.125rem 0.5rem rgba(0, 0, 0, 0.075);
    transition: all 0.3s ease;
    background: white;
    overflow: hidden;
}

.card:hover {
    transform: translateY(-3px);
    box-shadow: 0 0.5rem 1.5rem rgba(0, 0, 0, 0.15);
}

.card-header {
    background: linear-gradient(135deg, var(--primary-color), var(--info-color));
    color: white;
    font-weight: 600;
    border-radius: 0.75rem 0.75rem 0 0 !important;
    border: none;
}

/* 新聞卡片特殊樣式 */
.news-card {
    border-left: 4px solid var(--primary-color);
    transition: all 0.3s ease;
}

.news-card:hover {
    border-left-color: var(--success-color);
    background: linear-gradient(145deg, #ffffff, #f8f9fa);
}

.news-title {
    color: var(--dark-color);
    text-decoration: none;
    font-weight: 600;
    transition: color 0.3s ease;
}

.news-title:hover {
    color: var(--primary-color);
    text-decoration: none;
}

.news-meta {
    color: var(--secondary-color);
    font-size: 0.875rem;
}

.news-summary {
    color: #495057;
    line-height: 1.6;
    margin-top: 0.5rem;
}

/* 統計卡片 */
.stats-card {
    background: linear-gradient(135deg, var(--primary-color), var(--info-color));
    color: white;
    transition: all 0.3s ease;
    border-radius: 1rem;
}

.stats-card:hover {
    transform: scale(1.05) translateY(-2px);
    box-shadow: 0 0.75rem 2rem rgba(0, 123, 255, 0.3);
}

.stats-number {
    font-size: 2.5rem;
    font-weight: 700;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    line-height: 1;
}

/* 按鈕增強 */
.btn {
    border-radius: 0.5rem;
    font-weight: 500;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.btn:hover {
    transform: translateY(-1px);
}

.btn-primary {
    background: linear-gradient(135deg, #007bff, #0056b3);
    border: none;
}

.btn-primary:hover {
    background: linear-gradient(135deg, #0056b3, #004085);
}

/* 載入動畫 */
.loading-spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid rgba(0,123,255,.3);
    border-radius: 50%;
    border-top-color: #007bff;
    animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* 淡入動畫 */
.fade-in {
    animation: fadeIn 0.6s ease-in;
}

@keyframes fadeIn {
    from { 
        opacity: 0; 
        transform: translateY(20px); 
    }
    to { 
        opacity: 1; 
        transform: translateY(0); 
    }
}

/* 通知樣式 */
.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 1050;
    min-width: 300px;
    border-radius: 0.5rem;
    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
    animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

/* 表單優化 */
.form-control {
    border-radius: 0.5rem;
    border: 1px solid #ddd;
    transition: all 0.3s ease;
}

.form-control:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
    transform: translateY(-1px);
}

/* 搜索框特殊樣式 */
.search-container {
    position: relative;
    max-width: 500px;
    margin: 0 auto;
}

.search-input {
    border-radius: 2rem;
    padding-left: 3rem;
    border: 2px solid #e9ecef;
    transition: all 0.3s ease;
}

.search-input:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.15);
}

.search-icon {
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--secondary-color);
}

/* 響應式優化 */
@media (max-width: 768px) {
    .stats-number {
        font-size: 2rem;
    }
    
    .card {
        margin-bottom: 1rem;
    }
    
    .display-4 {
        font-size: 2rem;
    }
    
    .notification {
        right: 10px;
        left: 10px;
        min-width: auto;
    }
}

/* 滾動條美化 */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: var(--light-color);
}

::-webkit-scrollbar-thumb {
    background: var(--secondary-color);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--primary-color);
}

/* 頁腳樣式 */
.footer {
    background: linear-gradient(135deg, var(--dark-color), #495057);
    color: var(--light-color);
    margin-top: 3rem;
    padding: 2rem 0;
}

/* 標籤樣式 */
.badge {
    border-radius: 1rem;
    font-weight: 500;
}

/* 分頁樣式 */
.pagination .page-link {
    border-radius: 0.5rem;
    margin: 0 0.125rem;
    border: none;
    color: var(--primary-color);
}

.pagination .page-link:hover {
    background-color: var(--primary-color);
    color: white;
    transform: translateY(-1px);
}

/* 載入狀態 */
.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255, 0.9);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
}

/* 回到頂部按鈕 */
.back-to-top {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 50px;
    height: 50px;
    background: var(--primary-color);
    color: white;
    border: none;
    border-radius: 50%;
    font-size: 1.2rem;
    cursor: pointer;
    transition: all 0.3s ease;
    z-index: 1000;
    display: none;
}

.back-to-top:hover {
    background: var(--info-color);
    transform: translateY(-3px);
}
"""
        
        css_path = os.path.join(self.static_dir, "css", "enhanced.css")
        os.makedirs(os.path.dirname(css_path), exist_ok=True)
        
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(enhanced_css)
        
        logger.info("✅ 增強CSS樣式已部署")
    
    def deploy_enhanced_js(self):
        """部署增強的JavaScript功能"""
        enhanced_js = """
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
"""
        
        js_path = os.path.join(self.static_dir, "js", "enhanced.js")
        os.makedirs(os.path.dirname(js_path), exist_ok=True)
        
        with open(js_path, "w", encoding="utf-8") as f:
            f.write(enhanced_js)
        
        logger.info("✅ 增強JavaScript功能已部署")
    
    def update_base_template(self):
        """更新基礎模板以引入增強功能"""
        base_template_path = os.path.join(self.templates_dir, "base.html")
        
        if os.path.exists(base_template_path):
            # 讀取現有模板
            with open(base_template_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 檢查是否已經包含增強CSS
            if "enhanced.css" not in content:
                # 在現有CSS後添加增強CSS
                css_insertion = '    <link href="{{ url_for(\'static\', filename=\'css/enhanced.css\') }}" rel="stylesheet">'
                content = content.replace(
                    '<link href="{{ url_for(\'static\', filename=\'css/main.css\') }}" rel="stylesheet">',
                    '<link href="{{ url_for(\'static\', filename=\'css/main.css\') }}" rel="stylesheet">\n' + css_insertion
                )
            
            # 檢查是否已經包含增強JS
            if "enhanced.js" not in content:
                # 在body結束前添加增強JS
                js_insertion = '    <script src="{{ url_for(\'static\', filename=\'js/enhanced.js\') }}"></script>'
                content = content.replace(
                    '</body>',
                    '    ' + js_insertion + '\n</body>'
                )
            
            # 寫回文件
            with open(base_template_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            logger.info("✅ 基礎模板已更新，引入增強功能")
        else:
            logger.warning("⚠️ base.html 模板不存在，跳過更新")
    
    def create_search_functionality(self):
        """在首頁添加搜索功能"""
        index_template_path = os.path.join(self.templates_dir, "index.html")
        
        if os.path.exists(index_template_path):
            with open(index_template_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 檢查是否已經有搜索框
            if "searchInput" not in content:
                # 在統計數據後添加搜索框
                search_section = '''
<!-- 搜索功能 -->
<div class="row mb-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">
                    <i class="fas fa-search me-2"></i>搜索保險新聞
                </h5>
            </div>
            <div class="card-body">
                <div class="search-container">
                    <input type="text" id="searchInput" class="form-control search-input" 
                           placeholder="輸入關鍵詞搜索保險新聞...">
                    <i class="fas fa-search search-icon"></i>
                </div>
                <small class="text-muted">支持搜索新聞標題、內容和來源</small>
            </div>
        </div>
    </div>
</div>
'''
                
                # 在最新新聞之前插入搜索功能
                content = content.replace(
                    '<!-- 最新新聞 -->',
                    search_section + '\n<!-- 最新新聞 -->'
                )
                
                # 為新聞容器添加ID
                content = content.replace(
                    '<div class="row">',
                    '<div class="row" id="newsContainer">',
                    1  # 只替換第一個
                )
            
            with open(index_template_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            logger.info("✅ 首頁搜索功能已添加")
        else:
            logger.warning("⚠️ index.html 模板不存在，跳過搜索功能添加")
    
    def deploy_all_enhancements(self):
        """部署所有前端增強功能"""
        logger.info("🚀 開始部署前端增強功能...")
        
        try:
            # 確保目錄存在
            os.makedirs(self.static_dir, exist_ok=True)
            os.makedirs(self.templates_dir, exist_ok=True)
            
            # 部署各項增強功能
            self.deploy_enhanced_css()
            self.deploy_enhanced_js()
            self.update_base_template()
            self.create_search_functionality()
            
            logger.info("🎉 前端增強功能部署完成！")
            
            return {
                'status': 'success',
                'message': '前端增強功能已成功部署',
                'features': [
                    '增強CSS樣式（美化界面、動畫效果）',
                    '增強JavaScript功能（搜索、實時更新）',
                    '基礎模板更新（引入新功能）',
                    '搜索功能集成（首頁搜索框）'
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ 前端增強部署失敗: {e}")
            return {
                'status': 'error',
                'message': f'部署失敗: {e}'
            }

def main():
    """主執行函數"""
    print("🎨 啟動前端增強部署...")
    
    deployer = FrontendDeployer()
    result = deployer.deploy_all_enhancements()
    
    print(f"\n📋 部署結果:")
    print(f"  狀態: {result['status']}")
    print(f"  訊息: {result['message']}")
    
    if 'features' in result:
        print("  已部署功能:")
        for feature in result['features']:
            print(f"    ✅ {feature}")
    
    print("\n🚀 建議重新啟動應用以查看效果:")
    print("  python run.py")

if __name__ == "__main__":
    main()
