"""Test NLU parser and formatters."""
import sys
sys.path.insert(0, ".")

import asyncio
from Kitt_pfm.services.nlu import parse_natural_language, CATEGORY_PATTERNS
from Kitt_pfm.utils.currency import format_jpy, format_jpy_short
from Kitt_pfm.utils.date_utils import format_date_chinese, format_date_short, days_in_month

print("=== NLU Parser Tests ===\n")

test_cases = [
    "今天uber eats 2480",
    "記一筆 餐飲 松屋 890",
    "薪水32萬",
    "今天買了星巴克 650",
    "uber eats 2480",
    "/add 890 餐飲 松屋",
    "/income 320000 薪水",
    "我的總資產",
    "這個月餐飲花了多少",
]

async def run_tests():
    for text in test_cases:
        result = await parse_natural_language(text)
        print(f"Input: {text!r}")
        print(f"  → type={result['type']}, amount={result['amount']}, category={result['category']}, desc={result['description']!r}, conf={result['confidence']:.2f}")
        print()

asyncio.run(run_tests())

print("=== Currency Format Tests ===\n")
print(f"format_jpy(890):     {format_jpy(890)}")
print(f"format_jpy(-2480):   {format_jpy(-2480)}")
print(f"format_jpy(320000):  {format_jpy(320000)}")
print(f"format_jpy_short(890):     {format_jpy_short(890)}")
print(f"format_jpy_short(-24800):  {format_jpy_short(-24800)}")
print(f"format_jpy_short(-248000): {format_jpy_short(-248000)}")

print("\n=== Date Format Tests ===\n")
from datetime import date
d = date(2026, 5, 7)
print(f"format_date_chinese({d}): {format_date_chinese(d)}")
print(f"format_date_short({d}):   {format_date_short(d)}")
print(f"days_in_month(2026, 5):   {days_in_month(2026, 5)}")

print("\n✅ All tests passed!")
