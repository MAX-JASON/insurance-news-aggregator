"""
重要新聞推送服務
Important News Push Service

自動識別重要新聞並推送給相關業務員
"""

import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
import sqlite3
from pathlib import Path

# 導入相關模組
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notification.notification_service import notification_service
from database.models import News, User
from analyzer.importance_rating import ImportanceAnalyzer

logger = logging.getLogger(__name__)

@dataclass
class PushRule:
    """推送規則數據類"""
    name: str
    condition: Dict
    target_users: List[str]
    notification_methods: List[str]
    enabled: bool = True
    last_run: Optional[datetime] = None

class NewsPusher:
    """新聞推送服務類"""
    
    def __init__(self, db_path: Optional[str] = None, config_path: Optional[str] = None):
        """
        初始化推送服務
        
        Args:
            db_path: 資料庫路徑
            config_path: 配置檔案路徑
        """
        self.base_dir = Path(__file__).resolve().parent.parent
        self.db_path = db_path or self.base_dir / 'instance' / 'insurance_news.db'
        self.config_path = config_path or self.base_dir / 'config' / 'push_config.json'
        
        # 載入推送規則
        self.rules = self._load_push_rules()
        
        # 初始化重要性分析器
        self.importance_analyzer = ImportanceAnalyzer()
        
        # 推送歷史記錄
        self.push_history = []
        
    def _load_push_rules(self) -> List[PushRule]:
        """載入推送規則"""
        default_rules = [
            {
                "name": "高重要性新聞",
                "condition": {
                    "importance_score": {"min": 0.8},
                    "categories": ["重大政策", "市場動態", "法規變動"]
                },
                "target_users": ["all_active"],
                "notification_methods": ["email", "line"],
                "enabled": True
            },
            {
                "name": "緊急監管新聞",
                "condition": {
                    "importance_score": {"min": 0.9},
                    "keywords": ["金管會", "保險法", "監管", "罰款", "裁罰"],
                    "sentiment": "negative"
                },
                "target_users": ["managers", "compliance_officers"],
                "notification_methods": ["email", "line", "webhook"],
                "enabled": True
            },
            {
                "name": "業務機會提醒",
                "condition": {
                    "business_relevance": {"min": 0.7},
                    "keywords": ["新產品", "市場機會", "客群", "需求增長"]
                },
                "target_users": ["sales_agents"],
                "notification_methods": ["email"],
                "enabled": True
            },
            {
                "name": "每日重點摘要",
                "condition": {
                    "daily_summary": True,
                    "time": "08:00"
                },
                "target_users": ["all_users"],
                "notification_methods": ["email"],
                "enabled": True
            }
        ]
        
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    rules_data = json.load(f)
            else:
                rules_data = default_rules
                self._save_push_rules(rules_data)
                
            return [PushRule(**rule) for rule in rules_data]
        except Exception as e:
            logger.error(f"載入推送規則失敗: {e}")
            return [PushRule(**rule) for rule in default_rules]
    
    def _save_push_rules(self, rules_data: List[Dict]):
        """儲存推送規則"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(rules_data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            logger.error(f"儲存推送規則失敗: {e}")
    
    def check_and_push_news(self):
        """檢查並推送符合條件的新聞"""
        logger.info("開始檢查重要新聞推送...")
        
        # 獲取最近的新聞
        recent_news = self._get_recent_news()
        
        for rule in self.rules:
            if not rule.enabled:
                continue
                
            try:
                # 檢查是否為每日摘要規則
                if rule.condition.get('daily_summary'):
                    self._handle_daily_summary(rule)
                else:
                    # 檢查符合條件的新聞
                    matching_news = self._filter_news_by_rule(recent_news, rule)
                    if matching_news:
                        self._send_news_notifications(matching_news, rule)
                        
            except Exception as e:
                logger.error(f"處理推送規則 '{rule.name}' 失敗: {e}")
    
    def _get_recent_news(self, hours: int = 24) -> List[Dict]:
        """獲取最近的新聞"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            cursor.execute("""
                SELECT n.*, s.name as source_name, c.name as category_name
                FROM news n
                LEFT JOIN sources s ON n.source_id = s.id
                LEFT JOIN categories c ON n.category_id = c.id
                WHERE n.created_at >= ? AND n.status = 'active'
                ORDER BY n.created_at DESC
            """, (cutoff_time,))
            
            news_list = []
            for row in cursor.fetchall():
                news_data = dict(row)
                # 計算重要性分數（如果還沒有）
                if not news_data.get('importance_score'):
                    score = self.importance_analyzer.calculate_importance(
                        news_data['title'],
                        news_data['content']
                    )
                    news_data['importance_score'] = score
                
                news_list.append(news_data)
            
            conn.close()
            return news_list
            
        except Exception as e:
            logger.error(f"獲取最近新聞失敗: {e}")
            return []
    
    def _filter_news_by_rule(self, news_list: List[Dict], rule: PushRule) -> List[Dict]:
        """根據規則篩選新聞"""
        matching_news = []
        
        for news in news_list:
            if self._news_matches_rule(news, rule.condition):
                matching_news.append(news)
        
        return matching_news
    
    def _news_matches_rule(self, news: Dict, condition: Dict) -> bool:
        """檢查新聞是否符合規則條件"""
        try:
            # 檢查重要性分數
            if 'importance_score' in condition:
                importance_req = condition['importance_score']
                news_score = news.get('importance_score', 0)
                
                if 'min' in importance_req and news_score < importance_req['min']:
                    return False
                if 'max' in importance_req and news_score > importance_req['max']:
                    return False
            
            # 檢查分類
            if 'categories' in condition:
                required_categories = condition['categories']
                news_category = news.get('category_name', '')
                
                if news_category not in required_categories:
                    return False
            
            # 檢查關鍵詞
            if 'keywords' in condition:
                required_keywords = condition['keywords']
                news_text = f"{news.get('title', '')} {news.get('content', '')}"
                
                # 檢查是否包含任一關鍵詞
                if not any(keyword in news_text for keyword in required_keywords):
                    return False
            
            # 檢查業務相關性
            if 'business_relevance' in condition:
                relevance_req = condition['business_relevance']
                # 這裡可以根據實際的業務相關性評分來判斷
                # 暫時使用重要性分數作為替代
                business_score = news.get('importance_score', 0)
                
                if 'min' in relevance_req and business_score < relevance_req['min']:
                    return False
            
            # 檢查情感
            if 'sentiment' in condition:
                required_sentiment = condition['sentiment']
                news_sentiment = news.get('sentiment', 'neutral')
                
                if news_sentiment != required_sentiment:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"檢查新聞規則匹配失敗: {e}")
            return False
    
    def _get_target_users(self, target_users: List[str]) -> List[Dict]:
        """獲取目標用戶列表"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            users = []
            
            for target in target_users:
                if target == "all_active":
                    cursor.execute("SELECT * FROM users WHERE status = 'active'")
                    users.extend([dict(row) for row in cursor.fetchall()])
                elif target == "all_users":
                    cursor.execute("SELECT * FROM users")
                    users.extend([dict(row) for row in cursor.fetchall()])
                elif target == "managers":
                    cursor.execute("SELECT * FROM users WHERE role IN ('manager', 'admin')")
                    users.extend([dict(row) for row in cursor.fetchall()])
                elif target == "sales_agents":
                    cursor.execute("SELECT * FROM users WHERE role = 'agent'")
                    users.extend([dict(row) for row in cursor.fetchall()])
                elif target == "compliance_officers":
                    cursor.execute("SELECT * FROM users WHERE role = 'compliance'")
                    users.extend([dict(row) for row in cursor.fetchall()])
                else:
                    # 假設是具體的用戶ID或用戶名
                    cursor.execute("SELECT * FROM users WHERE id = ? OR username = ?", (target, target))
                    user = cursor.fetchone()
                    if user:
                        users.append(dict(user))
            
            conn.close()
            
            # 去重
            unique_users = {}
            for user in users:
                unique_users[user['id']] = user
            
            return list(unique_users.values())
            
        except Exception as e:
            logger.error(f"獲取目標用戶失敗: {e}")
            return []
    
    def _send_news_notifications(self, news_list: List[Dict], rule: PushRule):
        """發送新聞通知"""
        target_users = self._get_target_users(rule.target_users)
        
        if not target_users:
            logger.warning(f"規則 '{rule.name}' 沒有找到目標用戶")
            return
        
        # 準備通知內容
        subject = f"重要新聞提醒 - {rule.name}"
        content = self._format_news_notification(news_list, rule.name)
        html_content = self._format_news_notification_html(news_list, rule.name)
        
        # 收集郵件地址
        email_recipients = [user['email'] for user in target_users if user.get('email')]
        
        success_count = 0
        total_count = len(rule.notification_methods)
        
        # 發送通知
        for method in rule.notification_methods:
            try:
                if method == 'email' and email_recipients:
                    success = notification_service.send_email(
                        email_recipients, subject, content, html_content
                    )
                    if success:
                        success_count += 1
                        
                elif method == 'line':
                    line_message = f"📰 {subject}\n\n{self._format_news_for_line(news_list)}"
                    success = notification_service.send_line_notification(line_message)
                    if success:
                        success_count += 1
                        
                elif method == 'webhook':
                    webhook_data = {
                        "type": "news_alert",
                        "rule": rule.name,
                        "news_count": len(news_list),
                        "news": [self._summarize_news_for_webhook(news) for news in news_list],
                        "timestamp": datetime.now().isoformat()
                    }
                    success = notification_service.send_webhook_notification(webhook_data)
                    if success:
                        success_count += 1
                        
            except Exception as e:
                logger.error(f"發送 {method} 通知失敗: {e}")
        
        # 記錄推送歷史
        self._log_push_history(rule.name, len(news_list), len(target_users), success_count, total_count)
        
        logger.info(f"規則 '{rule.name}' 推送完成: {len(news_list)} 篇新聞, {len(target_users)} 位用戶, {success_count}/{total_count} 方式成功")
    
    def _handle_daily_summary(self, rule: PushRule):
        """處理每日摘要推送"""
        # 檢查是否已經發送過今日摘要
        today = datetime.now().date()
        if rule.last_run and rule.last_run.date() == today:
            return
        
        # 獲取今日重要新聞
        today_news = self._get_recent_news(hours=24)
        
        # 篩選重要新聞
        important_news = [news for news in today_news if news.get('importance_score', 0) >= 0.6]
        
        if important_news:
            # 按重要性排序
            important_news.sort(key=lambda x: x.get('importance_score', 0), reverse=True)
            
            # 取前10篇
            top_news = important_news[:10]
            
            self._send_daily_summary(top_news, rule)
            
            # 更新最後運行時間
            rule.last_run = datetime.now()
    
    def _send_daily_summary(self, news_list: List[Dict], rule: PushRule):
        """發送每日摘要"""
        target_users = self._get_target_users(rule.target_users)
        
        subject = f"每日保險新聞摘要 - {datetime.now().strftime('%Y年%m月%d日')}"
        content = self._format_daily_summary(news_list)
        html_content = self._format_daily_summary_html(news_list)
        
        # 發送郵件
        email_recipients = [user['email'] for user in target_users if user.get('email')]
        if email_recipients:
            success = notification_service.send_email(
                email_recipients, subject, content, html_content
            )
            
            if success:
                logger.info(f"每日摘要已發送給 {len(email_recipients)} 位用戶")
            else:
                logger.error("每日摘要發送失敗")
    
    def _format_news_notification(self, news_list: List[Dict], rule_name: str) -> str:
        """格式化新聞通知內容（純文字）"""
        content = f"根據規則「{rule_name}」，發現 {len(news_list)} 篇重要新聞：\n\n"
        
        for i, news in enumerate(news_list, 1):
            content += f"{i}. {news.get('title', '無標題')}\n"
            content += f"   來源：{news.get('source_name', '未知')}\n"
            content += f"   分類：{news.get('category_name', '未分類')}\n"
            content += f"   重要性：{news.get('importance_score', 0):.2f}\n"
            content += f"   時間：{news.get('published_date', news.get('created_at', ''))}\n"
            
            # 摘要內容（前200字）
            summary = news.get('content', '')[:200]
            if len(news.get('content', '')) > 200:
                summary += '...'
            content += f"   摘要：{summary}\n\n"
        
        content += "\n請登入系統查看完整內容。"
        return content
    
    def _format_news_notification_html(self, news_list: List[Dict], rule_name: str) -> str:
        """格式化新聞通知內容（HTML）"""
        html = f"""
        <html>
        <body>
            <h2>重要新聞提醒</h2>
            <p>根據規則「{rule_name}」，發現 <strong>{len(news_list)}</strong> 篇重要新聞：</p>
            
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr style="background-color: #f2f2f2;">
                    <th style="padding: 8px;">標題</th>
                    <th style="padding: 8px;">來源</th>
                    <th style="padding: 8px;">重要性</th>
                    <th style="padding: 8px;">時間</th>
                </tr>
        """
        
        for news in news_list:
            importance_color = "#ff4444" if news.get('importance_score', 0) >= 0.8 else "#ff8800" if news.get('importance_score', 0) >= 0.6 else "#4488ff"
            
            html += f"""
                <tr>
                    <td style="padding: 8px;">{news.get('title', '無標題')}</td>
                    <td style="padding: 8px;">{news.get('source_name', '未知')}</td>
                    <td style="padding: 8px; color: {importance_color}; font-weight: bold;">
                        {news.get('importance_score', 0):.2f}
                    </td>
                    <td style="padding: 8px;">{news.get('published_date', news.get('created_at', ''))}</td>
                </tr>
            """
        
        html += """
            </table>
            <br>
            <p>請登入系統查看完整內容。</p>
        </body>
        </html>
        """
        return html
    
    def _format_news_for_line(self, news_list: List[Dict]) -> str:
        """格式化LINE通知內容"""
        content = f"發現 {len(news_list)} 篇重要新聞：\n"
        
        for i, news in enumerate(news_list[:5], 1):  # LINE限制字數，只顯示前5篇
            content += f"\n{i}. {news.get('title', '無標題')}"
            content += f"\n📊 重要性：{news.get('importance_score', 0):.2f}"
            content += f"\n📰 來源：{news.get('source_name', '未知')}\n"
        
        if len(news_list) > 5:
            content += f"\n...還有 {len(news_list) - 5} 篇新聞"
        
        return content
    
    def _summarize_news_for_webhook(self, news: Dict) -> Dict:
        """為Webhook格式化新聞摘要"""
        return {
            "id": news.get('id'),
            "title": news.get('title'),
            "source": news.get('source_name'),
            "category": news.get('category_name'),
            "importance_score": news.get('importance_score'),
            "published_date": news.get('published_date'),
            "url": news.get('url')
        }
    
    def _format_daily_summary(self, news_list: List[Dict]) -> str:
        """格式化每日摘要（純文字）"""
        content = f"今日保險新聞摘要 ({datetime.now().strftime('%Y年%m月%d日')})\n"
        content += f"共收集 {len(news_list)} 篇重要新聞\n\n"
        
        for i, news in enumerate(news_list, 1):
            content += f"{i}. {news.get('title', '無標題')}\n"
            content += f"   重要性：{news.get('importance_score', 0):.2f} | "
            content += f"來源：{news.get('source_name', '未知')} | "
            content += f"分類：{news.get('category_name', '未分類')}\n\n"
        
        return content
    
    def _format_daily_summary_html(self, news_list: List[Dict]) -> str:
        """格式化每日摘要（HTML）"""
        html = f"""
        <html>
        <body>
            <h2>今日保險新聞摘要</h2>
            <p><strong>日期：</strong>{datetime.now().strftime('%Y年%m月%d日')}</p>
            <p><strong>重要新聞：</strong>{len(news_list)} 篇</p>
            
            <ol>
        """
        
        for news in news_list:
            importance_color = "#ff4444" if news.get('importance_score', 0) >= 0.8 else "#ff8800" if news.get('importance_score', 0) >= 0.6 else "#4488ff"
            
            html += f"""
                <li style="margin-bottom: 15px;">
                    <strong>{news.get('title', '無標題')}</strong><br>
                    <span style="color: {importance_color};">重要性：{news.get('importance_score', 0):.2f}</span> | 
                    <span>來源：{news.get('source_name', '未知')}</span> | 
                    <span>分類：{news.get('category_name', '未分類')}</span>
                </li>
            """
        
        html += """
            </ol>
            <p>詳細內容請登入系統查看。</p>
        </body>
        </html>
        """
        return html
    
    def _log_push_history(self, rule_name: str, news_count: int, user_count: int, success_count: int, total_count: int):
        """記錄推送歷史"""
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'rule_name': rule_name,
            'news_count': news_count,
            'user_count': user_count,
            'success_count': success_count,
            'total_count': total_count,
            'success_rate': success_count / total_count if total_count > 0 else 0
        }
        
        self.push_history.append(history_entry)
        
        # 限制歷史記錄大小
        if len(self.push_history) > 1000:
            self.push_history.pop(0)
    
    def get_push_statistics(self) -> Dict:
        """獲取推送統計數據"""
        if not self.push_history:
            return {
                'total_pushes': 0,
                'success_rate': 0,
                'recent_pushes': []
            }
        
        total_pushes = len(self.push_history)
        total_success = sum(h['success_count'] for h in self.push_history)
        total_attempts = sum(h['total_count'] for h in self.push_history)
        
        success_rate = total_success / total_attempts if total_attempts > 0 else 0
        
        # 最近10次推送
        recent_pushes = self.push_history[-10:]
        
        return {
            'total_pushes': total_pushes,
            'success_rate': success_rate,
            'recent_pushes': recent_pushes,
            'total_news_pushed': sum(h['news_count'] for h in self.push_history),
            'total_users_notified': sum(h['user_count'] for h in self.push_history)
        }

# 全域推送服務實例
news_pusher = NewsPusher()

if __name__ == "__main__":
    # 測試推送服務
    news_pusher.check_and_push_news()
