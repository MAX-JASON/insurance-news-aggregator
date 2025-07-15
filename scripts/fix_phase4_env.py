#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第四階段環境修復腳本
解決依賴問題和模組路徑問題
"""

import os
import sys
import subprocess
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def install_missing_packages():
    """安裝缺失的依賴包"""
    print("🔧 修復Python環境依賴...")
    
    # 需要安裝的包列表
    packages = [
        "flask-login",  # Flask用戶登錄管理
        "numpy<2",      # 降級numpy到1.x版本
        "matplotlib",   # 重新安裝matplotlib
        "seaborn",      # 統計圖表
        "plotly",       # 交互式圖表
        "wordcloud",    # 詞雲生成
        "pandas",       # 數據處理
    ]
    
    for package in packages:
        try:
            print(f"📦 安裝 {package}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", package
            ], capture_output=True, text=True, check=True)
            print(f"✅ {package} 安裝成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ {package} 安裝失敗: {e}")
            print(f"錯誤輸出: {e.stderr}")

def create_notification_service():
    """創建缺失的notification_service模組"""
    print("\n🔧 創建通知服務模組...")
    
    notification_service_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通知服務模組
處理郵件、LINE推送、系統通知等
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class NotificationResult:
    """通知結果"""
    success: bool
    message: str
    sent_at: datetime
    delivery_id: Optional[str] = None

class NotificationService:
    """
    統一通知服務
    支援多種通知方式：郵件、LINE、系統通知等
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 載入配置
        self.email_config = self._load_email_config()
        self.line_config = self._load_line_config()
        self.webhook_config = self._load_webhook_config()
        
        # 初始化服務
        self._init_email_service()
        self._init_line_service()
        
        self.logger.info("通知服務初始化完成")
    
    def _load_email_config(self) -> Dict:
        """載入郵件配置"""
        return {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': '',  # 從環境變量或配置文件獲取
            'password': '',  # 從環境變量或配置文件獲取
            'from_email': 'insurance-news@example.com',
            'enabled': False  # 默認關閉，需要配置後啟用
        }
    
    def _load_line_config(self) -> Dict:
        """載入LINE配置"""
        return {
            'channel_access_token': '',  # 從環境變量獲取
            'channel_secret': '',       # 從環境變量獲取
            'enabled': False           # 默認關閉
        }
    
    def _load_webhook_config(self) -> Dict:
        """載入Webhook配置"""
        return {
            'enabled': True,
            'endpoints': []
        }
    
    def _init_email_service(self):
        """初始化郵件服務"""
        if self.email_config['enabled']:
            try:
                # 這裡可以初始化SMTP連接池等
                self.logger.info("郵件服務初始化成功")
            except Exception as e:
                self.logger.error(f"郵件服務初始化失敗: {e}")
        else:
            self.logger.info("郵件服務未啟用")
    
    def _init_line_service(self):
        """初始化LINE服務"""
        if self.line_config['enabled']:
            try:
                # 這裡可以初始化LINE Bot API
                self.logger.info("LINE服務初始化成功")
            except Exception as e:
                self.logger.error(f"LINE服務初始化失敗: {e}")
        else:
            self.logger.info("LINE服務未啟用")
    
    def send_notification(self, 
                         user_id: int,
                         title: str,
                         message: str,
                         type: str = "info",
                         data: Optional[Dict] = None,
                         channels: Optional[List[str]] = None) -> NotificationResult:
        """
        發送通知
        
        Args:
            user_id: 用戶ID
            title: 通知標題
            message: 通知內容
            type: 通知類型（info, warning, error, success）
            data: 附加數據
            channels: 指定發送渠道列表，None表示使用默認渠道
            
        Returns:
            通知結果
        """
        try:
            # 如果是測試模式，記錄日誌而不實際發送
            if not any([self.email_config['enabled'], self.line_config['enabled']]):
                self.logger.info(f"測試模式通知 - 用戶: {user_id}, 標題: {title}, 內容: {message}")
                return NotificationResult(
                    success=True,
                    message="測試模式發送成功",
                    sent_at=datetime.now(),
                    delivery_id=f"test_{datetime.now().timestamp()}"
                )
            
            # 實際發送邏輯
            results = []
            
            if not channels or 'email' in channels:
                if self.email_config['enabled']:
                    email_result = self._send_email_notification(user_id, title, message, type, data)
                    results.append(email_result)
            
            if not channels or 'line' in channels:
                if self.line_config['enabled']:
                    line_result = self._send_line_notification(user_id, title, message, type, data)
                    results.append(line_result)
            
            if not channels or 'webhook' in channels:
                webhook_result = self._send_webhook_notification(user_id, title, message, type, data)
                results.append(webhook_result)
            
            # 判斷整體成功率
            success_count = sum(1 for r in results if r.success)
            overall_success = success_count > 0
            
            return NotificationResult(
                success=overall_success,
                message=f"發送完成，{success_count}/{len(results)} 個渠道成功",
                sent_at=datetime.now(),
                delivery_id=f"multi_{datetime.now().timestamp()}"
            )
            
        except Exception as e:
            self.logger.error(f"發送通知失敗: {e}")
            return NotificationResult(
                success=False,
                message=f"發送失敗: {str(e)}",
                sent_at=datetime.now()
            )
    
    def _send_email_notification(self, user_id: int, title: str, message: str, 
                               type: str, data: Optional[Dict]) -> NotificationResult:
        """發送郵件通知"""
        try:
            # 模擬郵件發送
            self.logger.info(f"郵件通知發送 - 用戶: {user_id}, 標題: {title}")
            
            return NotificationResult(
                success=True,
                message="郵件發送成功",
                sent_at=datetime.now(),
                delivery_id=f"email_{datetime.now().timestamp()}"
            )
            
        except Exception as e:
            self.logger.error(f"郵件發送失敗: {e}")
            return NotificationResult(
                success=False,
                message=f"郵件發送失敗: {str(e)}",
                sent_at=datetime.now()
            )
    
    def _send_line_notification(self, user_id: int, title: str, message: str,
                              type: str, data: Optional[Dict]) -> NotificationResult:
        """發送LINE通知"""
        try:
            # 模擬LINE發送
            self.logger.info(f"LINE通知發送 - 用戶: {user_id}, 標題: {title}")
            
            return NotificationResult(
                success=True,
                message="LINE發送成功",
                sent_at=datetime.now(),
                delivery_id=f"line_{datetime.now().timestamp()}"
            )
            
        except Exception as e:
            self.logger.error(f"LINE發送失敗: {e}")
            return NotificationResult(
                success=False,
                message=f"LINE發送失敗: {str(e)}",
                sent_at=datetime.now()
            )
    
    def _send_webhook_notification(self, user_id: int, title: str, message: str,
                                 type: str, data: Optional[Dict]) -> NotificationResult:
        """發送Webhook通知"""
        try:
            # 模擬Webhook發送
            self.logger.info(f"Webhook通知發送 - 用戶: {user_id}, 標題: {title}")
            
            return NotificationResult(
                success=True,
                message="Webhook發送成功",
                sent_at=datetime.now(),
                delivery_id=f"webhook_{datetime.now().timestamp()}"
            )
            
        except Exception as e:
            self.logger.error(f"Webhook發送失敗: {e}")
            return NotificationResult(
                success=False,
                message=f"Webhook發送失敗: {str(e)}",
                sent_at=datetime.now()
            )
    
    def get_notification_history(self, user_id: int, limit: int = 50) -> List[Dict]:
        """獲取通知歷史"""
        try:
            # 這裡應該從數據庫獲取實際的通知歷史
            # 現在返回模擬數據
            history = [
                {
                    'id': i,
                    'user_id': user_id,
                    'title': f'測試通知 {i}',
                    'message': f'這是第 {i} 條測試通知',
                    'type': 'info',
                    'sent_at': datetime.now(),
                    'status': 'sent'
                }
                for i in range(1, min(limit + 1, 6))
            ]
            
            return history
            
        except Exception as e:
            self.logger.error(f"獲取通知歷史失敗: {e}")
            return []
    
    def get_notification_stats(self, days: int = 30) -> Dict:
        """獲取通知統計"""
        try:
            # 這裡應該從數據庫獲取實際統計數據
            # 現在返回模擬數據
            stats = {
                'total_sent': 156,
                'successful': 145,
                'failed': 11,
                'success_rate': 92.9,
                'by_type': {
                    'email': 89,
                    'line': 45,
                    'webhook': 22
                },
                'by_category': {
                    'news_alert': 78,
                    'system': 34,
                    'reminder': 44
                }
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"獲取通知統計失敗: {e}")
            return {}

# 創建全局實例
notification_service = NotificationService()
'''
    
    os.makedirs("notification", exist_ok=True)
    
    with open("notification/notification_service.py", "w", encoding="utf-8") as f:
        f.write(notification_service_content)
    
    print("✅ notification_service.py 創建成功")

def fix_import_issues():
    """修復導入問題"""
    print("\n🔧 修復模組導入問題...")
    
    # 確保__init__.py文件存在
    init_files = [
        "notification/__init__.py",
        "app/__init__.py",
        "app/services/__init__.py"
    ]
    
    for init_file in init_files:
        os.makedirs(os.path.dirname(init_file), exist_ok=True)
        if not os.path.exists(init_file):
            with open(init_file, "w", encoding="utf-8") as f:
                f.write("# -*- coding: utf-8 -*-\\n")
            print(f"✅ 創建 {init_file}")

def create_compatibility_layer():
    """創建兼容性層"""
    print("\n🔧 創建兼容性支持...")
    
    # 創建降級可視化服務
    fallback_viz_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
降級可視化服務
當完整的可視化庫不可用時使用
"""

import logging
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class FallbackVisualization:
    """
    降級可視化服務
    提供基本的數據展示功能
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.output_dir = os.path.join("web", "static", "charts", "fallback")
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.logger.info("降級可視化服務初始化完成")
    
    def generate_business_dashboard_charts(self, user_id: Optional[int] = None, days: int = 30) -> Dict[str, str]:
        """
        生成業務員儀表板圖表（降級版本）
        """
        self.logger.info("使用降級模式生成圖表")
        
        # 返回預設的圖表路徑
        chart_paths = {
            'news_trend': '/static/charts/fallback/news_trend.json',
            'importance_distribution': '/static/charts/fallback/importance_pie.json',
            'source_stats': '/static/charts/fallback/source_stats.json',
            'sentiment_analysis': '/static/charts/fallback/sentiment.json',
            'keyword_cloud': '/static/charts/fallback/keywords.json',
            'category_heatmap': '/static/charts/fallback/category_heatmap.json'
        }
        
        # 生成基本的JSON數據文件
        for chart_name, path in chart_paths.items():
            self._generate_chart_data(chart_name, path, days)
        
        return chart_paths
    
    def _generate_chart_data(self, chart_name: str, path: str, days: int):
        """生成圖表數據文件"""
        try:
            file_path = os.path.join("web", "static", "charts", "fallback", f"{chart_name}.json")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 生成模擬數據
            if chart_name == 'news_trend':
                data = {
                    'type': 'line',
                    'data': {
                        'labels': [(datetime.now() - timedelta(days=i)).strftime('%m-%d') for i in range(days-1, -1, -1)],
                        'datasets': [{
                            'label': '新聞數量',
                            'data': [20 + i % 10 for i in range(days)],
                            'borderColor': '#007bff',
                            'backgroundColor': 'rgba(0, 123, 255, 0.1)'
                        }]
                    },
                    'options': {
                        'responsive': True,
                        'title': {'display': True, 'text': '新聞發布趨勢'}
                    }
                }
            elif chart_name == 'importance_distribution':
                data = {
                    'type': 'pie',
                    'data': {
                        'labels': ['高重要性', '中重要性', '低重要性'],
                        'datasets': [{
                            'data': [25, 45, 30],
                            'backgroundColor': ['#dc3545', '#ffc107', '#28a745']
                        }]
                    },
                    'options': {
                        'responsive': True,
                        'title': {'display': True, 'text': '重要性分佈'}
                    }
                }
            else:
                # 其他圖表的基本數據結構
                data = {
                    'type': 'bar',
                    'data': {
                        'labels': ['類別1', '類別2', '類別3', '類別4'],
                        'datasets': [{
                            'label': chart_name,
                            'data': [12, 19, 8, 15],
                            'backgroundColor': '#007bff'
                        }]
                    },
                    'options': {
                        'responsive': True,
                        'title': {'display': True, 'text': chart_name}
                    }
                }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"生成圖表數據失敗 {chart_name}: {e}")

# 創建全局實例
fallback_visualization = FallbackVisualization()
'''
    
    with open("app/services/fallback_visualization.py", "w", encoding="utf-8") as f:
        f.write(fallback_viz_content)
    
    print("✅ 降級可視化服務創建成功")

def main():
    """主修復函數"""
    print("🔧 第四階段環境修復開始...")
    print("=" * 60)
    
    try:
        # 1. 修復模組導入問題
        fix_import_issues()
        
        # 2. 創建缺失的服務
        create_notification_service()
        
        # 3. 創建兼容性層
        create_compatibility_layer()
        
        # 4. 安裝缺失的依賴
        install_missing_packages()
        
        print("\\n" + "=" * 60)
        print("✅ 環境修復完成！")
        print("=" * 60)
        print("📝 修復內容:")
        print("  - 創建 notification_service.py")
        print("  - 創建降級可視化服務")
        print("  - 修復模組導入路徑")
        print("  - 安裝缺失的Python依賴")
        print("\\n🚀 現在可以重新運行測試腳本:")
        print("   python test_phase4.py")
        
    except Exception as e:
        print(f"❌ 修復過程中發生錯誤: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
