import os
import sys

# 添加當前目錄到路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("正在啟動應用程式...")

try:
    # 嘗試運行 debug_app.py
    exec(open('debug_app.py').read())
except Exception as e:
    print(f"啟動失敗: {e}")
    
    # 如果失敗，嘗試最基本的 Flask 應用
    try:
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/')
        def home():
            return '''
            <h1>🎉 台灣保險新聞聚合器</h1>
            <p>應用程式已成功啟動！</p>
            <ul>
                <li><a href="/feedback">反饋頁面</a></li>
                <li><a href="/test">測試頁面</a></li>
            </ul>
            '''
        
        @app.route('/test')
        def test():
            return '<h1>測試頁面</h1><p>系統運行正常</p><a href="/">返回首頁</a>'
            
        @app.route('/feedback')
        def feedback():
            return '''
            <h1>反饋頁面</h1>
            <p>反饋功能正在運行中</p>
            <form method="post" action="/feedback/submit">
                <p>您的反饋：<br><textarea name="message" rows="4" cols="50"></textarea></p>
                <p><input type="submit" value="提交反饋"></p>
            </form>
            <a href="/">返回首頁</a>
            '''
            
        @app.route('/feedback/submit', methods=['POST'])
        def submit():
            return '<h1>感謝您的反饋！</h1><a href="/">返回首頁</a>'
        
        print("啟動基本 Flask 應用...")
        app.run(host='127.0.0.1', port=5000, debug=True)
        
    except Exception as e2:
        print(f"基本應用也無法啟動: {e2}")
