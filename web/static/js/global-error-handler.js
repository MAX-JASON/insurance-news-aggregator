/**
 * 全局錯誤處理和UI輔助函數
 * Global Error Handling and UI Helper Functions
 */

// 創建全局通知顯示系統
window.businessTools = window.businessTools || {};

// 通知顯示系統
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

// 全局錯誤處理
window.addEventListener('error', function(event) {
    console.error('全局錯誤:', event.error);
    
    // 如果錯誤與UI相關，顯示通知
    if (event.filename && event.filename.includes('static/js')) {
        window.businessTools.showToast('系統遇到錯誤，部分功能可能無法正常運作', 'error');
    }
});

// 捕獲未處理的Promise錯誤
window.addEventListener('unhandledrejection', function(event) {
    console.error('未處理的Promise錯誤:', event.reason);
    
    // 不顯示通知以避免過多干擾
});

// UI輔助函數
window.businessTools.openModal = function(modalId) {
    const modalElement = document.getElementById(modalId);
    if (modalElement) {
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
    } else {
        console.error(`找不到ID為${modalId}的Modal元素`);
    }
};

window.businessTools.closeModal = function(modalId) {
    const modalElement = document.getElementById(modalId);
    if (modalElement) {
        const modal = bootstrap.Modal.getInstance(modalElement);
        if (modal) {
            modal.hide();
        }
    }
};

// DOM載入完成後初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('全局錯誤處理和UI輔助函數已載入');
    
    // 確保所有模態框在關閉後從DOM中移除
    document.body.addEventListener('hidden.bs.modal', function (event) {
        if (event.target.classList.contains('modal') && event.target.id.startsWith('dynamic-')) {
            event.target.remove();
        }
    });
});
