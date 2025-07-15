"""
分析系統測試器
Analysis System Tester

測試和調校文本分析功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from config.settings import Config
from database.models import db, News
from analyzer.engine import InsuranceNewsAnalyzer

def test_analysis_system():
    """測試分析系統"""
    print("🧪 開始測試分析系統...")
    
    app = create_app(Config)
    
    with app.app_context():
        # 初始化分析器
        analyzer = InsuranceNewsAnalyzer()
        
        # 獲取一些新聞進行測試
        news_list = News.query.filter_by(status='active').limit(5).all()
        
        if not news_list:
            print("❌ 沒有找到新聞數據進行測試")
            return
        
        print(f"📊 找到 {len(news_list)} 則新聞進行分析測試")
        
        for i, news in enumerate(news_list, 1):
            print(f"\n📰 分析新聞 {i}: {news.title}")
            
            try:
                # 測試關鍵字提取
                keywords = analyzer.extract_keywords(news.content or news.summary)
                print(f"🔑 關鍵字: {keywords[:5]}")  # 顯示前5個
                
                # 測試情感分析
                sentiment = analyzer.analyze_sentiment(news.content or news.summary)
                print(f"😊 情感分數: {sentiment:.3f}")
                
                # 測試重要性評分
                importance = analyzer.calculate_importance_score(news.title, news.content or news.summary)
                print(f"⭐ 重要性: {importance:.3f}")
                
                # 測試保險類型分類
                insurance_type = analyzer.classify_insurance_type(news.title + " " + (news.content or news.summary))
                print(f"🏷️ 保險類型: {insurance_type}")
                
                # 更新數據庫中的分析結果
                news.sentiment_score = sentiment
                news.importance_score = importance
                news.keywords = ','.join(keywords[:10])  # 儲存前10個關鍵字
                
            except Exception as e:
                print(f"❌ 分析失敗: {e}")
        
        try:
            db.session.commit()
            print("✅ 分析結果已儲存到資料庫")
        except Exception as e:
            print(f"❌ 儲存分析結果失敗: {e}")
            db.session.rollback()

def test_batch_analysis():
    """批量分析測試"""
    print("\n🔄 開始批量分析測試...")
    
    app = create_app(Config)
    
    with app.app_context():
        analyzer = InsuranceNewsAnalyzer()
        
        # 獲取所有未分析的新聞
        unanalyzed_news = News.query.filter(
            News.status == 'active',
            News.sentiment_score.is_(None)
        ).all()
        
        if not unanalyzed_news:
            print("✅ 所有新聞都已完成分析")
            return
        
        print(f"📊 找到 {len(unanalyzed_news)} 則未分析的新聞")
        
        success_count = 0
        for news in unanalyzed_news:
            try:
                # 進行完整分析
                content = news.content or news.summary or news.title
                
                sentiment = analyzer.analyze_sentiment(content)
                importance = analyzer.calculate_importance_score(news.title, content)
                keywords = analyzer.extract_keywords(content)
                insurance_type = analyzer.classify_insurance_type(content)
                
                # 更新數據庫
                news.sentiment_score = sentiment
                news.importance_score = importance
                news.keywords = ','.join(keywords[:10])
                
                success_count += 1
                
            except Exception as e:
                print(f"❌ 分析新聞失敗 [{news.title}]: {e}")
        
        try:
            db.session.commit()
            print(f"✅ 成功分析並儲存 {success_count} 則新聞")
        except Exception as e:
            print(f"❌ 批量儲存失敗: {e}")
            db.session.rollback()

def generate_analysis_report():
    """生成分析報告"""
    print("\n📊 生成分析報告...")
    
    app = create_app(Config)
    
    with app.app_context():
        # 統計分析結果
        total_news = News.query.filter_by(status='active').count()
        analyzed_news = News.query.filter(
            News.status == 'active',
            News.sentiment_score.isnot(None)
        ).count()
        
        # 情感分析統計
        positive_news = News.query.filter(
            News.status == 'active',
            News.sentiment_score > 0.3
        ).count()
        
        negative_news = News.query.filter(
            News.status == 'active',
            News.sentiment_score < -0.1
        ).count()
        
        neutral_news = analyzed_news - positive_news - negative_news
        
        # 重要性統計
        high_importance = News.query.filter(
            News.status == 'active',
            News.importance_score > 0.7
        ).count()
        
        print(f"""
📈 分析系統報告
=================
總新聞數量: {total_news}
已分析數量: {analyzed_news}
分析完成率: {(analyzed_news/total_news*100):.1f}%

📊 情感分析結果:
正面新聞: {positive_news} ({(positive_news/analyzed_news*100):.1f}%)
中性新聞: {neutral_news} ({(neutral_news/analyzed_news*100):.1f}%)
負面新聞: {negative_news} ({(negative_news/analyzed_news*100):.1f}%)

⭐ 重要性分析:
高重要性新聞: {high_importance} ({(high_importance/analyzed_news*100):.1f}%)
        """)

if __name__ == "__main__":
    test_analysis_system()
    test_batch_analysis()
    generate_analysis_report()
