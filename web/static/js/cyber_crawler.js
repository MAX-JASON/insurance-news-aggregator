// Cyber Crawler JS - 賽博朋克爬蟲功能JS
// 此模組提供新聞爬取功能和界面交互

class CyberCrawler {
    constructor() {
        this.isRunning = false;
        this.resultsContainer = null;
        this.statusElement = null;
        this.progressBarElement = null;
        this.newsCountElement = null;
        this.init();
    }
    
    init() {
        console.log("🤖 初始化賽博朋克爬蟲系統...");
        this.createUIElements();
        this.bindEvents();
    }
    
    createUIElements() {
        // 創建爬蟲控制界面
        const controlPanel = document.createElement('div');
        controlPanel.className = 'cyber-crawler-panel';
        controlPanel.innerHTML = `
            <div class="cyber-crawler-header">
                <h3><i class="fas fa-spider"></i> 賽博朋克爬蟲控制台</h3>
                <div class="crawler-status">狀態: <span id="crawlerStatus" class="text-info">就緒</span></div>
            </div>
            <div class="progress cyber-progress mb-3">
                <div id="crawlerProgressBar" class="progress-bar progress-bar-striped progress-bar-animated" 
                     role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
            </div>
            <div class="d-flex gap-2 mb-3">
                <button id="startCrawlerBtn" class="neon-btn green flex-grow-1">
                    <i class="fas fa-play-circle"></i> 啟動爬蟲
                </button>
                <button id="viewResultsBtn" class="neon-btn purple flex-grow-1" disabled>
                    <i class="fas fa-chart-bar"></i> 查看結果
                </button>
            </div>
            <div class="crawler-stats">
                <div>爬取新聞: <span id="newsCount">0</span> 則</div>
                <div>來源數量: <span id="sourceCount">0</span> 個</div>
                <div>使用真實數據: <span id="useRealData">是</span></div>
            </div>
            <div id="crawlerResults" class="crawler-results" style="display: none;"></div>
        `;
        
        // 檢查是否在業務頁面，如果是則不顯示爬蟲控制台
        const currentPath = window.location.pathname;
        if (currentPath.includes('/business/')) {
            console.log('在業務頁面中，跳過爬蟲控制台創建');
            return;
        }
        
        // 安全地添加到頁面的內容區域，而不是頁面頂部
        const targetContainer = document.querySelector('.cyber-main') || 
                               document.querySelector('main .container') ||
                               document.querySelector('.container:not(.cyber-nav)') ||
                               document.querySelector('#content');
        
        if (targetContainer) {
            // 使用 appendChild 而不是 prepend，避免干擾導航
            targetContainer.appendChild(controlPanel);
        } else {
            console.warn('未找到合適的容器，跳過控制面板創建');
            return;
        }
        
        // 保存元素引用
        this.statusElement = document.getElementById('crawlerStatus');
        this.progressBarElement = document.getElementById('crawlerProgressBar');
        this.newsCountElement = document.getElementById('newsCount');
        this.resultsContainer = document.getElementById('crawlerResults');
    }
    
    bindEvents() {
        // 綁定爬蟲啟動按鈕
        document.getElementById('startCrawlerBtn').addEventListener('click', () => this.startCrawler());
        
        // 綁定查看結果按鈕
        document.getElementById('viewResultsBtn').addEventListener('click', () => this.toggleResults());
    }
    
    async startCrawler() {
        if (this.isRunning) return;
        this.isRunning = true;
        
        // 更新界面狀態
        this.statusElement.textContent = "執行中";
        this.statusElement.className = "text-warning";
        this.progressBarElement.style.width = "0%";
        document.getElementById('startCrawlerBtn').disabled = true;
        
        try {
            // 顯示模擬進度
            this.simulateProgress();
            
            // 呼叫後端爬蟲API
            const response = await fetch('/api/v1/crawler/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    use_mock: false, // 不使用模擬數據
                    sources: ['rss', 'real', 'ctee'] // 使用這些真實來源
                })
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                // 爬取成功
                this.progressBarElement.style.width = "100%";
                this.statusElement.textContent = "完成";
                this.statusElement.className = "text-success";
                document.getElementById('newsCount').textContent = "處理中...";
                
                // 設置定時檢查結果
                this.scheduleResultCheck();
            } else {
                // 爬取失敗
                this.progressBarElement.style.width = "100%";
                this.progressBarElement.className = "progress-bar bg-danger";
                this.statusElement.textContent = "失敗";
                this.statusElement.className = "text-danger";
                this.showErrorMessage(result.message || "爬蟲執行失敗");
            }
            
        } catch (error) {
            console.error("爬蟲執行錯誤:", error);
            this.progressBarElement.style.width = "100%";
            this.progressBarElement.className = "progress-bar bg-danger";
            this.statusElement.textContent = "錯誤";
            this.statusElement.className = "text-danger";
            this.showErrorMessage(error.message || "網絡錯誤");
        } finally {
            setTimeout(() => {
                document.getElementById('startCrawlerBtn').disabled = false;
                document.getElementById('viewResultsBtn').disabled = false;
                this.isRunning = false;
            }, 2000);
        }
    }
    
    simulateProgress() {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress > 90) {
                progress = 90;
                clearInterval(interval);
            }
            this.progressBarElement.style.width = `${progress}%`;
            this.progressBarElement.setAttribute('aria-valuenow', progress);
        }, 300);
        
        // 儲存interval以便在需要時清除
        this.progressInterval = interval;
    }
    
    async scheduleResultCheck() {
        // 等待2秒後檢查爬取結果
        setTimeout(async () => {
            try {
                const response = await fetch('/api/v1/crawler/status');
                const data = await response.json();
                
                if (data && data.status === 'success') {
                    // 更新結果
                    document.getElementById('newsCount').textContent = data.data.news.today || 0;
                    document.getElementById('sourceCount').textContent = data.data.sources.active || 0;
                    
                    // 顯示活動記錄
                    this.renderResults(data.data.recent_activities || []);
                    document.getElementById('viewResultsBtn').disabled = false;
                }
                
            } catch (error) {
                console.error("無法獲取爬蟲結果:", error);
            }
        }, 2000);
    }
    
    renderResults(activities) {
        if (!activities.length) {
            this.resultsContainer.innerHTML = '<div class="alert alert-info">沒有找到最近的爬蟲活動記錄</div>';
            return;
        }
        
        let html = `
            <h5 class="text-info mb-3">最近爬蟲活動</h5>
            <div class="table-responsive">
                <table class="table table-dark table-hover">
                    <thead>
                        <tr>
                            <th>來源</th>
                            <th>狀態</th>
                            <th>獲取新聞</th>
                            <th>時間</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        activities.forEach(activity => {
            const statusClass = activity.success ? 'text-success' : 'text-danger';
            const icon = activity.success ? 'check-circle' : 'times-circle';
            
            html += `
                <tr>
                    <td>${activity.source}</td>
                    <td class="${statusClass}">
                        <i class="fas fa-${icon}"></i>
                        ${activity.success ? '成功' : '失敗'}
                    </td>
                    <td>${activity.news_found || 0}</td>
                    <td>${this.formatTime(activity.created_at)}</td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
        
        this.resultsContainer.innerHTML = html;
    }
    
    formatTime(timestamp) {
        if (!timestamp) return 'N/A';
        
        try {
            const date = new Date(timestamp);
            return date.toLocaleString('zh-TW');
        } catch (e) {
            return timestamp;
        }
    }
    
    toggleResults() {
        if (this.resultsContainer.style.display === 'none') {
            this.resultsContainer.style.display = 'block';
        } else {
            this.resultsContainer.style.display = 'none';
        }
    }
    
    showErrorMessage(message) {
        this.resultsContainer.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
            </div>
        `;
        this.resultsContainer.style.display = 'block';
    }
}

// 初始化爬蟲
document.addEventListener('DOMContentLoaded', () => {
    window.cyberCrawler = new CyberCrawler();
    console.log("✅ 賽博朋克爬蟲系統已初始化");
});
