/**
 * 頁面通用腳本
 * 處理所有頁面共用的功能
 */

// 全局錯誤狀態追蹤
window.globalErrorCount = 0;
window.apiErrorTracker = {};

document.addEventListener('DOMContentLoaded', function() {
    // 初始化自動佈署調整
    safeExecute(initResponsiveAdjustments, 'ResponsiveAdjustments');
    
    // 初始化圖片錯誤處理
    safeExecute(initImageErrorHandling, 'ImageErrorHandling');
    
    // 初始化全局AJAX錯誤處理
    safeExecute(initAjaxErrorHandling, 'AjaxErrorHandling');
    
    // 初始化導航欄活動標記
    safeExecute(highlightCurrentNavItem, 'NavigationHighlight');
    
    // 初始化API錯誤追蹤
    safeExecute(initApiErrorTracking, 'ApiErrorTracking');
    
    console.log('通用腳本已載入');
});

// 安全執行函數
function safeExecute(fn, name) {
    try {
        fn();
    } catch (err) {
        console.error(`執行${name}時發生錯誤:`, err);
        // 不阻止其他功能繼續執行
    }
}

// 初始化API錯誤追蹤
function initApiErrorTracking() {
    // 創建API錯誤追蹤代理
    window.apiErrorTracker = {
        errors: {},
        
        // 記錄API錯誤
        logError: function(endpoint, status, message) {
            if (!this.errors[endpoint]) {
                this.errors[endpoint] = {
                    count: 0,
                    lastError: null,
                    disabled: false
                };
            }
            
            this.errors[endpoint].count++;
            this.errors[endpoint].lastError = { 
                status: status, 
                message: message,
                time: new Date().toISOString()
            };
            
            // 如果錯誤次數過多，禁用該API端點
            if (this.errors[endpoint].count >= 3) {
                this.errors[endpoint].disabled = true;
                console.warn(`API端點 ${endpoint} 因多次失敗已被禁用`);
            }
        },
        
        // 檢查API是否可用
        isAvailable: function(endpoint) {
            return !(this.errors[endpoint] && this.errors[endpoint].disabled);
        },
        
        // 重置特定端點
        resetEndpoint: function(endpoint) {
            if (this.errors[endpoint]) {
                this.errors[endpoint].count = 0;
                this.errors[endpoint].disabled = false;
                console.log(`已重置API端點 ${endpoint}`);
            }
        }
    };
}

// 自動佈署調整
function initResponsiveAdjustments() {
    // 調整小型設備上的標題和按鈕
    if (window.innerWidth < 768) {
        const pageHeaders = document.querySelectorAll('h1, h2.display-4');
        pageHeaders.forEach(header => {
            header.classList.add('fs-3');
        });
        
        const actionButtons = document.querySelectorAll('.btn-lg');
        actionButtons.forEach(btn => {
            btn.classList.remove('btn-lg');
            btn.classList.add('btn-md');
        });
    }
}

// 初始化圖片錯誤處理
function initImageErrorHandling() {
    // 設置所有圖片的錯誤處理
    document.querySelectorAll('img').forEach(img => {
        img.addEventListener('error', function() {
            if (!this.src.includes('news-placeholder.jpg')) {
                this.src = '/static/images/news-placeholder.jpg';
            }
        });
    });
}

// 初始化全局AJAX錯誤處理
function initAjaxErrorHandling() {
    // 攔截所有AJAX請求
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {
        // 檢查是否為API請求
        const isApiRequest = url.toString().includes('/api/');
        
        // 檢查此API端點是否已被禁用
        if (isApiRequest && window.apiErrorTracker) {
            const endpoint = url.toString().split('?')[0]; // 忽略查詢參數
            
            if (window.apiErrorTracker.isAvailable && !window.apiErrorTracker.isAvailable(endpoint)) {
                console.log(`API請求被阻止: ${endpoint} (因多次失敗)`);
                return Promise.reject(new Error(`API端點 ${endpoint} 已被禁用，因為多次請求失敗`));
            }
        }
        
        // 添加超時處理
        if (options && !options.signal) {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => {
                console.log('請求超時，正在中止...');
                controller.abort();
            }, 15000); // 增加到15秒超時，適應更長的API請求
            
            options.signal = controller.signal;
            
            // 執行請求並清除超時
            return originalFetch.call(this, url, options)
                .then(response => {
                    clearTimeout(timeoutId);
                    
                    if (!response.ok) {
                        // 記錄API錯誤
                        if (isApiRequest && window.apiErrorTracker && window.apiErrorTracker.logError) {
                            const endpoint = url.toString().split('?')[0];
                            window.apiErrorTracker.logError(endpoint, response.status, response.statusText);
                        }
                        
                        // 只顯示非404的API錯誤通知，避免干擾用戶
                        if (!isApiRequest || (response.status !== 404)) {
                            // 顯示友好的錯誤訊息
                            showErrorNotification(`請求失敗 (${response.status}: ${response.statusText})`);
                        }
                        console.error('AJAX請求失敗:', response.statusText);
                    }
                    return response;
                })
                .catch(error => {
                    clearTimeout(timeoutId);
                    
                    // 如果是API請求，記錄錯誤
                    if (isApiRequest && window.apiErrorTracker && window.apiErrorTracker.logError) {
                        const endpoint = url.toString().split('?')[0];
                        window.apiErrorTracker.logError(endpoint, 0, error.message);
                    }
                    
                    // 如果是終止錯誤，提示超時
                    if (error.name === 'AbortError') {
                        console.warn('AJAX請求超時 (15秒)');
                        if (!isApiRequest) {
                            showErrorNotification('請求超時，請稍後再試');
                        }
                    } else {
                        if (!isApiRequest) {
                            showErrorNotification('網絡請求失敗，請檢查網絡連接');
                        }
                        console.error('AJAX請求錯誤:', error);
                    }
                    throw error;
                });
        }
        
        return originalFetch.apply(this, arguments)
            .then(response => {
                if (!response.ok) {
                    // 記錄API錯誤
                    if (isApiRequest && window.apiErrorTracker && window.apiErrorTracker.logError) {
                        const endpoint = url.toString().split('?')[0];
                        window.apiErrorTracker.logError(endpoint, response.status, response.statusText);
                    }
                    
                    // 只顯示非404的API錯誤通知，避免干擾用戶
                    if (!isApiRequest || (response.status !== 404)) {
                        // 顯示友好的錯誤訊息
                        showErrorNotification(`請求失敗 (${response.status}: ${response.statusText})`);
                    }
                    console.error('AJAX請求失敗:', response.statusText);
                }
                return response;
            })
            .catch(error => {
                // 如果是API請求，記錄錯誤
                if (isApiRequest && window.apiErrorTracker && window.apiErrorTracker.logError) {
                    const endpoint = url.toString().split('?')[0];
                    window.apiErrorTracker.logError(endpoint, 0, error.message);
                }
                
                if (!isApiRequest) {
                    showErrorNotification('網絡請求失敗，請檢查網絡連接');
                }
                console.error('AJAX請求錯誤:', error);
                throw error;
            });
    };
}

// 突出顯示當前導航項目
function highlightCurrentNavItem() {
    const currentPath = window.location.pathname;
    
    // 簡單地匹配路徑的第一部分
    const mainPath = currentPath.split('/')[1];
    
    // 找到匹配的導航項並加亮
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        const href = link.getAttribute('href');
        if (!href) return;
        
        // 檢查是否匹配當前路徑
        if ((href === '/' && currentPath === '/') || 
            (href !== '/' && href.split('/')[1] === mainPath)) {
            link.classList.add('active');
            
            // 添加視覺指示器
            const indicator = document.createElement('span');
            indicator.className = 'nav-indicator';
            indicator.style.position = 'absolute';
            indicator.style.bottom = '0';
            indicator.style.left = '50%';
            indicator.style.width = '30px';
            indicator.style.height = '3px';
            indicator.style.backgroundColor = '#3498db';
            indicator.style.transform = 'translateX(-50%)';
            link.style.position = 'relative';
            link.appendChild(indicator);
        }
    });
}

// 顯示錯誤通知
function showErrorNotification(message) {
    // 檢查是否已經存在通知容器
    let notificationContainer = document.querySelector('.notification-container');
    
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.className = 'notification-container';
        notificationContainer.style.position = 'fixed';
        notificationContainer.style.top = '20px';
        notificationContainer.style.right = '20px';
        notificationContainer.style.zIndex = '9999';
        document.body.appendChild(notificationContainer);
    }
    
    // 創建新的通知
    const notification = document.createElement('div');
    notification.className = 'notification error-notification';
    notification.style.backgroundColor = '#f44336';
    notification.style.color = 'white';
    notification.style.padding = '15px';
    notification.style.marginBottom = '10px';
    notification.style.borderRadius = '5px';
    notification.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
    notification.style.display = 'flex';
    notification.style.justifyContent = 'space-between';
    notification.style.alignItems = 'center';
    notification.style.minWidth = '250px';
    notification.style.maxWidth = '450px';
    notification.style.animation = 'fadeIn 0.5s';
    
    notification.innerHTML = `
        <div style="margin-right: 15px;">
            <i class="fas fa-exclamation-circle" style="margin-right: 10px;"></i>
            ${message}
        </div>
        <button type="button" class="btn-close" style="color: white; opacity: 0.8; cursor: pointer;"></button>
    `;
    
    // 添加到容器
    notificationContainer.appendChild(notification);
    
    // 添加關閉按鈕事件
    notification.querySelector('.btn-close').addEventListener('click', function() {
        notification.remove();
    });
    
    // 5秒後自動消失
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.5s';
        setTimeout(() => {
            notification.remove();
        }, 500);
    }, 5000);
}

// 全局工具函數 - 安全獲取URL參數
window.getUrlParameter = function(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
};

// 添加CSS動畫
(function() {
    // 使用IIFE避免styleElement命名衝突
    const animStyleElement = document.createElement('style');
    animStyleElement.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes fadeOut {
            from { opacity: 1; transform: translateY(0); }
            to { opacity: 0; transform: translateY(-20px); }
        }
    `;
    document.head.appendChild(animStyleElement);
})();
