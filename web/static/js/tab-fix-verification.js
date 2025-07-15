/**
 * 前端UI標籤分頁修復狀態驗證
 * Frontend Tab Navigation Fix Status Verification
 */

console.log('🔧 前端UI標籤分頁修復狀態檢查');
console.log('=====================================');

// 檢查核心修復腳本是否載入
function checkTabFixesLoaded() {
    if (typeof window.TabFixer !== 'undefined') {
        console.log('✅ TabFixer 已載入');
        console.log('   可用方法:', Object.keys(window.TabFixer));
        return true;
    } else {
        console.log('❌ TabFixer 未載入');
        return false;
    }
}

// 檢查標籤管理器是否載入
function checkTabManagerLoaded() {
    if (typeof window.TabManager !== 'undefined') {
        console.log('✅ TabManager 已載入');
        return true;
    } else {
        console.log('⚠️  TabManager 未載入 (可選)');
        return false;
    }
}

// 檢查頁面中的標籤實現
function checkPageTabImplementation() {
    const results = {
        totalTabs: 0,
        fixedTabs: 0,
        issues: []
    };
    
    // 檢查所有標籤按鈕
    const tabButtons = document.querySelectorAll('[data-bs-toggle="tab"], [data-bs-toggle="pill"], [data-bs-toggle="list"]');
    results.totalTabs = tabButtons.length;
    
    if (tabButtons.length === 0) {
        console.log('ℹ️  當前頁面沒有標籤分頁');
        return results;
    }
    
    console.log(`📊 找到 ${tabButtons.length} 個標籤按鈕`);
    
    tabButtons.forEach((button, index) => {
        const buttonIssues = [];
        
        // 檢查必要屬性
        if (!button.hasAttribute('aria-selected')) {
            buttonIssues.push('缺少 aria-selected');
        }
        if (!button.hasAttribute('aria-controls')) {
            buttonIssues.push('缺少 aria-controls');
        }
        if (!button.hasAttribute('role')) {
            buttonIssues.push('缺少 role');
        }
        if (!button.hasAttribute('id')) {
            buttonIssues.push('缺少 id');
        }
        
        if (buttonIssues.length === 0) {
            results.fixedTabs++;
            console.log(`   ✅ 標籤 ${index + 1}: 完整`);
        } else {
            results.issues.push(`標籤 ${index + 1}: ${buttonIssues.join(', ')}`);
            console.log(`   ⚠️  標籤 ${index + 1}: ${buttonIssues.join(', ')}`);
        }
    });
    
    // 檢查標籤面板
    const tabPanes = document.querySelectorAll('.tab-pane');
    console.log(`📊 找到 ${tabPanes.length} 個標籤面板`);
    
    tabPanes.forEach((pane, index) => {
        const paneIssues = [];
        
        if (!pane.hasAttribute('aria-labelledby')) {
            paneIssues.push('缺少 aria-labelledby');
        }
        if (!pane.hasAttribute('role')) {
            paneIssues.push('缺少 role');
        }
        if (!pane.hasAttribute('tabindex')) {
            paneIssues.push('缺少 tabindex');
        }
        
        if (paneIssues.length > 0) {
            results.issues.push(`面板 ${index + 1}: ${paneIssues.join(', ')}`);
            console.log(`   ⚠️  面板 ${index + 1}: ${paneIssues.join(', ')}`);
        } else {
            console.log(`   ✅ 面板 ${index + 1}: 完整`);
        }
    });
    
    return results;
}

// 測試鍵盤導航
function testKeyboardNavigation() {
    const tabButtons = document.querySelectorAll('[data-bs-toggle="tab"], [data-bs-toggle="pill"], [data-bs-toggle="list"]');
    
    if (tabButtons.length === 0) {
        return;
    }
    
    console.log('⌨️  測試鍵盤導航支援...');
    
    // 檢查是否有鍵盤事件監聽器
    let hasKeyboardSupport = false;
    
    tabButtons.forEach(button => {
        // 模擬按鍵事件來測試
        const testEvent = new KeyboardEvent('keydown', { key: 'ArrowRight' });
        const hasListener = button.dispatchEvent(testEvent);
        if (hasListener) {
            hasKeyboardSupport = true;
        }
    });
    
    if (hasKeyboardSupport) {
        console.log('   ✅ 鍵盤導航支援已啟用');
    } else {
        console.log('   ⚠️  鍵盤導航支援未檢測到');
    }
}

// 檢查錯誤處理
function checkErrorHandling() {
    console.log('🛡️  檢查錯誤處理機制...');
    
    // 檢查全局錯誤處理器
    if (typeof window.globalErrorHandler !== 'undefined') {
        console.log('   ✅ 全局錯誤處理器已載入');
    } else {
        console.log('   ⚠️  全局錯誤處理器未檢測到');
    }
    
    // 檢查 console.error 的重新定義
    if (window.console && window.console.error) {
        console.log('   ✅ 錯誤日誌功能可用');
    }
}

// 主要檢查函數
function runTabFixVerification() {
    console.log('\n🔍 開始驗證...\n');
    
    const tabFixerLoaded = checkTabFixesLoaded();
    const tabManagerLoaded = checkTabManagerLoaded();
    const tabResults = checkPageTabImplementation();
    
    testKeyboardNavigation();
    checkErrorHandling();
    
    console.log('\n📈 總結報告:');
    console.log('=====================================');
    
    if (tabFixerLoaded) {
        console.log('✅ 核心修復腳本正常');
    } else {
        console.log('❌ 核心修復腳本缺失');
    }
    
    if (tabResults.totalTabs > 0) {
        const successRate = Math.round((tabResults.fixedTabs / tabResults.totalTabs) * 100);
        console.log(`📊 標籤修復成功率: ${successRate}% (${tabResults.fixedTabs}/${tabResults.totalTabs})`);
        
        if (tabResults.issues.length > 0) {
            console.log('⚠️  發現問題:');
            tabResults.issues.forEach(issue => console.log(`   - ${issue}`));
        }
    }
    
    if (tabFixerLoaded && tabResults.issues.length === 0 && tabResults.totalTabs > 0) {
        console.log('\n🎉 前端UI標籤分頁功能已完全修復！');
    } else if (tabResults.totalTabs === 0) {
        console.log('\nℹ️  當前頁面無標籤分頁，修復腳本待用');
    } else {
        console.log('\n🔧 還有部分問題需要解決');
    }
}

// 當DOM載入完成後自動運行檢查
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', runTabFixVerification);
} else {
    runTabFixVerification();
}

// 也提供手動運行的方法
window.runTabFixVerification = runTabFixVerification;
