/**
 * 瀏覽器錯誤修復和兼容性處理
 * Browser Error Fixes and Compatibility
 */

(function() {
    'use strict';
    
    console.log('🔧 瀏覽器錯誤修復工具已載入');
    
    // 修復Selection API錯誤（通常來自瀏覽器擴展）
    function fixSelectionErrors() {
        const originalGetRangeAt = Selection.prototype.getRangeAt;
        
        Selection.prototype.getRangeAt = function(index) {
            try {
                // 檢查索引是否有效
                if (index < 0 || index >= this.rangeCount) {
                    console.warn('Selection.getRangeAt: 無效的索引', index, '範圍數量:', this.rangeCount);
                    return null;
                }
                return originalGetRangeAt.call(this, index);
            } catch (error) {
                console.warn('Selection.getRangeAt 錯誤已被攔截:', error.message);
                return null;
            }
        };
    }
    
    // 攔截並過濾重複的錯誤消息
    function setupErrorFiltering() {
        const seenErrors = new Set();
        const maxErrorCount = 3;
        
        const originalError = console.error;
        console.error = function(...args) {
            const errorMessage = args.join(' ');
            
            // 過濾已知的擴展錯誤
            if (errorMessage.includes('content.js') && 
                errorMessage.includes('IndexSizeError')) {
                // 只顯示前幾次，避免刷屏
                const errorKey = 'content.js:IndexSizeError';
                const count = seenErrors.get(errorKey) || 0;
                
                if (count < maxErrorCount) {
                    seenErrors.set(errorKey, count + 1);
                    originalError.apply(console, ['[過濾重複錯誤]', ...args]);
                    
                    if (count === maxErrorCount - 1) {
                        originalError.call(console, '⚠️ content.js 錯誤已被過濾，後續相同錯誤將不再顯示');
                    }
                }
                return;
            }
            
            // 其他錯誤正常顯示
            originalError.apply(console, args);
        };
    }
    
    // 修復可能的Modal問題
    function fixModalIssues() {
        // 確保Modal背景點擊關閉功能正常
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('modal')) {
                // 檢查是否應該關閉Modal
                const modal = e.target;
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance && modal.getAttribute('data-bs-backdrop') !== 'static') {
                    modalInstance.hide();
                }
            }
        });
    }
    
    // 添加全局錯誤處理
    function setupGlobalErrorHandler() {
        window.addEventListener('error', function(event) {
            // 過濾已知的擴展錯誤
            if (event.filename && event.filename.includes('content.js')) {
                console.warn('🔧 瀏覽器擴展錯誤已被攔截:', event.message);
                event.preventDefault();
                return false;
            }
        });
        
        window.addEventListener('unhandledrejection', function(event) {
            console.warn('🔧 未處理的Promise拒絕:', event.reason);
        });
    }
    
    // DOM載入完成後執行修復
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            fixSelectionErrors();
            setupErrorFiltering();
            fixModalIssues();
            setupGlobalErrorHandler();
        });
    } else {
        // DOM已經載入完成
        fixSelectionErrors();
        setupErrorFiltering();
        fixModalIssues();
        setupGlobalErrorHandler();
    }
    
    // 為業務員頁面添加特定修復
    if (window.location.pathname.includes('/business')) {
        console.log('🎯 業務員頁面特定修復已啟用');
        
        // 修復智能分類檢視的潛在問題
        function fixCategoryButtons() {
            const categoryButtons = document.querySelectorAll('.category-btn');
            categoryButtons.forEach(button => {
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // 移除其他按鈕的active狀態
                    categoryButtons.forEach(btn => btn.classList.remove('active'));
                    
                    // 添加當前按鈕的active狀態
                    this.classList.add('active');
                    
                    // 觸發篩選事件
                    const category = this.textContent.trim();
                    if (window.businessDashboard && window.businessDashboard.filterByCategory) {
                        window.businessDashboard.filterByCategory(category);
                    }
                });
            });
        }
        
        // 修復全選功能
        function fixSelectAllFunction() {
            const selectAllCheckbox = document.getElementById('selectAll');
            if (selectAllCheckbox) {
                selectAllCheckbox.addEventListener('change', function() {
                    const isChecked = this.checked;
                    const itemCheckboxes = document.querySelectorAll('.news-select, .news-item-checkbox');
                    
                    itemCheckboxes.forEach(checkbox => {
                        checkbox.checked = isChecked;
                        
                        // 觸發change事件
                        const event = new Event('change', { bubbles: true });
                        checkbox.dispatchEvent(event);
                    });
                    
                    console.log('✅ 全選功能已觸發:', isChecked ? '全選' : '取消全選');
                });
            }
        }
        
        // 當頁面載入完成後應用修復
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(() => {
                fixCategoryButtons();
                fixSelectAllFunction();
                console.log('✅ 業務員頁面修復完成');
            }, 500);
        });
    }
    
    console.log('✅ 瀏覽器錯誤修復工具初始化完成');
})();
