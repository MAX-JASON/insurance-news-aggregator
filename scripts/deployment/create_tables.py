"""
創建數據庫表腳本
"""

from app import create_app
from database.models import db

def create_tables():
    """創建所有數據庫表"""
    app = create_app()
    with app.app_context():
        # 創建所有表
        db.create_all()
        print('數據庫表創建成功！')

if __name__ == '__main__':
    create_tables()
