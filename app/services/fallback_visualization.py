#!/usr/bin/env python3
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
