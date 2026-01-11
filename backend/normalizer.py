import re
from rapidfuzz import fuzz

# ============================================================================
# CONFIGURATION
# ============================================================================

VENDOR_ALIASES = {
    "Microsoft": ["ms", "msft", "microsoft", "sql", "windows", "win"],
    "Adobe": ["adobe"],
    "Oracle": ["oracle"],
    "VMware": ["vmware", "vm ware"],
    "Red Hat": ["redhat", "red hat", "rhel"],
    "Python Software Foundation": ["python"],
}

EDITION_KEYWORDS = [
    "professional plus", "professional",
    "enterprise edition", "enterprise",
    "developer edition", "developer",
    "standard edition", "standard",
    "ultimate", "premium", "basic", "home",
    "express", "community", "datacenter"
]

PRODUCT_ABBREVIATIONS = {
    "db": "database",
    "svr": "server",
    "srv": "server",
    "win": "windows",
}

ARCHITECTURE_KEYWORDS = [
    "amd64", "x86", "x64", "x86_64", "arm64", "i386", "i686", "arm"
]

# Products where vendor name is part of product name
COMPOUND_PRODUCTS = {
    "Microsoft": ["windows server", "sql server", "windows"],
    "VMware": ["vmware vsphere", "vmware"],
}


# ============================================================================
# STEP 1: PREPROCESSING
# ============================================================================

def preprocess(software_name):
    """
    Clean and normalize input before extraction.
    
    Returns: cleaned string
    """
    result = software_name
    
    # Normalize separators
    result = result.replace('_', ' ').replace('-', ' ')

    # Expand RHEL acronym BEFORE other processing
    result = re.sub(r'\bRHEL\b', 'Red Hat Enterprise Linux', result, flags=re.IGNORECASE)

    result = re.sub(r'\b(v|ver|version)\s*(?=\d)', '', result, flags=re.IGNORECASE)
    
    # Strip architecture keywords
    for arch in ARCHITECTURE_KEYWORDS:
        pattern = r'\b' + re.escape(arch) + r'\b'
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)
    
    # Expand common abbreviations
    for abbrev, full in PRODUCT_ABBREVIATIONS.items():
        pattern = r'\b' + re.escape(abbrev) + r'\b'
        result = re.sub(pattern, full, result, flags=re.IGNORECASE)
    
    # Collapse multiple spaces
    result = re.sub(r'\s+', ' ', result).strip()
    
    return result


# ============================================================================
# STEP 2: VENDOR EXTRACTION
# ============================================================================

def extract_vendor(software_name):
    """Extract vendor with special case handling."""
    name_lower = software_name.lower()
    
    for canonical_vendor, aliases in VENDOR_ALIASES.items():
        for alias in aliases:
            pattern = r'\b' + re.escape(alias) + r'\b'
            if re.search(pattern, name_lower):
                # Build context hints
                context = {
                    "matched_alias": alias,
                    "is_os": ("windows" in alias or "linux" in name_lower or 
                             "rhel" in alias or canonical_vendor == "Red Hat"),  # ← ADDED
                    "is_database": "database" in name_lower or canonical_vendor == "Oracle",
                }
                return canonical_vendor, alias, context
    
    return None, None, {}


# ============================================================================
# STEP 3: CONTEXT-AWARE VERSION EXTRACTION
# ============================================================================

def extract_version_contextual(software_name, vendor_context):
    """Extract version - return RAW, no normalization."""
    # Oracle special case
    if vendor_context.get("is_database") and vendor_context.get("matched_alias") == "oracle":
        dotted_match = re.search(r'\b(\d{2})\.[\d\.]+\b', software_name)
        if dotted_match:
            return f"{dotted_match.group(1)}c"
    
    # Try patterns from most specific to least specific
    patterns = [
        (r'(\d+\.\d+\.\d+)', "three_part"),    # 3.11.4, 2023.001 (no \b for v2023.001)
        (r'(\d+\.\d+)', "two_part"),           # 8.6, 7.0 (no \b)
        (r'(20\d{2})', "year"),                # 2019, v2023 (no \b)
        (r'\b(\d+[a-z])\b', "letter_suffix"),  # 19c
        (r'\b(DC)\b', "adobe_dc"),             # DC
        (r'\b(\d{1,3})\b', "simple_number"),   # 365
    ]
    
    for pattern, pattern_type in patterns:
        match = re.search(pattern, software_name, re.IGNORECASE)
        if match:
            return match.group(1)  # Return RAW - no normalization!
    
    return None


# ============================================================================
# STEP 4: CONTEXT-AWARE PRODUCT EXTRACTION
# ============================================================================

def extract_product_contextual(software_name, vendor, matched_alias, version):
    """
    Extract product using vendor context.
    
    Returns: product name
    """
    result = software_name
    
    # Check if this is a compound product (vendor is part of product name)
    is_compound = False
    if vendor and vendor in COMPOUND_PRODUCTS:
        result_lower = result.lower()
        for compound in COMPOUND_PRODUCTS[vendor]:
            if compound in result_lower:
                is_compound = True
                break
    
    # Remove vendor alias ONLY if not a compound product
    if matched_alias and not is_compound:
        pattern = r'\b' + re.escape(matched_alias) + r'\b'
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)
    
    # Remove version (but preserve DC in Adobe Acrobat DC)
    if version and version != "DC":
        pattern = re.escape(version) 
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)
    
    # Remove edition keywords
    for edition in EDITION_KEYWORDS:
        pattern = r'\b' + re.escape(edition) + r'\b'
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)
    
    # Clean up artifacts
    result = re.sub(r'\s+', ' ', result)      # Multiple spaces
    result = re.sub(r'^\s*\.\s*', '', result) # Leading dots
    result = re.sub(r'\s*\.\s*$', '', result) # Trailing dots
    result = result.strip()
    
    # If empty, use matched alias as fallback
    if not result and matched_alias:
        return matched_alias.title()
    
    return result.title() if result else None


# ============================================================================
# STEP 5: EDITION EXTRACTION
# ============================================================================

def extract_edition(software_name):
    """Extract edition keywords."""
    name_lower = software_name.lower()
    
    for edition in EDITION_KEYWORDS:
        pattern = r'\b' + re.escape(edition) + r'\b'
        if re.search(pattern, name_lower):
            return edition.title()
    
    return None


# ============================================================================
# STEP 6: MAIN NORMALIZATION FUNCTION
# ============================================================================

def normalize_software_name(software_name):
    """Main normalization pipeline."""
    # Step 1: Preprocess
    cleaned = preprocess(software_name)
    
    # Step 2: Extract vendor
    vendor, matched_alias, context = extract_vendor(cleaned)
    
    # Step 3: Extract version (ORIGINAL, before normalization)
    version_original = extract_version_contextual(cleaned, context)
    
    # Step 4: Extract edition
    edition = extract_edition(cleaned)
    
    # Step 5: Extract product (use ORIGINAL version for removal)
    product = extract_product_contextual(cleaned, vendor, matched_alias, version_original)
    
    # Step 6: Normalize version for lookup AFTER product extraction
    version_normalized = normalize_version_for_lookup(version_original)
    
    # Step 7: Calculate confidence
    confidence = 0.0
    if vendor:
        confidence += 0.4
    if product:
        confidence += 0.3
    if version_original:
        confidence += 0.2
    if edition:
        confidence += 0.1
    
    return {
        "raw_input": software_name,
        "preprocessed": cleaned,
        "vendor": vendor,
        "product": product,
        "version": version_normalized,  # Use normalized for lookup
        "edition": edition,
        "confidence_score": confidence,
        "context": context
    }

def normalize_version_for_lookup(version):
    """Normalize version ONLY for database lookup, not for removal."""
    if not version:
        return version
    
    # Keep original version as-is - normalization happens in eos_lookup
    return version