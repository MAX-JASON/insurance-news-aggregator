// 用戶偏好設定處理
$(document).ready(function() {
    // 初始化變數
    let userPreferences = {};
    
    // 載入用戶設定
    loadUserPreferences();
    
    // 保存按鈕點擊事件
    $('#savePreferences').on('click', function() {
        saveUserPreferences();
    });
    
    // 重設為默認值按鈕點擊事件
    $('#resetDefaults').on('click', function() {
        if (confirm('確定要將所有設定重設為默認值嗎？')) {
            resetToDefaults();
        }
    });
    
    // 當暗色模式開關切換時
    $('#darkMode').on('change', function() {
        if ($(this).is(':checked')) {
            alert('深色模式功能即將推出，敬請期待！');
            $(this).prop('checked', false);
        }
    });
    
    // 載入用戶偏好設定
    function loadUserPreferences() {
        // 顯示載入中動畫
        showLoading();
        
        // 發送請求獲取用戶設定
        $.ajax({
            url: '/business/api/preferences',
            type: 'GET',
            success: function(response) {
                if (response.status === 'success') {
                    // 儲存設定
                    userPreferences = response.data;
                    
                    // 將設定應用到表單
                    applyPreferencesToForm(userPreferences);
                } else {
                    showError('無法載入設定：' + response.message);
                }
            },
            error: function(xhr, status, error) {
                console.error('載入設定錯誤:', error);
                showError('無法載入設定，請稍後重試');
            },
            complete: function() {
                hideLoading();
            }
        });
    }
    
    // 將設定應用到表單
    function applyPreferencesToForm(preferences) {
        // 顯示設定
        if (preferences.display) {
            $(`input[name="defaultSorting"][value="${preferences.display.defaultSorting || 'importance'}"]`).prop('checked', true);
            $('#itemsPerPage').val(preferences.display.itemsPerPage || 15);
            $(`input[name="summaryLength"][value="${preferences.display.summaryLength || 'medium'}"]`).prop('checked', true);
            $(`input[name="dashboardLayout"][value="${preferences.display.dashboardLayout || 'standard'}"]`).prop('checked', true);
        }
        
        // 通知設定
        if (preferences.notifications) {
            $('#emailNotifications').prop('checked', preferences.notifications.email !== false);
            $(`input[name="notificationFrequency"][value="${preferences.notifications.frequency || 'daily'}"]`).prop('checked', true);
            $('#notify-high-importance').prop('checked', preferences.notifications.highImportance !== false);
            $('#notify-business-opportunities').prop('checked', preferences.notifications.businessOpportunities !== false);
            $('#notify-industry-updates').prop('checked', preferences.notifications.industryUpdates === true);
            $('#notify-regulatory-changes').prop('checked', preferences.notifications.regulatoryChanges !== false);
            $('#notificationLimit').val(preferences.notifications.limit || 3);
        }
        
        // 分類偏好
        if (preferences.categories) {
            // 如果有優先分類設定
            if (preferences.categories.priority) {
                const prioritySelect = $('#priorityCategories');
                preferences.categories.priority.forEach(function(categoryId) {
                    prioritySelect.find(`option[value="${categoryId}"]`).prop('selected', true);
                });
            }
            
            // 如果有忽略分類設定
            if (preferences.categories.ignored) {
                const ignoredSelect = $('#ignoredCategories');
                preferences.categories.ignored.forEach(function(categoryId) {
                    ignoredSelect.find(`option[value="${categoryId}"]`).prop('selected', true);
                });
            }
            
            $('#autoLearnCategories').prop('checked', preferences.categories.autoLearn !== false);
        }
        
        // 數據展示設定
        if (preferences.dataDisplay) {
            $('#stat-importance').prop('checked', preferences.dataDisplay.showImportance !== false);
            $('#stat-trend').prop('checked', preferences.dataDisplay.showTrend !== false);
            $('#stat-category').prop('checked', preferences.dataDisplay.showCategory !== false);
            $('#stat-business').prop('checked', preferences.dataDisplay.showBusiness !== false);
            $('#stat-client').prop('checked', preferences.dataDisplay.showClient === true);
            
            $(`input[name="defaultChartType"][value="${preferences.dataDisplay.chartType || 'bar'}"]`).prop('checked', true);
            $('#showDataLabels').prop('checked', preferences.dataDisplay.showLabels !== false);
            $('#animateCharts').prop('checked', preferences.dataDisplay.animate !== false);
        }
        
        // 分享設定
        if (preferences.sharing) {
            $(`input[name="defaultShareTemplate"][value="${preferences.sharing.template || 'detailed'}"]`).prop('checked', true);
            $('#share-email').prop('checked', preferences.sharing.email !== false);
            $('#share-line').prop('checked', preferences.sharing.line !== false);
            $('#share-wechat').prop('checked', preferences.sharing.wechat === true);
            $('#share-pdf').prop('checked', preferences.sharing.pdf !== false);
            
            if (preferences.sharing.signature) {
                $('#signatureText').val(preferences.sharing.signature);
            }
            
            $('#includeContactInfo').prop('checked', preferences.sharing.includeContactInfo !== false);
        }
    }
    
    // 從表單收集設定
    function collectPreferencesFromForm() {
        const preferences = {
            display: {
                defaultSorting: $('input[name="defaultSorting"]:checked').val(),
                itemsPerPage: parseInt($('#itemsPerPage').val(), 10),
                summaryLength: $('input[name="summaryLength"]:checked').val(),
                dashboardLayout: $('input[name="dashboardLayout"]:checked').val()
            },
            notifications: {
                email: $('#emailNotifications').is(':checked'),
                frequency: $('input[name="notificationFrequency"]:checked').val(),
                highImportance: $('#notify-high-importance').is(':checked'),
                businessOpportunities: $('#notify-business-opportunities').is(':checked'),
                industryUpdates: $('#notify-industry-updates').is(':checked'),
                regulatoryChanges: $('#notify-regulatory-changes').is(':checked'),
                limit: parseInt($('#notificationLimit').val(), 10)
            },
            categories: {
                priority: Array.from($('#priorityCategories option:selected')).map(opt => parseInt($(opt).val(), 10)),
                ignored: Array.from($('#ignoredCategories option:selected')).map(opt => parseInt($(opt).val(), 10)),
                autoLearn: $('#autoLearnCategories').is(':checked')
            },
            dataDisplay: {
                showImportance: $('#stat-importance').is(':checked'),
                showTrend: $('#stat-trend').is(':checked'),
                showCategory: $('#stat-category').is(':checked'),
                showBusiness: $('#stat-business').is(':checked'),
                showClient: $('#stat-client').is(':checked'),
                chartType: $('input[name="defaultChartType"]:checked').val(),
                showLabels: $('#showDataLabels').is(':checked'),
                animate: $('#animateCharts').is(':checked')
            },
            sharing: {
                template: $('input[name="defaultShareTemplate"]:checked').val(),
                email: $('#share-email').is(':checked'),
                line: $('#share-line').is(':checked'),
                wechat: $('#share-wechat').is(':checked'),
                pdf: $('#share-pdf').is(':checked'),
                signature: $('#signatureText').val(),
                includeContactInfo: $('#includeContactInfo').is(':checked')
            }
        };
        
        return preferences;
    }
    
    // 保存用戶偏好設定
    function saveUserPreferences() {
        // 從表單收集設定
        const preferences = collectPreferencesFromForm();
        
        // 顯示載入中動畫
        showLoading();
        
        // 發送保存請求
        $.ajax({
            url: '/business/api/preferences',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ preferences: preferences }),
            success: function(response) {
                if (response.status === 'success') {
                    showSuccess('您的設定已成功保存！');
                    userPreferences = preferences;
                } else {
                    showError('保存設定失敗：' + response.message);
                }
            },
            error: function(xhr, status, error) {
                console.error('保存設定錯誤:', error);
                showError('保存設定失敗，請稍後重試');
            },
            complete: function() {
                hideLoading();
            }
        });
    }
    
    // 重設為默認值
    function resetToDefaults() {
        // 設定默認值
        const defaultPreferences = {
            display: {
                defaultSorting: 'importance',
                itemsPerPage: 15,
                summaryLength: 'medium',
                dashboardLayout: 'standard'
            },
            notifications: {
                email: true,
                frequency: 'daily',
                highImportance: true,
                businessOpportunities: true,
                industryUpdates: false,
                regulatoryChanges: true,
                limit: 3
            },
            categories: {
                priority: [],
                ignored: [],
                autoLearn: true
            },
            dataDisplay: {
                showImportance: true,
                showTrend: true,
                showCategory: true,
                showBusiness: true,
                showClient: false,
                chartType: 'bar',
                showLabels: true,
                animate: true
            },
            sharing: {
                template: 'detailed',
                email: true,
                line: true,
                wechat: false,
                pdf: true,
                signature: '此資訊由您的保險專員提供，如有任何疑問，歡迎隨時聯絡。',
                includeContactInfo: true
            }
        };
        
        // 應用默認設定到表單
        applyPreferencesToForm(defaultPreferences);
        
        // 顯示提示
        showSuccess('已重設為默認值，請點擊儲存以保存設定');
    }
    
    // 顯示成功提示
    function showSuccess(message) {
        $('#saveSuccess').text(message).addClass('show').css('display', 'block');
        setTimeout(function() {
            $('#saveSuccess').removeClass('show');
        }, 3000);
    }
    
    // 顯示錯誤提示
    function showError(message) {
        $('#saveError').text(message).addClass('show').css('display', 'block');
        setTimeout(function() {
            $('#saveError').removeClass('show');
        }, 3000);
    }
    
    // 顯示載入中動畫
    function showLoading() {
        $('#savePreferences').prop('disabled', true).html('<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>處理中...');
    }
    
    // 隱藏載入中動畫
    function hideLoading() {
        $('#savePreferences').prop('disabled', false).html('儲存設定');
    }
});
