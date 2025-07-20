from fastapi import FastAPI
import asyncio
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
async def crack(req: CrackRequest):
    """
    Handle a cracking request:
    - Run the MD5 brute-force search in a background process using ProcessPoolExecutor
    - Return whether a matching phone number was found
    """
    logger.info(f"Received request to crack hash {req.hash[:8]}... in range {req.range_start} to {req.range_end}")

    cracker = MinionCracker(req.hash, req.range_start, req.range_end)
    loop = asyncio.get_running_loop()
    password = await loop.run_in_executor(executor, cracker.crack_range_sync)

    if password:
        logger.info(f"[✓] Found password for hash {req.hash[:8]}: {password}")
    else:
        logger.info(f"[X] No match for hash {req.hash[:8]} in range.")

    return {"found": password is not None, "password": password}