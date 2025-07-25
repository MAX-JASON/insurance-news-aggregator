"""Initial migration

Revision ID: 03f833202eb0
Revises: 
Create Date: 2025-06-15 03:12:03.926394

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '03f833202eb0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('news_categories',
    sa.Column('name', sa.String(length=100), nullable=False, comment='分類名稱'),
    sa.Column('description', sa.Text(), nullable=True, comment='分類描述'),
    sa.Column('parent_id', sa.Integer(), nullable=True, comment='父分類ID'),
    sa.Column('level', sa.Integer(), nullable=True, comment='層級(0為根分類)'),
    sa.Column('sort_order', sa.Integer(), nullable=True, comment='排序順序'),
    sa.Column('color_code', sa.String(length=7), nullable=True, comment='顏色代碼(#RRGGBB)'),
    sa.Column('icon', sa.String(length=50), nullable=True, comment='圖標名稱'),
    sa.Column('status', sa.String(length=20), nullable=True, comment='狀態'),
    sa.Column('news_count', sa.Integer(), nullable=True, comment='新聞數量'),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['parent_id'], ['news_categories.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('news_sources',
    sa.Column('name', sa.String(length=200), nullable=False, comment='來源名稱'),
    sa.Column('url', sa.String(length=500), nullable=False, comment='來源網址'),
    sa.Column('description', sa.Text(), nullable=True, comment='來源描述'),
    sa.Column('logo_url', sa.String(length=500), nullable=True, comment='LOGO網址'),
    sa.Column('crawl_frequency', sa.Integer(), nullable=True, comment='爬取頻率(秒)'),
    sa.Column('last_crawl_time', sa.DateTime(timezone=True), nullable=True, comment='最後爬取時間'),
    sa.Column('crawl_selector', sa.Text(), nullable=True, comment='CSS選擇器配置(JSON)'),
    sa.Column('status', sa.String(length=20), nullable=True, comment='狀態:active/inactive/suspended'),
    sa.Column('reliability_score', sa.Float(), nullable=True, comment='可靠性評分(0-1)'),
    sa.Column('total_news_count', sa.Integer(), nullable=True, comment='總新聞數量'),
    sa.Column('successful_crawls', sa.Integer(), nullable=True, comment='成功爬取次數'),
    sa.Column('failed_crawls', sa.Integer(), nullable=True, comment='失敗爬取次數'),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('system_configs',
    sa.Column('key', sa.String(length=100), nullable=False, comment='配置鍵'),
    sa.Column('value', sa.Text(), nullable=True, comment='配置值'),
    sa.Column('description', sa.Text(), nullable=True, comment='配置描述'),
    sa.Column('config_type', sa.String(length=50), nullable=True, comment='配置類型:string/int/float/boolean/json'),
    sa.Column('group_name', sa.String(length=100), nullable=True, comment='配置分組'),
    sa.Column('sort_order', sa.Integer(), nullable=True, comment='排序順序'),
    sa.Column('is_active', sa.Boolean(), nullable=True, comment='是否啟用'),
    sa.Column('is_readonly', sa.Boolean(), nullable=True, comment='是否只讀'),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key')
    )
    op.create_table('crawl_logs',
    sa.Column('source_id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
    sa.Column('duration', sa.Float(), nullable=True, comment='爬取耗時(秒)'),
    sa.Column('success', sa.Boolean(), nullable=True, comment='是否成功'),
    sa.Column('news_found', sa.Integer(), nullable=True, comment='發現新聞數量'),
    sa.Column('news_new', sa.Integer(), nullable=True, comment='新增新聞數量'),
    sa.Column('news_updated', sa.Integer(), nullable=True, comment='更新新聞數量'),
    sa.Column('error_message', sa.Text(), nullable=True, comment='錯誤信息'),
    sa.Column('error_type', sa.String(length=100), nullable=True, comment='錯誤類型'),
    sa.Column('user_agent', sa.String(length=500), nullable=True, comment='User Agent'),
    sa.Column('ip_address', sa.String(length=45), nullable=True, comment='IP地址'),
    sa.Column('response_status', sa.Integer(), nullable=True, comment='HTTP狀態碼'),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['source_id'], ['news_sources.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('news',
    sa.Column('title', sa.String(length=500), nullable=False, comment='新聞標題'),
    sa.Column('content', sa.Text(), nullable=False, comment='新聞內容'),
    sa.Column('summary', sa.Text(), nullable=True, comment='新聞摘要'),
    sa.Column('url', sa.String(length=1000), nullable=False, comment='原始網址'),
    sa.Column('source_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('published_date', sa.DateTime(timezone=True), nullable=False, comment='發布時間'),
    sa.Column('crawled_date', sa.DateTime(timezone=True), nullable=True, comment='爬取時間'),
    sa.Column('image_url', sa.String(length=1000), nullable=True, comment='主圖網址'),
    sa.Column('author', sa.String(length=200), nullable=True, comment='作者'),
    sa.Column('keywords', sa.Text(), nullable=True, comment='關鍵詞(JSON陣列)'),
    sa.Column('sentiment_score', sa.Float(), nullable=True, comment='情感分析評分(-1到1)'),
    sa.Column('importance_score', sa.Float(), nullable=True, comment='重要性評分(0-1)'),
    sa.Column('view_count', sa.Integer(), nullable=True, comment='瀏覽次數'),
    sa.Column('share_count', sa.Integer(), nullable=True, comment='分享次數'),
    sa.Column('status', sa.String(length=20), nullable=True, comment='狀態:active/hidden/deleted'),
    sa.Column('tags', sa.Text(), nullable=True, comment='標籤(JSON陣列)'),
    sa.Column('word_count', sa.Integer(), nullable=True, comment='字數'),
    sa.Column('reading_time', sa.Integer(), nullable=True, comment='預估閱讀時間(秒)'),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['news_categories.id'], ),
    sa.ForeignKeyConstraint(['source_id'], ['news_sources.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('url')
    )
    op.create_index('idx_news_importance', 'news', ['importance_score'], unique=False)
    op.create_index('idx_news_published_date', 'news', ['published_date'], unique=False)
    op.create_index('idx_news_sentiment', 'news', ['sentiment_score'], unique=False)
    op.create_index('idx_news_source_category', 'news', ['source_id', 'category_id'], unique=False)
    op.create_index('idx_news_status', 'news', ['status'], unique=False)
    op.create_table('analysis_logs',
    sa.Column('news_id', sa.Integer(), nullable=False),
    sa.Column('analysis_type', sa.String(length=50), nullable=False, comment='分析類型:keyword/sentiment/category'),
    sa.Column('analysis_result', sa.Text(), nullable=True, comment='分析結果(JSON)'),
    sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
    sa.Column('duration', sa.Float(), nullable=True, comment='分析耗時(秒)'),
    sa.Column('success', sa.Boolean(), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True, comment='錯誤信息'),
    sa.Column('model_name', sa.String(length=100), nullable=True, comment='使用的模型名稱'),
    sa.Column('model_version', sa.String(length=50), nullable=True, comment='模型版本'),
    sa.Column('confidence_score', sa.Float(), nullable=True, comment='置信度評分'),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['news_id'], ['news.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('analysis_logs')
    op.drop_index('idx_news_status', table_name='news')
    op.drop_index('idx_news_source_category', table_name='news')
    op.drop_index('idx_news_sentiment', table_name='news')
    op.drop_index('idx_news_published_date', table_name='news')
    op.drop_index('idx_news_importance', table_name='news')
    op.drop_table('news')
    op.drop_table('crawl_logs')
    op.drop_table('system_configs')
    op.drop_table('news_sources')
    op.drop_table('news_categories')
    # ### end Alembic commands ###
