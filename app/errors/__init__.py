"""
錯誤處理模組初始化
Error Handling Module Initialization

本模組提供統一的錯誤處理機制，用於捕獲和處理系統中的各種錯誤。
"""

from app.errors import handlers

def register_error_handlers(app):
    """
    註冊所有錯誤處理器
    
    Args:
        app: Flask應用實例
    """
    # 註冊HTTP錯誤處理器
    app.register_error_handler(400, handlers.bad_request_error)
    app.register_error_handler(401, handlers.unauthorized_error)
    app.register_error_handler(403, handlers.forbidden_error)
    app.register_error_handler(404, handlers.page_not_found_error)
    app.register_error_handler(429, handlers.too_many_requests_error)
    app.register_error_handler(500, handlers.internal_server_error)

    # 註冊自定義異常處理器
    app.register_error_handler(Exception, handlers.handle_general_exception)