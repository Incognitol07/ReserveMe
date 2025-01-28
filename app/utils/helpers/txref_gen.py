# app/utils/helpers/txref_gen.py

import secrets
import string

def create_random_key(length: int = 24) -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))