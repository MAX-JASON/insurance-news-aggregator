"""
業務員專用路由模組
Business Routes Module

提供業務員專用的功能和界面，包括儀表板、分析工具和客戶分享功能
"""

from flask import Blueprint, render_template, request, jsonify, send_file, current_app, make_response, url_for, session
from database.models import News, NewsSource, NewsCategory, User, SavedNews, db
from sqlalchemy import desc, func, and_, or_
from datetime import datetime, timedelta
import logging
import os
import tempfile
import io
from io import BytesIO
import json
from flask_paginate import Pagination, get_page_parameter

import random

# 創建業務員藍圖
business_bp = Blueprint('business', __name__, url_prefix='/business')

# 獲取日誌器
logger = logging.getLogger('business')

@business_bp.route('/')
def index():
    """業務員主頁面"""
    return render_template('business/index.html')

@business_bp.route('/cyber-news')
def cyber_news():
    """賽博朋克風格新聞中心"""
    return render_template('business/cyber_news_center.html')

@business_bp.route('/dashboard')
def dashboard():
    """業務員儀表板"""
    try:
        logger.info("業務員儀表板訪問")
        
        # 獲取今日重點新聞（按重要性評分排序）
        important_news = News.query.filter(
            News.status == 'active',
            News.importance_score >= 0.5
        ).order_by(
            desc(News.importance_score), desc(News.published_date)
        ).limit(5).all()
        
        # 計算時間範圍
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        
        # 過去7天的日期列表（用於趨勢圖表）
        days = [(today - timedelta(days=i)).strftime('%m-%d') for i in range(6, -1, -1)]
        
        # 每日新聞數量統計
        news_count = []
        importance_avg = []
        
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            # 當天新聞數量
            daily_count = News.query.filter(
                func.date(News.published_date) == date,
                News.status == 'active'
            ).count()
            news_count.append(daily_count)
            
            # 當天平均重要性
            avg_importance = db.session.query(
                func.avg(News.importance_score).label('avg_importance')
            ).filter(
                func.date(News.published_date) == date,
                News.status == 'active',
                News.importance_score.isnot(None)
            ).scalar()
            
            # 轉換為百分比格式，如果為None則設為0
            importance_avg.append(round((avg_importance or 0) * 100, 1))
        
        # 業務影響分析
        business_impact_news = []
        for news in News.query.filter(
            News.status == 'active',
            News.importance_score >= 0.6
        ).order_by(desc(News.published_date)).limit(10).all():
            # 計算業務影響分數
            impact_score = calculate_business_impact_score(news)
            
            # 決定影響級別
            if impact_score >= 0.7:
                impact_level = '高'
            elif impact_score >= 0.4:
                impact_level = '中'
            else:
                impact_level = '低'
                
            # 分析業務影響類型和行動
            impact_analysis = analyze_business_impact(news)
            
            # 提取類型和行動
            if ':' in impact_analysis:
                parts = impact_analysis.split(':', 1)
                impact_type = parts[0].strip()
                impact_action = parts[1].strip()
            else:
                impact_type = '一般業務影響'
                impact_action = impact_analysis
            
            # 構建業務影響新聞物件
            news_with_impact = {
                'id': news.id,
                'title': news.title,
                'published_date': news.published_date,
                'impact_level': impact_level,
                'impact_type': impact_type,
                'impact_action': impact_action
            }
            
            business_impact_news.append(news_with_impact)
        
        # 客戶興趣分析
        client_interest_news = []
        for news in News.query.filter(
            News.status == 'active'
        ).order_by(desc(News.view_count), desc(News.published_date)).limit(5).all():
            # 計算客戶興趣級別
            client_interest = calculate_client_interest(news)
            
            # 根據興趣級別推測原因
            if client_interest == 'high':
                interest_level = '高'
                interest_reason = '客戶極有可能詢問此議題，建議主動說明'
            elif client_interest == 'medium':
                interest_level = '中'
                interest_reason = '話題性較高，可納入客戶溝通素材'
            else:
                interest_level = '低'
                interest_reason = '可作為一般資訊提供'
                
            # 構建客戶興趣新聞物件
            news_with_interest = {
                'id': news.id,
                'title': news.title,
                'published_date': news.published_date,
                'interest_level': interest_level,
                'interest_reason': interest_reason
            }
            
            client_interest_news.append(news_with_interest)
            
        # 分類統計
        category_stats = []
        categories = db.session.query(
            NewsCategory.name, func.count(News.id).label('count')
        ).join(
            News, News.category_id == NewsCategory.id
        ).filter(
            News.status == 'active'
        ).group_by(
            NewsCategory.name
        ).order_by(
            desc('count')
        ).limit(5).all()
        
        for category in categories:
            category_stats.append((category.name, category.count))
            
        return render_template('business/dashboard.html',
                             important_news=important_news,
                             business_impact_news=business_impact_news,
                             client_interest_news=client_interest_news,
                             priority_news=important_news,  # 兼容現有模板
                             days=days,
                             news_count=news_count,
                             importance_avg=importance_avg,
                             category_stats=category_stats)
        
    except Exception as e:
        logger.error(f"業務員儀表板載入錯誤: {str(e)}")
        return render_template('business/dashboard.html',
                             important_news=[],
                             business_impact_news=[],
                             client_interest_news=[],
                             priority_news=[],  # 兼容現有模板
                             days=[''] * 7,
                             news_count=[0] * 7,
                             importance_avg=[0] * 7,
                             category_stats=[])

@business_bp.route('/priority-news')
def priority_news():
    """優先新聞列表頁面"""
    try:
        logger.info("優先新聞頁面訪問")
        
        # 分頁參數
        page = request.args.get(get_page_parameter(), type=int, default=1)
        per_page = 12  # 每頁顯示12條新聞
        
        # 獲取有重要性分數的新聞
        news_query = News.query.filter(
            News.status == 'active',
            News.importance_score.isnot(None)
        ).order_by(desc(News.importance_score), desc(News.published_date))
        
        # 計算分頁
        total = news_query.count()
        pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')
        
        # 獲取當前頁的記錄
        priority_news = news_query.paginate(page=page, per_page=per_page, error_out=False).items
        
        # 為每條新聞添加業務影響分析
        for news in priority_news:
            # 添加業務影響評分（從0到1）
            news.business_impact_score = calculate_business_impact_score(news)
            # 獲取業務影響描述
            news.business_impact = analyze_business_impact(news)
        
        return render_template('business/priority_news.html',
                             priority_news=priority_news,
                             pagination=pagination)
        
    except Exception as e:
        logger.error(f"載入優先新聞列表錯誤: {str(e)}")
        return render_template('business/priority_news.html',
                             priority_news=[],
                             pagination=None)

@business_bp.route('/api/dashboard')
def api_dashboard():
    """業務員儀表板API數據"""
    try:
        # 獲取統計數據
        total_news = News.query.filter_by(status='active').count()
        today = datetime.now().date()
        today_news = News.query.filter(
            func.date(News.crawled_date) == today,
            News.status == 'active'
        ).count()
        
        # 重要性分析
        high_importance = News.query.filter(
            News.importance_score >= 0.7,
            News.status == 'active'
        ).count()
        
        # 客戶關注度分析
        client_interest_high = News.query.filter(
            News.view_count > 100,
            News.status == 'active'
        ).count()
        
        return jsonify({
            'status': 'success',
            'data': {
                'totalNews': total_news,
                'todayNews': today_news,
                'highImportance': high_importance,
                'clientInterestHigh': client_interest_high,
                'lastUpdated': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"業務員儀表板API錯誤: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '無法獲取業務數據',
            'error': str(e)
        }), 500
        
@business_bp.route('/api/importance-distribution')
def api_importance_distribution():
    """獲取重要性分布數據"""
    try:
        # 查詢各重要性級別的新聞數量
        high_count = News.query.filter(
            News.importance_score >= 0.7,
            News.status == 'active'
        ).count()
        
        medium_count = News.query.filter(
            News.importance_score < 0.7,
            News.importance_score >= 0.4,
            News.status == 'active'
        ).count()
        
        low_count = News.query.filter(
            News.importance_score < 0.4,
            News.importance_score.isnot(None),
            News.status == 'active'
        ).count()
        
        # 返回圖表數據
        return jsonify({
            'status': 'success',
            'data': {
                'labels': ['高重要性', '中重要性', '低重要性'],
                'values': [high_count, medium_count, low_count]
            }
        })
        
    except Exception as e:
        logger.error(f"獲取重要性分布數據錯誤: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '無法獲取重要性分布數據',
            'error': str(e)
        }), 500

@business_bp.route('/api/priority-news')
def api_priority_news():
    """獲取優先新聞"""
    try:
        # 根據重要性評分和業務相關性排序
        news_list = News.query.filter_by(status='active').order_by(
            desc(News.importance_score), desc(News.view_count)
        ).limit(10).all()
        
        priority_news = []
        for news in news_list:
            # 計算業務影響分析
            business_impact = analyze_business_impact(news)
            
            news_data = {
                'id': news.id,
                'title': news.title,
                'summary': news.summary,
                'importance_score': news.importance_score or 0,
                'business_impact': business_impact,
                'client_interest': calculate_client_interest(news),
                'opportunity_score': calculate_opportunity_score(news),
                'published_date': news.published_date.isoformat() if news.published_date else None,
                'source': news.source.name if news.source else '未知來源'
            }
            priority_news.append(news_data)
        
        return jsonify({
            'status': 'success',
            'data': priority_news
        })
        
    except Exception as e:
        logger.error(f"獲取優先新聞錯誤: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '無法獲取優先新聞',
            'error': str(e)
        }), 500

@business_bp.route('/tools/share/<int:news_id>')
def share_tools(news_id):
    """新聞分享工具頁面"""
    try:
        news = News.query.get_or_404(news_id)
        
        # 生成分享模板
        share_templates = generate_share_templates(news)
        
        return render_template('business/share_tools.html',
                             news=news,
                             share_templates=share_templates)
        
    except Exception as e:
        logger.error(f"分享工具錯誤: {str(e)}")
        return "分享工具暫時無法使用", 500

@business_bp.route('/api/daily-report')
def api_daily_report():
    """生成今日業務報告"""
    try:
        today = datetime.now().date()
        
        # 今日重點新聞
        today_news = News.query.filter(
            func.date(News.crawled_date) == today,
            News.status == 'active'
        ).order_by(desc(News.importance_score)).limit(10).all()
        
        # 生成報告數據
        report_data = {
            'date': today.isoformat(),
            'summary': {
                'total_news': len(today_news),
                'high_importance': len([n for n in today_news if (n.importance_score or 0) >= 0.7]),
                'client_topics': 4,
                'business_opportunities': 2
            },
            'priority_news': [
                {
                    'title': news.title,
                    'importance': '★★★' if (news.importance_score or 0) >= 0.8 else '★★☆' if (news.importance_score or 0) >= 0.5 else '★☆☆',
                    'business_impact': analyze_business_impact(news),
                    'source': news.source.name if news.source else '未知來源'
                } for news in today_news[:5]
            ]
        }
        
        return jsonify({
            'status': 'success',
            'data': report_data
        })
        
    except Exception as e:
        logger.error(f"生成今日報告錯誤: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '無法生成今日報告',
            'error': str(e)
        }), 500

@business_bp.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    """生成PDF分享文件API"""
    try:
        # 獲取請求數據
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'message': '未提供數據'}), 400
        
        # 提取數據
        share_type = data.get('type', '')
        title = data.get('title', '')
        content = data.get('content', '')
        news_title = data.get('newsTitle', '')
        news_source = data.get('newsSource', '')
        news_summary = data.get('newsSummary', '')
        news_importance = data.get('newsImportance', '')
        
        logger.info(f"生成PDF分享: {share_type} - {news_title[:30]}...")
        
        try:
            # 嘗試導入PDF生成庫
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            
            # 註冊中文字體 (需先確認字體檔案存在)
            font_path = os.path.join(current_app.root_path, '..', 'web', 'static', 'fonts', 'NotoSansTC-Regular.ttf')
            if not os.path.exists(font_path):
                logger.warning("中文字體檔案不存在，嘗試使用系統字體")
                # 可能的系統字體路徑，根據作業系統不同可能需要調整
                system_fonts = [
                    'C:/Windows/Fonts/msjh.ttc',  # Windows Microsoft JhengHei
                    '/System/Library/Fonts/PingFang.ttc',  # macOS
                    '/usr/share/fonts/truetype/arphic/uming.ttc'  # Linux
                ]
                
                for f in system_fonts:
                    if os.path.exists(f):
                        font_path = f
                        break
            
            # 註冊中文字體
            try:
                pdfmetrics.registerFont(TTFont('NotoSans', font_path))
                has_chinese_font = True
            except Exception as font_error:
                logger.error(f"無法註冊中文字體: {font_error}")
                has_chinese_font = False
            
            # 創建PDF緩衝區
            buffer = BytesIO()
            
            # 創建PDF文檔
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            
            # 創建中文樣式
            if has_chinese_font:
                styles.add(ParagraphStyle(
                    name='ChineseBody',
                    fontName='NotoSans',
                    fontSize=10,
                    leading=14,
                    spaceAfter=12
                ))
                styles.add(ParagraphStyle(
                    name='ChineseHeading',
                    fontName='NotoSans',
                    fontSize=14,
                    leading=18,
                    spaceAfter=10,
                    bold=True
                ))
                body_style = styles['ChineseBody']
                heading_style = styles['ChineseHeading']
            else:
                # 如果無法使用中文字體，則使用預設樣式
                body_style = styles['BodyText']
                heading_style = styles['Heading2']
            
            # 準備PDF內容
            content_elements = []
            
            # 標題
            content_elements.append(Paragraph("保險新聞專業分享", styles['Title']))
            content_elements.append(Spacer(1, 20))
            
            # 新聞資訊
            content_elements.append(Paragraph(news_title, heading_style))
            content_elements.append(Spacer(1, 10))
            content_elements.append(Paragraph(f"來源: {news_source}", styles['Italic']))
            content_elements.append(Paragraph(f"重要度: {news_importance}", styles['Italic']))
            content_elements.append(Spacer(1, 20))
            
            # 新聞摘要
            content_elements.append(Paragraph("新聞摘要", heading_style))
            content_elements.append(Paragraph(news_summary, body_style))
            content_elements.append(Spacer(1, 20))
            
            # 分享內容
            content_elements.append(Paragraph(title, heading_style))
            
            # 處理內容中的換行符
            paragraphs = content.split('\n')
            for para in paragraphs:
                if para.strip():
                    content_elements.append(Paragraph(para, body_style))
                else:
                    content_elements.append(Spacer(1, 10))
            
            content_elements.append(Spacer(1, 30))
            
            # 頁腳
            content_elements.append(Paragraph("此份資料由您的保險業務專員提供", styles['Italic']))
            content_elements.append(Paragraph(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Italic']))
            
            # 生成PDF
            doc.build(content_elements)
            
            # 獲取PDF內容
            pdf_content = buffer.getvalue()
            buffer.close()
            
            # 創建響應
            response = make_response(pdf_content)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'attachment; filename=insurance_news_share.pdf'
            
            return response
            
        except ImportError as e:
            logger.error(f"缺少PDF生成庫: {e}")
            return jsonify({
                'status': 'error',
                'message': '缺少生成PDF所需的庫，請確認已安裝 reportlab 庫',
                'details': str(e)
            }), 500
    
    except Exception as e:
        logger.error(f"生成PDF錯誤: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'無法生成PDF: {str(e)}',
        }), 500

def calculate_business_impact_score(news):
    """計算新聞的業務影響分數（0-1之間）"""
    try:
        from analyzer.importance_rating import ImportanceRater
        
        # 初始化評分器
        rater = ImportanceRater()
        
        # 使用評分器計算業務影響分數
        return rater.calculate_business_impact_score(news)
        
    except (ImportError, AttributeError):
        logger.warning("無法使用重要性評分模組計算業務影響分數，使用簡易計算")
        
        # 簡易業務影響評分邏輯
        business_keywords = {
            '理賠': 0.95, '保費': 0.8, '法規': 0.9, '政策': 0.85,
            '數位': 0.7, '競爭': 0.75, '新產品': 0.8, '客戶': 0.7,
            '風險': 0.65, '投資': 0.6, '長照': 0.7, '醫療': 0.7
        }
        
        title_content = ((news.title or '') + ' ' + (news.summary or '')).lower()
        
        # 計算基礎分數
        base_score = news.importance_score or 0.5  # 使用重要性評分作為基礎分數，如果沒有則使用0.5
        
        # 根據關鍵詞調整業務影響分數
        keyword_score = 0
        matches = 0
        for keyword, weight in business_keywords.items():
            if keyword in title_content:
                keyword_score += weight
                matches += 1
        
        # 計算平均關鍵詞分數
        avg_keyword_score = keyword_score / max(matches, 1)
        
        # 組合基礎分數和關鍵詞分數
        impact_score = 0.6 * base_score + 0.4 * avg_keyword_score
        
        # 確保分數在0-1之間
        return max(0, min(impact_score, 1))

def analyze_business_impact(news):
    """分析新聞的業務影響"""
    try:
        from analyzer.importance_rating import ImportanceRater
        
        # 初始化評分器
        rater = ImportanceRater()
        
        # 使用評分器分析業務影響
        impact_analysis = rater.analyze_business_impact(news)
        
        # 返回影響描述
        return f"{impact_analysis['type']}影響 ({impact_analysis['level']}): {impact_analysis['action']}"
        
    except ImportError:
        logger.warning("無法導入重要性評分模組，使用簡易分析")
        
        # 簡易影響分析邏輯作為備用
        impact_keywords = {
            '理賠': {'impact': '客戶詢問增加', 'urgency': 'high', 'action': '準備理賠說明資料'},
            '保費': {'impact': '定價策略調整', 'urgency': 'medium', 'action': '更新保費比較表'},
            '法規': {'impact': '合規要求更新', 'urgency': 'high', 'action': '通知客戶法規變更'},
            '政策': {'impact': '業務策略調整', 'urgency': 'high', 'action': '依新政策調整銷售方向'},
            '數位': {'impact': '服務流程優化', 'urgency': 'medium', 'action': '引導客戶使用數位工具'},
            '競爭': {'impact': '市場策略調整', 'urgency': 'medium', 'action': '關注競爭對手動向'},
            '新產品': {'impact': '產品知識更新', 'urgency': 'medium', 'action': '學習新產品特性'},
            '投資': {'impact': '投資建議更新', 'urgency': 'medium', 'action': '更新投資型商品說明'},
            '長照': {'impact': '長照保險需求', 'urgency': 'medium', 'action': '主動提供長照方案'},
            '醫療': {'impact': '醫療保險重點', 'urgency': 'high', 'action': '檢視客戶醫療保障缺口'}
        }
        
        title_content = (news.title or '') + ' ' + (news.summary or '')
        
        for keyword, info in impact_keywords.items():
            if keyword in title_content:
                level = info['urgency']
                return f"{info['impact']} ({level}): {info['action']}"
        
        return '一般業務影響 (low): 可納入例行資訊更新'

def calculate_client_interest(news):
    """計算客戶關注度"""
    try:
        from analyzer.importance_rating import ImportanceRater
        
        # 初始化評分器
        rater = ImportanceRater()
        
        # 使用評分器分析客戶興趣
        interest_analysis = rater.calculate_client_interest(news)
        
        # 返回興趣級別
        return interest_analysis['level']
        
    except ImportError:
        logger.warning("無法導入重要性評分模組，使用簡易分析")
        
        # 簡易客戶興趣分析邏輯作為備用
        view_count = news.view_count or 0
        
        if view_count > 100:
            return 'high'
        elif view_count > 50:
            return 'medium'
        else:
            return 'low'

def calculate_opportunity_score(news):
    """計算商機評分"""
    opportunity_keywords = ['新商品', '市場', '需求', '趨勢', '投資', '長照']
    title_content = (news.title or '') + ' ' + (news.summary or '')
    
    score = 0
    for keyword in opportunity_keywords:
        if keyword in title_content:
            score += 1
    
    return min(score * 20, 100)  # 最高100分

def generate_share_templates(news):
    """生成分享模板"""
    return {
        'line': {
            'title': f"📰 重要保險新聞",
            'content': f"{news.title}\n\n{news.summary[:100]}...\n\n詳細內容請洽詢您的保險顧問"
        },
        'email': {
            'subject': f"保險新聞快報：{news.title[:30]}...",
            'content': f"親愛的客戶您好，\n\n今日為您整理重要保險新聞：\n\n{news.title}\n\n{news.summary}\n\n如有任何疑問，歡迎隨時聯繫。"
        },
        'wechat': {
            'title': news.title,
            'content': f"{news.summary}\n\n💡 專業解讀：這項新聞對您的保險規劃可能有重要影響，建議進一步討論。"
        }
    }

@business_bp.route('/news/favorite', methods=['POST'])
def favorite_news():
    """收藏新聞API"""
    try:
        # 獲取請求數據
        data = request.json
        if not data:
            return jsonify({'status': 'error', 'message': '未提供數據'}), 400
        
        news_id = data.get('news_id')
        if not news_id:
            return jsonify({'status': 'error', 'message': '未提供新聞ID'}), 400
        
        # 獲取用戶ID（實際應用中應從會話或JWT獲取）
        # 在示例中，我們暫時使用固定ID或請求中提供的ID
        user_id = data.get('user_id', 1)  # 默認使用ID為1的用戶
        
        # 查詢新聞是否存在
        news = News.query.get(news_id)
        if not news:
            return jsonify({'status': 'error', 'message': '新聞不存在'}), 404
        
        # 檢查是否已收藏
        existing_favorite = SavedNews.query.filter_by(user_id=user_id, news_id=news_id).first()
        
        if existing_favorite:
            # 如果已收藏，則取消收藏
            db.session.delete(existing_favorite)
            db.session.commit()
            return jsonify({'status': 'success', 'action': 'unfavorited', 'message': '已取消收藏'})
        else:
            # 如果未收藏，則添加收藏
            folder = data.get('folder', 'default')
            notes = data.get('notes', '')
            importance = data.get('importance', 0)
            
            # 創建收藏記錄
            new_favorite = SavedNews(
                user_id=user_id,
                news_id=news_id,
                folder=folder,
                notes=notes,
                importance=importance
            )
            
            db.session.add(new_favorite)
            db.session.commit()
            
            return jsonify({
                'status': 'success', 
                'action': 'favorited', 
                'message': '收藏成功',
                'favorite_id': new_favorite.id
            })
        
    except Exception as e:
        logger.error(f"收藏新聞錯誤: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'操作失敗: {str(e)}',
        }), 500

@business_bp.route('/news/favorites')
def list_favorites():
    """列出收藏的新聞"""
    try:
        # 獲取用戶ID（實際應用中應從會話或JWT獲取）
        # 在示例中，我們暫時使用固定ID或請求中提供的ID
        user_id = request.args.get('user_id', 1, type=int)  # 默認使用ID為1的用戶
        
        # 獲取篩選條件
        folder = request.args.get('folder', '')
        
        # 查詢條件
        query = SavedNews.query.filter_by(user_id=user_id)
        
        if folder:
            query = query.filter_by(folder=folder)
        
        # 排序
        sort_by = request.args.get('sort', 'date')
        if sort_by == 'importance':
            query = query.order_by(SavedNews.importance.desc())
        else:  # 默認按收藏時間排序
            query = query.order_by(SavedNews.created_at.desc())
        
        # 分頁參數
        page = request.args.get(get_page_parameter(), type=int, default=1)
        per_page = 10  # 每頁顯示10條
        
        # 獲取收藏記錄
        favorites = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 構建返回數據
        favorites_data = []
        for fav in favorites.items:
            news = News.query.get(fav.news_id)
            if news:
                favorites_data.append({
                    'favorite_id': fav.id,
                    'news_id': news.id,
                    'title': news.title,
                    'summary': news.summary,
                    'source': news.source.name if news.source else '未知來源',
                    'published_date': news.published_date.isoformat() if news.published_date else None,
                    'importance_score': news.importance_score or 0,
                    'user_importance': fav.importance,
                    'folder': fav.folder,
                    'notes': fav.notes,
                    'favorited_at': fav.created_at.isoformat()
                })
        
        return render_template('business/favorites.html',
                             favorites=favorites_data,
                             pagination=favorites,
                             folders=get_favorite_folders(user_id),
                             current_folder=folder)
        
    except Exception as e:
        logger.error(f"獲取收藏列表錯誤: {str(e)}")
        return render_template('business/favorites.html',
                             favorites=[],
                             pagination=None,
                             folders=[],
                             current_folder='')

@business_bp.route('/api/search')
def api_search():
    """即時搜索API"""
    try:
        # 獲取搜索詞
        search_term = request.args.get('term', '').strip()
        if not search_term or len(search_term) < 2:
            return jsonify({
                'status': 'error',
                'message': '搜索詞過短',
                'data': []
            })
        
        # 記錄搜索請求
        logger.info(f"即時搜索請求: '{search_term}'")
        
        # 使用PostgreSQL全文搜索或SQLite的LIKE查詢
        # 注意: 生產環境中應使用更高效的全文搜索解決方案
        try:
            # 假設使用PostgreSQL
            search_query = News.query.filter(
                db.or_(
                    News.title.ilike(f'%{search_term}%'),
                    News.content.ilike(f'%{search_term}%'),
                    News.summary.ilike(f'%{search_term}%'),
                    News.keywords.ilike(f'%{search_term}%')
                ),
                News.status == 'active'
            )
        except Exception as search_error:
            logger.warning(f"高級搜索失敗，回退到基本搜索: {search_error}")
            # 基本搜索回退
            search_query = News.query.filter(
                db.or_(
                    News.title.like(f'%{search_term}%'),
                    News.summary.like(f'%{search_term}%')
                ),
                News.status == 'active'
            )
        
        # 根據重要性評分排序
        search_query = search_query.order_by(desc(News.importance_score), desc(News.published_date))
        
        # 限制返回結果數量
        search_results = search_query.limit(10).all()
        
        # 格式化結果
        results = []
        for news in search_results:
            results.append({
                'id': news.id,
                'title': news.title,
                'summary': news.summary,
                'published_date': news.published_date.isoformat() if news.published_date else None,
                'importance_score': news.importance_score or 0,
                'source_name': news.source.name if news.source else '未知來源'
            })
        
        # 返回搜索結果
        return jsonify({
            'status': 'success',
            'message': f'找到 {len(results)} 筆結果',
            'data': results
        })
        
    except Exception as e:
        logger.error(f"搜索API錯誤: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '搜索處理時發生錯誤',
            'error': str(e),
            'data': []
        }), 500

@business_bp.route('/search')
def search_page():
    """進階搜索頁面"""
    try:
        # 獲取搜索詞
        search_term = request.args.get('term', '').strip()
        
        # 獲取過濾條件
        category_id = request.args.get('category', type=int)
        importance_level = request.args.get('importance')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # 構建基本查詢
        query = News.query.filter(News.status == 'active')
        
        # 應用搜索詞過濾
        if search_term:
            query = query.filter(
                db.or_(
                    News.title.ilike(f'%{search_term}%'),
                    News.content.ilike(f'%{search_term}%'),
                    News.summary.ilike(f'%{search_term}%')
                )
            )
        
        # 應用分類過濾
        if category_id:
            query = query.filter(News.category_id == category_id)
        
        # 應用重要性過濾
        if importance_level:
            if importance_level == 'high':
                query = query.filter(News.importance_score >= 0.7)
            elif importance_level == 'medium':
                query = query.filter(News.importance_score.between(0.4, 0.7))
            elif importance_level == 'low':
                query = query.filter(News.importance_score < 0.4)
        
        # 應用日期過濾
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(News.published_date >= date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                # 設置為當天結束時間
                date_to_obj = date_to_obj.replace(hour=23, minute=59, second=59)
                query = query.filter(News.published_date <= date_to_obj)
            except ValueError:
                pass
        
        # 排序
        sort_by = request.args.get('sort', 'importance')
        if sort_by == 'date':
            query = query.order_by(desc(News.published_date))
        elif sort_by == 'view_count':
            query = query.order_by(desc(News.view_count))
        else:  # 默認按重要性排序
            query = query.order_by(desc(News.importance_score))
        
        # 分頁
        page = request.args.get(get_page_parameter(), type=int, default=1)
        per_page = 15  # 每頁顯示15條
        
        # 獲取新聞
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        news_results = pagination.items
        
        # 獲取所有分類供過濾使用
        categories = NewsCategory.query.all()
        
        # 渲染搜索結果頁面
        return render_template(
            'business/search.html',
            news_results=news_results,
            pagination=pagination,
            search_term=search_term,
            categories=categories,
            selected_category=category_id,
            importance_level=importance_level,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by
        )
        
    except Exception as e:
        logger.error(f"搜索頁面錯誤: {str(e)}")
        return render_template(
            'business/search.html',
            news_results=[],
            pagination=None,
            search_term=search_term if 'search_term' in locals() else '',
            categories=[],
            selected_category=None,
            importance_level=None,
            date_from=None,
            date_to=None,
            sort_by='importance',
            error=str(e)
        )

def get_favorite_folders(user_id):
    """獲取用戶的所有收藏夾"""
    try:
        # 查詢用戶的所有不同收藏夾
        folders = db.session.query(SavedNews.folder, func.count(SavedNews.id).label('count')).\
                  filter(SavedNews.user_id == user_id).\
                  group_by(SavedNews.folder).\
                  order_by(SavedNews.folder).all()
        
        # 返回格式化的結果
        return [{'name': folder.folder, 'count': folder.count} for folder in folders]
        
    except Exception as e:
        logger.error(f"獲取收藏夾錯誤: {str(e)}")
        return [{'name': 'default', 'count': 0}]

@business_bp.route('/preferences')
def preferences():
    """用戶偏好設定頁面"""
    try:
        logger.info("用戶偏好設定頁面訪問")
        
        # 獲取所有分類供分類偏好設定使用
        categories = NewsCategory.query.filter_by(status='active').order_by(NewsCategory.name).all()
        
        return render_template('business/preferences.html',
                             categories=categories)
        
    except Exception as e:
        logger.error(f"載入用戶偏好設定頁面錯誤: {str(e)}")
        return render_template('business/preferences.html',
                             categories=[],
                             error=str(e))

@business_bp.route('/client-tool')
def client_tool():
    """客戶互動工具頁面"""
    try:
        logger.info("客戶互動工具頁面訪問")
        return render_template('business/client_tool.html')
    except Exception as e:
        logger.error(f"載入客戶互動工具頁面錯誤: {str(e)}")
        return render_template('business/client_tool.html', error=str(e))

@business_bp.route('/share-tools')
def share_tools_page():
    """分享工具頁面"""
    try:
        logger.info("分享工具頁面訪問")
        return render_template('business/share_tools.html')
    except Exception as e:
        logger.error(f"載入分享工具頁面錯誤: {str(e)}")
        return render_template('business/share_tools.html', error=str(e))

@business_bp.route('/favorites')
def favorites_page():
    """我的最愛頁面"""
    try:
        logger.info("我的最愛頁面訪問")
        return render_template('business/favorites.html')
    except Exception as e:
        logger.error(f"載入我的最愛頁面錯誤: {str(e)}")
        return render_template('business/favorites.html', error=str(e))

@business_bp.route('/share-analytics')
def share_analytics():
    """分享效率評估頁面"""
    try:
        logger.info("分享效率評估頁面訪問")
        return render_template('business/share_analytics.html')
    except Exception as e:
        logger.error(f"載入分享效率評估頁面錯誤: {str(e)}")
        return render_template('business/share_analytics.html', error=str(e))

@business_bp.route('/api/preferences', methods=['GET', 'POST'])
def api_preferences():
    """用戶偏好設定API"""
    try:
        # 獲取用戶ID (實際應用中應從會話獲取)
        user_id = request.args.get('user_id', 1, type=int)
        
        # 獲取用戶
        user = User.query.get_or_404(user_id)
        
        if request.method == 'GET':
            # 獲取用戶設定
            preferences = {}
            
            if user.preferences:
                # 如果存在偏好設定，解析JSON
                try:
                    import json
                    preferences = json.loads(user.preferences)
                except (json.JSONDecodeError, TypeError):
                    # 如果解析失敗，返回空對象
                    preferences = {}
            
            # 設置默認值
            if not preferences.get('display'):
                preferences['display'] = {
                    'defaultSorting': 'importance',
                    'itemsPerPage': 15,
                    'summaryLength': 'medium',
                    'dashboardLayout': 'standard'
                }
                
            if not preferences.get('notifications'):
                preferences['notifications'] = {
                    'email': True,
                    'frequency': 'daily',
                    'highImportance': True,
                    'businessOpportunities': True,
                    'industryUpdates': False,
                    'regulatoryChanges': True,
                    'limit': 3
                }
                
            if not preferences.get('categories'):
                preferences['categories'] = {
                    'priority': [],
                    'ignored': [],
                    'autoLearn': True
                }
                
            if not preferences.get('dataDisplay'):
                preferences['dataDisplay'] = {
                    'showImportance': True,
                    'showTrend': True,
                    'showCategory': True,
                    'showBusiness': True,
                    'showClient': False,
                    'chartType': 'bar',
                    'showLabels': True,
                    'animate': True
                }
                
            if not preferences.get('sharing'):
                preferences['sharing'] = {
                    'template': 'detailed',
                    'email': True,
                    'line': True,
                    'wechat': False,
                    'pdf': True,
                    'signature': '此資訊由您的保險專員提供，如有任何疑問，歡迎隨時聯絡。',
                    'includeContactInfo': True
                }
            
            # 返回用戶設定
            return jsonify({
                'status': 'success',
                'data': preferences
            })
            
        elif request.method == 'POST':
            # 獲取請求數據
            data = request.json
            if not data:
                return jsonify({'status': 'error', 'message': '未提供數據'}), 400
            
            # 獲取偏好設定
            preferences = data.get('preferences')
            if not preferences:
                return jsonify({'status': 'error', 'message': '未提供偏好設定'}), 400
            
            # 儲存偏好設定
            try:
                import json
                user.preferences = json.dumps(preferences, ensure_ascii=False)
                db.session.commit()
                
                # 記錄設定更新
                logger.info(f"用戶 {user_id} 更新了偏好設定")
                
                return jsonify({
                    'status': 'success',
                    'message': '偏好設定已保存',
                })
                
            except Exception as save_error:
                db.session.rollback()
                logger.error(f"保存用戶偏好設定錯誤: {str(save_error)}")
                return jsonify({
                    'status': 'error',
                    'message': f'無法保存設定: {str(save_error)}'
                }), 500
                
    except Exception as e:
        logger.error(f"用戶偏好設定API錯誤: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'處理請求時發生錯誤: {str(e)}'
        }), 500

# ==================== 新增交互功能API端點 ====================

@business_bp.route('/api/filter', methods=['POST'])
def api_filter_news():
    """API端點：篩選新聞"""
    try:
        data = request.get_json()
        filters = data.get('filters', {})
        
        # 建立查詢
        query = News.query
        
        # 應用篩選條件
        if 'high-priority' in filters:
            query = query.filter(News.importance_score >= 0.7)
        
        if 'opportunities' in filters:
            query = query.filter(News.content.contains('機會') | News.content.contains('商機'))
        
        if 'regulatory' in filters:
            query = query.filter(News.content.contains('法規') | News.content.contains('金管會'))
        
        # 自定義篩選
        if 'date_from' in filters:
            date_from = datetime.strptime(filters['date_from'], '%Y-%m-%d')
            query = query.filter(News.published_date >= date_from)
        
        if 'date_to' in filters:
            date_to = datetime.strptime(filters['date_to'], '%Y-%m-%d')
            query = query.filter(News.published_date <= date_to)
        
        if 'sources' in filters:
            source_names = filters['sources']
            query = query.join(NewsSource).filter(NewsSource.name.in_(source_names))
        
        if 'importance' in filters:
            importance_conditions = []
            if 'high' in filters['importance']:
                importance_conditions.append(News.importance_score >= 0.7)
            if 'medium' in filters['importance']:
                importance_conditions.append(and_(News.importance_score >= 0.4, News.importance_score < 0.7))
            if 'low' in filters['importance']:
                importance_conditions.append(News.importance_score < 0.4)
            
            if importance_conditions:
                query = query.filter(or_(*importance_conditions))
        
        if 'keywords' in filters:
            keyword_conditions = []
            for keyword in filters['keywords']:
                keyword_conditions.append(News.title.contains(keyword))
                keyword_conditions.append(News.content.contains(keyword))
            
            if keyword_conditions:
                query = query.filter(or_(*keyword_conditions))
        
        # 排序和分頁
        news = query.order_by(News.importance_score.desc(), News.published_date.desc()).limit(50).all()
        
        # 統計資訊
        total_count = News.query.count()
        filtered_count = len(news)
        new_count = News.query.filter(News.published_date >= datetime.now().date()).count()
        
        news_data = []
        for item in news:
            news_data.append({
                'id': item.id,
                'title': item.title,
                'summary': item.summary,
                'source_name': item.source.name if item.source else '未知來源',
                'published_date': item.published_date.isoformat() if item.published_date else None,
                'importance_score': item.importance_score or 0.0
            })
        
        return jsonify({
            'status': 'success',
            'news': news_data,
            'stats': {
                'total': total_count,
                'filtered': filtered_count,
                'new_count': new_count
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"篩選新聞錯誤: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '篩選失敗，請稍後再試'
        }), 500

@business_bp.route('/api/bulk-action', methods=['POST'])
def api_bulk_action():
    """API端點：批量操作"""
    try:
        data = request.get_json()
        action = data.get('action')
        news_ids = data.get('news_ids', [])
        
        if not action or not news_ids:
            return jsonify({
                'status': 'error',
                'message': '缺少必要參數'
            }), 400
        
        # 獲取新聞項目
        news_items = News.query.filter(News.id.in_(news_ids)).all()
        
        if action == 'export':
            # 匯出功能
            return jsonify({
                'status': 'success',
                'message': f'已匯出 {len(news_items)} 筆新聞',
                'download_url': f'/business/export?ids={",".join(map(str, news_ids))}'
            })
        
        elif action == 'share':
            # 批量分享功能
            return jsonify({
                'status': 'success',
                'message': f'已準備分享 {len(news_items)} 筆新聞',
                'share_url': f'/business/share/bulk?ids={",".join(map(str, news_ids))}'
            })
        
        elif action == 'priority':
            # 設為優先
            for item in news_items:
                item.importance_score = min((item.importance_score or 0) + 0.1, 1.0)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': f'已將 {len(news_items)} 筆新聞設為優先'
            })
        
        elif action == 'archive':
            # 封存功能（假設有is_archived欄位）
            return jsonify({
                'status': 'success',
                'message': f'已封存 {len(news_items)} 筆新聞'
            })
        
        else:
            return jsonify({
                'status': 'error',
                'message': '不支援的操作'
            }), 400
        
    except Exception as e:
        current_app.logger.error(f"批量操作錯誤: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '操作失敗，請稍後再試'
        }), 500

@business_bp.route('/api/news/refresh', methods=['POST'])
def api_refresh_news():
    """API端點：刷新新聞列表"""
    try:
        data = request.get_json()
        filters = data.get('filters', {})
        
        # 獲取最新新聞
        query = News.query
        
        # 應用現有篩選條件
        # ... (篩選邏輯同上)
        
        news = query.order_by(News.importance_score.desc(), News.published_date.desc()).limit(20).all()
        
        # 檢查新的重要新聞
        recent_important = News.query.filter(
            News.published_date >= datetime.now() - timedelta(hours=1),
            News.importance_score >= 0.7
        ).count()
        
        news_data = []
        for item in news:
            news_data.append({
                'id': item.id,
                'title': item.title,
                'summary': item.summary,
                'source_name': item.source_name,
                'published_date': item.published_date.isoformat() if item.published_date else None,
                'importance_score': item.importance_score or 0.0
            })
        
        # 統計資訊
        stats = {
            'total_news': News.query.count(),
            'high_importance': News.query.filter(News.importance_score >= 0.7).count(),
            'today_news': News.query.filter(News.published_date >= datetime.now().date()).count(),
            'favorites': SavedNews.query.filter_by(user_id=1).count()  # 假設用戶ID為1
        }
        
        return jsonify({
            'status': 'success',
            'news': news_data,
            'stats': stats,
            'new_important_count': recent_important
        })
        
    except Exception as e:
        current_app.logger.error(f"刷新新聞錯誤: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '刷新失敗，請稍後再試'
        }), 500

@business_bp.route('/api/clients')
def api_clients():
    """API端點：獲取客戶列表"""
    try:
        # 模擬客戶資料（實際應用中應從資料庫獲取）
        clients = [
            {
                'id': 1,
                'name': '王小明',
                'phone': '0912-345-678',
                'email': 'wang@example.com',
                'type': '個人客戶',
                'created_date': '2024-01-15T00:00:00'
            },
            {
                'id': 2,
                'name': '李美華',
                'phone': '0987-654-321',
                'email': 'li@example.com',
                'type': '企業客戶',
                'created_date': '2024-02-20T00:00:00'
            },
            {
                'id': 3,
                'name': '張志偉',
                'phone': '0923-456-789',
                'email': 'zhang@example.com',
                'type': '個人客戶',
                'created_date': '2024-03-10T00:00:00'
            }
        ]
        
        return jsonify({
            'status': 'success',
            'clients': clients
        })
        
    except Exception as e:
        current_app.logger.error(f"獲取客戶列表錯誤: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '獲取客戶列表失敗'
        }), 500

@business_bp.route('/api/analytics', methods=['POST'])
def api_analytics():
    """API端點：分析追蹤"""
    try:
        data = request.get_json()
        event_type = data.get('event_type')
        event_data = data.get('data')
        
        # 記錄分析資料（實際應用中應存入資料庫）
        current_app.logger.info(f"Analytics: {event_type} - {event_data}")
        
        return jsonify({
            'status': 'success',
            'message': '分析資料已記錄'
        })
        
    except Exception as e:
        current_app.logger.error(f"分析追蹤錯誤: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '分析追蹤失敗'
        }), 500

@business_bp.route('/api/generate-template', methods=['POST'])
def api_generate_template():
    """API端點：生成客戶溝通模板"""
    try:
        data = request.get_json()
        template_type = data.get('template_type', 'email')
        client_type = data.get('client_type', 'individual')
        goal = data.get('communication_goal', 'inform')
        news_id = data.get('news_id')
        
        # 獲取新聞資料
        news = News.query.get(news_id) if news_id else None
        
        # 根據參數生成模板
        templates = {
            'email': {
                'individual': {
                    'inform': f"""親愛的客戶您好：

我是您的保險專員，想與您分享一則重要的保險新聞：

【{news.title if news else '保險新資訊'}】

{news.summary if news else '這是一則重要的保險相關資訊，可能會對您的保障規劃產生影響。'}

為了確保您的保障權益，建議我們安排時間詳細討論這項變化對您既有保單的影響，並評估是否需要調整保障內容。

如有任何疑問，歡迎隨時與我聯絡。

祝好
您的保險專員""",
                    'sell': f"""親愛的客戶您好：

根據最新的保險市場動態：

【{news.title if news else '市場新機會'}】

{news.summary if news else '市場上出現了新的保險商品機會，可能非常適合您的需求。'}

基於您目前的保障狀況，我認為這是一個很好的機會來優化您的保險規劃。這項新商品具有以下優勢：

1. 更完善的保障範圍
2. 更優惠的保費結構
3. 更彈性的給付條件

建議我們盡快安排時間面談，為您詳細說明並客製化最適合的保障方案。

期待與您聯絡
您的保險專員"""
                }
            }
        }
        
        template = templates.get(template_type, {}).get(client_type, {}).get(goal, '模板生成中...')
        
        return jsonify({
            'status': 'success',
            'template': template
        })
        
    except Exception as e:
        current_app.logger.error(f"生成模板錯誤: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '模板生成失敗'
        }), 500

@business_bp.route('/api/category-news', methods=['GET'])
def api_category_news():
    """API端點：獲取特定分類的新聞"""
    try:
        group = request.args.get('group', '')
        category = request.args.get('category', '')
        
        # 定義分類映射
        category_mapping = {
            '客戶關注': {
                '理賠案例': ['理賠', '賠案', '理賠審核', '理賠爭議'],
                '保費調整': ['保費', '費率', '調漲', '調整'],
                '法規變動': ['法規', '金管會', '監理', '規定']
            },
            '公司動態': {
                '新商品發布': ['新商品', '產品', '發布', '上市'],
                '通路政策': ['通路', '業務', '政策', '獎勵'],
                '獲獎消息': ['獲獎', '得獎', '獎項', '表揚']
            },
            '市場分析': {
                '保費趨勢': ['趨勢', '成長', '市場', '預測'],
                '競爭分析': ['競爭', '市佔', '外資', '分析'],
                '客群變化': ['客群', '消費者', '世代', '行為']
            }
        }
        
        # 獲取關鍵字
        keywords = []
        if group in category_mapping and category in category_mapping[group]:
            keywords = category_mapping[group][category]
        
        # 構建查詢
        query = News.query.filter(News.status == 'active')
        
        if keywords:
            # 使用OR條件搜索標題或摘要中包含任一關鍵字的新聞
            conditions = []
            for keyword in keywords:
                conditions.append(News.title.contains(keyword))
                conditions.append(News.summary.contains(keyword))
            
            query = query.filter(or_(*conditions))
        
        # 按重要性排序，限制數量
        news_items = query.order_by(desc(News.importance_score)).limit(20).all()
        
        # 轉換為JSON格式
        news_data = []
        for news in news_items:
            news_data.append({
                'id': news.id,
                'title': news.title,
                'summary': news.summary,
                'importance_score': news.importance_score,
                'published_date': news.published_date.isoformat() if news.published_date else None,
                'source_name': news.source.name if news.source else '未知來源',
                'url': news.url
            })
        
        return jsonify({
            'status': 'success',
            'news': news_data,
            'group': group,
            'category': category,
            'count': len(news_data)
        })
        
    except Exception as e:
        current_app.logger.error(f"獲取分類新聞錯誤: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '獲取分類新聞失敗'
        }), 500

@business_bp.route('/api/category-group', methods=['GET'])
def api_category_group():
    """API端點：獲取分類組的所有新聞"""
    try:
        group = request.args.get('group', '')
        
        # 定義分類組映射
        group_mapping = {
            '客戶關注': ['理賠', '賠案', '保費', '費率', '法規', '金管會', '監理'],
            '公司動態': ['新商品', '產品', '發布', '通路', '業務', '政策', '獲獎', '得獎'],
            '市場分析': ['趨勢', '成長', '市場', '競爭', '市佔', '客群', '消費者', '分析']
        }
        
        # 獲取關鍵字
        keywords = group_mapping.get(group, [])
        
        # 構建查詢
        query = News.query.filter(News.status == 'active')
        
        if keywords:
            # 使用OR條件搜索標題或摘要中包含任一關鍵字的新聞
            conditions = []
            for keyword in keywords:
                conditions.append(News.title.contains(keyword))
                conditions.append(News.summary.contains(keyword))
            
            query = query.filter(or_(*conditions))
        
        # 按重要性排序，限制數量
        news_items = query.order_by(desc(News.importance_score)).limit(50).all()
        
        # 轉換為JSON格式
        news_data = []
        for news in news_items:
            news_data.append({
                'id': news.id,
                'title': news.title,
                'summary': news.summary,
                'importance_score': news.importance_score,
                'published_date': news.published_date.isoformat() if news.published_date else None,
                'source_name': news.source.name if news.source else '未知來源',
                'url': news.url
            })
        
        return jsonify({
            'status': 'success',
            'news': news_data,
            'group': group,
            'count': len(news_data)
        })
        
    except Exception as e:
        current_app.logger.error(f"獲取分類組新聞錯誤: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '獲取分類組新聞失敗'
        }), 500

@business_bp.route('/api/category-stats', methods=['GET'])
def api_category_stats():
    """API端點：獲取智能分類統計數據"""
    try:
        from sqlalchemy import text
        
        # 定義分類統計
        category_stats = {
            '客戶關注': {
                '理賠案例': 0,
                '保費調整': 0, 
                '法規變動': 0
            },
            '公司動態': {
                '新商品發布': 0,
                '通路政策': 0,
                '獲獎消息': 0
            },
            '市場分析': {
                '保費趨勢': 0,
                '競爭分析': 0,
                '客群變化': 0
            }
        }
        
        # 計算各分類的新聞數量
        category_mapping = {
            '客戶關注': {
                '理賠案例': ['理賠', '賠案', '理賠審核', '理賠爭議'],
                '保費調整': ['保費', '費率', '調漲', '調整'],
                '法規變動': ['法規', '金管會', '監理', '規定']
            },
            '公司動態': {
                '新商品發布': ['新商品', '產品', '發布', '上市'],
                '通路政策': ['通路', '業務', '政策', '獎勵'],
                '獲獎消息': ['獲獎', '得獎', '獎項', '表揚']
            },
            '市場分析': {
                '保費趨勢': ['趨勢', '成長', '市場', '預測'],
                '競爭分析': ['競爭', '市佔', '外資', '分析'],
                '客群變化': ['客群', '消費者', '世代', '行為']
            }
        }
        
        for group, categories in category_mapping.items():
            for category, keywords in categories.items():
                # 計算包含關鍵字的新聞數量
                conditions = []
                for keyword in keywords:
                    conditions.append(f"title LIKE '%{keyword}%' OR summary LIKE '%{keyword}%'")
                
                where_clause = " OR ".join(conditions)
                sql = text(f"SELECT COUNT(*) FROM news WHERE status = 'active' AND ({where_clause})")
                
                result = db.session.execute(sql).scalar()
                category_stats[group][category] = result or 0
        
        return jsonify({
            'status': 'success',
            'stats': category_stats
        })
        
    except Exception as e:
        current_app.logger.error(f"獲取分類統計錯誤: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '獲取分類統計失敗'
        }), 500

# 賽博朋克業務員界面的專用API端點
@business_bp.route('/api/cyber-news')
def api_cyber_news():
    """賽博朋克新聞API端點"""
    # 模擬新聞數據
    news_data = generate_mock_business_news()
    
    # 應用篩選
    filter_type = request.args.get('filter', 'all')
    if filter_type != 'all':
        news_data = apply_news_filter(news_data, filter_type)
    
    # 分頁
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    start = (page - 1) * per_page
    end = start + per_page
    
    return jsonify({
        'news': news_data[start:end],
        'total': len(news_data),
        'page': page,
        'per_page': per_page,
        'has_more': end < len(news_data)
    })

@business_bp.route('/api/cyber-clients')
def api_cyber_clients():
    """賽博朋克客戶API端點"""
    clients = [
        {
            'id': 1,
            'name': '張美玲',
            'avatar': '張',
            'priority': 'high',
            'last_contact': '2024-01-15',
            'status': 'active',
            'interests': ['醫療險', '儲蓄險'],
            'age': 35,
            'occupation': '工程師'
        },
        {
            'id': 2,
            'name': '李志明',
            'avatar': '李',
            'priority': 'medium',
            'last_contact': '2024-01-12',
            'status': 'follow_up',
            'interests': ['投資型保險', '退休規劃'],
            'age': 45,
            'occupation': '經理'
        },
        {
            'id': 3,
            'name': '王小華',
            'avatar': '王',
            'priority': 'critical',
            'last_contact': '2024-01-10',
            'status': 'urgent',
            'interests': ['旅平險', '意外險'],
            'age': 28,
            'occupation': '設計師'
        }
    ]
    
    return jsonify(clients)

@business_bp.route('/api/cyber-opportunities')
def api_cyber_opportunities():
    """賽博朋克業務機會API端點"""
    opportunities = generate_business_opportunities()
    return jsonify(opportunities)

@business_bp.route('/api/cyber-share', methods=['POST'])
def api_cyber_share():
    """賽博朋克分享新聞API端點"""
    data = request.get_json()
    news_id = data.get('news_id')
    share_method = data.get('method')  # 'line', 'email', 'pdf'
    clients = data.get('clients', [])
    
    # 模擬分享處理
    result = {
        'success': True,
        'message': f'新聞 {news_id} 已通過 {share_method} 分享給 {len(clients)} 位客戶',
        'share_id': f'share_{random.randint(1000, 9999)}'
    }
    
    return jsonify(result)

@business_bp.route('/api/cyber-stats')
def api_cyber_stats():
    """賽博朋克統計數據API端點"""
    stats = {
        'daily_news': 156,
        'important_news': 23,
        'opportunities': 7,
        'shared_news': 45,
        'trends': {
            'daily_news': 12,
            'important_news': 8,
            'opportunities': -2,
            'shared_news': 15
        }
    }
    
    return jsonify(stats)

def generate_mock_business_news():
    """生成模擬業務新聞數據"""
    news_templates = [
        {
            'title': '金管會發布新版保險商品管理辦法',
            'summary': '金融監督管理委員會今日發布修正版保險商品管理辦法，針對數位化投保流程、商品揭露義務等進行重大調整。',
            'category': '法規',
            'impact': '高',
            'tags': ['法規', '數位化', '商品管理']
        },
        {
            'title': '數位保險平台使用率創新高',
            'summary': '根據最新統計，國內數位保險平台使用率較去年同期成長35%，年輕世代成為主要推動力。',
            'category': '市場',
            'impact': '中',
            'tags': ['數位保險', '市場趨勢', '年輕族群']
        },
        {
            'title': '醫療險理賠爭議案例分析',
            'summary': '保險事業發展中心發布年度醫療險理賠爭議分析報告，提供業務員參考指引。',
            'category': '理賠',
            'impact': '中',
            'tags': ['醫療險', '理賠', '爭議處理']
        },
        {
            'title': '退休規劃：年金保險趨勢觀察',
            'summary': '隨著高齡化社會來臨，年金保險商品需求持續增長，業者推出多元化商品因應市場需求。',
            'category': '商品',
            'impact': '高',
            'tags': ['年金', '退休規劃', '高齡化']
        },
        {
            'title': '保險科技FinTech最新發展',
            'summary': 'AI人工智慧、區塊鏈、物聯網等新技術正在重塑保險業生態，為業務員帶來新的工作模式。',
            'category': '科技',
            'impact': '高',
            'tags': ['FinTech', 'AI', '數位轉型']
        }
    ]
    
    sources = ['工商時報', '經濟日報', '聯合報', '中時電子報', '保險雜誌']
    priorities = ['low', 'medium', 'high', 'critical']
    clients = ['張美玲', '李志明', '王小華']
    
    news_list = []
    for i in range(50):
        template = random.choice(news_templates)
        news = {
            'id': i + 1,
            'title': f"{template['title']} - 案例 {i+1}",
            'summary': template['summary'],
            'content': f"完整新聞內容：{template['summary']} 這是一條詳細的新聞內容，提供更多背景資訊和分析。",
            'category': template['category'],
            'priority': random.choice(priorities),
            'source': random.choice(sources),
            'timestamp': datetime.now() - timedelta(hours=random.randint(1, 72)),
            'tags': template['tags'],
            'business_impact': template['impact'],
            'relevant_clients': random.sample(clients, random.randint(0, 2)),
            'read_count': random.randint(50, 500),
            'share_count': random.randint(5, 50),
            'bookmark_count': random.randint(2, 25),
            'url': f"https://example.com/news/{i+1}",
            'image_url': f"https://picsum.photos/300/200?random={i+1}"
        }
        news_list.append(news)
    
    return news_list

def apply_news_filter(news_data, filter_type):
    """應用新聞篩選"""
    if filter_type == 'today':
        today = datetime.now().date()
        return [n for n in news_data if n['timestamp'].date() == today]
    elif filter_type == 'important':
        return [n for n in news_data if n['priority'] in ['high', 'critical']]
    elif filter_type == 'opportunity':
        return [n for n in news_data if n['business_impact'] == '高']
    elif filter_type == 'saved':
        # 模擬已收藏的新聞
        return news_data[:10]
    
    return news_data

def generate_business_opportunities():
    """生成業務機會提醒"""
    opportunities = [
        {
            'id': 1,
            'type': 'news_trend',
            'title': '醫療險新聞熱度上升',
            'description': '過去24小時內醫療險相關新聞增加30%，建議聯繫關注健康保障的客戶',
            'priority': 'high',
            'suggested_clients': ['張美玲'],
            'suggested_products': ['醫療險', '重大疾病險'],
            'created_at': datetime.now() - timedelta(hours=2)
        },
        {
            'id': 2,
            'type': 'client_behavior',
            'title': '客戶搜索退休規劃',
            'description': '李志明最近在網站上瀏覽了多篇退休規劃文章',
            'priority': 'medium',
            'suggested_clients': ['李志明'],
            'suggested_products': ['年金險', '投資型保險'],
            'created_at': datetime.now() - timedelta(hours=5)
        },
        {
            'id': 3,
            'type': 'market_trend',
            'title': '旅遊保險需求增加',
            'description': '疫情後旅遊市場復甦，旅平險詢問度大幅提升',
            'priority': 'medium',
            'suggested_clients': ['王小華'],
            'suggested_products': ['旅平險', '海外醫療險'],
            'created_at': datetime.now() - timedelta(hours=8)
        }
    ]
    
    return opportunities
