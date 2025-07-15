// 添加賽博朋克爬蟲啟動功能
$(document).ready(function() {
    // 綁定爬蟲啟動按鈕
    $('.crawler-start-btn, .cyber-crawler-btn').on('click', function(e) {
        e.preventDefault();
        
        // 顯示賽博朋克風格的加載動畫
        showCyberLoading('🤖 正在啟動賽博朋克爬蟲...');
        
        // 發送API請求啟動爬蟲
        $.ajax({
            url: '/api/v1/crawler/start',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                use_mock: true,
                sources: []
            }),
            success: function(response) {
                console.log('爬蟲啟動成功', response);
                showCyberSuccess(response.message || '爬蟲任務已啟動');
                
                // 顯示任務ID
                $('#taskId').text(response.task_id || '未知');
                
                // 延遲後刷新頁面上的數據
                setTimeout(function() {
                    refreshNewsData();
                }, 6000);
            },
            error: function(xhr) {
                console.error('爬蟲啟動失敗', xhr);
                let errorMsg = '啟動爬蟲失敗';
                try {
                    const resp = JSON.parse(xhr.responseText);
                    if (resp.message) {
                        errorMsg = resp.message;
                    }
                } catch (e) {}
                
                showCyberError(errorMsg);
            },
            complete: function() {
                // 5秒後隱藏加載動畫
                setTimeout(function() {
                    hideCyberLoading();
                }, 5000);
            }
        });
    });
    
    // 刷新新聞數據
    function refreshNewsData() {
        // 這裡可以添加刷新頁面上的新聞列表的代碼
        // 如果有相關元素的話
        if ($('#newsList').length > 0) {
            // 顯示微加載動畫
            $('#newsList').prepend('<div class="cyber-loader">載入中...</div>');
            
            // 獲取新的新聞數據
            $.get('/api/cyber-news', function(data) {
                if (data.status === 'success' && data.data) {
                    // 清空並重新填充新聞列表
                    $('.cyber-loader').remove();
                    // 這裡需要根據實際的數據結構和UI設計來實現
                    console.log('新聞數據已更新', data);
                }
            });
        }
    }
    
    // 賽博朋克風格的UI通知函數
    function showCyberLoading(message) {
        if ($('.cyber-notification').length > 0) {
            $('.cyber-notification').remove();
        }
        
        $('body').append(`
            <div class="cyber-notification cyber-loading">
                <div class="cyber-notification-content">
                    <div class="cyber-spinner"></div>
                    <div class="cyber-notification-message">${message}</div>
                </div>
            </div>
        `);
    }
    
    function showCyberSuccess(message) {
        if ($('.cyber-notification').length > 0) {
            $('.cyber-notification').remove();
        }
        
        $('body').append(`
            <div class="cyber-notification cyber-success">
                <div class="cyber-notification-content">
                    <i class="fas fa-check-circle"></i>
                    <div class="cyber-notification-message">${message}</div>
                </div>
            </div>
        `);
        
        setTimeout(function() {
            $('.cyber-notification').fadeOut();
        }, 5000);
    }
    
    function showCyberError(message) {
        if ($('.cyber-notification').length > 0) {
            $('.cyber-notification').remove();
        }
        
        $('body').append(`
            <div class="cyber-notification cyber-error">
                <div class="cyber-notification-content">
                    <i class="fas fa-exclamation-circle"></i>
                    <div class="cyber-notification-message">${message}</div>
                </div>
            </div>
        `);
        
        setTimeout(function() {
            $('.cyber-notification').fadeOut();
        }, 7000);
    }
    
    function hideCyberLoading() {
        $('.cyber-notification.cyber-loading').fadeOut();
    }
    
    // 添加賽博朋克風格通知的CSS
    $('head').append(`
        <style>
        .cyber-notification {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            padding: 15px;
            border-radius: 5px;
            background: rgba(18, 24, 38, 0.9);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 212, 255, 0.5);
            box-shadow: 0 0 15px rgba(0, 212, 255, 0.5);
            color: white;
            font-family: 'Courier New', monospace;
            max-width: 350px;
            animation: cyber-glow 2s ease-in-out infinite;
        }
        
        .cyber-notification-content {
            display: flex;
            align-items: center;
        }
        
        .cyber-spinner {
            width: 24px;
            height: 24px;
            border: 3px solid rgba(0, 212, 255, 0.3);
            border-radius: 50%;
            border-top-color: rgba(0, 212, 255, 1);
            animation: cyber-spin 1s linear infinite;
            margin-right: 15px;
        }
        
        .cyber-notification i {
            font-size: 24px;
            margin-right: 15px;
        }
        
        .cyber-success {
            border-color: rgba(57, 255, 20, 0.7);
            box-shadow: 0 0 15px rgba(57, 255, 20, 0.5);
        }
        
        .cyber-success i {
            color: rgba(57, 255, 20, 1);
        }
        
        .cyber-error {
            border-color: rgba(255, 7, 58, 0.7);
            box-shadow: 0 0 15px rgba(255, 7, 58, 0.5);
        }
        
        .cyber-error i {
            color: rgba(255, 7, 58, 1);
        }
        
        @keyframes cyber-spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @keyframes cyber-glow {
            0%, 100% { box-shadow: 0 0 15px rgba(0, 212, 255, 0.5); }
            50% { box-shadow: 0 0 25px rgba(0, 212, 255, 0.8); }
        }
        </style>
    `);
});
