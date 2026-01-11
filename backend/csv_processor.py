import csv
import io
from normalizer import normalize_software_name
from eos_lookup import lookup_eos_date
from risk_calculator import calculate_risk

def process_csv(input_file):
    """
    Process software inventory CSV file.
    
    Args:
        input_file: Path to CSV file
    
    Returns:
        List of dicts with normalized data, EOS info, and risk scores
    """
    results = []
    
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            software_name = row.get('software_name', '')
            
            # Step 1: Normalize the software name
            normalized = normalize_software_name(software_name)
            
            # Step 2: Look up EOS date
            eos_info = None
            if normalized['vendor'] and normalized['product'] and normalized['version']:
                eos_info = lookup_eos_date(
                    normalized['vendor'],
                    normalized['product'],
                    normalized['version']
                )
            
            # Step 3: Calculate risk
            risk_info = {"risk_level": "UNKNOWN", "days_until_eos": None, "reason": "No EOS data available"}
            if eos_info:
                risk_info = calculate_risk(eos_info.get('eos_date'))
            
            # Combine everything
            result = {
                "raw_input": software_name,
                "install_date": row.get('install_date', ''),
                "source": row.get('source', ''),
                "vendor": normalized['vendor'],
                "product": normalized['product'],
                "version": normalized['version'],
                "edition": normalized['edition'],
                "confidence_score": normalized['confidence_score'],
                "eos_date": eos_info.get('eos_date') if eos_info else None,
                "eos_source": eos_info.get('source') if eos_info else None,
                "risk_level": risk_info['risk_level'],
                "days_until_eos": risk_info['days_until_eos'],
                "risk_reason": risk_info['reason']
            }
            
            results.append(result)
    
    return results


def process_csv_data(csv_string):
    """
    Process CSV data from a string (for API use).
    
    Args:
        csv_string: CSV content as string
    
    Returns:
        List of dicts with normalized data, EOS info, and risk scores
    """
    results = []
    csv_file = io.StringIO(csv_string)
    reader = csv.DictReader(csv_file)
    
    for row in reader:
        software_name = row.get('software_name', '')
        
        # Step 1: Normalize the software name
        normalized = normalize_software_name(software_name)
        
        # Step 2: Look up EOS date
        eos_info = None
        if normalized['vendor'] and normalized['product'] and normalized['version']:
            eos_info = lookup_eos_date(
                normalized['vendor'],
                normalized['product'],
                normalized['version']
            )
        
        # Step 3: Calculate risk
        risk_info = {"risk_level": "UNKNOWN", "days_until_eos": None, "reason": "No EOS data available"}
        if eos_info:
            risk_info = calculate_risk(eos_info.get('eos_date'))
        
        # Combine everything
        result = {
            "raw_input": software_name,
            "install_date": row.get('install_date', ''),
            "source": row.get('source', ''),
            "vendor": normalized['vendor'],
            "product": normalized['product'],
            "version": normalized['version'],
            "edition": normalized['edition'],
            "confidence_score": normalized['confidence_score'],
            "eos_date": eos_info.get('eos_date') if eos_info else None,
            "eos_source": eos_info.get('source') if eos_info else None,
            "risk_level": risk_info['risk_level'],
            "days_until_eos": risk_info['days_until_eos'],
            "risk_reason": risk_info['reason']
        }
        
        results.append(result)
    
    return results