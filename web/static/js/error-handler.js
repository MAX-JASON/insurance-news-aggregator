/**
 * 錯誤處理與頁面修復模組
 * 處理錯誤情況與網頁修復功能
 */

// 全局API可用性跟踪
window.apiEndpointsAvailable = true;

document.addEventListener('DOMContentLoaded', function() {
    // 初始化網路狀態監控
    initNetworkMonitor();
    
    // 初始化錯誤捕獲
    initErrorCapture();
    
    // 初始化自動重試功能
    initAutoRetry();
    
    // 檢查API可用性
    checkApiAvailability();
    
    console.log('錯誤處理與頁面修復模組已載入');
});

// 網路狀態監控
function initNetworkMonitor() {
    // 監聽網路狀態變化
    window.addEventListener('online', function() {
        showNotification('網絡已恢復連接', 'success');
        // 嘗試重新加載失敗的資源
        retryFailedResources();
    });
    
    window.addEventListener('offline', function() {
        showNotification('網絡連接已斷開', 'warning');
        // 啟用離線模式
        enableOfflineMode();
    });
}

// 錯誤捕獲
function initErrorCapture() {
    // 全局錯誤捕獲
    window.addEventListener('error', function(event) {
        // 忽略第三方腳本錯誤和 Script error
        if ((event.filename && !event.filename.includes(window.location.host)) || 
            event.message === 'Script error.' || 
            !event.message) {
            return;
        }
        
        console.error('捕獲到頁面錯誤:', event.message);
        
        // 記錄錯誤 (只記錄有效的錯誤信息)
        if (event.message && event.message !== 'undefined') {
            logError({
                message: event.message,
                source: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                error: event.error
            });
        }
        
        // 如果是資源加載錯誤，嘗試恢復
        if (event.target && (event.target.tagName === 'IMG' || event.target.tagName === 'SCRIPT')) {
            handleResourceError(event.target);
        }
    }, true);
    
    // Promise 錯誤捕獲
    window.addEventListener('unhandledrejection', function(event) {
        console.error('未處理的Promise拒絕:', event.reason);
        
        logError({
            message: '未處理的Promise錯誤',
            error: event.reason
        });
    });
}

// 自動重試功能
function initAutoRetry() {
    // 重試隊列
    window.retryQueue = [];
    
    // 定時檢查重試隊列
    setInterval(function() {
        if (navigator.onLine && window.retryQueue.length > 0) {
            const nextRetry = window.retryQueue.shift();
            if (nextRetry && typeof nextRetry === 'function') {
                try {
                    nextRetry();
                } catch (err) {
                    console.error('重試操作失敗:', err);
                }
            }
        }
    }, 5000);
}

// 處理資源錯誤
function handleResourceError(element) {
    if (element.tagName === 'IMG') {
        // 處理圖片加載錯誤
        handleImageError(element);
    } else if (element.tagName === 'SCRIPT') {
        // 處理腳本加載錯誤
        handleScriptError(element);
    }
}

// 處理圖片加載錯誤
function handleImageError(imgElement) {
    // 設置默認替代圖片 (確保路徑正確)
    if (!imgElement.src.includes('news-placeholder.jpg')) {
        console.log('嘗試恢復圖片:', imgElement.src);
        
        // 保存原始圖片URL
        const originalSrc = imgElement.src;
        
        // 設置圖片懶加載屬性
        imgElement.setAttribute('data-original-src', originalSrc);
        
        // 設置替代圖片 (確保路徑正確)
        let placeholderPath = '/static/images/news-placeholder.jpg';
        
        // 嘗試不同的路徑格式
        const testImg = new Image();
        testImg.onerror = function() {
            // 如果直接路徑失敗，嘗試相對路徑
            placeholderPath = 'static/images/news-placeholder.jpg';
            
            // 設置內聯占位圖 (base64)，作為最後的後備方案
            if (placeholderPath === 'static/images/news-placeholder.jpg') {
                const inlinePlaceholder = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMDAiIGhlaWdodD0iMTUwIiB2aWV3Qm94PSIwIDAgMjAwIDE1MCIgZmlsbD0iI2RkZCI+PHJlY3Qgd2lkdGg9IjIwMCIgaGVpZ2h0PSIxNTAiIGZpbGw9IiNlZWUiLz48dGV4dCB4PSI1MCUiIHk9IjUwJSIgZm9udC1mYW1pbHk9IkFyaWFsLCBzYW5zLXNlcmlmIiBmb250LXNpemU9IjE0IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjYWFhIiBkeT0iLjNlbSI+圖片無法顯示</dGV4dD48L3N2Zz4=';
                imgElement.src = inlinePlaceholder;
                return;
            }
            
            imgElement.src = placeholderPath;
        };
        
        // 先嘗試原始路徑
        testImg.src = placeholderPath;
        imgElement.src = placeholderPath;
        
        // 添加重試邏輯
        imgElement.addEventListener('click', function() {
            // 點擊時嘗試重新加載原圖片
            this.src = this.getAttribute('data-original-src');
        });
        
        // 添加工具提示
        imgElement.title = '圖片加載失敗，點擊重試';
        
        // 添加到重試隊列
        window.retryQueue.push(function() {
            if (imgElement && document.body.contains(imgElement)) {
                const tempImg = new Image();
                tempImg.onload = function() {
                    imgElement.src = originalSrc;
                };
                tempImg.src = originalSrc;
            }
        });
    }
}

// 處理腳本加載錯誤
function handleScriptError(scriptElement) {
    const scriptSrc = scriptElement.src;
    console.log('腳本加載失敗:', scriptSrc);
    
    // 僅處理我們自己的腳本
    if (scriptSrc && scriptSrc.includes(window.location.host)) {
        // 添加到重試隊列
        window.retryQueue.push(function() {
            // 創建新的腳本元素
            const newScript = document.createElement('script');
            newScript.src = scriptSrc + '?retry=' + new Date().getTime(); // 添加時間戳防止緩存
            document.head.appendChild(newScript);
        });
    }
}

// 重試失敗的資源
function retryFailedResources() {
    // 重試失敗的圖片
    document.querySelectorAll('img[data-original-src]').forEach(function(img) {
        const originalSrc = img.getAttribute('data-original-src');
        if (originalSrc) {
            const tempImg = new Image();
            tempImg.onload = function() {
                img.src = originalSrc;
                img.removeAttribute('data-original-src');
                img.removeAttribute('title');
            };
            tempImg.src = originalSrc;
        }
    });
}

// 啟用離線模式
function enableOfflineMode() {
    // 顯示離線通知
    const offlineAlert = document.createElement('div');
    offlineAlert.className = 'alert alert-warning alert-dismissible fade show';
    offlineAlert.setAttribute('role', 'alert');
    offlineAlert.id = 'offline-alert';
    offlineAlert.innerHTML = `
        <i class="fas fa-wifi-slash me-2"></i>您目前處於離線狀態，部分功能可能無法正常運行。
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // 檢查是否已經顯示了離線通知
    if (!document.getElementById('offline-alert')) {
        // 添加到頁面頂部
        document.body.insertBefore(offlineAlert, document.body.firstChild);
        
        // 創建Bootstrap警告對象
        const bsAlert = new bootstrap.Alert(offlineAlert);
    }
    
    // 禁用需要網絡連接的功能
    disableNetworkFeatures();
}

// 禁用需要網絡連接的功能
function disableNetworkFeatures() {
    // 禁用表單提交
    document.querySelectorAll('form').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!navigator.onLine) {
                e.preventDefault();
                showNotification('您處於離線狀態，無法提交表單', 'warning');
            }
        });
    });
    
    // 禁用AJAX相關按鈕
    document.querySelectorAll('[data-requires-network="true"]').forEach(function(el) {
        el.disabled = true;
        el.title = '離線模式下不可用';
    });
}

// 顯示通知
function showNotification(message, type = 'info') {
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
    
    // 顏色映射
    const colorMap = {
        'success': '#28a745',
        'info': '#17a2b8',
        'warning': '#ffc107',
        'danger': '#dc3545'
    };
    
    // 圖標映射
    const iconMap = {
        'success': 'fas fa-check-circle',
        'info': 'fas fa-info-circle',
        'warning': 'fas fa-exclamation-triangle',
        'danger': 'fas fa-exclamation-circle'
    };
    
    // 創建新的通知
    const notification = document.createElement('div');
    notification.className = `notification ${type}-notification`;
    notification.style.backgroundColor = colorMap[type] || colorMap.info;
    notification.style.color = type === 'warning' ? '#212529' : 'white';
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
            <i class="${iconMap[type] || iconMap.info}" style="margin-right: 10px;"></i>
            ${message}
        </div>
        <button type="button" class="btn-close" style="color: ${type === 'warning' ? '#212529' : 'white'}; opacity: 0.8; cursor: pointer;"></button>
    `;
    
    // 添加到容器
    notificationContainer.appendChild(notification);
    
    // 添加關閉按鈕事件
    notification.querySelector('.btn-close').addEventListener('click', function() {
        notification.style.animation = 'fadeOut 0.5s';
        setTimeout(() => {
            notification.remove();
        }, 500);
    });
    
    // 5秒後自動消失
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.5s';
        setTimeout(() => {
            notification.remove();
        }, 500);
    }, 5000);
}

// 記錄錯誤
function logError(errorData) {
    // 如果錯誤數據不完整，則不記錄
    if (!errorData || !errorData.message) {
        return;
    }
    
    // 保存到本地存儲，以便在用戶報告問題時提供
    try {
        const errors = JSON.parse(localStorage.getItem('pageErrors') || '[]');
        errors.push({
            ...errorData,
            timestamp: new Date().toISOString(),
            url: window.location.href
        });
        
        // 只保留最近的10個錯誤
        if (errors.length > 10) {
            errors.shift();
        }
        
        localStorage.setItem('pageErrors', JSON.stringify(errors));
    } catch (e) {
        console.error('無法保存錯誤日誌:', e);
    }
    
    // 檢查API是否可用 (通過檢查局部變數)
    const apiAvailable = window.apiEndpointsAvailable || false;
    
    // 只有在API可用時才發送錯誤報告
    if (navigator.onLine && apiAvailable) {
        try {
            fetch('/api/v1/log-error', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ...errorData,
                    url: window.location.href,
                    userAgent: navigator.userAgent
                })
            })
            .then(response => {
                if (!response.ok) {
                    // API不可用，標記為不可用
                    window.apiEndpointsAvailable = false;
                    console.log('錯誤日誌API不可用，已禁用遠程錯誤記錄');
                }
            })
            .catch(e => {
                window.apiEndpointsAvailable = false;
                console.log('錯誤日誌上傳失敗:', e);
            });
        } catch (e) {
            console.log('無法發送錯誤日誌:', e);
        }
    } else if (navigator.onLine && !apiAvailable) {
        // 系統在線但API不可用，不重試
        console.log('錯誤日誌API已標記為不可用，跳過上傳');
    } else {
        // 離線狀態，將錯誤日誌添加到重試隊列
        window.retryQueue.push(function() {
            logError(errorData);
        });
    }
}

// 顯示錯誤對話框
function showErrorDialog(title, message, retryCallback) {
    // 創建模態對話框
    const modalId = 'errorModal' + Date.now();
    const modalDiv = document.createElement('div');
    modalDiv.className = 'modal fade';
    modalDiv.id = modalId;
    modalDiv.setAttribute('tabindex', '-1');
    modalDiv.setAttribute('aria-labelledby', `${modalId}Label`);
    modalDiv.setAttribute('aria-hidden', 'true');
    
    modalDiv.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header bg-danger text-white">
                    <h5 class="modal-title" id="${modalId}Label">
                        <i class="fas fa-exclamation-triangle me-2"></i>${title || '發生錯誤'}
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <p>${message || '處理請求時發生錯誤，請稍後再試。'}</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">關閉</button>
                    ${retryCallback ? '<button type="button" class="btn btn-primary retry-btn">重試</button>' : ''}
                </div>
            </div>
        </div>
    `;
    
    // 添加到文檔
    document.body.appendChild(modalDiv);
    
    // 初始化模態對話框
    const modal = new bootstrap.Modal(modalDiv);
    modal.show();
    
    // 監聽模態對話框關閉事件
    modalDiv.addEventListener('hidden.bs.modal', function () {
        document.body.removeChild(modalDiv);
    });
    
    // 綁定重試按鈕點擊事件
    if (retryCallback) {
        modalDiv.querySelector('.retry-btn').addEventListener('click', function() {
            modal.hide();
            if (typeof retryCallback === 'function') {
                retryCallback();
            }
        });
    }
    
    return modal;
}

// 檢查API可用性
function checkApiAvailability() {
    // 使用健康檢查API來確認API可用性
    fetch('/api/v1/health', { 
        method: 'GET',
        headers: { 'Accept': 'application/json' },
        // 設置較短的超時時間
        signal: AbortSignal.timeout(2000)
    })
    .then(response => {
        if (response.ok) {
            window.apiEndpointsAvailable = true;
            console.log('API端點可用');
        } else {
            window.apiEndpointsAvailable = false;
            console.log('API端點返回錯誤狀態，標記為不可用');
        }
    })
    .catch(err => {
        // API不可用
        window.apiEndpointsAvailable = false;
        console.log('API端點不可用，禁用相關功能:', err.message);
        
        // 如果是404錯誤，可能是API尚未實現或路徑有誤
        if (err.message && err.message.includes('404')) {
            console.log('API端點未找到 (404)，可能是開發環境或API尚未實現');
        }
    });
}

// 修復Bootstrap Modal問題
function fixBootstrapModalIssues() {
    // 檢查是否存在bootstrap全局對象
    if (typeof bootstrap === 'undefined' || !bootstrap.Modal) {
        console.warn('Bootstrap Modal未正確載入，嘗試修復...');
        
        // 創建一個簡單的模態對話框替代方案
        window.SimpleModal = function(modalElement) {
            this.element = modalElement;
            
            this.show = function() {
                this.element.style.display = 'block';
                document.body.classList.add('modal-open');
                
                // 創建背景遮罩
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);
                
                this.element.classList.add('show');
                this.element.style.display = 'block';
                this.element.setAttribute('aria-modal', 'true');
                this.element.setAttribute('role', 'dialog');
            };
            
            this.hide = function() {
                this.element.classList.remove('show');
                this.element.style.display = 'none';
                this.element.setAttribute('aria-hidden', 'true');
                this.element.removeAttribute('aria-modal');
                
                // 移除背景遮罩
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) {
                    document.body.removeChild(backdrop);
                }
                
                document.body.classList.remove('modal-open');
            };
        };
        
        // 替換bootstrap.Modal
        if (typeof bootstrap === 'undefined') {
            window.bootstrap = {};
        }
        
        window.bootstrap.Modal = window.SimpleModal;
        console.log('已創建Bootstrap Modal替代方案');
    }
}

// 頁面載入完成後執行修復
window.addEventListener('load', function() {
    // 延遲執行，確保所有腳本都已加載
    setTimeout(function() {
        fixBootstrapModalIssues();
    }, 1000);
});

// 導出為全局函數
window.showErrorDialog = showErrorDialog;
window.showNotification = showNotification;
window.retryFailedResources = retryFailedResources;
window.checkApiAvailability = checkApiAvailability;
window.fixBootstrapModalIssues = fixBootstrapModalIssues;
