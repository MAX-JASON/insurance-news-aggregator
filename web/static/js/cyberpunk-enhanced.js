// 增強版賽博朋克業務系統 JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Enhanced Cyberpunk Business System Loaded');
    
    // 初始化所有功能
    initializeSystem();
});

function initializeSystem() {
    // 初始化通用按鈕功能
    initializeButtons();
    
    // 初始化表單功能
    initializeForms();
    
    // 初始化交互效果
    initializeInteractions();
    
    // 初始化通知系統
    initializeNotifications();
    
    // 添加賽博朋克效果
    addCyberpunkEffects();
}

// 按鈕功能初始化
function initializeButtons() {
    // 處理所有按鈕點擊
    document.addEventListener('click', function(e) {
        const target = e.target.closest('button, .btn');
        if (!target) return;
        
        // 添加點擊效果
        addClickEffect(target);
        
        // 處理特定按鈕類型
        if (target.classList.contains('refresh-btn')) {
            handleRefresh(target);
        } else if (target.classList.contains('export-btn')) {
            handleExport(target);
        } else if (target.classList.contains('search-btn')) {
            handleSearch(target);
        } else if (target.classList.contains('filter-btn')) {
            handleFilter(target);
        } else if (target.classList.contains('save-btn')) {
            handleSave(target);
        } else if (target.classList.contains('cancel-btn')) {
            handleCancel(target);
        } else if (target.classList.contains('share-btn')) {
            handleShare(target);
        } else if (target.classList.contains('favorite-btn')) {
            handleFavorite(target);
        } else if (target.classList.contains('view-btn')) {
            handleView(target);
        } else if (target.classList.contains('edit-btn')) {
            handleEdit(target);
        } else if (target.classList.contains('delete-btn')) {
            handleDelete(target);
        }
    });
}

// 添加點擊效果
function addClickEffect(element) {
    element.style.transform = 'scale(0.95)';
    setTimeout(() => {
        element.style.transform = '';
    }, 150);
}

// 刷新功能
function handleRefresh(btn) {
    const container = btn.closest('.card, .container, .content');
    showLoading(container);
    
    setTimeout(() => {
        hideLoading(container);
        showNotification('數據已刷新', 'success');
    }, 2000);
}

// 導出功能
function handleExport(btn) {
    const format = btn.getAttribute('data-format') || 'xlsx';
    showNotification(`正在準備 ${format.toUpperCase()} 導出...`, 'info');
    
    setTimeout(() => {
        const filename = `export_${new Date().toISOString().split('T')[0]}.${format}`;
        showNotification(`已導出: ${filename}`, 'success');
    }, 1500);
}

// 搜索功能
function handleSearch(btn) {
    const searchInput = document.querySelector('input[type="search"], .search-input');
    if (searchInput) {
        const query = searchInput.value.trim();
        if (query) {
            showNotification(`搜索: "${query}"`, 'info');
            // 這裡可以添加實際的搜索邏輯
        } else {
            showNotification('請輸入搜索關鍵字', 'warning');
        }
    }
}

// 過濾功能
function handleFilter(btn) {
    const filterValue = btn.getAttribute('data-filter');
    const items = document.querySelectorAll('.filterable-item, .news-item, .client-item');
    
    items.forEach(item => {
        const category = item.getAttribute('data-category');
        if (!filterValue || filterValue === 'all' || category === filterValue) {
            item.style.display = 'block';
            item.style.animation = 'fadeInUp 0.3s ease';
        } else {
            item.style.display = 'none';
        }
    });
    
    // 更新按鈕狀態
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    
    showNotification(`已應用過濾器: ${filterValue || '全部'}`, 'info');
}

// 保存功能
function handleSave(btn) {
    const form = btn.closest('form');
    if (form) {
        const formData = new FormData(form);
        showNotification('正在保存...', 'info');
        
        setTimeout(() => {
            showNotification('保存成功', 'success');
        }, 1000);
    }
}

// 取消功能
function handleCancel(btn) {
    const form = btn.closest('form');
    if (form) {
        form.reset();
        showNotification('已取消操作', 'info');
    }
}

// 分享功能
function handleShare(btn) {
    const itemId = btn.getAttribute('data-id');
    const itemTitle = btn.getAttribute('data-title') || '新聞項目';
    
    const shareModal = createShareModal(itemId, itemTitle);
    document.body.appendChild(shareModal);
}

// 收藏功能
function handleFavorite(btn) {
    const isActive = btn.classList.contains('active');
    
    if (isActive) {
        btn.classList.remove('active');
        btn.innerHTML = '<i class="fas fa-bookmark"></i>';
        showNotification('已取消收藏', 'info');
    } else {
        btn.classList.add('active');
        btn.innerHTML = '<i class="fas fa-bookmark text-warning"></i>';
        showNotification('已添加收藏', 'success');
    }
}

// 查看功能
function handleView(btn) {
    const itemId = btn.getAttribute('data-id');
    showNotification(`正在查看項目 ${itemId}`, 'info');
}

// 編輯功能
function handleEdit(btn) {
    const itemId = btn.getAttribute('data-id');
    showNotification(`正在編輯項目 ${itemId}`, 'info');
}

// 刪除功能
function handleDelete(btn) {
    const itemId = btn.getAttribute('data-id');
    if (confirm('確定要刪除此項目嗎？')) {
        showNotification(`已刪除項目 ${itemId}`, 'success');
        const item = btn.closest('.item, .card, .row');
        if (item) {
            item.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => item.remove(), 300);
        }
    }
}

// 創建分享模態框
function createShareModal(itemId, itemTitle) {
    const modal = document.createElement('div');
    modal.className = 'cyber-modal';
    modal.innerHTML = `
        <div class="cyber-modal-content">
            <div class="cyber-modal-header">
                <h4 class="neon-text">分享項目</h4>
                <button class="cyber-close-btn">&times;</button>
            </div>
            <div class="cyber-modal-body">
                <h5>${itemTitle}</h5>
                <div class="share-options">
                    <button class="btn-cyber-primary" onclick="shareToEmail('${itemId}')">
                        <i class="fas fa-envelope"></i> 電子郵件
                    </button>
                    <button class="btn-cyber-primary" onclick="shareToLine('${itemId}')">
                        <i class="fab fa-line"></i> LINE
                    </button>
                    <button class="btn-cyber-primary" onclick="copyShareLink('${itemId}')">
                        <i class="fas fa-link"></i> 複製連結
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // 綁定關閉事件
    modal.querySelector('.cyber-close-btn').onclick = () => modal.remove();
    modal.onclick = (e) => {
        if (e.target === modal) modal.remove();
    };
    
    return modal;
}

// 表單功能初始化
function initializeForms() {
    // 實時驗證
    document.addEventListener('input', function(e) {
        if (e.target.matches('input, textarea, select')) {
            validateField(e.target);
        }
    });
    
    // 表單提交
    document.addEventListener('submit', function(e) {
        const form = e.target;
        if (form.matches('form')) {
            e.preventDefault();
            handleFormSubmit(form);
        }
    });
}

// 字段驗證
function validateField(field) {
    const value = field.value.trim();
    
    if (field.hasAttribute('required') && !value) {
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');
    } else {
        field.classList.add('is-valid');
        field.classList.remove('is-invalid');
    }
}

// 表單提交處理
function handleFormSubmit(form) {
    const formData = new FormData(form);
    showNotification('正在提交表單...', 'info');
    
    setTimeout(() => {
        showNotification('表單提交成功', 'success');
        form.reset();
    }, 1500);
}

// 交互效果初始化
function initializeInteractions() {
    // 懸停效果
    document.addEventListener('mouseenter', function(e) {
        if (e.target.matches('.card, .btn, .news-item')) {
            e.target.style.transform = 'translateY(-2px)';
        }
    }, true);
    
    document.addEventListener('mouseleave', function(e) {
        if (e.target.matches('.card, .btn, .news-item')) {
            e.target.style.transform = '';
        }
    }, true);
}

// 通知系統初始化
function initializeNotifications() {
    if (!document.querySelector('.notification-container')) {
        const container = document.createElement('div');
        container.className = 'notification-container';
        document.body.appendChild(container);
    }
}

// 顯示通知
function showNotification(message, type = 'info') {
    const container = document.querySelector('.notification-container');
    const notification = document.createElement('div');
    notification.className = `cyber-notification ${type}`;
    
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    notification.innerHTML = `
        <i class="${icons[type]}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(notification);
    
    // 動畫效果
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // 自動移除
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// 載入效果
function showLoading(container) {
    if (!container) return;
    
    const loader = document.createElement('div');
    loader.className = 'cyber-loader';
    loader.innerHTML = '<div class="cyber-spinner"></div>';
    container.appendChild(loader);
    container.classList.add('loading');
}

function hideLoading(container) {
    if (!container) return;
    
    const loader = container.querySelector('.cyber-loader');
    if (loader) loader.remove();
    container.classList.remove('loading');
}

// 賽博朋克效果
function addCyberpunkEffects() {
    // 掃描線效果
    if (!document.querySelector('.scanlines')) {
        const scanlines = document.createElement('div');
        scanlines.className = 'scanlines';
        document.body.appendChild(scanlines);
    }
    
    // 隨機閃爍效果
    setInterval(() => {
        const elements = document.querySelectorAll('.neon-text, .cyber-glow');
        elements.forEach(el => {
            if (Math.random() < 0.05) {
                el.style.animation = 'flicker 0.2s ease-in-out';
                setTimeout(() => {
                    el.style.animation = '';
                }, 200);
            }
        });
    }, 3000);
}

// 分享功能 - 全局函數
window.shareToEmail = function(itemId) {
    showNotification('正在打開電子郵件客戶端...', 'info');
    setTimeout(() => {
        showNotification('已打開電子郵件客戶端', 'success');
    }, 1000);
};

window.shareToLine = function(itemId) {
    showNotification('正在分享到 LINE...', 'info');
    setTimeout(() => {
        showNotification('已分享到 LINE', 'success');
    }, 1000);
};

window.copyShareLink = function(itemId) {
    const link = `${window.location.origin}/item/${itemId}`;
    navigator.clipboard.writeText(link).then(() => {
        showNotification('連結已複製到剪貼板', 'success');
    }).catch(() => {
        showNotification('複製失敗，請手動複製', 'error');
    });
};

// 工具函數
window.cyberpunkUtils = {
    showNotification,
    showLoading,
    hideLoading,
    addClickEffect
};
