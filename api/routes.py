"""
API 路由模組
API Routes Module

提供RESTful API接口
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timezone, timedelta
from database.models import News, NewsSource, NewsCategory, CrawlLog, SystemConfig, db
from sqlalchemy import desc, func
from analyzer.engine import get_analyzer, analyze_news_article
from crawler.manager import get_crawler_manager
import logging

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

@api_bp.route('/health')
def health():
    """健康檢查端點"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': '2.0.0'
    })

@api_bp.route('/news')
def get_news():
    """獲取新聞列表"""
    try:
        # 分頁參數
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # 過濾參數
        source_id = request.args.get('source_id', type=int)
        category_id = request.args.get('category_id', type=int)
        keyword = request.args.get('keyword', '').strip()
        show_all = request.args.get('show_all', 'false').lower() == 'true'
        
        # 構建查詢 - 預設只顯示7天內的新聞
        query = News.query.filter_by(status='active')
        
        # 如果沒有特別要求顯示全部，則只顯示7天內的新聞
        if not show_all:
            seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
            query = query.filter(News.published_date >= seven_days_ago)
        
        if source_id:
            query = query.filter_by(source_id=source_id)
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        if keyword:
            query = query.filter(
                db.or_(
                    News.title.contains(keyword),
                    News.summary.contains(keyword),
                    News.content.contains(keyword)
                )
            )
        
        # 排序和分頁
        query = query.order_by(desc(News.published_date))
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # 序列化結果
        news_list = []
        for news in pagination.items:
            news_data = {
                'id': news.id,
                'title': news.title,
                'summary': news.summary,
                'url': news.url,
                'published_date': news.published_date.isoformat(),
                'crawled_date': news.crawled_date.isoformat(),
                'source': {
                    'id': news.source.id,
                    'name': news.source.name
                } if news.source else None,
                'category': {
                    'id': news.category.id,
                    'name': news.category.name
                } if news.category else None,
                'view_count': news.view_count,
                'sentiment_score': news.sentiment_score,
                'importance_score': news.importance_score,
                'word_count': news.word_count,
                'reading_time': news.reading_time
            }
            news_list.append(news_data)
        
        return jsonify({
            'status': 'success',
            'data': news_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"獲取新聞列表失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '獲取新聞列表失敗'
        }), 500

@api_bp.route('/news/<int:news_id>')
def get_news_detail(news_id):
    """獲取單篇新聞詳情"""
    try:
        news = News.query.filter_by(id=news_id, status='active').first()
        
        if not news:
            return jsonify({
                'status': 'error',
                'message': '新聞不存在或已被刪除'
            }), 404
        
        # 增加瀏覽次數
        news.view_count = (news.view_count or 0) + 1
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'data': {
                'id': news.id,
                'title': news.title,
                'content': news.content,
                'summary': news.summary,
                'url': news.url,
                'published_at': news.published_date.isoformat() if news.published_date else None,
                'source': news.source.name if news.source else '未知來源',
                'category': news.category.name if news.category else '未分類',
                'view_count': news.view_count,
                'crawled_date': news.crawled_date.isoformat() if news.crawled_date else None
            }
        })
    
    except Exception as e:
        logging.error(f"獲取新聞詳情失敗: {str(e)}")
        return jsonify({
            'status': 'error', 
            'message': '獲取新聞詳情失敗'
        }), 500

@api_bp.route('/sources')
def get_sources():
    """獲取新聞來源列表"""
    try:
        sources = NewsSource.query.filter_by(status='active').all()
        
        sources_list = []
        for source in sources:
            sources_list.append({
                'id': source.id,
                'name': source.name,
                'url': source.url,
                'description': source.description,
                'logo_url': source.logo_url,
                'total_news_count': source.total_news_count,
                'reliability_score': source.reliability_score,
                'last_crawl_time': source.last_crawl_time.isoformat() if source.last_crawl_time else None
            })
        
        return jsonify({
            'status': 'success',
            'data': sources_list
        })
        
    except Exception as e:
        logger.error(f"獲取新聞來源失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '獲取新聞來源失敗'
        }), 500

@api_bp.route('/categories')
def get_categories():
    """獲取新聞分類列表"""
    try:
        categories = NewsCategory.query.filter_by(status='active').order_by(NewsCategory.sort_order).all()
        
        categories_list = []
        for category in categories:
            categories_list.append({
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'color_code': category.color_code,
                'icon': category.icon,
                'news_count': category.news_count,
                'level': category.level
            })
        
        return jsonify({
            'status': 'success',
            'data': categories_list
        })
        
    except Exception as e:
        logger.error(f"獲取新聞分類失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '獲取新聞分類失敗'
        }), 500

@api_bp.route('/stats')
def get_stats():
    """獲取系統統計數據"""
    try:
        from datetime import date
        
        # 基本統計
        total_news = News.query.filter_by(status='active').count()
        total_sources = NewsSource.query.filter_by(status='active').count()
        total_categories = NewsCategory.query.count()
        
        # 今日新聞統計
        today = date.today()
        today_news = News.query.filter(
            func.date(News.crawled_date) == today,
            News.status == 'active'
        ).count()
        
        # 最近7天統計
        week_ago = date.today() - timedelta(days=7)
        week_news = News.query.filter(
            func.date(News.crawled_date) >= week_ago,
            News.status == 'active'
        ).count()
        
        # 來源統計
        source_stats = db.session.query(
            NewsSource.name,
            func.count(News.id).label('count')
        ).join(News).filter(News.status == 'active').group_by(NewsSource.name).all()
        
        # 分類統計
        category_stats = db.session.query(
            NewsCategory.name,
            func.count(News.id).label('count')
        ).join(News).filter(News.status == 'active').group_by(NewsCategory.name).all()
        
        return jsonify({
            'status': 'success',
            'data': {
                'totalNews': total_news,
                'totalSources': total_sources,
                'totalCategories': total_categories,
                'todayNews': today_news,
                'weekNews': week_news,
                'sourceStats': [{'name': name, 'count': count} for name, count in source_stats],
                'categoryStats': [{'name': name, 'count': count} for name, count in category_stats],
                'lastUpdated': datetime.now(timezone.utc).isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"獲取統計數據失敗: {e}")
        return jsonify({
            'status': 'error',
            'message': '無法獲取統計數據',
            'error': str(e)
        }), 500

@api_bp.route('/crawler/start', methods=['POST'])
def start_crawler():
    """手動啟動爬蟲"""
    try:
        # 導入爬蟲管理器
        from crawler.manager import get_crawler_manager
        
        crawler_manager = get_crawler_manager()
        
        # 獲取參數
        data = request.get_json() or {}
        use_mock = data.get('use_mock', True)
        
        # 執行爬取
        result = crawler_manager.crawl_all_sources(use_mock=use_mock)
        
        if result['status'] == 'success':
            return jsonify({
                'status': 'success',
                'message': '爬蟲啟動成功',
                'data': result
            })
        else:
            return jsonify({
                'status': 'error',
                'message': result['message']
            }), 400
            
    except Exception as e:
        logger.error(f"啟動爬蟲失敗: {e}")
        return jsonify({
            'status': 'error',
            'message': f'啟動爬蟲失敗: {str(e)}'
        }), 500

@api_bp.route('/crawler/status')
def get_crawler_status():
    """獲取爬蟲狀態"""
    try:
        # 基本統計
        total_sources = NewsSource.query.count()
        active_sources = NewsSource.query.filter_by(status='active').count()
        
        # 今日爬取統計
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        today_logs = CrawlLog.query.filter(CrawlLog.start_time >= today_start)
        
        total_crawls_today = today_logs.count()
        successful_crawls_today = today_logs.filter_by(success=True).count()
        failed_crawls_today = today_logs.filter_by(success=False).count()
        
        # 最近活動
        recent_logs = CrawlLog.query.order_by(desc(CrawlLog.start_time)).limit(10).all()
        
        # 新聞統計
        total_news = News.query.filter_by(status='active').count()
        news_today = News.query.filter(
            News.crawled_date >= today_start,
            News.status == 'active'
        ).count()
        
        return jsonify({
            'status': 'success',
            'data': {
                'sources': {
                    'total': total_sources,
                    'active': active_sources,
                    'inactive': total_sources - active_sources
                },
                'crawls_today': {
                    'total': total_crawls_today,
                    'successful': successful_crawls_today,
                    'failed': failed_crawls_today,
                    'success_rate': round(successful_crawls_today / total_crawls_today * 100, 1) if total_crawls_today > 0 else 0
                },
                'news': {
                    'total': total_news,
                    'today': news_today
                },
                'recent_activities': [
                    {
                        'id': log.id,
                        'source': log.source.name if log.source else 'Unknown',
                        'success': log.success,
                        'news_found': log.news_found,
                        'news_new': log.news_new,
                        'duration': round(log.duration, 2) if log.duration else None,
                        'created_at': log.created_at.isoformat(),
                        'error_message': log.error_message
                    } for log in recent_logs
                ]
            }
        })
        
    except Exception as e:
        logger.error(f"獲取爬蟲狀態失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '獲取爬蟲狀態失敗'
        }), 500

@api_bp.route('/crawler/sources')
def get_crawler_sources():
    """獲取爬蟲來源統計"""
    try:
        sources = NewsSource.query.all()
        
        sources_data = []
        for source in sources:
            # 計算最近爬取時間
            last_log = CrawlLog.query.filter_by(source_id=source.id).order_by(desc(CrawlLog.created_at)).first()
            
            # 計算成功率
            total_crawls = source.successful_crawls + source.failed_crawls
            success_rate = round(source.successful_crawls / total_crawls * 100, 1) if total_crawls > 0 else 0
            
            sources_data.append({
                'id': source.id,
                'name': source.name,
                'url': source.url,
                'status': source.status,
                'total_news': source.total_news_count,
                'successful_crawls': source.successful_crawls,
                'failed_crawls': source.failed_crawls,
                'success_rate': success_rate,
                'reliability_score': round(source.reliability_score, 3),
                'last_crawl': last_log.created_at.isoformat() if last_log else None,
                'last_crawl_success': last_log.success if last_log else None
            })
        
        return jsonify({
            'status': 'success',
            'data': sources_data
        })
        
    except Exception as e:
        logger.error(f"獲取爬蟲來源失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '獲取爬蟲來源失敗'
        }), 500

@api_bp.route('/crawler/logs')
def get_crawler_logs():
    """獲取爬蟲日誌"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        source_id = request.args.get('source_id', type=int)
        
        query = CrawlLog.query.order_by(desc(CrawlLog.created_at))
        
        if source_id:
            query = query.filter_by(source_id=source_id)
        
        logs = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'logs': [
                    {
                        'id': log.id,
                        'source': log.source.name if log.source else 'Unknown',
                        'success': log.success,
                        'news_found': log.news_found,
                        'news_new': log.news_new,
                        'news_updated': log.news_updated,
                        'duration': round(log.duration, 2) if log.duration else None,
                        'created_at': log.created_at.isoformat(),
                        'error_message': log.error_message,
                        'error_type': log.error_type
                    } for log in logs.items
                ],
                'pagination': {
                    'page': logs.page,
                    'pages': logs.pages,
                    'per_page': logs.per_page,
                    'total': logs.total,
                    'has_next': logs.has_next,
                    'has_prev': logs.has_prev
                }
            }
        })
        
    except Exception as e:
        logger.error(f"獲取爬蟲日誌失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '獲取爬蟲日誌失敗'
        }), 500

@api_bp.route('/stats/dashboard')
def get_dashboard_stats():
    """獲取儀表板統計數據"""
    try:
        # 時間範圍
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        
        # 基本統計
        total_news = News.query.filter_by(status='active').count()
        total_sources = NewsSource.query.count()
        total_categories = NewsCategory.query.count()
        
        # 今日統計
        news_today = News.query.filter(
            News.crawled_date >= today_start,
            News.status == 'active'
        ).count()
        
        # 本週統計
        news_this_week = News.query.filter(
            News.crawled_date >= week_start,
            News.status == 'active'
        ).count()
        
        # 來源分佈
        source_stats = db.session.query(
            NewsSource.name,
            func.count(News.id).label('count')
        ).join(News).filter(News.status == 'active').group_by(NewsSource.name).all()
        
        # 分類分佈
        category_stats = db.session.query(
            NewsCategory.name,
            func.count(News.id).label('count')
        ).join(News).filter(News.status == 'active').group_by(NewsCategory.name).all()
        
        # 過去7天的新聞趨勢
        daily_stats = []
        for i in range(7):
            day_start = today_start - timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            count = News.query.filter(
                News.crawled_date >= day_start,
                News.crawled_date < day_end,
                News.status == 'active'
            ).count()
            
            daily_stats.append({
                'date': day_start.strftime('%Y-%m-%d'),
                'count': count
            })
        
        daily_stats.reverse()  # 按時間正序排列
        
        return jsonify({
            'status': 'success',
            'data': {
                'overview': {
                    'total_news': total_news,
                    'total_sources': total_sources,
                    'total_categories': total_categories,
                    'news_today': news_today,
                    'news_this_week': news_this_week
                },
                'source_distribution': [
                    {'name': name, 'count': count}
                    for name, count in source_stats
                ],
                'category_distribution': [
                    {'name': name, 'count': count}
                    for name, count in category_stats
                ],
                'daily_trend': daily_stats
            }
        })
        
    except Exception as e:
        logger.error(f"獲取儀表板統計失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '獲取儀表板統計失敗'
        }), 500

# 新增分析相關端點
@api_bp.route('/analysis/article/<int:article_id>')
def analyze_article(article_id):
    """分析單篇文章"""
    try:
        # 查找文章
        article = News.query.get_or_404(article_id)
        
        # 準備文章數據
        article_data = {
            'title': article.title,
            'content': article.content,
            'published_date': article.published_date,
            'source': article.source.name if article.source else None
        }
        
        # 執行分析
        analysis_result = analyze_news_article(article_data)
        
        return jsonify({
            'status': 'success',
            'data': analysis_result
        })
        
    except Exception as e:
        logger.error(f"文章分析失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '文章分析失敗'
        }), 500

@api_bp.route('/analysis/trends')
def get_trends():
    """獲取新聞趨勢分析"""
    try:
        # 獲取時間範圍參數
        days = request.args.get('days', 30, type=int)
        days = min(max(days, 1), 90)  # 限制在1-90天之間
        
        # 獲取指定時間範圍內的文章
        cutoff_date = datetime.now() - timedelta(days=days)
        articles = News.query.filter(
            News.published_date >= cutoff_date,
            News.status == 'active'
        ).all()
        
        if not articles:
            return jsonify({
                'status': 'success',
                'data': {
                    'message': '指定時間範圍內沒有找到文章',
                    'trends': {},
                    'hot_topics': [],
                    'sentiment_trend': {}
                }
            })
        
        # 準備文章數據
        articles_data = []
        for article in articles:
            articles_data.append({
                'title': article.title,
                'content': article.content,
                'published_date': article.published_date,
                'source': article.source.name if article.source else None
            })
        
        # 執行趨勢分析
        analyzer = get_analyzer()
        trend_result = analyzer.analyze_trends(articles_data, days)
        
        return jsonify({
            'status': 'success',
            'data': trend_result
        })
        
    except Exception as e:
        logger.error(f"趨勢分析失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '趨勢分析失敗'
        }), 500

@api_bp.route('/analysis/keywords')
def get_keywords():
    """獲取熱門關鍵詞"""
    try:
        # 獲取參數
        days = request.args.get('days', 7, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        # 獲取最近文章
        cutoff_date = datetime.now() - timedelta(days=days)
        articles = News.query.filter(
            News.published_date >= cutoff_date,
            News.status == 'active'
        ).all()
        
        if not articles:
            return jsonify({
                'status': 'success',
                'data': {
                    'keywords': [],
                    'total_articles': 0
                }
            })
        
        # 提取所有關鍵詞
        analyzer = get_analyzer()
        all_keywords = []
        
        for article in articles:
            text = f"{article.title} {article.content}"
            keywords = analyzer.extract_keywords(text, top_k=10)
            all_keywords.extend(keywords)
        
        # 統計關鍵詞頻率
        from collections import Counter
        keyword_freq = Counter()
        for keyword, weight in all_keywords:
            keyword_freq[keyword] += weight
        
        # 獲取最熱門的關鍵詞
        top_keywords = [
            {'keyword': keyword, 'weight': weight}
            for keyword, weight in keyword_freq.most_common(limit)
        ]
        
        return jsonify({
            'status': 'success',
            'data': {
                'keywords': top_keywords,
                'total_articles': len(articles),
                'analysis_period': f'{days} 天'
            }
        })
        
    except Exception as e:
        logger.error(f"關鍵詞分析失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '關鍵詞分析失敗'
        }), 500

@api_bp.route('/analysis/sentiment')
def get_sentiment_analysis():
    """獲取情感分析統計"""
    try:
        # 獲取參數
        days = request.args.get('days', 7, type=int)
        
        # 獲取最近文章
        cutoff_date = datetime.now() - timedelta(days=days)
        articles = News.query.filter(
            News.published_date >= cutoff_date,
            News.status == 'active'
        ).all()
        
        if not articles:
            return jsonify({
                'status': 'success',
                'data': {
                    'sentiment_distribution': {},
                    'daily_sentiment': {},
                    'total_articles': 0
                }
            })
        
        # 執行情感分析
        analyzer = get_analyzer()
        sentiment_stats = {'positive': 0, 'negative': 0, 'neutral': 0}
        daily_sentiment = {}
        
        for article in articles:
            text = f"{article.title} {article.content}"
            sentiment = analyzer.analyze_sentiment(text)
            
            # 統計整體情感分布
            sentiment_stats[sentiment['sentiment']] += 1
            
            # 按日期統計情感
            date_str = article.published_date.strftime('%Y-%m-%d')
            if date_str not in daily_sentiment:
                daily_sentiment[date_str] = {
                    'positive': 0, 'negative': 0, 'neutral': 0,
                    'average_score': 0, 'scores': []
                }
            
            daily_sentiment[date_str][sentiment['sentiment']] += 1
            daily_sentiment[date_str]['scores'].append(sentiment['score'])
        
        # 計算每日平均情感分數
        for date_data in daily_sentiment.values():
            if date_data['scores']:
                date_data['average_score'] = sum(date_data['scores']) / len(date_data['scores'])
            del date_data['scores']  # 不需要返回原始分數
        
        return jsonify({
            'status': 'success',
            'data': {
                'sentiment_distribution': sentiment_stats,
                'daily_sentiment': daily_sentiment,
                'total_articles': len(articles),
                'analysis_period': f'{days} 天'
            }
        })
        
    except Exception as e:
        logger.error(f"情感分析失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '情感分析失敗'
        }), 500

@api_bp.route('/analysis/clustering')
def get_clustering():
    """獲取文章聚類分析"""
    try:
        # 獲取參數
        days = request.args.get('days', 30, type=int)
        clusters = request.args.get('clusters', 5, type=int)
        
        # 獲取最近文章
        cutoff_date = datetime.now() - timedelta(days=days)
        articles = News.query.filter(
            News.published_date >= cutoff_date,
            News.status == 'active'
        ).all()
        
        if len(articles) < 2:
            return jsonify({
                'status': 'success',
                'data': {
                    'message': '文章數量不足，無法進行聚類分析',
                    'clusters': {},
                    'total_articles': len(articles)
                }
            })
        
        # 準備文章數據
        articles_data = []
        for article in articles:
            articles_data.append({
                'id': article.id,
                'title': article.title,
                'content': article.content,
                'published_date': article.published_date,
                'source': article.source.name if article.source else None
            })
        
        # 執行聚類分析
        analyzer = get_analyzer()
        clustering_result = analyzer.cluster_articles(articles_data, clusters)
        
        return jsonify({
            'status': 'success',
            'data': clustering_result
        })
        
    except Exception as e:
        logger.error(f"聚類分析失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '聚類分析失敗'
        }), 500

@api_bp.route('/feedback/submit', methods=['POST'])
def submit_feedback():
    """提交用戶反饋"""
    try:
        # 獲取請求數據
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': '未提供有效數據'
            }), 400
        
        # 檢查必填字段
        required_fields = ['category', 'rating']
        if not all(field in data for field in required_fields):
            return jsonify({
                'status': 'error',
                'message': '缺少必填字段'
            }), 400
            
        # 匿名用戶ID
        user_id = 0
        
        # 導入反饋管理器
        from src.services.user_feedback import FeedbackManager
        feedback_manager = FeedbackManager()
        
        # 添加反饋
        feedback = feedback_manager.add_feedback(
            user_id=user_id,
            category=data.get('category'),
            rating=int(data.get('rating')),
            message=data.get('message', ''),
            features=data.get('features', []),
            source=data.get('source', 'api'),
            metadata=data.get('metadata', {})
        )
        
        if feedback:
            return jsonify({
                'status': 'success',
                'message': '反饋提交成功',
                'id': feedback.id
            }), 201
        else:
            return jsonify({
                'status': 'error',
                'message': '反饋提交失敗'
            }), 500
            
    except Exception as e:
        logger.error(f"API提交反饋失敗: {e}")
        return jsonify({
            'status': 'error',
            'message': f'處理請求時出錯: {str(e)}'
        }), 500

@api_bp.route('/analysis/similar/<int:article_id>')
def get_similar_articles(article_id):
    """獲取相似文章"""
    try:
        # 查找目標文章
        target_article = News.query.get_or_404(article_id)
        target_text = f"{target_article.title} {target_article.content}"
        
        # 獲取其他文章
        other_articles = News.query.filter(
            News.id != article_id,
            News.status == 'active'
        ).limit(100).all()  # 限制比較範圍以提高性能
        
        if not other_articles:
            return jsonify({
                'status': 'success',
                'data': {
                    'similar_articles': [],
                    'message': '沒有找到其他文章進行比較'
                }
            })
        
        # 準備文章文本列表
        article_texts = []
        article_info = []
        for article in other_articles:
            article_texts.append(f"{article.title} {article.content}")
            article_info.append({
                'id': article.id,
                'title': article.title,
                'published_date': article.published_date.isoformat(),
                'source': article.source.name if article.source else None
            })
        
        # 找出相似文章
        analyzer = get_analyzer()
        similar_indices = analyzer.find_similar_articles(target_text, article_texts, top_k=10)
        
        # 組織結果
        similar_articles = []
        for idx, similarity in similar_indices:
            article_data = article_info[idx].copy()
            article_data['similarity'] = float(similarity)
            similar_articles.append(article_data)
        
        return jsonify({
            'status': 'success',
            'data': {
                'target_article': {
                    'id': target_article.id,
                    'title': target_article.title
                },
                'similar_articles': similar_articles
            }
        })
        
    except Exception as e:
        logger.error(f"相似文章查找失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '相似文章查找失敗'
        }), 500

# 日期過濾器控制端點
@api_bp.route('/crawler/date-filter', methods=['GET'])
def get_date_filter_status():
    """獲取日期過濾器狀態"""
    try:
        manager = get_crawler_manager()
        status = manager.date_filter.get_status()
        
        return jsonify({
            'status': 'success',
            'data': status
        })
        
    except Exception as e:
        logger.error(f"獲取日期過濾器狀態失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '獲取狀態失敗'
        }), 500

@api_bp.route('/crawler/date-filter', methods=['POST'])
def update_date_filter():
    """更新日期過濾器設定"""
    try:
        data = request.get_json() or {}
        
        max_age_days = data.get('max_age_days')
        enable_filter = data.get('enable_filter')
        
        # 驗證參數
        if max_age_days is not None:
            if not isinstance(max_age_days, int) or max_age_days < 1 or max_age_days > 365:
                return jsonify({
                    'status': 'error',
                    'message': '最大天數必須是1-365之間的整數'
                }), 400
        
        if enable_filter is not None:
            if not isinstance(enable_filter, bool):
                return jsonify({
                    'status': 'error',
                    'message': '啟用狀態必須是布林值'
                }), 400
        
        # 更新設定
        manager = get_crawler_manager()
        result = manager.update_date_filter_settings(
            max_age_days=max_age_days,
            enable_filter=enable_filter
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"更新日期過濾器設定失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '更新設定失敗'
        }), 500

@api_bp.route('/crawler/status-with-filter')
def get_crawler_status_with_filter():
    """獲取爬蟲完整狀態（包含日期過濾器）"""
    try:
        manager = get_crawler_manager()
        status = manager.get_crawler_status()
        
        return jsonify({
            'status': 'success',
            'data': status
        })
        
    except Exception as e:
        logger.error(f"獲取爬蟲狀態失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '獲取狀態失敗'
        }), 500

@api_bp.route('/news/cleanup', methods=['POST'])
def cleanup_old_news():
    """清理超過指定天數的舊新聞"""
    try:
        data = request.get_json() or {}
        days = data.get('days', 7)
        dry_run = data.get('dry_run', True)
        
        # 驗證參數
        if not isinstance(days, int) or days < 1 or days > 365:
            return jsonify({
                'status': 'error',
                'message': '天數必須是1-365之間的整數'
            }), 400
        
        # 導入清理服務
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from auto_cleanup_service import NewsCleanupService
        
        service = NewsCleanupService(max_age_days=days)
        
        if dry_run:
            # 試運行模式，只統計不實際刪除
            import sqlite3
            from datetime import datetime, timezone, timedelta
            
            conn = sqlite3.connect(service.db_path)
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            
            cursor.execute("""
                SELECT COUNT(*) 
                FROM news 
                WHERE (published_date < ? OR crawled_date < ?)
                AND status = 'active'
            """, (cutoff_date, cutoff_date))
            
            old_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM news WHERE status = 'active'")
            active_count = cursor.fetchone()[0]
            
            conn.close()
            
            return jsonify({
                'status': 'success',
                'message': f'找到 {old_count} 條超過 {days} 天的舊新聞',
                'data': {
                    'old_news_count': old_count,
                    'active_news_count': active_count,
                    'will_remain': active_count - old_count,
                    'dry_run': True
                }
            })
        else:
            # 實際執行清理
            success = service.cleanup_old_news()
            
            if success:
                status = service.get_status()
                return jsonify({
                    'status': 'success',
                    'message': '舊新聞清理完成',
                    'data': status
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': '清理失敗'
                }), 500
        
    except Exception as e:
        logger.error(f"新聞清理失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'清理操作失敗: {str(e)}'
        }), 500

@api_bp.route('/news/cleanup/status')
def get_cleanup_status():
    """獲取新聞清理狀態"""
    try:
        from auto_cleanup_service import NewsCleanupService
        
        service = NewsCleanupService()
        status = service.get_status()
        
        if status:
            return jsonify({
                'status': 'success',
                'data': status
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '無法獲取清理狀態'
            }), 500
            
    except Exception as e:
        logger.error(f"獲取清理狀態失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '獲取狀態失敗'
        }), 500
