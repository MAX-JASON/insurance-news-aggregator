/**
 * Bootstrap Modal 修復與替代方案
 * 用於解決 Bootstrap Modal 組件加載失敗或配置錯誤的問題
 */

(function() {
    // 檢查是否已經有modal-polyfill標記，避免重複加載
    if (window.modalPolyfillLoaded) {
        return;
    }
    
    console.log('Modal修復工具已載入');
    
    // 標記為已加載
    window.modalPolyfillLoaded = true;
    
    // 在頁面載入完成後檢查Bootstrap Modal
    window.addEventListener('load', function() {
        setTimeout(checkAndFixBootstrapModal, 500);
    });
    
    // 檢查並修復Bootstrap Modal
    function checkAndFixBootstrapModal() {
        // 檢查是否已正確加載Bootstrap Modal
        if (typeof bootstrap === 'undefined' || !bootstrap.Modal || !bootstrap.Modal.prototype.show) {
            console.warn('檢測到Bootstrap Modal組件問題，啟用替代方案');
            
            // 創建一個簡易的Modal替代方案
            createModalPolyfill();
        } else {
            // Bootstrap Modal 正確加載，但可能有配置問題
            patchExistingBootstrapModal();
        }
    }
    
    // 創建Modal替代方案
    function createModalPolyfill() {
        // 創建Bootstrap命名空間（如果不存在）
        if (typeof bootstrap === 'undefined') {
            window.bootstrap = {};
        }
        
        // 簡易Modal實現
        window.bootstrap.Modal = function(element, options) {
            this.element = typeof element === 'string' ? document.querySelector(element) : element;
            this.options = options || {};
            this.backdrop = this.options.backdrop !== false;
            this.keyboard = this.options.keyboard !== false;
            this._isShown = false;
            this._backdropElement = null;
            
            // 初始化
            this._init();
        };
        
        // 原型方法
        window.bootstrap.Modal.prototype = {
            _init: function() {
                // 添加必要的事件監聽器
                const self = this;
                
                // 處理ESC鍵關閉
                if (this.keyboard) {
                    document.addEventListener('keydown', function(event) {
                        if (event.key === 'Escape' && self._isShown) {
                            self.hide();
                        }
                    });
                }
                
                // 點擊關閉按鈕
                const closeButtons = this.element.querySelectorAll('[data-bs-dismiss="modal"]');
                closeButtons.forEach(function(button) {
                    button.addEventListener('click', function() {
                        self.hide();
                    });
                });
                
                // 點擊背景關閉
                if (this.backdrop !== 'static') {
                    this.element.addEventListener('click', function(event) {
                        if (event.target === self.element) {
                            self.hide();
                        }
                    });
                }
            },
            
            show: function() {
                if (this._isShown) return;
                
                // 添加顯示類別
                this.element.classList.add('show');
                this.element.style.display = 'block';
                this.element.setAttribute('aria-modal', 'true');
                this.element.removeAttribute('aria-hidden');
                
                // 添加背景遮罩
                if (this.backdrop) {
                    this._createBackdrop();
                }
                
                // 防止頁面滾動
                document.body.classList.add('modal-open');
                document.body.style.overflow = 'hidden';
                document.body.style.paddingRight = '15px';
                
                this._isShown = true;
                
                // 觸發顯示事件
                this._triggerEvent('shown.bs.modal');
            },
            
            hide: function() {
                if (!this._isShown) return;
                
                // 移除顯示類別
                this.element.classList.remove('show');
                this.element.style.display = 'none';
                this.element.setAttribute('aria-hidden', 'true');
                this.element.removeAttribute('aria-modal');
                
                // 移除背景遮罩
                this._removeBackdrop();
                
                // 恢復頁面滾動
                document.body.classList.remove('modal-open');
                document.body.style.overflow = '';
                document.body.style.paddingRight = '';
                
                this._isShown = false;
                
                // 觸發隱藏事件
                this._triggerEvent('hidden.bs.modal');
            },
            
            toggle: function() {
                if (this._isShown) {
                    this.hide();
                } else {
                    this.show();
                }
            },
            
            _createBackdrop: function() {
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);
                
                this._backdropElement = backdrop;
                
                // 處理背景點擊
                if (this.backdrop !== 'static') {
                    backdrop.addEventListener('click', () => this.hide());
                }
            },
            
            _removeBackdrop: function() {
                if (this._backdropElement) {
                    document.body.removeChild(this._backdropElement);
                    this._backdropElement = null;
                }
            },
            
            _triggerEvent: function(eventName) {
                const event = new Event(eventName, { bubbles: true, cancelable: true });
                this.element.dispatchEvent(event);
            }
        };
        
        // 處理頁面上已有的Modal元素
        document.querySelectorAll('[data-bs-toggle="modal"]').forEach(function(trigger) {
            const targetId = trigger.getAttribute('data-bs-target') || trigger.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                const modal = new bootstrap.Modal(targetElement);
                
                trigger.addEventListener('click', function(event) {
                    event.preventDefault();
                    modal.show();
                });
            }
        });
        
        console.log('Modal替代方案已創建完成');
    }
    
    // 修補現有的Bootstrap Modal
    function patchExistingBootstrapModal() {
        const originalModal = bootstrap.Modal;
        
        // 保存原始方法的引用
        const originalInitialize = originalModal.prototype._initializeBackDrop;
        
        // 修補_initializeBackDrop方法
        bootstrap.Modal.prototype._initializeBackDrop = function() {
            try {
                // 嘗試調用原始方法
                if (typeof originalInitialize === 'function') {
                    return originalInitialize.apply(this, arguments);
                }
                
                // 如果原始方法不存在或不是函數，使用替代實現
                console.warn('Bootstrap Modal _initializeBackDrop方法不可用，使用替代實現');
                
                // 簡單的backdrop實現
                const backdropElement = document.createElement('div');
                backdropElement.className = 'modal-backdrop fade show';
                document.body.appendChild(backdropElement);
                
                this._backdrop = {
                    element: backdropElement,
                    dispose: function() {
                        document.body.removeChild(backdropElement);
                    }
                };
                
                return this._backdrop;
            } catch (error) {
                console.error('修復Modal背景時發生錯誤:', error);
                // 返回一個簡單的對象以避免進一步的錯誤
                return { element: null, dispose: function() {} };
            }
        };
        
        console.log('已修補現有Bootstrap Modal');
    }
    
    // 公開API
    window.fixBootstrapModals = checkAndFixBootstrapModal;
})();
