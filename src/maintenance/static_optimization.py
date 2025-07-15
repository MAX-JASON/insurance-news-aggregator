"""
靜態資源優化腳本
Static Resources Optimization Script

提供CSS、JavaScript文件壓縮和優化功能，並實現懶加載策略
"""

import os
import re
import time
import logging
import shutil
import json
from csscompressor import compress as compress_css
from jsmin import jsmin
from flask import current_app
from datetime import datetime

# 設置日誌
logger = logging.getLogger('maintenance.static_optimization')

class StaticResourceOptimizer:
    """靜態資源優化器"""
    
    def __init__(self, static_folder, build_folder=None):
        """初始化
        
        Args:
            static_folder: 靜態資源源文件夾
            build_folder: 優化後的目標文件夾，預設為static_folder/dist
        """
        self.static_folder = static_folder
        self.build_folder = build_folder or os.path.join(static_folder, 'dist')
        self.css_files = []
        self.js_files = []
        self.image_files = []
        self.manifest = {}
        
        # 確保目標資料夾存在
        os.makedirs(self.build_folder, exist_ok=True)
    
    def scan_files(self):
        """掃描所有需要優化的文件"""
        for root, dirs, files in os.walk(self.static_folder):
            # 跳過dist目錄
            if '/dist' in root or '\\dist' in root:
                continue
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.static_folder)
                
                if file.endswith('.css'):
                    self.css_files.append((file_path, rel_path))
                elif file.endswith('.js'):
                    self.js_files.append((file_path, rel_path))
                elif file.endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp')):
                    self.image_files.append((file_path, rel_path))
        
        logger.info(f"掃描到 {len(self.css_files)} 個CSS文件，{len(self.js_files)} 個JS文件，{len(self.image_files)} 個圖片文件")
    
    def optimize_css(self):
        """優化CSS文件"""
        for file_path, rel_path in self.css_files:
            try:
                # 讀取CSS文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                
                # 壓縮CSS
                minified_css = compress_css(css_content)
                
                # 計算文件名稱（添加哈希值）
                file_hash = str(hash(minified_css))[-8:]
                base_name = os.path.basename(rel_path)
                name_parts = os.path.splitext(base_name)
                new_name = f"{name_parts[0]}.min.{file_hash}{name_parts[1]}"
                
                # 計算輸出路徑
                output_dir = os.path.dirname(os.path.join(self.build_folder, rel_path))
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, new_name)
                
                # 寫入優化後的CSS
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(minified_css)
                
                # 添加到資源映射表
                self.manifest[rel_path] = os.path.join(os.path.dirname(rel_path), new_name).replace('\\', '/')
                
                logger.info(f"優化CSS文件: {rel_path} -> {os.path.join(os.path.dirname(rel_path), new_name)}")
            except Exception as e:
                logger.error(f"優化CSS文件失敗 {rel_path}: {e}")
    
    def optimize_js(self):
        """優化JavaScript文件"""
        for file_path, rel_path in self.js_files:
            try:
                # 讀取JS文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    js_content = f.read()
                
                # 壓縮JS
                minified_js = jsmin(js_content)
                
                # 計算文件名稱（添加哈希值）
                file_hash = str(hash(minified_js))[-8:]
                base_name = os.path.basename(rel_path)
                name_parts = os.path.splitext(base_name)
                new_name = f"{name_parts[0]}.min.{file_hash}{name_parts[1]}"
                
                # 計算輸出路徑
                output_dir = os.path.dirname(os.path.join(self.build_folder, rel_path))
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, new_name)
                
                # 寫入優化後的JS
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(minified_js)
                
                # 添加到資源映射表
                self.manifest[rel_path] = os.path.join(os.path.dirname(rel_path), new_name).replace('\\', '/')
                
                logger.info(f"優化JS文件: {rel_path} -> {os.path.join(os.path.dirname(rel_path), new_name)}")
            except Exception as e:
                logger.error(f"優化JS文件失敗 {rel_path}: {e}")
    
    def copy_images(self):
        """複製圖片文件（可以在這裡實現圖片壓縮，但需要額外的依賴）"""
        for file_path, rel_path in self.image_files:
            try:
                # 計算輸出路徑
                output_path = os.path.join(self.build_folder, rel_path)
                output_dir = os.path.dirname(output_path)
                os.makedirs(output_dir, exist_ok=True)
                
                # 複製圖片
                shutil.copy2(file_path, output_path)
                
                # 添加到資源映射表
                self.manifest[rel_path] = rel_path
                
                logger.info(f"複製圖片文件: {rel_path}")
            except Exception as e:
                logger.error(f"複製圖片文件失敗 {rel_path}: {e}")
    
    def generate_lazy_load_js(self):
        """生成懶加載JavaScript"""
        lazy_load_js = """
/**
 * 保險新聞聚合器 - 懶加載工具
 * Insurance News Aggregator - Lazy Loading Utils
 */
(function() {
    // 懶加載圖片
    function lazyLoadImages() {
        var lazyImages = [].slice.call(document.querySelectorAll('img.lazy'));
        
        if ("IntersectionObserver" in window) {
            let lazyImageObserver = new IntersectionObserver(function(entries, observer) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        let lazyImage = entry.target;
                        lazyImage.src = lazyImage.dataset.src;
                        if (lazyImage.dataset.srcset) {
                            lazyImage.srcset = lazyImage.dataset.srcset;
                        }
                        lazyImage.classList.remove("lazy");
                        lazyImageObserver.unobserve(lazyImage);
                    }
                });
            });

            lazyImages.forEach(function(lazyImage) {
                lazyImageObserver.observe(lazyImage);
            });
        } else {
            // 不支援 Intersection Observer 的瀏覽器的備用方案
            let active = false;

            const lazyLoad = function() {
                if (active === false) {
                    active = true;

                    setTimeout(function() {
                        lazyImages.forEach(function(lazyImage) {
                            if ((lazyImage.getBoundingClientRect().top <= window.innerHeight && lazyImage.getBoundingClientRect().bottom >= 0) && getComputedStyle(lazyImage).display !== "none") {
                                lazyImage.src = lazyImage.dataset.src;
                                if (lazyImage.dataset.srcset) {
                                    lazyImage.srcset = lazyImage.dataset.srcset;
                                }
                                lazyImage.classList.remove("lazy");

                                lazyImages = lazyImages.filter(function(image) {
                                    return image !== lazyImage;
                                });

                                if (lazyImages.length === 0) {
                                    document.removeEventListener("scroll", lazyLoad);
                                    window.removeEventListener("resize", lazyLoad);
                                    window.removeEventListener("orientationChange", lazyLoad);
                                }
                            }
                        });

                        active = false;
                    }, 200);
                }
            };

            document.addEventListener("scroll", lazyLoad);
            window.addEventListener("resize", lazyLoad);
            window.addEventListener("orientationChange", lazyLoad);
            lazyLoad();
        }
    }

    // 延遲加載CSS
    function loadDeferredStyles() {
        var loadDeferredStyles = function() {
            var addStylesNodes = document.querySelectorAll("link[rel='preload'][as='style']");
            var i, l = addStylesNodes.length;
            for (i = 0; i < l; i++) {
                addStylesNodes[i].rel = "stylesheet";
            }
        };
        var raf = window.requestAnimationFrame || window.mozRequestAnimationFrame ||
                window.webkitRequestAnimationFrame || window.msRequestAnimationFrame;
        if (raf) raf(function() { window.setTimeout(loadDeferredStyles, 0); });
        else window.addEventListener('load', loadDeferredStyles);
    }

    // DOM加載完成後執行
    document.addEventListener('DOMContentLoaded', function() {
        lazyLoadImages();
        loadDeferredStyles();
    });
})();
"""
        
        output_path = os.path.join(self.build_folder, 'js', 'lazy-load.min.js')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(lazy_load_js)
        
        self.manifest['js/lazy-load.js'] = 'js/lazy-load.min.js'
        logger.info("生成懶加載JavaScript")
    
    def generate_manifest(self):
        """生成資源清單文件"""
        manifest_path = os.path.join(self.build_folder, 'manifest.json')
        
        # 添加時間戳
        self.manifest['_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.manifest['_version'] = str(int(time.time()))
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(self.manifest, f, ensure_ascii=False, indent=2)
        
        logger.info(f"生成資源清單文件: {manifest_path}")
    
    def generate_helper(self):
        """生成Flask靜態資源助手"""
        helper_code = """
'''
靜態資源助手
Static Assets Helper

提供優化後的靜態資源URL生成功能
'''

import os
import json
from flask import url_for, current_app

class StaticAssets:
    '''靜態資源助手類'''
    
    _instance = None
    _manifest = None
    
    @classmethod
    def instance(cls):
        '''獲取單例實例'''
        if cls._instance is None:
            cls._instance = StaticAssets()
        return cls._instance
    
    def __init__(self):
        '''初始化'''
        self.load_manifest()
    
    def load_manifest(self):
        '''加載資源清單'''
        try:
            manifest_path = os.path.join(current_app.static_folder, 'dist', 'manifest.json')
            with open(manifest_path, 'r', encoding='utf-8') as f:
                self._manifest = json.load(f)
        except Exception as e:
            current_app.logger.error(f"無法載入靜態資源清單: {e}")
            self._manifest = {}
    
    def url_for(self, path):
        '''獲取優化後的靜態資源URL'''
        if self._manifest is None:
            self.load_manifest()
        
        # 使用清單映射，如果沒有則使用原始路徑
        if path in self._manifest:
            return url_for('static', filename=f"dist/{self._manifest[path]}")
        else:
            return url_for('static', filename=path)
    
    def version(self):
        '''獲取靜態資源版本'''
        if self._manifest is None:
            self.load_manifest()
        
        return self._manifest.get('_version', '')

# 創建全局實例
assets = StaticAssets.instance()
"""
        
        output_path = os.path.join(self.static_folder, '..', '..', 'app', 'static_assets.py')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(helper_code)
        
        logger.info(f"生成Flask靜態資源助手: {output_path}")
    
    def update_templates(self):
        """更新模板中的靜態資源引用"""
        template_folder = os.path.join(os.path.dirname(self.static_folder), 'templates')
        
        for root, dirs, files in os.walk(template_folder):
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    self._update_template(file_path)
    
    def _update_template(self, template_path):
        """更新單個模板文件中的靜態資源引用"""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 更新CSS引用
            pattern = r'<link\s+[^>]*href=[\"\']{{ url_for\([\'"]static[\'"],\s*filename=[\'"]([^\'"]*)[\'"]\) }}[\"\'][^>]*>'
            
            def css_replacer(match):
                path = match.group(1)
                if path in self.manifest:
                    return f'<link rel="stylesheet" href="{{ assets.url_for(\'{path}\') }}">'
                return match.group(0)
            
            content = re.sub(pattern, css_replacer, content)
            
            # 更新JS引用
            pattern = r'<script\s+[^>]*src=[\"\']{{ url_for\([\'"]static[\'"],\s*filename=[\'"]([^\'"]*)[\'"]\) }}[\"\'][^>]*>'
            
            def js_replacer(match):
                path = match.group(1)
                if path in self.manifest:
                    return f'<script src="{{ assets.url_for(\'{path}\') }}">'
                return match.group(0)
            
            content = re.sub(pattern, js_replacer, content)
            
            # 添加懶加載JS引用（如果還沒有）
            if '<script src="{{ assets.url_for(\'js/lazy-load.js\') }}">' not in content:
                content = content.replace('</body>', '<script src="{{ assets.url_for(\'js/lazy-load.js\') }}"></script></body>')
            
            # 添加靜態資源助手導入（如果還沒有）
            pattern = r'{% extends [\'"][^\']*[\'"] %}'
            if re.search(pattern, content) and '{% from "static_assets.html" import assets %}' not in content:
                content = re.sub(pattern, r'\g<0>\n{% from "static_assets.html" import assets %}', content)
            
            # 轉換圖片為懶加載
            pattern = r'<img\s+([^>]*)src=[\"\']{{ url_for\([\'"]static[\'"],\s*filename=[\'"]([^\'"]*)[\'"]\) }}[\"\']([^>]*)>'
            
            def img_replacer(match):
                prefix = match.group(1)
                path = match.group(2)
                suffix = match.group(3)
                
                if 'class=' in prefix or 'class=' in suffix:
                    result = re.sub(r'class=[\"\']([^\"\']*)[\"\']', r'class="\1 lazy"', match.group(0))
                    result = result.replace('src="', 'data-src="')
                    return result
                else:
                    result = match.group(0).replace('<img ', '<img class="lazy" ')
                    result = result.replace('src="', 'data-src="')
                    return result
            
            content = re.sub(pattern, img_replacer, content)
            
            # 寫回文件
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"更新模板文件: {template_path}")
        except Exception as e:
            logger.error(f"更新模板文件失敗 {template_path}: {e}")
    
    def run(self):
        """執行所有優化任務"""
        self.scan_files()
        self.optimize_css()
        self.optimize_js()
        self.copy_images()
        self.generate_lazy_load_js()
        self.generate_manifest()
        self.generate_helper()
        #self.update_templates()
        
        return {
            'css_files': len(self.css_files),
            'js_files': len(self.js_files),
            'image_files': len(self.image_files),
            'manifest': self.manifest
        }

def create_static_assets_template():
    """創建靜態資源助手模板"""
    template_content = """{% macro url_for(path) %}{{ assets.url_for(path) }}{% endmacro %}"""
    
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'web', 'templates', 'static_assets.html')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    logger.info(f"創建靜態資源助手模板: {output_path}")

def main():
    """主函數"""
    # 設置日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/static_optimization.log'),
            logging.StreamHandler()
        ]
    )
    
    logger.info("啟動靜態資源優化腳本")
    
    # 獲取靜態資源路徑
    static_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'web', 'static')
    
    # 創建優化器
    optimizer = StaticResourceOptimizer(static_folder)
    
    # 執行優化
    start_time = time.time()
    results = optimizer.run()
    duration = time.time() - start_time
    
    # 創建靜態資源助手模板
    create_static_assets_template()
    
    # 記錄優化結果
    logger.info(f"靜態資源優化完成，耗時: {duration:.2f}秒")
    logger.info(f"優化CSS文件: {results['css_files']}個")
    logger.info(f"優化JS文件: {results['js_files']}個")
    logger.info(f"處理圖片文件: {results['image_files']}個")
    
    # 回傳結果
    return results

if __name__ == "__main__":
    main()
