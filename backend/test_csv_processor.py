from csv_processor import process_csv
import json

# Process the sample CSV
results = process_csv('data/sample_input.csv')

print("CSV Processing Results:\n")
print("="*80)

for result in results:
    print(f"\nRaw Input: {result['raw_input']}")
    print(f"Source: {result['source']}")
    print(f"-" * 40)
    print(f"Vendor: {result['vendor']}")
    print(f"Product: {result['product']}")
    print(f"Version: {result['version']}")
    print(f"Edition: {result['edition']}")
    print(f"Confidence: {result['confidence_score']:.2f}")
    print(f"-" * 40)
    print(f"EOS Date: {result['eos_date']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Days Until EOS: {result['days_until_eos']}")
    print(f"Risk Reason: {result['risk_reason']}")
    print("="*80)

# Summary
print("\n\nRISK SUMMARY:")
risk_counts = {}
for result in results:
    level = result['risk_level']
    risk_counts[level] = risk_counts.get(level, 0) + 1

for level, count in sorted(risk_counts.items()):
    print(f"  {level}: {count} products")