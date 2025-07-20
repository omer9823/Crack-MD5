from fastapi import FastAPI
import hashlib
from typing import Optional
import asyncio
from concurrent.futures import ProcessPoolExecutor
from app.models.CrackRequest import CrackRequest
import logging
from app.utils import phone_to_int, int_to_phone

# -------- Logging -------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] [%(levelname)s] %(message)s"
)
logger = logging.getLogger("MINION")
# -------------------------- #

app = FastAPI()
executor = ProcessPoolExecutor()

def crack_range_sync(hash_val: str, r_start: int, r_end: int) -> Optional[str]:
    """
    Brute-force the MD5 hash over phone numbers with the given prefix and range.
    """
    for i in range(r_start, r_end + 1):
        phone = int_to_phone(i)
        candidate_hash = hashlib.md5(phone.encode()).hexdigest()
        if candidate_hash == hash_val:
            return phone
    return None

@app.post("/crack")
async def crack(req: CrackRequest):
    """
    Handle a cracking request:
    - Run the MD5 brute-force search in a background process using ProcessPoolExecutor
    - Return whether a matching phone number was found
    """
    logger.info(f"Received request to crack hash {req.hash[:8]}... in range {req.range_start} to {req.range_end}")

    loop = asyncio.get_running_loop()
    password = await loop.run_in_executor(executor, crack_range_sync, req.hash, req.range_start, req.range_end)

    if password:
        logger.info(f"[✓] Found password for hash {req.hash[:8]}: {password}")
    else:
        logger.info(f"[X] No match for hash {req.hash[:8]} in range.")

    return {"found": password is not None, "password": password}