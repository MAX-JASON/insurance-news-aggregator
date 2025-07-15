/**
 * 智能分類檢視按鈕功能
 * Category Classification View Button Functionality
 */

// 當文檔載入完成後執行
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 初始化智能分類檢視按鈕功能');
    
    // 延遲初始化以確保所有元素都已載入
    setTimeout(() => {
        initCategoryButtons();
        loadCategoryStats(); // 載入分類統計數據
    }, 100);
});

/**
 * 載入分類統計數據
 */
function loadCategoryStats() {
    console.log('📊 開始載入分類統計數據...');
    
    fetch('/business/api/category-stats')
        .then(response => {
            if (!response.ok) {
                throw new Error(`API回應錯誤: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('✅ API回應:', data);
            if (data.stats) {
                updateCategoryStatsDisplay(data.stats);
                console.log('✅ 分類統計數據載入成功:', data.stats);
            } else {
                throw new Error('API返回數據格式錯誤');
            }
        })
        .catch(error => {
            console.error('❌ 載入分類統計數據失敗:', error);
            // 使用備用數據
            const fallbackStats = {
                '客戶關注': {
                    '理賠案例': 8,
                    '保費調整': 5,
                    '法規變動': 3
                },
                '公司動態': {
                    '新商品發布': 4,
                    '通路政策': 2,
                    '獲獎消息': 1
                },
                '市場分析': {
                    '保費趨勢': 6,
                    '競爭分析': 3,
                    '客群變化': 2
                }
            };
            updateCategoryStatsDisplay(fallbackStats);
        });
}

/**
 * 更新分類統計顯示
 * @param {Object} stats - 統計數據對象
 */
function updateCategoryStatsDisplay(stats) {
    for (const [group, categories] of Object.entries(stats)) {
        for (const [category, count] of Object.entries(categories)) {
            const countElement = document.getElementById(`count-${category}`);
            if (countElement) {
                countElement.textContent = count;
                // 根據數量設置不同的樣式
                if (count > 5) {
                    countElement.className = 'badge bg-danger';
                } else if (count > 2) {
                    countElement.className = 'badge bg-warning';
                } else if (count > 0) {
                    countElement.className = 'badge bg-info';
                } else {
                    countElement.className = 'badge bg-secondary';
                }
            }
        }
    }
}

/**
 * 初始化所有分類按鈕
 */
function initCategoryButtons() {
    // 獲取所有分類項目
    const categoryItems = document.querySelectorAll('.category-item');
    const viewAllButtons = document.querySelectorAll('.view-all-btn');
    
    // 為分類項目添加點擊事件
    if (categoryItems.length > 0) {
        categoryItems.forEach(item => {
            item.addEventListener('click', function(event) {
                handleCategoryItemClick(event.currentTarget);
            });
            // 添加懸停效果
            item.style.cursor = 'pointer';
        });
        console.log(`已為 ${categoryItems.length} 個分類項目添加點擊事件`);
    } else {
        console.warn('未找到任何分類項目');
    }
    
    // 為「查看全部」按鈕添加點擊事件
    if (viewAllButtons.length > 0) {
        viewAllButtons.forEach(button => {
            button.addEventListener('click', function(event) {
                handleViewAllClick(event.currentTarget);
            });
        });
        console.log(`已為 ${viewAllButtons.length} 個「查看全部」按鈕添加點擊事件`);
    } else {
        console.warn('未找到任何「查看全部」按鈕');
    }
}

/**
 * 處理分類項目點擊
 * @param {HTMLElement} item - 被點擊的項目元素
 */
function handleCategoryItemClick(item) {
    // 獲取分類項目的類型和名稱
    const categoryText = item.getAttribute('data-category');
    const categoryCount = item.querySelector('.badge')?.textContent || '0';
    
    // 從父元素獲取分類組
    const categoryCard = item.closest('.card');
    const categoryGroup = categoryCard ? categoryCard.querySelector('.card-header h6')?.textContent.replace(/^\s*[\w\s]*\s*/, '').trim() : '未知分類';
    
    console.log(`分類點擊: ${categoryGroup} > ${categoryText}, 數量: ${categoryCount}`);
    
    // 顯示載入指示器
    showLoadingSpinner();
    
    // 嘗試獲取相關的新聞
    fetchCategoryNews(categoryGroup, categoryText)
        .then(data => {
            // 更新UI顯示結果
            updateNewsList(data, `${categoryGroup}: ${categoryText}`, categoryCount);
        })
        .catch(error => {
            console.error('獲取分類新聞失敗:', error);
            showToast(`無法載入「${categoryText}」相關新聞，請稍後再試`, 'error');
        })
        .finally(() => {
            hideLoadingSpinner();
        });
}

/**
 * 處理「查看全部」按鈕點擊
 * @param {HTMLElement} button - 被點擊的按鈕元素
 */
function handleViewAllClick(button) {
    // 從按鈕的data屬性獲取分類組
    const categoryGroup = button.getAttribute('data-group');
    
    console.log(`查看全部點擊: ${categoryGroup}`);
    
    // 顯示載入指示器
    showLoadingSpinner();
    
    // 嘗試獲取該分類組的所有新聞
    fetchCategoryGroupNews(categoryGroup)
        .then(data => {
            // 更新UI顯示結果
            updateNewsList(data, categoryGroup, data.length);
        })
        .catch(error => {
            console.error('獲取分類組新聞失敗:', error);
            showToast(`無法載入「${categoryGroup}」分類新聞，請稍後再試`, 'error');
        })
        .finally(() => {
            hideLoadingSpinner();
        });
}

/**
 * 獲取特定分類的新聞
 * @param {string} group - 分類組名稱
 * @param {string} category - 分類名稱
 * @returns {Promise} 返回包含新聞數據的Promise
 */
function fetchCategoryNews(group, category) {
    // 創建API請求的URL
    let apiUrl = '/business/api/category-news';
    
    // 使用fetch API發送請求
    return fetch(`${apiUrl}?group=${encodeURIComponent(group)}&category=${encodeURIComponent(category)}`)
        .then(response => {
            // 檢查回應狀態
            if (!response.ok) {
                throw new Error(`API回應錯誤: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // 檢查API返回的數據狀態
            if (data.status === 'success') {
                return data.news || [];
            } else {
                throw new Error(data.message || '獲取數據失敗');
            }
        })
        .catch(error => {
            // 如果API請求失敗，則使用備用數據
            console.warn('API請求失敗，使用備用數據:', error);
            return getFallbackCategoryNews(group, category);
        });
}

/**
 * 獲取分類組的所有新聞
 * @param {string} group - 分類組名稱
 * @returns {Promise} 返回包含新聞數據的Promise
 */
function fetchCategoryGroupNews(group) {
    // 創建API請求的URL
    let apiUrl = '/business/api/category-group';
    
    // 使用fetch API發送請求
    return fetch(`${apiUrl}?group=${encodeURIComponent(group)}`)
        .then(response => {
            // 檢查回應狀態
            if (!response.ok) {
                throw new Error(`API回應錯誤: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // 檢查API返回的數據狀態
            if (data.status === 'success') {
                return data.news || [];
            } else {
                throw new Error(data.message || '獲取數據失敗');
            }
        })
        .catch(error => {
            // 如果API請求失敗，則使用備用數據
            console.warn('API請求失敗，使用備用數據:', error);
            return getFallbackCategoryGroupNews(group);
        });
}

/**
 * 獲取備用的分類新聞數據
 * @param {string} group - 分類組名稱
 * @param {string} category - 分類名稱
 * @returns {Array} 返回模擬的新聞數據
 */
function getFallbackCategoryNews(group, category) {
    // 客戶關注分類
    const clientInterestNews = {
        '理賠案例': [
            {
                id: 101,
                title: '重大傷病理賠審核標準更新：明年起病歷審查變更',
                summary: '保險公司將依照新標準審核重大傷病理賠申請，影響特定慢性病患者權益。',
                importance_score: 0.85,
                published_date: '2025-07-01T10:30:00Z',
                source_name: '金管會公告'
            },
            {
                id: 102,
                title: '理賠爭議案例分析：法院認定保險公司拒賠不當',
                summary: '最高法院判決保險公司對特定疾病的理賠拒絕有誤，需重新審核類似案例。',
                importance_score: 0.75,
                published_date: '2025-06-28T09:15:00Z',
                source_name: '法律動態週刊'
            }
        ],
        '保費調整': [
            {
                id: 103,
                title: '明年起多家保險公司醫療險保費調漲',
                summary: '因應醫療通膨，多家大型保險公司計劃調升醫療險保費，預計增幅5-15%。',
                importance_score: 0.8,
                published_date: '2025-07-02T14:20:00Z',
                source_name: '保險業動態'
            }
        ],
        '法規變動': [
            {
                id: 104,
                title: '金管會提高投資型保單資訊揭露要求',
                summary: '為保護消費者權益，投資型保單將需更詳細說明費用結構及投資風險。',
                importance_score: 0.9,
                published_date: '2025-07-03T11:45:00Z',
                source_name: '金融監理週刊'
            }
        ]
    };
    
    // 公司動態分類
    const companyNewsData = {
        '新商品發布': [
            {
                id: 105,
                title: '創新長照保險結合AI照護服務上市',
                summary: '業界首創AI照護評估與理賠系統，簡化理賠流程並提供即時照護建議。',
                importance_score: 0.7,
                published_date: '2025-07-02T16:30:00Z',
                source_name: '產品發布會'
            }
        ],
        '通路政策': [
            {
                id: 106,
                title: '數位通路獎勵計畫大幅提升：業務員線上業績額外加成',
                summary: '保險公司推出數位轉型獎勵方案，鼓勵業務員拓展線上銷售管道。',
                importance_score: 0.65,
                published_date: '2025-06-30T13:40:00Z',
                source_name: '通路週報'
            }
        ],
        '獲獎消息': [
            {
                id: 107,
                title: '三家本土保險公司獲亞洲保險創新大獎',
                summary: '台灣保險業在亞洲保險創新大會中表現亮眼，獲得多項技術創新與服務品質獎項。',
                importance_score: 0.55,
                published_date: '2025-06-25T09:00:00Z',
                source_name: '亞洲保險評論'
            }
        ]
    };
    
    // 市場分析分類
    const marketAnalysisData = {
        '保費趨勢': [
            {
                id: 108,
                title: '全球保費增長放緩，亞太區仍保持強勁動能',
                summary: '國際保險研究機構預測明年全球保費增速降至3.5%，但亞太區可望維持6%以上增幅。',
                importance_score: 0.75,
                published_date: '2025-07-01T08:45:00Z',
                source_name: '全球保險觀察'
            }
        ],
        '競爭分析': [
            {
                id: 109,
                title: '外資保險在台市佔率分析：創新服務成關鍵競爭力',
                summary: '研究顯示外資保險公司透過數位創新與客製化服務持續擴大市佔，本土保險業需積極轉型。',
                importance_score: 0.6,
                published_date: '2025-06-29T10:20:00Z',
                source_name: '產業分析報告'
            }
        ],
        '客群變化': [
            {
                id: 110,
                title: 'Z世代保險消費行為研究：數位體驗與社會責任成關鍵',
                summary: '最新消費者調查顯示，年輕世代選購保險更重視數位體驗、社會責任與彈性客製化。',
                importance_score: 0.65,
                published_date: '2025-06-28T15:30:00Z',
                source_name: '消費者趨勢研究'
            }
        ]
    };
    
    // 根據分類組和分類名稱返回相應的數據
    if (group.includes('客戶關注')) {
        return clientInterestNews[category] || [];
    } else if (group.includes('公司動態')) {
        return companyNewsData[category] || [];
    } else if (group.includes('市場分析')) {
        return marketAnalysisData[category] || [];
    }
    
    // 默認返回空數組
    return [];
}

/**
 * 獲取備用的分類組新聞數據
 * @param {string} group - 分類組名稱
 * @returns {Array} 返回模擬的新聞數據
 */
function getFallbackCategoryGroupNews(group) {
    // 客戶關注分類組
    if (group.includes('客戶關注')) {
        return [
            ...getFallbackCategoryNews(group, '理賠案例'),
            ...getFallbackCategoryNews(group, '保費調整'),
            ...getFallbackCategoryNews(group, '法規變動')
        ];
    }
    
    // 公司動態分類組
    if (group.includes('公司動態')) {
        return [
            ...getFallbackCategoryNews(group, '新商品發布'),
            ...getFallbackCategoryNews(group, '通路政策'),
            ...getFallbackCategoryNews(group, '獲獎消息')
        ];
    }
    
    // 市場分析分類組
    if (group.includes('市場分析')) {
        return [
            ...getFallbackCategoryNews(group, '保費趨勢'),
            ...getFallbackCategoryNews(group, '競爭分析'),
            ...getFallbackCategoryNews(group, '客群變化')
        ];
    }
    
    // 默認返回空數組
    return [];
}

/**
 * 更新新聞列表顯示
 * @param {Array} newsData - 新聞數據數組
 * @param {string} categoryTitle - 分類標題
 * @param {number} count - 新聞數量
 */
function updateNewsList(newsData, categoryTitle, count) {
    // 獲取新聞列表容器
    const newsListContainer = document.getElementById('newsList');
    
    // 如果找不到容器，則顯示錯誤並返回
    if (!newsListContainer) {
        console.error('找不到新聞列表容器元素');
        showToast('無法更新新聞列表，頁面結構可能已變更', 'error');
        return;
    }
    
    // 清空現有內容
    newsListContainer.innerHTML = '';
    
    // 添加分類標題和結果計數
    const headerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h5><i class="fas fa-filter me-2"></i>${categoryTitle}</h5>
            <span class="badge bg-primary">${count} 筆結果</span>
        </div>
    `;
    newsListContainer.insertAdjacentHTML('beforeend', headerHTML);
    
    // 如果沒有新聞數據，顯示無結果訊息
    if (!newsData || newsData.length === 0) {
        const noResultsHTML = `
            <div class="text-center py-4">
                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                <p class="text-muted">此分類中沒有新聞</p>
            </div>
        `;
        newsListContainer.insertAdjacentHTML('beforeend', noResultsHTML);
        return;
    }
    
    // 遍歷新聞數據，生成新聞項目
    newsData.forEach(news => {
        // 決定重要性類別和標記
        let importanceClass, importanceText, importanceStars;
        if (news.importance_score >= 0.7) {
            importanceClass = 'bg-danger';
            importanceText = '高';
            importanceStars = '★★★';
        } else if (news.importance_score >= 0.4) {
            importanceClass = 'bg-warning text-dark';
            importanceText = '中';
            importanceStars = '★★☆';
        } else {
            importanceClass = 'bg-info';
            importanceText = '低';
            importanceStars = '★☆☆';
        }
        
        // 格式化日期
        const publishDate = new Date(news.published_date).toLocaleDateString('zh-TW');
        
        // 生成新聞項目HTML
        const newsItemHTML = `
            <div class="news-item priority-news" data-news-id="${news.id}" draggable="true">
                <div class="d-flex align-items-start">
                    <div class="me-3">
                        <input type="checkbox" class="news-select form-check-input" value="${news.id}">
                    </div>
                    <div class="flex-grow-1">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h6>
                                    <span class="importance-star">${importanceStars}</span>
                                    ${news.title}
                                </h6>
                                <p class="text-muted mb-2">${news.summary}</p>
                                <span class="badge ${importanceClass}">重要性：${importanceText}</span>
                                <span class="badge bg-secondary">來源：${news.source_name}</span>
                            </div>
                            <div class="text-end">
                                <div class="btn-group" role="group">
                                    <button class="btn btn-outline-primary btn-sm favorite-btn" data-news-id="${news.id}" data-bs-toggle="tooltip" title="收藏">
                                        <i class="far fa-heart"></i>
                                    </button>
                                    <button class="btn btn-outline-success btn-sm quick-action-btn" data-action="client-template" data-news-id="${news.id}" data-bs-toggle="tooltip" title="生成客戶模板">
                                        <i class="fas fa-file-alt"></i>
                                    </button>
                                    <button class="btn btn-outline-info btn-sm advanced-share-btn" data-news-id="${news.id}" data-bs-toggle="tooltip" title="進階分享">
                                        <i class="fas fa-share-alt"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // 添加到容器中
        newsListContainer.insertAdjacentHTML('beforeend', newsItemHTML);
    });
    
    // 初始化新的工具提示
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // 讓業務儀表板知道狀態已更新
    if (window.businessDashboard) {
        window.businessDashboard.updateBulkActionState();
    }
    
    // 顯示成功訊息
    showToast(`已載入「${categoryTitle}」相關新聞`, 'success');
}

/**
 * 顯示載入指示器
 */
function showLoadingSpinner() {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        spinner.classList.remove('d-none');
    }
}

/**
 * 隱藏載入指示器
 */
function hideLoadingSpinner() {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        spinner.classList.add('d-none');
    }
}

/**
 * 顯示提示訊息
 * @param {string} message - 訊息內容
 * @param {string} type - 訊息類型 (success, info, warning, error)
 */
function showToast(message, type = 'info') {
    // 使用現有通知系統
    if (window.businessTools && window.businessTools.showToast) {
        window.businessTools.showToast(message, type);
    } else if (window.businessDashboard && window.businessDashboard.showToast) {
        window.businessDashboard.showToast(message, type);
    } else {
        // 簡易fallback
        alert(message);
    }
}
