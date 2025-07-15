"""
Web 路由模組
Web Routes Module

提供Web頁面路由
"""

from flask import Blueprint, render_template, request, current_app, jsonify, redirect, url_for
from database.models import News, NewsSource, NewsCategory, db, Feedback
from sqlalchemy import desc, func, or_
from datetime import datetime, timedelta
import logging
import json
from datetime import datetime, timedelta
# 導入必要模組

# 創建Web藍圖
web_bp = Blueprint('web', __name__)

# 獲取日誌器
logger = logging.getLogger('web')

@web_bp.route('/')
def index():
    """首頁"""
    try:
        logger.info("首頁訪問請求")
          # 獲取真實的最新新聞數據
        latest_news = News.query.filter_by(status='active').order_by(desc(News.crawled_date)).limit(6).all()
        
        # 統計數據
        total_news = News.query.filter_by(status='active').count()
        total_sources = NewsSource.query.filter_by(status='active').count()
        total_categories = NewsCategory.query.count()
        
        # 今日新聞數量
        today = datetime.now().date()
        today_news = News.query.filter(
            func.date(News.crawled_date) == today,
            News.status == 'active'
        ).count()
        
        # 如果沒有真實數據，提供示例數據
        if not latest_news:
            latest_news = [
                {
                    'id': 1,
                    'title': '保險業數位轉型加速進行',
                    'summary': '各大保險公司積極投入數位化轉型，運用AI和大數據技術提升服務效率...',
                    'published_date': '2024-01-15T10:00:00Z',
                    'source': '保險日報',
                    'category': '產業動態',
                    'image_url': '/static/images/news-placeholder.jpg'
                },
                {
                    'id': 2,
                    'title': '新型醫療保險商品上市',
                    'summary': '針對高齡化社會推出創新醫療保險商品，提供更全面的健康保障...',
                    'published_date': '2024-01-15T09:30:00Z',
                    'source': '金融時報',
                    'category': '商品資訊',
                    'image_url': '/static/images/news-placeholder.jpg'
                }
            ]
        
        return render_template('index.html',                             latest_news=latest_news,
                             total_news=total_news,
                             total_sources=total_sources,
                             total_categories=total_categories,
                             today_news=today_news)
        
    except Exception as e:
        logger.error(f"首頁載入錯誤: {str(e)}")
        # 即使發生錯誤，也嘗試提供基本統計數據
        try:
            total_news = News.query.filter_by(status='active').count()
            total_sources = NewsSource.query.filter_by(status='active').count()
            total_categories = NewsCategory.query.count()
            today_news = News.query.filter(
                func.date(News.crawled_date) == datetime.now().date(),
                News.status == 'active'
            ).count()
        except:
            total_news = total_sources = total_categories = today_news = 0
            
        return render_template('index.html', 
                             latest_news=[],
                             total_news=total_news,
                             total_sources=total_sources,
                             total_categories=total_categories,
                             today_news=today_news)

@web_bp.route('/news')
def news_list():
    """新聞列表頁"""
    try:
        page = request.args.get('page', 1, type=int)
        category = request.args.get('category', '')
        source = request.args.get('source', '')
        search = request.args.get('search', '')
        sort_by = request.args.get('sort', 'date')
        
        logger.info(f"新聞列表頁訪問 - 頁碼: {page}, 分類: {category}, 來源: {source}, 搜尋: {search}, 排序: {sort_by}")
        
        # 構建查詢
        query = News.query.filter_by(status='active')
        
        if category:
            query = query.join(NewsCategory).filter(NewsCategory.name == category)
        
        if source:
            query = query.join(NewsSource).filter(NewsSource.name == source)
            
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    News.title.like(search_term),
                    News.summary.like(search_term),
                    News.content.like(search_term)
                )
            )
        
        # 排序
        if sort_by == 'view':
            query = query.order_by(desc(News.view_count), desc(News.crawled_date))
        elif sort_by == 'importance':
            query = query.order_by(desc(News.importance_score), desc(News.crawled_date))
        else:  # date
            query = query.order_by(desc(News.crawled_date))
        
        # 分頁查詢
        pagination = query.paginate(
            page=page, per_page=20, error_out=False
        )
        
        news_list = []
        for news in pagination.items:
            news_data = {
                'id': news.id,
                'title': news.title or f'保險新聞標題 {news.id}',
                'summary': news.summary or '新聞摘要內容...',
                'published_date': news.published_date.isoformat() if news.published_date else '2024-01-01T00:00:00Z',
                'source': news.source.name if news.source else '未知來源',
                'category': news.category.name if news.category else '未分類',
                'view_count': news.view_count or 0,                'image_url': news.image_url or '/static/images/news-placeholder.jpg'
            }
            news_list.append(news_data)
        
        # 獲取所有可用的分類和來源
        all_categories = NewsCategory.query.all()
        all_sources = NewsSource.query.filter_by(status='active').all()
        
        return render_template('news/list.html',
                             news_list=news_list,
                             pagination=pagination,
                             current_category=category,
                             current_source=source,
                             current_search=search,
                             current_sort=sort_by,
                             all_categories=all_categories,
                             all_sources=all_sources,
                             now=datetime.now())
    
    except Exception as e:
        logger.error(f"新聞列表頁載入失敗: {str(e)}")
        return render_template('errors/500.html'), 500

@web_bp.route('/news/<int:news_id>')
def news_detail(news_id):
    """新聞詳情頁"""
    try:
        logger.info(f"新聞詳情頁訪問 - ID: {news_id}")
        
        # 嘗試從資料庫獲取新聞詳情
        try:
            from app import db
            from database.models import News, NewsSource, NewsCategory
            
            with db.session.begin():
                news = News.query.get(news_id)
                
                if news:
                    # 確保有完整的關聯資料
                    source_name = news.source.name if news.source else "未知來源"
                    category_name = news.category.name if news.category else "一般新聞"
                    
                    # 格式化新聞數據
                    news_data = {
                        'id': news.id,
                        'title': news.title,
                        'content': news.content,
                        'summary': news.summary,
                        'url': news.url,  # 原始新聞連結
                        'source': source_name,
                        'category': category_name,
                        'published_date': news.published_date,
                        'author': news.author,
                        'view_count': news.view_count or 0,
                        'importance_score': news.importance_score or 0,
                        'tags': json.loads(news.tags) if news.tags else [],
                        'created_at': news.created_at
                    }
                    
                    # 增加瀏覽次數
                    news.view_count = (news.view_count or 0) + 1
                    db.session.commit()
                    
                    # 獲取相關新聞
                    try:
                        related_news = News.query.filter(
                            News.id != news_id,
                            News.source_id == news.source_id
                        ).limit(5).all()
                        
                        related_news_data = []
                        for related in related_news:
                            related_news_data.append({
                                'id': related.id,
                                'title': related.title,
                                'summary': related.summary,
                                'published_date': related.published_date,
                                'source': related.source.name if related.source else "未知來源"
                            })
                    except Exception:
                        related_news_data = []
                    
                    return render_template('news/detail.html', 
                                         news=news_data,
                                         related_news=related_news_data)
                else:
                    # 新聞不存在，返回404或模擬數據
                    raise Exception("新聞不存在")
                    
        except Exception as db_error:
            logger.warning(f"資料庫查詢失敗，使用模擬數據: {str(db_error)}")
            # 如果資料庫查詢失敗，返回模擬數據
            pass
        
        # 模擬數據作為備用
        news_data = {
            'id': news_id,
            'title': f'台灣保險新聞標題 {news_id}',
            'content': '''這是一篇關於台灣保險業的重要新聞。內容包含了最新的保險政策變化、市場動態以及對消費者的影響分析。
            
台灣保險業作為金融服務業的重要組成部分，其發展狀況直接關係到國民經濟的穩定性和人民生活的保障水平。近年來，隨著監管政策的不斷完善和市場競爭的日益激烈，台灣保險業正面臨著前所未有的挑戰和機遇。

從市場角度來看，台灣消費者對保險產品的需求日益多樣化，特別是在健康險、長照險等領域，需求增長尤為明顯。保險公司也在積極調整產品結構，推出更多符合台灣市場需求的創新產品。

監管方面，金管會持續加強對台灣保險業的監管力度，確保行業健康發展的同時，也要求保險公司提升服務品質，保護消費者權益。''',
            'summary': f'這是第 {news_id} 則台灣保險新聞的詳細摘要內容，涵蓋了重要的行業動態和政策變化。',
            'url': 'https://example.com/news/original-link',
            'source': '台灣保險日報',
            'category': '產業動態',
            'published_date': '2025-06-16',
            'author': '記者姓名',
            'view_count': 150,
            'importance_score': 0.8,
            'tags': ['台灣保險', '政策', '市場'],
            'created_at': '2025-06-16'        }
        
        return render_template('news/detail_business.html', 
                             news=news_data,
                             related_news=[])
        
    except Exception as e:
        logger.error(f"新聞詳情頁錯誤: {str(e)}")
        return render_template('errors/404.html'), 404

@web_bp.route('/search')
def search():
    """搜索頁面"""
    try:
        keyword = request.args.get('keyword', '').strip()
        page = request.args.get('page', 1, type=int)
        
        logger.info(f"搜索頁面訪問 - 關鍵詞: {keyword}")
        
        if not keyword:
            return render_template('news/search.html',
                                 keyword='',
                                 results=[],
                                 pagination=None)
        
        # 模擬搜索結果
        results = [
            {
                'id': i,
                'title': f'包含 "{keyword}" 的保險新聞 {i}',
                'summary': f'這是包含關鍵詞 "{keyword}" 的新聞摘要...',
                'published_date': '2024-01-15T10:00:00Z',
                'source': '保險日報',
                'category': '產業動態',
                'relevance_score': 0.95 - i * 0.05
            } for i in range(1, 11)  # 10筆搜索結果
        ]
          # 模擬分頁 - 使用相同的 MockPagination 類
        class MockPagination:
            def __init__(self, page, per_page, total, pages):
                self.page = page
                self.per_page = per_page
                self.total = total
                self.pages = pages
                self.has_prev = page > 1
                self.has_next = page < pages
                self.prev_num = page - 1 if page > 1 else None
                self.next_num = page + 1 if page < pages else None
            
            def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
                """模擬 Flask-SQLAlchemy 的 iter_pages 方法"""
                last = self.pages
                for num in range(1, last + 1):
                    if num <= left_edge or \
                       (self.page - left_current - 1 < num < self.page + right_current) or \
                       num > last - right_edge:
                        yield num
        
        pagination = MockPagination(page, 10, 25, 3)
        
        return render_template('news/search.html',
                             keyword=keyword,
                             results=results,
                             pagination=pagination)
    
    except Exception as e:
        logger.error(f"搜索頁面載入失敗: {str(e)}")
        return render_template('errors/500.html'), 500

@web_bp.route('/about')
def about():
    """關於我們頁面"""
    return render_template('about.html')

@web_bp.route('/api-docs')
def api_docs():
    """API文檔頁面"""
    return render_template('api_docs.html')

@web_bp.route('/crawler/control')
def crawler_control():
    """爬蟲控制面板"""
    try:
        # 使用新版爬蟲控制面板
        return render_template('crawler_control_new.html')
    except Exception as e:
        logger.error(f"爬蟲控制面板載入失敗: {e}")
        return render_template('errors/500.html'), 500

@web_bp.route('/crawler/control/legacy')
def crawler_control_legacy():
    """舊版爬蟲控制面板"""
    try:
        return render_template('crawler_control.html')
    except Exception as e:
        logger.error(f"舊版爬蟲控制面板載入失敗: {e}")
        return render_template('errors/500.html'), 500

@web_bp.route('/crawler')
def crawler_redirect():
    """重定向到爬蟲監控頁面"""
    return redirect(url_for('web.crawler_monitor'))

@web_bp.route('/crawler/monitor')
def crawler_monitor():
    """爬蟲監控頁面 (直接顯示，不重定向)"""
    try:
        logger.info("爬蟲監控頁面訪問請求")
        return render_template('monitor/crawler.html')
    except Exception as e:
        logger.error(f"爬蟲監控頁面錯誤: {str(e)}")
        return render_template('errors/500.html', error="頁面載入失敗"), 500

# AJAX端點
@web_bp.route('/api/web/latest-news')
def ajax_latest_news():
    """AJAX獲取最新新聞"""
    try:
        limit = request.args.get('limit', 5, type=int)
        
        # 模擬最新新聞
        latest_news = [
            {
                'id': i,
                'title': f'最新保險新聞 {i}',
                'published_date': '2024-01-15T10:00:00Z',
                'source': '保險日報'
            } for i in range(1, limit + 1)
        ]
        
        return jsonify({
            'status': 'success',
            'data': latest_news
        })
    
    except Exception as e:
        logger.error(f"AJAX獲取最新新聞失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# 註釋掉重複的業務員路由 - 已改用 business_routes.py 中的專業版本
# @web_bp.route('/business')
# def business_dashboard():
#     """業務員工作台"""
#     try:
#         logger.info("業務員工作台頁面請求")
#         
#         # 獲取最新重要新聞
#         latest_news = News.query.filter_by(status='active').order_by(desc(News.crawled_date)).limit(8).all()
#         
#         # 統計數據
#         total_news = News.query.filter_by(status='active').count()
#         total_sources = NewsSource.query.filter_by(status='active').count()
#         
#         # 今日新聞數量
#         today = datetime.now().date()
#         today_news = News.query.filter(
#             func.date(News.crawled_date) == today,
#             News.status == 'active'
#         ).count()
#         
#         return render_template('business/dashboard.html',
#                              latest_news=latest_news,
#                              total_news=total_news,
#                              total_sources=total_sources,
#                              today_news=today_news)
#         
#     except Exception as e:
#         logger.error(f"業務員工作台頁面錯誤: {str(e)}")
#         return render_template('errors/500.html'), 500

# @web_bp.route('/business/search')
# def business_search():
#     """業務員搜尋頁面"""
#     try:
#         return render_template('business/search.html')
#     except Exception as e:
#         logger.error(f"業務員搜尋頁面錯誤: {str(e)}")
#         return render_template('errors/500.html'), 500

# @web_bp.route('/business/favorites')
# def business_favorites():
#     """業務員收藏頁面"""
#     try:
#         return render_template('business/favorites.html')
#     except Exception as e:
#         logger.error(f"業務員收藏頁面錯誤: {str(e)}")
#         return render_template('errors/500.html'), 500

# @web_bp.route('/business/tools')
# def client_tool():
#     """業務員工具頁面"""
#     try:
#         logger.info("業務員工具頁面訪問請求")
#         return render_template('business/client_tool.html')
#     except Exception as e:
#         logger.error(f"業務員工具頁面錯誤: {str(e)}")
#         return render_template('errors/500.html'), 500

# @web_bp.route('/business/')
# @web_bp.route('/business/index')
# def index():
#     """業務員賽博朋克首頁"""
#     try:
#         logger.info("業務員賽博朋克首頁訪問請求")
#         return render_template('business/index.html')
#     except Exception as e:
#         logger.error(f"業務員首頁錯誤: {str(e)}")
#         return render_template('errors/500.html'), 500

# @web_bp.route('/business/cyber-news')
# def cyber_news():
#     """業務員賽博朋克新聞中心"""
#     try:
#         logger.info("業務員賽博朋克新聞中心訪問請求")
#         # 獲取最新新聞
#         latest_news = News.query.filter_by(status='active').order_by(desc(News.crawled_date)).limit(12).all()
#         return render_template('business/cyber_news_center.html', latest_news=latest_news)
#     except Exception as e:
#         logger.error(f"賽博朋克新聞中心錯誤: {str(e)}")
#         return render_template('errors/500.html'), 500

# @web_bp.route('/business/preferences')
# def preferences():
#     """業務員個人化設定"""
#     try:
#         logger.info("業務員個人化設定頁面訪問請求")
#         return render_template('business/preferences.html')
#     except Exception as e:
#         logger.error(f"個人化設定頁面錯誤: {str(e)}")
#         return render_template('errors/500.html'), 500

# @web_bp.route('/business/share-tools')
# def share_tools():
#     """業務員分享工具"""
#     try:
#         logger.info("業務員分享工具頁面訪問請求")
#         return render_template('business/share_tools.html')
#     except Exception as e:
#         logger.error(f"分享工具頁面錯誤: {str(e)}")
#         return render_template('errors/500.html'), 500
