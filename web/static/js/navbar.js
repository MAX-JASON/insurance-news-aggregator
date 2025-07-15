/**
 * 導航欄與全局功能腳本 - 保險新聞聚合平台
 * Navbar and Global Functions - Insurance News Aggregator
 */

$(document).ready(function() {
    // 初始化通知提示元素
    initializeTooltips();
    
    // 初始化主題設置
    initializeTheme();
    
    // 初始化通知系統
    initializeNotifications();
    
    // 檢查系統狀態
    checkSystemStatus();
});

/**
 * 初始化通知提示元素
 */
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * 初始化主題設置
 */
function initializeTheme() {
    try {
        // 讀取已保存的主題設置
        const savedSettings = localStorage.getItem('userSettings');
        if (savedSettings) {
            const settings = JSON.parse(savedSettings);
            applyTheme(settings.theme || 'light');
            applyFontSize(settings.fontSize || 16);
            
            if (settings.compactView) {
                document.body.classList.add('compact-view');
            }
            
            console.log('主題已從本地存儲載入並應用', settings.theme);
        }
        
        // 主題切換器事件綁定
        $('.theme-switcher').on('click', function(e) {
            e.preventDefault();
            const theme = $(this).data('theme');
            if (theme) {
                applyTheme(theme);
                updateSavedTheme(theme);
            }
        });
    } catch (error) {
        console.error('初始化主題設置時出錯:', error);
    }
}

/**
 * 應用主題
 */
function applyTheme(theme) {
    // 移除所有現有主題類
    document.body.classList.remove('theme-light', 'theme-dark', 'theme-blue', 'theme-professional');
    
    // 添加新主題類
    document.body.classList.add('theme-' + theme);
    
    console.log('已套用主題:', theme);
}

/**
 * 更新保存的主題設置
 */
function updateSavedTheme(theme) {
    try {
        let settings = { theme: theme };
        
        // 如果已有設置，則只更新主題
        const savedSettings = localStorage.getItem('userSettings');
        if (savedSettings) {
            settings = JSON.parse(savedSettings);
            settings.theme = theme;
        }
        
        // 保存設置
        localStorage.setItem('userSettings', JSON.stringify(settings));
        console.log('已更新已保存的主題設置:', theme);
    } catch (error) {
        console.error('更新主題設置時出錯:', error);
    }
}

/**
 * 應用字體大小
 */
function applyFontSize(size) {
    document.documentElement.style.fontSize = size + 'px';
    console.log('已套用字體大小:', size + 'px');
}

/**
 * 初始化通知系統
 */
function initializeNotifications() {
    // 如果全局通知工具已定義，則不需要再定義
    if (window.businessTools && window.businessTools.showToast) {
        return;
    }
    
    // 否則創建基本的通知功能
    window.businessTools = window.businessTools || {};
    window.businessTools.showToast = function(message, type = 'info') {
        // 檢查是否已存在容器
        let toastContainer = document.getElementById('global-toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'global-toast-container';
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            toastContainer.style.zIndex = '1090';
            document.body.appendChild(toastContainer);
        }
        
        // 設定通知類型樣式
        let bgClass = 'bg-info';
        let icon = '<i class="fas fa-info-circle me-2"></i>';
        
        switch (type) {
            case 'success':
                bgClass = 'bg-success';
                icon = '<i class="fas fa-check-circle me-2"></i>';
                break;
            case 'warning':
                bgClass = 'bg-warning text-dark';
                icon = '<i class="fas fa-exclamation-circle me-2"></i>';
                break;
            case 'error':
                bgClass = 'bg-danger';
                icon = '<i class="fas fa-times-circle me-2"></i>';
                break;
        }
        
        // 創建唯一ID
        const toastId = 'toast-' + Date.now();
        
        // 創建通知元素
        const toast = `
            <div class="toast" id="${toastId}" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header ${bgClass} text-white">
                    ${icon} <strong class="me-auto">系統通知</strong>
                    <small>${new Date().toLocaleTimeString()}</small>
                    <button type="button" class="btn-close btn-close-white ms-2" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;
        
        // 添加通知到容器
        toastContainer.insertAdjacentHTML('beforeend', toast);
        
        // 顯示通知
        const toastElement = document.getElementById(toastId);
        const bsToast = new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: 5000
        });
        
        bsToast.show();
        
        // 自動移除
        toastElement.addEventListener('hidden.bs.toast', function() {
            toastElement.remove();
        });
    };
    
    console.log('通知系統已初始化');
}

/**
 * 檢查系統狀態
 */
function checkSystemStatus() {
    // 檢查是否需要顯示系統狀態
    if (!document.body.classList.contains('show-system-status')) {
        return;
    }
    
    try {
        // 這裡可以添加對API的調用來獲取系統狀態
        fetch('/api/v1/system/status')
            .then(response => {
                if (!response.ok) {
                    throw new Error('系統狀態檢查失敗');
                }
                return response.json();
            })
            .then(data => {
                console.log('系統狀態:', data);
                if (data.status === 'error') {
                    // 顯示系統狀態警告
                    if (window.businessTools && window.businessTools.showToast) {
                        window.businessTools.showToast('系統狀態異常，部分功能可能無法正常工作', 'warning');
                    }
                }
            })
            .catch(error => {
                console.error('檢查系統狀態時出錯:', error);
            });
    } catch (error) {
        console.error('檢查系統狀態時出錯:', error);
    }
}
