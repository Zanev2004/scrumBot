import json
from datetime import datetime

def load_eos_database():
    """Load the EOS database from JSON file."""
    with open('data/eos_database.json', 'r') as f:
        return json.load(f)

def lookup_eos_date(vendor, product, version):
    """
    Look up end-of-support date for a software product.
    
    Args:
        vendor: Vendor name (e.g., "Microsoft")
        product: Product name (e.g., "Office")
        version: Version string (e.g., "2019")
    
    Returns:
        dict with eos_date, source, notes (if available)
        None if not found
    """
    db = load_eos_database()
    
    # Try multiple lookup strategies
    lookup_keys = [
        f"{vendor} {product}",  # "Microsoft Office"
        product,                # "Office"
        f"{product}",          # Just product name
    ]
    
    for product_key in lookup_keys:
        if product_key in db:
            if version in db[product_key]:
                return db[product_key][version]
    
    return None