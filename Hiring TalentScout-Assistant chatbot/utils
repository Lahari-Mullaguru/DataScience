import re
import random
import hashlib

def validate_email(email):
    pattern = r"[^@]+@[^@]+\.[^@]+"
    return re.match(pattern, email)

def validate_phone(phone):
    pattern = r"^\+?\d{10,15}$"
    return re.match(pattern, phone)

def anonymize_data(data):
    """Simulates anonymization using hashing."""
    return {k: hashlib.sha256(str(v).encode()).hexdigest() for k, v in data.items()}

def generate_session_id():
    return hashlib.sha256(str(random.random()).encode()).hexdigest()

def is_exit_command(user_input):
    exit_keywords = ["exit", "quit", "bye", "goodbye", "end"]
    return any(word in user_input.lower() for word in exit_keywords)
