"""
系統效能壓力測試腳本
System Performance Load Test Script

模擬高負載情境測試系統效能
"""

import os
import sys
import logging
import time
import json
import sqlite3
import requests
import threading
import statistics
import argparse
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# 設置基本路徑
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 添加路徑到系統路徑
sys.path.insert(0, str(BASE_DIR))

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'logs', 'load_test.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('load.test')

class LoadTester:
    """效能壓力測試器"""
    
    def __init__(self, base_url=None, output_dir=None):
        """初始化測試器
        
        Args:
            base_url: 應用基礎URL
            output_dir: 測試結果輸出目錄
        """
        # 設置URL
        self.base_url = base_url or 'http://localhost:5000'
        
        # 設置輸出目錄
        if output_dir:
            self.output_dir = output_dir
        else:
            self.output_dir = os.path.join(BASE_DIR, 'tests', 'results')
        
        # 確保輸出目錄存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 用於存儲測試結果
        self.results = {}
        
        # 圖表輸出目錄
        self.charts_dir = os.path.join(self.output_dir, 'charts')
        os.makedirs(self.charts_dir, exist_ok=True)
        
        # 測試配置
        self.test_config = {
            'default_users': 10,
            'default_requests': 100,
            'default_timeout': 30,
            'admin_user': {'username': 'admin', 'password': 'admin123'},
            'test_user': {'username': 'testuser', 'password': 'testpass'}
        }
        
        # API令牌
        self.api_token = None
    
    def get_api_token(self):
        """獲取API令牌"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=self.test_config['admin_user'],
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('token')
                logger.info("成功獲取API令牌")
                return token
            else:
                logger.error(f"獲取API令牌失敗: {response.text}")
                return None
        except Exception as e:
            logger.error(f"獲取API令牌錯誤: {e}")
            return None
    
    def test_endpoint(self, url, method='GET', data=None, headers=None, auth=False, name=None):
        """測試單個端點
        
        Args:
            url: 端點URL
            method: HTTP方法
            data: 請求數據
            headers: 請求頭
            auth: 是否需要認證
            name: 測試名稱
            
        Returns:
            響應時間 (秒)
        """
        full_url = f"{self.base_url}{url}"
        
        # 準備請求頭
        headers = headers or {}
        if auth and self.api_token:
            headers['Authorization'] = f"Bearer {self.api_token}"
        
        try:
            start_time = time.time()
            
            if method.upper() == 'GET':
                response = requests.get(full_url, headers=headers, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(full_url, json=data, headers=headers, timeout=10)
            elif method.upper() == 'PUT':
                response = requests.put(full_url, json=data, headers=headers, timeout=10)
            elif method.upper() == 'DELETE':
                response = requests.delete(full_url, headers=headers, timeout=10)
            else:
                return None
            
            end_time = time.time()
            response_time = end_time - start_time
            
            status_code = response.status_code
            
            return {
                'response_time': response_time,
                'status_code': status_code,
                'success': 200 <= status_code < 300,
                'url': url,
                'method': method
            }
        
        except requests.exceptions.Timeout:
            return {
                'response_time': 10,  # 超時時間
                'status_code': 0,
                'success': False,
                'url': url,
                'method': method,
                'error': 'timeout'
            }
        except Exception as e:
            return {
                'response_time': None,
                'status_code': 0,
                'success': False,
                'url': url,
                'method': method,
                'error': str(e)
            }
    
    def run_load_test(self, endpoint_config, num_users=None, num_requests=None, ramp_up=0):
        """運行負載測試
        
        Args:
            endpoint_config: 端點配置
            num_users: 模擬用戶數
            num_requests: 每個用戶的請求數
            ramp_up: 用戶逐步增加時間 (秒)
            
        Returns:
            測試結果字典
        """
        num_users = num_users or self.test_config['default_users']
        num_requests = num_requests or self.test_config['default_requests']
        
        logger.info(f"開始負載測試: {endpoint_config['name']}")
        logger.info(f"用戶數: {num_users}, 每用戶請求數: {num_requests}, 總請求數: {num_users * num_requests}")
        
        # 準備測試數據
        all_results = []
        start_time = time.time()
        
        # 創建模擬用戶線程
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = []
            
            # 提交用戶任務
            for user_id in range(num_users):
                if ramp_up > 0:
                    # 根據ramp_up時間逐步啟動用戶
                    delay = ramp_up * (user_id / num_users)
                    time.sleep(delay)
                
                for req_id in range(num_requests):
                    future = executor.submit(
                        self.test_endpoint,
                        endpoint_config['url'],
                        endpoint_config.get('method', 'GET'),
                        endpoint_config.get('data'),
                        endpoint_config.get('headers'),
                        endpoint_config.get('auth', False),
                        endpoint_config['name']
                    )
                    futures.append(future)
            
            # 收集結果
            for future in as_completed(futures):
                result = future.result()
                if result:
                    all_results.append(result)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 分析結果
        response_times = [r['response_time'] for r in all_results if r['response_time'] is not None]
        success_count = sum(1 for r in all_results if r.get('success'))
        status_codes = {}
        
        for result in all_results:
            status_code = result.get('status_code', 0)
            status_codes[status_code] = status_codes.get(status_code, 0) + 1
        
        # 計算統計數據
        if response_times:
            avg_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
        else:
            avg_response_time = median_response_time = min_response_time = max_response_time = p95_response_time = 0
        
        # 計算每秒請求數
        requests_per_second = len(all_results) / total_time if total_time > 0 else 0
        
        # 計算成功率
        success_rate = success_count / len(all_results) * 100 if all_results else 0
        
        # 構建結果
        result = {
            'name': endpoint_config['name'],
            'url': endpoint_config['url'],
            'method': endpoint_config.get('method', 'GET'),
            'num_users': num_users,
            'num_requests': num_requests,
            'total_requests': len(all_results),
            'successful_requests': success_count,
            'success_rate': success_rate,
            'total_time': total_time,
            'requests_per_second': requests_per_second,
            'avg_response_time': avg_response_time,
            'median_response_time': median_response_time,
            'min_response_time': min_response_time,
            'max_response_time': max_response_time,
            'p95_response_time': p95_response_time,
            'status_codes': status_codes,
            'raw_results': all_results
        }
        
        # 保存結果
        self.results[endpoint_config['name']] = result
        
        # 輸出結果概要
        logger.info(f"測試完成: {endpoint_config['name']}")
        logger.info(f"總請求數: {len(all_results)}, 成功請求數: {success_count}, 成功率: {success_rate:.2f}%")
        logger.info(f"總時間: {total_time:.2f}秒, 每秒請求數: {requests_per_second:.2f}")
        logger.info(f"平均響應時間: {avg_response_time:.4f}秒, 中位數響應時間: {median_response_time:.4f}秒")
        logger.info(f"最小響應時間: {min_response_time:.4f}秒, 最大響應時間: {max_response_time:.4f}秒, P95響應時間: {p95_response_time:.4f}秒")
        
        return result
    
    def run_all_tests(self, num_users=None, num_requests=None):
        """運行所有測試
        
        Args:
            num_users: 模擬用戶數
            num_requests: 每個用戶的請求數
            
        Returns:
            測試結果字典
        """
        # 獲取API令牌
        self.api_token = self.get_api_token()
        
        # 定義測試端點
        endpoints = [
            {
                'name': '首頁',
                'url': '/',
                'method': 'GET',
                'auth': False
            },
            {
                'name': '新聞列表',
                'url': '/news',
                'method': 'GET',
                'auth': False
            },
            {
                'name': '最新新聞API',
                'url': '/api/news/latest',
                'method': 'GET',
                'auth': True
            },
            {
                'name': '重要新聞API',
                'url': '/api/news/important',
                'method': 'GET',
                'auth': True
            },
            {
                'name': '關鍵詞API',
                'url': '/api/analyzer/keywords',
                'method': 'GET',
                'auth': True
            },
            {
                'name': '狀態API',
                'url': '/api/status',
                'method': 'GET',
                'auth': False
            }
        ]
        
        # 運行所有測試
        results = {}
        
        for endpoint in endpoints:
            result = self.run_load_test(endpoint, num_users, num_requests)
            results[endpoint['name']] = result
        
        # 生成測試報告
        self.generate_report()
        
        return results
    
    def generate_report(self):
        """生成測試報告"""
        if not self.results:
            logger.error("沒有測試結果可生成報告")
            return
        
        try:
            # 生成圖表
            self.generate_charts()
            
            # 準備報告數據
            report = {
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_endpoints': len(self.results),
                    'endpoints': list(self.results.keys())
                },
                'results': self.results
            }
            
            # 計算總體性能指標
            avg_response_times = [r['avg_response_time'] for r in self.results.values()]
            success_rates = [r['success_rate'] for r in self.results.values()]
            requests_per_second = [r['requests_per_second'] for r in self.results.values()]
            
            report['summary']['avg_response_time'] = statistics.mean(avg_response_times)
            report['summary']['avg_success_rate'] = statistics.mean(success_rates)
            report['summary']['avg_requests_per_second'] = statistics.mean(requests_per_second)
            
            # 保存報告
            report_path = os.path.join(self.output_dir, f'load_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"測試報告已保存至: {report_path}")
            
            return report
        
        except Exception as e:
            logger.error(f"生成測試報告失敗: {e}")
            return None
    
    def generate_charts(self):
        """生成測試圖表"""
        try:
            # 設置圖表風格
            plt.style.use('seaborn-v0_8')
            
            # 響應時間對比圖
            self.generate_response_time_chart()
            
            # 請求成功率圖
            self.generate_success_rate_chart()
            
            # 每秒請求數圖
            self.generate_requests_per_second_chart()
            
            logger.info(f"已生成測試圖表，保存在: {self.charts_dir}")
        
        except Exception as e:
            logger.error(f"生成圖表失敗: {e}")
    
    def generate_response_time_chart(self):
        """生成響應時間對比圖"""
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            endpoints = list(self.results.keys())
            avg_times = [r['avg_response_time'] * 1000 for r in self.results.values()]  # 轉換為毫秒
            p95_times = [r['p95_response_time'] * 1000 for r in self.results.values()]  # 轉換為毫秒
            
            x = np.arange(len(endpoints))
            width = 0.35
            
            ax.bar(x - width/2, avg_times, width, label='平均響應時間', color='#3498db')
            ax.bar(x + width/2, p95_times, width, label='P95響應時間', color='#e74c3c')
            
            ax.set_xlabel('端點')
            ax.set_ylabel('響應時間 (毫秒)')
            ax.set_title('不同端點的響應時間對比')
            ax.set_xticks(x)
            ax.set_xticklabels(endpoints, rotation=45, ha='right')
            ax.legend()
            
            plt.tight_layout()
            plt.grid(axis='y', alpha=0.3)
            
            # 保存圖表
            chart_path = os.path.join(self.charts_dir, 'response_time_comparison.png')
            plt.savefig(chart_path, dpi=100)
            plt.close(fig)
        
        except Exception as e:
            logger.error(f"生成響應時間圖表失敗: {e}")
    
    def generate_success_rate_chart(self):
        """生成請求成功率圖"""
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            endpoints = list(self.results.keys())
            success_rates = [r['success_rate'] for r in self.results.values()]
            
            # 顏色基於成功率
            colors = ['#27ae60' if rate > 95 else '#f39c12' if rate > 80 else '#e74c3c' for rate in success_rates]
            
            ax.bar(endpoints, success_rates, color=colors)
            
            ax.set_xlabel('端點')
            ax.set_ylabel('成功率 (%)')
            ax.set_title('不同端點的請求成功率')
            ax.set_ylim(0, 100)
            
            # 在每個柱子上添加標籤
            for i, v in enumerate(success_rates):
                ax.text(i, v + 1, f'{v:.1f}%', ha='center', va='bottom')
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.grid(axis='y', alpha=0.3)
            
            # 保存圖表
            chart_path = os.path.join(self.charts_dir, 'success_rate.png')
            plt.savefig(chart_path, dpi=100)
            plt.close(fig)
        
        except Exception as e:
            logger.error(f"生成成功率圖表失敗: {e}")
    
    def generate_requests_per_second_chart(self):
        """生成每秒請求數圖"""
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            endpoints = list(self.results.keys())
            rps_values = [r['requests_per_second'] for r in self.results.values()]
            
            ax.bar(endpoints, rps_values, color='#9b59b6')
            
            ax.set_xlabel('端點')
            ax.set_ylabel('每秒請求數')
            ax.set_title('不同端點的每秒處理請求數')
            
            # 在每個柱子上添加標籤
            for i, v in enumerate(rps_values):
                ax.text(i, v + 0.1, f'{v:.1f}', ha='center', va='bottom')
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.grid(axis='y', alpha=0.3)
            
            # 保存圖表
            chart_path = os.path.join(self.charts_dir, 'requests_per_second.png')
            plt.savefig(chart_path, dpi=100)
            plt.close(fig)
        
        except Exception as e:
            logger.error(f"生成每秒請求數圖表失敗: {e}")

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='保險新聞聚合器效能壓力測試')
    parser.add_argument('--url', default='http://localhost:5000', help='應用基礎URL')
    parser.add_argument('--users', type=int, default=10, help='模擬用戶數')
    parser.add_argument('--requests', type=int, default=20, help='每個用戶的請求數')
    parser.add_argument('--output', default=None, help='輸出目錄')
    
    args = parser.parse_args()
    
    logger.info("開始執行效能壓力測試")
    logger.info(f"目標URL: {args.url}")
    logger.info(f"模擬用戶數: {args.users}")
    logger.info(f"每用戶請求數: {args.requests}")
    
    # 創建測試器
    tester = LoadTester(args.url, args.output)
    
    # 運行測試
    results = tester.run_all_tests(args.users, args.requests)
    
    logger.info("測試完成")
    return {
        'status': 'success',
        'test_results': {k: {key: v[key] for key in ['success_rate', 'requests_per_second', 'avg_response_time']} 
                         for k, v in results.items()}
    }

if __name__ == "__main__":
    import matplotlib
    matplotlib.use('Agg')  # 設置後端為Agg
    main()
