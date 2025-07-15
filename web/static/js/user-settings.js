/**
 * 用戶個人設置和偏好管理
 * User Settings and Preferences Management
 */

$(document).ready(function() {
    // 初始化設置
    initUserSettings();
    
    // 綁定設置保存按鈕
    $('#save-user-settings').on('click', function() {
        saveUserSettings();
    });
    
    // 綁定重置設置按鈕
    $('#reset-user-settings').on('click', function() {
        resetUserSettings();
    });
    
    // 綁定主題切換
    $('.theme-option').on('click', function() {
        const theme = $(this).data('theme');
        changeTheme(theme);
    });
    
    // 綁定字體大小調整
    $('#font-size-slider').on('input', function() {
        const size = $(this).val();
        updateFontSize(size);
    });
});

/**
 * 初始化用戶設置
 */
function initUserSettings() {
    try {
        // 讀取保存的設置
        const savedSettings = localStorage.getItem('userSettings');
        if (savedSettings) {
            const settings = JSON.parse(savedSettings);
            
            // 應用設置到UI
            applyUserSettings(settings);
            
            // 設置控件狀態
            updateSettingControls(settings);
            
            console.log('用戶設置已載入', settings);
        } else {
            // 使用預設設置
            const defaultSettings = {
                theme: 'light',
                fontSize: 16,
                dashboardLayout: 'grid',
                notificationsEnabled: true,
                autoRefresh: false,
                refreshInterval: 5,
                compactView: false
            };
            
            // 保存默認設置
            localStorage.setItem('userSettings', JSON.stringify(defaultSettings));
            
            // 應用默認設置
            applyUserSettings(defaultSettings);
            
            // 設置控件狀態
            updateSettingControls(defaultSettings);
            
            console.log('已應用默認用戶設置');
        }
    } catch (error) {
        console.error('初始化用戶設置時出錯:', error);
        if (window.businessTools && window.businessTools.showToast) {
            window.businessTools.showToast('載入偏好設置時出錯，已使用系統預設值', 'warning');
        }
    }
}

/**
 * 應用用戶設置到UI
 */
function applyUserSettings(settings) {
    try {
        // 應用主題
        changeTheme(settings.theme);
        
        // 應用字體大小
        updateFontSize(settings.fontSize);
        
        // 應用儀表板布局
        if ($('#business-dashboard').length > 0) {
            const layoutClass = settings.dashboardLayout === 'grid' ? 'grid-layout' : 'list-layout';
            $('#business-dashboard').removeClass('grid-layout list-layout').addClass(layoutClass);
        }
        
        // 應用通知設置
        if (!settings.notificationsEnabled) {
            // 禁用通知的代碼...
        }
        
        // 應用自動刷新設置
        if (settings.autoRefresh) {
            setupAutoRefresh(settings.refreshInterval);
        }
        
        // 應用緊湊視圖
        if (settings.compactView) {
            $('body').addClass('compact-view');
        } else {
            $('body').removeClass('compact-view');
        }
    } catch (error) {
        console.error('應用用戶設置時出錯:', error);
    }
}

/**
 * 更新設置控件狀態
 */
function updateSettingControls(settings) {
    try {
        // 設置主題選擇
        $('.theme-option').removeClass('active');
        $(`.theme-option[data-theme="${settings.theme}"]`).addClass('active');
        
        // 設置字體大小滑塊
        $('#font-size-slider').val(settings.fontSize);
        
        // 設置儀表板布局選擇
        $('input[name="dashboard-layout"]').prop('checked', false);
        $(`input[name="dashboard-layout"][value="${settings.dashboardLayout}"]`).prop('checked', true);
        
        // 設置通知開關
        $('#notifications-toggle').prop('checked', settings.notificationsEnabled);
        
        // 設置自動刷新開關和間隔
        $('#auto-refresh-toggle').prop('checked', settings.autoRefresh);
        $('#refresh-interval').val(settings.refreshInterval);
        
        // 設置緊湊視圖開關
        $('#compact-view-toggle').prop('checked', settings.compactView);
    } catch (error) {
        console.error('更新設置控件狀態時出錯:', error);
    }
}

/**
 * 保存用戶設置
 */
function saveUserSettings() {
    try {
        // 讀取所有設置值
        const settings = {
            theme: $('.theme-option.active').data('theme') || 'light',
            fontSize: parseInt($('#font-size-slider').val()) || 16,
            dashboardLayout: $('input[name="dashboard-layout"]:checked').val() || 'grid',
            notificationsEnabled: $('#notifications-toggle').prop('checked'),
            autoRefresh: $('#auto-refresh-toggle').prop('checked'),
            refreshInterval: parseInt($('#refresh-interval').val()) || 5,
            compactView: $('#compact-view-toggle').prop('checked')
        };
        
        // 保存設置
        localStorage.setItem('userSettings', JSON.stringify(settings));
        
        // 應用設置
        applyUserSettings(settings);
        
        // 顯示成功通知
        if (window.businessTools && window.businessTools.showToast) {
            window.businessTools.showToast('您的偏好設置已保存並應用', 'success');
        }
        
        console.log('用戶設置已保存', settings);
    } catch (error) {
        console.error('保存用戶設置時出錯:', error);
        
        if (window.businessTools && window.businessTools.showToast) {
            window.businessTools.showToast('保存偏好設置時出錯，請重試', 'error');
        }
    }
}

/**
 * 重置用戶設置為默認值
 */
function resetUserSettings() {
    try {
        // 確認重置
        if (confirm('確定要將所有設置重置為預設值嗎？')) {
            // 刪除保存的設置
            localStorage.removeItem('userSettings');
            
            // 重新初始化設置
            initUserSettings();
            
            // 顯示成功通知
            if (window.businessTools && window.businessTools.showToast) {
                window.businessTools.showToast('所有設置已重置為預設值', 'info');
            }
        }
    } catch (error) {
        console.error('重置用戶設置時出錯:', error);
        
        if (window.businessTools && window.businessTools.showToast) {
            window.businessTools.showToast('重置設置時出錯，請重試', 'error');
        }
    }
}

/**
 * 切換主題
 */
function changeTheme(theme) {
    try {
        const body = $('body');
        
        // 移除所有主題類
        body.removeClass('theme-light theme-dark theme-blue theme-professional');
        
        // 添加選定的主題類
        body.addClass('theme-' + theme);
        
        // 更新活動主題選項
        $('.theme-option').removeClass('active');
        $(`.theme-option[data-theme="${theme}"]`).addClass('active');
        
        // 更新本地存儲中的主題設置
        updateStoredSetting('theme', theme);
        
        console.log('主題已切換為:', theme);
    } catch (error) {
        console.error('切換主題時出錯:', error);
    }
}

/**
 * 更新字體大小
 */
function updateFontSize(size) {
    try {
        // 設置根元素字體大小
        document.documentElement.style.fontSize = size + 'px';
        
        // 更新顯示的大小值
        $('#font-size-value').text(size + 'px');
        
        // 更新本地存儲中的字體大小設置
        updateStoredSetting('fontSize', parseInt(size));
        
        console.log('字體大小已更新為:', size + 'px');
    } catch (error) {
        console.error('更新字體大小時出錯:', error);
    }
}

/**
 * 設置自動刷新
 */
function setupAutoRefresh(interval) {
    try {
        // 清除現有的刷新計時器
        if (window.autoRefreshTimer) {
            clearInterval(window.autoRefreshTimer);
        }
        
        // 設置新的刷新計時器
        const minutes = parseInt(interval) || 5;
        const milliseconds = minutes * 60 * 1000;
        
        window.autoRefreshTimer = setInterval(function() {
            // 根據頁面類型執行不同的刷新操作
            if ($('#news-list').length > 0) {
                // 刷新新聞列表
                refreshNewsList();
            } else if ($('#business-dashboard').length > 0) {
                // 刷新儀表板數據
                refreshDashboard();
            }
            
            console.log('頁面已自動刷新，下次刷新將在', minutes, '分鐘後進行');
        }, milliseconds);
        
        console.log('自動刷新已設置，間隔:', minutes, '分鐘');
    } catch (error) {
        console.error('設置自動刷新時出錯:', error);
    }
}

/**
 * 刷新新聞列表
 */
function refreshNewsList() {
    try {
        // 這裡可以使用頁面中已有的刷新函數
        if (typeof loadNews === 'function') {
            loadNews();
            
            // 顯示刷新通知
            if (window.businessTools && window.businessTools.showToast) {
                window.businessTools.showToast('新聞列表已刷新', 'info');
            }
        }
    } catch (error) {
        console.error('刷新新聞列表時出錯:', error);
    }
}

/**
 * 刷新儀表板
 */
function refreshDashboard() {
    try {
        // 這裡可以使用頁面中已有的刷新函數
        if (typeof loadDashboardData === 'function') {
            loadDashboardData();
            
            // 顯示刷新通知
            if (window.businessTools && window.businessTools.showToast) {
                window.businessTools.showToast('儀表板數據已刷新', 'info');
            }
        }
    } catch (error) {
        console.error('刷新儀表板時出錯:', error);
    }
}

/**
 * 更新本地存儲中的單個設置
 */
function updateStoredSetting(key, value) {
    try {
        // 讀取當前設置
        const savedSettings = localStorage.getItem('userSettings');
        if (savedSettings) {
            const settings = JSON.parse(savedSettings);
            
            // 更新設置
            settings[key] = value;
            
            // 保存更新後的設置
            localStorage.setItem('userSettings', JSON.stringify(settings));
        }
    } catch (error) {
        console.error('更新存儲設置時出錯:', error, key, value);
    }
}
