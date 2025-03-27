import re
from typing import Optional, List

def validate_email(email: str) -> bool:
    """Validate email format"""
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def validate_phone(phone: str) -> bool:
    """Validate phone number (digits only, min 10 chars)"""
    return phone.isdigit() and len(phone) >= 10

def parse_tech_stack(input_str: str) -> List[str]:
    """Parse comma/slash-separated tech stack"""
    return [tech.strip() for tech in re.split(r"[,/]", input_str) if tech.strip()]

def validate_experience(years: str) -> bool:
    """Validate years of experience"""
    return years.isdigit() and 0 <= int(years) <= 50
