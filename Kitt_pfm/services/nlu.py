"""Natural Language Understanding for KITT PFM.

Parses casual Chinese/Japanese/English sentences into structured transaction data.
Phase 1: Rule-based parser. Phase 2: LLM upgrade.
"""
import re
from datetime import date, timedelta
from typing import Optional, Tuple

CATEGORY_PATTERNS = {
    "餐飲": ["餐飲", "吃", "食物", "餐廳", "外食", "uber eats", "ubereats", "food", "餐厅", "餐馆", "食堂", "松屋", "吉野家", "すき家", "マクドナルド", "麦当劳"],
    "購物": ["購物", "超市", "便利商店", "7-11", "全家", "lawson", "amazon", "購物", "shopping", "买", "买东西", "コンビニ"],
    "交通": ["交通", "電車", "地鐵", "公車", "計程車", "uber", "transport", "bus", "train", "taxi", "gas", "汽油", "加油站", "新干线", "バス"],
    "娛樂": ["娛樂", "電影", "netflix", "spotify", "演唱會", "遊戲", "game", "movie", "映画", "Netflix"],
    "醫療": ["醫療", "藥局", "診所", "醫院", "看病", "health", "pharmacy", "病院", "药店", "耳鼻咽喉科", "内科"],
    "保險": ["保險", "insurance", "保険"],
    "住房": ["房租", "房貸", "管理費", "水電", "housing", "rent", "mortgage", "電気", "ガス"],
    "通訊": ["電話", "網路", "手機", "電信", "telecom", "phone", "internet", "携帯", "スマホ"],
    "教育": ["教育", "書籍", "學費", "補習", "education", "book", "school", "読書", "本"],
    "投資": ["投資", "證券", "股票", "基金", "investment", "stock", "securities", "株", "証券"],
    "收入": ["薪水", "工資", "收入", "獎金", "salary", "income", "pay", "paycheck", "報酬", "収入"],
}

INCOME_KEYWORDS = ["收入", "薪水", "工資", "獎金", "紅利", "退款", "回收", "進帳", "収入", "給与", "ボーナス", "配当", "income", "salary", "bonus", "received", "got paid"]

def parse_amount(text: str) -> Tuple[Optional[float], str]:
    """Extract amount from text. Returns (amount, currency)."""
    # Japanese 万/萬 pattern: 32萬, 3.2万
    m = re.search(r'([\d.]+)\s*(萬|万)', text)
    if m:
        amount = float(m.group(1)) * 10000
        return amount, "JPY"
    
    # Japanese: ¥3000, 3000円, 3,000円
    patterns = [
        r'[¥￥]?([\d,]+)\s*円?',
        r'([\d,]+)\s*元',
        r'\$?([\d,]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            num_str = match.group(1).replace(',', '')
            amount = float(num_str)
            return amount, "JPY"
    return None, "JPY"

def parse_date(text: str) -> date:
    """Parse date from text. Returns today if no date found."""
    today = date.today()
    
    if "今天" in text or "today" in text.lower() or "今日" in text:
        return today
    if "昨天" in text or "yesterday" in text.lower() or "昨日" in text:
        return today - timedelta(days=1)
    if "前天" in text or "day before yesterday" in text.lower() or "一昨日" in text:
        return today - timedelta(days=2)
    
    m = re.search(r'(\d{1,2})/(\d{1,2})', text)
    if m:
        try:
            return today.replace(month=int(m.group(1)), day=int(m.group(2)))
        except ValueError:
            pass
    
    m = re.search(r'(\d+)天前', text)
    if m:
        return today - timedelta(days=int(m.group(1)))
    
    return today

def detect_category(text: str) -> Optional[str]:
    """Detect category from text. Returns category name or None."""
    text_lower = text.lower()
    
    for cat_name, keywords in CATEGORY_PATTERNS.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                return cat_name
    return None

def is_income(text: str) -> bool:
    """Check if text describes income."""
    text_lower = text.lower()
    for kw in INCOME_KEYWORDS:
        if kw.lower() in text_lower:
            return True
    return False

def parse_slash_command(text: str) -> dict:
    """Parse /command style input like /add 890 餐飲 松屋"""
    parts = text.strip().split(maxsplit=1)
    if len(parts) < 2:
        return {}
    
    command = parts[0].lstrip('/')
    rest = parts[1]
    
    if command in ["add", "spend"]:
        rest_parts = rest.split(maxsplit=2)
        amount_str = rest_parts[0] if rest_parts else ""
        
        try:
            amount = float(amount_str.replace(',', ''))
        except ValueError:
            return {}
        amount = -abs(amount)  # expense = negative
        
        cat_name = None
        if len(rest_parts) > 1:
            for cat in CATEGORY_PATTERNS.keys():
                if cat in rest:
                    cat_name = cat
                    break
        
        desc = rest
        for cat in CATEGORY_PATTERNS.keys():
            desc = desc.replace(cat, "")
        desc = re.sub(r'[\d,]+', '', desc).strip()
        
        return {
            "type": "expense",
            "amount": amount,
            "category": cat_name,
            "description": desc,
        }
    
    elif command == "income":
        rest_parts = rest.split(maxsplit=1)
        amount_str = rest_parts[0] if rest_parts else ""
        
        try:
            amount = abs(float(amount_str.replace(',', '')))
        except ValueError:
            return {}
        
        desc = rest_parts[1] if len(rest_parts) > 1 else "收入"
        
        return {
            "type": "income",
            "amount": amount,
            "category": "收入",
            "description": desc,
        }
    
    return {}

async def parse_natural_language(text: str) -> dict:
    """Main NLU parser. Takes raw text, returns structured dict."""
    text = text.strip()
    original = text
    
    # Check for slash commands first
    if text.startswith('/'):
        result = parse_slash_command(text)
        if result:
            result["date"] = date.today()
            result["confidence"] = 1.0
            return result
    
    # Parse amount
    amount, currency = parse_amount(text)
    
    # Parse date
    trans_date = parse_date(text)
    
    # Detect category
    category = detect_category(text)
    
    # Detect type
    inc = is_income(text)
    if amount:
        amount = abs(amount) if inc else -abs(amount)
    
    # Extract description
    desc = text
    desc = re.sub(r'([\d.]+)\s*(萬|万)', '', desc)
    desc = re.sub(r'[¥￥]?[\d,]+\s*円?', '', desc)
    desc = re.sub(r'[\d,]+\s*元', '', desc)
    desc = re.sub(r'\$?[\d,]+', '', desc)
    for cat in CATEGORY_PATTERNS.keys():
        desc = desc.replace(cat, "")
    desc = re.sub(r'\s+', ' ', desc).strip()
    if not desc:
        desc = original[:50]
    
    # Confidence
    confidence = 0.4
    if amount:
        confidence += 0.3
    if category:
        confidence += 0.2
    
    return {
        "type": "income" if inc else "expense",
        "amount": amount,
        "category": category,
        "description": desc,
        "date": trans_date,
        "merchant": desc.split()[0] if desc else "",
        "confidence": min(confidence, 1.0),
    }
