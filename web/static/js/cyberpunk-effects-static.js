/**
 * 賽博朋克靜態效果系統
 * Cyberpunk Static Effects System - No Animations
 * 專為業務員工作環境設計，無動態效果干擾
 */

class CyberpunkStaticSystem {
    constructor() {
        this.isInitialized = false;
        this.init();
    }
    
    init() {
        if (this.isInitialized) return;
        
        console.log('🤖 賽博朋克靜態系統載入中...');
        
        this.setupTheme();
        this.enhanceUI();
        this.bindEvents();
        
        this.isInitialized = true;
        console.log('✅ 賽博朋克靜態系統已啟動');
    }
    
    setupTheme() {
        // 確保body有賽博朋克主題類別
        document.body.classList.add('cyberpunk-theme');
        
        // 移除所有現有的動畫粒子
        const existingParticles = document.querySelectorAll('.particles-container, #cyber-particles-canvas');
        existingParticles.forEach(element => element.remove());
    }
    
    enhanceUI() {
        // 增強卡片樣式
        this.enhanceCards();
        
        // 增強按鈕樣式
        this.enhanceButtons();
        
        // 增強表格樣式
        this.enhanceTables();
        
        // 增強導航欄
        this.enhanceNavbar();
    }
    
    enhanceCards() {
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.classList.add('cyber-card');
        });
        
        const newsCards = document.querySelectorAll('.news-card');
        newsCards.forEach(card => {
            card.classList.add('cyber-news-card');
        });
    }
    
    enhanceButtons() {
        const buttons = document.querySelectorAll('.btn-primary, .btn-secondary');
        buttons.forEach(btn => {
            btn.classList.add('btn-cyber');
        });
        
        const dangerButtons = document.querySelectorAll('.btn-danger');
        dangerButtons.forEach(btn => {
            btn.classList.add('btn-cyber', 'btn-cyber-danger');
        });
        
        const successButtons = document.querySelectorAll('.btn-success');
        successButtons.forEach(btn => {
            btn.classList.add('btn-cyber', 'btn-cyber-success');
        });
    }
    
    enhanceTables() {
        const tables = document.querySelectorAll('.table');
        tables.forEach(table => {
            table.classList.add('cyber-table');
        });
    }
    
    enhanceNavbar() {
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            navbar.classList.add('cyber-nav');
        }
    }
    
    bindEvents() {
        // 主題切換功能
        this.setupThemeSwitcher();
        
        // 表單增強
        this.enhanceForms();
        
        // 工具提示增強
        this.enhanceTooltips();
    }
    
    setupThemeSwitcher() {
        const themeSwitchers = document.querySelectorAll('.theme-switcher');
        themeSwitchers.forEach(switcher => {
            switcher.addEventListener('click', (e) => {
                e.preventDefault();
                const theme = switcher.dataset.theme;
                
                if (theme === 'cyberpunk') {
                    document.body.className = 'cyberpunk-theme';
                    console.log('🤖 已切換至賽博朋克主題');
                } else {
                    document.body.className = theme ? `theme-${theme}` : '';
                    console.log(`🎨 已切換至${theme}主題`);
                }
            });
        });
    }
    
    enhanceForms() {
        const inputs = document.querySelectorAll('.form-control');
        inputs.forEach(input => {
            input.classList.add('cyber-input');
        });
        
        const selects = document.querySelectorAll('.form-select');
        selects.forEach(select => {
            select.classList.add('cyber-input');
        });
    }
    
    enhanceTooltips() {
        // 為賽博朋克元素添加工具提示
        const cyberElements = document.querySelectorAll('[data-cyber-tooltip]');
        cyberElements.forEach(element => {
            const tooltip = element.dataset.cyberTooltip;
            element.title = `🤖 ${tooltip}`;
        });
    }
    
    // 靜態發光效果（純CSS，無動畫）
    addStaticGlow(element, color = '#00D4FF') {
        element.style.boxShadow = `0 0 10px ${color}40, inset 0 0 10px ${color}20`;
        element.style.border = `1px solid ${color}60`;
    }
    
    // 移除發光效果
    removeStaticGlow(element) {
        element.style.boxShadow = '';
        element.style.border = '';
    }
    
    // 靜態高亮文字
    highlightText(element, color = '#00FFFF') {
        element.style.color = color;
        element.style.textShadow = `0 0 5px ${color}80`;
    }
    
    // 工具函數：創建賽博朋克風格的通知
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert cyber-alert cyber-alert-${type}`;
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '9999';
        notification.style.maxWidth = '400px';
        
        const icon = this.getNotificationIcon(type);
        notification.innerHTML = `
            <i class="${icon} me-2"></i>
            ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;
        
        document.body.appendChild(notification);
        
        // 自動移除通知（3秒後）
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 3000);
    }
    
    getNotificationIcon(type) {
        const icons = {
            'info': 'fas fa-info-circle',
            'success': 'fas fa-check-circle',
            'warning': 'fas fa-exclamation-triangle',
            'danger': 'fas fa-exclamation-circle'
        };
        return icons[type] || icons['info'];
    }
    
    // 工具函數：創建賽博朋克風格的確認對話框
    showConfirmDialog(message, onConfirm, onCancel) {
        const overlay = document.createElement('div');
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100%';
        overlay.style.height = '100%';
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
        overlay.style.zIndex = '10000';
        overlay.style.display = 'flex';
        overlay.style.alignItems = 'center';
        overlay.style.justifyContent = 'center';
        
        const dialog = document.createElement('div');
        dialog.className = 'cyber-card';
        dialog.style.maxWidth = '400px';
        dialog.style.margin = '0';
        
        dialog.innerHTML = `
            <h5 class="text-cyber-primary mb-3">🤖 確認操作</h5>
            <p class="mb-4">${message}</p>
            <div class="d-flex gap-2 justify-content-end">
                <button class="btn btn-cyber btn-cyber-danger" onclick="window.cyberConfirmCancel()">取消</button>
                <button class="btn btn-cyber" onclick="window.cyberConfirmOk()">確認</button>
            </div>
        `;
        
        overlay.appendChild(dialog);
        document.body.appendChild(overlay);
        
        // 設置全域回調函數
        window.cyberConfirmOk = () => {
            overlay.remove();
            delete window.cyberConfirmOk;
            delete window.cyberConfirmCancel;
            if (onConfirm) onConfirm();
        };
        
        window.cyberConfirmCancel = () => {
            overlay.remove();
            delete window.cyberConfirmOk;
            delete window.cyberConfirmCancel;
            if (onCancel) onCancel();
        };
    }
    
    // 工具函數：格式化賽博朋克風格的數字
    formatCyberNumber(number) {
        if (number >= 1000000) {
            return (number / 1000000).toFixed(1) + 'M';
        } else if (number >= 1000) {
            return (number / 1000).toFixed(1) + 'K';
        }
        return number.toString();
    }
    
    // 工具函數：創建賽博朋克風格的載入指示器
    showLoadingIndicator(message = '載入中...') {
        const loader = document.createElement('div');
        loader.id = 'cyber-loader';
        loader.style.position = 'fixed';
        loader.style.top = '50%';
        loader.style.left = '50%';
        loader.style.transform = 'translate(-50%, -50%)';
        loader.style.zIndex = '10001';
        
        loader.innerHTML = `
            <div class="cyber-card text-center">
                <div class="spinner-border text-cyber-primary mb-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="text-cyber-primary mb-0">🤖 ${message}</p>
            </div>
        `;
        
        document.body.appendChild(loader);
        return loader;
    }
    
    // 隱藏載入指示器
    hideLoadingIndicator() {
        const loader = document.getElementById('cyber-loader');
        if (loader) {
            loader.remove();
        }
    }
}

// 賽博朋克音效系統 - 靜態版本（僅提供API，不自動播放）
class CyberpunkSoundSystem {
    constructor() {
        this.audioContext = null;
        this.sounds = new Map();
        this.isEnabled = false; // 預設禁用音效
    }
    
    // 啟用音效（需要用戶手動啟用）
    enable() {
        if (!this.audioContext) {
            try {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                this.isEnabled = true;
                console.log('🔊 賽博朋克音效系統已啟用');
            } catch (e) {
                console.warn('⚠️ 音效系統不受支持');
            }
        }
    }
    
    // 禁用音效
    disable() {
        this.isEnabled = false;
        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }
        console.log('🔇 賽博朋克音效系統已禁用');
    }
    
    // 播放音效（僅在啟用時）
    playSound(type) {
        if (!this.isEnabled || !this.audioContext) return;
        
        // 這裡可以添加實際的音效播放邏輯
        // 目前只記錄日誌
        console.log(`🎵 播放音效: ${type}`);
    }
}

// 全域實例
let cyberpunkSystem;
let soundSystem;

// DOM載入完成後初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化靜態賽博朋克系統
    cyberpunkSystem = new CyberpunkStaticSystem();
    
    // 初始化音效系統（但保持禁用狀態）
    soundSystem = new CyberpunkSoundSystem();
    
    // 在全域範圍提供系統實例
    window.cyberpunkSystem = cyberpunkSystem;
    window.soundSystem = soundSystem;
    
    console.log('🤖 賽博朋克靜態界面系統已完全載入 - 無動畫干擾版本');
});

// 禁用所有現有的動畫和過渡效果
function disableAllAnimations() {
    const style = document.createElement('style');
    style.innerHTML = `
        *, *::before, *::after {
            animation-duration: 0s !important;
            animation-delay: 0s !important;
            transition-duration: 0s !important;
            transition-delay: 0s !important;
        }
    `;
    document.head.appendChild(style);
}

// 立即禁用動畫
disableAllAnimations();
