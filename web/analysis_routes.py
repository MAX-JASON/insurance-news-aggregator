"""
分析相關的Web路由
提供新聞分析的前端界面
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from datetime import datetime, timedelta
from database.models import News, NewsSource, NewsCategory, db
from sqlalchemy import desc, func
import json

# 延遲導入分析引擎以避免循環依賴
def get_analyzer_safe():
    """安全獲取分析引擎"""
    try:
        from analyzer.engine import get_analyzer
        return get_analyzer()
    except Exception as e:
        print(f"分析引擎導入錯誤: {e}")
        return None

def analyze_news_article_safe(article_data):
    """安全分析文章"""
    try:
        from analyzer.engine import analyze_news_article
        return analyze_news_article(article_data)
    except Exception as e:
        print(f"文章分析錯誤: {e}")
        return {
            'keywords': [],
            'sentiment_analysis': {'sentiment': 'neutral', 'score': 0.0},
            'classification': {'category': 'unknown', 'confidence': 0.0},
            'summary': '分析功能暫時不可用'
        }

analysis_bp = Blueprint('analysis', __name__, url_prefix='/analysis')

@analysis_bp.route('/')
def dashboard():
    """分析儀表板主頁"""
    try:
        # 獲取統計數據
        total_news = News.query.filter_by(status='active').count()
        recent_news = News.query.filter_by(status='active').order_by(desc(News.created_at)).limit(10).all()
        
        # 獲取分析器
        analyzer = get_analyzer_safe()
        
        # 分析最近新聞的情感分布
        sentiment_stats = {'positive': 0, 'negative': 0, 'neutral': 0}
        if analyzer:
            for news in recent_news:
                text = f"{news.title} {news.content}"
                sentiment = analyzer.analyze_sentiment(text)
                sentiment_stats[sentiment['sentiment']] += 1
        
        return render_template('analysis/dashboard.html',
                             total_news=total_news,
                             recent_news=recent_news,
                             sentiment_stats=sentiment_stats)
    except Exception as e:
        flash(f'載入分析儀表板失敗: {str(e)}', 'error')
        return render_template('analysis/dashboard.html',
                             total_news=0,
                             recent_news=[],
                             sentiment_stats={'positive': 0, 'negative': 0, 'neutral': 0})

@analysis_bp.route('/article/<int:article_id>')
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
        analysis_result = analyze_news_article_safe(article_data)
        
        return render_template('analysis/article_detail.html',
                             article=article,
                             analysis=analysis_result)
    except Exception as e:
        flash(f'文章分析失敗: {str(e)}', 'error')
        return redirect(url_for('analysis.dashboard'))

@analysis_bp.route('/trends')
def trends():
    """趨勢分析頁面"""
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
        
        trend_data = {}
        hot_keywords = []
        
        if articles:
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
            
            trend_data = trend_result
            hot_keywords = trend_result.get('hot_topics', [])[:20]
        
        return render_template('analysis/trends.html',
                             trend_data=trend_data,
                             hot_keywords=hot_keywords,
                             articles_count=len(articles),
                             time_range=days)
    except Exception as e:
        flash(f'趨勢分析失敗: {str(e)}', 'error')
        return render_template('analysis/trends.html',
                             trend_data={},
                             hot_keywords=[],
                             articles_count=0,
                             time_range=days)

@analysis_bp.route('/keywords')
def keywords():
    """關鍵詞分析頁面"""
    try:
        # 獲取參數
        days = request.args.get('days', 7, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        # 獲取最近文章
        cutoff_date = datetime.now() - timedelta(days=days)
        articles = News.query.filter(
            News.published_date >= cutoff_date,
            News.status == 'active'
        ).all()
        
        keywords_data = []
        
        if articles:
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
            keywords_data = [
                {'keyword': keyword, 'weight': weight}
                for keyword, weight in keyword_freq.most_common(limit)
            ]
        
        return render_template('analysis/keywords.html',
                             keywords_data=keywords_data,
                             articles_count=len(articles),
                             time_range=days)
    except Exception as e:
        flash(f'關鍵詞分析失敗: {str(e)}', 'error')
        return render_template('analysis/keywords.html',
                             keywords_data=[],
                             articles_count=0,
                             time_range=days)

@analysis_bp.route('/sentiment')
def sentiment():
    """情感分析頁面"""
    try:
        # 獲取參數
        days = request.args.get('days', 7, type=int)
        
        # 獲取最近文章
        cutoff_date = datetime.now() - timedelta(days=days)
        articles = News.query.filter(
            News.published_date >= cutoff_date,
            News.status == 'active'
        ).all()
        
        sentiment_data = {
            'distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
            'daily_trend': {},
            'recent_articles': []
        }
        
        if articles:
            # 執行情感分析
            analyzer = get_analyzer()
            daily_sentiment = {}
            
            for article in articles:
                text = f"{article.title} {article.content}"
                sentiment_result = analyzer.analyze_sentiment(text)
                
                # 統計整體情感分布
                sentiment_data['distribution'][sentiment_result['sentiment']] += 1
                
                # 按日期統計情感
                date_str = article.published_date.strftime('%Y-%m-%d')
                if date_str not in daily_sentiment:
                    daily_sentiment[date_str] = {
                        'positive': 0, 'negative': 0, 'neutral': 0,
                        'scores': []
                    }
                
                daily_sentiment[date_str][sentiment_result['sentiment']] += 1
                daily_sentiment[date_str]['scores'].append(sentiment_result['score'])
                
                # 收集最近文章的情感分析結果
                if len(sentiment_data['recent_articles']) < 10:
                    sentiment_data['recent_articles'].append({
                        'id': article.id,
                        'title': article.title,
                        'sentiment': sentiment_result['sentiment'],
                        'score': sentiment_result['score'],
                        'published_date': article.published_date
                    })
            
            # 計算每日平均情感分數
            for date, data in daily_sentiment.items():
                if data['scores']:
                    data['average_score'] = sum(data['scores']) / len(data['scores'])
                del data['scores']  # 不需要在前端顯示
            
            sentiment_data['daily_trend'] = daily_sentiment
        
        return render_template('analysis/sentiment.html',
                             sentiment_data=sentiment_data,
                             articles_count=len(articles),
                             time_range=days)
    except Exception as e:
        flash(f'情感分析失敗: {str(e)}', 'error')
        return render_template('analysis/sentiment.html',
                             sentiment_data={
                                 'distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
                                 'daily_trend': {},
                                 'recent_articles': []
                             },
                             articles_count=0,
                             time_range=days)

@analysis_bp.route('/clustering')
def clustering():
    """聚類分析頁面"""
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
        
        clustering_data = {
            'clusters': {},
            'cluster_centers': [],
            'total_articles': len(articles)
        }
        
        if len(articles) >= 3:  # 至少需要3篇文章才能聚類
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
            clustering_data.update(clustering_result)
        
        return render_template('analysis/clustering.html',
                             clustering_data=clustering_data,
                             time_range=days,
                             cluster_count=clusters)
    except Exception as e:
        flash(f'聚類分析失敗: {str(e)}', 'error')
        return render_template('analysis/clustering.html',
                             clustering_data={
                                 'clusters': {},
                                 'cluster_centers': [],
                                 'total_articles': 0
                             },
                             time_range=days,
                             cluster_count=clusters)

# API端點 - 為前端AJAX請求提供JSON數據
@analysis_bp.route('/api/keywords/<int:days>')
def api_keywords(days):
    """關鍵詞API"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        articles = News.query.filter(
            News.published_date >= cutoff_date,
            News.status == 'active'
        ).all()
        
        if not articles:
            return jsonify({'keywords': [], 'count': 0})
        
        analyzer = get_analyzer()
        all_keywords = []
        
        for article in articles:
            text = f"{article.title} {article.content}"
            keywords = analyzer.extract_keywords(text, top_k=10)
            all_keywords.extend(keywords)
        
        from collections import Counter
        keyword_freq = Counter()
        for keyword, weight in all_keywords:
            keyword_freq[keyword] += weight
        
        keywords_data = [
            {'text': keyword, 'value': weight}
            for keyword, weight in keyword_freq.most_common(50)
        ]
        
        return jsonify({'keywords': keywords_data, 'count': len(articles)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/api/sentiment/<int:days>')
def api_sentiment(days):
    """情感分析API"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        articles = News.query.filter(
            News.published_date >= cutoff_date,
            News.status == 'active'
        ).all()
        
        if not articles:
            return jsonify({'data': [], 'distribution': {}})
        
        analyzer = get_analyzer()
        daily_data = {}
        distribution = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for article in articles:
            text = f"{article.title} {article.content}"
            sentiment = analyzer.analyze_sentiment(text)
            
            date_str = article.published_date.strftime('%Y-%m-%d')
            if date_str not in daily_data:
                daily_data[date_str] = {'positive': 0, 'negative': 0, 'neutral': 0}
            
            daily_data[date_str][sentiment['sentiment']] += 1
            distribution[sentiment['sentiment']] += 1
        
        # 轉換為圖表數據格式
        chart_data = []
        for date, counts in sorted(daily_data.items()):
            chart_data.append({
                'date': date,
                'positive': counts['positive'],
                'negative': counts['negative'],
                'neutral': counts['neutral']
            })
        
        return jsonify({
            'data': chart_data,
            'distribution': distribution,
            'total': len(articles)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
