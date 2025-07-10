import hashlib
import random
import string
import time
from fastapi import Header, HTTPException
import time
from collections import defaultdict


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


# In-memory stores
fixed_window_store = defaultdict(lambda: {"count": 0, "start": time.time()})
sliding_window_store = defaultdict(list)
token_bucket_store = defaultdict(lambda: {"tokens": 0, "last": time.time()})
leaky_bucket_store = defaultdict(lambda: {"water": 0, "last": time.time()})


async def fixed_window(key: str, limit: int, window: int = 60) -> bool:
    now = time.time()
    window_data = fixed_window_store[key]

    if now - window_data["start"] > window:
        fixed_window_store[key] = {"count": 1, "start": now}
        return True

    if window_data["count"] < limit:
        window_data["count"] += 1
        return True

    return False


async def sliding_window(key: str, limit: int, window: int = 60) -> bool:
    now = time.time()
    requests = sliding_window_store[key]

    # Remove old requests
    sliding_window_store[key] = [ts for ts in requests if now - ts < window]

    if len(sliding_window_store[key]) >= limit:
        return False

    sliding_window_store[key].append(now)
    return True


async def token_bucket(key: str, rate: float, capacity: int, window: int = 60) -> bool:
    now = time.time()
    data = token_bucket_store[key]
    elapsed = now - data["last"]

    data["tokens"] = min(capacity, data["tokens"] + elapsed * (rate / window))
    data["last"] = now

    if data["tokens"] >= 1:
        data["tokens"] -= 1
        return True

    return False


def leaky_bucket(key: str, rate: float, capacity: int) -> bool:
    now = time.time()
    data = leaky_bucket_store[key]
    elapsed = now - data["last"]

    data["water"] = max(0, data["water"] - elapsed * rate)
    data["last"] = now

    if data["water"] < capacity:
        data["water"] += 1
        return True

    return False
