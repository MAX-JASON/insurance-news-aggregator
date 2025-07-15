"""
相關保險產品推薦系統
Related Insurance Product Recommendation System

根據新聞內容推薦相關保險產品
"""

import os
import json
import logging
import pickle
import time
import re
import sqlite3
import numpy as np
from pathlib import Path
from collections import defaultdict
import jieba
import jieba.analyse
from datetime import datetime

# 設置基本路徑
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'logs', 'product_recommendation.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('product.recommendation')

class ProductRecommender:
    """保險產品推薦器"""
    
    def __init__(self, db_path=None, cache_dir=None):
        """初始化推薦器
        
        Args:
            db_path: 數據庫路徑，None使用默認路徑
            cache_dir: 緩存目錄，None使用默認路徑
        """
        # 設置路徑
        if db_path is None:
            self.db_path = os.path.join(BASE_DIR, 'instance', 'insurance_news.db')
        else:
            self.db_path = db_path
        
        if cache_dir is None:
            self.cache_dir = os.path.join(BASE_DIR, 'cache', 'recommendations')
        else:
            self.cache_dir = cache_dir
        
        # 確保緩存目錄存在
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 載入產品數據
        self.products_file = os.path.join(BASE_DIR, 'data', 'products', 'insurance_products.json')
        self.products = self.load_products()
        
        # 緩存文件
        self.cache_file = os.path.join(self.cache_dir, 'recommendations_cache.pkl')
        self.recommendations_cache = self.load_cache()
        
        # 載入保險術語詞典
        self.load_insurance_dictionary()
        
        # 特徵向量緩存
        self.vectors_file = os.path.join(self.cache_dir, 'product_vectors.pkl')
        self.product_vectors = self.load_vectors()
    
    def load_products(self):
        """載入保險產品數據
        
        Returns:
            產品字典
        """
        # 檢查產品文件是否存在
        if not os.path.exists(self.products_file):
            # 創建產品目錄
            os.makedirs(os.path.dirname(self.products_file), exist_ok=True)
            # 創建示例產品數據
            self.create_sample_products()
        
        try:
            with open(self.products_file, 'r', encoding='utf-8') as f:
                products = json.load(f)
            logger.info(f"已載入 {len(products)} 個保險產品")
            return products
        except Exception as e:
            logger.error(f"載入保險產品失敗: {e}")
            return {}
    
    def create_sample_products(self):
        """創建示例產品數據"""
        products = {
            "life_insurance": {
                "id": "life_insurance",
                "name": "人壽保險",
                "description": "提供死亡、全殘等保障的基本保險產品，保障家人經濟安全。",
                "features": ["死亡給付", "殘廢給付", "滿期保險金", "分紅選項"],
                "tags": ["人壽", "死亡保障", "家庭保障", "長期保險"],
                "target_audience": ["家庭", "有撫養責任者", "中年人士", "高收入者"],
                "keywords": ["人壽", "壽險", "死亡", "殘廢", "家庭保障", "保障", "分紅保單"]
            },
            "health_insurance": {
                "id": "health_insurance",
                "name": "健康醫療保險",
                "description": "涵蓋疾病治療、住院醫療等費用的保險產品，減輕醫療費用負擔。",
                "features": ["住院給付", "手術費用", "門診給付", "重大疾病保障"],
                "tags": ["健康", "醫療", "住院", "疾病", "手術"],
                "target_audience": ["所有年齡層", "注重健康者", "慢性病患者"],
                "keywords": ["健康", "醫療", "住院", "手術", "疾病", "門診", "藥費", "癌症", "重大疾病"]
            },
            "accident_insurance": {
                "id": "accident_insurance",
                "name": "意外傷害保險",
                "description": "針對意外事故造成的傷害提供經濟保障的產品，包含意外死亡、殘廢及醫療費用。",
                "features": ["意外死亡給付", "意外殘廢給付", "意外醫療費用", "日常意外保障"],
                "tags": ["意外", "傷害", "醫療", "緊急"],
                "target_audience": ["各年齡層", "活動量大者", "特定職業工作者"],
                "keywords": ["意外", "傷害", "骨折", "燒燙傷", "交通事故", "緊急", "急診"]
            },
            "travel_insurance": {
                "id": "travel_insurance",
                "name": "旅行保險",
                "description": "為旅行期間可能發生的風險提供保障，包含醫療、行李損失、行程取消等。",
                "features": ["旅遊醫療", "行李遺失賠償", "旅程取消賠償", "旅遊責任險", "緊急援助服務"],
                "tags": ["旅遊", "旅行", "國外", "行李", "醫療"],
                "target_audience": ["旅行者", "商務差旅", "留學生", "海外工作者"],
                "keywords": ["旅遊", "旅行", "出國", "國外", "行李", "護照", "簽證", "班機延誤", "酒店", "遊輪"]
            },
            "auto_insurance": {
                "id": "auto_insurance",
                "name": "汽車保險",
                "description": "涵蓋汽車損失、責任及相關風險的保險產品，提供車輛與駕駛人保障。",
                "features": ["車損險", "第三責任險", "乘客險", "竊盜險", "道路救援"],
                "tags": ["汽車", "車輛", "交通", "駕駛", "責任"],
                "target_audience": ["車主", "駕駛人", "運輸業者"],
                "keywords": ["汽車", "車輛", "交通", "駕駛", "肇事", "車禍", "撞擊", "維修", "修車", "輪胎", "引擎"]
            },
            "property_insurance": {
                "id": "property_insurance",
                "name": "財產保險",
                "description": "保障房屋、建築物及內部財物因意外事故造成的損失，如火災、颱風、地震等。",
                "features": ["火災保障", "颱風保障", "地震保障", "水災保障", "財物損失"],
                "tags": ["財產", "房屋", "建築", "災害"],
                "target_audience": ["房屋所有者", "商業財產持有者", "租賃者"],
                "keywords": ["財產", "房屋", "建築", "火災", "颱風", "地震", "水災", "土石流", "雷擊", "爆炸", "財物"]
            },
            "liability_insurance": {
                "id": "liability_insurance",
                "name": "責任保險",
                "description": "保障因被保險人疏失而導致第三者人身傷亡或財產損失的賠償責任。",
                "features": ["公共責任", "產品責任", "專業責任", "雇主責任"],
                "tags": ["責任", "賠償", "公共", "雇主", "產品"],
                "target_audience": ["企業", "專業人士", "雇主", "產品製造商"],
                "keywords": ["責任", "賠償", "疏失", "過失", "訴訟", "公共責任", "專業責任", "雇主", "產品瑕疵"]
            },
            "commercial_insurance": {
                "id": "commercial_insurance",
                "name": "商業保險",
                "description": "為企業營運提供全面保障，包含財產、責任、營業中斷等風險保障。",
                "features": ["財產保障", "責任保障", "營業中斷", "員工保障", "網絡風險"],
                "tags": ["商業", "企業", "營運", "風險管理"],
                "target_audience": ["企業", "公司", "商店", "工廠"],
                "keywords": ["企業", "公司", "營運", "生意", "商業", "營業額", "虧損", "中斷", "員工", "網絡風險", "資安"]
            },
            "investment_insurance": {
                "id": "investment_insurance",
                "name": "投資型保險",
                "description": "結合保險保障與投資功能的產品，提供壽險保障同時創造資產增值機會。",
                "features": ["人壽保障", "投資帳戶", "資產增值", "靈活提領", "保費調整"],
                "tags": ["投資", "儲蓄", "增值", "理財"],
                "target_audience": ["有投資需求者", "中高收入者", "理財規劃者"],
                "keywords": ["投資", "理財", "基金", "股票", "債券", "報酬", "收益", "配息", "資產", "增值"]
            },
            "retirement_insurance": {
                "id": "retirement_insurance",
                "name": "退休年金保險",
                "description": "專為退休規劃設計的保險產品，提供定期給付，確保退休生活經濟來源。",
                "features": ["定期年金給付", "一次性給付選項", "保證給付期間", "累積期利息", "稅務優惠"],
                "tags": ["退休", "年金", "養老", "理財"],
                "target_audience": ["退休規劃者", "中年以上人士", "穩健理財者"],
                "keywords": ["退休", "養老", "年金", "領取", "定期給付", "老年", "晚年", "生活費", "安養"]
            }
        }
        
        try:
            with open(self.products_file, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            logger.info("已創建示例產品數據")
            return products
        except Exception as e:
            logger.error(f"創建示例產品數據失敗: {e}")
            return {}
    
    def load_cache(self):
        """載入推薦緩存
        
        Returns:
            推薦緩存字典
        """
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'rb') as f:
                    cache = pickle.load(f)
                logger.info(f"已載入推薦緩存，包含 {len(cache)} 條記錄")
                return cache
            return {}
        except Exception as e:
            logger.error(f"載入推薦緩存失敗: {e}")
            return {}
    
    def save_cache(self):
        """保存推薦緩存"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.recommendations_cache, f)
            logger.debug("推薦緩存已更新")
        except Exception as e:
            logger.error(f"保存推薦緩存失敗: {e}")
    
    def load_insurance_dictionary(self):
        """載入保險術語詞典"""
        try:
            # 檢查保險詞典
            dict_path = os.path.join(BASE_DIR, 'analyzer', 'insurance_dictionary.py')
            if os.path.exists(dict_path):
                sys.path.insert(0, str(BASE_DIR))
                from analyzer.insurance_dictionary import INSURANCE_TERMS
                
                # 加載保險詞彙到jieba
                for term in INSURANCE_TERMS:
                    jieba.add_word(term, freq=50000, tag='n')
                
                logger.info(f"已載入 {len(INSURANCE_TERMS)} 個保險術語")
            else:
                logger.warning("未找到保險術語詞典")
        except Exception as e:
            logger.error(f"載入保險術語詞典失敗: {e}")
    
    def load_vectors(self):
        """載入產品向量緩存
        
        Returns:
            產品向量字典
        """
        try:
            if os.path.exists(self.vectors_file) and os.path.getmtime(self.vectors_file) > os.path.getmtime(self.products_file):
                with open(self.vectors_file, 'rb') as f:
                    vectors = pickle.load(f)
                logger.info(f"已載入 {len(vectors)} 個產品向量")
                return vectors
            
            # 如果沒有緩存或產品文件更新，重新生成向量
            return self.generate_product_vectors()
        
        except Exception as e:
            logger.error(f"載入產品向量失敗: {e}")
            return self.generate_product_vectors()
    
    def generate_product_vectors(self):
        """生成產品特徵向量
        
        Returns:
            產品向量字典
        """
        vectors = {}
        
        for product_id, product in self.products.items():
            # 提取產品文本
            text = (
                product['name'] + ' ' +
                product['description'] + ' ' +
                ' '.join(product.get('features', [])) + ' ' +
                ' '.join(product.get('tags', [])) + ' ' +
                ' '.join(product.get('keywords', []))
            )
            
            # 提取關鍵詞
            keywords = jieba.analyse.extract_tags(text, topK=20, withWeight=True)
            
            # 創建詞頻字典
            word_weights = {}
            for word, weight in keywords:
                word_weights[word] = weight
            
            # 保存向量
            vectors[product_id] = word_weights
        
        # 緩存向量
        try:
            with open(self.vectors_file, 'wb') as f:
                pickle.dump(vectors, f)
            logger.info(f"已生成並緩存 {len(vectors)} 個產品向量")
        except Exception as e:
            logger.error(f"緩存產品向量失敗: {e}")
        
        return vectors
    
    def get_product_by_id(self, product_id):
        """根據ID獲取產品
        
        Args:
            product_id: 產品ID
            
        Returns:
            產品字典，未找到則返回None
        """
        return self.products.get(product_id)
    
    def get_all_products(self):
        """獲取所有產品
        
        Returns:
            產品列表
        """
        return list(self.products.values())
    
    def extract_news_features(self, news):
        """提取新聞特徵
        
        Args:
            news: 新聞字典
            
        Returns:
            特徵字典
        """
        # 合併文本
        text = f"{news.get('title', '')} {news.get('summary', '')} {news.get('content', '')}"
        
        # 提取關鍵詞
        keywords = jieba.analyse.extract_tags(text, topK=30, withWeight=True)
        
        # 創建詞頻字典
        word_weights = {}
        for word, weight in keywords:
            word_weights[word] = weight
        
        return word_weights
    
    def calculate_similarity(self, news_features, product_features):
        """計算相似度
        
        Args:
            news_features: 新聞特徵字典
            product_features: 產品特徵字典
            
        Returns:
            相似度分數
        """
        # 提取所有關鍵詞
        all_words = set(list(news_features.keys()) + list(product_features.keys()))
        
        # 計算餘弦相似度
        dot_product = 0
        news_norm = 0
        product_norm = 0
        
        for word in all_words:
            news_weight = news_features.get(word, 0)
            product_weight = product_features.get(word, 0)
            
            dot_product += news_weight * product_weight
            news_norm += news_weight ** 2
            product_norm += product_weight ** 2
        
        news_norm = news_norm ** 0.5
        product_norm = product_norm ** 0.5
        
        if news_norm == 0 or product_norm == 0:
            return 0
        
        similarity = dot_product / (news_norm * product_norm)
        return similarity
    
    def recommend_products(self, news, limit=3):
        """推薦相關產品
        
        Args:
            news: 新聞字典
            limit: 最大推薦數
            
        Returns:
            推薦產品列表
        """
        news_id = news.get('id')
        
        # 檢查緩存
        if news_id in self.recommendations_cache:
            return self.recommendations_cache[news_id]
        
        # 提取新聞特徵
        news_features = self.extract_news_features(news)
        
        # 計算相似度
        similarities = []
        for product_id, product_features in self.product_vectors.items():
            similarity = self.calculate_similarity(news_features, product_features)
            similarities.append((product_id, similarity))
        
        # 排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # 提取推薦產品
        recommendations = []
        for product_id, similarity in similarities[:limit]:
            if similarity > 0.1:  # 設定最低相似度閾值
                product = self.get_product_by_id(product_id)
                if product:
                    recommendations.append({
                        'product': product,
                        'similarity': similarity
                    })
        
        # 更新緩存
        self.recommendations_cache[news_id] = recommendations
        self.save_cache()
        
        return recommendations
    
    def batch_process_news(self, days=7):
        """批量處理新聞
        
        Args:
            days: 最近天數
            
        Returns:
            處理結果統計
        """
        try:
            # 連接數據庫
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 計算時間範圍
            cutoff_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 查詢最近的新聞
            cursor.execute(
                """
                SELECT 
                    id, title, content, summary, published_at, source, url, importance_score 
                FROM 
                    news 
                WHERE 
                    published_at > date('now', ?) 
                ORDER BY 
                    published_at DESC
                """,
                (f'-{days} day',)
            )
            
            news_list = []
            for row in cursor.fetchall():
                news = {
                    'id': row[0],
                    'title': row[1],
                    'content': row[2],
                    'summary': row[3],
                    'published_at': row[4],
                    'source': row[5],
                    'url': row[6],
                    'importance_score': row[7]
                }
                news_list.append(news)
            
            # 關閉連接
            conn.close()
            
            # 處理每條新聞
            processed = 0
            for news in news_list:
                news_id = news['id']
                
                # 跳過已處理的新聞
                if news_id in self.recommendations_cache:
                    continue
                
                # 推薦產品
                recommendations = self.recommend_products(news)
                
                if recommendations:
                    processed += 1
            
            logger.info(f"批量處理完成，已處理 {processed} 條新聞")
            
            return {
                'total': len(news_list),
                'processed': processed,
                'cached': len(self.recommendations_cache)
            }
        
        except Exception as e:
            logger.error(f"批量處理新聞失敗: {e}")
            return {
                'total': 0,
                'processed': 0,
                'cached': len(self.recommendations_cache),
                'error': str(e)
            }
    
    def get_product_recommendation_stats(self):
        """獲取產品推薦統計
        
        Returns:
            統計數據字典
        """
        stats = {
            'total_recommendations': len(self.recommendations_cache),
            'product_distribution': defaultdict(int),
            'average_recommendations': 0
        }
        
        if not self.recommendations_cache:
            return stats
        
        # 計算產品分佈
        total_recs = 0
        for news_id, recommendations in self.recommendations_cache.items():
            total_recs += len(recommendations)
            for rec in recommendations:
                product_id = rec['product']['id']
                stats['product_distribution'][product_id] += 1
        
        # 計算平均推薦數
        if len(self.recommendations_cache) > 0:
            stats['average_recommendations'] = total_recs / len(self.recommendations_cache)
        
        # 將defaultdict轉為普通dict
        stats['product_distribution'] = dict(stats['product_distribution'])
        
        return stats

def main():
    """主函數"""
    import sys
    
    logging.info("啟動保險產品推薦系統")
    
    # 創建推薦器
    recommender = ProductRecommender()
    
    # 批量處理新聞
    result = recommender.batch_process_news(days=7)
    
    # 獲取統計數據
    stats = recommender.get_product_recommendation_stats()
    
    return {
        'status': 'success',
        'processing_result': result,
        'stats': stats
    }

if __name__ == "__main__":
    # 導入sys模組，需要在此處導入
    import sys
    main()
