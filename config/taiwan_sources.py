"""
台灣保險新聞來源配置
Taiwan Insurance News Sources Configuration

統一管理所有台灣保險相關新聞來源
"""

# 台灣保險專業新聞源
TAIWAN_INSURANCE_SOURCES = {
    # 保險專業類
    'insurance_professional': {
        'goodins': {
            'name': '保險雲雜誌',
            'base_url': 'https://www.goodins.life',
            'rss_url': None,
            'category': '保險專業',
            'description': '台灣保險業專業媒體，提供深度保險資訊',
            'priority': 'high',
            'keywords': ['保險', '保單', '理賠', '保費']
        },
        'rmim': {
            'name': '保險事業發展中心',
            'base_url': 'https://www.rmim.com.tw',
            'rss_url': None,
            'category': '保險研究',
            'description': '保險業發展研究與教育機構',
            'priority': 'high',
            'keywords': ['保險研究', '教育訓練', '證照']
        },
        'lia_roc': {
            'name': '中華民國人壽保險商業同業公會',
            'base_url': 'https://www.lia-roc.org.tw',
            'rss_url': None,
            'category': '保險公會',
            'description': '人壽保險業同業公會官方資訊',
            'priority': 'high',
            'keywords': ['人壽保險', '壽險', '公會']
        },
        'tii': {
            'name': '中華民國產物保險商業同業公會',
            'base_url': 'https://www.tii.org.tw',
            'rss_url': None,
            'category': '保險公會',
            'description': '產物保險業同業公會官方資訊',
            'priority': 'high',
            'keywords': ['產險', '車險', '火險']
        }
    },
    
    # 財經理財類
    'financial_media': {
        'udn_money': {
            'name': '經濟日報理財',
            'base_url': 'https://money.udn.com',
            'rss_url': 'https://money.udn.com/rssfeed/news/1001/5591?ch=fb_share',
            'category': '財經理財',
            'description': '經濟日報理財頻道，專業財經報導',
            'priority': 'high',
            'keywords': ['理財', '投資', '保險']
        },
        'ctee': {
            'name': '工商時報',
            'base_url': 'https://www.ctee.com.tw',
            'rss_url': 'https://www.ctee.com.tw/rss/ctee-fm.xml',
            'category': '財經新聞',
            'description': '台灣重要財經媒體',
            'priority': 'high',
            'keywords': ['財經', '金融', '保險']
        },
        'wealth': {
            'name': '財訊雜誌',
            'base_url': 'https://www.wealth.com.tw',
            'rss_url': None,
            'category': '財經雜誌',
            'description': '台灣財經雜誌權威',
            'priority': 'medium',
            'keywords': ['財經', '投資', '理財']
        },
        'businesstoday': {
            'name': '今周刊',
            'base_url': 'https://www.businesstoday.com.tw',
            'rss_url': None,
            'category': '商業雜誌',
            'description': '知名商業財經雜誌',
            'priority': 'medium',
            'keywords': ['商業', '投資', '保險']
        },
        'cw': {
            'name': '天下雜誌',
            'base_url': 'https://www.cw.com.tw',
            'rss_url': None,
            'category': '財經雜誌',
            'description': '台灣知名雜誌',
            'priority': 'medium',
            'keywords': ['財經', '政策', '社會']
        },
        'storm_finance': {
            'name': '風傳媒財經',
            'base_url': 'https://www.storm.mg/finance',
            'rss_url': 'https://www.storm.mg/feeds/finance',
            'category': '網路媒體',
            'description': '風傳媒財經頻道',
            'priority': 'medium',
            'keywords': ['財經', '政治', '保險']
        },
        'money101': {
            'name': 'Money101理財',
            'base_url': 'https://www.money101.com.tw',
            'rss_url': None,
            'category': '理財媒體',
            'description': '專業理財比較平台',
            'priority': 'medium',
            'keywords': ['理財', '保險', '比較']
        }
    },
    
    # 醫療長照類
    'healthcare_media': {
        'heho': {
            'name': 'Heho健康',
            'base_url': 'https://heho.com.tw',
            'rss_url': 'https://heho.com.tw/feed/',
            'category': '健康媒體',
            'description': '台灣健康資訊媒體',
            'priority': 'medium',
            'keywords': ['健康', '醫療', '長照']
        },
        'edh': {
            'name': '早安健康',
            'base_url': 'https://www.edh.tw',
            'rss_url': None,
            'category': '健康媒體',
            'description': '健康生活資訊平台',
            'priority': 'medium',
            'keywords': ['健康', '養生', '醫療']
        },
        'commonhealth': {
            'name': '康健雜誌',
            'base_url': 'https://www.commonhealth.com.tw',
            'rss_url': None,
            'category': '健康雜誌',
            'description': '台灣知名健康雜誌',
            'priority': 'medium',
            'keywords': ['健康', '醫療', '保健']
        }
    },
    
    # 政府機關類
    'government_sources': {
        'fsc': {
            'name': '金融監督管理委員會',
            'base_url': 'https://www.fsc.gov.tw',
            'rss_url': None,
            'category': '政府機關',
            'description': '金管會官方網站',
            'priority': 'critical',
            'keywords': ['金管會', '監理', '法規']
        },
        'insurance_bureau': {
            'name': '保險局',
            'base_url': 'https://www.ib.gov.tw',
            'rss_url': None,
            'category': '政府機關',
            'description': '保險局官方網站',
            'priority': 'critical',
            'keywords': ['保險局', '監理', '法規']
        },
        'banking_bureau': {
            'name': '銀行局',
            'base_url': 'https://www.banking.gov.tw',
            'rss_url': None,
            'category': '政府機關',
            'description': '銀行局官方網站',
            'priority': 'high',
            'keywords': ['銀行', '金融', '法規']
        },
        'mof': {
            'name': '財政部',
            'base_url': 'https://www.mof.gov.tw',
            'rss_url': None,
            'category': '政府機關',
            'description': '財政部官方網站',
            'priority': 'high',
            'keywords': ['財政', '稅務', '政策']
        },
        'mohw': {
            'name': '衛生福利部',
            'base_url': 'https://www.mohw.gov.tw',
            'rss_url': None,
            'category': '政府機關',
            'description': '衛福部官方網站',
            'priority': 'medium',
            'keywords': ['健保', '長照', '醫療']
        },
        'longtermcare': {
            'name': '長期照顧專區',
            'base_url': 'https://1966.gov.tw',
            'rss_url': None,
            'category': '政府專區',
            'description': '長照服務資源',
            'priority': 'medium',
            'keywords': ['長照', '失能', '照護']
        }
    },
    
    # RSS 新聞源
    'rss_sources': {
        'google_insurance_tw': {
            'name': 'Google新聞-台灣保險',
            'rss_url': 'https://news.google.com/rss/search?q=台灣+保險&hl=zh-TW&gl=TW&ceid=TW:zh-Hant',
            'category': 'RSS新聞',
            'description': 'Google新聞台灣保險關鍵字',
            'priority': 'high',
            'keywords': ['台灣', '保險']
        },
        'google_financial_tw': {
            'name': 'Google新聞-台灣金融',
            'rss_url': 'https://news.google.com/rss/search?q=台灣+金融+保險&hl=zh-TW&gl=TW&ceid=TW:zh-Hant',
            'category': 'RSS新聞',
            'description': 'Google新聞台灣金融保險',
            'priority': 'high',
            'keywords': ['台灣', '金融', '保險']
        },
        'google_healthcare_tw': {
            'name': 'Google新聞-台灣醫療',
            'rss_url': 'https://news.google.com/rss/search?q=台灣+醫療+保險&hl=zh-TW&gl=TW&ceid=TW:zh-Hant',
            'category': 'RSS新聞',
            'description': 'Google新聞台灣醫療保險',
            'priority': 'medium',
            'keywords': ['台灣', '醫療', '保險']
        },
        'google_longtermcare_tw': {
            'name': 'Google新聞-台灣長照',
            'rss_url': 'https://news.google.com/rss/search?q=台灣+長照+保險&hl=zh-TW&gl=TW&ceid=TW:zh-Hant',
            'category': 'RSS新聞',
            'description': 'Google新聞台灣長照保險',
            'priority': 'medium',
            'keywords': ['台灣', '長照', '保險']
        }
    }
}

# 台灣保險關鍵詞庫（擴充版）
TAIWAN_INSURANCE_KEYWORDS = {
    # 基本保險詞彙
    'basic_insurance': [
        '保險', '保費', '保單', '理賠', '投保', '承保', '續保', '退保',
        '保障', '保額', '保險金', '保險費', '保險期間', '保險人', '被保險人',
        '要保人', '受益人', '保險契約', '保險條款', '保險責任'
    ],
    
    # 保險類型
    'insurance_types': [
        '人壽保險', '壽險', '定期壽險', '終身壽險', '儲蓄險', '投資型保單',
        '產物保險', '產險', '車險', '機車險', '汽車險', '強制險', '任意險',
        '火災保險', '地震險', '颱風險', '住宅險', '旅遊險', '旅平險',
        '健康保險', '健康險', '醫療險', '癌症險', '重大疾病險', '手術險',
        '意外保險', '意外險', '傷害險', '失能險', '長照險', '年金險'
    ],
    
    # 台灣保險公司
    'taiwan_insurers': [
        # 壽險公司
        '南山人壽', '國泰人壽', '富邦人壽', '新光人壽', '台灣人壽',
        '中國信託', '第一金人壽', '兆豐人壽', '玉山人壽', '宏泰人壽',
        '保德信人壽', '安聯人壽', '三商美邦', '遠雄人壽', '康健人壽',
        '全球人壽', '友邦人壽', '台銀人壽', '合庫人壽', '元大人壽',
        
        # 產險公司
        '新安東京海上', '富邦產險', '國泰產險', '新光產險', '南山產險',
        '明台產險', '華南產險', '第一產險', '兆豐產險', '泰安產險',
        '和泰產險', '中央產險', '臺產', '旺旺友聯', '安達產險'
    ],
    
    # 監理機關
    'regulators': [
        '金管會', '保險局', '金融監督管理委員會', '保險監理',
        '金檢', '金融檢查', '裁罰', '糾正', '警告', '停業', '撤照'
    ],
    
    # 法規制度
    'regulations': [
        '保險法', '保險業法', '保險代理人', '保險經紀人', '保險公證人',
        'RBC', '清償能力', '資本適足率', '準備金', '責任準備金',
        'IFRS17', '會計準則', '精算', '保險精算', '風險管理'
    ],
    
    # 台灣特有制度
    'taiwan_specific': [
        '全民健保', '二代健保', '補充保費', '健保卡', '健保署',
        '勞保', '勞退', '勞工保險', '勞工退休金', '國民年金',
        '農保', '農民保險', '軍公教保險', '公保', '私校退撫'
    ],
    
    # 長照相關
    'long_term_care': [
        '長期照顧', '長照2.0', '失智症', '失能', '居家照護', '日照中心',
        '長照險', '長照給付', '照顧服務', '失能等級', 'ADL', 'IADL'
    ],
    
    # 保險科技
    'insurtech': [
        'InsurTech', '保險科技', '數位保險', '線上投保', 'AI理賠',
        '區塊鏈', '物聯網', 'IoT', '穿戴裝置', '遠距醫療'
    ],
    
    # 投資理財
    'investment': [
        '利變型', '分紅保單', '投資連結', '萬能壽險', '變額年金',
        '基金', '股票', '債券', '投資標的', '報酬率', '風險'
    ]
}

# 排除關鍵詞（避免誤判）
EXCLUDE_KEYWORDS = [
    '車保', '汽車保養', '保濕', '保養', '保健食品', '保鮮',
    '保溫', '保暖', '保密', '保護', '保存', '保持', '保守',
    '保證金', '保釋金', '保釋', '保外就醫', '保外候審'
]

def get_all_sources():
    """獲取所有新聞源"""
    all_sources = {}
    for category in TAIWAN_INSURANCE_SOURCES.values():
        all_sources.update(category)
    return all_sources

def get_sources_by_category(category_name):
    """根據分類獲取新聞源"""
    return TAIWAN_INSURANCE_SOURCES.get(category_name, {})

def get_sources_by_priority(priority):
    """根據優先級獲取新聞源"""
    sources = {}
    for category in TAIWAN_INSURANCE_SOURCES.values():
        for source_id, source_info in category.items():
            if source_info.get('priority') == priority:
                sources[source_id] = source_info
    return sources

def get_all_keywords():
    """獲取所有關鍵詞"""
    all_keywords = []
    for category in TAIWAN_INSURANCE_KEYWORDS.values():
        all_keywords.extend(category)
    return all_keywords

def is_insurance_related(text):
    """判斷文本是否與保險相關"""
    text_lower = text.lower()
    
    # 檢查排除關鍵詞
    for exclude_word in EXCLUDE_KEYWORDS:
        if exclude_word in text_lower:
            return False
    
    # 檢查保險關鍵詞
    all_keywords = get_all_keywords()
    for keyword in all_keywords:
        if keyword in text_lower:
            return True
    
    return False
