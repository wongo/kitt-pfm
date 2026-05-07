"""Date utilities."""
from datetime import date

def format_date_chinese(d: date) -> str:
    """2026-05-07 → 2026年5月7日"""
    return f"{d.year}年{d.month}月{d.day}日"

def format_date_short(d: date) -> str:
    """2026-05-07 → 05/07"""
    return f"{d.month:02d}/{d.day:02d}"

def days_in_month(year: int, month: int) -> int:
    """Return days in given month."""
    if month == 12:
        next_month = date(year+1, 1, 1)
    else:
        next_month = date(year, month+1, 1)
    return (next_month - date(year, month, 1)).days

def days_left_in_month(d: date) -> int:
    """Days remaining from today until end of month."""
    total = days_in_month(d.year, d.month)
    return total - d.day + 1
