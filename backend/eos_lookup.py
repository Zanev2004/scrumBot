import json
from rapidfuzz import process, fuzz

def load_eos_database():
    """Load the EOS database from JSON file."""
    with open('data/eos_database.json', 'r') as f:
        return json.load(f)

def normalize_version(version):
    """
    Normalize version strings for better matching.
    
    Examples:
        3.11.4 → 3.11
        19.3.0.0.0 → 19
        7.0.3 → 7.0  ← NEW
        8.6 → 8.6 (handled by context in normalizer)
    """
    if not version:
        return version
    
    # Handle "c" suffix (Oracle 19c)
    if version.endswith('c'):
        return version
    
    # Split by dots
    parts = version.split('.')
    
    # If it's a very long version (19.3.0.0.0), take first part
    if len(parts) > 3:
        return parts[0]
    
    # If it's X.Y.Z, return X.Y
    if len(parts) == 3:
        return f"{parts[0]}.{parts[1]}"
    
    # If it's X.Y, keep as is
    if len(parts) == 2:
        return f"{parts[0]}.{parts[1]}"
    
    return version

def find_best_product_match(vendor, product, db):
    """Find best matching product in database using fuzzy matching."""
    if not product:
        return None, 0
    
    # Build search queries (normalize to lowercase for better matching)
    search_queries = []
    if vendor and product:
        search_queries.append(f"{vendor} {product}".lower())
    if product:
        search_queries.append(product.lower())
    
    best_match = None
    best_score = 0
    
    # Normalize database keys to lowercase for comparison
    db_products = list(db.keys())
    db_lower_map = {k.lower(): k for k in db_products}
    
    for query in search_queries:
        match = process.extractOne(
            query,
            list(db_lower_map.keys()),
            scorer=fuzz.token_sort_ratio
        )
        
        if match:
            matched_key_lower, score, _ = match
            
            ##print(f"DEBUG: Query '{query}' matched '{matched_key_lower}' with score {score}")
            
            if score > best_score:
                best_score = score
                best_match = db_lower_map[matched_key_lower]
    
    if best_score >= 70:
        return best_match, best_score
    
    return None, 0

def find_best_version_match(target_version, available_versions, product_name=""):
    """
    Find best matching version using fuzzy matching with multiple strategies.
    """
    if not target_version or not available_versions:
        return None, 0
    
    # Try multiple normalization strategies
    candidates = [target_version]  # Original
    
    # Add normalized version
    normalized = normalize_version(target_version)
    if normalized != target_version:
        candidates.append(normalized)
    
    # For X.Y versions, also try just X (for OS versions like RHEL 8.6 → 8)
    parts = target_version.split('.')
    if len(parts) == 2:
        candidates.append(parts[0])
    
    # For X.Y.Z versions, also try X.Y
    if len(parts) == 3:
        candidates.append(f"{parts[0]}.{parts[1]}")
    
    best_match = None
    best_score = 0
    
    for candidate in candidates:
        # Try exact match first
        if candidate in available_versions:
            return candidate, 100
        
        # Try fuzzy match
        match = process.extractOne(
            candidate,
            available_versions,
            scorer=fuzz.ratio
        )
        
        if match:
            matched_version, score, _ = match
            if score > best_score and score >= 60:
                best_score = score
                best_match = matched_version
    
    if best_match:
        return best_match, best_score
    
    return None, 0

def lookup_eos_date(vendor, product, version):
    """
    Look up end-of-support date using fuzzy matching.
    
    Args:
        vendor: Vendor name (e.g., "Microsoft")
        product: Product name (e.g., "Office")
        version: Version string (e.g., "2019")
    
    Returns:
        dict with eos_date, source, notes, match_confidence
        None if not found
    """
    db = load_eos_database()
    
    # Step 1: Find best product match
    matched_product, product_confidence = find_best_product_match(vendor, product, db)
    
    if not matched_product:
        return None
    
    # Step 2: Find best version match
    available_versions = list(db[matched_product].keys())
    matched_version, version_confidence = find_best_version_match(version, available_versions)
    
    if not matched_version:
        return None
    
    # Step 3: Return EOS data with confidence scores
    eos_data = db[matched_product][matched_version].copy()
    eos_data['match_confidence'] = {
        'product': product_confidence,
        'version': version_confidence,
        'overall': (product_confidence + version_confidence) / 2
    }
    
    return eos_data