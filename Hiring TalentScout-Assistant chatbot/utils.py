import re
import random
import hashlib

def validate_email(email: str) -> bool:
    pattern = r"[^@]+@[^@]+\\.[^@]+"
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    cleaned = re.sub(r"[^\\d]", "", phone)
    return len(cleaned) >= 10




def anonymize_data(data):
    """Simulates anonymization using hashing."""
    return {k: hashlib.sha256(str(v).encode()).hexdigest() for k, v in data.items()}

def generate_session_id():
    return hashlib.sha256(str(random.random()).encode()).hexdigest()

def is_exit_command(user_input):
    exit_keywords = ["exit", "quit", "bye", "goodbye", "end"]
    return any(word in user_input.lower() for word in exit_keywords)
