from risk_calculator import calculate_risk
from datetime import date, timedelta

# Generate test dates relative to today
today = date.today()

test_cases = [
    # (eos_date, description)
    ("2025-10-14", "Microsoft Office 2019 (already past EOS)"),
    ((today + timedelta(days=30)).strftime("%Y-%m-%d"), "30 days until EOS"),
    ((today + timedelta(days=120)).strftime("%Y-%m-%d"), "120 days until EOS"),
    ((today + timedelta(days=365)).strftime("%Y-%m-%d"), "1 year until EOS"),
    (None, "Office 365 (subscription)"),
    ("invalid-date", "Invalid date format"),
]

print("Testing Risk Calculator:\n")
print(f"Today's date: {today}\n")

for eos_date, description in test_cases:
    result = calculate_risk(eos_date)
    
    print(f"Test: {description}")
    print(f"  EOS Date: {eos_date}")
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Days Until EOS: {result['days_until_eos']}")
    print(f"  Reason: {result['reason']}")
    print()