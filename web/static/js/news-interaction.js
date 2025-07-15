/**
 * 新聞互動功能模組
 * 處理新聞列表頁面的互動邏輯
 */

// 等待DOM加載完成
document.addEventListener('DOMContentLoaded', function() {
    // 初始化篩選器互動
    initFilterInteractions();
    
    // 初始化視圖模式
    initViewMode();
    
    // 初始化搜索功能
    initSearchFeature();
});

// 初始化篩選器互動
function initFilterInteractions() {
    // 為所有篩選器添加事件處理器
    const categoryFilter = document.getElementById('categoryFilter');
    const sourceFilter = document.getElementById('sourceFilter');
    const sortFilter = document.getElementById('sortFilter');
    
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            filterNews();
        });
    }
    
    if (sourceFilter) {
        sourceFilter.addEventListener('change', function() {
            filterNews();
        });
    }
    
    if (sortFilter) {
        sortFilter.addEventListener('change', function() {
            filterNews();
        });
    }
    
    // 添加一個重置篩選按鈕
    const filterSection = document.querySelector('.filter-section');
    if (filterSection) {
        const resetButton = document.createElement('div');
        resetButton.className = 'text-center mt-3';
        resetButton.innerHTML = `
            <button class="btn btn-sm btn-outline-secondary" onclick="resetFilters()">
                <i class="fas fa-times me-1"></i>重置所有篩選
            </button>
        `;
        
        filterSection.appendChild(resetButton);
    }
}

// 重置所有篩選器
function resetFilters() {
    const categoryFilter = document.getElementById('categoryFilter');
    const sourceFilter = document.getElementById('sourceFilter');
    const sortFilter = document.getElementById('sortFilter');
    const searchInput = document.getElementById('searchInput');
    
    if (categoryFilter) categoryFilter.value = '';
    if (sourceFilter) sourceFilter.value = '';
    if (sortFilter) sortFilter.value = 'date';
    if (searchInput) searchInput.value = '';
    
    // 刷新頁面，去除所有參數
    window.location.href = window.location.pathname;
}

// 初始化視圖模式
function initViewMode() {
    // 從localStorage獲取用戶偏好
    const savedViewMode = localStorage.getItem('newsViewMode');
    const newsGrid = document.getElementById('newsGrid');
    
    console.log('初始化視圖模式，偏好：', savedViewMode);
    
    if (newsGrid) {
        // 強制清除可能衝突的樣式
        newsGrid.style.cssText = '';
        
        // 套用視圖模式
        if (savedViewMode === 'list') {
            console.log('套用列表視圖');
            
            // 套用列表樣式
            newsGrid.classList.remove('news-grid');
            newsGrid.classList.add('news-list');
            newsGrid.style.display = 'block';
            
            // 強制指定列表樣式
            newsGrid.style.gridTemplateColumns = 'none';
            newsGrid.style.gap = '0';
            
            // 更新所有卡片樣式
            const newsCards = document.querySelectorAll('.news-card');
            newsCards.forEach(card => {
                card.style.width = '100%';
                card.style.marginBottom = '15px';
            });
            
            // 更新按鈕圖示
            const viewToggleBtn = document.querySelector('button[onclick="toggleViewMode()"] i');
            if (viewToggleBtn) {
                viewToggleBtn.className = 'fas fa-th-large me-1';
            }
        } else {
            console.log('套用網格視圖（預設）');
            
            // 預設是網格模式
            newsGrid.classList.add('news-grid');
            newsGrid.classList.remove('news-list');
            newsGrid.style.display = 'grid';
            
            // 強制指定網格樣式
            newsGrid.style.gridTemplateColumns = 'repeat(auto-fill, minmax(350px, 1fr))';
            newsGrid.style.gap = '1.5rem';
            
            // 確保卡片不帶列表視圖樣式
            const newsCards = document.querySelectorAll('.news-card');
            newsCards.forEach(card => {
                card.style.width = '';
                card.style.marginBottom = '';
            });
            
            // 更新按鈕圖示
            const viewToggleBtn = document.querySelector('button[onclick="toggleViewMode()"] i');
            if (viewToggleBtn) {
                viewToggleBtn.className = 'fas fa-list me-1';
            }
        }
    } else {
        console.warn('找不到新聞網格元素，無法初始化視圖模式');
    }
}

// 初始化搜索功能
function initSearchFeature() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', function(event) {
            if (event.key === 'Enter') {
                searchNews();
            }
        });
    }
}

// 篩選新聞
function filterNews() {
    const category = document.getElementById('categoryFilter')?.value || '';
    const source = document.getElementById('sourceFilter')?.value || '';
    const sort = document.getElementById('sortFilter')?.value || 'date';
    const searchTerm = document.getElementById('searchInput')?.value.trim() || '';
    
    const urlParams = new URLSearchParams(window.location.search);
    
    if (category) {
        urlParams.set('category', category);
    } else {
        urlParams.delete('category');
    }
    
    if (source) {
        urlParams.set('source', source);
    } else {
        urlParams.delete('source');
    }
    
    if (sort) {
        urlParams.set('sort', sort);
    } else {
        urlParams.delete('sort');
    }
    
    if (searchTerm) {
        urlParams.set('search', searchTerm);
    } else {
        urlParams.delete('search');
    }
    
    // 重置頁碼
    urlParams.delete('page');
    
    // 顯示加載指示器
    showLoading("套用篩選中...");
    
    // 使用 window.location.href 而不是 search 以保留基本路徑
    window.location.href = window.location.pathname + '?' + urlParams.toString();
}

// 搜索新聞
function searchNews() {
    const searchTerm = document.getElementById('searchInput')?.value.trim() || '';
    
    if (!searchTerm) {
        // 如果搜索詞為空，提示用戶
        alert('請輸入搜索關鍵詞');
        return;
    }
    
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('search', searchTerm);
    urlParams.delete('page'); // 重置頁碼
    
    // 顯示加載指示器
    showLoading("搜索中...");
    
    window.location.href = window.location.pathname + '?' + urlParams.toString();
}

// 刷新新聞列表
function refreshNews() {
    // 顯示加載指示器
    showLoading("更新新聞中...");
    
    // 保留目前的篩選條件
    const urlParams = new URLSearchParams(window.location.search);
    
    // 添加timestamp參數以確保不使用緩存
    urlParams.set('_t', new Date().getTime());
    
    // 重新載入頁面
    window.location.href = window.location.pathname + '?' + urlParams.toString();
}

// 切換視圖模式 (網格/列表)
function toggleViewMode() {
    const newsGrid = document.getElementById('newsGrid');
    
    console.log('切換視圖模式被觸發');
    
    // 確保元素存在
    if (!newsGrid) {
        console.error('找不到新聞網格元素');
        return;
    }
    
    // 檢查當前視圖模式
    if (newsGrid.classList.contains('news-grid')) {
        console.log('從網格視圖切換到列表視圖');
        
        // 切換到列表視圖 - 首先應用列表樣式
        const newsCards = document.querySelectorAll('.news-card');
        newsCards.forEach(card => {
            card.style.width = '100%';
            card.style.marginBottom = '15px';
        });
        
        // 改變容器樣式
        newsGrid.classList.remove('news-grid');
        newsGrid.classList.add('news-list');
        newsGrid.style.display = 'block';
        
        // 強制指定清晰的列表樣式
        newsGrid.style.gridTemplateColumns = 'none';
        newsGrid.style.gap = '0';
        
        // 儲存用戶偏好
        localStorage.setItem('newsViewMode', 'list');
        
        // 更新按鈕圖示
        const viewToggleBtn = document.querySelector('button[onclick="toggleViewMode()"] i');
        if (viewToggleBtn) {
            viewToggleBtn.className = 'fas fa-th-large me-1';
        }
    } else {
        console.log('從列表視圖切換到網格視圖');
        
        // 切換到網格視圖 - 恢復卡片樣式
        const newsCards = document.querySelectorAll('.news-card');
        newsCards.forEach(card => {
            card.style.width = '';
            card.style.marginBottom = '';
        });
        
        // 改變容器樣式
        newsGrid.classList.add('news-grid');
        newsGrid.classList.remove('news-list');
        newsGrid.style.display = 'grid';
        
        // 強制指定清晰的網格樣式
        newsGrid.style.gridTemplateColumns = 'repeat(auto-fill, minmax(350px, 1fr))';
        newsGrid.style.gap = '1.5rem';
        
        // 儲存用戶偏好
        localStorage.setItem('newsViewMode', 'grid');
        
        // 更新按鈕圖示
        const viewToggleBtn = document.querySelector('button[onclick="toggleViewMode()"] i');
        if (viewToggleBtn) {
            viewToggleBtn.className = 'fas fa-list me-1';
        }
    }
    
    // 為了確保視覺效果更加明顯，添加簡單的動畫效果
    const newsCards = document.querySelectorAll('.news-card');
    newsCards.forEach(card => {
        card.style.transition = 'all 0.3s ease';
    });
}

// 分享新聞
function shareNews(newsId, newsTitle) {
    if (navigator.share) {
        navigator.share({
            title: newsTitle,
            url: window.location.origin + '/news/' + newsId
        }).catch(err => {
            console.error('分享失敗:', err);
            fallbackShare(newsId);
        });
    } else {
        fallbackShare(newsId);
    }
}

// 備用分享方法
function fallbackShare(newsId) {
    const url = window.location.origin + '/news/' + newsId;
    
    try {
        navigator.clipboard.writeText(url).then(() => {
            alert('新聞連結已複製到剪貼板');
        });
    } catch (err) {
        console.error('複製到剪貼板失敗:', err);
        
        // 最後備用方案 - 提示用戶手動複製
        const tempInput = document.createElement('input');
        tempInput.value = url;
        document.body.appendChild(tempInput);
        tempInput.select();
        document.execCommand('copy');
        document.body.removeChild(tempInput);
        
        alert('新聞連結已複製到剪貼板');
    }
}

// 收藏新聞
function bookmarkNews(newsId) {
    // 嘗試從localStorage獲取已收藏的新聞
    let bookmarks = JSON.parse(localStorage.getItem('newsBookmarks')) || [];
    
    // 檢查是否已經收藏
    const index = bookmarks.indexOf(newsId);
    
    if (index === -1) {
        // 添加到收藏
        bookmarks.push(newsId);
        localStorage.setItem('newsBookmarks', JSON.stringify(bookmarks));
        alert('新聞已加入收藏');
        
        // 更新UI
        const bookmarkBtn = event.currentTarget;
        if (bookmarkBtn) {
            bookmarkBtn.innerHTML = '<i class="fas fa-bookmark"></i>';
            bookmarkBtn.classList.replace('btn-outline-success', 'btn-success');
        }
    } else {
        // 從收藏中移除
        bookmarks.splice(index, 1);
        localStorage.setItem('newsBookmarks', JSON.stringify(bookmarks));
        alert('新聞已從收藏中移除');
        
        // 更新UI
        const bookmarkBtn = event.currentTarget;
        if (bookmarkBtn) {
            bookmarkBtn.innerHTML = '<i class="far fa-bookmark"></i>';
            bookmarkBtn.classList.replace('btn-success', 'btn-outline-success');
        }
    }
    
    // API調用（如果後端有實現）
    try {
        fetch('/api/v1/bookmarks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ newsId: newsId, action: index === -1 ? 'add' : 'remove' })
        });
    } catch (err) {
        console.log('無法連接到收藏API，僅使用本地儲存');
    }
}

// 顯示加載指示器
function showLoading(message) {
    // 檢查是否已存在加載指示器
    let loadingEl = document.getElementById('loadingIndicator');
    
    if (!loadingEl) {
        // 創建加載指示器
        loadingEl = document.createElement('div');
        loadingEl.id = 'loadingIndicator';
        loadingEl.style.position = 'fixed';
        loadingEl.style.top = '50%';
        loadingEl.style.left = '50%';
        loadingEl.style.transform = 'translate(-50%, -50%)';
        loadingEl.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
        loadingEl.style.color = 'white';
        loadingEl.style.padding = '20px';
        loadingEl.style.borderRadius = '10px';
        loadingEl.style.zIndex = '9999';
        loadingEl.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-light" role="status">
                    <span class="visually-hidden">載入中...</span>
                </div>
                <div class="mt-2">${message || '載入中...'}</div>
            </div>
        `;
        
        document.body.appendChild(loadingEl);
    } else {
        // 更新訊息
        const messageEl = loadingEl.querySelector('.mt-2');
        if (messageEl) {
            messageEl.textContent = message || '載入中...';
        }
        
        // 確保可見
        loadingEl.style.display = 'block';
    }
}
