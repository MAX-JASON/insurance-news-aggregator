/**
 * 統一標籤分頁管理器
 * Universal Tab Manager for Insurance News Aggregator
 */

class TabManager {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            type: options.type || 'bootstrap', // 'bootstrap', 'pills', 'custom'
            theme: options.theme || 'default',
            animation: options.animation !== false,
            hashNavigation: options.hashNavigation || false,
            onTabChange: options.onTabChange || null,
            lazy: options.lazy || false,
            ...options
        };
        
        this.tabs = [];
        this.activeTab = null;
        this.initialized = false;
        
        this.init();
    }
    
    init() {
        if (!this.container) {
            console.error('TabManager: 找不到容器元素');
            return;
        }
        
        this.createTabStructure();
        this.bindEvents();
        this.setupHashNavigation();
        this.initialized = true;
        
        console.log('TabManager 已初始化');
    }
    
    createTabStructure() {
        // 創建標籤導航結構
        const navClass = this.getNavClass();
        
        this.container.innerHTML = `
            <div class="tab-manager-container">
                <ul class="nav ${navClass}" role="tablist">
                    <!-- 標籤將動態添加到這裡 -->
                </ul>
                <div class="tab-content">
                    <!-- 標籤內容將動態添加到這裡 -->
                </div>
            </div>
        `;
        
        this.navContainer = this.container.querySelector('.nav');
        this.contentContainer = this.container.querySelector('.tab-content');
    }
    
    getNavClass() {
        switch (this.options.type) {
            case 'pills':
                return 'nav-pills';
            case 'tabs':
                return 'nav-tabs';
            case 'vertical':
                return 'nav-pills flex-column';
            case 'custom':
                return `nav-${this.options.theme}`;
            default:
                return 'nav-tabs';
        }
    }
    
    addTab(id, title, content, options = {}) {
        const tab = {
            id,
            title,
            content,
            active: options.active || false,
            icon: options.icon || null,
            badge: options.badge || null,
            disabled: options.disabled || false,
            lazy: options.lazy || this.options.lazy,
            onShow: options.onShow || null,
            onHide: options.onHide || null
        };
        
        this.tabs.push(tab);
        this.renderTab(tab);
        
        if (tab.active && !this.activeTab) {
            this.setActiveTab(id);
        }
        
        return this;
    }
    
    renderTab(tab) {
        // 創建標籤按鈕
        const navItem = document.createElement('li');
        navItem.className = 'nav-item';
        navItem.setAttribute('role', 'presentation');
        
        const navLink = document.createElement('button');
        navLink.className = `nav-link ${tab.active ? 'active' : ''} ${tab.disabled ? 'disabled' : ''}`;
        navLink.id = `${tab.id}-tab`;
        navLink.setAttribute('data-bs-toggle', 'tab');
        navLink.setAttribute('data-bs-target', `#${tab.id}`);
        navLink.setAttribute('type', 'button');
        navLink.setAttribute('role', 'tab');
        navLink.setAttribute('aria-controls', tab.id);
        navLink.setAttribute('aria-selected', tab.active);
        
        if (tab.disabled) {
            navLink.setAttribute('disabled', 'disabled');
        }
        
        // 構建標籤標題內容
        let titleContent = '';
        if (tab.icon) {
            titleContent += `<i class="${tab.icon} me-2"></i>`;
        }
        titleContent += tab.title;
        if (tab.badge) {
            titleContent += ` <span class="badge bg-secondary ms-2">${tab.badge}</span>`;
        }
        
        navLink.innerHTML = titleContent;
        navItem.appendChild(navLink);
        this.navContainer.appendChild(navItem);
        
        // 創建標籤內容
        const tabPane = document.createElement('div');
        tabPane.className = `tab-pane fade ${tab.active ? 'show active' : ''}`;
        tabPane.id = tab.id;
        tabPane.setAttribute('role', 'tabpanel');
        tabPane.setAttribute('aria-labelledby', `${tab.id}-tab`);
        
        if (tab.lazy && !tab.active) {
            // 延遲載入內容
            tabPane.innerHTML = `
                <div class="text-center py-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">載入中...</span>
                    </div>
                </div>
            `;
        } else {
            tabPane.innerHTML = typeof tab.content === 'function' ? tab.content() : tab.content;
        }
        
        this.contentContainer.appendChild(tabPane);
        
        // 為按鈕添加點擊事件
        navLink.addEventListener('click', (e) => {
            e.preventDefault();
            if (!tab.disabled) {
                this.setActiveTab(tab.id);
            }
        });
    }
    
    setActiveTab(id) {
        const tab = this.tabs.find(t => t.id === id);
        if (!tab || tab.disabled) {
            return false;
        }
        
        // 隱藏當前活動標籤
        if (this.activeTab) {
            this.hideTab(this.activeTab.id);
        }
        
        // 顯示新標籤
        this.showTab(id);
        this.activeTab = tab;
        
        // 更新URL hash（如果啟用）
        if (this.options.hashNavigation) {
            window.location.hash = id;
        }
        
        // 觸發全局回調
        if (this.options.onTabChange) {
            this.options.onTabChange(tab);
        }
        
        return true;
    }
    
    showTab(id) {
        const tab = this.tabs.find(t => t.id === id);
        if (!tab) return;
        
        // 更新導航
        const navLink = document.getElementById(`${id}-tab`);
        const tabPane = document.getElementById(id);
        
        if (navLink && tabPane) {
            // 移除所有活動狀態
            this.navContainer.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
                link.setAttribute('aria-selected', 'false');
            });
            
            this.contentContainer.querySelectorAll('.tab-pane').forEach(pane => {
                pane.classList.remove('show', 'active');
            });
            
            // 設置新的活動狀態
            navLink.classList.add('active');
            navLink.setAttribute('aria-selected', 'true');
            
            if (this.options.animation) {
                tabPane.classList.add('fade');
                setTimeout(() => {
                    tabPane.classList.add('show', 'active');
                }, 10);
            } else {
                tabPane.classList.add('show', 'active');
            }
            
            // 延遲載入內容
            if (tab.lazy && tabPane.innerHTML.includes('spinner-border')) {
                this.loadTabContent(tab);
            }
            
            // 觸發標籤顯示回調
            if (tab.onShow) {
                tab.onShow(tab);
            }
        }
    }
    
    hideTab(id) {
        const tab = this.tabs.find(t => t.id === id);
        if (!tab) return;
        
        const navLink = document.getElementById(`${id}-tab`);
        const tabPane = document.getElementById(id);
        
        if (navLink && tabPane) {
            navLink.classList.remove('active');
            navLink.setAttribute('aria-selected', 'false');
            tabPane.classList.remove('show', 'active');
            
            // 觸發標籤隱藏回調
            if (tab.onHide) {
                tab.onHide(tab);
            }
        }
    }
    
    loadTabContent(tab) {
        const tabPane = document.getElementById(tab.id);
        if (!tabPane) return;
        
        try {
            const content = typeof tab.content === 'function' ? tab.content() : tab.content;
            
            if (typeof content === 'string') {
                tabPane.innerHTML = content;
            } else if (content instanceof Promise) {
                content.then(result => {
                    tabPane.innerHTML = result;
                }).catch(error => {
                    tabPane.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            載入內容失敗: ${error.message}
                        </div>
                    `;
                });
            }
        } catch (error) {
            tabPane.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    載入內容時發生錯誤: ${error.message}
                </div>
            `;
        }
    }
    
    removeTab(id) {
        const tabIndex = this.tabs.findIndex(t => t.id === id);
        if (tabIndex === -1) return false;
        
        const tab = this.tabs[tabIndex];
        
        // 如果是活動標籤，切換到其他標籤
        if (this.activeTab && this.activeTab.id === id) {
            const nextTab = this.tabs[tabIndex + 1] || this.tabs[tabIndex - 1];
            if (nextTab) {
                this.setActiveTab(nextTab.id);
            }
        }
        
        // 移除DOM元素
        const navLink = document.getElementById(`${id}-tab`);
        const tabPane = document.getElementById(id);
        
        if (navLink && navLink.parentElement) {
            navLink.parentElement.remove();
        }
        if (tabPane) {
            tabPane.remove();
        }
        
        // 從數組中移除
        this.tabs.splice(tabIndex, 1);
        
        return true;
    }
    
    disableTab(id) {
        const tab = this.tabs.find(t => t.id === id);
        if (!tab) return false;
        
        tab.disabled = true;
        const navLink = document.getElementById(`${id}-tab`);
        if (navLink) {
            navLink.classList.add('disabled');
            navLink.setAttribute('disabled', 'disabled');
        }
        
        return true;
    }
    
    enableTab(id) {
        const tab = this.tabs.find(t => t.id === id);
        if (!tab) return false;
        
        tab.disabled = false;
        const navLink = document.getElementById(`${id}-tab`);
        if (navLink) {
            navLink.classList.remove('disabled');
            navLink.removeAttribute('disabled');
        }
        
        return true;
    }
    
    updateTabBadge(id, badge) {
        const tab = this.tabs.find(t => t.id === id);
        if (!tab) return false;
        
        tab.badge = badge;
        const navLink = document.getElementById(`${id}-tab`);
        if (navLink) {
            const existingBadge = navLink.querySelector('.badge');
            if (existingBadge) {
                existingBadge.textContent = badge;
            } else if (badge) {
                navLink.innerHTML += ` <span class="badge bg-secondary ms-2">${badge}</span>`;
            }
        }
        
        return true;
    }
    
    bindEvents() {
        // 處理鍵盤導航
        this.container.addEventListener('keydown', (e) => {
            if (e.target.classList.contains('nav-link')) {
                switch (e.key) {
                    case 'ArrowLeft':
                    case 'ArrowUp':
                        this.navigateTab(-1);
                        e.preventDefault();
                        break;
                    case 'ArrowRight':
                    case 'ArrowDown':
                        this.navigateTab(1);
                        e.preventDefault();
                        break;
                    case 'Home':
                        this.setActiveTab(this.tabs[0].id);
                        e.preventDefault();
                        break;
                    case 'End':
                        this.setActiveTab(this.tabs[this.tabs.length - 1].id);
                        e.preventDefault();
                        break;
                }
            }
        });
    }
    
    navigateTab(direction) {
        if (!this.activeTab) return;
        
        const currentIndex = this.tabs.findIndex(t => t.id === this.activeTab.id);
        const enabledTabs = this.tabs.filter(t => !t.disabled);
        const currentEnabledIndex = enabledTabs.findIndex(t => t.id === this.activeTab.id);
        
        let nextIndex = currentEnabledIndex + direction;
        if (nextIndex < 0) {
            nextIndex = enabledTabs.length - 1;
        } else if (nextIndex >= enabledTabs.length) {
            nextIndex = 0;
        }
        
        const nextTab = enabledTabs[nextIndex];
        if (nextTab) {
            this.setActiveTab(nextTab.id);
            document.getElementById(`${nextTab.id}-tab`).focus();
        }
    }
    
    setupHashNavigation() {
        if (!this.options.hashNavigation) return;
        
        // 處理初始hash
        const hash = window.location.hash.substring(1);
        if (hash && this.tabs.find(t => t.id === hash)) {
            this.setActiveTab(hash);
        }
        
        // 監聽hash變化
        window.addEventListener('hashchange', () => {
            const newHash = window.location.hash.substring(1);
            if (newHash && this.tabs.find(t => t.id === newHash)) {
                this.setActiveTab(newHash);
            }
        });
    }
    
    getActiveTab() {
        return this.activeTab;
    }
    
    getAllTabs() {
        return [...this.tabs];
    }
    
    destroy() {
        if (this.container) {
            this.container.innerHTML = '';
        }
        this.tabs = [];
        this.activeTab = null;
        this.initialized = false;
    }
}

// 靜態方法：創建簡單標籤管理器
TabManager.createSimple = function(containerId, tabs, options = {}) {
    const manager = new TabManager(containerId, options);
    
    tabs.forEach((tab, index) => {
        manager.addTab(
            tab.id || `tab-${index}`,
            tab.title,
            tab.content,
            {
                active: index === 0,
                icon: tab.icon,
                badge: tab.badge,
                ...tab.options
            }
        );
    });
    
    return manager;
};

// 全局暴露
window.TabManager = TabManager;

// 自動初始化具有特定屬性的元素
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('[data-tab-manager]').forEach(element => {
        const options = JSON.parse(element.getAttribute('data-tab-options') || '{}');
        new TabManager(element.id, options);
    });
});
