"""
工作流管理器
Workflow Manager

提供工作流的高級管理功能，包括預設工作流模板和排程管理
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import time
from croniter import croniter
from .workflow_service import WorkflowService, workflow_service

logger = logging.getLogger(__name__)

class WorkflowManager:
    """工作流管理器類"""
    
    def __init__(self, workflow_service: WorkflowService = None):
        """
        初始化工作流管理器
        
        Args:
            workflow_service: 工作流服務實例
        """
        self.workflow_service = workflow_service or workflow_service
        self.scheduled_workflows: Dict[str, Dict] = {}
        self.scheduler_running = False
        self.scheduler_thread = None
        
        # 初始化預設工作流
        self._create_default_workflows()
    
    def _create_default_workflows(self):
        """創建預設工作流模板"""
        
        # 1. 每日新聞收集工作流
        daily_news_workflow_id = self.workflow_service.create_workflow(
            "每日新聞收集",
            "每日自動收集和分析保險新聞"
        )
        
        # 添加任務
        scrape_task_id = self.workflow_service.add_task_to_workflow(
            daily_news_workflow_id,
            "爬取新聞",
            "scrape_news",
            {"sources": "all", "max_articles": 100},
            description="從所有新聞來源爬取最新文章"
        )
        
        analyze_task_id = self.workflow_service.add_task_to_workflow(
            daily_news_workflow_id,
            "分析新聞",
            "analyze_news",
            {"sentiment": True, "keywords": True},
            depends_on=[scrape_task_id],
            description="分析新聞內容和情感"
        )
        
        self.workflow_service.add_task_to_workflow(
            daily_news_workflow_id,
            "發送日報",
            "send_notification",
            {"message": "每日新聞收集和分析完成", "type": "email"},
            depends_on=[analyze_task_id],
            description="發送每日新聞摘要"
        )
        
        # 設定排程（每天早上8點）
        self.schedule_workflow(daily_news_workflow_id, "0 8 * * *")
        
        # 2. 週報生成工作流
        weekly_report_workflow_id = self.workflow_service.create_workflow(
            "週報生成",
            "每週生成保險新聞分析報告"
        )
        
        report_task_id = self.workflow_service.add_task_to_workflow(
            weekly_report_workflow_id,
            "生成週報",
            "generate_report",
            {"report_type": "weekly", "format": "pdf"},
            description="生成週度分析報告"
        )
        
        self.workflow_service.add_task_to_workflow(
            weekly_report_workflow_id,
            "發送週報",
            "send_notification",
            {"message": "週報已生成", "type": "email"},
            depends_on=[report_task_id],
            description="發送週報通知"
        )
        
        # 設定排程（每週一早上9點）
        self.schedule_workflow(weekly_report_workflow_id, "0 9 * * 1")
        
        # 3. 系統維護工作流
        maintenance_workflow_id = self.workflow_service.create_workflow(
            "系統維護",
            "定期系統清理和維護"
        )
        
        self.workflow_service.add_task_to_workflow(
            maintenance_workflow_id,
            "清理日誌",
            "cleanup_logs",
            {"days": 30},
            description="清理30天前的日誌檔案"
        )
        
        # 設定排程（每天凌晨2點）
        self.schedule_workflow(maintenance_workflow_id, "0 2 * * *")
        
        logger.info("Default workflows created successfully")
    
    def schedule_workflow(self, workflow_id: str, cron_expression: str):
        """
        排程工作流
        
        Args:
            workflow_id: 工作流ID
            cron_expression: Cron 表達式
        """
        if workflow_id not in self.workflow_service.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        # 驗證 cron 表達式
        try:
            cron = croniter(cron_expression, datetime.utcnow())
            next_run = cron.get_next(datetime)
        except Exception as e:
            raise ValueError(f"Invalid cron expression: {str(e)}")
        
        self.scheduled_workflows[workflow_id] = {
            'cron_expression': cron_expression,
            'next_run': next_run,
            'enabled': True
        }
        
        # 更新工作流對象
        workflow = self.workflow_service.workflows[workflow_id]
        workflow.schedule = cron_expression
        workflow.next_run = next_run
        
        logger.info(f"Workflow {workflow_id} scheduled with expression: {cron_expression}")
    
    def unschedule_workflow(self, workflow_id: str):
        """
        取消工作流排程
        
        Args:
            workflow_id: 工作流ID
        """
        if workflow_id in self.scheduled_workflows:
            del self.scheduled_workflows[workflow_id]
            
            # 更新工作流對象
            if workflow_id in self.workflow_service.workflows:
                workflow = self.workflow_service.workflows[workflow_id]
                workflow.schedule = None
                workflow.next_run = None
            
            logger.info(f"Workflow {workflow_id} unscheduled")
    
    def start_scheduler(self):
        """啟動排程器"""
        if not self.scheduler_running:
            self.scheduler_running = True
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()
            logger.info("Workflow scheduler started")
    
    def stop_scheduler(self):
        """停止排程器"""
        self.scheduler_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        logger.info("Workflow scheduler stopped")
    
    def _scheduler_loop(self):
        """排程器主循環"""
        while self.scheduler_running:
            try:
                current_time = datetime.utcnow()
                
                for workflow_id, schedule_info in self.scheduled_workflows.items():
                    if not schedule_info['enabled']:
                        continue
                    
                    next_run = schedule_info['next_run']
                    
                    # 檢查是否到了執行時間
                    if current_time >= next_run:
                        logger.info(f"Triggering scheduled workflow: {workflow_id}")
                        
                        # 執行工作流
                        success = self.workflow_service.start_workflow(workflow_id)
                        
                        if success:
                            # 計算下次執行時間
                            cron = croniter(schedule_info['cron_expression'], current_time)
                            next_run = cron.get_next(datetime)
                            schedule_info['next_run'] = next_run
                            
                            # 更新工作流對象
                            if workflow_id in self.workflow_service.workflows:
                                self.workflow_service.workflows[workflow_id].next_run = next_run
                        
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
            
            # 每分鐘檢查一次
            time.sleep(60)
    
    def enable_workflow_schedule(self, workflow_id: str):
        """
        啟用工作流排程
        
        Args:
            workflow_id: 工作流ID
        """
        if workflow_id in self.scheduled_workflows:
            self.scheduled_workflows[workflow_id]['enabled'] = True
            logger.info(f"Workflow {workflow_id} schedule enabled")
    
    def disable_workflow_schedule(self, workflow_id: str):
        """
        停用工作流排程
        
        Args:
            workflow_id: 工作流ID
        """
        if workflow_id in self.scheduled_workflows:
            self.scheduled_workflows[workflow_id]['enabled'] = False
            logger.info(f"Workflow {workflow_id} schedule disabled")
    
    def get_scheduled_workflows(self) -> List[Dict]:
        """
        獲取排程工作流列表
        
        Returns:
            排程工作流資訊列表
        """
        result = []
        
        for workflow_id, schedule_info in self.scheduled_workflows.items():
            workflow = self.workflow_service.workflows.get(workflow_id)
            if workflow:
                result.append({
                    'workflow_id': workflow_id,
                    'workflow_name': workflow.name,
                    'cron_expression': schedule_info['cron_expression'],
                    'next_run': schedule_info['next_run'].isoformat(),
                    'enabled': schedule_info['enabled'],
                    'last_run': workflow.last_run.isoformat() if workflow.last_run else None
                })
        
        return result
    
    def trigger_workflow_now(self, workflow_id: str) -> bool:
        """
        立即觸發工作流執行
        
        Args:
            workflow_id: 工作流ID
            
        Returns:
            觸發是否成功
        """
        return self.workflow_service.start_workflow(workflow_id)
    
    def create_custom_workflow(self, 
                             name: str,
                             description: str,
                             tasks: List[Dict],
                             schedule: Optional[str] = None) -> str:
        """
        創建自訂工作流
        
        Args:
            name: 工作流名稱
            description: 工作流描述
            tasks: 任務列表
            schedule: 排程表達式（可選）
            
        Returns:
            工作流ID
        """
        workflow_id = self.workflow_service.create_workflow(name, description)
        
        task_id_map = {}
        
        # 添加任務
        for task_config in tasks:
            task_name = task_config['name']
            function_name = task_config['function']
            parameters = task_config.get('parameters', {})
            depends_on_names = task_config.get('depends_on', [])
            task_description = task_config.get('description', '')
            
            # 轉換依賴任務名稱為ID
            depends_on_ids = [task_id_map.get(dep_name) for dep_name in depends_on_names]
            depends_on_ids = [tid for tid in depends_on_ids if tid is not None]
            
            task_id = self.workflow_service.add_task_to_workflow(
                workflow_id,
                task_name,
                function_name,
                parameters,
                depends_on_ids,
                task_description
            )
            
            task_id_map[task_name] = task_id
        
        # 設定排程
        if schedule:
            self.schedule_workflow(workflow_id, schedule)
        
        logger.info(f"Custom workflow '{name}' created with ID: {workflow_id}")
        return workflow_id
    
    def get_workflow_templates(self) -> List[Dict]:
        """
        獲取工作流模板
        
        Returns:
            工作流模板列表
        """
        return [
            {
                'name': '每日新聞收集',
                'description': '自動收集和分析保險新聞',
                'tasks': [
                    {'name': '爬取新聞', 'function': 'scrape_news'},
                    {'name': '分析新聞', 'function': 'analyze_news', 'depends_on': ['爬取新聞']},
                    {'name': '發送通知', 'function': 'send_notification', 'depends_on': ['分析新聞']}
                ],
                'schedule': '0 8 * * *'
            },
            {
                'name': '週報生成',
                'description': '生成週度分析報告',
                'tasks': [
                    {'name': '生成報告', 'function': 'generate_report'},
                    {'name': '發送報告', 'function': 'send_notification', 'depends_on': ['生成報告']}
                ],
                'schedule': '0 9 * * 1'
            },
            {
                'name': '系統維護',
                'description': '定期系統清理',
                'tasks': [
                    {'name': '清理日誌', 'function': 'cleanup_logs'}
                ],
                'schedule': '0 2 * * *'
            }
        ]

# 全域工作流管理器實例
workflow_manager = WorkflowManager()
