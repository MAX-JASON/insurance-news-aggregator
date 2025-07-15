/**
 * 標籤分頁修復和增強腳本
 * Tab Navigation Fix & Enhancement Script
 */

// 等待DOM載入完成
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 開始修復標籤分頁功能...');
    
    // 修復所有標籤分頁問題
    fixAllTabIssues();
    
    // 增強標籤分頁功能
    enhanceTabFunctionality();
    
    console.log('✅ 標籤分頁修復完成');
});

/**
 * 修復所有標籤分頁問題
 */
function fixAllTabIssues() {
    // 1. 修復Bootstrap標籤分頁
    fixBootstrapTabs();
    
    // 2. 修復Pills導航
    fixPillsNavigation();
    
    // 3. 修復自定義標籤
    fixCustomTabs();
    
    // 4. 修復鍵盤導航
    fixKeyboardNavigation();
    
    // 5. 修復無障礙訪問
    fixAccessibility();
}

/**
 * 修復Bootstrap標籤分頁
 */
function fixBootstrapTabs() {
    const tabContainers = document.querySelectorAll('.nav-tabs, [data-bs-toggle="tab"]');
    
    tabContainers.forEach(container => {
        const tabs = container.querySelectorAll('[data-bs-toggle="tab"], [data-bs-toggle="pill"]');
        
        tabs.forEach(tab => {
            // 確保有正確的事件監聽器
            if (!tab.hasAttribute('data-tab-fixed')) {
                tab.addEventListener('click', function(e) {
                    e.preventDefault();
                    handleTabClick(this);
                });
                
                // 標記為已修復
                tab.setAttribute('data-tab-fixed', 'true');
            }
            
            // 修復aria屬性
            if (!tab.hasAttribute('role')) {
                tab.setAttribute('role', 'tab');
            }
            
            if (!tab.hasAttribute('aria-selected')) {
                tab.setAttribute('aria-selected', tab.classList.contains('active') ? 'true' : 'false');
            }
            
            // 確保tabindex
            if (!tab.hasAttribute('tabindex')) {
                tab.setAttribute('tabindex', tab.classList.contains('active') ? '0' : '-1');
            }
        });
    });
}

/**
 * 修復Pills導航
 */
function fixPillsNavigation() {
    const pillsContainers = document.querySelectorAll('.nav-pills');
    
    pillsContainers.forEach(container => {
        const pills = container.querySelectorAll('.nav-link');
        
        pills.forEach(pill => {
            if (!pill.hasAttribute('data-pill-fixed')) {
                // 添加點擊處理
                pill.addEventListener('click', function(e) {
                    e.preventDefault();
                    handlePillClick(this);
                });
                
                // 添加鍵盤支持
                pill.addEventListener('keydown', function(e) {
                    handleTabKeydown(e, this);
                });
                
                pill.setAttribute('data-pill-fixed', 'true');
            }
        });
    });
}

/**
 * 修復自定義標籤
 */
function fixCustomTabs() {
    // 處理list-group標籤 (如用戶設置頁面)
    const listGroups = document.querySelectorAll('.list-group[role="tablist"]');
    
    listGroups.forEach(group => {
        const items = group.querySelectorAll('.list-group-item[data-bs-toggle="list"]');
        
        items.forEach(item => {
            if (!item.hasAttribute('data-list-fixed')) {
                item.addEventListener('click', function(e) {
                    e.preventDefault();
                    handleListItemClick(this);
                });
                
                item.addEventListener('keydown', function(e) {
                    handleTabKeydown(e, this);
                });
                
                item.setAttribute('data-list-fixed', 'true');
            }
        });
    });
}

/**
 * 處理標籤點擊
 */
function handleTabClick(tab) {
    const target = tab.getAttribute('data-bs-target') || tab.getAttribute('href');
    
    if (!target) {
        console.warn('標籤缺少目標:', tab);
        return;
    }
    
    // 移除所有兄弟標籤的活動狀態
    const siblings = tab.parentElement.parentElement.querySelectorAll('[data-bs-toggle="tab"], [data-bs-toggle="pill"]');
    siblings.forEach(sibling => {
        sibling.classList.remove('active');
        sibling.setAttribute('aria-selected', 'false');
        sibling.setAttribute('tabindex', '-1');
    });
    
    // 激活當前標籤
    tab.classList.add('active');
    tab.setAttribute('aria-selected', 'true');
    tab.setAttribute('tabindex', '0');
    
    // 處理標籤內容
    showTabContent(target);
    
    // 觸發自定義事件
    tab.dispatchEvent(new CustomEvent('tab:shown', {
        detail: { target: target, tab: tab }
    }));
}

/**
 * 處理Pills點擊
 */
function handlePillClick(pill) {
    const target = pill.getAttribute('data-bs-target') || pill.getAttribute('href');
    
    if (!target) {
        console.warn('Pills缺少目標:', pill);
        return;
    }
    
    // 移除所有兄弟pills的活動狀態
    const siblings = pill.parentElement.parentElement.querySelectorAll('.nav-link');
    siblings.forEach(sibling => {
        sibling.classList.remove('active');
        sibling.setAttribute('aria-selected', 'false');
    });
    
    // 激活當前pill
    pill.classList.add('active');
    pill.setAttribute('aria-selected', 'true');
    
    // 處理內容
    showTabContent(target);
    
    // 觸發事件
    pill.dispatchEvent(new CustomEvent('pill:shown', {
        detail: { target: target, pill: pill }
    }));
}

/**
 * 處理列表項點擊
 */
function handleListItemClick(item) {
    const target = item.getAttribute('href');
    
    if (!target) {
        console.warn('列表項缺少目標:', item);
        return;
    }
    
    // 移除所有兄弟項的活動狀態
    const siblings = item.parentElement.querySelectorAll('.list-group-item');
    siblings.forEach(sibling => {
        sibling.classList.remove('active');
        sibling.setAttribute('aria-selected', 'false');
    });
    
    // 激活當前項
    item.classList.add('active');
    item.setAttribute('aria-selected', 'true');
    
    // 處理內容
    showTabContent(target);
    
    // 觸發事件
    item.dispatchEvent(new CustomEvent('list:shown', {
        detail: { target: target, item: item }
    }));
}

/**
 * 顯示標籤內容
 */
function showTabContent(target) {
    const targetElement = document.querySelector(target);
    
    if (!targetElement) {
        console.warn('找不到目標元素:', target);
        return;
    }
    
    // 查找所有相關的標籤面板
    const tabContent = targetElement.closest('.tab-content');
    if (tabContent) {
        // 隱藏所有標籤面板
        tabContent.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('show', 'active');
        });
        
        // 顯示目標面板
        targetElement.classList.add('show', 'active');
        
        // 添加淡入效果
        if (targetElement.classList.contains('fade')) {
            setTimeout(() => {
                targetElement.classList.add('show');
            }, 10);
        }
    }
    
    // 如果有延遲載入的內容，現在載入
    if (targetElement.hasAttribute('data-lazy-load') && 
        !targetElement.hasAttribute('data-loaded')) {
        loadTabContentLazy(targetElement);
    }
}

/**
 * 延遲載入標籤內容
 */
function loadTabContentLazy(tabPane) {
    const loadUrl = tabPane.getAttribute('data-lazy-load');
    
    if (!loadUrl) return;
    
    // 顯示載入指示器
    tabPane.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">載入中...</span>
            </div>
            <div class="mt-2">載入內容中...</div>
        </div>
    `;
    
    // 載入內容
    fetch(loadUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.text();
        })
        .then(html => {
            tabPane.innerHTML = html;
            tabPane.setAttribute('data-loaded', 'true');
            
            // 觸發載入完成事件
            tabPane.dispatchEvent(new CustomEvent('tab:loaded', {
                detail: { url: loadUrl, content: html }
            }));
        })
        .catch(error => {
            console.error('載入標籤內容失敗:', error);
            tabPane.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    載入內容失敗: ${error.message}
                    <button class="btn btn-sm btn-outline-danger ms-2" onclick="this.closest('.tab-pane').removeAttribute('data-loaded'); loadTabContentLazy(this.closest('.tab-pane'))">
                        重試
                    </button>
                </div>
            `;
        });
}

/**
 * 修復鍵盤導航
 */
function fixKeyboardNavigation() {
    document.addEventListener('keydown', function(e) {
        const target = e.target;
        
        // 只處理標籤元素
        if (!target.matches('[role="tab"], .nav-link, .list-group-item[data-bs-toggle="list"]')) {
            return;
        }
        
        handleTabKeydown(e, target);
    });
}

/**
 * 處理標籤鍵盤事件
 */
function handleTabKeydown(e, tab) {
    const parent = tab.closest('.nav, .list-group');
    if (!parent) return;
    
    const tabs = Array.from(parent.querySelectorAll('[role="tab"], .nav-link, .list-group-item[data-bs-toggle="list"]'));
    const currentIndex = tabs.indexOf(tab);
    
    let nextIndex;
    
    switch (e.key) {
        case 'ArrowLeft':
        case 'ArrowUp':
            nextIndex = currentIndex > 0 ? currentIndex - 1 : tabs.length - 1;
            e.preventDefault();
            break;
        case 'ArrowRight':
        case 'ArrowDown':
            nextIndex = currentIndex < tabs.length - 1 ? currentIndex + 1 : 0;
            e.preventDefault();
            break;
        case 'Home':
            nextIndex = 0;
            e.preventDefault();
            break;
        case 'End':
            nextIndex = tabs.length - 1;
            e.preventDefault();
            break;
        case 'Enter':
        case ' ':
            tab.click();
            e.preventDefault();
            break;
        default:
            return;
    }
    
    if (nextIndex !== undefined) {
        tabs[nextIndex].focus();
        tabs[nextIndex].click();
    }
}

/**
 * 修復無障礙訪問
 */
function fixAccessibility() {
    // 修復所有標籤容器的role
    document.querySelectorAll('.nav-tabs, .nav-pills').forEach(nav => {
        if (!nav.hasAttribute('role')) {
            nav.setAttribute('role', 'tablist');
        }
    });
    
    // 修復所有標籤面板的role
    document.querySelectorAll('.tab-pane').forEach(pane => {
        if (!pane.hasAttribute('role')) {
            pane.setAttribute('role', 'tabpanel');
        }
        
        // 確保有aria-labelledby
        const id = pane.id;
        if (id && !pane.hasAttribute('aria-labelledby')) {
            const tab = document.querySelector(`[data-bs-target="#${id}"], [href="#${id}"]`);
            if (tab && tab.id) {
                pane.setAttribute('aria-labelledby', tab.id);
            }
        }
        
        // 設置tabindex
        if (!pane.hasAttribute('tabindex')) {
            pane.setAttribute('tabindex', '0');
        }
    });
}

/**
 * 增強標籤分頁功能
 */
function enhanceTabFunctionality() {
    // 1. 添加標籤切換動畫
    addTabAnimations();
    
    // 2. 添加標籤狀態記憶
    addTabMemory();
    
    // 3. 添加標籤事件監聽
    addTabEventListeners();
    
    // 4. 添加標籤工具提示
    addTabTooltips();
}

/**
 * 添加標籤切換動畫
 */
function addTabAnimations() {
    const style = document.createElement('style');
    style.textContent = `
        .tab-pane {
            transition: opacity 0.3s ease-in-out;
        }
        
        .tab-pane:not(.show) {
            opacity: 0;
        }
        
        .tab-pane.show {
            opacity: 1;
        }
        
        .nav-link {
            transition: all 0.2s ease-in-out;
        }
        
        .nav-link:hover {
            transform: translateY(-1px);
        }
        
        .nav-link.active {
            transform: none;
        }
    `;
    document.head.appendChild(style);
}

/**
 * 添加標籤狀態記憶
 */
function addTabMemory() {
    // 保存活動標籤到localStorage
    document.addEventListener('tab:shown', function(e) {
        const tabId = e.target.getAttribute('aria-controls') || 
                     e.detail.target.replace('#', '');
        const pageKey = window.location.pathname;
        
        try {
            const savedTabs = JSON.parse(localStorage.getItem('activeTabs') || '{}');
            savedTabs[pageKey] = tabId;
            localStorage.setItem('activeTabs', JSON.stringify(savedTabs));
        } catch (error) {
            console.warn('無法保存標籤狀態:', error);
        }
    });
    
    // 恢復上次活動的標籤
    window.addEventListener('load', function() {
        const pageKey = window.location.pathname;
        
        try {
            const savedTabs = JSON.parse(localStorage.getItem('activeTabs') || '{}');
            const lastActiveTab = savedTabs[pageKey];
            
            if (lastActiveTab) {
                const tab = document.querySelector(`[aria-controls="${lastActiveTab}"], [data-bs-target="#${lastActiveTab}"], [href="#${lastActiveTab}"]`);
                if (tab) {
                    setTimeout(() => tab.click(), 100);
                }
            }
        } catch (error) {
            console.warn('無法恢復標籤狀態:', error);
        }
    });
}

/**
 * 添加標籤事件監聽
 */
function addTabEventListeners() {
    // 全局標籤事件處理
    document.addEventListener('tab:shown', function(e) {
        console.log('標籤已切換:', e.detail);
        
        // 如果有圖表需要重新調整大小
        if (window.Chart) {
            setTimeout(() => {
                Object.values(Chart.instances).forEach(chart => {
                    chart.resize();
                });
            }, 300);
        }
        
        // 觸發window resize事件 (某些組件可能需要)
        setTimeout(() => {
            window.dispatchEvent(new Event('resize'));
        }, 300);
    });
    
    // 標籤載入事件處理
    document.addEventListener('tab:loaded', function(e) {
        console.log('標籤內容已載入:', e.detail);
        
        // 重新初始化新載入內容中的組件
        initializeComponentsInElement(e.target);
    });
}

/**
 * 添加標籤工具提示
 */
function addTabTooltips() {
    document.querySelectorAll('.nav-link[title], .list-group-item[title]').forEach(element => {
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            new bootstrap.Tooltip(element);
        }
    });
}

/**
 * 在指定元素中初始化組件
 */
function initializeComponentsInElement(element) {
    // 重新初始化工具提示
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        element.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
            new bootstrap.Tooltip(el);
        });
    }
    
    // 重新初始化模態框
    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        element.querySelectorAll('[data-bs-toggle="modal"]').forEach(el => {
            // Modal會自動初始化，不需要手動創建
        });
    }
    
    // 如果有Chart.js圖表，重新調整大小
    if (window.Chart) {
        setTimeout(() => {
            element.querySelectorAll('canvas').forEach(canvas => {
                const chart = Chart.getChart(canvas);
                if (chart) {
                    chart.resize();
                }
            });
        }, 100);
    }
}

/**
 * 公共API
 */
window.TabFixer = {
    fixAllTabs: fixAllTabIssues,
    showTab: function(tabSelector) {
        const tab = document.querySelector(tabSelector);
        if (tab) {
            tab.click();
        }
    },
    loadTabContent: loadTabContentLazy,
    enhanceTabs: enhanceTabFunctionality
};
