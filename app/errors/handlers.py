"""
錯誤處理器
Error Handlers

提供統一的錯誤處理函數，用於處理不同類型的HTTP錯誤和系統異常。
"""

import traceback
import logging
from flask import render_template, request, jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger('error')

def is_api_request():
    """
    判斷是否為API請求
    
    Returns:
        bool: 是否為API請求
    """
    path = request.path
    accept = request.headers.get('Accept', '')
    return path.startswith('/api') or 'application/json' in accept

def bad_request_error(error):
    """
    400 錯誤處理
    
    Args:
        error: 錯誤對象
    
    Returns:
        響應對象
    """
    logger.warning(f"400錯誤: {error}")
    if is_api_request():
        return jsonify({
            'error': 'bad_request',
            'message': '請求格式錯誤',
            'status_code': 400
        }), 400
    return render_template('errors/400.html', error=error), 400

def unauthorized_error(error):
    """
    401 錯誤處理
    
    Args:
        error: 錯誤對象
    
    Returns:
        響應對象
    """
    logger.warning(f"401錯誤: {error}")
    if is_api_request():
        return jsonify({
            'error': 'unauthorized',
            'message': '需要身份驗證',
            'status_code': 401
        }), 401
    return render_template('errors/401.html', error=error), 401

def forbidden_error(error):
    """
    403 錯誤處理
    
    Args:
        error: 錯誤對象
    
    Returns:
        響應對象
    """
    logger.warning(f"403錯誤: {error}")
    if is_api_request():
        return jsonify({
            'error': 'forbidden',
            'message': '沒有權限訪問該資源',
            'status_code': 403
        }), 403
    return render_template('errors/403.html', error=error), 403

def page_not_found_error(error):
    """
    404 錯誤處理
    
    Args:
        error: 錯誤對象
    
    Returns:
        響應對象
    """
    logger.warning(f"404錯誤: {request.path}")
    if is_api_request():
        return jsonify({
            'error': 'not_found',
            'message': '找不到請求的資源',
            'status_code': 404
        }), 404
    return render_template('errors/404.html', error=error), 404

def too_many_requests_error(error):
    """
    429 錯誤處理
    
    Args:
        error: 錯誤對象
    
    Returns:
        響應對象
    """
    logger.warning(f"429錯誤: 來自{request.remote_addr}的請求過多")
    if is_api_request():
        return jsonify({
            'error': 'too_many_requests',
            'message': '請求頻率過高，請稍後再試',
            'status_code': 429
        }), 429
    return render_template('errors/429.html', error=error), 429

def internal_server_error(error):
    """
    500 錯誤處理
    
    Args:
        error: 錯誤對象
    
    Returns:
        響應對象
    """
    error_msg = str(error)
    logger.error(f"500錯誤: {error_msg}")
    logger.error(traceback.format_exc())
    
    if is_api_request():
        return jsonify({
            'error': 'internal_server_error',
            'message': '服務器內部錯誤',
            'status_code': 500
        }), 500
    return render_template('errors/500.html', error=error), 500

def handle_general_exception(error):
    """
    處理一般異常
    
    Args:
        error: 錯誤對象
    
    Returns:
        響應對象
    """
    error_msg = str(error)
    logger.error(f"未處理異常: {error_msg}")
    logger.error(traceback.format_exc())
    
    # 如果是HTTP異常，使用其狀態碼
    if isinstance(error, HTTPException):
        code = error.code
    else:
        code = 500
    
    if is_api_request():
        return jsonify({
            'error': 'server_error',
            'message': '處理請求時發生錯誤',
            'status_code': code
        }), code
    return render_template('errors/generic.html', error=error, code=code), code