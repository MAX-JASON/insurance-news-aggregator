"""
通知服務模組
Notification Service Module

負責發送各種類型的通知（郵件、簡訊、即時通訊等）
"""

import smtplib
import logging
try:
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    from email.mime.base import MimeBase
    from email import encoders
except ImportError:
    # Fallback for older Python versions
    from email.MIMEText import MIMEText as MimeText
    from email.MIMEMultipart import MIMEMultipart as MimeMultipart
    from email.MIMEBase import MIMEBase as MimeBase
    import email.Encoders as encoders
from datetime import datetime
from typing import List, Dict, Optional, Union
import json
import requests
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class NotificationConfig:
    """通知配置數據類"""
    email_enabled: bool = True
    email_smtp_server: str = "smtp.gmail.com"
    email_smtp_port: int = 587
    email_username: str = ""
    email_password: str = ""
    email_from: str = ""
    
    webhook_enabled: bool = False
    webhook_url: str = ""
    
    line_enabled: bool = False
    line_token: str = ""

class NotificationService:
    """通知服務類"""
    
    def __init__(self, config: Optional[NotificationConfig] = None):
        """
        初始化通知服務
        
        Args:
            config: 通知配置對象
        """
        self.config = config or NotificationConfig()
        self.notification_history = []
        self.max_history_size = 1000
        
    def send_email(self, 
                   to_addresses: Union[str, List[str]], 
                   subject: str, 
                   body: str, 
                   html_body: Optional[str] = None,
                   attachments: Optional[List[str]] = None) -> bool:
        """
        發送電子郵件
        
        Args:
            to_addresses: 收件人地址
            subject: 郵件主題
            body: 郵件內容（純文字）
            html_body: HTML 格式郵件內容
            attachments: 附件檔案路徑列表
            
        Returns:
            發送是否成功
        """
        if not self.config.email_enabled:
            logger.warning("Email notification is disabled")
            return False
        
        if not self.config.email_username or not self.config.email_password:
            logger.error("Email credentials not configured")
            return False
        
        try:
            # 確保 to_addresses 是列表
            if isinstance(to_addresses, str):
                to_addresses = [to_addresses]
            
            # 創建郵件
            msg = MimeMultipart('alternative')
            msg['From'] = self.config.email_from or self.config.email_username
            msg['To'] = ', '.join(to_addresses)
            msg['Subject'] = subject
            
            # 添加純文字內容
            text_part = MimeText(body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # 添加 HTML 內容（如果提供）
            if html_body:
                html_part = MimeText(html_body, 'html', 'utf-8')
                msg.attach(html_part)
            
            # 添加附件（如果提供）
            if attachments:
                for file_path in attachments:
                    try:
                        with open(file_path, 'rb') as attachment:
                            part = MimeBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {file_path.split("/")[-1]}'
                            )
                            msg.attach(part)
                    except Exception as e:
                        logger.warning(f"Failed to attach file {file_path}: {str(e)}")
            
            # 發送郵件
            with smtplib.SMTP(self.config.email_smtp_server, self.config.email_smtp_port) as server:
                server.starttls()
                server.login(self.config.email_username, self.config.email_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {', '.join(to_addresses)}")
            self._log_notification('email', to_addresses, subject, True)
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            self._log_notification('email', to_addresses, subject, False, str(e))
            return False
    
    def send_webhook_notification(self, data: Dict, url: Optional[str] = None) -> bool:
        """
        發送 Webhook 通知
        
        Args:
            data: 要發送的數據
            url: Webhook URL（可選，使用配置中的URL）
            
        Returns:
            發送是否成功
        """
        if not self.config.webhook_enabled:
            logger.warning("Webhook notification is disabled")
            return False
        
        webhook_url = url or self.config.webhook_url
        if not webhook_url:
            logger.error("Webhook URL not configured")
            return False
        
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(webhook_url, json=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.info("Webhook notification sent successfully")
                self._log_notification('webhook', [webhook_url], str(data), True)
                return True
            else:
                logger.error(f"Webhook failed with status {response.status_code}")
                self._log_notification('webhook', [webhook_url], str(data), False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {str(e)}")
            self._log_notification('webhook', [webhook_url], str(data), False, str(e))
            return False
    
    def send_line_notification(self, message: str, token: Optional[str] = None) -> bool:
        """
        發送 LINE Notify 通知
        
        Args:
            message: 通知訊息
            token: LINE Notify Token（可選，使用配置中的token）
            
        Returns:
            發送是否成功
        """
        if not self.config.line_enabled:
            logger.warning("LINE notification is disabled")
            return False
        
        line_token = token or self.config.line_token
        if not line_token:
            logger.error("LINE token not configured")
            return False
        
        try:
            url = "https://notify-api.line.me/api/notify"
            headers = {"Authorization": f"Bearer {line_token}"}
            data = {"message": message}
            
            response = requests.post(url, headers=headers, data=data, timeout=10)
            
            if response.status_code == 200:
                logger.info("LINE notification sent successfully")
                self._log_notification('line', ['LINE'], message, True)
                return True
            else:
                logger.error(f"LINE notification failed with status {response.status_code}")
                self._log_notification('line', ['LINE'], message, False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send LINE notification: {str(e)}")
            self._log_notification('line', ['LINE'], message, False, str(e))
            return False
    
    def send_alert_notification(self, alert: Dict) -> bool:
        """
        發送警報通知
        
        Args:
            alert: 警報字典
            
        Returns:
            發送是否成功
        """
        alert_type = alert.get('type', 'UNKNOWN')
        level = alert.get('level', 'INFO')
        message = alert.get('message', 'No message')
        timestamp = alert.get('timestamp', datetime.utcnow())
        
        # 格式化通知內容
        subject = f"[{level}] {alert_type} Alert"
        body = f"""
警報通知 / Alert Notification

類型: {alert_type}
等級: {level}
訊息: {message}
時間: {timestamp}

請檢查系統狀態並採取必要行動。
Please check system status and take necessary actions.
        """.strip()
        
        html_body = f"""
        <html>
        <body>
            <h2 style="color: {'red' if level == 'CRITICAL' else 'orange' if level == 'WARNING' else 'blue'};">
                警報通知 / Alert Notification
            </h2>
            <table border="1" style="border-collapse: collapse;">
                <tr><td><strong>類型</strong></td><td>{alert_type}</td></tr>
                <tr><td><strong>等級</strong></td><td>{level}</td></tr>
                <tr><td><strong>訊息</strong></td><td>{message}</td></tr>
                <tr><td><strong>時間</strong></td><td>{timestamp}</td></tr>
            </table>
            <p>請檢查系統狀態並採取必要行動。</p>
        </body>
        </html>
        """
        
        success = True
        
        # 發送郵件通知
        if self.config.email_enabled and self.config.email_username:
            admin_email = self.config.email_from or "admin@example.com"
            success &= self.send_email([admin_email], subject, body, html_body)
        
        # 發送 LINE 通知
        if self.config.line_enabled:
            line_message = f"🚨 {subject}\n{message}\n時間: {timestamp}"
            success &= self.send_line_notification(line_message)
        
        # 發送 Webhook 通知
        if self.config.webhook_enabled:
            webhook_data = {
                "type": "alert",
                "alert": alert,
                "timestamp": timestamp.isoformat() if hasattr(timestamp, 'isoformat') else str(timestamp)
            }
            success &= self.send_webhook_notification(webhook_data)
        
        return success
    
    def send_system_report(self, report: Dict, recipients: List[str]) -> bool:
        """
        發送系統報告
        
        Args:
            report: 報告數據字典
            recipients: 收件人列表
            
        Returns:
            發送是否成功
        """
        subject = f"系統狀態報告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # 格式化報告內容
        body = self._format_report_text(report)
        html_body = self._format_report_html(report)
        
        return self.send_email(recipients, subject, body, html_body)
    
    def _format_report_text(self, report: Dict) -> str:
        """格式化純文字報告"""
        return f"""
系統狀態報告
=============

時間: {report.get('timestamp', 'N/A')}

系統指標:
- CPU 使用率: {report.get('system', {}).get('cpu_percent', 'N/A')}%
- 記憶體使用率: {report.get('system', {}).get('memory_percent', 'N/A')}%
- 磁碟使用率: {report.get('system', {}).get('disk_usage', 'N/A')}%

應用指標:
- 總請求數: {report.get('application', {}).get('total_requests', 'N/A')}
- 錯誤數: {report.get('application', {}).get('error_count', 'N/A')}
- 平均響應時間: {report.get('application', {}).get('response_time_avg', 'N/A')}ms

健康狀態: {report.get('health_status', 'N/A')}
警報數量: {report.get('alerts', 'N/A')}
        """.strip()
    
    def _format_report_html(self, report: Dict) -> str:
        """格式化 HTML 報告"""
        return f"""
        <html>
        <body>
            <h2>系統狀態報告</h2>
            <p><strong>時間:</strong> {report.get('timestamp', 'N/A')}</p>
            
            <h3>系統指標</h3>
            <ul>
                <li>CPU 使用率: {report.get('system', {}).get('cpu_percent', 'N/A')}%</li>
                <li>記憶體使用率: {report.get('system', {}).get('memory_percent', 'N/A')}%</li>
                <li>磁碟使用率: {report.get('system', {}).get('disk_usage', 'N/A')}%</li>
            </ul>
            
            <h3>應用指標</h3>
            <ul>
                <li>總請求數: {report.get('application', {}).get('total_requests', 'N/A')}</li>
                <li>錯誤數: {report.get('application', {}).get('error_count', 'N/A')}</li>
                <li>平均響應時間: {report.get('application', {}).get('response_time_avg', 'N/A')}ms</li>
            </ul>
            
            <p><strong>健康狀態:</strong> {report.get('health_status', 'N/A')}</p>
            <p><strong>警報數量:</strong> {report.get('alerts', 'N/A')}</p>
        </body>
        </html>
        """
    
    def _log_notification(self, 
                         notification_type: str, 
                         recipients: List[str], 
                         subject: str, 
                         success: bool, 
                         error_message: Optional[str] = None):
        """
        記錄通知日誌
        
        Args:
            notification_type: 通知類型
            recipients: 收件人列表
            subject: 主題
            success: 是否成功
            error_message: 錯誤訊息
        """
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': notification_type,
            'recipients': recipients,
            'subject': subject,
            'success': success,
            'error_message': error_message
        }
        
        self.notification_history.append(log_entry)
        
        # 限制歷史大小
        if len(self.notification_history) > self.max_history_size:
            self.notification_history.pop(0)
    
    def get_notification_history(self, limit: int = 50) -> List[Dict]:
        """
        獲取通知歷史
        
        Args:
            limit: 返回記錄數量限制
            
        Returns:
            通知歷史列表
        """
        return self.notification_history[-limit:]
    
    def test_notifications(self) -> Dict[str, bool]:
        """
        測試所有通知管道
        
        Returns:
            測試結果字典
        """
        results = {}
        
        # 測試郵件
        if self.config.email_enabled:
            test_email = self.config.email_from or self.config.email_username
            results['email'] = self.send_email(
                [test_email], 
                "測試郵件 / Test Email", 
                "這是一封測試郵件。This is a test email."
            )
        
        # 測試 LINE
        if self.config.line_enabled:
            results['line'] = self.send_line_notification("測試通知 / Test notification")
        
        # 測試 Webhook
        if self.config.webhook_enabled:
            results['webhook'] = self.send_webhook_notification({
                "type": "test",
                "message": "測試 Webhook / Test webhook",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return results

# 全域通知服務實例
notification_service = NotificationService()
