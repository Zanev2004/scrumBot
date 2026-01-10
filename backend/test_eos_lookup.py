from eos_lookup import lookup_eos_date

# Test cases
test_cases = [
    ("Microsoft", "Office", "2019"),
    ("Microsoft", "Office", "365"),
    ("Microsoft", "Windows Server", "2019"),
    ("Python Software Foundation", "Python", "3.11"),
    ("Oracle", "Database", "19c"),
    ("Adobe", "Acrobat", "DC"),
]

print("Testing EOS Lookup:\n")

for vendor, product, version in test_cases:
    result = lookup_eos_date(vendor, product, version)
    
    print(f"Product: {vendor} {product} {version}")
    if result:
        print(f"  EOS Date: {result.get('eos_date', 'N/A')}")
        print(f"  Source: {result.get('source', 'N/A')}")
        if 'notes' in result:
            print(f"  Notes: {result['notes']}")
    else:
        print(f"  ⚠️  Not found in database")
    print()