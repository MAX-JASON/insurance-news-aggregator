"""
智能分類系統
Intelligent Classification System

依業務相關性對新聞進行智能分類
"""

import os
import re
import json
import logging
import jieba
import jieba.analyse
import numpy as np
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# 設置日誌
logger = logging.getLogger('maintenance.news_classifier')

class NewsClassifier:
    """新聞分類器"""
    
    def __init__(self, model_path=None):
        """初始化
        
        Args:
            model_path: 模型保存路徑
        """
        self.model_path = model_path or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'news_classifier.pkl')
        self.categories = []
        self.pipeline = None
        self.category_keywords = {}
        self.insurance_dict_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'analyzer', 'insurance_dictionary.py')
        self.load_insurance_dictionary()
    
    def load_insurance_dictionary(self):
        """加載保險專業詞庫"""
        try:
            with open(self.insurance_dict_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 從Python文件中提取字典
            pattern = r'INSURANCE_KEYWORDS\s*=\s*{([^}]*)}'
            match = re.search(pattern, content, re.DOTALL)
            if match:
                keywords_str = match.group(1)
                # 使用eval解析字典（在這個受控環境中安全）
                keywords_dict = eval('{' + keywords_str + '}')
                self.category_keywords = keywords_dict
                logger.info(f"已載入保險專業詞庫: {len(self.category_keywords)}個類別")
                
                # 將詞加入jieba分詞器
                for category, words in self.category_keywords.items():
                    for word in words:
                        jieba.add_word(word, freq=None, tag=None)
            else:
                logger.warning("無法從文件中提取保險專業詞庫")
        except Exception as e:
            logger.error(f"載入保險專業詞庫失敗: {e}")
    
    def preprocess_text(self, text):
        """文本預處理
        
        Args:
            text: 原始文本
            
        Returns:
            處理後的文本
        """
        if not text:
            return ''
            
        # 將文本轉換為小寫
        text = text.lower()
        
        # 使用jieba進行分詞
        words = jieba.cut(text)
        
        # 過濾停用詞和標點符號
        filtered_words = []
        stop_words = {'的', '了', '和', '是', '在', '有', '為', '以', '與', '將', '等', '方面', '這個', '可以', '並', '就是'}
        for word in words:
            if word.strip() and not re.match(r'^\W+$', word) and word not in stop_words:
                filtered_words.append(word)
        
        return ' '.join(filtered_words)
    
    def extract_features(self, text):
        """特徵提取
        
        Args:
            text: 預處理後的文本
            
        Returns:
            特徵字典
        """
        features = {}
        
        # TF-IDF關鍵詞提取
        keywords = jieba.analyse.extract_tags(text, topK=20)
        for keyword in keywords:
            features[f'keyword_{keyword}'] = True
        
        # 分類特定詞匹配度
        for category, words in self.category_keywords.items():
            count = 0
            for word in words:
                if word in text:
                    count += 1
            if len(words) > 0:
                features[f'category_{category}'] = count / len(words)
            else:
                features[f'category_{category}'] = 0
        
        # 文本長度特徵
        features['text_length'] = len(text)
        
        return features
    
    def train_model(self, news_data):
        """訓練分類模型
        
        Args:
            news_data: 新聞數據列表，每個元素為dict包含'title', 'content', 'category'
            
        Returns:
            訓練結果報告
        """
        try:
            # 提取類別標籤
            categories = set(item['category'] for item in news_data)
            self.categories = list(categories)
            logger.info(f"訓練數據包含 {len(self.categories)} 個類別: {self.categories}")
            
            # 準備訓練數據
            X = []
            y = []
            for item in news_data:
                title = item.get('title', '')
                content = item.get('content', '')
                summary = item.get('summary', '')
                
                # 合併標題和內容，標題權重更高
                full_text = f"{title} {title} {summary} {content}"
                processed_text = self.preprocess_text(full_text)
                
                X.append(processed_text)
                y.append(item['category'])
            
            # 分割訓練集和測試集
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # 創建分類管道
            self.pipeline = Pipeline([
                ('vectorizer', TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
                ('classifier', MultinomialNB())
            ])
            
            # 訓練模型
            self.pipeline.fit(X_train, y_train)
            
            # 評估模型
            y_pred = self.pipeline.predict(X_test)
            report = classification_report(y_test, y_pred)
            logger.info(f"模型訓練完成，評估報告:\n{report}")
            
            # 保存模型
            self._save_model()
            
            return {
                'status': 'success',
                'categories': self.categories,
                'sample_count': len(X),
                'report': report
            }
            
        except Exception as e:
            logger.error(f"模型訓練失敗: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def classify_news(self, title, content, summary=None):
        """對新聞進行分類
        
        Args:
            title: 新聞標題
            content: 新聞內容
            summary: 新聞摘要
            
        Returns:
            分類結果和信心度
        """
        try:
            # 檢查模型
            if not self.pipeline:
                self._load_model()
                if not self.pipeline:
                    return self._rule_based_classify(title, content, summary)
            
            # 合併文本
            full_text = f"{title} {title} {summary or ''} {content}"
            processed_text = self.preprocess_text(full_text)
            
            # 使用模型預測
            category = self.pipeline.predict([processed_text])[0]
            
            # 獲取各類別概率
            probabilities = self.pipeline.predict_proba([processed_text])[0]
            confidence = max(probabilities)
            
            # 獲取置信度排名
            category_probs = [(self.categories[i], prob) for i, prob in enumerate(probabilities)]
            category_probs.sort(key=lambda x: x[1], reverse=True)
            
            return {
                'category': category,
                'confidence': float(confidence),
                'top_categories': category_probs[:3]
            }
            
        except Exception as e:
            logger.error(f"新聞分類失敗: {e}")
            return self._rule_based_classify(title, content, summary)
    
    def _rule_based_classify(self, title, content, summary=None):
        """基於規則的分類（備用方法）
        
        Args:
            title: 新聞標題
            content: 新聞內容
            summary: 新聞摘要
            
        Returns:
            分類結果和信心度
        """
        # 合併文本
        full_text = f"{title} {title} {summary or ''} {content}"
        
        # 計算每個類別的匹配度
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = 0
            matched_keywords = []
            for keyword in keywords:
                if keyword in full_text:
                    score += 1
                    matched_keywords.append(keyword)
            
            if len(keywords) > 0:
                category_scores[category] = {
                    'score': score / len(keywords),
                    'matched_keywords': matched_keywords
                }
        
        # 找出得分最高的類別
        if category_scores:
            sorted_categories = sorted(category_scores.items(), key=lambda x: x[1]['score'], reverse=True)
            top_category = sorted_categories[0][0]
            confidence = sorted_categories[0][1]['score']
            matched_keywords = sorted_categories[0][1]['matched_keywords']
            
            top_categories = [(cat, score['score']) for cat, score in sorted_categories[:3]]
            
            return {
                'category': top_category,
                'confidence': float(confidence),
                'matched_keywords': matched_keywords,
                'top_categories': top_categories,
                'method': 'rule_based'
            }
        else:
            # 如果沒有匹配的類別，返回通用類別
            return {
                'category': '一般新聞',
                'confidence': 0.0,
                'matched_keywords': [],
                'top_categories': [('一般新聞', 0.0)],
                'method': 'rule_based'
            }
    
    def _save_model(self):
        """保存模型"""
        import pickle
        
        try:
            # 確保目錄存在
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            # 保存模型和類別標籤
            with open(self.model_path, 'wb') as f:
                pickle.dump({
                    'pipeline': self.pipeline,
                    'categories': self.categories
                }, f)
            
            logger.info(f"模型已保存到: {self.model_path}")
        except Exception as e:
            logger.error(f"保存模型失敗: {e}")
    
    def _load_model(self):
        """載入模型"""
        import pickle
        
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.pipeline = data['pipeline']
                    self.categories = data['categories']
                
                logger.info(f"已載入模型: {len(self.categories)}個類別")
                return True
            else:
                logger.warning(f"模型文件不存在: {self.model_path}")
                return False
        except Exception as e:
            logger.error(f"載入模型失敗: {e}")
            return False
    
    def reclassify_all_news(self, db_session, min_confidence=0.6):
        """重新分類所有新聞
        
        Args:
            db_session: 資料庫會話
            min_confidence: 最低信心度，低於此值的分類結果不採用
            
        Returns:
            分類統計
        """
        from database.models import News, NewsCategory
        
        try:
            # 載入模型
            if not self.pipeline:
                self._load_model()
            
            # 獲取所有新聞
            news_items = db_session.query(News).all()
            logger.info(f"開始重新分類 {len(news_items)} 條新聞")
            
            # 創建或獲取所有類別
            category_map = {}
            for category_name in self.categories:
                category = db_session.query(NewsCategory).filter_by(name=category_name).first()
                if not category:
                    category = NewsCategory(name=category_name, description=f"{category_name}相關新聞")
                    db_session.add(category)
                    db_session.flush()
                category_map[category_name] = category
            
            # 重新分類每條新聞
            stats = {
                'total': len(news_items),
                'updated': 0,
                'unchanged': 0,
                'low_confidence': 0
            }
            
            for news in news_items:
                result = self.classify_news(news.title, news.content, news.summary)
                
                if result['confidence'] >= min_confidence:
                    category_name = result['category']
                    
                    # 如果類別發生變化
                    if not news.category or news.category.name != category_name:
                        news.category = category_map[category_name]
                        news.category_confidence = result['confidence']
                        stats['updated'] += 1
                    else:
                        stats['unchanged'] += 1
                else:
                    stats['low_confidence'] += 1
            
            # 提交變更
            db_session.commit()
            logger.info(f"新聞重新分類完成: {stats['updated']}條更新，{stats['unchanged']}條未變，{stats['low_confidence']}條置信度過低")
            
            return stats
            
        except Exception as e:
            db_session.rollback()
            logger.error(f"新聞重新分類失敗: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

def add_classification_fields():
    """添加分類相關的資料庫欄位"""
    from app import create_app, db
    from config.settings import Config
    from sqlalchemy import Column, Float, Text
    
    app = create_app(Config)
    
    with app.app_context():
        try:
            # 檢查News表是否已存在category_confidence欄位
            from database.models import News
            if not hasattr(News, 'category_confidence'):
                from sqlalchemy import Column, Float
                from sqlalchemy.ext.declarative import declarative_base
                
                # 添加欄位
                Base = declarative_base()
                db.engine.execute('ALTER TABLE news ADD COLUMN category_confidence FLOAT DEFAULT NULL;')
                db.engine.execute('ALTER TABLE news ADD COLUMN classification_details TEXT DEFAULT NULL;')
                db.session.commit()
                
                logger.info("已添加分類相關的資料庫欄位")
            else:
                logger.info("分類相關的資料庫欄位已存在")
                
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"添加資料庫欄位失敗: {e}")
            return False

def prepare_training_data(db_session, min_samples=10, max_samples=1000):
    """從資料庫中準備訓練數據
    
    Args:
        db_session: 資料庫會話
        min_samples: 每個類別最少樣本數
        max_samples: 每個類別最多樣本數
        
    Returns:
        訓練數據列表
    """
    from database.models import News, NewsCategory
    
    try:
        # 獲取所有有效的類別
        categories = db_session.query(NewsCategory).filter(NewsCategory.news.any()).all()
        logger.info(f"找到 {len(categories)} 個有效類別")
        
        training_data = []
        for category in categories:
            # 獲取該類別下的新聞
            news_items = db_session.query(News).filter_by(category_id=category.id, status='active').limit(max_samples).all()
            
            if len(news_items) >= min_samples:
                for news in news_items:
                    training_data.append({
                        'title': news.title,
                        'content': news.content,
                        'summary': news.summary,
                        'category': category.name
                    })
                logger.info(f"類別 '{category.name}' 添加了 {len(news_items)} 個樣本")
            else:
                logger.info(f"類別 '{category.name}' 樣本數不足 ({len(news_items)} < {min_samples})，跳過")
        
        logger.info(f"總共準備了 {len(training_data)} 個訓練樣本")
        return training_data
    
    except Exception as e:
        logger.error(f"準備訓練數據失敗: {e}")
        return []

def main():
    """主函數"""
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/news_classifier.log'),
            logging.StreamHandler()
        ]
    )
    
    logger.info("啟動新聞分類系統")
    
    # 添加分類相關的資料庫欄位
    add_classification_fields()
    
    # 創建分類器
    classifier = NewsClassifier()
    
    # 創建應用上下文
    from app import create_app, db
    from config.settings import Config
    
    app = create_app(Config)
    
    with app.app_context():
        # 準備訓練數據
        training_data = prepare_training_data(db.session)
        
        if training_data:
            # 訓練模型
            training_result = classifier.train_model(training_data)
            logger.info(f"模型訓練結果: {training_result}")
            
            # 重新分類所有新聞
            reclassify_result = classifier.reclassify_all_news(db.session)
            logger.info(f"新聞重新分類結果: {reclassify_result}")
            
            return {
                'training': training_result,
                'reclassify': reclassify_result
            }
        else:
            logger.warning("沒有足夠的訓練數據，使用規則型分類")
            
            # 使用規則型分類器重新分類新聞
            reclassify_result = classifier.reclassify_all_news(db.session)
            logger.info(f"新聞重新分類結果: {reclassify_result}")
            
            return {
                'training': {'status': 'skipped'},
                'reclassify': reclassify_result
            }

if __name__ == "__main__":
    main()
