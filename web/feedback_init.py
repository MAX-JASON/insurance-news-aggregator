"""
初始化用戶反饋藍圖
Initialize User Feedback Blueprint

此模組用於將用戶反饋藍圖註冊到Flask應用程式
"""

from flask import Flask
from src.services.user_feedback import feedback_bp, register_feedback_blueprint

def init_feedback(app: Flask) -> Flask:
    """初始化用戶反饋模組並註冊藍圖
    
    Args:
        app: Flask應用實例
        
    Returns:
        Flask: 註冊了反饋藍圖的Flask應用實例
    """
    # 註冊反饋藍圖
    app = register_feedback_blueprint(app)
    app.logger.info("用戶反饋模組初始化完成")
    return app
