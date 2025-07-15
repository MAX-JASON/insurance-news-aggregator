#!/usr/bin/env python3
"""
前端標籤分頁功能驗證腳本
"""

import os
import re
from pathlib import Path

def check_template_file(file_path):
    """檢查模板文件的標籤實現"""
    results = {
        'file': str(file_path),
        'has_tabs': False,
        'tab_type': None,
        'accessibility_issues': [],
        'missing_attributes': []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查是否有標籤
        if any(pattern in content for pattern in ['nav-tabs', 'nav-pills', 'data-bs-toggle']):
            results['has_tabs'] = True
            
            # 確定標籤類型
            if 'nav-tabs' in content:
                results['tab_type'] = 'Bootstrap Tabs'
            elif 'nav-pills' in content:
                results['tab_type'] = 'Bootstrap Pills'
            elif 'data-bs-toggle="list"' in content:
                results['tab_type'] = 'List Group'
            
            # 檢查無障礙屬性
            tab_buttons = re.findall(r'<[^>]*data-bs-toggle=["\'][^"\']*["\'][^>]*>', content)
            
            for button in tab_buttons:
                if 'aria-selected' not in button:
                    results['missing_attributes'].append('aria-selected')
                if 'aria-controls' not in button:
                    results['missing_attributes'].append('aria-controls')
                if 'role="tab"' not in button:
                    results['missing_attributes'].append('role="tab"')
            
            # 檢查標籤面板
            tab_panes = re.findall(r'<[^>]*class=["\'][^"\']*tab-pane[^"\']*["\'][^>]*>', content)
            
            for pane in tab_panes:
                if 'aria-labelledby' not in pane:
                    results['missing_attributes'].append('aria-labelledby')
                if 'tabindex' not in pane:
                    results['missing_attributes'].append('tabindex')
                if 'role="tabpanel"' not in pane:
                    results['missing_attributes'].append('role="tabpanel"')
            
            # 移除重複項
            results['missing_attributes'] = list(set(results['missing_attributes']))
            
    except Exception as e:
        results['error'] = str(e)
    
    return results

def check_javascript_file(file_path):
    """檢查JavaScript文件的標籤處理"""
    results = {
        'file': str(file_path),
        'has_tab_handling': False,
        'has_accessibility_support': False,
        'has_keyboard_navigation': False,
        'has_error_handling': False
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查標籤處理
        if any(pattern in content for pattern in ['tab', 'Tab', 'data-bs-toggle']):
            results['has_tab_handling'] = True
        
        # 檢查無障礙支持
        if any(pattern in content for pattern in ['aria-', 'role=', 'tabindex']):
            results['has_accessibility_support'] = True
        
        # 檢查鍵盤導航
        if any(pattern in content for pattern in ['keydown', 'ArrowLeft', 'ArrowRight', 'Enter', 'Space']):
            results['has_keyboard_navigation'] = True
        
        # 檢查錯誤處理
        if any(pattern in content for pattern in ['try', 'catch', 'error', 'Error']):
            results['has_error_handling'] = True
            
    except Exception as e:
        results['error'] = str(e)
    
    return results

def main():
    """主函數"""
    base_dir = Path(__file__).parent
    web_dir = base_dir / 'web'
    
    print("🔍 前端標籤分頁功能驗證報告")
    print("=" * 60)
    
    # 檢查模板文件
    print("\n📄 模板文件檢查:")
    print("-" * 40)
    
    template_files = []
    for root, dirs, files in os.walk(web_dir / 'templates'):
        for file in files:
            if file.endswith('.html'):
                template_files.append(Path(root) / file)
    
    template_issues = 0
    for template_file in template_files:
        result = check_template_file(template_file)
        
        if result['has_tabs']:
            status = "✅" if not result['missing_attributes'] else "⚠️"
            print(f"{status} {result['file']}")
            print(f"   類型: {result['tab_type']}")
            
            if result['missing_attributes']:
                template_issues += 1
                print(f"   缺少屬性: {', '.join(result['missing_attributes'])}")
            else:
                print("   ✅ 無障礙屬性完整")
    
    # 檢查JavaScript文件
    print("\n📜 JavaScript文件檢查:")
    print("-" * 40)
    
    js_files = []
    static_dir = web_dir / 'static' / 'js'
    if static_dir.exists():
        for file in static_dir.glob('*.js'):
            js_files.append(file)
    
    js_issues = 0
    for js_file in js_files:
        result = check_javascript_file(js_file)
        
        if result['has_tab_handling']:
            features = []
            if result['has_accessibility_support']:
                features.append("無障礙")
            if result['has_keyboard_navigation']:
                features.append("鍵盤導航")
            if result['has_error_handling']:
                features.append("錯誤處理")
            
            status = "✅" if len(features) >= 2 else "⚠️"
            if len(features) < 2:
                js_issues += 1
            
            print(f"{status} {result['file']}")
            print(f"   功能: {', '.join(features) if features else '基本標籤處理'}")
    
    # 檢查關鍵文件
    print("\n🔧 關鍵修復文件檢查:")
    print("-" * 40)
    
    key_files = [
        'web/static/js/tab-fixes.js',
        'web/static/js/tab-manager.js'
    ]
    
    missing_files = 0
    for key_file in key_files:
        # 修復路徑檢查
        file_path = base_dir / key_file.replace('/', os.sep)
        if file_path.exists():
            print(f"✅ {key_file}")
            # 檢查文件大小
            size = file_path.stat().st_size
            print(f"   文件大小: {size:,} bytes")
        else:
            missing_files += 1
            print(f"❌ {key_file} (缺失)")
    
    # 總結
    print("\n📊 檢查總結:")
    print("-" * 40)
    
    total_issues = template_issues + js_issues + missing_files
    
    if total_issues == 0:
        print("🎉 所有標籤分頁功能已正確實現！")
        print("✅ 模板文件無障礙屬性完整")
        print("✅ JavaScript功能齊全")
        print("✅ 關鍵修復文件存在")
    else:
        print(f"⚠️  發現 {total_issues} 個問題需要解決")
        if template_issues > 0:
            print(f"   - {template_issues} 個模板文件缺少無障礙屬性")
        if js_issues > 0:
            print(f"   - {js_issues} 個JavaScript文件功能不完整")
        if missing_files > 0:
            print(f"   - {missing_files} 個關鍵文件缺失")
    
    print("\n建議:")
    print("1. 確保所有頁面都載入 tab-fixes.js")
    print("2. 測試鍵盤導航功能")
    print("3. 使用螢幕閱讀器驗證無障礙訪問")
    print("4. 檢查不同瀏覽器的兼容性")

if __name__ == "__main__":
    main()
