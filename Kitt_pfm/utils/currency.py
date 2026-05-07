"""Currency formatting utilities."""

def format_jpy(amount: float, show_sign: bool = True) -> str:
    """Format amount as Japanese Yen."""
    sign = "+" if amount > 0 and show_sign else ""
    return f"{sign}¥{int(amount):,}"

def format_jpy_short(amount: float) -> str:
    """Short format: 12000 → 1.2万"""
    abs_amount = abs(amount)
    sign = "-" if amount < 0 else ""
    if abs_amount >= 10000:
        return f"{sign}¥{abs_amount/10000:.1f}万"
    return f"{sign}¥{int(abs_amount):,}"
