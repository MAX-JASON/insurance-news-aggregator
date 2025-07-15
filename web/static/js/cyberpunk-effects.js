/**
 * 賽博朋克粒子效果系統
 * Cyberpunk Particle Effects System
 */

class CyberpunkParticleSystem {
    constructor() {
        this.particles = [];
        this.canvas = null;
        this.ctx = null;
        this.animationId = null;
        this.isRunning = false;
        
        this.init();
    }
    
    init() {
        this.createCanvas();
        this.createHTMLParticles();
        this.bindEvents();
        this.start();
    }
    
    createCanvas() {
        // 創建canvas用於複雜動畫
        this.canvas = document.createElement('canvas');
        this.canvas.id = 'cyber-particles-canvas';
        this.canvas.style.position = 'fixed';
        this.canvas.style.top = '0';
        this.canvas.style.left = '0';
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
        this.canvas.style.pointerEvents = 'none';
        this.canvas.style.zIndex = '-1';
        this.canvas.style.opacity = '0.6';
        
        document.body.appendChild(this.canvas);
        this.ctx = this.canvas.getContext('2d');
        this.resize();
    }
    
    createHTMLParticles() {
        // 創建HTML粒子容器
        const container = document.createElement('div');
        container.className = 'particles-container';
        document.body.appendChild(container);
        
        // 生成不同類型的玻璃粒子
        // 大粒子 - 5個
        for (let i = 0; i < 5; i++) {
            this.createFloatingParticle(container, 'large');
        }
        
        // 中粒子 - 10個
        for (let i = 0; i < 10; i++) {
            this.createFloatingParticle(container, 'medium');
        }
        
        // 小粒子 - 20個
        for (let i = 0; i < 20; i++) {
            this.createFloatingParticle(container, 'small');
        }
    }
    
    createFloatingParticle(container, size = 'medium') {
        const particle = document.createElement('div');
        particle.className = `particle ${size}`;
        
        // 根據大小設置屬性
        const sizeMap = {
            'large': { min: 6, max: 10, colors: ['#00FFFF', '#00D4FF'] },
            'medium': { min: 4, max: 6, colors: ['#8B5FBF', '#FF073A'] },
            'small': { min: 2, max: 4, colors: ['#39FF14', '#FF8C00'] }
        };
        
        const config = sizeMap[size];
        const particleSize = Math.random() * (config.max - config.min) + config.min;
        const left = Math.random() * 100;
        const top = Math.random() * 100;
        
        particle.style.width = `${particleSize}px`;
        particle.style.height = `${particleSize}px`;
        particle.style.left = `${left}%`;
        particle.style.top = `${top}%`;
        // 禁用所有動畫
        particle.style.animation = 'none';
        
        // 設置顏色
        const color = config.colors[Math.floor(Math.random() * config.colors.length)];
        particle.style.setProperty('--particle-color', color);
        
        container.appendChild(particle);
        
        // 移除隨機重新生成，保持固定位置
    }
    
    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }
    
    bindEvents() {
        window.addEventListener('resize', () => this.resize());
        
        // 禁用滑鼠移動和點擊特效，避免分散注意力
        /*
        document.addEventListener('mousemove', (e) => {
            this.createMouseTrail(e.clientX, e.clientY);
        });
        
        document.addEventListener('click', (e) => {
            this.createClickEffect(e.clientX, e.clientY);
        });
        */
    }
    
    createMouseTrail(x, y) {
        // 創建滑鼠軌跡粒子
        if (Math.random() > 0.8) {
            const trail = document.createElement('div');
            trail.style.position = 'fixed';
            trail.style.left = x + 'px';
            trail.style.top = y + 'px';
            trail.style.width = '3px';
            trail.style.height = '3px';
            trail.style.background = '#00FFFF';
            trail.style.borderRadius = '50%';
            trail.style.pointerEvents = 'none';
            trail.style.zIndex = '999';
            trail.style.boxShadow = '0 0 10px #00FFFF';
            trail.style.transition = 'all 0.5s ease-out';
            
            document.body.appendChild(trail);
            
            setTimeout(() => {
                trail.style.opacity = '0';
                trail.style.transform = 'scale(0)';
                setTimeout(() => trail.remove(), 500);
            }, 10);
        }
    }
    
    createClickEffect(x, y) {
        // 創建點擊波紋效果
        const ripple = document.createElement('div');
        ripple.style.position = 'fixed';
        ripple.style.left = (x - 25) + 'px';
        ripple.style.top = (y - 25) + 'px';
        ripple.style.width = '50px';
        ripple.style.height = '50px';
        ripple.style.border = '2px solid #00D4FF';
        ripple.style.borderRadius = '50%';
        ripple.style.pointerEvents = 'none';
        ripple.style.zIndex = '999';
        ripple.style.animation = 'clickRipple 0.6s ease-out forwards';
        
        document.body.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
        
        // 添加CSS動畫
        if (!document.getElementById('click-ripple-style')) {
            const style = document.createElement('style');
            style.id = 'click-ripple-style';
            style.textContent = `
                @keyframes clickRipple {
                    0% {
                        transform: scale(0);
                        opacity: 1;
                    }
                    100% {
                        transform: scale(2);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    start() {
        if (this.isRunning) return;
        this.isRunning = true;
        // 只繪製一次靜態效果，不需要持續動畫
        this.draw();
    }
    
    stop() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
        this.isRunning = false;
    }
    
    animate() {
        // 禁用動畫循環，保持靜態顯示
        // this.draw();
        // this.animationId = requestAnimationFrame(() => this.animate());
    }
    
    draw() {
        if (!this.ctx) return;
        
        // 清除畫布
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 繪製動態網格線
        this.drawDynamicGrid();
        
        // 繪製數據流
        this.drawDataStream();
    }
    
    drawDynamicGrid() {
        const gridSize = 50;
        
        // 靜態網格，移除動態效果
        this.ctx.strokeStyle = 'rgba(0, 212, 255, 0.1)';
        this.ctx.lineWidth = 1;
        
        // 垂直線 - 固定位置
        for (let x = 0; x < this.canvas.width; x += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }
        
        // 水平線 - 固定位置
        for (let y = 0; y < this.canvas.height; y += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }
    }
    
    drawDataStream() {
        // 移除動態數據流，繪製靜態線條
        for (let i = 0; i < 5; i++) {
            const y = (this.canvas.height / 5) * i;
            const opacity = 0.3;
            
            this.ctx.strokeStyle = `rgba(57, 255, 20, ${opacity})`;
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();
            
            // 靜態直線
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }
    }
}

/**
 * 賽博朋克UI增強效果
 */
class CyberpunkUIEnhancer {
    constructor() {
        this.init();
    }
    
    init() {
        this.addHoverEffects();
        this.addScrollEffects();
        this.addLoadingEffects();
        this.addTypingEffect();
    }
    
    addHoverEffects() {
        // 為卡片添加懸停效果
        document.addEventListener('mouseover', (e) => {
            if (e.target.closest('.glass-card, .news-card')) {
                const card = e.target.closest('.glass-card, .news-card');
                this.addCardGlow(card);
            }
        });
        
        document.addEventListener('mouseout', (e) => {
            if (e.target.closest('.glass-card, .news-card')) {
                const card = e.target.closest('.glass-card, .news-card');
                this.removeCardGlow(card);
            }
        });
    }
    
    addCardGlow(card) {
        card.style.boxShadow = `
            0 8px 32px rgba(31, 38, 135, 0.37),
            0 0 30px rgba(0, 212, 255, 0.3),
            inset 0 0 20px rgba(255, 255, 255, 0.05)
        `;
    }
    
    removeCardGlow(card) {
        card.style.boxShadow = `0 8px 32px rgba(31, 38, 135, 0.37)`;
    }
    
    addScrollEffects() {
        // 滾動視差效果
        window.addEventListener('scroll', () => {
            const scrollY = window.scrollY;
            const particles = document.querySelectorAll('.particle');
            
            particles.forEach((particle, index) => {
                const speed = (index % 3 + 1) * 0.5;
                particle.style.transform = `translateY(${scrollY * speed}px)`;
            });
        });
    }
    
    addLoadingEffects() {
        // 為按鈕添加載入效果
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('neon-btn')) {
                this.addButtonLoadingEffect(e.target);
            }
        });
    }
    
    addButtonLoadingEffect(button) {
        const originalText = button.textContent;
        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        
        // 創建載入動畫
        const loader = document.createElement('div');
        loader.style.position = 'absolute';
        loader.style.top = '0';
        loader.style.left = '-100%';
        loader.style.width = '100%';
        loader.style.height = '100%';
        loader.style.background = 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent)';
        loader.style.animation = 'buttonScan 1s ease-in-out';
        
        button.appendChild(loader);
        
        // 添加CSS動畫
        if (!document.getElementById('button-scan-style')) {
            const style = document.createElement('style');
            style.id = 'button-scan-style';
            style.textContent = `
                @keyframes buttonScan {
                    0% { left: -100%; }
                    100% { left: 100%; }
                }
            `;
            document.head.appendChild(style);
        }
        
        setTimeout(() => {
            loader.remove();
        }, 1000);
    }
    
    addTypingEffect() {
        // 為標題添加打字機效果
        const titles = document.querySelectorAll('[data-typing]');
        titles.forEach(title => {
            const text = title.textContent;
            title.textContent = '';
            this.typeText(title, text, 50);
        });
    }
    
    typeText(element, text, speed) {
        let i = 0;
        const timer = setInterval(() => {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
            } else {
                clearInterval(timer);
            }
        }, speed);
    }
}

/**
 * 賽博朋克音效系統
 */
class CyberpunkSoundSystem {
    constructor() {
        this.sounds = {};
        this.enabled = false;
        this.init();
    }
    
    init() {
        // 檢查用戶是否允許音效
        this.checkAudioPermission();
        
        if (this.enabled) {
            this.loadSounds();
            this.bindSoundEvents();
        }
    }
    
    checkAudioPermission() {
        // 簡單檢查，實際應用中可能需要用戶明確同意
        this.enabled = localStorage.getItem('cyberpunk-sound-enabled') === 'true';
    }
    
    loadSounds() {
        // 使用Web Audio API創建音效
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        
        // 按鈕點擊音效
        this.sounds.click = this.createBeepSound(800, 0.1);
        this.sounds.hover = this.createBeepSound(600, 0.05);
        this.sounds.notification = this.createBeepSound(1000, 0.2);
    }
    
    createBeepSound(frequency, duration) {
        return () => {
            if (!this.enabled) return;
            
            const oscillator = this.audioContext.createOscillator();
            const gainNode = this.audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            
            oscillator.frequency.value = frequency;
            oscillator.type = 'square';
            
            gainNode.gain.setValueAtTime(0.1, this.audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration);
            
            oscillator.start(this.audioContext.currentTime);
            oscillator.stop(this.audioContext.currentTime + duration);
        };
    }
    
    bindSoundEvents() {
        // 按鈕點擊音效
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('neon-btn')) {
                this.sounds.click();
            }
        });
        
        // 懸停音效
        document.addEventListener('mouseover', (e) => {
            if (e.target.classList.contains('neon-btn')) {
                this.sounds.hover();
            }
        });
    }
    
    enableSound() {
        this.enabled = true;
        localStorage.setItem('cyberpunk-sound-enabled', 'true');
        this.loadSounds();
        this.bindSoundEvents();
    }
    
    disableSound() {
        this.enabled = false;
        localStorage.setItem('cyberpunk-sound-enabled', 'false');
    }
}

// 初始化系統
document.addEventListener('DOMContentLoaded', () => {
    // 初始化粒子系統
    window.cyberpunkParticles = new CyberpunkParticleSystem();
    
    // 初始化UI增強
    window.cyberpunkUI = new CyberpunkUIEnhancer();
    
    // 初始化音效系統
    window.cyberpunkSound = new CyberpunkSoundSystem();
    
    console.log('🔮 Cyberpunk systems initialized');
});

// 導出供外部使用
window.CyberpunkParticleSystem = CyberpunkParticleSystem;
window.CyberpunkUIEnhancer = CyberpunkUIEnhancer;
window.CyberpunkSoundSystem = CyberpunkSoundSystem;
