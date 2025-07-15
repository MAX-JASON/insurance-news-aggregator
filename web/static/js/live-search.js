// 即時搜索功能
$(document).ready(function() {
    // 初始化搜索相關變數
    let searchTimer = null;
    let lastSearchTerm = '';
    const minSearchLength = 2;
    const searchDelay = 300; // 毫秒
    
    // 建立本地快取數據 - 用於API故障時的備用
    let cachedNewsItems = [];
    
    // 預先載入一些新聞數據供本地搜索使用
    loadSampleNewsData();
    
    // 即時搜索輸入框事件處理
    $('#liveSearch').on('input', function() {
        const searchTerm = $(this).val().trim();
        
        // 如果搜索詞太短，清空結果並返回
        if (searchTerm.length < minSearchLength) {
            $('#searchResults').empty().hide();
            return;
        }
        
        // 如果與上次相同且不為空，不重複處理
        if (searchTerm === lastSearchTerm && searchTerm !== '') {
            return;
        }
        
        // 清除之前的定時器
        if (searchTimer) {
            clearTimeout(searchTimer);
        }
        
        // 顯示加載指示器
        $('#searchSpinner').show();
        
        // 設定延遲執行搜索，避免每次按鍵都發送請求
        searchTimer = setTimeout(function() {
            // 更新上次搜索詞
            lastSearchTerm = searchTerm;
            
            // 設置請求超時
            const timeoutPromise = new Promise((_, reject) => {
                setTimeout(() => reject(new Error('請求超時')), 3000);
            });
            
            // 實際API請求
            const fetchPromise = new Promise((resolve, reject) => {
                $.ajax({
                    url: '/business/api/search',
                    type: 'GET',
                    data: { term: searchTerm },
                    success: function(response) {
                        resolve(response.data);
                    },
                    error: function(xhr, status, error) {
                        reject(new Error(error));
                    }
                });
            });
            
            // 隱藏加載指示器並使用Promise.race來處理可能的超時
            Promise.race([fetchPromise, timeoutPromise])
                .then(data => {
                    $('#searchSpinner').hide();
                    // 將API返回的數據添加到本地快取中
                    if (data && data.length > 0) {
                        updateCachedNewsItems(data);
                    }
                    // 顯示搜索結果
                    displaySearchResults(data);
                })
                .catch(error => {
                    $('#searchSpinner').hide();
                    console.warn('API搜索失敗，使用本地搜索:', error);
                    
                    // 使用本地搜索作為備用
                    const localResults = performLocalSearch(searchTerm);
                    displaySearchResults(localResults);
                });
        }, searchDelay);
    });
    
    // 處理搜索結果清除
    $('#clearSearch').click(function() {
        $('#liveSearch').val('');
        $('#searchResults').empty().hide();
        lastSearchTerm = '';
    });
    
    // 本地搜索函數
    function performLocalSearch(term) {
        if (!term || cachedNewsItems.length === 0) return [];
        
        const searchTermLower = term.toLowerCase();
        
        return cachedNewsItems.filter(news => {
            // 檢查標題、摘要和來源是否包含搜索詞
            const titleMatch = news.title && news.title.toLowerCase().includes(searchTermLower);
            const summaryMatch = news.summary && news.summary.toLowerCase().includes(searchTermLower);
            const sourceMatch = news.source_name && news.source_name.toLowerCase().includes(searchTermLower);
            
            return titleMatch || summaryMatch || sourceMatch;
        });
    }
    
    // 載入示例新聞數據
    function loadSampleNewsData() {
        // 從頁面上已有的新聞卡片收集數據
        const newsCards = document.querySelectorAll('.news-card, .priority-news, .news-item');
        
        if (newsCards.length > 0) {
            newsCards.forEach(card => {
                const title = card.querySelector('h6, .card-title')?.innerText.trim();
                const summary = card.querySelector('.card-text, p.text-muted')?.innerText.trim();
                const sourceElem = card.querySelector('.badge, small:contains("來源")');
                const source = sourceElem ? sourceElem.innerText.trim() : '未知來源';
                
                if (title) {
                    cachedNewsItems.push({
                        id: card.dataset.newsId || Date.now() + Math.random().toString(36).substr(2, 5),
                        title: title,
                        summary: summary || title,
                        source_name: source,
                        importance_score: Math.random(),
                        published_date: new Date().toISOString()
                    });
                }
            });
        }
        
        // 如果頁面上沒有找到，則添加一些預設數據
        if (cachedNewsItems.length === 0) {
            const sampleData = [
                {
                    id: 1,
                    title: '數位理賠新制度上路，客戶申請更便民',
                    summary: '影響分析：所有客戶都會詢問，建議主動說明新流程',
                    source_name: '金管會公告',
                    importance_score: 0.9,
                    published_date: '2025-07-01T10:00:00Z'
                },
                {
                    id: 2,
                    title: '長照保險需求調查：8成民眾有投保意願',
                    summary: '影響分析：長照商品推廣的最佳時機',
                    source_name: '保險日報',
                    importance_score: 0.75,
                    published_date: '2025-06-29T10:00:00Z'
                },
                {
                    id: 3,
                    title: '金管會發布新投資型保單規範',
                    summary: '影響分析：需要向客戶說明新規範對既有保單的影響',
                    source_name: '金融監督管理委員會',
                    importance_score: 0.65,
                    published_date: '2025-06-28T10:00:00Z'
                },
                {
                    id: 4,
                    title: 'ESG投資型保單成為市場新寵',
                    summary: '永續投資概念受到年輕族群青睞，結合保障與ESG投資功能的保單銷售成長',
                    source_name: '財經日報',
                    importance_score: 0.5,
                    published_date: '2025-06-25T10:00:00Z'
                },
                {
                    id: 5,
                    title: '保險科技新創募資達10億',
                    summary: '國內保險科技新創公司宣佈完成10億元募資，將用於開發AI理賠系統',
                    source_name: '科技新報',
                    importance_score: 0.3,
                    published_date: '2025-06-20T10:00:00Z'
                }
            ];
            
            cachedNewsItems = sampleData;
        }
        
        console.log(`已載入 ${cachedNewsItems.length} 筆本地快取新聞數據`);
    }
    
    // 更新本地快取數據
    function updateCachedNewsItems(newItems) {
        if (!newItems || newItems.length === 0) return;
        
        // 將新數據添加到快取中，避免重複
        newItems.forEach(newItem => {
            const existingIndex = cachedNewsItems.findIndex(item => item.id === newItem.id);
            if (existingIndex >= 0) {
                // 更新現有項目
                cachedNewsItems[existingIndex] = { ...cachedNewsItems[existingIndex], ...newItem };
            } else {
                // 添加新項目
                cachedNewsItems.push(newItem);
            }
        });
        
        // 限制快取大小
        if (cachedNewsItems.length > 100) {
            cachedNewsItems = cachedNewsItems.slice(-100);
        }
    }
    
    // 顯示搜索結果函數
    function displaySearchResults(results) {
        const $resultsContainer = $('#searchResults');
        
        // 清空結果容器
        $resultsContainer.empty();
        
        // 如果沒有結果
        if (!results || results.length === 0) {
            $resultsContainer.html(`
                <div class="text-center py-4">
                    <i class="fas fa-search fa-2x text-muted mb-2"></i>
                    <p class="text-muted">沒有找到相符的結果</p>
                </div>
            `);
            $resultsContainer.show();
            return;
        }
        
        // 建立結果列表
        let resultsHTML = '<div class="list-group">';
        
        // 遍歷結果
        results.forEach(function(news) {
            // 決定重要性標記樣式
            let importanceClass = '';
            let importanceText = '';
            
            if (!news.importance_score) {
                news.importance_score = 0.5; // 預設值
            }
            
            if (news.importance_score >= 0.7) {
                importanceClass = 'bg-danger';
                importanceText = '高重要性';
            } else if (news.importance_score >= 0.4) {
                importanceClass = 'bg-warning text-dark';
                importanceText = '中重要性';
            } else {
                importanceClass = 'bg-info text-white';
                importanceText = '低重要性';
            }
            
            // 格式化日期
            let publishDate = '未知日期';
            if (news.published_date) {
                try {
                    publishDate = new Date(news.published_date).toLocaleDateString();
                } catch (e) {
                    console.warn('日期格式化失敗:', e);
                }
            }
            
            // 確保有摘要，並限制長度
            const summary = news.summary 
                ? (news.summary.length > 100 ? news.summary.substring(0, 100) + '...' : news.summary) 
                : '無摘要';
            
            // 添加結果項目
            resultsHTML += `
                <a href="/news/${news.id}" class="list-group-item list-group-item-action">
                    <div class="d-flex justify-content-between align-items-start">
                        <h6 class="mb-1">${news.title}</h6>
                        <span class="badge ${importanceClass}">${importanceText}</span>
                    </div>
                    <p class="mb-1 small text-muted">${summary}</p>
                    <div class="d-flex justify-content-between align-items-center small">
                        <span>${news.source_name || '未知來源'}</span>
                        <span>${publishDate}</span>
                    </div>
                </a>
            `;
        });
        
        resultsHTML += '</div>';
        
        // 添加結果數量標記和動作按鈕
        const resultsHeader = `
            <div class="d-flex justify-content-between align-items-center mb-3">
                <span class="text-muted">找到 ${results.length} 筆結果</span>
                <div>
                    <a href="/business/search?term=${encodeURIComponent(lastSearchTerm)}" class="btn btn-sm btn-outline-primary">
                        進階搜索
                    </a>
                </div>
            </div>
        `;
        
        // 顯示結果
        $resultsContainer.html(resultsHeader + resultsHTML);
        
        // 顯示結果容器
        $resultsContainer.show();
    }
});
