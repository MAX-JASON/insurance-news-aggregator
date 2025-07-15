/**
 * 賽博朋克業務儀表板互動腳本
 * Cyberpunk Business Dashboard Interactive Script
 */

// 確保DOM加載完成
document.addEventListener('DOMContentLoaded', function() {
    console.log('🤖 初始化賽博朋克業務儀表板...');
    initCyberpunkDashboard();
});

// 主初始化函數
function initCyberpunkDashboard() {
    // 應用賽博朋克風格
    applyCyberpunkStyle();
    
    // 初始化交互組件
    initInteractiveComponents();
    
    // 初始化視覺效果
    initVisualEffects();
    
    // 綁定事件處理器
    bindEventHandlers();
    
    // 模擬數據加載
    simulateDataLoading();
    
    console.log('🌐 賽博朋克業務儀表板初始化完成');
}

// 應用賽博朋克風格到各元素
function applyCyberpunkStyle() {
    // 應用主儀表板風格
    const dashboard = document.querySelector('.business-dashboard');
    if (dashboard) {
        dashboard.classList.add('cyber-dashboard');
    }
    
    // 卡片風格
    document.querySelectorAll('.card').forEach(card => {
        card.classList.add('cyber-card');
    });
    
    // 新聞項目風格
    document.querySelectorAll('.news-item').forEach(item => {
        item.classList.add('cyber-news');
    });
    
    // 按鈕風格
    document.querySelectorAll('.btn-outline-primary, .btn-primary').forEach(btn => {
        btn.classList.add('cyber-btn');
    });
    
    document.querySelectorAll('.btn-outline-success, .btn-success').forEach(btn => {
        btn.classList.add('cyber-btn', 'cyber-btn-green');
    });
    
    document.querySelectorAll('.btn-outline-danger, .btn-danger').forEach(btn => {
        btn.classList.add('cyber-btn', 'cyber-btn-pink');
    });
    
    // 搜索框風格
    const searchContainer = document.querySelector('.search-container');
    if (searchContainer) {
        searchContainer.classList.add('cyber-search');
    }
    
    // 分類統計卡風格
    document.querySelectorAll('.card[class*="border-"]').forEach(card => {
        card.classList.add('cyber-stats-card');
    });
    
    // 分類項目風格
    document.querySelectorAll('.category-item').forEach(item => {
        item.classList.add('cyber-category');
    });
    
    // 分享工具風格
    document.querySelectorAll('.share-tools').forEach(tool => {
        tool.classList.add('cyber-tools');
    });
    
    // 商機卡片風格
    document.querySelectorAll('.opportunity-card').forEach(card => {
        card.classList.add('cyber-opportunity');
    });
    
    // 客戶興趣風格
    document.querySelectorAll('.client-interest').forEach(card => {
        card.classList.add('cyber-interest');
    });
    
    // 趨勢指標風格
    document.querySelectorAll('.trend-indicator').forEach(indicator => {
        indicator.classList.add('cyber-trend');
    });
    
    // 霓虹文字效果
    document.querySelectorAll('h5, h6').forEach(heading => {
        heading.classList.add('cyber-text-glow');
    });
    
    console.log('💎 已應用賽博朋克風格');
}

// 初始化交互組件
function initInteractiveComponents() {
    // 初始化拖拽排序
    initDraggableSorting();
    
    // 初始化實時搜索
    initLiveSearch();
    
    // 初始化批量操作
    initBulkActions();
    
    // 初始化自動更新
    initAutoRefresh();
    
    // 初始化工具提示
    initTooltips();
    
    console.log('🔧 已初始化互動組件');
}

// 初始化視覺效果
function initVisualEffects() {
    // 添加網格背景
    addGridBackground();
    
    // 添加霓虹效果
    addNeonEffects();
    
    // 添加數據流視覺效果
    addDataFlowEffects();
    
    console.log('✨ 已初始化視覺效果');
}

// 初始化拖拽排序
function initDraggableSorting() {
    const newsList = document.getElementById('newsList');
    if (newsList && typeof Sortable !== 'undefined') {
        new Sortable(newsList, {
            animation: 150,
            ghostClass: 'sortable-ghost',
            chosenClass: 'sortable-chosen',
            dragClass: 'sortable-drag',
            handle: '.news-item',
            onEnd: function(evt) {
                const item = evt.item;
                console.log('項目已移動到索引 ' + evt.newIndex);
                // 在此處添加移動後的處理邏輯
                flashElement(item, 'rgba(0, 212, 255, 0.3)');
            }
        });
        
        console.log('📋 新聞項目排序功能已啟用');
    } else {
        console.warn('⚠️ 無法初始化拖拽排序功能，請確認已加載 Sortable.js');
    }
}

// 初始化實時搜索
function initLiveSearch() {
    const searchInput = document.getElementById('liveSearch');
    const searchResults = document.getElementById('searchResults');
    const searchSpinner = document.getElementById('searchSpinner');
    const clearSearch = document.getElementById('clearSearch');
    
    if (searchInput && searchResults && searchSpinner) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            
            // 清除之前的超時
            clearTimeout(searchTimeout);
            
            // 如果查詢為空，隱藏結果和加載動畫
            if (!query) {
                searchResults.style.display = 'none';
                searchSpinner.style.display = 'none';
                return;
            }
            
            // 顯示加載動畫
            searchSpinner.style.display = 'block';
            
            // 設置超時來模擬API調用延遲
            searchTimeout = setTimeout(() => {
                // 模擬API調用
                simulateSearchResults(query)
                    .then(results => {
                        // 隱藏加載動畫
                        searchSpinner.style.display = 'none';
                        
                        // 顯示結果
                        searchResults.innerHTML = results;
                        searchResults.style.display = 'block';
                        
                        // 綁定結果點擊事件
                        bindSearchResultsEvents();
                    });
            }, 300);
        });
        
        // 清除搜索按鈕
        if (clearSearch) {
            clearSearch.addEventListener('click', function() {
                searchInput.value = '';
                searchResults.style.display = 'none';
                searchSpinner.style.display = 'none';
            });
        }
        
        // 點擊其他區域時隱藏搜索結果
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.style.display = 'none';
            }
        });
        
        console.log('🔍 實時搜索功能已啟用');
    }
}

// 模擬搜索結果
function simulateSearchResults(query) {
    return new Promise((resolve) => {
        // 模擬數據
        const demoResults = [
            { title: '數位保險新時代：AI與大數據如何改變風險評估', category: '科技趨勢', date: '2025-07-05' },
            { title: '保險理賠自動化提升：客戶滿意度增長30%', category: '行業新聞', date: '2025-07-06' },
            { title: '長照險市場分析：老齡化社會的機遇與挑戰', category: '市場分析', date: '2025-07-07' },
            { title: '金管會最新規範對投資型保單的影響', category: '法規更新', date: '2025-07-07' },
            { title: '2025年保險業數位轉型趨勢報告', category: '研究報告', date: '2025-07-08' }
        ];
        
        // 過濾結果
        const filteredResults = demoResults.filter(item => 
            item.title.toLowerCase().includes(query.toLowerCase()) || 
            item.category.toLowerCase().includes(query.toLowerCase())
        );
        
        // 生成HTML
        let resultsHTML = '';
        
        if (filteredResults.length === 0) {
            resultsHTML = `
                <div class="p-3 bg-dark text-light">
                    <p class="mb-0"><i class="fas fa-info-circle me-2"></i>沒有找到與 "${query}" 相關的結果</p>
                </div>
            `;
        } else {
            resultsHTML = `
                <div class="list-group">
                    ${filteredResults.map(item => `
                        <a href="#" class="list-group-item list-group-item-action search-result-item" data-title="${item.title}">
                            <div class="d-flex justify-content-between align-items-center">
                                <h6 class="mb-1">${item.title}</h6>
                                <span class="badge bg-primary">${item.category}</span>
                            </div>
                            <small class="text-muted"><i class="far fa-clock me-1"></i>${item.date}</small>
                        </a>
                    `).join('')}
                </div>
                <div class="p-2 bg-dark">
                    <a href="/business/search?q=${encodeURIComponent(query)}" class="btn btn-sm cyber-btn w-100">
                        <i class="fas fa-search me-1"></i>查看全部結果
                    </a>
                </div>
            `;
        }
        
        setTimeout(() => {
            resolve(resultsHTML);
        }, 300); // 模擬網絡延遲
    });
}

// 綁定搜索結果點擊事件
function bindSearchResultsEvents() {
    document.querySelectorAll('.search-result-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const title = this.getAttribute('data-title');
            showNotification(`已選擇: "${title}"`, 'success');
            
            // 在此處添加點擊搜索結果後的處理邏輯
            document.getElementById('searchResults').style.display = 'none';
        });
    });
}

// 初始化批量操作
function initBulkActions() {
    const selectAll = document.getElementById('selectAll');
    const newsSelects = document.querySelectorAll('.news-select');
    const bulkActionsContainer = document.getElementById('bulkActionsContainer');
    const selectedCount = document.getElementById('selectedCount');
    const bulkActionBtns = document.querySelectorAll('.bulk-action-btn');
    
    if (selectAll && newsSelects.length > 0 && bulkActionsContainer && selectedCount) {
        // 全選按鈕
        selectAll.addEventListener('change', function() {
            const isChecked = this.checked;
            newsSelects.forEach(checkbox => {
                checkbox.checked = isChecked;
                
                // 更新選中項目的視覺樣式
                const newsItem = checkbox.closest('.news-item');
                if (newsItem) {
                    if (isChecked) {
                        newsItem.classList.add('selected');
                    } else {
                        newsItem.classList.remove('selected');
                    }
                }
            });
            
            // 更新計數和批量操作容器顯示
            updateSelectedCount();
        });
        
        // 單個選擇按鈕
        newsSelects.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                // 更新選中項目的視覺樣式
                const newsItem = this.closest('.news-item');
                if (newsItem) {
                    if (this.checked) {
                        newsItem.classList.add('selected');
                    } else {
                        newsItem.classList.remove('selected');
                    }
                }
                
                // 檢查是否所有項目都被選中
                const allChecked = Array.from(newsSelects).every(cb => cb.checked);
                selectAll.checked = allChecked;
                
                // 更新計數和批量操作容器顯示
                updateSelectedCount();
            });
        });
        
        // 批量操作按鈕
        bulkActionBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const action = this.getAttribute('data-action');
                const selectedItems = document.querySelectorAll('.news-select:checked');
                const selectedIds = Array.from(selectedItems).map(cb => cb.value);
                
                performBulkAction(action, selectedIds);
            });
        });
        
        console.log('📦 批量操作功能已啟用');
    }
    
    // 更新選中項目計數
    function updateSelectedCount() {
        const selectedItems = document.querySelectorAll('.news-select:checked');
        const count = selectedItems.length;
        
        if (selectedCount) {
            selectedCount.textContent = count;
        }
        
        // 顯示或隱藏批量操作容器
        if (bulkActionsContainer) {
            if (count > 0) {
                bulkActionsContainer.classList.remove('d-none');
            } else {
                bulkActionsContainer.classList.add('d-none');
            }
        }
    }
    
    // 執行批量操作
    function performBulkAction(action, ids) {
        console.log(`執行批量操作: ${action}，選中的項目ID: ${ids.join(', ')}`);
        
        // 在此處添加不同批量操作的處理邏輯
        switch (action) {
            case 'export':
                showNotification(`已選擇匯出 ${ids.length} 筆項目`, 'info');
                // 模擬下載操作
                setTimeout(() => {
                    showNotification('匯出成功！檔案已保存到下載資料夾', 'success');
                }, 1500);
                break;
            case 'share':
                showNotification(`已選擇分享 ${ids.length} 筆項目`, 'info');
                // 模擬分享對話框
                $('#shareModal').modal('show');
                break;
            case 'priority':
                showNotification(`已將 ${ids.length} 筆項目設為優先`, 'success');
                // 模擬視覺效果
                ids.forEach(id => {
                    const item = document.querySelector(`.news-item[data-news-id="${id}"]`);
                    if (item) {
                        item.classList.add('priority-highlight');
                        setTimeout(() => {
                            item.classList.remove('priority-highlight');
                        }, 2000);
                    }
                });
                break;
            case 'archive':
                showNotification(`已封存 ${ids.length} 筆項目`, 'success');
                // 模擬視覺效果
                ids.forEach(id => {
                    const item = document.querySelector(`.news-item[data-news-id="${id}"]`);
                    if (item) {
                        item.style.opacity = '0.5';
                        setTimeout(() => {
                            item.style.display = 'none';
                        }, 1000);
                    }
                });
                break;
        }
    }
}

// 初始化自動更新
function initAutoRefresh() {
    const autoRefreshSwitch = document.getElementById('autoRefresh');
    let refreshInterval;
    
    if (autoRefreshSwitch) {
        autoRefreshSwitch.addEventListener('change', function() {
            if (this.checked) {
                showNotification('自動更新已啟用，每60秒刷新一次', 'info');
                
                // 設置刷新間隔
                refreshInterval = setInterval(() => {
                    refreshDashboard(true);
                }, 60000); // 60秒
            } else {
                showNotification('自動更新已停用', 'info');
                
                // 清除刷新間隔
                if (refreshInterval) {
                    clearInterval(refreshInterval);
                }
            }
        });
        
        console.log('🔄 自動更新功能已啟用');
    }
}

// 初始化工具提示
function initTooltips() {
    // 檢查是否已載入Bootstrap
    if (typeof bootstrap !== 'undefined') {
        // 初始化所有帶有data-bs-toggle="tooltip"屬性的元素
        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
            new bootstrap.Tooltip(el);
        });
        
        console.log('🔍 工具提示功能已啟用');
    } else {
        console.warn('⚠️ 無法初始化工具提示，請確認已加載 Bootstrap');
    }
}

// 添加網格背景
function addGridBackground() {
    // 檢查是否已存在網格背景
    if (!document.querySelector('.cyber-dashboard-grid')) {
        const dashboard = document.querySelector('.business-dashboard');
        
        if (dashboard) {
            // 創建網格背景
            const grid = document.createElement('div');
            grid.className = 'cyber-dashboard-grid';
            grid.style.position = 'absolute';
            grid.style.top = '0';
            grid.style.left = '0';
            grid.style.right = '0';
            grid.style.bottom = '0';
            grid.style.pointerEvents = 'none';
            grid.style.zIndex = '-1';
            grid.style.opacity = '0.1';
            grid.style.backgroundImage = `
                linear-gradient(rgba(0, 212, 255, 0.3) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 212, 255, 0.3) 1px, transparent 1px)
            `;
            grid.style.backgroundSize = '20px 20px';
            
            // 將網格背景添加到儀表板
            dashboard.style.position = 'relative';
            dashboard.appendChild(grid);
            
            console.log('🌐 已添加網格背景');
        }
    }
}

// 添加霓虹效果
function addNeonEffects() {
    // 為標題添加霓虹發光效果
    document.querySelectorAll('.business-dashboard h1, .card-header h5, .card-header h6').forEach(el => {
        el.classList.add('cyber-text-glow');
    });
    
    // 為重要按鈕添加脈衝效果
    document.querySelectorAll('.btn-primary, .favorite-btn').forEach(el => {
        el.classList.add('cyber-pulse');
    });
    
    console.log('💫 已添加霓虹效果');
}

// 添加數據流視覺效果
function addDataFlowEffects() {
    // 這個函數可以用來創建更複雜的視覺效果，如數據流動畫
    // 簡化版本：為重要項目添加閃爍效果
    document.querySelectorAll('.importance-star, .trend-indicator').forEach(el => {
        el.classList.add('cyber-text-glow');
    });
    
    console.log('📊 已添加數據流效果');
}

// 綁定事件處理器
function bindEventHandlers() {
    // 收藏按鈕
    document.querySelectorAll('.favorite-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const newsId = this.getAttribute('data-news-id');
            toggleFavorite(this, newsId);
        });
    });
    
    // 快速操作按鈕
    document.querySelectorAll('.quick-action-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const action = this.getAttribute('data-action');
            const newsId = this.getAttribute('data-news-id');
            
            performQuickAction(action, newsId);
        });
    });
    
    // 進階分享按鈕
    document.querySelectorAll('.advanced-share-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const newsId = this.getAttribute('data-news-id');
            
            showAdvancedShareOptions(newsId);
        });
    });
    
    // 模板生成器按鈕
    document.querySelectorAll('.template-generator-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const newsId = this.getAttribute('data-news-id');
            
            generateTemplate(newsId);
        });
    });
    
    // 分類篩選按鈕
    document.querySelectorAll('.quick-filter').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const filter = this.getAttribute('data-filter');
            
            applyFilter(filter);
            
            // 更新按鈕狀態
            document.querySelectorAll('.quick-filter').forEach(b => {
                b.classList.remove('active', 'btn-primary');
                b.classList.add('btn-outline-primary');
            });
            this.classList.remove('btn-outline-primary');
            this.classList.add('active', 'btn-primary');
        });
    });
    
    // 自定義篩選按鈕
    const customFilterBtn = document.getElementById('customFilter');
    if (customFilterBtn) {
        customFilterBtn.addEventListener('click', function(e) {
            e.preventDefault();
            showCustomFilterDialog();
        });
    }
    
    // 客戶列表按鈕
    const clientListBtn = document.getElementById('clientListBtn');
    if (clientListBtn) {
        clientListBtn.addEventListener('click', function(e) {
            e.preventDefault();
            showClientList();
        });
    }
    
    // 查看全部按鈕
    document.querySelectorAll('.view-all-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const group = this.getAttribute('data-group');
            
            viewAllItems(group);
        });
    });
    
    // 分類項目點擊
    document.querySelectorAll('.category-item').forEach(item => {
        item.addEventListener('click', function(e) {
            const category = this.getAttribute('data-category');
            
            showCategoryNews(category);
        });
    });
    
    console.log('🎮 已綁定互動事件');
}

// 切換收藏狀態
function toggleFavorite(button, newsId) {
    const isFavorite = button.querySelector('i').classList.contains('fas');
    
    if (isFavorite) {
        // 取消收藏
        button.querySelector('i').classList.remove('fas');
        button.querySelector('i').classList.add('far');
        showNotification('已從收藏中移除', 'info');
    } else {
        // 加入收藏
        button.querySelector('i').classList.remove('far');
        button.querySelector('i').classList.add('fas');
        showNotification('已加入收藏', 'success');
        
        // 視覺反饋
        button.classList.add('pulse-once');
        setTimeout(() => {
            button.classList.remove('pulse-once');
        }, 1000);
    }
    
    // 在此處添加收藏操作的實際API調用
    console.log(`切換收藏狀態：ID ${newsId}，當前狀態：${!isFavorite ? '已收藏' : '未收藏'}`);
}

// 執行快速操作
function performQuickAction(action, newsId) {
    console.log(`執行快速操作：${action}，新聞ID：${newsId}`);
    
    // 根據不同操作執行對應邏輯
    switch (action) {
        case 'client-template':
            showNotification('正在生成客戶模板...', 'info');
            // 模擬API調用
            setTimeout(() => {
                showNotification('客戶模板已生成！', 'success');
            }, 1000);
            break;
            
        case 'product-link':
            showNotification('正在尋找相關產品...', 'info');
            // 模擬API調用
            setTimeout(() => {
                showProductLinks();
            }, 800);
            break;
            
        case 'market-analysis':
            showNotification('載入市場分析數據...', 'info');
            // 模擬API調用
            setTimeout(() => {
                showMarketAnalysis();
            }, 1200);
            break;
            
        case 'regulation-guide':
            showNotification('載入法規解讀...', 'info');
            // 模擬API調用
            setTimeout(() => {
                showRegulationGuide();
            }, 1000);
            break;
    }
}

// 顯示進階分享選項
function showAdvancedShareOptions(newsId) {
    console.log(`顯示進階分享選項，新聞ID：${newsId}`);
    
    // 實作：顯示分享對話框或展開分享選項
    // 這裡使用Bootstrap模態框作為示例
    if (typeof bootstrap !== 'undefined') {
        // 假設已經有一個預定義的模態框，ID為shareModal
        const shareModal = new bootstrap.Modal(document.getElementById('shareModal'));
        shareModal.show();
    } else {
        // 備用方案：顯示通知
        showNotification('分享選項已開啟', 'info');
    }
}

// 生成模板
function generateTemplate(newsId) {
    console.log(`生成模板，新聞ID：${newsId}`);
    
    showNotification('正在生成模板...', 'info');
    
    // 模擬API調用
    setTimeout(() => {
        showNotification('模板生成成功！已保存到模板庫', 'success');
    }, 1500);
}

// 應用篩選
function applyFilter(filter) {
    console.log(`應用篩選：${filter}`);
    
    showNotification(`正在篩選：${filter}...`, 'info');
    
    // 顯示載入指示器
    const loadingSpinner = document.getElementById('loadingSpinner');
    if (loadingSpinner) {
        loadingSpinner.classList.remove('d-none');
    }
    
    // 模擬API調用
    setTimeout(() => {
        // 隱藏載入指示器
        if (loadingSpinner) {
            loadingSpinner.classList.add('d-none');
        }
        
        // 更新篩選統計
        updateFilterStats(filter);
        
        // 更新新聞列表（模擬）
        simulateFilteredResults(filter);
        
        showNotification(`已顯示 ${filter} 篩選結果`, 'success');
    }, 800);
}

// 更新篩選統計
function updateFilterStats(filter) {
    const filterStats = document.getElementById('filterStats');
    if (filterStats) {
        let statsText = '';
        
        switch (filter) {
            case 'high-priority':
                statsText = '篩選條件：高重要性 | 共找到 3 筆符合項目';
                break;
            case 'opportunities':
                statsText = '篩選條件：商機 | 共找到 5 筆符合項目';
                break;
            case 'regulatory':
                statsText = '篩選條件：法規 | 共找到 2 筆符合項目';
                break;
            default:
                statsText = `篩選條件：${filter} | 共找到多筆符合項目`;
        }
        
        filterStats.textContent = statsText;
    }
}

// 模擬篩選結果
function simulateFilteredResults(filter) {
    // 在實際應用中，這裡應該是API調用
    // 為了演示，我們只進行簡單的DOM操作
    
    // 取得所有新聞項目
    const newsItems = document.querySelectorAll('.news-item');
    
    // 隱藏所有項目
    newsItems.forEach(item => {
        item.style.display = 'none';
    });
    
    // 根據篩選條件顯示特定項目
    setTimeout(() => {
        switch (filter) {
            case 'high-priority':
                // 顯示帶有importance-star的項目（高重要性）
                document.querySelectorAll('.news-item .importance-star').forEach(star => {
                    if (star.textContent.includes('★★★')) {
                        star.closest('.news-item').style.display = 'block';
                        flashElement(star.closest('.news-item'), 'rgba(255, 7, 58, 0.3)');
                    }
                });
                break;
                
            case 'opportunities':
                // 顯示帶有badge bg-warning的項目（商機）
                document.querySelectorAll('.news-item .badge.bg-warning, .news-item .badge.bg-info').forEach(badge => {
                    badge.closest('.news-item').style.display = 'block';
                    flashElement(badge.closest('.news-item'), 'rgba(57, 255, 20, 0.3)');
                });
                break;
                
            case 'regulatory':
                // 顯示帶有badge bg-secondary的項目（法規）
                document.querySelectorAll('.news-item .badge.bg-secondary').forEach(badge => {
                    badge.closest('.news-item').style.display = 'block';
                    flashElement(badge.closest('.news-item'), 'rgba(0, 212, 255, 0.3)');
                });
                break;
                
            default:
                // 顯示所有項目
                newsItems.forEach(item => {
                    item.style.display = 'block';
                });
        }
    }, 200);
}

// 顯示自定義篩選對話框
function showCustomFilterDialog() {
    console.log('顯示自定義篩選對話框');
    
    showNotification('自定義篩選功能已開啟', 'info');
    
    // 實作：顯示自定義篩選對話框
    // 這裡使用Bootstrap模態框作為示例
    if (typeof bootstrap !== 'undefined') {
        // 假設已經有一個預定義的模態框，ID為customFilterModal
        const customFilterModal = new bootstrap.Modal(document.getElementById('customFilterModal'));
        customFilterModal.show();
    }
}

// 顯示客戶列表
function showClientList() {
    console.log('顯示客戶列表');
    
    showNotification('正在載入客戶列表...', 'info');
    
    // 模擬API調用
    setTimeout(() => {
        // 假設已經有一個預定義的模態框，ID為clientListModal
        if (typeof bootstrap !== 'undefined') {
            const clientListModal = new bootstrap.Modal(document.getElementById('clientListModal'));
            clientListModal.show();
        } else {
            showNotification('客戶列表已準備就緒', 'success');
        }
    }, 800);
}

// 查看全部項目
function viewAllItems(group) {
    console.log(`查看全部項目：${group}`);
    
    showNotification(`正在載入全部 ${group} 項目...`, 'info');
    
    // 模擬頁面導航
    setTimeout(() => {
        // 根據不同分組處理不同頁面導航
        switch (group) {
            case '客戶關注':
                window.location.href = '/business/categories/client-interests';
                break;
            case '公司動態':
                window.location.href = '/business/categories/company-news';
                break;
            case '市場分析':
                window.location.href = '/business/categories/market-analysis';
                break;
            default:
                window.location.href = '/business/categories';
        }
    }, 500);
}

// 顯示分類新聞
function showCategoryNews(category) {
    console.log(`顯示分類新聞：${category}`);
    
    showNotification(`正在載入 ${category} 相關新聞...`, 'info');
    
    // 在此處添加加載特定分類新聞的邏輯
    // 可以是頁面導航或加載模態框
    setTimeout(() => {
        window.location.href = `/business/category/${encodeURIComponent(category)}`;
    }, 500);
}

// 顯示產品連結
function showProductLinks() {
    showNotification('已找到3個相關產品', 'success');
    
    // 實作：顯示產品連結對話框
    // 這裡使用Bootstrap模態框作為示例
    if (typeof bootstrap !== 'undefined') {
        // 假設已經有一個預定義的模態框，ID為productLinksModal
        const productLinksModal = new bootstrap.Modal(document.getElementById('productLinksModal'));
        productLinksModal.show();
    }
}

// 顯示市場分析
function showMarketAnalysis() {
    showNotification('市場分析數據已載入', 'success');
    
    // 實作：顯示市場分析對話框或頁面
    // 這裡使用Bootstrap模態框作為示例
    if (typeof bootstrap !== 'undefined') {
        // 假設已經有一個預定義的模態框，ID為marketAnalysisModal
        const marketAnalysisModal = new bootstrap.Modal(document.getElementById('marketAnalysisModal'));
        marketAnalysisModal.show();
    }
}

// 顯示法規解讀
function showRegulationGuide() {
    showNotification('法規解讀已載入', 'success');
    
    // 實作：顯示法規解讀對話框或頁面
    // 這裡使用Bootstrap模態框作為示例
    if (typeof bootstrap !== 'undefined') {
        // 假設已經有一個預定義的模態框，ID為regulationGuideModal
        const regulationGuideModal = new bootstrap.Modal(document.getElementById('regulationGuideModal'));
        regulationGuideModal.show();
    }
}

// 顯示通知
function showNotification(message, type = 'info') {
    // 檢查是否存在通知容器，如果不存在則創建
    let notifContainer = document.getElementById('cyber-notifications');
    
    if (!notifContainer) {
        notifContainer = document.createElement('div');
        notifContainer.id = 'cyber-notifications';
        notifContainer.style.position = 'fixed';
        notifContainer.style.top = '20px';
        notifContainer.style.right = '20px';
        notifContainer.style.zIndex = '9999';
        notifContainer.style.maxWidth = '300px';
        document.body.appendChild(notifContainer);
    }
    
    // 創建通知元素
    const notif = document.createElement('div');
    notif.className = `cyber-notification cyber-notification-${type}`;
    notif.innerHTML = `
        <div class="cyber-notification-content">
            <i class="fas ${getIconForType(type)} me-2"></i>
            <span>${message}</span>
        </div>
    `;
    
    // 添加樣式
    notif.style.backgroundColor = getColorForType(type);
    notif.style.color = '#ffffff';
    notif.style.padding = '12px 15px';
    notif.style.borderRadius = '5px';
    notif.style.marginBottom = '10px';
    notif.style.boxShadow = `0 0 15px ${getGlowForType(type)}`;
    notif.style.animation = 'fadeInRight 0.3s ease-out forwards';
    notif.style.opacity = '0';
    notif.style.transform = 'translateX(50px)';
    
    // 添加到容器
    notifContainer.appendChild(notif);
    
    // 添加CSS動畫
    if (!document.getElementById('cyber-notification-style')) {
        const style = document.createElement('style');
        style.id = 'cyber-notification-style';
        style.textContent = `
            @keyframes fadeInRight {
                from {
                    opacity: 0;
                    transform: translateX(50px);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
            
            @keyframes fadeOutRight {
                from {
                    opacity: 1;
                    transform: translateX(0);
                }
                to {
                    opacity: 0;
                    transform: translateX(50px);
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // 設置淡出動畫
    setTimeout(() => {
        notif.style.animation = 'fadeOutRight 0.3s ease-in forwards';
        setTimeout(() => {
            notifContainer.removeChild(notif);
        }, 300);
    }, 3000);
    
    // 輔助函數：根據類型獲取圖標
    function getIconForType(type) {
        switch (type) {
            case 'success': return 'fa-check-circle';
            case 'error': return 'fa-exclamation-circle';
            case 'warning': return 'fa-exclamation-triangle';
            default: return 'fa-info-circle';
        }
    }
    
    // 輔助函數：根據類型獲取顏色
    function getColorForType(type) {
        switch (type) {
            case 'success': return 'rgba(57, 255, 20, 0.8)';
            case 'error': return 'rgba(255, 7, 58, 0.8)';
            case 'warning': return 'rgba(255, 140, 0, 0.8)';
            default: return 'rgba(0, 212, 255, 0.8)';
        }
    }
    
    // 輔助函數：根據類型獲取發光效果
    function getGlowForType(type) {
        switch (type) {
            case 'success': return 'rgba(57, 255, 20, 0.4)';
            case 'error': return 'rgba(255, 7, 58, 0.4)';
            case 'warning': return 'rgba(255, 140, 0, 0.4)';
            default: return 'rgba(0, 212, 255, 0.4)';
        }
    }
}

// 閃爍元素（視覺反饋）
function flashElement(element, color) {
    const originalBackground = element.style.backgroundColor;
    
    element.style.transition = 'background-color 0.3s ease';
    element.style.backgroundColor = color;
    
    setTimeout(() => {
        element.style.backgroundColor = originalBackground;
    }, 500);
}

// 模擬數據加載
function simulateDataLoading() {
    // 更新分類統計數據
    setTimeout(() => {
        // 客戶關注分類
        document.getElementById('count-理賠案例').textContent = '12';
        document.getElementById('count-保費調整').textContent = '8';
        document.getElementById('count-法規變動').textContent = '5';
        
        // 公司動態分類
        document.getElementById('count-新商品發布').textContent = '3';
        document.getElementById('count-通路政策').textContent = '7';
        document.getElementById('count-獲獎消息').textContent = '2';
        
        // 市場分析分類
        document.getElementById('count-保費趨勢').textContent = '6';
        document.getElementById('count-競爭分析').textContent = '4';
        document.getElementById('count-客群變化').textContent = '9';
    }, 1000);
    
    console.log('📊 已模擬數據加載');
}

// 刷新儀表板
function refreshDashboard(isAutoRefresh = false) {
    console.log(`刷新儀表板 ${isAutoRefresh ? '(自動)' : ''}`);
    
    // 顯示加載指示器
    const loadingSpinner = document.getElementById('loadingSpinner');
    if (loadingSpinner) {
        loadingSpinner.classList.remove('d-none');
    }
    
    // 模擬API調用
    setTimeout(() => {
        // 隱藏加載指示器
        if (loadingSpinner) {
            loadingSpinner.classList.add('d-none');
        }
        
        // 更新數據
        simulateDataLoading();
        
        showNotification(isAutoRefresh ? '儀表板已自動更新' : '儀表板已手動更新', 'success');
    }, 1000);
}

// 輸出到全局範圍，供外部訪問
window.businessDashboard = {
    refreshNewsList: refreshDashboard,
    showNotification: showNotification,
    applyFilter: applyFilter,
    toggleFavorite: toggleFavorite
};

// 導出為工具類，供其他模塊使用
window.businessTools = {
    showToast: showNotification,
    flashElement: flashElement
};
