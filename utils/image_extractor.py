#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
圖片提取工具
Image Extraction Utility

從新聞內容中提取主圖
"""

import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging
import re

logger = logging.getLogger(__name__)

class ImageExtractor:
    """圖片提取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 忽略的圖片類型
        self.ignore_patterns = [
            r'logo',
            r'icon',
            r'avatar',
            r'banner',
            r'advertisement',
            r'ad_',
            r'social',
            r'share',
            r'button'
        ]
        
        # 優先的圖片選擇器
        self.priority_selectors = [
            'meta[property="og:image"]',
            'meta[name="twitter:image"]',
            'article img',
            '.content img',
            '.news-content img',
            '.article-content img',
            'img[src*="news"]',
            'img[src*="article"]'
        ]
    
    def extract_from_url(self, url, content=None):
        """從URL提取圖片"""
        try:
            if not content:
                response = self.session.get(url, timeout=10, verify=False)
                if response.status_code != 200:
                    return None
                content = response.text
            
            return self.extract_from_content(url, content)
            
        except Exception as e:
            logger.error(f"從URL提取圖片失敗 {url}: {e}")
            return None
    
    def extract_from_content(self, base_url, content):
        """從HTML內容中提取圖片"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # 1. 嘗試Meta標籤
            image_url = self._extract_from_meta(soup, base_url)
            if image_url:
                logger.info(f"✅ 從Meta標籤提取圖片: {image_url}")
                return image_url
            
            # 2. 嘗試優先選擇器
            image_url = self._extract_from_selectors(soup, base_url)
            if image_url:
                logger.info(f"✅ 從內容選擇器提取圖片: {image_url}")
                return image_url
            
            # 3. 通用img標籤搜索
            image_url = self._extract_from_images(soup, base_url)
            if image_url:
                logger.info(f"✅ 從通用img標籤提取圖片: {image_url}")
                return image_url
            
            logger.warning(f"⚠️ 未找到合適圖片: {base_url}")
            return None
            
        except Exception as e:
            logger.error(f"解析HTML內容失敗: {e}")
            return None
    
    def _extract_from_meta(self, soup, base_url):
        """從Meta標籤提取"""
        # Open Graph 圖片
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return self._normalize_url(og_image['content'], base_url)
        
        # Twitter 圖片
        twitter_image = soup.find('meta', name='twitter:image')
        if twitter_image and twitter_image.get('content'):
            return self._normalize_url(twitter_image['content'], base_url)
        
        return None
    
    def _extract_from_selectors(self, soup, base_url):
        """使用優先選擇器提取"""
        for selector in self.priority_selectors:
            if 'meta' in selector:
                continue  # Meta已經處理過了
                
            elements = soup.select(selector)
            for element in elements:
                img_url = element.get('src') or element.get('data-src')
                if img_url and self._is_valid_image(img_url):
                    normalized_url = self._normalize_url(img_url, base_url)
                    if self._verify_image_url(normalized_url):
                        return normalized_url
        
        return None
    
    def _extract_from_images(self, soup, base_url):
        """從所有img標籤中提取"""
        images = soup.find_all('img')
        
        # 按圖片質量評分排序
        scored_images = []
        for img in images:
            img_url = img.get('src') or img.get('data-src')
            if img_url and self._is_valid_image(img_url):
                score = self._score_image(img, img_url)
                if score > 0:
                    scored_images.append((score, img_url))
        
        # 返回評分最高的圖片
        if scored_images:
            scored_images.sort(reverse=True)
            best_img_url = scored_images[0][1]
            normalized_url = self._normalize_url(best_img_url, base_url)
            if self._verify_image_url(normalized_url):
                return normalized_url
        
        return None
    
    def _is_valid_image(self, img_url):
        """檢查是否為有效圖片"""
        if not img_url:
            return False
        
        # 檢查是否包含忽略模式
        for pattern in self.ignore_patterns:
            if re.search(pattern, img_url, re.IGNORECASE):
                return False
        
        # 檢查檔案副檔名
        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        img_url_lower = img_url.lower()
        
        # 直接檢查副檔名
        for ext in valid_extensions:
            if ext in img_url_lower:
                return True
        
        # 如果沒有明確副檔名，但看起來像圖片URL
        if any(keyword in img_url_lower for keyword in ['image', 'photo', 'pic']):
            return True
        
        return False
    
    def _score_image(self, img_element, img_url):
        """為圖片評分"""
        score = 1
        
        # 檢查圖片尺寸屬性
        width = img_element.get('width')
        height = img_element.get('height')
        
        if width and height:
            try:
                w, h = int(width), int(height)
                if w >= 300 and h >= 200:
                    score += 3
                elif w >= 200 and h >= 150:
                    score += 2
                elif w >= 100 and h >= 100:
                    score += 1
            except ValueError:
                pass
        
        # 檢查alt屬性
        alt = img_element.get('alt', '').lower()
        if any(keyword in alt for keyword in ['news', 'article', 'main', 'primary']):
            score += 2
        
        # 檢查CSS類別
        css_class = img_element.get('class', [])
        if isinstance(css_class, list):
            css_class = ' '.join(css_class)
        
        if any(keyword in css_class.lower() for keyword in ['main', 'primary', 'featured', 'hero']):
            score += 2
        
        # 檢查URL質量
        if any(keyword in img_url.lower() for keyword in ['content', 'news', 'article', 'main']):
            score += 1
        
        return score
    
    def _normalize_url(self, img_url, base_url):
        """標準化URL"""
        if not img_url:
            return None
        
        # 移除多餘的空白
        img_url = img_url.strip()
        
        # 處理相對URL
        if img_url.startswith('//'):
            parsed_base = urlparse(base_url)
            img_url = f"{parsed_base.scheme}:{img_url}"
        elif img_url.startswith('/'):
            img_url = urljoin(base_url, img_url)
        elif not img_url.startswith(('http://', 'https://')):
            img_url = urljoin(base_url, img_url)
        
        return img_url
    
    def _verify_image_url(self, img_url):
        """驗證圖片URL是否可訪問"""
        try:
            response = self.session.head(img_url, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                return 'image' in content_type
        except Exception:
            pass
        
        return False

# 創建全局實例
image_extractor = ImageExtractor()

def extract_image_from_url(url, content=None):
    """便利函數：從URL提取圖片"""
    return image_extractor.extract_from_url(url, content)

def extract_image_from_content(base_url, content):
    """便利函數：從HTML內容提取圖片"""
    return image_extractor.extract_from_content(base_url, content)
