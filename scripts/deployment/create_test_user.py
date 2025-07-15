"""
創建測試用戶腳本
"""

from app import create_app
from database.models import User, db

def create_test_user():
    """創建測試用戶"""
    app = create_app()
    with app.app_context():
        # 檢查用戶是否已存在
        existing_user = User.query.filter_by(username='testuser').first()
        if existing_user:
            print(f'測試用戶已存在，ID: {existing_user.id}')
            return
            
        # 創建新用戶
        user = User(
            username='testuser',
            email='test@example.com',
            full_name='測試使用者',
            job_title='資深業務',
            department='業務部'
        )
        user.set_password('password')
        
        # 保存到數據庫
        db.session.add(user)
        db.session.commit()
        
        print(f'創建測試用戶成功，ID: {user.id}')

if __name__ == '__main__':
    create_test_user()
