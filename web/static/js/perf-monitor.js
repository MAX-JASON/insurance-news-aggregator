/**
 * 頁面性能監控工具
 * 用於監測和報告頁面載入性能與使用者體驗指標
 */

// 性能監控配置
const perfMonitorConfig = {
    // 是否啟用性能監控
    enabled: true,
    // 是否收集核心Web指標
    collectCoreWebVitals: true,
    // 上報頻率（百分比，1-100）
    reportingRate: 10,
    // 是否記錄到控制台
    consoleLog: false,
    // 是否發送到伺服器
    reportToServer: true,
    // API端點
    apiEndpoint: '/api/v1/perf-monitor',
    // 忽略的路徑（正則表達式）
    ignorePaths: [/^\/api\//, /^\/static\//]
};

// 初始化性能監控
function initPerfMonitor() {
    // 如果禁用，直接返回
    if (!perfMonitorConfig.enabled) return;
    
    // 隨機採樣，基於reportingRate
    if (Math.random() * 100 > perfMonitorConfig.reportingRate) return;
    
    // 檢查當前路徑是否應被忽略
    const currentPath = window.location.pathname;
    for (const pattern of perfMonitorConfig.ignorePaths) {
        if (pattern.test(currentPath)) return;
    }
    
    // 收集基本性能數據
    window.addEventListener('load', function() {
        setTimeout(function() {
            const perfData = collectPerformanceData();
            logPerformanceData(perfData);
            if (perfMonitorConfig.reportToServer) {
                reportPerformanceData(perfData);
            }
        }, 0);
    });
    
    // 如果啟用了Core Web Vitals收集
    if (perfMonitorConfig.collectCoreWebVitals && 'PerformanceObserver' in window) {
        collectCoreWebVitals();
    }
}

// 收集性能數據
function collectPerformanceData() {
    const perf = window.performance;
    
    if (!perf || !perf.timing) {
        return {
            url: window.location.href,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            networkType: navigator.connection ? navigator.connection.effectiveType : 'unknown',
            error: '瀏覽器不支持性能API'
        };
    }
    
    const timing = perf.timing;
    const navigationStart = timing.navigationStart;
    
    // 計算關鍵時間點
    const perfMetrics = {
        url: window.location.href,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        screenSize: `${window.innerWidth}x${window.innerHeight}`,
        networkType: navigator.connection ? navigator.connection.effectiveType : 'unknown',
        timings: {
            // 頁面整體載入時間
            pageLoadTime: timing.loadEventEnd - navigationStart,
            // DNS查詢時間
            dnsTime: timing.domainLookupEnd - timing.domainLookupStart,
            // TCP連接時間
            tcpTime: timing.connectEnd - timing.connectStart,
            // 請求回應時間
            requestTime: timing.responseEnd - timing.requestStart,
            // DOM解析時間
            domParsingTime: timing.domComplete - timing.domLoading,
            // 首次渲染時間
            firstPaintTime: getFirstPaint() - navigationStart,
            // DOM內容載入時間
            domContentLoadedTime: timing.domContentLoadedEventEnd - navigationStart,
            // 頁面互動準備時間
            timeToInteractive: getTimeToInteractive() - navigationStart
        },
        // 資源載入統計
        resources: getResourceStats(),
        // 導航類型（直接訪問、重新載入、返回前進等）
        navigationType: getNavigationType(),
        // 瀏覽器緩存使用情況
        cacheStats: getCacheStats()
    };
    
    return perfMetrics;
}

// 獲取首次渲染時間
function getFirstPaint() {
    // 嘗試從Paint Timing API獲取
    if (window.performance && window.performance.getEntriesByType) {
        const paintMetrics = performance.getEntriesByType('paint');
        const firstPaint = paintMetrics.find(entry => entry.name === 'first-paint');
        if (firstPaint) {
            return firstPaint.startTime + performance.timing.navigationStart;
        }
    }
    
    // 如果不支持Paint Timing API，則使用估算值
    return performance.timing.domLoading;
}

// 估算頁面可互動時間
function getTimeToInteractive() {
    // 簡單估算: DOMContentLoaded + 小延遲
    return performance.timing.domContentLoadedEventEnd + 100;
}

// 獲取資源載入統計
function getResourceStats() {
    if (!performance.getEntriesByType) return {};
    
    const resourceEntries = performance.getEntriesByType('resource');
    let totalTransferSize = 0;
    let totalDuration = 0;
    
    const resourceTypes = {
        script: { count: 0, size: 0, time: 0 },
        css: { count: 0, size: 0, time: 0 },
        image: { count: 0, size: 0, time: 0 },
        font: { count: 0, size: 0, time: 0 },
        other: { count: 0, size: 0, time: 0 }
    };
    
    resourceEntries.forEach(entry => {
        const size = entry.transferSize || 0;
        const time = entry.duration || 0;
        totalTransferSize += size;
        totalDuration += time;
        
        // 根據資源類型進行分類
        let type = 'other';
        
        if (entry.name.match(/\.js(\?|$)/)) {
            type = 'script';
        } else if (entry.name.match(/\.css(\?|$)/)) {
            type = 'css';
        } else if (entry.name.match(/\.(png|jpg|jpeg|gif|svg|webp)(\?|$)/)) {
            type = 'image';
        } else if (entry.name.match(/\.(woff|woff2|ttf|otf|eot)(\?|$)/)) {
            type = 'font';
        }
        
        resourceTypes[type].count++;
        resourceTypes[type].size += size;
        resourceTypes[type].time += time;
    });
    
    return {
        totalCount: resourceEntries.length,
        totalSize: Math.round(totalTransferSize / 1024), // KB
        totalDuration: Math.round(totalDuration),
        byType: resourceTypes
    };
}

// 獲取導航類型
function getNavigationType() {
    if (!performance || !performance.navigation) return 'unknown';
    
    const navTypes = [
        'navigate',      // 0: 直接訪問
        'reload',        // 1: 重新載入
        'back_forward',  // 2: 後退/前進
        'reserved'       // 3: 保留值
    ];
    
    return navTypes[performance.navigation.type] || 'unknown';
}

// 獲取緩存統計資料
function getCacheStats() {
    if (!performance.getEntriesByType) return {};
    
    const resourceEntries = performance.getEntriesByType('resource');
    let cachedResources = 0;
    let nonCachedResources = 0;
    
    resourceEntries.forEach(entry => {
        // 如果transferSize為0或非常小，可能是從緩存讀取的
        if (entry.transferSize === 0 || (entry.transferSize < 100 && entry.decodedBodySize > 0)) {
            cachedResources++;
        } else {
            nonCachedResources++;
        }
    });
    
    return {
        cachedCount: cachedResources,
        nonCachedCount: nonCachedResources,
        cacheHitRate: resourceEntries.length ? 
            Math.round((cachedResources / resourceEntries.length) * 100) : 0
    };
}

// 收集Core Web Vitals
function collectCoreWebVitals() {
    try {
        // Largest Contentful Paint
        new PerformanceObserver(entryList => {
            const entries = entryList.getEntries();
            const lastEntry = entries[entries.length - 1];
            window._lcp = lastEntry.renderTime || lastEntry.loadTime;
        }).observe({ type: 'largest-contentful-paint', buffered: true });
        
        // First Input Delay
        new PerformanceObserver(entryList => {
            const entries = entryList.getEntries();
            entries.forEach(entry => {
                window._fid = entry.processingStart - entry.startTime;
            });
        }).observe({ type: 'first-input', buffered: true });
        
        // Cumulative Layout Shift
        let cumulativeLayoutShift = 0;
        new PerformanceObserver(entryList => {
            const entries = entryList.getEntries();
            entries.forEach(entry => {
                if (!entry.hadRecentInput) {
                    cumulativeLayoutShift += entry.value;
                }
            });
            window._cls = cumulativeLayoutShift;
        }).observe({ type: 'layout-shift', buffered: true });
    } catch (e) {
        console.warn('Core Web Vitals measurement failed:', e);
    }
}

// 輸出性能數據到控制台
function logPerformanceData(perfData) {
    if (!perfMonitorConfig.consoleLog) return;
    
    console.group('📊 頁面性能指標');
    console.log('📁 頁面URL:', perfData.url);
    console.log('⏱️ 頁面載入時間:', perfData.timings.pageLoadTime, 'ms');
    console.log('🖥️ DOM內容載入:', perfData.timings.domContentLoadedTime, 'ms');
    console.log('🎨 首次渲染時間:', perfData.timings.firstPaintTime, 'ms');
    console.log('👆 可互動時間:', perfData.timings.timeToInteractive, 'ms');
    
    if (perfData.resources) {
        console.group('📦 資源統計');
        console.log('總資源數:', perfData.resources.totalCount);
        console.log('總傳輸大小:', perfData.resources.totalSize, 'KB');
        console.log('總載入時間:', perfData.resources.totalDuration, 'ms');
        console.log('緩存使用率:', perfData.cacheStats.cacheHitRate, '%');
        console.groupEnd();
    }
    
    // 如果有Core Web Vitals數據，則顯示
    if (window._lcp || window._fid || window._cls !== undefined) {
        console.group('🌟 Core Web Vitals');
        if (window._lcp) console.log('LCP:', Math.round(window._lcp), 'ms');
        if (window._fid) console.log('FID:', Math.round(window._fid), 'ms');
        if (window._cls !== undefined) console.log('CLS:', window._cls.toFixed(3));
        console.groupEnd();
    }
    
    console.groupEnd();
}

// 向服務器報告性能數據
function reportPerformanceData(perfData) {
    // 添加Core Web Vitals數據
    if (perfMonitorConfig.collectCoreWebVitals) {
        perfData.webVitals = {
            lcp: window._lcp ? Math.round(window._lcp) : null,
            fid: window._fid ? Math.round(window._fid) : null,
            cls: window._cls !== undefined ? window._cls.toFixed(3) : null
        };
    }
    
    // 發送到伺服器
    fetch(perfMonitorConfig.apiEndpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(perfData),
        // 使用keepalive確保數據在頁面關閉後仍能發送
        keepalive: true
    }).catch(err => {
        if (perfMonitorConfig.consoleLog) {
            console.warn('無法發送性能數據:', err);
        }
    });
}

// 初始化性能監控
initPerfMonitor();

// 導出核心功能
window.perfMonitor = {
    getPerformanceData: collectPerformanceData,
    logPerformanceData: logPerformanceData
};
