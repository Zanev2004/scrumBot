from normalizer import normalize_software_name

# Test cases from our sample data
test_cases = [
    "MS Office Professional Plus 2019",
    "microsoft_office_365_proplus",
    "Adobe Acrobat DC",
    "Oracle Database 19c Enterprise Edition",
    "Python 3.11.4",
    "Windows Server 2019 Standard",
]

print("Testing Normalizer:\n")
for software in test_cases:
    result = normalize_software_name(software)
    print(f"Input: {software}")
    print(f"  Vendor: {result['vendor']}")
    print(f"  Product: {result['product']}")
    print(f"  Version: {result['version']}")
    print(f"  Edition: {result['edition']}")
    print(f"  Confidence: {result['confidence_score']}\n")