"""
客戶端問答範本管理
Client Q&A Template Management

提供客戶常見問答範本管理功能
"""

import os
import json
import time
import logging
from datetime import datetime
import re
import random
from collections import defaultdict
import pickle
from pathlib import Path

# 設置日誌
logger = logging.getLogger('templates.qa')

class TemplateManager:
    """問答範本管理器"""
    
    def __init__(self, templates_dir='data/templates', cache_dir='cache/templates'):
        """初始化
        
        Args:
            templates_dir: 範本存儲目錄
            cache_dir: 範本緩存目錄
        """
        self.templates_dir = templates_dir
        self.cache_dir = cache_dir
        self.templates = {}
        self.categories = set()
        self.last_loaded = 0
        self.cache_file = os.path.join(cache_dir, 'templates_cache.pkl')
        
        # 確保目錄存在
        os.makedirs(templates_dir, exist_ok=True)
        os.makedirs(cache_dir, exist_ok=True)
        
        # 載入範本
        self.load_templates()
    
    def load_templates(self, force=False):
        """載入所有範本
        
        Args:
            force: 是否強制重新載入
        """
        # 檢查是否需要重新載入
        if not force and self.templates and time.time() - self.last_loaded < 3600:
            return
        
        # 嘗試從緩存載入
        if not force and os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                    if cache_data.get('timestamp', 0) > self.last_loaded:
                        self.templates = cache_data.get('templates', {})
                        self.categories = cache_data.get('categories', set())
                        self.last_loaded = cache_data.get('timestamp', time.time())
                        logger.info(f"從緩存載入 {len(self.templates)} 個範本")
                        return
            except Exception as e:
                logger.error(f"載入範本緩存失敗: {e}")
        
        # 從文件載入
        try:
            templates = {}
            categories = set()
            
            # 遍歷目錄中的所有JSON文件
            for root, _, files in os.walk(self.templates_dir):
                for file in files:
                    if not file.endswith('.json'):
                        continue
                    
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                            # 處理每個範本
                            for template in data.get('templates', []):
                                if 'id' not in template or 'question' not in template or 'answer' not in template:
                                    logger.warning(f"範本格式不正確: {template}")
                                    continue
                                
                                template_id = template['id']
                                templates[template_id] = template
                                
                                # 添加分類
                                if 'categories' in template:
                                    for category in template['categories']:
                                        categories.add(category)
                    except Exception as e:
                        logger.error(f"載入範本文件失敗 {file_path}: {e}")
            
            self.templates = templates
            self.categories = categories
            self.last_loaded = time.time()
            logger.info(f"載入 {len(templates)} 個範本")
            
            # 儲存到緩存
            self._save_cache()
        
        except Exception as e:
            logger.error(f"載入範本失敗: {e}")
    
    def _save_cache(self):
        """儲存範本到緩存"""
        try:
            cache_data = {
                'templates': self.templates,
                'categories': self.categories,
                'timestamp': time.time()
            }
            
            with open(self.cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            logger.debug("範本緩存已更新")
        except Exception as e:
            logger.error(f"儲存範本緩存失敗: {e}")
    
    def get_template(self, template_id):
        """獲取特定範本
        
        Args:
            template_id: 範本ID
            
        Returns:
            範本字典，不存在則返回None
        """
        # 確保範本已載入
        self.load_templates()
        
        return self.templates.get(template_id)
    
    def search_templates(self, query, category=None, limit=10):
        """搜索範本
        
        Args:
            query: 搜索關鍵詞
            category: 範本分類
            limit: 最大結果數
            
        Returns:
            範本列表
        """
        # 確保範本已載入
        self.load_templates()
        
        results = []
        query = query.lower()
        
        for template in self.templates.values():
            # 檢查分類
            if category and category not in template.get('categories', []):
                continue
            
            # 檢查關鍵詞
            if (query in template.get('question', '').lower() or
                query in template.get('answer', '').lower() or
                any(query in keyword.lower() for keyword in template.get('keywords', []))):
                results.append(template)
            
            # 達到限制數量時停止
            if len(results) >= limit:
                break
        
        return results
    
    def get_categories(self):
        """獲取所有分類
        
        Returns:
            分類集合
        """
        # 確保範本已載入
        self.load_templates()
        
        return list(self.categories)
    
    def add_template(self, template):
        """添加新範本
        
        Args:
            template: 範本字典
            
        Returns:
            範本ID
        """
        # 確保範本已載入
        self.load_templates()
        
        # 驗證範本格式
        if 'question' not in template or 'answer' not in template:
            raise ValueError("範本必須包含問題和答案")
        
        # 生成ID
        if 'id' not in template:
            template['id'] = f"template_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # 添加時間戳
        template['created_at'] = template.get('created_at', datetime.now().isoformat())
        template['updated_at'] = datetime.now().isoformat()
        
        # 儲存範本
        self.templates[template['id']] = template
        
        # 添加分類
        if 'categories' in template:
            for category in template['categories']:
                self.categories.add(category)
        
        # 儲存到文件
        self._save_template_to_file(template)
        
        # 更新緩存
        self._save_cache()
        
        return template['id']
    
    def update_template(self, template_id, template):
        """更新範本
        
        Args:
            template_id: 範本ID
            template: 範本字典
            
        Returns:
            布爾值，表示是否更新成功
        """
        # 確保範本已載入
        self.load_templates()
        
        # 檢查範本是否存在
        if template_id not in self.templates:
            return False
        
        # 更新範本
        template['id'] = template_id
        template['updated_at'] = datetime.now().isoformat()
        self.templates[template_id] = template
        
        # 更新分類
        if 'categories' in template:
            for category in template['categories']:
                self.categories.add(category)
        
        # 儲存到文件
        self._save_template_to_file(template)
        
        # 更新緩存
        self._save_cache()
        
        return True
    
    def delete_template(self, template_id):
        """刪除範本
        
        Args:
            template_id: 範本ID
            
        Returns:
            布爾值，表示是否刪除成功
        """
        # 確保範本已載入
        self.load_templates()
        
        # 檢查範本是否存在
        if template_id not in self.templates:
            return False
        
        # 獲取範本所在文件
        template = self.templates[template_id]
        category = template.get('categories', ['general'])[0]
        file_path = os.path.join(self.templates_dir, f"{category}.json")
        
        # 從內存中刪除
        del self.templates[template_id]
        
        # 從文件中刪除
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                data['templates'] = [t for t in data.get('templates', []) if t.get('id') != template_id]
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"從文件刪除範本失敗 {template_id}: {e}")
            return False
        
        # 更新緩存
        self._save_cache()
        
        # 重新計算分類
        self._recalculate_categories()
        
        return True
    
    def _save_template_to_file(self, template):
        """將範本儲存到文件
        
        Args:
            template: 範本字典
        """
        # 確定範本所屬分類
        category = template.get('categories', ['general'])[0]
        file_path = os.path.join(self.templates_dir, f"{category}.json")
        
        try:
            # 讀取現有文件
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {'templates': []}
            
            # 更新範本
            templates = data.get('templates', [])
            updated = False
            
            for i, t in enumerate(templates):
                if t.get('id') == template['id']:
                    templates[i] = template
                    updated = True
                    break
            
            if not updated:
                templates.append(template)
            
            data['templates'] = templates
            
            # 寫入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        except Exception as e:
            logger.error(f"儲存範本到文件失敗: {e}")
    
    def _recalculate_categories(self):
        """重新計算所有分類"""
        categories = set()
        
        for template in self.templates.values():
            if 'categories' in template:
                for category in template['categories']:
                    categories.add(category)
        
        self.categories = categories

class ClientQueryMatcher:
    """客戶問題匹配器"""
    
    def __init__(self, template_manager):
        """初始化
        
        Args:
            template_manager: TemplateManager實例
        """
        self.template_manager = template_manager
        self.keyword_index = defaultdict(list)
        self.last_indexed = 0
        self.build_index()
    
    def build_index(self, force=False):
        """建立關鍵詞索引
        
        Args:
            force: 是否強制重建
        """
        # 檢查是否需要重建
        if not force and self.keyword_index and time.time() - self.last_indexed < 3600:
            return
        
        # 強制重新載入範本
        self.template_manager.load_templates(force=force)
        
        # 建立索引
        keyword_index = defaultdict(list)
        
        for template_id, template in self.template_manager.templates.items():
            # 從問題中提取關鍵詞
            question = template.get('question', '')
            keywords = template.get('keywords', [])
            
            # 添加問題中的關鍵詞
            question_keywords = self._extract_keywords(question)
            
            all_keywords = set(keywords + question_keywords)
            for keyword in all_keywords:
                keyword = keyword.lower()
                keyword_index[keyword].append(template_id)
        
        self.keyword_index = keyword_index
        self.last_indexed = time.time()
        logger.info(f"建立關鍵詞索引完成，共 {len(keyword_index)} 個關鍵詞")
    
    def _extract_keywords(self, text):
        """從文本中提取關鍵詞
        
        Args:
            text: 要提取的文本
            
        Returns:
            關鍵詞列表
        """
        # 簡單分詞，移除標點符號和停用詞
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        
        # 簡單停用詞過濾
        stopwords = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一個', '上', '也', '很', '到', '說', '要', '去', '你', '會', '著', '好', '自己', '這'}
        keywords = [w for w in words if len(w) > 1 and w not in stopwords]
        
        return keywords
    
    def match_query(self, query, threshold=0.3, limit=3):
        """匹配客戶問題
        
        Args:
            query: 客戶問題
            threshold: 匹配閾值
            limit: 最大結果數
            
        Returns:
            匹配結果列表
        """
        # 確保索引已建立
        self.build_index()
        
        # 提取查詢關鍵詞
        query_keywords = self._extract_keywords(query)
        query_keywords = [kw.lower() for kw in query_keywords]
        
        # 候選範本
        candidate_templates = defaultdict(int)
        
        # 根據關鍵詞查找候選範本
        for keyword in query_keywords:
            for template_id in self.keyword_index.get(keyword, []):
                candidate_templates[template_id] += 1
        
        # 計算匹配分數
        results = []
        for template_id, keyword_matches in candidate_templates.items():
            template = self.template_manager.get_template(template_id)
            if not template:
                continue
            
            # 計算基本分數
            keyword_score = keyword_matches / max(1, len(query_keywords))
            
            # 附加重要性分數
            importance = template.get('importance', 1)
            
            # 最終分數
            score = keyword_score * importance
            
            if score >= threshold:
                results.append({
                    'template_id': template_id,
                    'template': template,
                    'score': score
                })
        
        # 排序並限制結果數量
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]

def create_template_samples():
    """創建示例範本"""
    # 確保目錄存在
    templates_dir = 'data/templates'
    os.makedirs(templates_dir, exist_ok=True)
    
    # 保險類範本
    insurance_templates = {
        'templates': [
            {
                'id': 'ins_001',
                'question': '什麼是重大傷病保險？',
                'answer': '重大傷病保險是一種針對特定嚴重疾病或傷害提供保障的保險產品。當被保險人罹患保單所列的重大疾病（如癌症、心臟病、中風等）時，保險公司將支付約定的保險金。此類保險通常包含等待期，建議在健康狀況良好時及早投保。',
                'keywords': ['重大傷病', '重疾', '癌症', '心臟病', '保障'],
                'categories': ['insurance'],
                'importance': 1.5,
                'created_at': '2023-01-15T08:30:00',
                'updated_at': '2023-01-15T08:30:00'
            },
            {
                'id': 'ins_002',
                'question': '保險理賠流程是什麼？',
                'answer': '保險理賠流程一般包括以下步驟：1. 事故發生後立即通知保險公司；2. 填寫理賠申請書；3. 提交必要的證明文件（如診斷證明、收據等）；4. 保險公司進行審核；5. 核定後進行賠付。建議保留所有相關文件和證明，並在規定時間內提出申請。',
                'keywords': ['理賠', '流程', '申請', '賠付', '文件'],
                'categories': ['insurance'],
                'importance': 1.2,
                'created_at': '2023-01-16T10:15:00',
                'updated_at': '2023-01-16T10:15:00'
            },
            {
                'id': 'ins_003',
                'question': '如何選擇適合自己的保險產品？',
                'answer': '選擇保險產品時應考慮以下因素：1. 個人風險狀況和保障需求；2. 預算和支付能力；3. 保單條款和保障範圍；4. 保險公司的財務穩定性和理賠服務品質；5. 產品的性價比。建議先評估自身需求，必要時可諮詢專業保險顧問，選擇最適合自己的保障組合。',
                'keywords': ['選擇', '保險產品', '需求', '保障', '預算'],
                'categories': ['insurance'],
                'importance': 1.3,
                'created_at': '2023-01-17T14:20:00',
                'updated_at': '2023-01-17T14:20:00'
            }
        ]
    }
    
    # 企業類範本
    business_templates = {
        'templates': [
            {
                'id': 'bus_001',
                'question': '企業如何評估員工團體保險需求？',
                'answer': '企業評估員工團體保險需求可從以下方面考慮：1. 行業風險特性和員工崗位風險；2. 員工人口結構和健康狀況；3. 預算限制和成本效益；4. 現有福利計劃的補充；5. 競爭對手福利水平。完善的團體保險計劃可提高員工滿意度和忠誠度，同時降低人力資源風險。',
                'keywords': ['企業', '團體保險', '員工福利', '風險評估'],
                'categories': ['business'],
                'importance': 1.4,
                'created_at': '2023-01-18T09:45:00',
                'updated_at': '2023-01-18T09:45:00'
            },
            {
                'id': 'bus_002',
                'question': '企業如何處理商業中斷風險？',
                'answer': '企業可通過以下方式管理商業中斷風險：1. 購買營業中斷保險；2. 制定業務連續性計劃；3. 建立供應鏈多元化策略；4. 定期進行風險評估和演練；5. 建立應急基金。營業中斷保險可彌補因意外事故導致的營業損失，包括固定費用支出和預期利潤損失。',
                'keywords': ['商業中斷', '營業中斷', '業務連續性', '風險管理'],
                'categories': ['business'],
                'importance': 1.5,
                'created_at': '2023-01-19T11:30:00',
                'updated_at': '2023-01-19T11:30:00'
            },
            {
                'id': 'bus_003',
                'question': '企業責任險有哪些種類？',
                'answer': '企業責任險主要包括以下幾種：1. 公共責任險：涵蓋因企業經營導致第三方人身傷害或財產損失的賠償責任；2. 產品責任險：保障因產品缺陷導致的賠償責任；3. 專業責任險：針對專業服務過失導致的賠償責任；4. 董事及高管責任險：保障企業管理層因決策失誤面臨的個人賠償；5. 雇主責任險：保障因工作環境導致員工傷亡的賠償。',
                'keywords': ['企業責任險', '公共責任', '產品責任', '專業責任', '董事責任'],
                'categories': ['business'],
                'importance': 1.3,
                'created_at': '2023-01-20T15:10:00',
                'updated_at': '2023-01-20T15:10:00'
            }
        ]
    }
    
    # 存儲範本文件
    with open(os.path.join(templates_dir, 'insurance.json'), 'w', encoding='utf-8') as f:
        json.dump(insurance_templates, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(templates_dir, 'business.json'), 'w', encoding='utf-8') as f:
        json.dump(business_templates, f, ensure_ascii=False, indent=2)
    
    logger.info("示例範本已創建")

def main():
    """主函數"""
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/templates.log'),
            logging.StreamHandler()
        ]
    )
    
    logger.info("啟動客戶問答範本管理")
    
    # 創建示例範本
    if not os.path.exists('data/templates'):
        logger.info("創建示例範本")
        create_template_samples()
    
    # 初始化範本管理器
    template_manager = TemplateManager()
    
    # 初始化問題匹配器
    query_matcher = ClientQueryMatcher(template_manager)
    
    # 測試範本搜索
    query = "保險理賠流程是什麼"
    results = query_matcher.match_query(query)
    
    logger.info(f"測試查詢: '{query}'")
    for i, result in enumerate(results, 1):
        template = result['template']
        logger.info(f"結果 {i}: {template['question']} (分數: {result['score']:.2f})")
    
    return {
        'status': 'success',
        'templates_count': len(template_manager.templates),
        'categories': template_manager.get_categories(),
        'search_test': {
            'query': query,
            'results': len(results)
        }
    }

if __name__ == "__main__":
    main()
