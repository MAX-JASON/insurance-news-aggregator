"""
工作流服務模組
Workflow Service Module

負責管理和執行各種工作流程
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import threading
import time

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """任務狀態枚舉"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkflowStatus(Enum):
    """工作流狀態枚舉"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Task:
    """任務數據類"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    function: Optional[Callable] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: int = 300  # 5分鐘
    depends_on: List[str] = field(default_factory=list)

@dataclass
class Workflow:
    """工作流數據類"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    tasks: List[Task] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    schedule: Optional[str] = None  # Cron 格式
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class WorkflowService:
    """工作流服務類"""
    
    def __init__(self):
        """初始化工作流服務"""
        self.workflows: Dict[str, Workflow] = {}
        self.running_tasks: Dict[str, threading.Thread] = {}
        self.task_registry: Dict[str, Callable] = {}
        self.scheduler_running = False
        self.scheduler_thread = None
        
        # 註冊預設任務
        self._register_default_tasks()
    
    def _register_default_tasks(self):
        """註冊預設任務"""
        self.register_task("scrape_news", self._scrape_news_task)
        self.register_task("analyze_news", self._analyze_news_task)
        self.register_task("send_notification", self._send_notification_task)
        self.register_task("cleanup_logs", self._cleanup_logs_task)
        self.register_task("generate_report", self._generate_report_task)
    
    def register_task(self, name: str, function: Callable):
        """
        註冊任務函數
        
        Args:
            name: 任務名稱
            function: 任務函數
        """
        self.task_registry[name] = function
        logger.info(f"Task '{name}' registered")
    
    def create_workflow(self, name: str, description: str = "") -> str:
        """
        創建新工作流
        
        Args:
            name: 工作流名稱
            description: 工作流描述
            
        Returns:
            工作流ID
        """
        workflow = Workflow(name=name, description=description)
        self.workflows[workflow.id] = workflow
        logger.info(f"Workflow '{name}' created with ID: {workflow.id}")
        return workflow.id
    
    def add_task_to_workflow(self, 
                           workflow_id: str, 
                           task_name: str,
                           function_name: str,
                           parameters: Dict[str, Any] = None,
                           depends_on: List[str] = None,
                           description: str = "") -> str:
        """
        添加任務到工作流
        
        Args:
            workflow_id: 工作流ID
            task_name: 任務名稱
            function_name: 函數名稱
            parameters: 任務參數
            depends_on: 依賴的任務ID列表
            description: 任務描述
            
        Returns:
            任務ID
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        if function_name not in self.task_registry:
            raise ValueError(f"Task function '{function_name}' not registered")
        
        task = Task(
            name=task_name,
            description=description,
            function=self.task_registry[function_name],
            parameters=parameters or {},
            depends_on=depends_on or []
        )
        
        self.workflows[workflow_id].tasks.append(task)
        logger.info(f"Task '{task_name}' added to workflow {workflow_id}")
        return task.id
    
    def start_workflow(self, workflow_id: str) -> bool:
        """
        啟動工作流
        
        Args:
            workflow_id: 工作流ID
            
        Returns:
            啟動是否成功
        """
        if workflow_id not in self.workflows:
            logger.error(f"Workflow {workflow_id} not found")
            return False
        
        workflow = self.workflows[workflow_id]
        
        if workflow.status == WorkflowStatus.RUNNING:
            logger.warning(f"Workflow {workflow_id} is already running")
            return False
        
        workflow.status = WorkflowStatus.ACTIVE
        workflow.started_at = datetime.utcnow()
        
        # 在新線程中執行工作流
        thread = threading.Thread(target=self._execute_workflow, args=(workflow_id,))
        thread.daemon = True
        thread.start()
        
        logger.info(f"Workflow {workflow_id} started")
        return True
    
    def _execute_workflow(self, workflow_id: str):
        """
        執行工作流
        
        Args:
            workflow_id: 工作流ID
        """
        workflow = self.workflows[workflow_id]
        
        try:
            # 獲取任務執行順序
            execution_order = self._get_task_execution_order(workflow.tasks)
            
            for task in execution_order:
                if workflow.status != WorkflowStatus.ACTIVE:
                    break
                
                # 執行任務
                self._execute_task(task)
                
                # 檢查任務是否失敗
                if task.status == TaskStatus.FAILED:
                    logger.error(f"Task {task.name} failed, stopping workflow")
                    workflow.status = WorkflowStatus.FAILED
                    break
            
            # 檢查所有任務是否完成
            if all(task.status == TaskStatus.COMPLETED for task in workflow.tasks):
                workflow.status = WorkflowStatus.COMPLETED
                workflow.completed_at = datetime.utcnow()
                logger.info(f"Workflow {workflow_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Error executing workflow {workflow_id}: {str(e)}")
            workflow.status = WorkflowStatus.FAILED
        
        finally:
            workflow.last_run = datetime.utcnow()
    
    def _get_task_execution_order(self, tasks: List[Task]) -> List[Task]:
        """
        獲取任務執行順序（拓撲排序）
        
        Args:
            tasks: 任務列表
            
        Returns:
            排序後的任務列表
        """
        # 簡化版本：按依賴關係排序
        task_dict = {task.id: task for task in tasks}
        visited = set()
        result = []
        
        def visit(task_id: str):
            if task_id in visited:
                return
            
            task = task_dict.get(task_id)
            if not task:
                return
            
            # 先訪問依賴
            for dep_id in task.depends_on:
                visit(dep_id)
            
            visited.add(task_id)
            result.append(task)
        
        # 訪問所有任務
        for task in tasks:
            visit(task.id)
        
        return result
    
    def _execute_task(self, task: Task):
        """
        執行單個任務
        
        Args:
            task: 任務對象
        """
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        
        try:
            logger.info(f"Executing task: {task.name}")
            
            # 執行任務函數
            if task.function:
                result = task.function(**task.parameters)
                task.result = result
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            logger.info(f"Task {task.name} completed successfully")
            
        except Exception as e:
            logger.error(f"Task {task.name} failed: {str(e)}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            
            # 重試邏輯
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                logger.info(f"Retrying task {task.name} (attempt {task.retry_count + 1})")
                time.sleep(2)  # 等待2秒後重試
                self._execute_task(task)
    
    def pause_workflow(self, workflow_id: str) -> bool:
        """
        暫停工作流
        
        Args:
            workflow_id: 工作流ID
            
        Returns:
            暫停是否成功
        """
        if workflow_id not in self.workflows:
            return False
        
        workflow = self.workflows[workflow_id]
        if workflow.status == WorkflowStatus.ACTIVE:
            workflow.status = WorkflowStatus.PAUSED
            logger.info(f"Workflow {workflow_id} paused")
            return True
        
        return False
    
    def resume_workflow(self, workflow_id: str) -> bool:
        """
        恢復工作流
        
        Args:
            workflow_id: 工作流ID
            
        Returns:
            恢復是否成功
        """
        if workflow_id not in self.workflows:
            return False
        
        workflow = self.workflows[workflow_id]
        if workflow.status == WorkflowStatus.PAUSED:
            workflow.status = WorkflowStatus.ACTIVE
            logger.info(f"Workflow {workflow_id} resumed")
            return True
        
        return False
    
    def get_workflow_status(self, workflow_id: str) -> Dict:
        """
        獲取工作流狀態
        
        Args:
            workflow_id: 工作流ID
            
        Returns:
            工作流狀態字典
        """
        if workflow_id not in self.workflows:
            return {}
        
        workflow = self.workflows[workflow_id]
        
        return {
            'id': workflow.id,
            'name': workflow.name,
            'status': workflow.status.value,
            'created_at': workflow.created_at.isoformat(),
            'started_at': workflow.started_at.isoformat() if workflow.started_at else None,
            'completed_at': workflow.completed_at.isoformat() if workflow.completed_at else None,
            'last_run': workflow.last_run.isoformat() if workflow.last_run else None,
            'tasks': [
                {
                    'id': task.id,
                    'name': task.name,
                    'status': task.status.value,
                    'started_at': task.started_at.isoformat() if task.started_at else None,
                    'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                    'error_message': task.error_message
                }
                for task in workflow.tasks
            ]
        }
    
    def list_workflows(self) -> List[Dict]:
        """
        列出所有工作流
        
        Returns:
            工作流列表
        """
        return [
            {
                'id': workflow.id,
                'name': workflow.name,
                'description': workflow.description,
                'status': workflow.status.value,
                'task_count': len(workflow.tasks),
                'created_at': workflow.created_at.isoformat(),
                'last_run': workflow.last_run.isoformat() if workflow.last_run else None
            }
            for workflow in self.workflows.values()
        ]
    
    # 預設任務函數
    def _scrape_news_task(self, **kwargs):
        """爬取新聞任務"""
        logger.info("Executing news scraping task")
        # 這裡應該調用實際的爬蟲服務
        time.sleep(2)  # 模擬執行時間
        return {"status": "success", "articles_count": 10}
    
    def _analyze_news_task(self, **kwargs):
        """分析新聞任務"""
        logger.info("Executing news analysis task")
        # 這裡應該調用實際的分析服務
        time.sleep(1)
        return {"status": "success", "analyzed_count": 10}
    
    def _send_notification_task(self, message: str = "", **kwargs):
        """發送通知任務"""
        logger.info(f"Sending notification: {message}")
        # 這裡應該調用實際的通知服務
        return {"status": "success", "message": message}
    
    def _cleanup_logs_task(self, days: int = 7, **kwargs):
        """清理日誌任務"""
        logger.info(f"Cleaning up logs older than {days} days")
        # 這裡應該實現實際的日誌清理邏輯
        return {"status": "success", "cleaned_files": 5}
    
    def _generate_report_task(self, report_type: str = "daily", **kwargs):
        """生成報告任務"""
        logger.info(f"Generating {report_type} report")
        # 這裡應該調用實際的報告生成邏輯
        return {"status": "success", "report_path": f"/reports/{report_type}_report.pdf"}

# 全域工作流服務實例
workflow_service = WorkflowService()
