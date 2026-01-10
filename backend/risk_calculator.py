from datetime import datetime, date

def calculate_risk(eos_date_str):
    """
    Calculate risk level based on EOS date.
    
    Args:
        eos_date_str: Date string in format "YYYY-MM-DD" or None
    
    Returns:
        dict with:
            - risk_level: "CRITICAL", "HIGH", "MEDIUM", "LOW", or "UNKNOWN"
            - days_until_eos: int or None
            - reason: explanation string
    """
    # Handle None/null EOS dates (subscription services)
    if eos_date_str is None:
        return {
            "risk_level": "LOW",
            "days_until_eos": None,
            "reason": "Subscription-based, continuously updated"
        }
    
    # Parse EOS date
    try:
        eos_date = datetime.strptime(eos_date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return {
            "risk_level": "UNKNOWN",
            "days_until_eos": None,
            "reason": "Invalid EOS date format"
        }
    
    # Calculate days until EOS
    today = date.today()
    days_until = (eos_date - today).days
    
    # Determine risk level
    if days_until < 0:
        return {
            "risk_level": "CRITICAL",
            "days_until_eos": days_until,
            "reason": f"Already past EOS by {abs(days_until)} days"
        }
    elif days_until < 90:
        return {
            "risk_level": "HIGH",
            "days_until_eos": days_until,
            "reason": f"EOS in {days_until} days (< 90 days)"
        }
    elif days_until < 180:
        return {
            "risk_level": "MEDIUM",
            "days_until_eos": days_until,
            "reason": f"EOS in {days_until} days (90-180 days)"
        }
    else:
        return {
            "risk_level": "LOW",
            "days_until_eos": days_until,
            "reason": f"EOS in {days_until} days (> 180 days)"
        }