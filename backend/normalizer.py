import re
from rapidfuzz import fuzz

VENDOR_ALIASES = {
    "Microsoft": ["ms", "Microsoft Corp.", "msft", "microsoft"],
    "Adobe": ["adobe"],
    "Google": ["Alphabet", "Google LLC", "GOOGL"],
    "Apple": ["AAPL", "Apple Inc.", "Apple Computer"],
    "Amazon": ["AMZN", "Amazon.com, Inc.", "Amazon Web Services"],
    "Oracle": ["ORCL", "oracle"],
    "VMware": ["VMW", "vmware", "vm ware"],
    "Red Hat": ["RedHat", "red hat", "rhel"],
    "Python software foundation": ["python", "python.org"],
}


EDITION_KEYWORDS = [
    "professional plus", "professional",  # Check multi-word first
    "enterprise edition", "enterprise",
    "developer edition", "developer", 
    "standard edition", "standard",
    "ultimate", "premium", "basic", "home",
    "express", "community", "datacenter"
]




def detect_vendor(software_name):
    """Detects the vendor of a given software name using alias matching and fuzzy string matching."""
    name_lower = software_name.lower()

    # Check each vendor's aliases
    for canonical_vendor, aliases in VENDOR_ALIASES.items():
        for alias in aliases:
            # Use word boundaries to avoid substring matches
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, name_lower):
                return canonical_vendor, alias # High confidence - exact match
    

    # Special case: Windows products without MS/Microsoft prefix
    if re.search(r'\bwindows\b', name_lower):
        return "Microsoft", "windows"

    # No match found
    return None, None


def extract_version(software_name):
    """
    Extract version number from software name.
    Returns: version string or None
    """
    # Try patterns in order of specificity
    

    # Pattern 1: Dotted version (3.11.4, 19.3.0.0.0)
    dotted_match = re.search(r'\b\d+(\.\d+)+\b', software_name)
    if dotted_match:
        return dotted_match.group()

    # Pattern 2: Year (2019, 2022)
    year_match = re.search(r'\b20\d{2}\b', software_name)
    if year_match:
        return year_match.group()
    
    # Pattern 3: Number with letter suffix (19c, 8c)
    letter_match = re.search(r'\b\d+[a-z]\b', software_name.lower())
    if letter_match:
        return letter_match.group()
    
    # Pattern 4: Simple numbers (365, 11, 8) - last resort
    number_match = re.search(r'\b\d{1,3}\b', software_name)
    if number_match:
        return number_match.group()
    
    return None



def extract_edition(software_name):

    name_lower = software_name.lower()

    for edition in EDITION_KEYWORDS:
        pattern = r'\b' + re.escape(edition) + r'\b'
        if re.search(pattern,name_lower):
            return edition.title()
        
    return None



def extract_product(software_name, vendor=None, matched_alias=None, version=None, edition=None):
    """
    Extract product name by removing known components.
    Returns: cleaned product name
    """
    result = software_name
    
    # Remove vendor if found
    if matched_alias:
        for alias in VENDOR_ALIASES.get(vendor, []):
            # Remove the alias with word boundaries
            pattern = r'\b' + re.escape(alias) + r'\b'
            result = re.sub(pattern, '', result, flags=re.IGNORECASE)
    
    # Remove version if found
    if version:
        pattern = r'\b' + re.escape(version) + r'\b'
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)
    
    # Remove edition if found
    if edition:
        pattern = r'\b' + re.escape(edition) + r'\b'
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)
        
    
    # Clean up: remove extra spaces, underscores, hyphens
    result = re.sub(r'[_\-]+', ' ', result)  # Replace _ and - with spaces
    result = re.sub(r'\s+', ' ', result)      # Collapse multiple spaces
    result = result.strip()                    # Remove leading/trailing spaces
    
    return result if result else matched_alias  # If empty, use alias as product




def normalize_software_name(software_name):
    """
    Main normalization function.
    Returns: dict with vendor, product, version, edition, confidence
    """

    normalized_input = software_name.replace('_', ' ').replace('-', ' ')

    

    # Step 1: Detect vendor
    vendor, matched_alias = detect_vendor(normalized_input)  # Unpack tuple
    
    # Step 2: Extract version
    version = extract_version(normalized_input)
    
    # Step 3: Extract edition
    edition = extract_edition(normalized_input)
    
    # Step 4: Extract product (needs other components)
    product = extract_product(normalized_input, vendor, matched_alias, version, edition)
    
    # Step 5: Calculate confidence score
    confidence = 0.0
    if vendor:
        confidence += 0.4
    if product:
        confidence += 0.3
    if version:
        confidence += 0.2
    if edition:
        confidence += 0.1
    
    return {
        "raw_input": software_name,
        "vendor": vendor,
        "product": product,
        "version": version,
        "edition": edition,
        "confidence_score": confidence
    }

