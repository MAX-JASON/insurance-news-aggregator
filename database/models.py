"""
資料庫模型定義
Database Models Definition

定義保險新聞聚合器的所有資料模型
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from app import db

# 使用 Flask-SQLAlchemy 的 Model 基類
class BaseModel(db.Model):
    """基礎模型類，包含通用欄位"""
    
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(
        db.DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    def to_dict(self, exclude_fields=None):
        """轉換為字典格式"""
        exclude_fields = exclude_fields or []
        result = {}
        for column in self.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(self, column.name)
                if isinstance(value, datetime):
                    value = value.isoformat()
                result[column.name] = value
        return result
    
    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id}>'

class NewsSource(BaseModel):
    """新聞來源模型"""
    
    __tablename__ = 'news_sources'
    
    name = db.Column(db.String(200), nullable=False, unique=True, comment='來源名稱')
    url = db.Column(db.String(500), nullable=False, comment='來源網址')
    description = db.Column(db.Text, comment='來源描述')
    logo_url = db.Column(db.String(500), comment='LOGO網址')
    
    # 爬蟲相關配置
    crawl_frequency = db.Column(db.Integer, default=3600, comment='爬取頻率(秒)')
    last_crawl_time = db.Column(db.DateTime(timezone=True), comment='最後爬取時間')
    crawl_selector = db.Column(db.Text, comment='CSS選擇器配置(JSON)')
    
    # 狀態和信譽
    status = db.Column(db.String(20), default='active', comment='狀態:active/inactive/suspended')
    reliability_score = db.Column(db.Float, default=1.0, comment='可靠性評分(0-1)')
    
    # 統計信息
    total_news_count = db.Column(db.Integer, default=0, comment='總新聞數量')
    successful_crawls = db.Column(db.Integer, default=0, comment='成功爬取次數')
    failed_crawls = db.Column(db.Integer, default=0, comment='失敗爬取次數')
    
    # 關聯關係
    news = relationship('News', back_populates='source', lazy='dynamic')
    
    def __repr__(self):
        return f'<NewsSource {self.name}>'

class NewsCategory(BaseModel):
    """新聞分類模型"""
    
    __tablename__ = 'news_categories'
    
    name = db.Column(db.String(100), nullable=False, unique=True, comment='分類名稱')
    description = db.Column(db.Text, comment='分類描述')
    
    # 層級結構
    parent_id = db.Column(db.Integer, db.ForeignKey('news_categories.id'), comment='父分類ID')
    level = db.Column(db.Integer, default=0, comment='層級(0為根分類)')
    sort_order = db.Column(db.Integer, default=0, comment='排序順序')
    
    # 顯示設置
    color_code = db.Column(db.String(7), comment='顏色代碼(#RRGGBB)')
    icon = db.Column(db.String(50), comment='圖標名稱')
    
    # 狀態
    status = db.Column(db.String(20), default='active', comment='狀態')
    news_count = db.Column(db.Integer, default=0, comment='新聞數量')
      # 關聯關係
    news = relationship('News', back_populates='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<NewsCategory {self.name}>'

class News(BaseModel):
    """新聞模型"""
    
    __tablename__ = 'news'
    
    # 基本信息
    title = db.Column(db.String(500), nullable=False, comment='新聞標題')
    content = db.Column(db.Text, nullable=False, comment='新聞內容')
    summary = db.Column(db.Text, comment='新聞摘要')
    url = db.Column(db.String(1000), unique=True, nullable=False, comment='原始網址')
    
    # 外鍵關聯
    source_id = db.Column(db.Integer, db.ForeignKey('news_sources.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('news_categories.id'))
    
    # 時間信息
    published_date = db.Column(db.DateTime(timezone=True), nullable=False, comment='發布時間')
    crawled_date = db.Column(
        db.DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        comment='爬取時間'
    )
    
    # 媒體信息
    image_url = db.Column(db.String(1000), comment='主圖網址')
    author = db.Column(db.String(200), comment='作者')
    
    # 分析結果
    keywords = db.Column(db.Text, comment='關鍵詞(JSON陣列)')
    sentiment_score = db.Column(db.Float, comment='情感分析評分(-1到1)')
    importance_score = db.Column(db.Float, default=0.0, comment='重要性評分(0-1)')
    
    # 統計信息
    view_count = db.Column(db.Integer, default=0, comment='瀏覽次數')
    share_count = db.Column(db.Integer, default=0, comment='分享次數')
    
    # 狀態和標籤
    status = db.Column(db.String(20), default='active', comment='狀態:active/hidden/deleted')
    tags = db.Column(db.Text, comment='標籤(JSON陣列)')
    
    # 內容特徵
    word_count = db.Column(db.Integer, comment='字數')
    reading_time = db.Column(db.Integer, comment='預估閱讀時間(秒)')
    
    # 關聯關係
    source = relationship('NewsSource', back_populates='news')
    category = relationship('NewsCategory', back_populates='news')
    
    # 索引
    __table_args__ = (
        Index('idx_news_published_date', 'published_date'),
        Index('idx_news_source_category', 'source_id', 'category_id'),
        Index('idx_news_status', 'status'),
        Index('idx_news_sentiment', 'sentiment_score'),
        Index('idx_news_importance', 'importance_score'),
    )
    
    def get_image_url(self):
        """獲取圖片URL，提供備用方案"""
        if self.image_url:
            # 檢查是否為完整URL
            if self.image_url.startswith(('http://', 'https://')):
                return self.image_url
            else:
                # 處理相對路徑
                from flask import url_for
                return url_for('static', filename=f'images/{self.image_url}', _external=True)
        
        # 返回預設圖片
        from flask import url_for
        return url_for('static', filename='images/news-placeholder.jpg', _external=True)
    
    def get_formatted_published_date(self):
        """獲取格式化的發佈時間"""
        if self.published_date:
            return self.published_date.strftime('%Y-%m-%d %H:%M')
        return '未知時間'
    
    def get_reading_time_text(self):
        """獲取閱讀時間文字"""
        if self.reading_time:
            minutes = self.reading_time // 60
            return f'{minutes}分鐘' if minutes > 0 else '1分鐘'
        return '預估1分鐘'
    
    def __repr__(self):
        return f'<News {self.title[:50]}...>'

class CrawlLog(BaseModel):
    """爬取日誌模型"""
    
    __tablename__ = 'crawl_logs'
    
    source_id = db.Column(db.Integer, db.ForeignKey('news_sources.id'), nullable=False)
    
    # 爬取信息
    start_time = db.Column(db.DateTime(timezone=True), nullable=False)
    end_time = db.Column(db.DateTime(timezone=True))
    duration = db.Column(db.Float, comment='爬取耗時(秒)')
    
    # 結果統計
    success = db.Column(db.Boolean, default=False, comment='是否成功')
    news_found = db.Column(db.Integer, default=0, comment='發現新聞數量')
    news_new = db.Column(db.Integer, default=0, comment='新增新聞數量')
    news_updated = db.Column(db.Integer, default=0, comment='更新新聞數量')
    
    # 錯誤信息
    error_message = db.Column(db.Text, comment='錯誤信息')
    error_type = db.Column(db.String(100), comment='錯誤類型')
    
    # 技術信息
    user_agent = db.Column(db.String(500), comment='User Agent')
    ip_address = db.Column(db.String(45), comment='IP地址')
    response_status = db.Column(db.Integer, comment='HTTP狀態碼')
    
    # 關聯關係
    source = relationship('NewsSource')
    
    def __repr__(self):
        return f'<CrawlLog {self.source_id} {self.start_time}>'

class AnalysisLog(BaseModel):
    """分析日誌模型"""
    
    __tablename__ = 'analysis_logs'
    
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)
    
    # 分析類型和結果
    analysis_type = db.Column(db.String(50), nullable=False, comment='分析類型:keyword/sentiment/category')
    analysis_result = db.Column(db.Text, comment='分析結果(JSON)')
    
    # 執行信息
    start_time = db.Column(db.DateTime(timezone=True), nullable=False)
    end_time = db.Column(db.DateTime(timezone=True))
    duration = db.Column(db.Float, comment='分析耗時(秒)')
    
    # 狀態
    success = db.Column(db.Boolean, default=False)
    error_message = db.Column(db.Text, comment='錯誤信息')
    
    # 模型信息
    model_name = db.Column(db.String(100), comment='使用的模型名稱')
    model_version = db.Column(db.String(50), comment='模型版本')
    confidence_score = db.Column(db.Float, comment='置信度評分')
    
    # 關聯關係
    news = relationship('News')
    
    def __repr__(self):
        return f'<AnalysisLog {self.analysis_type} {self.news_id}>'

class ErrorLog(BaseModel):
    """錯誤日誌模型"""
    
    __tablename__ = 'error_logs'
    
    # 基本錯誤信息
    timestamp = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), comment='錯誤時間')
    level = db.Column(db.String(20), nullable=False, default='ERROR', comment='錯誤等級:DEBUG/INFO/WARNING/ERROR/CRITICAL')
    module = db.Column(db.String(100), comment='錯誤發生模組')
    message = db.Column(db.Text, nullable=False, comment='錯誤信息')
    
    # 詳細錯誤信息
    traceback = db.Column(db.Text, comment='錯誤堆疊')
    request_path = db.Column(db.String(500), comment='請求路徑')
    request_method = db.Column(db.String(10), comment='請求方法')
    
    # 環境信息
    user_agent = db.Column(db.String(500), comment='User Agent')
    ip_address = db.Column(db.String(45), comment='IP地址')
    
    # 附加信息
    context = db.Column(db.Text, comment='上下文信息(JSON)')
    
    def __repr__(self):
        return f'<ErrorLog {self.level} {self.module}: {self.message[:50]}>'

class User(BaseModel):
    """用戶模型"""
    
    __tablename__ = 'users'
    
    # 基本信息
    username = db.Column(db.String(100), unique=True, nullable=False, comment='用戶名')
    email = db.Column(db.String(100), unique=True, nullable=False, comment='電子郵件')
    password_hash = db.Column(db.String(200), nullable=False, comment='密碼雜湊')
    
    # 個人信息
    full_name = db.Column(db.String(100), comment='姓名')
    job_title = db.Column(db.String(100), comment='職稱')
    department = db.Column(db.String(100), comment='部門')
    
    # 狀態
    status = db.Column(db.String(20), default='active', comment='狀態:active/inactive/suspended')
    role = db.Column(db.String(20), default='user', comment='角色:admin/manager/user')
    last_login = db.Column(db.DateTime(timezone=True), comment='最後登入時間')
    
    # 偏好設定
    preferences = db.Column(db.Text, comment='偏好設定(JSON)')
    
    # 關聯關係
    saved_news = relationship('SavedNews', back_populates='user')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def check_password(self, password):
        """檢查密碼"""
        # 實際應用中應使用適當的密碼雜湊函數
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    def set_password(self, password):
        """設置密碼"""
        # 實際應用中應使用適當的密碼雜湊函數
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

class SavedNews(BaseModel):
    """收藏新聞模型"""
    
    __tablename__ = 'saved_news'
    
    # 外鍵關聯
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)
    
    # 收藏信息
    folder = db.Column(db.String(100), default='default', comment='收藏夾名稱')
    notes = db.Column(db.Text, comment='備註')
    importance = db.Column(db.Integer, default=0, comment='用戶標記的重要性(1-5)')
    
    # 關聯關係
    user = relationship('User', back_populates='saved_news')
    news = relationship('News')
    
    # 確保用戶不會重複收藏同一新聞
    __table_args__ = (
        db.UniqueConstraint('user_id', 'news_id', name='unique_user_news'),
    )
    
    def __repr__(self):
        return f'<SavedNews user:{self.user_id} news:{self.news_id}>'

class Feedback(BaseModel):
    """用戶反饋模型"""
    
    __tablename__ = 'feedback'
    
    # 基本信息
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='用戶ID，0表示匿名用戶')
    category = db.Column(db.String(50), nullable=False, comment='反饋類別')
    rating = db.Column(db.Integer, nullable=False, comment='評分（1-5）')
    message = db.Column(db.Text, comment='反饋訊息')
    
    # 相關功能
    features = db.Column(db.Text, comment='相關功能（JSON陣列）')
    
    # 來源信息
    source = db.Column(db.String(20), default='web', comment='來源：web/api/mobile')
    timestamp = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # 附加信息
    extra_data = db.Column(db.Text, comment='元數據（JSON）')
    status = db.Column(db.String(20), default='new', comment='狀態：new/viewed/responded')
    
    # 管理信息
    admin_notes = db.Column(db.Text, comment='管理員備註')
    response_message = db.Column(db.Text, comment='回覆訊息')
    response_timestamp = db.Column(db.DateTime(timezone=True), comment='回覆時間')
    
    def __repr__(self):
        return f'<Feedback {self.id}: {self.category}>'

class SystemConfig(BaseModel):
    """系統配置模型"""
    
    __tablename__ = 'system_configs'
    
    key = db.Column(db.String(100), unique=True, nullable=False, comment='配置鍵')
    value = db.Column(db.Text, comment='配置值')
    description = db.Column(db.Text, comment='配置描述')
    config_type = db.Column(db.String(50), default='string', comment='配置類型:string/int/float/boolean/json')
    
    # 分組和排序
    group_name = db.Column(db.String(100), comment='配置分組')
    sort_order = db.Column(db.Integer, default=0, comment='排序順序')
    
    # 狀態
    is_active = db.Column(db.Boolean, default=True, comment='是否啟用')
    is_readonly = db.Column(db.Boolean, default=False, comment='是否只讀')
    
    def __repr__(self):
        return f'<SystemConfig {self.key}>'
    
    @classmethod
    def get_value(cls, key, default=None):
        """獲取配置值"""
        config = cls.query.filter_by(key=key, is_active=True).first()
        if not config:
            return default
        
        try:
            if config.config_type == 'int':
                return int(config.value)
            elif config.config_type == 'float':
                return float(config.value)
            elif config.config_type == 'boolean':
                return config.value.lower() in ('true', '1', 'yes')
            elif config.config_type == 'json':
                import json
                return json.loads(config.value)
            else:
                return config.value
        except (ValueError, TypeError):
            return default
    
    @classmethod
    def set_value(cls, key, value, description=None, config_type='string'):
        """設置配置值"""
        config = cls.query.filter_by(key=key).first()
        if not config:
            config = cls(key=key, config_type=config_type)
            db.session.add(config)
        
        if config_type == 'json':
            import json
            config.value = json.dumps(value, ensure_ascii=False)
        else:
            config.value = str(value)
        
        if description:
            config.description = description
            
        db.session.commit()
        return config
