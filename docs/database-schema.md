vendors (master list)
id
cannon name (e.g. , "Microsoft)
aliases (["MSFT", "microsoft", "MS"])

products (master list)
id
vendor_id
product_name (e.g., "Office")
product_family (e.g., "Office Suite")

software_inventory (messy reality)
id
raw_input
normalized_vendor_id
normalized_product_id
version
edition
source (CMDB, endpoint tool, etc.)
confidence_score (0-1)
created_at

eos_dates (support lifecycle data)
id
product_id
version
eos_date
source (vendor website, scraped, predicted)
last_verified

risk_assessments (calculated)
id
inventory_id
risk_level (critical, high, medium, low)
days_until_eos
calculated_at
