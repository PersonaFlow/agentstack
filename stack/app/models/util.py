import string
import random


def generate_unique_identifier(length=16):
    """Generate a random string of fixed length."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))
