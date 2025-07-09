import hashlib
import random
import string
import time
from fastapi import Header, HTTPException


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def generate_random_ids():
    uppercase = ''.join(random.choices(string.ascii_uppercase, k=10))
    lowercase = ''.join(random.choices(string.ascii_lowercase, k=10))
    epoch = int(time.time())
    unique = f"{epoch}"
    for i in range(0, 10):
        unique += f"{lowercase[i]}{uppercase[i]}"
    return unique


async def get_api_key(x_api_key: str = Header(None)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key header")
    return x_api_key
