"""
新聞重要性評分系統
News Importance Rating System

為新聞條目提供多維度評分，包括業務相關性、時效性、客戶影響等
"""

import logging
import re
import math
import json
import os
from datetime import datetime, timedelta
from collections import Counter
from typing import Dict, List, Any, Tuple

from analyzer.text_processor import get_text_processor

logger = logging.getLogger(__name__)

class ImportanceRater:
    """多維度新聞重要性評分器"""
    
    def __init__(self, config_path=None):
        """初始化評分器"""
        self.logger = logging.getLogger(__name__)
        self.keywords = {}
        self.text_processor = get_text_processor()
        self.load_keywords(config_path)
        
    def load_keywords(self, config_path=None):
        """載入關鍵字與權重配置"""
        try:
            if not config_path:
                # 嘗試從預設路徑載入
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                config_path = os.path.join(base_dir, 'config', 'importance_keywords.json')
            
            if not os.path.exists(config_path):
                self.logger.warning(f"關鍵字配置文件不存在: {config_path}，使用預設配置")
                # 預設關鍵字與權重
                self.keywords = {
                    # 高重要性關鍵字 (權重1.5)
                    "高重要性": {
                        "法規": 1.5, "監管": 1.5, "金管會": 1.5, "保險局": 1.5,
                        "法律": 1.5, "強制": 1.5, "違規": 1.5, "罰款": 1.5,
                        "重大變更": 1.5, "必須": 1.5, "危機": 1.5, "緊急": 1.5
                    },
                    # 業務相關關鍵字 (權重1.2)
                    "業務相關": {
                        "銷售": 1.2, "業務": 1.2, "佣金": 1.2, "獎金": 1.2,
                        "通路": 1.2, "招攬": 1.2, "銷售策略": 1.2, "業績": 1.2,
                        "客戶": 1.2, "顧問": 1.2, "業務員": 1.2
                    },
                    # 產品關鍵字 (權重1.0)
                    "產品相關": {
                        "新產品": 1.0, "保單": 1.0, "壽險": 1.0, "健康險": 1.0,
                        "醫療險": 1.0, "重疾險": 1.0, "意外險": 1.0, "投資型": 1.0,
                        "保障": 1.0, "理賠": 1.0, "給付": 1.0
                    },
                    # 市場趨勢關鍵字 (權重0.8)
                    "市場趨勢": {
                        "趨勢": 0.8, "市場": 0.8, "發展": 0.8, "前景": 0.8,
                        "預測": 0.8, "變化": 0.8, "成長": 0.8, "競爭": 0.8
                    }
                }
            else:
                # 從配置文件載入
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.keywords = json.load(f)
                
            self.logger.info(f"成功載入關鍵字配置，共 {sum(len(v) for v in self.keywords.values())} 個關鍵字")
                
        except Exception as e:
            self.logger.error(f"載入關鍵字配置失敗: {e}")
            # 設置一個最小的關鍵字集合作為備份
            self.keywords = {
                "高重要性": {"法規": 1.5, "金管會": 1.5},
                "業務相關": {"業務": 1.2, "客戶": 1.2},
                "產品相關": {"保單": 1.0, "理賠": 1.0},
                "市場趨勢": {"趨勢": 0.8, "市場": 0.8}
            }
    
    def rate_importance(self, news_item):
        """根據新聞內容評估重要性分數
        
        Args:
            news_item: 包含標題、摘要、內容等屬性的新聞物件
            
        Returns:
            float: 0.0-1.0之間的重要性分數
        """
        try:
            # 準備分析文本
            title = news_item.title if hasattr(news_item, 'title') and news_item.title else ""
            summary = news_item.summary if hasattr(news_item, 'summary') and news_item.summary else ""
            content = news_item.content if hasattr(news_item, 'content') and news_item.content else ""
            
            # 多維度評分
            dimensions = self.calculate_dimensions(news_item, title, summary, content)
            
            # 根據各維度評分計算綜合得分
            weights = {
                "regulatory": 0.30,  # 法規重要性
                "business": 0.25,    # 業務影響
                "timeliness": 0.20,  # 時效性
                "client": 0.15,      # 客戶關注度
                "trend": 0.10        # 趨勢重要性
            }
            
            final_score = sum(dimensions[dim] * weights[dim] for dim in weights)
            
            # 記錄評分結果
            self.logger.debug(f"新聞「{title}」多維度評分: {dimensions}")
            self.logger.debug(f"新聞「{title}」最終重要性評分: {final_score:.2f}")
            
            return final_score
            
        except Exception as e:
            self.logger.error(f"評分過程發生錯誤: {e}")
            return 0.5  # 返回中等分數作為默認值
            
    def calculate_dimensions(self, news_item, title, summary, content):
        """計算新聞的多維度評分
        
        Args:
            news_item: 新聞項目
            title: 標題
            summary: 摘要
            content: 內容
            
        Returns:
            dict: 包含各維度評分的字典
        """
        # 合併文本，標題權重加強
        combined_text = f"{title} {title} {summary} {content}"
        
        # 使用文本處理器進行關鍵詞分析
        all_keywords = {k: v for category in self.keywords.values() for k, v in category.items()}
        keyword_matches = self.text_processor.find_keywords_in_text(combined_text, list(all_keywords.keys()), use_synonym=True)
        
        # 1. 法規重要性維度
        regulatory_keywords = self.keywords.get("高重要性", {})
        regulatory_score = self._calculate_dimension_score(keyword_matches, regulatory_keywords)
        
        # 2. 業務影響維度
        business_keywords = self.keywords.get("業務相關", {})
        business_score = self._calculate_dimension_score(keyword_matches, business_keywords)
        
        # 3. 產品相關維度
        product_keywords = self.keywords.get("產品相關", {})
        product_score = self._calculate_dimension_score(keyword_matches, product_keywords)
        
        # 4. 企業發展維度
        enterprise_keywords = self.keywords.get("企業發展", {}) if "企業發展" in self.keywords else {}
        enterprise_score = self._calculate_dimension_score(keyword_matches, enterprise_keywords)
        
        # 5. 趨勢重要性維度
        trend_keywords = self.keywords.get("市場趨勢", {})
        trend_score = self._calculate_dimension_score(keyword_matches, trend_keywords)
        
        # 6. 客戶關注度維度
        client_keywords = self.keywords.get("客戶服務", {}) if "客戶服務" in self.keywords else {}
        client_score = self._calculate_dimension_score(keyword_matches, client_keywords)
        
        # 7. 時效性維度評分
        timeliness_score = self._calculate_timeliness_score(news_item)
        
        # 8. 重大事件影響維度
        event_keywords = self.keywords.get("重大事件", {}) if "重大事件" in self.keywords else {}
        event_score = self._calculate_dimension_score(keyword_matches, event_keywords)
        
        # 整合業務相關維度（業務+產品+企業發展）
        combined_business_score = (business_score * 0.5 + product_score * 0.3 + enterprise_score * 0.2)
        
        # 整合趨勢重要性維度（趨勢+事件）
        combined_trend_score = (trend_score * 0.6 + event_score * 0.4)
        
        dimensions = {
            "regulatory": regulatory_score,
            "business": combined_business_score,
            "timeliness": timeliness_score,
            "client": client_score,
            "trend": combined_trend_score
        }
        
        return dimensions
    
    def _calculate_dimension_score(self, keyword_matches, dimension_keywords):
        """計算某一維度的評分
        
        Args:
            keyword_matches: 所有匹配到的關鍵詞及次數
            dimension_keywords: 該維度的關鍵詞及權重
            
        Returns:
            float: 0.0-1.0之間的維度評分
        """
        if not dimension_keywords:
            return 0.0
            
        score = 0.0
        max_possible = sum(sorted([w for w in dimension_keywords.values()], reverse=True)[:3])
        
        for keyword, weight in dimension_keywords.items():
            if keyword in keyword_matches:
                count = keyword_matches[keyword]
                score += min(count, 3) * weight  # 限制單一關鍵字的最大貢獻
        
        if max_possible <= 0:
            max_possible = 1
            
        return min(score / max_possible, 1.0)
    
    def _calculate_timeliness_score(self, news_item):
        """計算新聞的時效性評分
        
        Args:
            news_item: 新聞項目
            
        Returns:
            float: 0.0-1.0之間的時效性評分
        """
        # 默認時效性分數
        timeliness_score = 0.5
        
        if hasattr(news_item, 'published_date') and news_item.published_date:
            days_old = (datetime.now() - news_item.published_date).days
            
            if days_old <= 1:  # 1天內
                timeliness_score = 1.0
            elif days_old <= 2:  # 2天內
                timeliness_score = 0.9
            elif days_old <= 3:  # 3天內
                timeliness_score = 0.8
            elif days_old <= 5:  # 5天內
                timeliness_score = 0.7
            elif days_old <= 7:  # 一週內
                timeliness_score = 0.6
            elif days_old <= 14:  # 兩週內
                timeliness_score = 0.4
            elif days_old <= 30:  # 一個月內
                timeliness_score = 0.3
            else:  # 一個月以上
                timeliness_score = 0.2
        
        return timeliness_score
    
    def analyze_business_impact(self, news_item):
        """分析新聞對業務的影響
        
        Args:
            news_item: 包含標題、摘要、內容等屬性的新聞物件
            
        Returns:
            dict: 包含影響類型、影響程度、建議行動的字典
        """
        impact_types = {
            "客戶關係": ["客戶", "服務", "滿意度", "投訴", "理賠", "體驗", "服務品質", "客服", "諮詢"],
            "產品策略": ["新產品", "產品調整", "保費", "保障", "給付", "商品設計", "產品升級", "停售", "費率"],
            "銷售技巧": ["銷售", "業績", "說明", "解釋", "溝通", "招攬", "銷售策略", "業務員", "顧問"],
            "法規合規": ["法規", "監管", "金管會", "違規", "合規", "保險法", "法令遵循", "罰款", "強制規定"],
            "市場競爭": ["競爭", "市占", "同業", "優勢", "策略", "市場佔有", "市場份額", "競爭對手"],
            "數位轉型": ["數位", "科技", "線上", "APP", "網路", "平台", "智能", "自動化", "電子保單"],
            "風險管理": ["風險", "資本", "準備金", "清償", "評等", "償付能力", "風險控制", "再保險"],
            "投資策略": ["投資", "報酬", "收益", "利率", "資產", "配置", "投資組合", "ESG"]
        }
        
        try:
            # 準備分析文本
            title = news_item.title if hasattr(news_item, 'title') and news_item.title else ""
            summary = news_item.summary if hasattr(news_item, 'summary') and news_item.summary else ""
            content = news_item.content if hasattr(news_item, 'content') and news_item.content else ""
            
            combined_text = f"{title} {title} {summary} {content}"  # 標題權重加倍
            
            # 使用文本處理器進行分析
            impact_scores = {}
            
            for impact_type, keywords in impact_types.items():
                # 使用文本處理器查找關鍵字
                matches = self.text_processor.find_keywords_in_text(combined_text, keywords, use_synonym=True)
                
                if matches:
                    # 計算分數 (關鍵詞出現總數 + 唯一關鍵詞數量*0.5)
                    match_count = sum(matches.values())
                    unique_matches = len(matches)
                    score = match_count + unique_matches * 0.5
                    impact_scores[impact_type] = score
                else:
                    impact_scores[impact_type] = 0
            
            # 找出影響最大的兩個類型
            sorted_impacts = sorted(impact_scores.items(), key=lambda x: x[1], reverse=True)
            primary_impact = sorted_impacts[0][0] if sorted_impacts else "一般業務"
            
            # 如果第二大影響接近第一大影響，則一併考慮
            secondary_impact = None
            if len(sorted_impacts) > 1:
                if sorted_impacts[1][1] > 0 and sorted_impacts[0][1] > 0:
                    ratio = sorted_impacts[1][1] / sorted_impacts[0][1]
                    if ratio >= 0.7:  # 如果第二大影響至少為第一大影響的70%
                        secondary_impact = sorted_impacts[1][0]
            
            # 根據多維度評分確定影響程度
            dimensions = self.calculate_dimensions(news_item, title, summary, content)
            
            # 整合各維度評分
            regulatory_weight = 0.4
            business_weight = 0.3
            timeliness_weight = 0.2
            client_weight = 0.1
            
            impact_score = (dimensions["regulatory"] * regulatory_weight +
                           dimensions["business"] * business_weight +
                           dimensions["timeliness"] * timeliness_weight +
                           dimensions["client"] * client_weight)
            
            # 決定影響程度
            if impact_score >= 0.7:
                impact_level = "高"
                urgency = "亟需關注"
            elif impact_score >= 0.4:
                impact_level = "中"
                urgency = "建議關注"
            else:
                impact_level = "低"
                urgency = "可作參考"
            
            # 生成業務建議
            suggestions = {
                "客戶關係": "與客戶主動溝通相關新聞內容，增強信任關係，提升服務體驗",
                "產品策略": "了解產品細節，針對新聞調整商品推薦策略，掌握產品變更要點",
                "銷售技巧": "根據新聞內容調整銷售話術和說明方式，強化商品優勢說明",
                "法規合規": "確保業務活動符合新法規要求，立即調整不符合規定的作業流程，避免違規風險",
                "市場競爭": "分析競爭情況，強調自家產品相較於競品的優勢，掌握市場動態",
                "數位轉型": "熟悉公司數位工具和平台操作，協助客戶適應新的數位服務",
                "風險管理": "了解公司風險管理政策，向客戶說明保險公司財務穩健性的重要性",
                "投資策略": "掌握投資型保單的最新投資策略，向客戶清楚說明報酬與風險"
            }
            
            action = suggestions.get(primary_impact, "關注相關發展並適時與客戶分享資訊")
            
            # 如果有次要影響類型，加入次要建議
            if secondary_impact:
                secondary_action = suggestions.get(secondary_impact, "")
                if secondary_action and secondary_action != action:
                    action += f"；另外，{secondary_action.lower()}"
            
            result = {
                "type": primary_impact,
                "level": impact_level,
                "urgency": urgency,
                "action": action
            }
            
            # 如果有次要影響類型，加入結果
            if secondary_impact:
                result["secondary_type"] = secondary_impact
            
            return result
            
        except Exception as e:
            self.logger.error(f"影響分析過程發生錯誤: {e}")
            return {
                "type": "未知",
                "level": "中",
                "urgency": "需進一步評估",
                "action": "建議追蹤新聞後續發展"
            }

    def calculate_client_interest(self, news_item):
        """計算客戶可能感興趣的程度
        
        Args:
            news_item: 新聞條目
            
        Returns:
            dict: 包含興趣程度和原因的字典
        """
        try:
            # 計算多維度評分
            title = news_item.title if hasattr(news_item, 'title') and news_item.title else ""
            summary = news_item.summary if hasattr(news_item, 'summary') and news_item.summary else ""
            content = news_item.content if hasattr(news_item, 'content') and news_item.content else ""
            
            dimensions = self.calculate_dimensions(news_item, title, summary, content)
            
            # 客戶關注度類別
            client_interest_categories = {
                "權益變動": ["權益", "福利", "優惠", "增加", "提升", "改善", "調降", "減少", "縮減", "取消"],
                "理賠相關": ["理賠", "給付", "申請", "審核", "拒賠", "理賠期間", "給付條件", "賠償"],
                "保費調整": ["保費", "費率", "調整", "調漲", "調降", "折扣", "優惠", "減免", "分期"],
                "稅務優惠": ["稅", "節稅", "扣除額", "免稅", "稅務優惠", "退稅", "減稅", "稅額抵減"],
                "保障範圍": ["保障", "範圍", "承保", "除外責任", "不保事項", "等待期", "承保條件"],
                "服務升級": ["服務", "升級", "改善", "線上", "數位", "方便", "簡化", "流程優化"],
                "健康風險": ["健康", "疾病", "預防", "保健", "檢查", "風險因子", "生活習慣"],
                "退休規劃": ["退休", "老年", "年金", "養老", "長照", "老人", "高齡化"]
            }
            
            combined_text = f"{title} {title} {summary} {content}"  # 標題權重加倍
            
            # 分析各類別的相關性
            category_scores = {}
            for category, keywords in client_interest_categories.items():
                matches = self.text_processor.find_keywords_in_text(combined_text, keywords, use_synonym=True)
                if matches:
                    # 計算分數
                    score = sum(matches.values()) + len(matches) * 0.5
                    category_scores[category] = score
                else:
                    category_scores[category] = 0
            
            # 找出最相關的類別
            sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
            top_categories = [c for c, s in sorted_categories if s > 0][:2]  # 最多取前兩個相關類別
            
            # 計算客戶興趣分數
            # 基於多維度評分和客戶相關類別
            client_dimension = dimensions["client"] * 0.6  # 客戶維度佔60%
            regulatory_dimension = dimensions["regulatory"] * 0.1  # 法規維度佔10%
            business_dimension = dimensions["business"] * 0.2  # 業務維度佔20%
            timeliness_dimension = dimensions["timeliness"] * 0.1  # 時效性維度佔10%
            
            # 客戶類別相關性加成
            category_bonus = 0.0
            if top_categories:
                category_bonus = min(sorted_categories[0][1] / 5, 0.3)  # 最高加成0.3
            
            # 最終客戶興趣分數
            interest_score = client_dimension + regulatory_dimension + business_dimension + timeliness_dimension + category_bonus
            interest_score = min(interest_score, 1.0)  # 確保不超過1.0
            
            # 確定興趣級別和原因
            if interest_score >= 0.7:
                interest_level = "高"
                if top_categories:
                    reason = f"涉及{', '.join(top_categories)}等客戶直接關注議題"
                else:
                    reason = "業界重要新聞，可提升專業形象並增強客戶信任"
            elif interest_score >= 0.4:
                interest_level = "中"
                if top_categories:
                    reason = f"與{top_categories[0]}相關，適合選擇性分享給相關客戶"
                else:
                    reason = "與客戶保障間接相關，可適當分享以展現專業"
            else:
                interest_level = "低"
                reason = "行業一般資訊，非針對特定客群，可視情況分享"
            
            # 準備客戶分享建議
            sharing_suggestions = {
                "權益變動": "向客戶說明新聞中的權益變動如何影響其保單權益",
                "理賠相關": "解釋理賠程序變化或提醒客戶理賠注意事項",
                "保費調整": "說明保費調整原因及對客戶現有保單的潛在影響",
                "稅務優惠": "提醒客戶保險相關稅務優惠及如何善用",
                "保障範圍": "向客戶解釋保障範圍的變化及其重要性",
                "服務升級": "介紹新的服務功能及如何使客戶受益",
                "健康風險": "分享健康相關資訊，並連結至保險保障需求",
                "退休規劃": "討論退休規劃相關話題，引導客戶思考長期保障"
            }
            
            sharing_advice = ""
            if top_categories:
                sharing_advice = sharing_suggestions.get(top_categories[0], "")
            
            return {
                "level": interest_level,
                "score": interest_score,
                "reason": reason,
                "categories": top_categories,
                "sharing_advice": sharing_advice
            }
            
        except Exception as e:
            self.logger.error(f"客戶興趣分析錯誤: {e}")
            return {
                "level": "中",
                "score": 0.5,
                "reason": "無法完全分析，建議由業務員判斷",
                "categories": [],
                "sharing_advice": "建議閱讀新聞內容後再決定是否與客戶分享"
            }
