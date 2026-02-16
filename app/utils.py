import string
import random
from datetime import datetime

def generate_short_code(length=6):
    """Generates a random 6-character alphanumeric string."""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def get_now():
    """Returns the current timestamp in the format expected by SQLite."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')