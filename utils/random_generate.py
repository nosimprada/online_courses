import random

def generate_token_hash(length: int = 32) -> str:
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(random.choice(characters) for _ in range(length))

def generate_short_code(length: int = 6) -> str:
    characters = "0123456789"
    return ''.join(random.choice(characters) for _ in range(length))