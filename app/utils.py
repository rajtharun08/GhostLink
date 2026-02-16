import string
import random

def generate_short_code(length=6):
    """Generates a random 6-character alphanumeric string."""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))