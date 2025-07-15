@echo off
chcp 65001 >nul
echo ===================================================
echo   台灣保險新聞爬蟲控制面板
echo   Taiwan Insurance News Crawler Control Panel
echo ===================================================
echo.

:: 檢查虛擬環境Python
set PYTHON_PATH=D:\insurance-news-aggregator\venv\Scripts\python.exe
if not exist "%PYTHON_PATH%" (
    echo [Error] 無法找到虛擬環境Python！路徑：%PYTHON_PATH%
    echo 請確保虛擬環境已正確安裝。
    echo.
    pause
    exit /b 1
)

:: 切換到正確目錄
cd /d "%~dp0"

:menu
cls
color 1F
echo ===================================================
echo   台灣保險新聞爬蟲控制面板 v1.0
echo   Taiwan Insurance News Crawler Control Panel
echo ===================================================
echo.
echo  [1] 執行模擬爬蟲 (安全模式)
echo      Run Mock Crawler (Safe Mode)
echo.
echo  [2] 執行真實爬蟲 (可能被網站阻擋)
echo      Run Real Crawler (May be blocked by websites)
echo.
echo  [3] 查看爬蟲狀態
echo      View Crawler Status
echo.
echo  [4] 查看爬取的新聞數量
echo      View Number of Crawled News
echo.
echo  [5] 啟動系統並打開網頁
echo      Start System and Open Web Page
echo.
echo  [0] 退出
echo      Exit
echo.
echo ===================================================
echo.

set /p choice=請選擇操作 [0-5]: 

if "%choice%"=="1" goto run_mock_crawler
if "%choice%"=="2" goto run_real_crawler
if "%choice%"=="3" goto view_status
if "%choice%"=="4" goto view_count
if "%choice%"=="5" goto start_system
if "%choice%"=="0" goto end

echo 無效的選擇，請重試。
timeout /t 2 >nul
goto menu

:run_mock_crawler
cls
color 0A
echo ===================================================
echo   執行模擬爬蟲 (安全模式)
echo   Running Mock Crawler (Safe Mode)
echo ===================================================
echo.
echo 正在啟動爬蟲，請稍候...
echo.

"%PYTHON_PATH%" -c "from crawler.manager import get_crawler_manager; print('爬蟲初始化中...'); manager = get_crawler_manager(); print('開始執行模擬爬蟲...'); result = manager.crawl_all_sources(use_mock=True); print(f'爬蟲執行結果: {result[\"message\"]}'); print(f'總共抓取了 {result.get(\"total\", 0)} 條新聞')"

echo.
echo 操作完成，按任意鍵返回主選單...
pause >nul
goto menu

:run_real_crawler
cls
color 0E
echo ===================================================
echo   執行真實爬蟲 (可能被網站阻擋)
echo   Running Real Crawler (May be blocked by websites)
echo ===================================================
echo.
echo 警告: 真實爬蟲會連接到實際網站抓取資料，頻繁使用可能導致IP被阻擋。
echo Warning: Real crawler connects to actual websites. Frequent use may result in IP being blocked.
echo.
echo 是否確定要繼續? (Y/N)
set /p confirm=

if /i not "%confirm%"=="Y" goto menu

echo.
echo 正在啟動真實爬蟲，請稍候...
echo.

"%PYTHON_PATH%" -c "from crawler.manager import get_crawler_manager; print('爬蟲初始化中...'); manager = get_crawler_manager(); print('開始執行真實爬蟲...'); result = manager.run_all_crawlers(use_real=True); print(f'爬蟲執行結果: {result[\"message\"]}'); print(f'總共抓取了 {result.get(\"total\", 0)} 條新聞')"

echo.
echo 操作完成，按任意鍵返回主選單...
pause >nul
goto menu

:view_status
cls
color 0B
echo ===================================================
echo   查看爬蟲狀態
echo   View Crawler Status
echo ===================================================
echo.
echo 正在檢查爬蟲狀態，請稍候...
echo.

"%PYTHON_PATH%" -c "from crawler.manager import get_crawler_manager; print('爬蟲初始化中...'); manager = get_crawler_manager(); status = manager.get_crawler_status(); print(f'爬蟲狀態: {\"運行中\" if status[\"is_running\"] else \"未運行\"}'); print(f'自動爬蟲: {\"已啟用\" if status[\"auto_crawl_enabled\"] else \"未啟用\"}'); print(f'最後運行時間: {status[\"last_crawl_time\"] or \"從未運行\"}'); print(f'總爬取次數: {status[\"stats\"][\"total_news\"]} 條新聞'); print(f'成功次數: {status[\"stats\"][\"successful_crawls\"]}, 失敗次數: {status[\"stats\"][\"failed_crawls\"]}')"

echo.
echo 操作完成，按任意鍵返回主選單...
pause >nul
goto menu

:view_count
cls
color 0B
echo ===================================================
echo   查看爬取的新聞數量
echo   View Number of Crawled News
echo ===================================================
echo.
echo 正在統計新聞數量，請稍候...
echo.

"%PYTHON_PATH%" -c "import os, sqlite3; db_path = os.path.join('instance', 'insurance_news.db'); conn = sqlite3.connect(db_path) if os.path.exists(db_path) else None; print('連接資料庫成功' if conn else '無法連接資料庫'); cursor = conn.cursor() if conn else None; cursor.execute('SELECT COUNT(*) FROM news') if cursor else None; count = cursor.fetchone()[0] if cursor else 0; print(f'資料庫中共有 {count} 條新聞'); cursor.execute('SELECT source, COUNT(*) as count FROM news GROUP BY source ORDER BY count DESC') if cursor else None; sources = cursor.fetchall() if cursor else []; print('\\n來源統計:'); [print(f'- {source}: {count} 條新聞') for source, count in sources]; conn.close() if conn else None"

echo.
echo 操作完成，按任意鍵返回主選單...
pause >nul
goto menu

:start_system
cls
color 0D
echo ===================================================
echo   啟動系統並打開網頁
echo   Start System and Open Web Page
echo ===================================================
echo.
echo 正在啟動系統，請稍候...
echo.

start "" "UI啟動.bat"
timeout /t 5 >nul
start "" http://127.0.0.1:5000

echo.
echo 系統已啟動並打開瀏覽器，按任意鍵返回主選單...
pause >nul
goto menu

:end
color 07
echo.
echo 感謝使用台灣保險新聞爬蟲控制面板！
echo.
exit /b 0
