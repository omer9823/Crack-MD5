from fastapi import FastAPI
import asyncio
from typing import Dict
from concurrent.futures import ProcessPoolExecutor
from app.models.CrackRequest import CrackRequest
import logging
from app.minion.minion_service import MinionCracker

# -------- Logging -------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] [%(levelname)s] %(message)s"
)
logger = logging.getLogger("MINION")
# -------------------------- #

app = FastAPI()
executor = ProcessPoolExecutor()

@app.post("/crack")
async def crack(req: CrackRequest) -> Dict[str,str]:
    """
    Handle a cracking request:
    - Receives a list of MD5 hashes and a phone number range
    - Runs brute-force over the range in a background process (ProcessPoolExecutor)
    - Returns a dictionary of found hashes mapped to their corresponding phone numbers
    """
    logger.info(f"Received request to crack hashs in range {req.range_start} to {req.range_end}")

    cracker = MinionCracker(req.hashes, req.range_start, req.range_end)
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(executor, cracker.crack_range_sync)

    if result:
        for h, phone in result.items():
            logger.info(f"[✓] Found match: {h[:8]} → {phone}")
    else:
        logger.info("[X] No matches found in this range.")

    return result