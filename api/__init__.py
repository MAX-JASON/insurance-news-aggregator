"""
API 模組
API Module

提供 REST API 相關功能
"""

try:
    # 優先導入標準路由
    from .routes import api_bp
except ImportError:
    try:
        # 嘗試導入修復版路由
        from .routes_fix import api_bp
    except ImportError:
        # 嘗試導入簡單API路由
        from .simple_api import simple_api_bp as api_bp

__all__ = ['api_bp']
